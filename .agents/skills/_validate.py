"""Validate flexloop skills completeness and usability."""
import os
import re

skills_dir = r"s:/Dao/libs/dev/flexloop/.agents/skills"
expected_skills = ["commit", "debug", "land", "linear", "pull", "push"]
required_sections = ["Goals", "Steps"]

results = []

for skill_name in expected_skills:
    skill_path = os.path.join(skills_dir, skill_name, "SKILL.md")
    issues = []

    if not os.path.isfile(skill_path):
        issues.append("MISSING: SKILL.md not found")
        results.append((skill_name, "FAIL", issues, 0))
        continue

    with open(skill_path, encoding="utf-8") as f:
        content = f.read()

    # Frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        issues.append("MISSING: frontmatter")
    else:
        fm = fm_match.group(1)
        if "name:" not in fm:
            issues.append("MISSING: frontmatter name field")
        if "description:" not in fm:
            issues.append("MISSING: frontmatter description field")

    # Required sections
    for section in required_sections:
        if not re.search(r"^#+\s+" + section, content, re.MULTILINE):
            issues.append("MISSING: section [" + section + "]")

    # Name consistency
    if fm_match:
        name_match = re.search(r"name:\s*(\S+)", fm_match.group(1))
        if name_match and name_match.group(1) != skill_name:
            issues.append(
                "MISMATCH: name=" + name_match.group(1) + ", expected=" + skill_name
            )

    # Codex session references (should use Agent)
    codex_session_count = len(re.findall(r"Codex session", content))
    if codex_session_count > 0:
        issues.append("NOTE: " + str(codex_session_count) + " Codex session refs")

    line_count = content.count("\n") + 1
    status = (
        "PASS"
        if not issues
        else "WARN" if all("NOTE:" in i for i in issues) else "FAIL"
    )
    results.append((skill_name, status, issues, line_count))

# Print results
header = f"{'Skill':<10} {'Status':<6} {'Lines':<7} Issues"
print(header)
print("-" * 70)
for name, status, issues, lines in results:
    issue_str = "; ".join(issues) if issues else "None"
    print(f"{name:<10} {status:<6} {lines:<7} {issue_str}")

# land_watch.py check
watch_path = os.path.join(skills_dir, "land", "land_watch.py")
if os.path.isfile(watch_path):
    with open(watch_path, encoding="utf-8") as f:
        py_content = f.read()

    py_issues = []
    if "AGENT_BOTS" not in py_content:
        py_issues.append("MISSING: AGENT_BOTS constant")
    if "[codex]" not in py_content:
        py_issues.append("MISSING: [codex] backward compatibility")
    if "Agent Review" not in py_content and "Codex Review" not in py_content:
        py_issues.append("MISSING: Agent/Codex Review pattern")

    py_status = "PASS" if not py_issues else "FAIL"
    py_lines = py_content.count("\n") + 1
    py_issue_str = "; ".join(py_issues) if py_issues else "None"
    print(f"\nland_watch  {py_status:<6} {py_lines:<7} {py_issue_str}")
else:
    print(f"\nland_watch  FAIL    0       MISSING file")

# Summary
total_pass = sum(1 for r in results if r[1] == "PASS")
total = len(results)
print(f"\nSummary: {total_pass}/{total} skills PASS")
