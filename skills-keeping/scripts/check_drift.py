#!/usr/bin/env python3
"""Report skill copies that should be symlinks into the skills repo.

Usage: check_drift.py [--projects DIR ...] [--all]
A project copy is fine when the project's skills-lock.json tracks it and it matches the repo.
Exit 1 when it finds drift (a copy or a broken link), 0 when clean.
"""
import argparse, hashlib, json, os, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOME = Path.home()
AGENT_DIRS = [".agents/skills", ".claude/skills", ".codex/skills", ".config/opencode/skills",
              ".opencode/skills", ".commandcode/skills", ".openhands/skills", ".pi/agent/skills"]
PROJECT_DIRS = [".agents/skills", ".claude/skills", ".codex/skills", ".opencode/skills"]
SKIP = {"node_modules", "__pycache__", ".git"}


def digest(root: Path):
    """(content hash, newest mtime) of a skill folder."""
    h, newest = hashlib.sha256(), 0.0
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        for f in sorted(files):
            p = Path(dirpath) / f
            h.update(str(p.relative_to(root)).encode())
            try:
                h.update(p.read_bytes())
                newest = max(newest, p.stat().st_mtime)
            except OSError:
                pass
    return h.hexdigest(), newest


def repo_skills():
    return {p.parent.name for p in REPO.glob("*/SKILL.md")}


def tracked(root: Path):
    """Skill names in <root>/skills-lock.json (installed with `skills add`, updated with `skills update -p`)."""
    try:
        return set(json.loads((root / "skills-lock.json").read_text())["skills"])
    except (OSError, ValueError, KeyError):
        return set()


def scan(folder: Path, repo: set, show_all: bool, root: Path = None):
    """Yield (status, line) for each skill entry in a folder."""
    for e in sorted(folder.iterdir()):
        if e.name.startswith(".") or e.name == "synced":
            continue
        if e.is_symlink():
            target = Path(os.path.realpath(e))
            if not target.exists():
                yield "DRIFT", f"BROKEN LINK  {e} -> {os.readlink(e)}"
            continue
        if not e.is_dir() or not (e / "SKILL.md").exists():
            continue
        if e.name in repo:
            a, ta = digest(e)
            b, tb = digest(REPO / e.name)
            if root is None:
                fix = f"replace with a symlink to {REPO / e.name}"
            elif e.name in tracked(root):
                fix = "push the repo, then: npx skills update -p -y  (never edit a project copy in place)"
                if a == b:
                    if show_all:
                        yield "ok", f"tracked, same {e}"
                    continue
            else:
                fix = f"untracked: npx skills add nathnael-desta/skills --skill {e.name} -a claude-code codex -y  (writes skills-lock.json; commit it)"
            if a == b:
                yield "DRIFT", f"COPY (same)    {e}  -> {fix}"
            else:
                newer = "copy is NEWER" if ta > tb else "repo is newer"
                yield "DRIFT", f"COPY (differs) {e}  [{newer}] -> diff -r, merge into the repo first, then: {fix}"
        elif show_all:
            yield "ok", f"local only    {e}  (not in repo: vendor, project-specific, or not yet adopted)"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--projects", nargs="*", default=[], help="project roots to scan (default: current dir)")
    ap.add_argument("--all", action="store_true", help="also list local-only skills and external links")
    args = ap.parse_args()
    repo, drift = repo_skills(), 0
    folders = [(HOME / d, None) for d in AGENT_DIRS]
    for proj in args.projects or [os.getcwd()]:
        folders += [(Path(proj).expanduser() / d, Path(proj).expanduser()) for d in PROJECT_DIRS]
    seen = set()
    for f, root in folders:
        if not f.is_dir() or f.is_symlink() or f.resolve() in seen:
            continue
        seen.add(f.resolve())
        rows = list(scan(f, repo, args.all, root))
        if rows:
            print(f"\n{f}")
            for status, line in rows:
                drift += status == "DRIFT"
                print("  " + line)
    hub = HOME / ".agents/skills"
    missing = sorted(s for s in repo if hub.is_dir() and not (hub / s).exists())
    if args.all and missing:
        print(f"\nrepo skills not linked into {hub}: {', '.join(missing)}")
    print(f"\n{drift} drift item(s)" if drift else "\nclean: no copies of repo skills outside the repo")
    sys.exit(1 if drift else 0)


if __name__ == "__main__":
    main()
