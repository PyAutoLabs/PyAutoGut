"""Lint the Gut's two workflows: they parse, and the void workflow carries
its safety gates — the author-association gate, the `void:` title prefix
(labels can be dropped by the issue form), the namespace refusal, the held
refusal and `push origin --delete` behind an ls-remote read — plus the
sibling-repo reach: the App-token branch, the repo column and the per-ref
failure rows, and the dispatch-only dry-run probe."""

from pathlib import Path

import yaml

WF = Path(__file__).resolve().parents[1] / ".github" / "workflows"


def _load(name):
    text = (WF / name).read_text()
    return text, yaml.safe_load(text)


def _on(doc):
    return doc.get("on", doc.get(True))  # yaml 1.1 reads `on` as True


def test_void_workflow_triggers_and_permissions():
    text, doc = _load("void.yml")
    assert doc["name"] == "Gut Void"
    on = _on(doc)
    assert on["issues"] == {"types": ["opened"]}
    # dispatch exists only for the dry-run probe; it never reaches `void`
    assert on["workflow_dispatch"]["inputs"]["dry_run"]["default"] is False
    assert "github.event.issue.title" in doc["jobs"]["void"]["if"]
    assert doc["permissions"] == {"contents": "write", "issues": "write",
                                  "actions": "write"}


def test_void_workflow_gates_on_author_association_and_title_prefix():
    text, doc = _load("void.yml")
    gate = '["OWNER", "MEMBER", "COLLABORATOR"]'
    void_if = doc["jobs"]["void"]["if"]
    refuse_if = doc["jobs"]["refuse"]["if"]
    for cond in (void_if, refuse_if):
        assert gate in cond
        assert "startsWith(github.event.issue.title, 'void:')" in cond
        assert "contains(github.event.issue.labels.*.name, 'void')" in cond
    assert "!contains(fromJSON" in refuse_if
    assert '--reason "not planned"' in text
    assert "gh label create void" in text and "|| true" in text


def test_void_workflow_refuses_names_outside_the_namespace_and_held():
    text, _ = _load("void.yml")
    assert "*..*|/*|*/|*//*|-*|refs/*" in text
    assert '[ "$n" != "main" ]' in text
    assert "is HELD" in text and ".held | map(.name) | index($n)" in text
    assert "jq -r '.due[] | [.repo, .name] | @tsv' plan.json" in text
    assert "valid_repo" in text and "names refs on more than one repo" in text
    # the title is untrusted: read from env, never interpolated in a script
    assert "TITLE: ${{ github.event.issue.title }}" in text
    for step in _load("void.yml")[1]["jobs"]["void"]["steps"]:
        assert "github.event.issue.title" not in str(step.get("run", ""))
        assert "steps.resolve.outputs.target" not in str(step.get("run", ""))


def test_void_workflow_verifies_then_deletes_then_reports():
    text, _ = _load("void.yml")
    assert 'git ls-remote origin "$ref"' in text
    assert 'git push origin --delete "$ref"' in text
    assert text.index('git ls-remote origin "$ref"') < text.index(
        'git push origin --delete "$ref"')
    assert "recovery is no longer possible" in text
    assert "--reason completed" in text
    assert "gh workflow run gut_board.yml" in text
    assert "if: failure()" in text


def test_board_workflow_publishes_and_validates_the_feed():
    text, doc = _load("gut_board.yml")
    on = _on(doc)
    assert on["schedule"] == [{"cron": "45 5 * * *"}]
    assert "workflow_dispatch" in on
    assert on["workflow_run"] == {"workflows": ["Gut Void"],
                                  "types": ["completed"]}
    assert doc["permissions"] == {"contents": "read", "pages": "write",
                                  "id-token": "write"}
    for out in ("index.html", "badge.json", "board.json", "state.json",
                "dashboard.md"):
        assert f"_site/{out}" in text
    steps = doc["jobs"]["board"]["steps"]
    names = [s.get("name", "") for s in steps]
    assert "Validate the cockpit feed against the Brain contract" in names
    assert "PyAutoBrain/board/_state.py _site/state.json" in text
    uses = [s.get("uses", "") for s in steps]
    assert any(u.startswith("actions/configure-pages") for u in uses)
    assert any(u.startswith("actions/deploy-pages") for u in uses)
    assert "enablement: true" in text


def test_void_workflow_reaches_sibling_repos_with_the_app_token():
    text, doc = _load("void.yml")
    steps = {s.get("name"): s for s in doc["jobs"]["void"]["steps"]}
    mint = steps["Mint App token (every installed repo — delete sibling refs)"]
    assert mint["uses"] == "actions/create-github-app-token@v3"
    assert mint["with"]["client-id"] == "${{ vars.APP_CLIENT_ID }}"
    assert mint["with"]["private-key"] == "${{ secrets.APP_PRIVATE_KEY }}"
    assert mint["with"]["permission-contents"] == "write"
    assert "repositories" not in mint["with"]  # owner-wide: any sibling
    void = steps["Void each ref (ls-remote → push --delete → verify)"]
    # the App token is scoped to the one step that needs it
    assert void["env"] == {"APP_TOKEN": "${{ steps.app_token.outputs.token }}"}
    assert sum("steps.app_token.outputs.token" in str(s)
               for s in steps.values()) == 1
    run = void["run"]
    assert 'if [ "$repo" = "$own" ]; then' in run
    # gh is git's credential helper; no credential in a URL or a header env
    assert 'GH_TOKEN="$APP_TOKEN" gh auth setup-git' in run
    assert "PAT_PYAUTOLABS" not in text and "x-access-token" not in text
    assert "GIT_CONFIG_KEY" not in text and "extraheader" not in run
    assert "|| github.token" not in text
    assert 'url="https://github.com/$owner/$repo.git"' in run
    # ls-remote → push --delete → verify on the sibling, in that order
    i_ls = run.index('sibling_git ls-remote "$url" "$ref" 2>ls.err')
    i_push = run.index('sibling_git push "$url" --delete "$ref"')
    i_verify = run.index('left=$(sibling_git ls-remote "$url" "$ref"')
    assert i_ls < i_push < i_verify
    # per-ref outcomes: unreadable, 403, generic failure
    assert "could not read $repo with the App token" in run
    assert "403 — the App token cannot push to $repo" in run
    assert "left in place" in run and 'echo "$repo" >> token_failed.txt' in run


def test_void_dry_run_probe_deletes_nothing():
    text, doc = _load("void.yml")
    probe = doc["jobs"]["probe"]
    assert probe["if"] == "github.event_name == 'workflow_dispatch' && inputs.dry_run"
    assert probe["permissions"] == {"contents": "read"}
    body = "\n".join(str(s.get("run", "")) for s in probe["steps"])
    assert "push --dry-run" in body and "ls-remote" in body
    for forbidden in ("gh issue", "gh workflow run", "push origin --delete"):
        assert forbidden not in body
    import re
    assert not re.search(r"git -C \"\$sib\" push (?!--dry-run)", body)


def test_void_comment_has_a_repo_column_and_names_the_pat_gaps():
    text, doc = _load("void.yml")
    assert "| repo | name | pre-delete sha | result |" in text
    assert "|---|---|---|---|" in text
    report = next(s for s in doc["jobs"]["void"]["steps"]
                  if s.get("name") == "Report, close and re-render")["run"]
    assert "token_failed.txt" in report and "pyautolabs-bot App token" in report
    # a failure leaves the issue open (exit before close)
    assert report.index('if [ "$FAIL" = "1" ]') < report.index("--reason completed")
