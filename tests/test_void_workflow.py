"""Lint the Gut's two workflows: they parse, and the void workflow carries
its safety gates — the author-association gate, the `void:` title prefix
(labels can be dropped by the issue form), the namespace refusal, the held
refusal and `push origin --delete` behind an ls-remote read."""

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
    assert _on(doc) == {"issues": {"types": ["opened"]}}
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
    assert "is HELD" in text and ".held | index($n)" in text
    assert "jq -r '.due[]' plan.json" in text
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
