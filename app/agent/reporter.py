"""
agent/reporter.py
Generates Autopilot and Manual security audit reports from a list of AuditResult.

Autopilot mode  — plain English, severity, file/line, explanation, fix suggestion.
Manual mode     — everything above + Semgrep rule ID, raw relevant code chunks, fix as diff block.
"""

from __future__ import annotations

import base64
import html as html_lib
from datetime import datetime
from pathlib import Path
from typing import Literal

from agent.models import AuditResult

# ─────────────────────────────────────────────
# Severity colour mapping (used in HTML)
# ─────────────────────────────────────────────
SEVERITY_COLOR = {
    "ERROR":   "#e53e3e",
    "WARNING": "#dd6b20",
    "INFO":    "#3182ce",
}

SEVERITY_EMOJI = {
    "ERROR":   "🔴",
    "WARNING": "🟡",
    "INFO":    "🔵",
}

Mode = Literal["autopilot", "manual"]


# ═══════════════════════════════════════════════════════════════
# MARKDOWN
# ═══════════════════════════════════════════════════════════════

def _md_finding_block(result: AuditResult, mode: Mode, index: int) -> str:
    f = result.finding
    emoji = SEVERITY_EMOJI.get(f.severity.upper(), "⚪")
    lines: list[str] = []

    lines.append(f"## {index}. {emoji} {f.severity.upper()} — `{Path(f.path).name}`")
    lines.append("")
    lines.append(f"**File:** `{f.path}` · **Line:** {f.stLine}")

    if mode == "manual":
        lines.append(f"**Rule ID:** `{f.check_id}`")

    lines.append("")
    lines.append(f"**What's wrong:**")
    lines.append(f"> {f.msg}")
    lines.append("")
    lines.append(f"**Explanation:**")
    lines.append(result.explanation or "_No explanation generated._")
    lines.append("")

    if mode == "manual" and result.relevant_chunks:
        lines.append("**Relevant code context:**")
        lines.append("")
        for chunk in result.relevant_chunks:
            lines.append("```")
            lines.append(chunk.strip())
            lines.append("```")
        lines.append("")

    if result.fix:
        if mode == "manual":
            lines.append("**Suggested fix (diff):**")
            lines.append("")
            lines.append("```diff")
            # Prefix every line with '+' to present as an addition patch
            for line in result.fix.strip().splitlines():
                if line.startswith("-") or line.startswith("+"):
                    lines.append(line)   # already marked
                else:
                    lines.append(f"+ {line}")
            lines.append("```")
        else:
            lines.append("**How to fix:**")
            lines.append(result.fix)

    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def build_markdown(results: list[AuditResult], mode: Mode, repo_name: str = "repo") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    severity_counts = _count_severities(results)

    header = [
        f"# Pragma Security Audit — `{repo_name}`",
        "",
        f"**Mode:** {'🤖 Autopilot' if mode == 'autopilot' else '🛠 Manual'}  ",
        f"**Generated:** {now}  ",
        f"**Findings:** {len(results)} total — "
        f"🔴 {severity_counts['ERROR']} critical · "
        f"🟡 {severity_counts['WARNING']} warnings · "
        f"🔵 {severity_counts['INFO']} info",
        "",
        "---",
        "",
    ]

    if not results:
        return "\n".join(header) + "\n✅ No findings. Clean scan.\n"

    blocks = [_md_finding_block(r, mode, i + 1) for i, r in enumerate(results)]
    return "\n".join(header) + "\n".join(blocks)


# ═══════════════════════════════════════════════════════════════
# HTML
# ═══════════════════════════════════════════════════════════════

def _html_finding_card(result: AuditResult, mode: Mode, index: int) -> str:
    f = result.finding
    sev = f.severity.upper()
    color = SEVERITY_COLOR.get(sev, "#718096")
    emoji = SEVERITY_EMOJI.get(sev, "⚪")
    fname = html_lib.escape(Path(f.path).name)
    fpath = html_lib.escape(f.path)
    msg   = html_lib.escape(f.msg)
    explanation = html_lib.escape(result.explanation or "No explanation generated.")

    rule_row = ""
    if mode == "manual":
        rule_row = f'<p class="meta">Rule: <code>{html_lib.escape(f.check_id)}</code></p>'

    chunks_section = ""
    if mode == "manual" and result.relevant_chunks:
        chunk_blocks = "".join(
            f'<pre><code>{html_lib.escape(c.strip())}</code></pre>'
            for c in result.relevant_chunks
        )
        chunks_section = f"""
        <div class="section">
            <h4>Relevant code context</h4>
            {chunk_blocks}
        </div>"""

    fix_section = ""
    if result.fix:
        fix_escaped = html_lib.escape(result.fix.strip())
        if mode == "manual":
            # Build diff lines
            diff_lines = []
            for line in result.fix.strip().splitlines():
                if line.startswith("-"):
                    diff_lines.append(f'<span class="diff-del">{html_lib.escape(line)}</span>')
                elif line.startswith("+"):
                    diff_lines.append(f'<span class="diff-add">{html_lib.escape(line)}</span>')
                else:
                    diff_lines.append(f'<span class="diff-add">+ {html_lib.escape(line)}</span>')
            diff_html = "\n".join(diff_lines)
            fix_section = f"""
        <div class="section">
            <h4>Suggested fix (diff)</h4>
            <pre class="diff"><code>{diff_html}</code></pre>
        </div>"""
        else:
            fix_section = f"""
        <div class="section">
            <h4>How to fix</h4>
            <p>{fix_escaped}</p>
        </div>"""

    return f"""
    <div class="card" id="finding-{index}">
        <div class="card-header" style="border-left: 4px solid {color};">
            <span class="badge" style="background:{color};">{emoji} {sev}</span>
            <span class="card-title">{index}. <code>{fname}</code></span>
            <span class="card-meta">Line {f.stLine}</span>
        </div>
        <div class="card-body">
            <p class="meta">File: <code>{fpath}</code></p>
            {rule_row}
            <div class="section">
                <h4>What's wrong</h4>
                <blockquote>{msg}</blockquote>
            </div>
            <div class="section">
                <h4>Explanation</h4>
                <p>{explanation}</p>
            </div>
            {chunks_section}
            {fix_section}
        </div>
    </div>"""


def build_html(results: list[AuditResult], mode: Mode, repo_name: str = "repo") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    severity_counts = _count_severities(results)
    mode_label = "🤖 Autopilot" if mode == "autopilot" else "🛠 Manual"

    cards = "\n".join(
        _html_finding_card(r, mode, i + 1) for i, r in enumerate(results)
    ) if results else '<p class="empty">✅ No findings. Clean scan.</p>'

    # Embed the markdown as base64 so the download button works with no server round-trip
    md_content   = build_markdown(results, mode, repo_name)
    md_b64        = base64.b64encode(md_content.encode("utf-8")).decode("ascii")
    slug          = repo_name.replace("/", "_").replace(" ", "_")
    md_filename   = f"pragma_report_{slug}.md"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Pragma Audit — {html_lib.escape(repo_name)}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #0f1117; color: #e2e8f0; padding: 2rem;
    line-height: 1.6;
  }}
  h1 {{ font-size: 1.6rem; color: #fff; margin-bottom: .25rem; }}
  h4 {{ font-size: .85rem; text-transform: uppercase; letter-spacing: .05em;
        color: #a0aec0; margin-bottom: .5rem; }}
  .meta-bar {{
    display: flex; flex-wrap: wrap; gap: 1rem; align-items: center;
    margin-bottom: 2rem; color: #a0aec0; font-size: .9rem;
  }}
  .pill {{
    padding: .2rem .7rem; border-radius: 999px; font-size: .8rem;
    font-weight: 600; background: #1a202c; border: 1px solid #2d3748;
  }}
  .btn-download {{
    margin-left: auto;
    padding: .35rem .9rem;
    border-radius: 7px;
    border: 1px solid #4a5568;
    background: #2d3748;
    color: #e2e8f0;
    font-size: .82rem;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: .4rem;
    transition: background .15s;
  }}
  .btn-download:hover {{ background: #3a4a5c; }}
  .card {{
    background: #1a202c; border-radius: 10px; margin-bottom: 1.5rem;
    overflow: hidden; border: 1px solid #2d3748;
  }}
  .card-header {{
    display: flex; align-items: center; gap: .75rem;
    padding: .75rem 1.25rem; background: #171923;
  }}
  .badge {{
    padding: .2rem .65rem; border-radius: 6px; font-size: .75rem;
    font-weight: 700; color: #fff; white-space: nowrap;
  }}
  .card-title {{ font-weight: 600; flex: 1; }}
  .card-meta {{ font-size: .8rem; color: #718096; }}
  .card-body {{ padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }}
  .section {{ display: flex; flex-direction: column; gap: .4rem; }}
  .meta {{ font-size: .82rem; color: #718096; }}
  blockquote {{
    border-left: 3px solid #4a5568; padding-left: .75rem;
    color: #cbd5e0; font-style: italic;
  }}
  pre {{
    background: #171923; border: 1px solid #2d3748; border-radius: 6px;
    padding: .85rem 1rem; overflow-x: auto; font-size: .82rem;
  }}
  code {{ font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace; }}
  pre.diff {{ background: #0d1117; }}
  .diff-add {{ color: #68d391; display: block; }}
  .diff-del {{ color: #fc8181; display: block; }}
  .empty {{ color: #68d391; font-size: 1.1rem; text-align: center; padding: 3rem; }}
</style>
</head>
<body>
  <h1>🔍 Pragma Security Audit — <code>{html_lib.escape(repo_name)}</code></h1>
  <div class="meta-bar">
    <span>{mode_label}</span>
    <span>Generated: {now}</span>
    <span class="pill" style="color:#e53e3e;">🔴 {severity_counts['ERROR']} critical</span>
    <span class="pill" style="color:#dd6b20;">🟡 {severity_counts['WARNING']} warnings</span>
    <span class="pill" style="color:#3182ce;">🔵 {severity_counts['INFO']} info</span>
    <button class="btn-download" onclick="downloadMd()">⬇ Download .md</button>
  </div>
  {cards}
<script>
  function downloadMd() {{
    const b64 = "{md_b64}";
    const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
    const blob  = new Blob([bytes], {{ type: "text/markdown" }});
    const a     = document.createElement("a");
    a.href      = URL.createObjectURL(blob);
    a.download  = "{md_filename}";
    a.click();
    URL.revokeObjectURL(a.href);
  }}
</script>
</body>
</html>"""


# ═══════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════

def generate_report(
    results: list[AuditResult],
    mode: Mode,
    repo_name: str = "repo",
    output_dir: str = ".",
) -> Path:
    """
    Write the HTML report (with embedded MD download button) to output_dir.
    Returns the Path to the written HTML file.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    slug      = repo_name.replace("/", "_").replace(" ", "_")
    html_path = out / f"pragma_report_{slug}.html"
    html_path.write_text(build_html(results, mode, repo_name), encoding="utf-8")

    return html_path


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _count_severities(results: list[AuditResult]) -> dict[str, int]:
    counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    for r in results:
        key = r.finding.severity.upper()
        if key in counts:
            counts[key] += 1
        else:
            counts["INFO"] += 1   # fallback bucket
    return counts