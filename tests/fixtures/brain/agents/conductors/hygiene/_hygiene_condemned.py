"""A tiny stand-in for PyAutoBrain's condemned.md parser — same interface
(parse_manifest, classify, ref_name), so the Gut's tests stay hermetic and
never import a Brain checkout."""

import datetime
import re

_HEAD = re.compile(r"^##\s+(?!#)(.+?)\s*$")
_FIELD = re.compile(r"^-\s*([A-Za-z][\w-]*)\s*:\s*(.*?)\s*$")
_REF = re.compile(r"refs/heads/archive/condemned/([A-Za-z0-9._*][A-Za-z0-9._/*-]*)")


def parse_manifest(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    out, cur = [], None
    for line in text.splitlines():
        h = _HEAD.match(line)
        if h:
            if cur and (cur.get("type") or cur.get("locator")):
                out.append(cur)
            cur = {"name": h.group(1)}
        elif cur is not None and (f := _FIELD.match(line)):
            cur[f.group(1).lower()] = f.group(2)
    if cur and (cur.get("type") or cur.get("locator")):
        out.append(cur)
    return out


def classify(entries, today):
    due, pending, undated = [], [], []
    for e in entries:
        try:
            d = datetime.date.fromisoformat((e.get("sweep-after") or "").strip())
        except ValueError:
            undated.append(e)
            continue
        (due if d <= today else pending).append(e)
    return due, pending, undated


def ref_name(entry):
    text = (entry.get("archive-ref") or "").strip()
    if not text or text.strip("`").lower().startswith("n/a"):
        return None
    m = _REF.search(text)
    return m.group(1).rstrip("./") if m else None
