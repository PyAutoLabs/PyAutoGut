"""A minimal stand-in for PyAutoBrain's board/_theme.py (same call surface
the Gut renderer uses), so the html test needs no Brain checkout."""

JS = "/* copy */"


def css(key):
    return f":root{{--accent:#000}} /* theme:{key} */"


def hero(key, kind, lede_html=""):
    return f'<header class="hero">PyAuto<b>{key}</b> {kind}</header>{lede_html}'


def stats(*pairs):
    return "".join(f"<li><b>{n}</b>{label}</li>" for n, label in pairs)


def board_links(base_url, current=None, policy=None):
    return {"brain": f"{base_url}/SomeBrain/"}


def boards_footer(links, current):
    return "".join(f'<a data-organ="{k}" href="{u}">{k}</a>'
                   for k, u in links.items())
