#!/usr/bin/env python3
"""scripts/board.py — the PyAutoGut Dashboard.

A clear overview of **everything in the Gut** — every condemned ref held
under ``refs/heads/archive/condemned/<name>`` on this repo's remote, read
against the Mind's ``condemned.md`` ledger — and a button on every voidable
row that removes it permanently.

**Truth is two sources, never one.** ``collect()`` lists the refs with
``git ls-remote`` and parses the ledger with the Brain's parser
(``agents/conductors/hygiene/_hygiene_condemned.py``, imported from a
checked-out PyAutoBrain like the theme is), then reconciles them. Drift in
either direction is shown, not hidden:

* **due** — ledger entry past its ``sweep-after`` date, ref present;
* **in transit** — ref present, ``sweep-after`` still ahead (days left);
* **held** — ref present, entry undated (``never``): kept until a human asks
  in a session; never one-tap voidable, never in ``void: all-due``;
* **orphan refs** — a ref no ledger entry claims;
* **dangling entries** — an entry whose ``archive-ref`` is missing from the
  remote (split out as **voided — entry still in condemned.md** when a recent
  ``void:`` issue names it: the void workflow cannot edit the Mind, so the
  ledger row is retired by a session);
* **held on another repo** — an entry whose ``archive-ref`` says the ref
  lives on a sibling repo's origin (``… on <Repo> origin``): read with a
  best-effort ``ls-remote`` of that repo, flagged when due, voidable only in
  a session (this repo's token cannot delete another repo's refs);
* **history-only** — ``archive-ref: n/a`` (bytes live in remote history):
  listed for completeness, never voidable;
* **recently voided** — the last closed ``void:`` issues (best-effort).

**The button is a prefilled GitHub issue.** "Void permanently" opens
``issues/new?title=void:+<name>&labels=void&body=…``; pressing Submit is the
human's ``--yes``. ``.github/workflows/void.yml`` deletes the ref with this
repo's own token, comments the pre-delete SHA, closes the issue and
re-renders this board. ``void: all-due`` voids every *due* row at once.

**Shape** (mirrors ``PyAutoHands/autohands/board.py``): ``collect()`` is the
only I/O and degrades per-section into ``errors[]``; ``render(snapshot,
fmt)`` is pure — ``md | md-brief | html | json | badge | state`` plus the
void workflow's ``due-names`` / ``void-plan``.
Owner and repo come from ``git remote`` — no instance names live here (the
tenant firewall).

Usage:
    python scripts/board.py [--mind P] [--brain P] [--remote origin] [--repo P]
                            [--today YYYY-MM-DD]
                            (--collect OUT | --snapshot F)
                            (--md|--md-brief|--html|--json|--badge|--state|
                             --due-names|--void-plan)
"""

from __future__ import annotations

import datetime
import fnmatch
import html as _html
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote_plus

GUT_HOME = Path(__file__).resolve().parents[1]
BOARD_KEY = "gut"  # this board's entry in the Brain's palette table
NS = "refs/heads/archive/condemned/"
SCHEMA_VERSION = 1
PARSER_REL = Path("agents") / "conductors" / "hygiene" / "_hygiene_condemned.py"
LEDGER = "condemned.md"
RECENT_VOIDED = 10
BUCKETS = ("due", "transit", "held", "orphans", "dangling", "voided_pending",
           "elsewhere", "history")
# The rows the one-tap button may void: refs in THIS repo that a human has not
# asked to hold. Held (undated) rows are voided only in a session.
VOIDABLE = ("due", "transit", "orphans")

# A void name is appended to NS and nothing else, so it cannot leave the
# namespace — but it must also be a sane ref tail: no traversal, no leading
# dash (an option to git), no globs, never `main`.
_NAME_RE = re.compile(r"^[A-Za-z0-9._][A-Za-z0-9._/-]*$")


def valid_name(name: str) -> bool:
    """True for a ref tail the void workflow may act on (its bash twin is
    ``valid_name`` in ``.github/workflows/void.yml``)."""
    return bool(name) and name != "main" and name != "all-due" \
        and ".." not in name and "//" not in name \
        and not name.endswith("/") and not name.startswith("refs/") \
        and bool(_NAME_RE.match(name))


# --- locating the Brain and the Mind ------------------------------------------
def _brain_home(brain: str | None = None) -> Path | None:
    for cand in (brain, os.environ.get("PYAUTO_BRAIN"), GUT_HOME / "PyAutoBrain",
                 GUT_HOME.parent / "PyAutoBrain"):
        if cand and ((Path(cand) / "board").is_dir()
                     or (Path(cand) / PARSER_REL).is_file()):
            return Path(cand)
    return None


def _mind_home(mind: str | None = None) -> Path | None:
    for cand in (mind, os.environ.get("PYAUTO_MIND"), GUT_HOME / "PyAutoMind",
                 GUT_HOME.parent / "PyAutoMind"):
        if cand and (Path(cand) / LEDGER).is_file():
            return Path(cand)
    return None


def load_parser(brain: str | Path | None = None):
    """The Brain's condemned.md parser (``parse_manifest``, ``classify``,
    ``ref_name``), loaded by path so the ledger is read one way everywhere."""
    home = _brain_home(str(brain) if brain else None)
    path = home / PARSER_REL if home else None
    if not path or not path.is_file():
        raise RuntimeError(
            "the condemned.md parser (PyAutoBrain/" + PARSER_REL.as_posix() +
            ") is not in reach — pass --brain or set PYAUTO_BRAIN")
    spec = importlib.util.spec_from_file_location(
        f"_gut_condemned_parser_{abs(hash(str(path)))}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for fn in ("parse_manifest", "classify", "ref_name"):
        if not hasattr(mod, fn):
            raise RuntimeError(f"{path} has no {fn}() — the Brain checkout "
                               "predates PyAutoGut#9")
    return mod


_THEME_BRAIN: list = [None]


def theme():
    """The shared theme module (PyAutoBrain/board/_theme.py). Only the html
    path needs it; every other surface renders with no Brain in reach."""
    home = _brain_home(_THEME_BRAIN[0])
    board = home / "board" if home else None
    if board and (board / "_theme.py").is_file():
        if str(board) not in sys.path:
            sys.path.insert(0, str(board))
        import _theme
        return _theme
    raise RuntimeError(
        "the shared board theme (PyAutoBrain/board/_theme.py) is not in reach "
        "— check PyAutoBrain out beside this repo or pass --brain")


# --- identity (derived, never hardcoded — tenant firewall) -------------------
def parse_owner_repo(url: str) -> tuple[str, str]:
    m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$", url.strip())
    return (m.group(1), m.group(2)) if m else ("", "")


def _owner_repo(repo_path: Path, remote: str) -> tuple[str, str]:
    out = subprocess.run(["git", "-C", str(repo_path), "remote", "get-url",
                          remote], capture_output=True, text=True).stdout
    return parse_owner_repo(out)


# --- pure reconciliation --------------------------------------------------------
def parse_ls_remote(text: str) -> dict[str, str]:
    """``git ls-remote`` output → ``{name: sha}`` for refs under NS only."""
    refs = {}
    for line in (text or "").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].startswith(NS):
            refs[parts[1][len(NS):]] = parts[0]
    return refs


_HOST_RE = re.compile(r"\bon\s+`?([A-Za-z0-9_.-]+)`?\s+origin\b")


def ref_host(entry: dict) -> str | None:
    """The repo an entry's ``archive-ref`` says the ref lives on
    (``… on <Repo> origin``), or None when it does not say."""
    m = _HOST_RE.search(entry.get("archive-ref") or "")
    return m.group(1) if m else None


def _date(s):
    try:
        return datetime.date.fromisoformat(str(s or "").strip())
    except ValueError:
        return None


def _clip(text: object, limit: int = 160) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def repo_url(snap: dict) -> str:
    o, r = snap.get("owner"), snap.get("repo")
    return f"https://github.com/{o}/{r}" if o and r else ""


def pages_url(snap: dict) -> str:
    o, r = str(snap.get("owner") or "").lower(), snap.get("repo") or ""
    return f"https://{o}.github.io/{r}/" if o and r else ""


def void_issue_url(snap: dict, row: dict) -> str:
    """The one-tap button: a prefilled issue whose submission voids the ref."""
    base = repo_url(snap)
    if not base or not row.get("name") or not row.get("sha"):
        return ""
    body = (f"Void `{NS}{row['name']}` permanently.\n\n"
            f"- entry: {row.get('entry') or '(no ledger entry — orphan ref)'}\n"
            f"- reason: {_clip(row.get('reason') or '-', 300)}\n"
            f"- sweep-after: {row.get('sweep_after') or '-'}\n"
            f"- pre-delete sha: {row['sha']}\n\n"
            "Submitting this issue voids the ref permanently. It is processed "
            "by the Gut Void workflow (void.yml); recovery is no longer "
            "possible afterwards.")
    return (f"{base}/issues/new?title={quote_plus('void: ' + row['name'])}"
            f"&labels=void&body={quote_plus(body)}")


def void_all_due_url(snap: dict) -> str:
    base = repo_url(snap)
    due = (snap.get("buckets") or {}).get("due") or []
    if not base or not due:
        return ""
    names = [r["name"] for r in due]
    shown = names[:40]
    listing = "\n".join(f"- {n}" for n in shown)
    if len(names) > len(shown):
        listing += f"\n- … and {len(names) - len(shown)} more"
    body = (f"Void every Gut ref whose ledger entry is past its sweep-after "
            f"date — {len(names)} ref(s) as of {snap.get('today')}:\n\n"
            f"{listing}\n\nThe workflow recomputes the due set from "
            "condemned.md when it runs; undated (held) entries and refs with "
            "no ledger entry are never included.\n\nSubmitting this issue "
            "voids the refs permanently. Recovery is no longer possible "
            "afterwards.")
    return (f"{base}/issues/new?title={quote_plus('void: all-due')}"
            f"&labels=void&body={quote_plus(body)}")


def _session_void(row: dict, why: str) -> str:
    return (f"Void the Gut ref `{row['name']}` ({why}): in PyAutoGut run "
            f"`bin/pyauto-gut void {row['name']} --yes`, then retire its "
            "entry from PyAutoMind/condemned.md in a Mind commit.")


def _foreign_void(row: dict) -> str:
    return (f"Void the condemned ref `{NS}{row['name']}` held on "
            f"{row['host']} (ledger entry `{row['entry']}`, sweep-after "
            f"{row.get('sweep_after') or '-'}): from a {row['host']} checkout "
            f"run `git push origin --delete {NS}{row['name']}` after checking "
            f"`git ls-remote origin {NS}{row['name']}` still reads "
            f"{(row.get('sha') or '?')[:12]}, then retire the entry from "
            "PyAutoMind/condemned.md.")


def _retire_prompt(row: dict, how: str) -> str:
    return (f"Retire the `{row['entry']}` entry from PyAutoMind/condemned.md "
            f"(and its contents line): its Gut ref "
            f"`{NS}{row.get('name') or '?'}` is {how}. The bytes are gone, so "
            "the ledger row is only bookkeeping now.")


def reconcile(entries, refs, parser, today, repo, voided_names=(),
              foreign=None):
    """Entries × refs → the board's buckets (lists of row dicts). Pure.

    ``foreign`` maps a sibling repo name to its ``{name: sha}`` archive refs
    (or None when that repo could not be listed) for entries whose ref lives
    on another repo's origin.
    """
    buckets = {b: [] for b in BUCKETS}
    claimed: set[str] = set()
    voided_names = set(voided_names)
    foreign = foreign or {}
    for e in entries:
        base = {"entry": e.get("name", "?"), "type": e.get("type") or "-",
                "reason": e.get("reason") or "", "condemned":
                e.get("condemned") or "", "sweep_after":
                (e.get("sweep-after") or "").strip(), "archive_ref":
                _clip(e.get("archive-ref") or "", 240)}
        name = parser.ref_name(e)
        if not name:
            buckets["history"].append({**base, "name": None, "sha": "",
                                       "why": "archive-ref n/a — bytes live in "
                                              "remote history"})
            continue
        names = (sorted(n for n in refs if fnmatch.fnmatchcase(n, name))
                 if "*" in name else ([name] if name in refs else []))
        host = ref_host(e)
        if not names:
            if host and repo and host != repo:
                listed = foreign.get(host)
                sha = (listed or {}).get(name, "")
                if listed is not None and not sha:
                    buckets["dangling"].append({**base, "name": name, "sha": "",
                                                "host": host})
                    continue
                row = {**base, "name": name, "sha": sha, "host": host,
                       "why": f"held on {host}, not in the Gut" +
                              ("" if listed is not None else
                               " (could not be listed this render)")}
                d = _date(base["sweep_after"])
                if d is not None and d <= today and sha:
                    row["days"] = (today - d).days
                    row["overdue"] = True
                buckets["elsewhere"].append(row)
            elif name in voided_names:
                buckets["voided_pending"].append({**base, "name": name,
                                                  "sha": ""})
            else:
                buckets["dangling"].append({**base, "name": name, "sha": ""})
            continue
        d = _date(base["sweep_after"])
        for n in names:
            claimed.add(n)
            row = {**base, "name": n, "sha": refs[n]}
            if d is None:
                buckets["held"].append(row)
            elif d <= today:
                buckets["due"].append({**row, "days": (today - d).days})
            else:
                buckets["transit"].append({**row, "days": (d - today).days})
    for n in sorted(set(refs) - claimed):
        buckets["orphans"].append({"entry": "", "name": n, "sha": refs[n],
                                   "type": "-", "reason": "",
                                   "condemned": "", "sweep_after": ""})
    buckets["due"].sort(key=lambda r: (-r["days"], r["name"]))
    buckets["transit"].sort(key=lambda r: (r["days"], r["name"]))
    buckets["elsewhere"].sort(key=lambda r: (-r.get("days", -1), r["name"]))
    return buckets


def build_snapshot(ledger_text, ls_remote_text, parser, today, owner, repo,
                   voided=(), errors=(), refs_listed=True, generated=None,
                   foreign=None):
    """The whole snapshot from already-fetched inputs. Pure (tests call it)."""
    refs = parse_ls_remote(ls_remote_text) if refs_listed else {}
    entries = parser.parse_manifest(ledger_text or "")
    voided = list(voided)
    names = {n for v in voided for n in v.get("names") or []}
    snap = {
        "schema_version": SCHEMA_VERSION,
        "generated": generated or datetime.datetime.now(
            datetime.timezone.utc).isoformat(),
        "today": today.isoformat(),
        "owner": owner, "repo": repo,
        "refs_listed": bool(refs_listed),
        "ref_count": len(refs),
        "entry_count": len(entries),
        "buckets": reconcile(entries, refs, parser, today, repo, names,
                             foreign)
        if refs_listed else {b: [] for b in BUCKETS},
        "voided": voided[:RECENT_VOIDED],
        "errors": list(errors),
    }
    for key, rows in snap["buckets"].items():
        for row in rows:
            row["void_url"] = (void_issue_url(snap, row)
                               if key in VOIDABLE and row.get("sha") else "")
    snap["void_all_due_url"] = void_all_due_url(snap)
    return snap


# --- I/O ------------------------------------------------------------------------
def _recent_voided(owner: str, repo: str) -> list[dict]:
    out = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/issues?state=closed&per_page=100"
                      "&sort=updated&direction=desc"],
        capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise RuntimeError(_clip(out.stderr or "gh api failed", 200))
    rows = []
    for it in json.loads(out.stdout or "[]"):
        title = str(it.get("title") or "")
        if "pull_request" in it or not title.lower().startswith("void:"):
            continue
        if it.get("state_reason") not in (None, "completed"):
            continue
        target = title[5:].strip()
        rows.append({"number": it.get("number"), "title": title,
                     "url": it.get("html_url") or "",
                     "closed_at": it.get("closed_at") or "",
                     "names": [] if target == "all-due" else [target]})
    rows.sort(key=lambda r: r["closed_at"], reverse=True)
    return rows[:RECENT_VOIDED]


def collect(mind=None, brain=None, remote="origin", repo_path=None,
            today=None) -> dict:
    """Gather the snapshot. Degrades per-section into errors[]; never raises
    for a source that cannot be read (a missing parser is the one exception:
    without it the ledger cannot be read at all)."""
    repo_path = Path(repo_path or GUT_HOME)
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    errors: list[str] = []
    parser = load_parser(brain)
    owner, repo = _owner_repo(repo_path, remote)
    if not owner:
        errors.append(f"could not derive owner/repo from git remote '{remote}'")
    ls = subprocess.run(["git", "-C", str(repo_path), "ls-remote", "--heads",
                         remote, "archive/condemned/*"],
                        capture_output=True, text=True, timeout=120)
    refs_listed = ls.returncode == 0
    if not refs_listed:
        errors.append("git ls-remote: " + _clip(ls.stderr or "failed", 200))
    home = _mind_home(mind)
    text = ""
    if home is None:
        errors.append(f"{LEDGER} not found — pass --mind")
    else:
        text = (home / LEDGER).read_text(encoding="utf-8")
    foreign = {}
    if owner:
        hosts = {ref_host(e) for e in parser.parse_manifest(text)
                 if parser.ref_name(e)} - {None, repo}
        for host in sorted(hosts):
            out = subprocess.run(
                ["git", "ls-remote", "--heads",
                 f"https://github.com/{owner}/{host}.git",
                 "archive/condemned/*"],
                capture_output=True, text=True, timeout=120)
            if out.returncode == 0:
                foreign[host] = parse_ls_remote(out.stdout)
            else:
                foreign[host] = None
                errors.append(f"git ls-remote {host}: "
                              + _clip(out.stderr or "failed", 160))
    voided = []
    if owner:
        try:
            voided = _recent_voided(owner, repo)
        except (OSError, RuntimeError, ValueError,
                subprocess.SubprocessError) as e:
            errors.append(f"recently voided: {e}")
    return build_snapshot(text, ls.stdout, parser, today, owner, repo, voided,
                          errors, refs_listed, foreign=foreign)


# --- counts / status ------------------------------------------------------------
def counts(snap: dict) -> dict:
    b = snap.get("buckets") or {}
    c = {k: len(b.get(k) or []) for k in BUCKETS}
    c["due_elsewhere"] = sum(1 for r in b.get("elsewhere") or []
                             if r.get("overdue"))
    return c


def status(snap: dict) -> str:
    """grey (nothing listed) · yellow (anything due, orphaned or dangling) ·
    green (transit is clean). Never red: nothing in the Gut can break."""
    if not snap.get("refs_listed"):
        return "grey"
    c = counts(snap)
    if c["due"] or c["due_elsewhere"] or c["orphans"] or c["dangling"] \
            or c["voided_pending"]:
        return "yellow"
    return "green"


def _summary(snap: dict) -> str:
    c = counts(snap)
    bits = [f"{c['due']} due", f"{c['transit']} in transit",
            f"{c['held']} held"]
    if c["due_elsewhere"]:
        bits.append(f"{c['due_elsewhere']} due on other repos")
    if c["orphans"]:
        bits.append(f"{c['orphans']} orphan ref(s)")
    if c["dangling"] + c["voided_pending"]:
        bits.append(f"{c['dangling'] + c['voided_pending']} dangling entr"
                    f"{'y' if c['dangling'] + c['voided_pending'] == 1 else 'ies'}")
    return " · ".join(bits)


# --- markdown -------------------------------------------------------------------
_TITLES = {
    "due": "Due for voiding",
    "transit": "In transit",
    "held": "Held (undated — void only on explicit request)",
    "orphans": "Orphan refs (no ledger entry)",
    "dangling": "Dangling entries (ref missing)",
    "voided_pending": "Voided — entry still in condemned.md",
    "elsewhere": "Held on another repo (void in a session)",
    "history": "History-only (not voidable here)",
}


def _render_md(snap: dict) -> str:
    out = [f"# PyAutoGut Dashboard", "",
           f"**{status(snap).upper()}** — {_summary(snap)} "
           f"({snap.get('ref_count', 0)} refs, {snap.get('entry_count', 0)} "
           f"ledger entries, as of {snap.get('today')})", ""]
    if snap.get("void_all_due_url"):
        out += [f"[Void all due →]({snap['void_all_due_url']})", ""]
    for key in BUCKETS:
        rows = (snap.get("buckets") or {}).get(key) or []
        if not rows:
            continue
        out += [f"## {_TITLES[key]} ({len(rows)})", "",
                "| ref | entry | sweep-after | sha | action |",
                "|---|---|---|---|---|"]
        for r in rows:
            act = f"[void]({r['void_url']})" if r.get("void_url") else "-"
            days = (f" ({r['days']}d "
                    f"{'over' if key in ('due', 'elsewhere') else 'left'})"
                    if "days" in r else "")
            out.append(f"| `{r.get('name') or '-'}` | {r.get('entry') or '-'} "
                       f"| {_clip(r.get('sweep_after') or '-', 40)}{days} "
                       f"| {(r.get('sha') or '-')[:10]} | {act} |")
        out.append("")
    if snap.get("voided"):
        out += ["## Recently voided", ""]
        out += [f"- [#{v['number']}]({v['url']}) {v['title']} "
                f"({str(v.get('closed_at'))[:10]})" for v in snap["voided"]]
        out.append("")
    if snap.get("errors"):
        out += ["## Unavailable this render", ""]
        out += [f"- {e}" for e in snap["errors"]]
        out.append("")
    return "\n".join(out)


def _render_md_brief(snap: dict) -> str:
    bits = [f"\U0001f5d1️ **{status(snap).upper()}** — {_summary(snap)}"]
    url = pages_url(snap)
    if url:
        bits.append(f"[dashboard →]({url})")
    return " · ".join(bits)


# --- html -----------------------------------------------------------------------
_LEDE = ("Everything the Gut holds, read against the Mind's "
         "<code>condemned.md</code>. <b>Void permanently</b> opens a prefilled "
         "issue — submitting it is the yes. Tap \U0001f4cb to copy a command "
         "for a Claude Code session instead.")

_EXTRA_CSS = """
.acts{display:flex;flex-wrap:wrap;gap:.35rem;margin-top:.4rem}
a.void{display:inline-block;padding:.34rem .7rem;border-radius:9px;
 font-size:.85rem;font-weight:650;color:var(--bad);border:1px solid var(--bad);
 background:transparent;white-space:nowrap}
a.void:hover{background:var(--bad);color:#fff;text-decoration:none}
a.void.all{margin:.3rem 0 .6rem}
.flag{color:var(--warn);font-weight:600;font-size:.85em}
.sha{font-size:.8em}
.errors{margin-top:1.2rem}
footer{margin-top:2rem;color:var(--muted);font-size:.82em}
"""


def _esc(v) -> str:
    return _html.escape(str(v), quote=True)


def _chip(payload: str, label: str) -> str:
    return (f"<button class='copy text' type='button' title='{_esc(label)}' "
            f"data-cmd=\"{_esc(payload)}\">\U0001f4cb {_esc(label)}</button>")


def _row_html(key: str, r: dict) -> str:
    name = r.get("name") or "-"
    head = f"<b>{_esc(name)}</b>"
    if r.get("entry") and r.get("entry") != name:
        head += f" <span class='muted'>· {_esc(r['entry'])}</span>"
    facts = []
    if r.get("type") and r["type"] != "-":
        facts.append(_esc(r["type"]))
    if r.get("condemned"):
        facts.append(f"condemned {_esc(r['condemned'])}")
    if r.get("sweep_after"):
        facts.append(f"sweep-after {_esc(_clip(r['sweep_after'], 60))}")
    if "days" in r:
        facts.append(f"<b class='warn'>{r['days']}d over</b>"
                     if key in ("due", "elsewhere") else f"{r['days']}d left")
    if r.get("sha"):
        facts.append(f"<code class='sha'>{_esc(r['sha'][:12])}</code>")
    lines = [head]
    if key == "orphans":
        lines.append("<span class='flag'>no ledger entry</span>")
    if r.get("why"):
        lines.append(f"<span class='muted'>{_esc(r['why'])}</span>")
    if r.get("reason"):
        lines.append(f"<span class='muted'>{_esc(_clip(r['reason'], 180))}</span>")
    if facts:
        lines.append(f"<span class='facets'>{' · '.join(facts)}</span>")
    acts = []
    if r.get("void_url"):
        acts.append(f"<a class='void' href=\"{_esc(r['void_url'])}\">"
                    "Void permanently</a>")
    if key == "elsewhere" and r.get("sha"):
        acts.append(_chip(_foreign_void(r), "void via session"))
    elif r.get("sha"):
        acts.append(_chip(f"bin/pyauto-gut recover {name}", "recover"))
        why = {"due": "sweep-after passed", "orphans": "no ledger entry",
               "held": "held — explicit human request"}.get(key, "in transit")
        acts.append(_chip(_session_void(r, why), "void via session"))
    if key == "dangling":
        acts.append(_chip(_retire_prompt(r, "missing from the Gut remote"),
                          "retire entry"))
    if key == "voided_pending":
        acts.append(_chip(_retire_prompt(r, "voided (a closed void: issue)"),
                          "retire entry"))
    body = "<br>".join(lines)
    act = f"<span class='acts'>{''.join(acts)}</span>" if acts else ""
    return f"<div class='task'><p>{body}{act}</p></div>"


_FOLD_AFTER = 8


def _section_html(key: str, rows: list, snap: dict) -> str:
    if not rows:
        return ""
    head = (f"<h2>{_esc(_TITLES[key])} <span class='muted'>({len(rows)})"
            "</span></h2>")
    extra = ""
    if key == "due" and snap.get("void_all_due_url"):
        extra = (f"<a class='void all' href=\"{_esc(snap['void_all_due_url'])}\">"
                 f"Void all due ({len(rows)})</a>")
    items = [_row_html(key, r) for r in rows]
    if len(items) > _FOLD_AFTER + 2:
        items = items[:_FOLD_AFTER] + [
            f"<details><summary>{len(items) - _FOLD_AFTER} more</summary>"
            + "".join(items[_FOLD_AFTER:]) + "</details>"]
    return head + extra + "".join(items)


def _boards_nav(snap: dict) -> str:
    owner = str(snap.get("owner") or "").lower()
    if not owner:
        return ""
    t_ = theme()
    links = getattr(t_, "board_links", None)
    return t_.boards_footer(links(f"https://{owner}.github.io", BOARD_KEY),
                            BOARD_KEY) if links else ""


def _render_html(snap: dict) -> str:
    t_ = theme()
    c = counts(snap)
    st = status(snap)
    tone = {"green": "ok", "yellow": "warn", "grey": "muted"}[st]
    stats = t_.stats((c["due"], "due"), (c["transit"], "in transit"),
                     (c["held"], "held"), (c["orphans"], "orphans"),
                     (c["dangling"] + c["voided_pending"], "dangling"),
                     (c["history"], "history-only")) \
        if hasattr(t_, "stats") else ""
    sections = "".join(_section_html(k, (snap.get("buckets") or {}).get(k) or [],
                                     snap) for k in BUCKETS)
    if not snap.get("refs_listed"):
        sections = ("<p class='muted'>The Gut's refs could not be listed this "
                    "render — nothing is shown rather than a guess.</p>" +
                    sections)
    elif not sections:
        sections = "<p class='muted'>The Gut is empty.</p>"
    voided = ""
    if snap.get("voided"):
        voided = "<h2>Recently voided</h2>" + "".join(
            f"<div class='task'><p><a href=\"{_esc(v['url'])}\">#{v['number']}"
            f"</a> {_esc(v['title'])} <span class='muted'>"
            f"{_esc(str(v.get('closed_at'))[:10])}</span></p></div>"
            for v in snap["voided"])
    errors = ""
    if snap.get("errors"):
        errors = ("<div class='errors'><p class='muted'>unavailable this "
                  "render:</p><ul class='muted'>" + "".join(
                      f"<li>{_esc(e)}</li>" for e in snap["errors"]) +
                  "</ul></div>")
    gh = repo_url(snap)
    gh_link = f' · <a href="{gh}">GitHub</a>' if gh else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PyAutoGut Dashboard</title>
<style>{t_.css(BOARD_KEY)}{_EXTRA_CSS}</style>
</head>
<body>
{t_.hero(BOARD_KEY, "Dashboard", _LEDE)}
<p class="verdict {tone}"><b class="{tone}">{st.upper()}</b>
<span class="muted">{_esc(_summary(snap))}</span></p>
{stats}
<p class="muted">{snap.get('ref_count', 0)} refs on the remote ·
{snap.get('entry_count', 0)} ledger entries · as of {_esc(snap.get('today'))} ·
<a href="dashboard.md">markdown version</a>{gh_link}</p>
{sections}
{voided}
{errors}
{_boards_nav(snap)}
<footer>Rendered by <code>scripts/board.py</code> from <code>git ls-remote</code>
+ the Mind's <code>condemned.md</code> · generated
{_esc(snap.get('generated') or '?')}.</footer>
<script>{t_.JS}</script>
</body></html>
"""


# --- badge / state --------------------------------------------------------------
def badge_endpoint(snap: dict) -> dict:
    if not snap.get("refs_listed"):
        return {"schemaVersion": 1, "label": "gut", "message": "unknown",
                "color": "lightgrey"}
    c = counts(snap)
    return {"schemaVersion": 1, "label": "gut",
            "message": f"{c['transit']} in transit · {c['due']} due",
            "color": "yellow" if status(snap) == "yellow" else "green"}


def _iso_z(ts) -> str:
    try:
        t = datetime.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=datetime.timezone.utc)
    except (TypeError, ValueError):
        t = datetime.datetime.now(datetime.timezone.utc)
    return t.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


STATE_ITEMS_MAX = 20


def to_state(snap: dict) -> dict:
    """The organ-cockpit feed (contract v1, owned by PyAutoBrain
    ``board/_state.py``): due rows first (yellow, url = the row's one-tap
    void issue), then orphans / dangling / voided-pending (info), then
    collection errors (info); capped at 20."""
    st = status(snap)
    b = snap.get("buckets") or {}
    items = []
    for r in b.get("due") or []:
        items.append({"severity": "yellow",
                      "text": _clip(f"due: {r['name']} — sweep-after "
                                    f"{r['sweep_after']} ({r['days']}d over)"),
                      "url": r.get("void_url") or None,
                      "prompt": _session_void(r, "sweep-after passed")})
    for r in b.get("elsewhere") or []:
        if r.get("overdue"):
            items.append({"severity": "yellow",
                          "text": _clip(f"due on {r['host']}: {r['name']} — "
                                        f"sweep-after {r['sweep_after']} "
                                        f"({r['days']}d over)"),
                          "url": None, "prompt": _foreign_void(r)})
    for r in b.get("orphans") or []:
        items.append({"severity": "info",
                      "text": _clip(f"orphan ref: {r['name']} — no ledger entry"),
                      "url": r.get("void_url") or None,
                      "prompt": _session_void(r, "no ledger entry")})
    for key, how in (("dangling", "missing from the Gut remote"),
                     ("voided_pending", "voided (a closed void: issue)")):
        for r in b.get(key) or []:
            items.append({"severity": "info",
                          "text": _clip(f"{'dangling' if key == 'dangling' else 'voided'}"
                                        f" entry: {r['entry']} — ref "
                                        f"{r.get('name')} {how}"),
                          "url": None, "prompt": _retire_prompt(r, how)})
    items += [{"severity": "info", "text": _clip(f"unavailable this render: {e}"),
               "url": None, "prompt": None} for e in snap.get("errors") or []]
    if st == "grey":
        headline = "GREY — the Gut's refs could not be listed"
    elif st == "green":
        headline = _summary(snap)
    else:
        headline = f"YELLOW — {_summary(snap)}"
    return {
        "schema_version": 1,
        "organ": BOARD_KEY,
        "repo": snap.get("repo") or "PyAutoGut",
        "status": st,
        "headline": _clip(headline),
        "updated": _iso_z(snap.get("generated")),
        "pages_url": pages_url(snap) or "./",
        "items": items[:STATE_ITEMS_MAX],
    }


def render(snap: dict, fmt: str = "md") -> str:
    if fmt == "md":
        return _render_md(snap)
    if fmt == "md-brief":
        return _render_md_brief(snap)
    if fmt == "html":
        return _render_html(snap)
    if fmt == "json":
        return json.dumps({**snap, "pages_url": pages_url(snap)}, indent=2,
                          sort_keys=True)
    if fmt == "badge":
        return json.dumps(badge_endpoint(snap))
    if fmt == "state":
        return json.dumps(to_state(snap), indent=2)
    if fmt == "due-names":
        # The void workflow's `void: all-due` set: due rows only — undated,
        # orphan, other-repo and history-only rows are never in it.
        return "\n".join(r["name"] for r in (snap.get("buckets") or {})
                         .get("due") or [] if valid_name(r["name"]))
    if fmt == "void-plan":
        # What void.yml may act on, by bucket: `due` (the all-due set),
        # `voidable` (due + transit + orphans — one-tap single voids) and
        # `held` (refused: undated entries are voided only in a session).
        b = snap.get("buckets") or {}
        pick = lambda keys: sorted({r["name"] for k in keys
                                    for r in b.get(k) or []
                                    if r.get("sha") and valid_name(r["name"])})
        return json.dumps({"refs_listed": bool(snap.get("refs_listed")),
                           "due": pick(("due",)), "voidable": pick(VOIDABLE),
                           "held": pick(("held",))}, indent=2)
    raise ValueError(f"unknown board fmt: {fmt!r}")


# --- CLI ------------------------------------------------------------------------
FORMATS = ("md", "md-brief", "html", "json", "badge", "state", "due-names",
           "void-plan")


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="board.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    for f in FORMATS:
        g.add_argument(f"--{f}", action="store_true")
    ap.add_argument("--mind", help="PyAutoMind checkout (holds condemned.md)")
    ap.add_argument("--brain", help="PyAutoBrain checkout (parser + theme)")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--repo", help="the PyAutoGut checkout to ls-remote from")
    ap.add_argument("--today", help="pin the reference date (YYYY-MM-DD)")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--collect", metavar="OUT")
    src.add_argument("--snapshot", metavar="F")
    ns = ap.parse_args(argv)
    _THEME_BRAIN[0] = ns.brain
    today = _date(ns.today) if ns.today else None

    if ns.collect:
        snap = collect(ns.mind, ns.brain, ns.remote, ns.repo, today)
        Path(ns.collect).write_text(json.dumps(snap, indent=2, sort_keys=True)
                                    + "\n", encoding="utf-8")
        print(f"collected → {ns.collect} ({snap['ref_count']} refs, "
              f"{snap['entry_count']} entries; {_summary(snap)}; "
              f"{len(snap['errors'])} error(s))", file=sys.stderr)
        return 0
    snap = (json.loads(Path(ns.snapshot).read_text(encoding="utf-8"))
            if ns.snapshot else collect(ns.mind, ns.brain, ns.remote, ns.repo,
                                        today))
    fmt = next((f for f in FORMATS if getattr(ns, f.replace("-", "_"))), "md")
    print(render(snap, fmt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
