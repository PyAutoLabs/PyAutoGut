"""Hermetic tests for scripts/board.py — the PyAutoGut Dashboard.

No network, no Brain checkout, no Mind: a fake `git ls-remote` listing, a
fixture condemned.md written into tmp_path, and a tiny stand-in parser/theme
under tests/fixtures/brain with the Brain's interface. No instance names:
the owner is SomeOrg, the repo SomeGut.
"""

import datetime
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

GUT_HOME = Path(__file__).resolve().parents[1]
FIXTURE_BRAIN = Path(__file__).resolve().parent / "fixtures" / "brain"
sys.path.insert(0, str(GUT_HOME / "scripts"))

import board  # noqa: E402

TODAY = datetime.date(2026, 9, 26)
NS = "refs/heads/archive/condemned/"

LEDGER = """\
# Condemned material

## Entry schema
- `type` — prose, not an entry

<!--
## commented-example
- type: branch
- archive-ref: refs/heads/archive/condemned/commented-example @ 0de4514
-->

## team/old-spike
- type: branch
- locator: feature/old-spike
- reason: superseded by the real approach
- condemned: 2026-07-12
- sweep-after: 2026-08-12
- archive-ref: refs/heads/archive/condemned/team-old-spike @ aaaa111

## fresh/experiment
- type: branch
- locator: feature/fresh
- reason: retired by the user
- condemned: 2026-09-20
- sweep-after: 2026-10-20
- archive-ref: `refs/heads/archive/condemned/fresh-experiment` on SomeGut origin @ bbbb222

## history/kept
- type: branch
- locator: master
- reason: original project history
- sweep-after: never — void only on explicit human request
- archive-ref: `refs/heads/archive/condemned/history-kept` on SomeGut origin (cccc333)

## purge/datasets
- type: file
- locator: dataset/old
- sweep-after: 2026-08-29
- archive-ref: n/a — committed deletion; pre-purge SHA `8625a1de`

## gone/missing
- type: branch
- locator: feature/gone
- sweep-after: 2026-08-01
- archive-ref: refs/heads/archive/condemned/gone-missing @ dddd444

## voided/already
- type: branch
- locator: feature/voided
- sweep-after: 2026-08-01
- archive-ref: refs/heads/archive/condemned/voided-already @ eeee555

## batch/sessions
- type: branch
- locator: 2 session branches
- sweep-after: 2026-11-24
- archive-ref: 2 refs under `refs/heads/archive/condemned/batch-*` on SomeGut origin

## sibling/stash
- type: stash
- locator: stash@{0}
- sweep-after: 2026-08-29
- archive-ref: refs/heads/archive/condemned/sibling-stash-0 on SomeSibling origin (ffff666)
"""

LS_REMOTE = "\n".join(f"{sha}\t{NS}{name}" for name, sha in (
    ("team-old-spike", "a" * 40), ("fresh-experiment", "b" * 40),
    ("history-kept", "c" * 40), ("batch-one", "1" * 40),
    ("batch-two", "2" * 40), ("__selftest_branch__", "9" * 40),
)) + "\n" + "7" * 40 + "\trefs/heads/main\n"


@pytest.fixture
def parser():
    return board.load_parser(FIXTURE_BRAIN)


def _snap(parser, ls=LS_REMOTE, listed=True, foreign=None, voided=()):
    return board.build_snapshot(
        LEDGER, ls, parser, TODAY, "SomeOrg", "SomeGut", voided=voided,
        refs_listed=listed, generated="2026-09-26T06:00:00+00:00",
        foreign={"SomeSibling": {"sibling-stash-0": "6" * 40}}
        if foreign is None else foreign)


def _names(snap, key):
    return [r["name"] for r in snap["buckets"][key]]


def test_parse_ls_remote_keeps_only_the_archive_namespace():
    refs = board.parse_ls_remote(LS_REMOTE)
    assert "main" not in refs and len(refs) == 6
    assert refs["team-old-spike"] == "a" * 40


def test_reconcile_sorts_every_ref_and_entry_into_its_bucket(parser):
    voided = [{"number": 7, "title": "void: voided-already", "url": "u",
               "closed_at": "2026-09-25T00:00:00Z", "names": ["voided-already"]}]
    snap = _snap(parser, voided=voided)
    assert _names(snap, "due") == ["team-old-spike"]
    assert snap["buckets"]["due"][0]["days"] == 45
    assert _names(snap, "transit") == ["fresh-experiment", "batch-one",
                                       "batch-two"]
    assert _names(snap, "held") == ["history-kept"]
    assert _names(snap, "orphans") == ["__selftest_branch__"]
    assert _names(snap, "dangling") == ["gone-missing"]
    assert _names(snap, "voided_pending") == ["voided-already"]
    assert [r["entry"] for r in snap["buckets"]["history"]] == ["purge/datasets"]
    elsewhere = snap["buckets"]["elsewhere"]
    assert [r["name"] for r in elsewhere] == ["sibling-stash-0"]
    assert elsewhere[0]["overdue"] and elsewhere[0]["host"] == "SomeSibling"


def test_the_void_name_comes_from_archive_ref_not_the_heading(parser):
    snap = _snap(parser)
    row = snap["buckets"]["due"][0]
    assert row["entry"] == "team/old-spike" and row["name"] == "team-old-spike"


def test_a_ref_missing_on_its_sibling_repo_is_dangling(parser):
    snap = _snap(parser, foreign={"SomeSibling": {}})
    assert "sibling-stash-0" in _names(snap, "dangling")
    unlisted = _snap(parser, foreign={"SomeSibling": None})
    assert _names(unlisted, "elsewhere") == ["sibling-stash-0"]
    assert not unlisted["buckets"]["elsewhere"][0].get("overdue")


def test_void_link_is_well_formed_and_only_on_present_voidable_refs(parser):
    snap = _snap(parser)
    b = snap["buckets"]
    for key in board.VOIDABLE:
        for row in b[key]:
            url = urlsplit(row["void_url"])
            assert url.netloc == "github.com"
            assert url.path == "/SomeOrg/SomeGut/issues/new"
            q = parse_qs(url.query)
            assert q["title"] == [f"void: {row['name']}"]
            assert q["labels"] == ["void"]
            assert row["sha"] in q["body"][0]
            assert f"- repo: {board.row_repo(snap, row)}" in q["body"][0]
            assert "Submitting this issue voids the ref permanently." in q["body"][0]
    assert "title=void%3A+team-old-spike" in b["due"][0]["void_url"]
    for key in ("held", "dangling", "voided_pending", "history"):
        assert all(not r["void_url"] for r in b[key]), key


def test_sibling_held_rows_get_the_button_naming_the_repo(parser):
    b = _snap(parser)["buckets"]
    row = b["elsewhere"][0]
    q = parse_qs(urlsplit(row["void_url"]).query)
    assert q["title"] == ["void: sibling-stash-0"]
    body = q["body"][0]
    assert "- repo: SomeSibling" in body and "on SomeSibling" in body
    assert "PAT_PYAUTOLABS" in body and "6" * 40 in body
    # not listed this render → no SHA → no button
    unlisted = _snap(parser, foreign={"SomeSibling": None})
    assert not unlisted["buckets"]["elsewhere"][0]["void_url"]


def test_an_undated_sibling_ref_is_held_not_voidable(parser):
    ledger = LEDGER + (
        "\n## sibling/history\n- type: branch\n"
        "- sweep-after: never — void only on explicit human request\n"
        "- archive-ref: refs/heads/archive/condemned/sibling-history "
        "on SomeSibling origin\n")
    snap = board.build_snapshot(
        ledger, LS_REMOTE, parser, TODAY, "SomeOrg", "SomeGut",
        generated="2026-09-26T06:00:00+00:00",
        foreign={"SomeSibling": {"sibling-stash-0": "6" * 40,
                                 "sibling-history": "5" * 40}})
    rows = {r["name"]: r for r in snap["buckets"]["elsewhere"]}
    assert not rows["sibling-history"]["void_url"]
    plan = json.loads(board.render(snap, "void-plan"))
    assert {"name": "sibling-history", "repo": "SomeSibling",
            "sha": "5" * 40} in plan["held"]
    assert "sibling-history" not in [e["name"] for e in plan["voidable"]]
    assert "sibling-history" not in [e["name"] for e in plan["due"]]


def test_void_plan_carries_the_repo_and_all_due_reaches_siblings(parser):
    snap = _snap(parser)
    assert board.render(snap, "due-names").split() == ["team-old-spike",
                                                        "sibling-stash-0"]
    plan = json.loads(board.render(snap, "void-plan"))
    assert plan["repo"] == "SomeGut"
    assert plan["due"] == [
        {"name": "sibling-stash-0", "repo": "SomeSibling", "sha": "6" * 40},
        {"name": "team-old-spike", "repo": "SomeGut", "sha": "a" * 40}]
    assert plan["held"] == [{"name": "history-kept", "repo": "SomeGut",
                             "sha": "c" * 40}]
    voidable = {(e["repo"], e["name"]) for e in plan["voidable"]}
    assert ("SomeGut", "history-kept") not in voidable
    assert ("SomeSibling", "sibling-stash-0") in voidable
    assert ("SomeGut", "__selftest_branch__") in voidable
    assert ("SomeGut", "fresh-experiment") in voidable
    # orphans are single-void only, never in the all-due set
    assert "__selftest_branch__" not in [e["name"] for e in plan["due"]]
    q = parse_qs(urlsplit(snap["void_all_due_url"]).query)
    assert q["title"] == ["void: all-due"]
    assert "history-kept" not in q["body"][0]
    assert "sibling-stash-0 (on SomeSibling)" in q["body"][0]
    # a sibling that could not be listed is left out of the plan entirely
    unlisted = json.loads(board.render(
        _snap(parser, foreign={"SomeSibling": None}), "void-plan"))
    assert all(e["repo"] == "SomeGut" for k in ("due", "voidable", "held")
               for e in unlisted[k])


def test_valid_name_refuses_anything_outside_the_namespace():
    for bad in ("", "main", "all-due", "../x", "a/../b", "/abs", "-rf",
                "refs/heads/main", "a b", "glob-*", "trail/", "a//b"):
        assert not board.valid_name(bad), bad
    for good in ("team-old-spike", "__selftest_branch__", "team/inference"):
        assert board.valid_name(good), good


# The Brain's state contract, copied rather than imported (tests stay
# hermetic; the workflow runs the real validator on the published file).
def _validate_state(s):
    assert set(("schema_version", "organ", "repo", "status", "headline",
                "updated", "pages_url", "items")) <= set(s)
    assert s["schema_version"] == 1 and s["status"] in (
        "green", "yellow", "red", "stale", "grey")
    assert "\n" not in s["headline"] and s["updated"].endswith("Z")
    for it in s["items"]:
        assert it["severity"] in ("red", "yellow", "info") and it["text"]


def test_state_is_yellow_with_due_rows_first_and_validates(parser):
    state = board.to_state(_snap(parser))
    _validate_state(state)
    assert state["status"] == "yellow" and state["organ"] == "gut"
    assert state["items"][0]["severity"] == "yellow"
    sib = [i for i in state["items"] if i["text"].startswith("due on SomeSibling")]
    assert sib and "title=void%3A+sibling-stash-0" in sib[0]["url"]
    assert state["items"][0]["url"].startswith(
        "https://github.com/SomeOrg/SomeGut/issues/new?title=void%3A+team-old-spike")
    assert "pyauto-gut void team-old-spike --yes" in state["items"][0]["prompt"]
    assert state["pages_url"] == "https://someorg.github.io/SomeGut/"
    assert len(state["items"]) <= board.STATE_ITEMS_MAX


def test_state_is_green_when_transit_is_clean_and_grey_when_unlisted(parser):
    clean = f"{'b' * 40}\t{NS}fresh-experiment\n"
    minimal = board.build_snapshot(
        LEDGER.split("## team/old-spike")[0] + "## fresh/experiment\n"
        "- type: branch\n- sweep-after: 2026-10-20\n"
        "- archive-ref: refs/heads/archive/condemned/fresh-experiment\n",
        clean, parser, TODAY, "SomeOrg", "SomeGut",
        generated="2026-09-26T06:00:00+00:00")
    state = board.to_state(minimal)
    _validate_state(state)
    assert state["status"] == "green"
    grey = board.to_state(_snap(parser, ls="", listed=False))
    _validate_state(grey)
    assert grey["status"] == "grey" and "never" not in grey["headline"]


def test_status_is_never_red(parser):
    for snap in (_snap(parser), _snap(parser, ls="", listed=False)):
        assert board.status(snap) != "red"


def test_badge(parser):
    badge = json.loads(board.render(_snap(parser), "badge"))
    assert badge == {"schemaVersion": 1, "label": "gut",
                     "message": "3 in transit · 1 due", "color": "yellow"}
    grey = json.loads(board.render(_snap(parser, ls="", listed=False), "badge"))
    assert grey["color"] == "lightgrey"


def test_markdown_surfaces(parser):
    snap = _snap(parser)
    md = board.render(snap, "md")
    assert "## Due for voiding (1)" in md and "`team-old-spike`" in md
    brief = board.render(snap, "md-brief")
    assert "1 due" in brief and "\n" not in brief


def test_cli_snapshot_roundtrip_renders_state_and_html(parser, tmp_path):
    snap_file = tmp_path / "snap.json"
    snap_file.write_text(json.dumps(_snap(parser)))
    run = lambda *a: subprocess.run(
        [sys.executable, str(GUT_HOME / "scripts" / "board.py"),
         "--brain", str(FIXTURE_BRAIN), "--snapshot", str(snap_file), *a],
        capture_output=True, text=True, check=True).stdout
    _validate_state(json.loads(run("--state")))
    page = run("--html")
    assert "/* theme:gut */" in page
    assert "Void all due (2)" in page  # 1 due in the Gut + 1 on a sibling
    # 1 due + 3 transit + 1 orphan + 1 held on another repo
    assert page.count("class='void'") == 6
    assert "on SomeSibling" in page
    assert "no ledger entry" in page
    assert "retire entry" in page


def test_collect_reads_a_fixture_ledger_and_a_local_remote(tmp_path):
    # A real `git ls-remote` against a local bare repo — no network.
    remote = tmp_path / "remote.git"
    work = tmp_path / "work"
    git = lambda *a, cwd=None: subprocess.run(
        ["git", *a], cwd=cwd, check=True, capture_output=True, text=True)
    git("init", "--bare", "-q", str(remote))
    git("init", "-q", str(work))
    git("-c", "user.name=t", "-c", "user.email=t@example.org", "commit",
        "--allow-empty", "-q", "-m", "x", cwd=work)
    git("remote", "add", "origin", str(remote), cwd=work)
    git("push", "-q", "origin", f"HEAD:{NS}team-old-spike", cwd=work)
    mind = tmp_path / "mind"
    mind.mkdir()
    (mind / "condemned.md").write_text(LEDGER)
    snap = board.collect(mind, FIXTURE_BRAIN, "origin", work, TODAY)
    assert snap["refs_listed"] and snap["ref_count"] == 1
    assert _names(snap, "due") == ["team-old-spike"]
    # owner cannot be derived from a local path: said, not guessed
    assert any("owner" in e for e in snap["errors"])
    assert board.to_state(snap)["pages_url"] == "./"


def test_general_checkin_preserves_destructive_approval(parser, monkeypatch):
    captured = {}
    def panel(key, title, description, prompt, **kwargs):
        captured.update(kwargs, prompt=prompt)
        return "<section data-orchestration-panel></section>"
    board._THEME_BRAIN[0] = FIXTURE_BRAIN
    monkeypatch.setattr(board.theme(), "orchestration_panel", panel)
    snap = _snap(parser)
    rendered = board.render(snap, "html")
    assert rendered.index("data-orchestration-panel") < rendered.index('id="inventory"')
    assert "explicit human authorization" in captured["prompt"]
    assert "a general check-in grants none" in captured["prompt"]
    assert {link["href"] for link in captured["work_links"]} == {
        "https://github.com/SomeOrg/SomeGut",
        "https://github.com/SomeOrg/PyAutoMind/blob/main/condemned.md"}
    assert snap["void_all_due_url"] in rendered.replace("&amp;", "&")
