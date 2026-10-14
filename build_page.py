"""
build_page.py: writes index.html, a one-page view of the research database.

It reads claims.json, sources.json, questions.md and REPORT.md. A claim's
status comes only from REPORT.md (written by verify.py): verified claims are
shown under their question, everything else is listed as held with the
checker's reason. A claim missing from REPORT.md counts as held until
`python verify.py` is run again.

Usage:
  python verify.py        (check claims first)
  python build_page.py    (then rebuild the page)

Python standard library only. Nothing in this file calls an AI model.
"""

import datetime
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
NUMBER = r"\d[\d,]*(?:\.\d+)?"


def load(name):
    path = HERE / name
    return json.loads(path.read_text(encoding="utf-8") or "[]") if path.exists() else []


def report_status():
    """{claim_id: (status, reason)} from REPORT.md's table."""
    path = HERE / "REPORT.md"
    if not path.exists():
        return {}
    status = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| c"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)[1:-1]]
        if len(cells) == 8:
            status[cells[0]] = ("verified" if cells[6] == "verified" else "held", cells[7])
    return status


def questions():
    """[(number, text)] from the numbered bold questions in questions.md."""
    text = (HERE / "questions.md").read_text(encoding="utf-8")
    section = re.search(r"^# Questions\s*$(.*?)(?=^# |\Z)", text, flags=re.M | re.S)
    text = section.group(1) if section else ""
    found = re.findall(r"^(\d+)\.\s+\*\*(.+?)\*\*", text, flags=re.M | re.S)
    return [(int(n), " ".join(q.split())) for n, q in found]


def topic():
    text = (HERE / "questions.md").read_text(encoding="utf-8")
    match = re.search(r"# Topic\s+(.+?)(?:\n\s*\n)", text, flags=re.S)
    return " ".join(match.group(1).split()) if match else ""


def e(text):
    return html.escape(str(text))


def display_value(claim):
    value, unit = claim.get("value", ""), claim.get("unit", "")
    if unit.lower().startswith("us dollars"):
        return f"${value}"
    return value


def checks_for(claim):
    """Plain, predictable reminders for a person reviewing a verified claim."""
    notes = []
    numbers = set(re.findall(NUMBER, claim.get("quote", "")))
    if len(numbers) > 1:
        notes.append(f"The quote contains {len(numbers)} different numbers. "
                     "Confirm this value is the one the subject describes.")
    years = set(re.findall(r"\b(?:19|20)\d\d\b", claim.get("quote", "")))
    if len(years) > 1:
        notes.append("The quote mentions more than one year. Confirm the period.")
    return notes


def claim_card(claim, source, reason=None):
    title = source.get("title", claim.get("source_id", ""))
    url = source.get("url", "")
    link = (f'<a href="{e(url)}">{e(title)}</a>' if url else e(title))
    notes = "".join(f"<li>{e(n)}</li>" for n in checks_for(claim))
    return f"""
    <article class="claim{' held' if reason is not None else ''}">
      <div class="figure">
        <span class="value">{e(display_value(claim))}</span>
        <span class="unit">{e(claim.get('unit', ''))}</span>
      </div>
      <p class="subject">{e(claim.get('subject', ''))}</p>
      <p class="meta">{e(claim.get('period', ''))} · claim {e(claim.get('claim_id', ''))}</p>
      <blockquote>{e(claim.get('quote', ''))}</blockquote>
      <p class="source">Source: {link} <span class="sid">({e(claim.get('source_id', ''))})</span></p>
      {f'<p class="reason"><strong>Held:</strong> {e(reason)}</p>' if reason is not None else ''}
      {f'<ul class="checks">{notes}</ul>' if notes and reason is None else ''}
    </article>"""


def build():
    claims = load("claims.json")
    sources = {s["id"]: s for s in load("sources.json")}
    status = report_status()

    verified, held = [], []
    for c in claims:
        st, reason = status.get(c.get("claim_id"), ("held", "not checked yet: run python verify.py"))
        (verified if st == "verified" else held).append((c, reason))

    sections = []
    for number, text in questions():
        cards = [claim_card(c, sources.get(c.get("source_id"), {}))
                 for c, _ in verified if c.get("question") == number]
        body = "".join(cards) if cards else '<p class="empty">No verified claims answer this question yet.</p>'
        sections.append(f"""
  <section>
    <h2><span class="qnum">Q{number}</span> {e(text)}</h2>
    <p class="count">{len(cards)} verified claim{'s' if len(cards) != 1 else ''}</p>
    {body}
  </section>""")

    unassigned = [c for c, _ in verified if c.get("question") not in {n for n, _ in questions()}]
    if unassigned:
        sections.append(f"""
  <section>
    <h2>Not linked to a question</h2>
    {''.join(claim_card(c, sources.get(c.get('source_id'), {})) for c in unassigned)}
  </section>""")

    held_html = ("".join(claim_card(c, sources.get(c.get("source_id"), {}), reason) for c, reason in held)
                 if held else '<p class="empty">No held claims. Every claim passed the checker.</p>')

    source_rows = "".join(
        f"<li><a href=\"{e(s.get('url', ''))}\">{e(s.get('title', s['id']))}</a> "
        f"<span class=\"sid\">({e(s['id'])}, added {e(s.get('added_on', ''))})</span></li>"
        for s in sources.values())

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CTCAC Housing Claims</title>
<style>
  :root {{
    --bg: #f7f6f3; --card: #ffffff; --text: #1f2328; --muted: #5f6670;
    --line: #e2e0da; --accent: #2f6f4f; --quote: #f1efe9; --held: #a3412b;
    --held-bg: #fbeeea;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #16181b; --card: #1f2226; --text: #e6e6e3; --muted: #a0a6ad;
      --line: #33373c; --accent: #7cc49d; --quote: #26292e; --held: #f0907a;
      --held-bg: #2e2220;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #16181b; --card: #1f2226; --text: #e6e6e3; --muted: #a0a6ad;
    --line: #33373c; --accent: #7cc49d; --quote: #26292e; --held: #f0907a;
    --held-bg: #2e2220;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--text);
         font: 16px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width: 860px; margin: 0 auto; padding: 32px 16px 64px; }}
  h1 {{ font-size: 1.7rem; margin: 0 0 8px; }}
  .lede {{ color: var(--muted); margin: 0 0 16px; }}
  .stats {{ display: flex; gap: 12px; flex-wrap: wrap; margin: 16px 0 8px; }}
  .stat {{ background: var(--card); border: 1px solid var(--line); border-radius: 8px;
          padding: 10px 14px; }}
  .stat b {{ font-size: 1.3rem; display: block; }}
  .stat.bad b {{ color: var(--held); }}
  .note {{ font-size: .9rem; color: var(--muted); }}
  section {{ margin-top: 40px; }}
  h2 {{ font-size: 1.2rem; margin: 0 0 4px; }}
  .qnum {{ color: var(--accent); margin-right: 4px; }}
  .count, .empty {{ color: var(--muted); font-size: .95rem; margin: 0 0 12px; }}
  .claim {{ background: var(--card); border: 1px solid var(--line); border-radius: 10px;
           padding: 16px 18px; margin: 12px 0; }}
  .claim.held {{ border-color: var(--held); background: var(--held-bg); }}
  .figure {{ display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }}
  .value {{ font-size: 1.6rem; font-weight: 700; color: var(--accent);
           font-variant-numeric: tabular-nums; }}
  .held .value {{ color: var(--held); }}
  .unit {{ color: var(--muted); font-size: .9rem; }}
  .subject {{ margin: 6px 0 2px; font-weight: 600; }}
  .meta, .source, .sid {{ color: var(--muted); font-size: .88rem; margin: 2px 0; }}
  blockquote {{ margin: 10px 0; padding: 10px 14px; background: var(--quote);
               border-left: 3px solid var(--accent); font-size: .93rem;
               white-space: pre-wrap; overflow-wrap: anywhere; }}
  .held blockquote {{ border-left-color: var(--held); }}
  .reason {{ color: var(--held); margin: 8px 0 0; }}
  .checks {{ margin: 8px 0 0; padding-left: 20px; font-size: .88rem; color: var(--muted); }}
  a {{ color: var(--accent); overflow-wrap: anywhere; }}
  footer {{ margin-top: 48px; border-top: 1px solid var(--line); padding-top: 16px; }}
  footer ul {{ padding-left: 20px; }}
</style>
</head>
<body>
<main>
  <h1>Affordable housing in California: verified claims</h1>
  <p class="lede">{e(topic())}</p>
  <div class="stats">
    <div class="stat"><b>{len(claims)}</b>claims</div>
    <div class="stat"><b>{len(verified)}</b>verified</div>
    <div class="stat{' bad' if held else ''}"><b>{len(held)}</b>held</div>
    <div class="stat"><b>{len(sources)}</b>sources</div>
  </div>
  <p class="note">"Verified" means the source file is unchanged, the quote appears word for word
  in it, and the number appears in the quote. It does not mean the claim is the right fact:
  read the quote, and check the notes under a claim. Credit amounts in staff reports are
  recommendations, not confirmed awards. Federal credits are annual; state credits are totals.</p>
  {''.join(sections)}
  <section>
    <h2>Held claims</h2>
    <p class="count">Claims that failed the checker. They are not counted above.</p>
    {held_html}
  </section>
  <footer>
    <h2>Sources</h2>
    <ul>{source_rows}</ul>
    <p class="note">Built {datetime.date.today().isoformat()} by build_page.py from claims.json
    and REPORT.md. Rebuild after every <code>python verify.py</code>.</p>
  </footer>
</main>
</body>
</html>
"""
    (HERE / "index.html").write_text(page, encoding="utf-8")
    print(f"Wrote index.html: {len(verified)} verified, {len(held)} held.")


if __name__ == "__main__":
    build()
