from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

import yaml


MAX_SKILL_NAME_LENGTH = 64
SKIP_PARTS = {"__pycache__", ".pytest_cache"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


class PackageSkillError(ValueError):
    pass


def package_skill(skill_path: Path, output_path: Path | None = None) -> Path:
    skill_path = skill_path.resolve()
    _validate_package_ready(skill_path)

    if output_path is None:
        output_path = skill_path / "skill.zip"
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    files = _package_files(skill_path)
    with zipfile.ZipFile(output_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            archive.write(file_path, file_path.relative_to(skill_path).as_posix())

    return output_path


def _validate_package_ready(skill_path: Path) -> None:
    if not skill_path.is_dir():
        raise PackageSkillError(f"Skill directory not found: {skill_path}")

    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        raise PackageSkillError("SKILL.md not found")

    frontmatter = _read_frontmatter(skill_md)
    name = frontmatter.get("name")
    description = frontmatter.get("description")

    if not isinstance(name, str) or not name.strip():
        raise PackageSkillError("SKILL.md frontmatter must include a non-empty name")
    if not re.fullmatch(r"[a-z0-9-]+", name):
        raise PackageSkillError("SKILL.md name must be lowercase hyphen-case")
    if name.startswith("-") or name.endswith("-") or "--" in name:
        raise PackageSkillError("SKILL.md name cannot start/end with hyphen or contain consecutive hyphens")
    if len(name) > MAX_SKILL_NAME_LENGTH:
        raise PackageSkillError(f"SKILL.md name exceeds {MAX_SKILL_NAME_LENGTH} characters")
    if not isinstance(description, str) or not description.strip():
        raise PackageSkillError("SKILL.md frontmatter must include a non-empty description")

    openai_yaml = skill_path / "agents" / "openai.yaml"
    if not openai_yaml.is_file():
        raise PackageSkillError("agents/openai.yaml not found")

    metadata = yaml.safe_load(openai_yaml.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise PackageSkillError("agents/openai.yaml must contain a YAML mapping")
    interface = metadata.get("interface")
    if not isinstance(interface, dict):
        raise PackageSkillError("agents/openai.yaml must include an interface mapping")
    for field in ("display_name", "short_description", "default_prompt"):
        if not isinstance(interface.get(field), str) or not interface[field].strip():
            raise PackageSkillError(f"agents/openai.yaml interface.{field} must be non-empty")
    if f"${name}" not in interface["default_prompt"]:
        raise PackageSkillError(f"agents/openai.yaml default_prompt must mention ${name}")


def _read_frontmatter(skill_md: Path) -> dict[str, object]:
    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        raise PackageSkillError("SKILL.md must start with YAML frontmatter")
    loaded = yaml.safe_load(match.group(1))
    if not isinstance(loaded, dict):
        raise PackageSkillError("SKILL.md frontmatter must be a YAML mapping")
    return loaded


def _package_files(skill_path: Path) -> list[Path]:
    files: list[Path] = []
    for path in skill_path.rglob("*"):
        relative = path.relative_to(skill_path)
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in relative.parts):
            continue
        if path.suffix in SKIP_SUFFIXES:
            continue
        if relative.as_posix() == "skill.zip":
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(skill_path).as_posix())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and package a skill directory as skill.zip.")
    parser.add_argument("skill", type=Path, help="Path to the skill directory.")
    parser.add_argument("--output", type=Path, default=None, help="Output zip path. Defaults to <skill>/skill.zip.")
    args = parser.parse_args(argv)

    try:
        output_path = package_skill(args.skill, args.output)
    except (OSError, PackageSkillError, yaml.YAMLError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Packaged skill: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
