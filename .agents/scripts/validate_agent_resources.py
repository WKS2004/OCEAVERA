#!/usr/bin/env python3
"""Check OCEAVERA agent resources and repository documentation without dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)]+)\)")
SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
LOCAL_ABSOLUTE = re.compile(r"(?<![A-Za-z0-9+.-])(?:[A-Za-z]:[\\/]|file://)")
SKIP = {".git", "__pycache__", ".venv", "venv", "node_modules"}


def load_json(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"{path.name}: cannot read JSON ({type(exc).__name__})")
        return {}


def resolve_local(root: Path, value: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value or SCHEME.match(value) or Path(value).is_absolute():
        errors.append("Registry contains an invalid local reference")
        return None
    path = (root / value).resolve()
    if not path.is_relative_to(root) or not path.exists():
        errors.append(f"Missing or outside local reference: {value}")
        return None
    return path


def read_scalar(value: str) -> str:
    if value.startswith('"'):
        result = json.loads(value)
        if not isinstance(result, str):
            raise ValueError("Expected a string")
        return result
    if not value or re.search(r"[:#\[\]{}<>\n]", value):
        raise ValueError("Unsupported plain scalar")
    return value


def check_skill(root: Path, entry: dict, errors: list[str]) -> None:
    skill_id = entry["id"]
    folder = resolve_local(root, entry.get("path"), errors)
    if folder is None:
        return
    if folder != root / ".agents" / "skills" / skill_id:
        errors.append(f"{skill_id}: registry path differs from skill identity")
    try:
        text = (folder / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not match:
            raise ValueError("Missing frontmatter")
        fields = {}
        for line in match[1].splitlines():
            key, value = line.split(": ", 1)
            if key in fields:
                raise ValueError("Duplicate field")
            fields[key] = read_scalar(value)
        if set(fields) != {"name", "description"}:
            raise ValueError("Unsupported or missing frontmatter fields")
        if fields["name"] != skill_id or not fields["description"] or len(fields["description"]) > 1024:
            raise ValueError("Name or description mismatch")
        if "[TODO:" in text:
            raise ValueError("Unfinished scaffold")
        metadata = (folder / "agents" / "openai.yaml").read_text(encoding="utf-8").splitlines()
        if not metadata or metadata[0] != "interface:":
            raise ValueError("Missing interface metadata")
        interface = {}
        for line in metadata[1:]:
            item = re.fullmatch(r'  (display_name|short_description): (".*")', line)
            if not item or item[1] in interface:
                raise ValueError("Unsupported or duplicate metadata field")
            interface[item[1]] = json.loads(item[2])
        if set(interface) != {"display_name", "short_description"}:
            raise ValueError("Missing interface fields")
        if not isinstance(interface["display_name"], str) or not interface["display_name"]:
            raise ValueError("Empty display name")
        if not isinstance(interface["short_description"], str) or not 25 <= len(interface["short_description"]) <= 64:
            raise ValueError("Interface description length")
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        errors.append(f"{skill_id}: {exc}")


def routing_text(registry: dict) -> str:
    lines = [
        "# Task routing",
        "",
        "Generated from the [skill registry](registry/skills.json). Change the registry and regenerate this view; project knowledge remains in documentation.",
        "",
        "For every task, read [change scope](rules/change-safety.md), [validation](rules/validation.md) and [contributor recording](rules/ai-usage.md). Then select the matching workflow below. Load only supporting references needed for the active mode.",
        "",
        "| Requested work | Workflow | Conditional rules |",
        "| --- | --- | --- |",
    ]
    for entry in registry["skills"]:
        rules = ", ".join(f"[{rule.replace('-', ' ')}](rules/{rule}.md)" for rule in entry["rules"])
        skill = f"[{entry['title']}](skills/{entry['id']}/SKILL.md)"
        lines.append(f"| {entry['selectWhen']} | {skill} | {rules} |")
    lines.extend([
        "",
        "Cross-cutting work may need more than one workflow: target sampling and spatial partitions should agree, data preparation and feature choices should respect validation, and assessment reporting should link actual technical evidence.",
        "",
        "This map selects guidance; it does not authorise a technical stage or establish that implementation exists. Consult the [repository map](repository-map.md) and current readiness before making completion claims.",
        "",
    ])
    return "\n".join(lines)


def check_contributions(root: Path, errors: list[str]) -> tuple[int, int, int]:
    """Validate attribution structure, not the truth of a contribution claim."""
    try:
        roster = (root / "docs/project/ai-team-members.md").read_text(encoding="utf-8")
        template = (root / "docs/project/ai-usage-log-template.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"Contribution conventions: unreadable source ({type(exc).__name__})")
        return 0, 0, 0
    table = re.search(
        r"\| GitHub Username \| Team Member Name \|\n\| --- \| --- \|\n((?:\|[^\n]+\n)+)",
        roster,
    )
    members = {}
    if table is None:
        errors.append("Contributor mapping: missing canonical table")
    else:
        for row in table[1].splitlines():
            columns = [value.strip() for value in row.strip("|").split("|")]
            if len(columns) != 2:
                errors.append("Contributor mapping: malformed row")
                continue
            username, full_name = columns
            if not re.fullmatch(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", username) or not full_name:
                errors.append("Contributor mapping: invalid identity")
            if username.casefold() in {value.casefold() for value in members}:
                errors.append("Contributor mapping: duplicate account")
            members[username] = full_name
    required = re.findall(r"^- \*\*([^\n]+?):\*\*", template, re.M)
    if len(required) != 10 or len(set(required)) != 10:
        errors.append("Contribution template: expected ten distinct recording fields")
    folder = root / "docs/ai-contribution"
    logs = 0
    records = 0
    if not folder.is_dir():
        errors.append("Contribution log directory is missing")
        return len(members), 0, 0
    for path in sorted(folder.iterdir()):
        if not path.is_file() or not path.name.endswith("-ai-usage.md"):
            errors.append(f"Contribution logs: unexpected entry {path.name}")
            continue
        logs += 1
        username = path.name.removesuffix("-ai-usage.md")
        if username not in members:
            errors.append(f"{path.name}: account does not match canonical mapping exactly")
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            errors.append(f"{path.name}: unreadable contribution log")
            continue
        headings = re.findall(r"^## (.+)$", content, re.M)
        if not headings or any(not re.fullmatch(r"\d{4}-\d{2}-\d{2} — .+", item) for item in headings):
            errors.append(f"{path.name}: missing or malformed dated entries")
            continue
        dates = [item[:10] for item in headings]
        if dates != sorted(dates):
            errors.append(f"{path.name}: entries are not in chronological order")
        for entry in re.split(r"^## .+$", content, flags=re.M)[1:]:
            records += 1
            fields = re.findall(r"^- \*\*([^\n]+?):\*\* (.+)$", entry, re.M)
            keys = [key for key, value in fields]
            if len(keys) != len(set(keys)) or set(keys) != set(required):
                errors.append(f"{path.name}: entry fields differ from the recording template")
                continue
            values = dict(fields)
            if values.get("GitHub Username") != username or values.get("Team Member Name") != members[username]:
                errors.append(f"{path.name}: entry identity differs from contributor mapping")
            if not re.search(r"UTC|GMT|Asia/", values.get("Date/time or time range", "")):
                errors.append(f"{path.name}: timestamp needs an explicit timezone")
    return len(members), logs, records


def run(root: Path, write_routing: bool) -> int:
    errors = []
    registry = load_json(root / ".agents/registry/skills.json", errors)
    cases = load_json(root / ".agents/evals/routing-cases.json", errors)
    if registry.get("schemaVersion") != 1 or not isinstance(registry.get("skills"), list):
        errors.append("Unsupported registry schema")
        return report(errors)
    entries = registry["skills"]
    ids = set()
    rules_used = set(registry.get("policy", {}).get("baseRules", []))
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            errors.append("Invalid skill registry entry")
            continue
        skill_id = entry["id"]
        if skill_id in ids or not NAME.fullmatch(skill_id) or len(skill_id) > 64:
            errors.append(f"Invalid or duplicate skill identity: {skill_id}")
        ids.add(skill_id)
        for field in ("title", "selectWhen"):
            if not isinstance(entry.get(field), str) or not entry[field].strip() or re.search(r"[|\n]", entry[field]):
                errors.append(f"{skill_id}: invalid routing text")
        if entry.get("origin") != "project":
            errors.append(f"{skill_id}: external imports require a reviewed validator/registry schema")
        if not isinstance(entry.get("rules"), list) or not isinstance(entry.get("knowledge"), list):
            errors.append(f"{skill_id}: missing rules or knowledge list")
            continue
        for rule in entry["rules"]:
            if not isinstance(rule, str) or not NAME.fullmatch(rule):
                errors.append(f"{skill_id}: invalid rule identity")
                continue
            rules_used.add(rule)
        for value in entry["knowledge"]:
            resolve_local(root, value, errors)
        check_skill(root, entry, errors)
    discovered = {p.name for p in (root / ".agents/skills").iterdir() if p.is_dir()}
    if discovered != ids:
        errors.append("Skill inventory and registry differ")
    actual_rules = {p.stem for p in (root / ".agents/rules").glob("*.md")}
    if actual_rules != rules_used:
        errors.append("Rule inventory and routing coverage differ")
    for rule in rules_used:
        resolve_local(root, f".agents/rules/{rule}.md", errors)
    for key in ("canonicalKnowledge", "rootInstructions"):
        resolve_local(root, registry.get("policy", {}).get(key), errors)
    if cases.get("schemaVersion") != 1 or not isinstance(cases.get("cases"), list):
        errors.append("Unsupported routing-case schema")
    else:
        case_ids = set()
        covered = set()
        for case in cases["cases"]:
            if not isinstance(case, dict) or not isinstance(case.get("id"), str):
                errors.append("Malformed routing case")
                continue
            if case["id"] in case_ids:
                errors.append("Duplicate routing-case identity")
            case_ids.add(case["id"])
            skills = case.get("expectedSkills", [])
            rules = case.get("expectedRules", [])
            if not isinstance(skills, list) or not isinstance(rules, list):
                errors.append(f"{case['id']}: invalid case references")
                continue
            if not skills or not set(skills) <= ids or not set(rules) <= actual_rules:
                errors.append(f"{case['id']}: unknown skill or rule")
            covered.update(skills)
            if not case.get("task") or not case.get("forbiddenClaims"):
                errors.append(f"{case['id']}: missing review expectation")
            for entry in entries:
                if entry.get("id") in skills:
                    needed = set(registry["policy"]["baseRules"]) | set(entry.get("rules", []))
                    if not needed <= set(rules):
                        errors.append(f"{case['id']}: incomplete rule expectations")
        if covered != ids:
            errors.append("Routing review cases do not cover the skill inventory")
    if errors:
        return report(errors)
    routing = root / ".agents/routing.md"
    expected = routing_text(registry)
    if write_routing:
        routing.write_text(expected, encoding="utf-8", newline="\n")
    elif not routing.is_file() or routing.read_text(encoding="utf-8") != expected:
        errors.append("Routing view is missing or stale; regenerate it")
    count = 0
    documents = 0
    for path in root.rglob("*"):
        if not path.is_file() or SKIP.intersection(path.relative_to(root).parts):
            continue
        if path.suffix not in {".md", ".yaml", ".yml", ".json", ".py"} and path.name not in {".editorconfig", ".gitignore", ".gitattributes"}:
            continue
        try:
            data = path.read_bytes()
            text = data.decode("utf-8")
        except (OSError, UnicodeError):
            errors.append(f"{path.relative_to(root)}: unreadable UTF-8 text")
            continue
        documents += 1
        if data.startswith(b"\xef\xbb\xbf") or b"\r" in data or not data.endswith(b"\n"):
            errors.append(f"{path.relative_to(root)}: encoding or newline convention")
        if any(line.rstrip() != line for line in text.splitlines()):
            errors.append(f"{path.relative_to(root)}: trailing whitespace")
        if path.suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError:
                errors.append(f"{path.relative_to(root)}: invalid JSON")
        if path.suffix != ".md":
            continue
        if LOCAL_ABSOLUTE.search(text):
            errors.append(f"{path.relative_to(root)}: absolute local reference")
        for target in LINK.findall(text):
            target = target.strip().split("#", 1)[0]
            if not target or SCHEME.match(target):
                continue
            count += 1
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(root) or not resolved.exists():
                errors.append(f"{path.relative_to(root)}: broken or outside link: {target}")
    contributors, logs, records = check_contributions(root, errors)
    if errors:
        return report(errors)
    print(f"PASS: {len(ids)} skills, {len(actual_rules)} rules, {len(cases['cases'])} routing review cases, {documents} text files and {count} local links.")
    print(f"PASS: contributor identities: {contributors}; contribution logs: {logs}; dated entries: {records}.")
    print("Structural checks only; manual cases are not executed agent evaluations and attribution claims need evidence.")
    return 0


def report(errors: list[str]) -> int:
    for error in errors:
        print(f"FAIL: {error}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-routing", action="store_true", help="Regenerate the routing view before checking")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    return run(root, args.write_routing)


if __name__ == "__main__":
    sys.exit(main())
