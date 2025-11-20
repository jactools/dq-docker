#!/usr/bin/env python3
import re
import sys
from pathlib import Path

def update_version(pr_number: str, pyproject_path: Path) -> int:
    text = pyproject_path.read_text(encoding="utf-8")

    # Find the first project-version occurrence and keep major.minor
    m = re.search(r'^(version\s*=\s*")(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>[^\"]+)(")', text, flags=re.MULTILINE)
    if m:
        major = m.group('major')
        minor = m.group('minor')
        new_version = f'{major}.{minor}.{pr_number}'
        new_text = text[:m.start()] + m.group(1) + new_version + m.group(5) + text[m.end():]
    else:
        # No match, append a project version entry under [project]
        new_version = f'0.1.{pr_number}'
        new_text = text + f"\n[project]\nversion = \"{new_version}\"\n"

    if new_text == text:
        print("No change to pyproject.toml")
        return 0

    pyproject_path.write_text(new_text, encoding="utf-8")
    print(f"Updated pyproject.toml version -> {new_version}")
    return 0


def main(argv):
    if len(argv) < 3:
        print("Usage: update_pyproject_version.py <PR_NUMBER> <pyproject.toml>")
        return 2
    pr_number = argv[1]
    path = Path(argv[2])
    if not path.exists():
        print(f"pyproject file not found: {path}")
        return 2
    return update_version(pr_number, path)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
