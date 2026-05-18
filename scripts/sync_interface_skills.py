#!/usr/bin/env python3
"""
Sync interface-skills from upstream repo into .agents/skills.

Pulls the latest interface-skills, copies/overwrites ui-* skills,
syncs shared references to .agents/skills/shared/references/,
and optionally creates a branch + PR.

Usage:
  python scripts/sync_interface_skills.py --all --branch chore/sync-interface-skills --pr
  python scripts/sync_interface_skills.py --skills ui-brief ui-blueprint --dry-run
"""

import argparse
import datetime
import logging
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
UPSTREAM_REPO = "https://github.com/ThorStarlord/interface-skills.git"


class SkillSyncer:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.temp_dir: Optional[Path] = None
        self.temp_upstream: Optional[Path] = None
        self.changes = {"updated": [], "created": []}

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="interface_skills_"))
        self.temp_upstream = self.temp_dir / "interface-skills"
        log.info(f"[TEMP] {self.temp_dir}")
        return self

    def __exit__(self, *args):
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                log.info(f"[CLEANUP] Removed {self.temp_dir}")
            except PermissionError:
                log.debug("[CLEANUP] Skipped (permission denied, OS will clean up)")

    def clone_upstream(self) -> bool:
        try:
            log.info(f"[CLONE] {UPSTREAM_REPO}")
            result = subprocess.run(
                ["git", "clone", "--depth=1", UPSTREAM_REPO, str(self.temp_upstream)],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode != 0:
                log.error(f"Clone failed: {result.stderr}")
                return False
            log.info(f"[SUCCESS] Cloned to {self.temp_upstream}")
            return True
        except Exception as e:
            log.error(f"[ERROR] Clone failed: {e}")
            return False

    def list_upstream_skills(self) -> List[str]:
        skills_src = self.temp_upstream / "skills"
        if not skills_src.exists():
            log.error(f"No skills/ folder in cloned repo: {skills_src}")
            return []
        skills = sorted([d.name for d in skills_src.iterdir() if d.is_dir()])
        log.info(f"[INVENTORY] Found {len(skills)} upstream skills")
        return skills

    def sync_skill(self, skill_name: str) -> bool:
        skill_src = self.temp_upstream / "skills" / skill_name
        if not skill_src.exists():
            log.warning(f"[SKIP] Skill not found: {skill_name}")
            return False

        skill_dst = SKILLS_DIR / skill_name
        if skill_dst.exists():
            action = "[UPDATE]"
            self.changes["updated"].append(skill_name)
        else:
            action = "[CREATE]"
            self.changes["created"].append(skill_name)

        if not self.dry_run:
            if skill_dst.exists():
                shutil.rmtree(skill_dst)
            shutil.copytree(skill_src, skill_dst)

        log.info(f"{action} {skill_name}")
        return True

    def sync_shared_references(self) -> bool:
        """Copy shared/references/* to .agents/skills/shared/references/."""
        shared_src = self.temp_upstream / "shared" / "references"
        if not shared_src.exists():
            log.warning("[SKIP] No shared/references in upstream")
            return False

        shared_dst = SKILLS_DIR / "shared" / "references"
        if not self.dry_run:
            if shared_dst.exists():
                shutil.rmtree(shared_dst)
            shutil.copytree(shared_src, shared_dst)

        ref_count = len(list(shared_src.iterdir())) if shared_src.exists() else 0
        log.info(f"[REFERENCES] Synced {ref_count} files to shared/references/")
        return True

    def create_branch_and_commit(self, branch_name: str) -> bool:
        try:
            if not self.dry_run:
                result = subprocess.run(
                    ["git", "checkout", "-b", branch_name],
                    cwd=REPO_ROOT, capture_output=True, text=True,
                )
                if result.returncode != 0:
                    log.error(f"Branch creation failed: {result.stderr}")
                    return False

            log.info(f"[BRANCH] {branch_name}")

            if not self.dry_run:
                result = subprocess.run(
                    ["git", "add", ".agents/skills/"],
                    cwd=REPO_ROOT, capture_output=True, text=True,
                )
                if result.returncode != 0:
                    log.error(f"Git add failed: {result.stderr}")
                    return False

            num_skills = len(self.changes["updated"]) + len(self.changes["created"])
            commit_msg = f"chore: sync interface-skills ({num_skills} skills)"

            if not self.dry_run:
                result = subprocess.run(
                    ["git", "commit", "-m", commit_msg],
                    cwd=REPO_ROOT, capture_output=True, text=True,
                )
                if result.returncode != 0:
                    log.error(f"Commit failed: {result.stderr}")
                    return False

            log.info(f"[COMMIT] {commit_msg}")
            return True
        except Exception as e:
            log.error(f"[ERROR] Commit failed: {e}")
            return False

    def create_pr(self) -> bool:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=REPO_ROOT, capture_output=True, text=True,
            )
            if result.returncode != 0:
                log.error("Could not get current branch")
                return False

            branch = result.stdout.strip()

            if not self.dry_run:
                result = subprocess.run(
                    ["git", "push", "-u", "origin", branch],
                    cwd=REPO_ROOT, capture_output=True, text=True,
                )
                if result.returncode != 0:
                    log.error(f"Push failed: {result.stderr}")
                    return False

            log.info(f"[PUSH] {branch}")

            pr_title = "chore: sync interface-skills"
            pr_body = (
                f"Synced interface-skills on {datetime.date.today()}\n\n"
                f"- Updated: {', '.join(self.changes['updated']) or 'none'}\n"
                f"- Created: {', '.join(self.changes['created']) or 'none'}"
            )

            if not self.dry_run:
                result = subprocess.run(
                    ["gh", "pr", "create", "--base", "main",
                     "--title", pr_title, "--body", pr_body],
                    cwd=REPO_ROOT, capture_output=True, text=True,
                )
                if result.returncode != 0:
                    log.error(f"PR creation failed: {result.stderr}")
                    log.info("Hint: run 'gh pr create' manually")
                    return False

            log.info(f"[PR] Created: {pr_title}")
            return True
        except Exception as e:
            log.error(f"[ERROR] PR creation failed: {e}")
            return False

    def summary(self):
        total = len(self.changes["updated"]) + len(self.changes["created"])
        log.info("")
        log.info("=" * 60)
        log.info("SUMMARY")
        log.info("=" * 60)
        log.info(f"Updated:  {len(self.changes['updated'])}")
        log.info(f"Created:  {len(self.changes['created'])}")
        log.info(f"Total:    {total}")
        if self.dry_run:
            log.info("\n[DRY RUN] No changes written.")
        log.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Sync interface-skills into .agents/skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/sync_interface_skills.py --all --dry-run
  python scripts/sync_interface_skills.py --all --pr
  python scripts/sync_interface_skills.py --skills ui-brief ui-blueprint --branch chore/sync-skills
        """
    )
    parser.add_argument("--all", action="store_true", help="Sync all available upstream skills")
    parser.add_argument("--skills", nargs="+", help="Sync specific skills (e.g., ui-brief ui-blueprint)")
    parser.add_argument(
        "--branch",
        default=f"chore/sync-interface-skills-{datetime.date.today().strftime('%Y%m%d')}",
        help="Git branch name (default: chore/sync-interface-skills-YYYYMMDD)"
    )
    parser.add_argument("--pr", action="store_true", help="Create a PR after pushing (requires 'gh' CLI)")
    parser.add_argument("--no-git", action="store_true", help="Sync files only — skip branch, commit, push, and PR")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing files")

    args = parser.parse_args()

    if not args.all and not args.skills:
        parser.print_help()
        sys.exit(1)

    if args.dry_run:
        log.info("[DRY RUN MODE] No files will be changed\n")

    with SkillSyncer(dry_run=args.dry_run) as syncer:
        if not syncer.clone_upstream():
            sys.exit(1)

        skills_to_sync = syncer.list_upstream_skills() if args.all else args.skills

        if not skills_to_sync:
            log.error("No skills to sync")
            sys.exit(1)

        log.info(f"[SYNC] {len(skills_to_sync)} skill(s)\n")

        for skill in skills_to_sync:
            syncer.sync_skill(skill)

        syncer.sync_shared_references()
        syncer.summary()

        if args.no_git:
            if args.pr:
                log.warning("[WARN] --no-git is set — ignoring --pr")
            log.info("[NO-GIT] Sync complete. Skipped branch/commit/push/PR.")
        elif not args.dry_run and syncer.changes["updated"] + syncer.changes["created"]:
            log.info("")
            if syncer.create_branch_and_commit(args.branch):
                if args.pr:
                    syncer.create_pr()
                else:
                    log.info(f"[TIP] Run 'git push -u origin {args.branch}' then 'gh pr create --base main'")
            else:
                log.error("Failed to commit changes")
                sys.exit(1)


if __name__ == "__main__":
    main()