"""The SessionStart hook is generated into every repo — and must not drift.

The hook is what makes a Claude Code web/mobile session run Python 3.12 instead
of the container's 3.11 default. The harness reads it per repo, so it cannot
live once in the workspace: every repo carries a copy. Copies rot — that is the
whole reason `policy/session_start_hook.sh` is the single source and
`check_session_hooks` exists.

Conventions this file follows (see `test_repos_sync_hygiene_coverage.py`):

1. **Fictional fixtures only.** `tests/**` is KEEP-copied verbatim into the
   public template, so nothing here names a real repository, and the assertions
   are about the check's logic rather than whatever happens to be checked out.
2. **Prove each leg FAILS.** Every failure mode below is driven with input that
   must trip it — a check that cannot fail is decoration.
"""

import json
import os
import stat
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import repos_sync  # noqa: E402

HOOK_TEXT = "#!/usr/bin/env bash\necho canonical\n"
REPOS = {"OrganOne": {"category": "organ"}, "LibTwo": {"category": "library"}}


def make_repo(root, name, *, hook=HOOK_TEXT, executable=True, settings="register"):
    """A checked-out repo with the hook installed in one of several states."""
    repo = root / name
    (repo / ".claude" / "hooks").mkdir(parents=True)
    if hook is not None:
        path = repo / repos_sync.SESSION_HOOK_REL
        path.write_text(hook)
        path.chmod(0o755 if executable else 0o644)
    if settings == "register":
        (repo / repos_sync.SESSION_SETTINGS_REL).write_text(
            json.dumps(repos_sync.register_session_hook({}), indent=2) + "\n"
        )
    elif settings is not None:
        (repo / repos_sync.SESSION_SETTINGS_REL).write_text(settings)
    return repo


def test_fully_installed_repo_is_clean(tmp_path):
    make_repo(tmp_path, "OrganOne")
    make_repo(tmp_path, "LibTwo")
    assert repos_sync.check_session_hooks(tmp_path, REPOS, HOOK_TEXT) == []


def test_repo_that_is_not_checked_out_is_skipped(tmp_path):
    make_repo(tmp_path, "OrganOne")  # LibTwo absent entirely
    assert repos_sync.check_session_hooks(tmp_path, REPOS, HOOK_TEXT) == []


def test_missing_hook_fails(tmp_path):
    make_repo(tmp_path, "OrganOne")
    make_repo(tmp_path, "LibTwo", hook=None)
    problems = repos_sync.check_session_hooks(tmp_path, REPOS, HOOK_TEXT)
    assert len(problems) == 1 and "LibTwo" in problems[0]


def test_edited_copy_fails(tmp_path):
    """The failure mode the whole check exists for: someone fixes the hook in
    one repo instead of in the canonical file."""
    make_repo(tmp_path, "OrganOne")
    make_repo(tmp_path, "LibTwo", hook=HOOK_TEXT + "# local tweak\n")
    problems = repos_sync.check_session_hooks(tmp_path, REPOS, HOOK_TEXT)
    assert len(problems) == 1 and "differs" in problems[0]


def test_non_executable_hook_fails(tmp_path):
    """A hook without +x is silently never run by the harness."""
    make_repo(tmp_path, "OrganOne", executable=False)
    make_repo(tmp_path, "LibTwo")
    problems = repos_sync.check_session_hooks(tmp_path, REPOS, HOOK_TEXT)
    assert len(problems) == 1 and "not executable" in problems[0]


def test_missing_or_unregistering_settings_fails(tmp_path):
    """An installed hook nothing points at is dead weight."""
    make_repo(tmp_path, "OrganOne", settings=None)
    make_repo(tmp_path, "LibTwo", settings=json.dumps({"hooks": {"Stop": []}}))
    problems = repos_sync.check_session_hooks(tmp_path, REPOS, HOOK_TEXT)
    assert len(problems) == 2
    assert any("no .claude/settings.json" in p for p in problems)
    assert any("does not register" in p for p in problems)


def test_unparseable_settings_counts_as_unregistered(tmp_path):
    make_repo(tmp_path, "OrganOne", settings="{not json")
    make_repo(tmp_path, "LibTwo")
    problems = repos_sync.check_session_hooks(tmp_path, REPOS, HOOK_TEXT)
    assert len(problems) == 1 and "does not register" in problems[0]


def test_write_fixes_every_failure_mode_and_is_idempotent(tmp_path):
    make_repo(tmp_path, "OrganOne", hook=HOOK_TEXT + "# drift\n", executable=False)
    make_repo(tmp_path, "LibTwo", hook=None, settings=None)
    assert repos_sync.check_session_hooks(tmp_path, REPOS, HOOK_TEXT) != []

    repos_sync.write_session_hooks(tmp_path, REPOS, HOOK_TEXT)
    assert repos_sync.check_session_hooks(tmp_path, REPOS, HOOK_TEXT) == []

    installed = tmp_path / "OrganOne" / repos_sync.SESSION_HOOK_REL
    assert installed.read_text() == HOOK_TEXT
    assert installed.stat().st_mode & stat.S_IXUSR
    before = {
        p: p.read_bytes()
        for p in (tmp_path / "LibTwo" / ".claude").rglob("*")
        if p.is_file()
    }
    repos_sync.write_session_hooks(tmp_path, REPOS, HOOK_TEXT)
    assert {p: p.read_bytes() for p in before} == before


def test_write_preserves_other_settings_keys(tmp_path):
    """A repo's own permissions/env/hooks must survive the registration."""
    repo = make_repo(tmp_path, "OrganOne", settings=json.dumps(
        {"env": {"KEEP": "me"}, "hooks": {"Stop": [{"hooks": []}]}}
    ))
    repos_sync.write_session_hooks(tmp_path, REPOS, HOOK_TEXT)
    settings = json.loads((repo / repos_sync.SESSION_SETTINGS_REL).read_text())
    assert settings["env"] == {"KEEP": "me"}
    assert "Stop" in settings["hooks"]
    assert repos_sync.SESSION_HOOK_COMMAND in repos_sync.session_start_entries(settings)


def test_canonical_hook_ships_and_is_the_installed_text():
    """The real file, not a fixture: it must exist, be executable and be what
    `--write` would install."""
    mind_root = Path(__file__).resolve().parents[1]
    canonical = mind_root / repos_sync.SESSION_HOOK_FILE
    assert canonical.exists(), f"{repos_sync.SESSION_HOOK_FILE} is missing"
    assert os.access(canonical, os.X_OK)
    text = repos_sync.load_session_hook(mind_root)
    assert text.startswith("#!")
    assert text == (mind_root / repos_sync.SESSION_HOOK_REL).read_text()
