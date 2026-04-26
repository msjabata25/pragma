"""
agent/reporter.py
Generates persona-based security audit reports (CEO, Public, Technical).
"""

from __future__ import annotations
import base64
import html as html_lib
from datetime import datetime
from pathlib import Path

from app.agent.models import AuditResult, Persona

# ─────────────────────────────────────────────
# UI Constants
# ─────────────────────────────────────────────
SEVERITY_COLOR = {
    "ERROR":   "#f87171",
    "WARNING": "#fb923c",
    "INFO":    "#60a5fa",
}

SEVERITY_BG = {
    "ERROR":   "rgba(248,113,113,0.08)",
    "WARNING": "rgba(251,146,60,0.08)",
    "INFO":    "rgba(96,165,250,0.08)",
}

SEVERITY_EMOJI = {
    "ERROR":   "🔴",
    "WARNING": "🟡",
    "INFO":    "🔵",
}

# ═══════════════════════════════════════════════════════════════
# MARKDOWN (For Download)
# ═══════════════════════════════════════════════════════════════

def _md_finding_block(result: AuditResult, mode: Persona, index: int) -> str:
    f = result.finding
    content = getattr(result, mode)
    emoji = SEVERITY_EMOJI.get(f.severity.upper(), "⚪")

    lines = [
        f"## {index}. {emoji} {f.severity.upper()} — `{Path(f.path).name}`",
        "",
        f"**File:** `{f.path}` · **Line:** {f.stLine}",
        "",
        "**Summary:**",
        content.explanation,
        "",
        "**Recommended Action:**",
        content.fix,
        "",
    ]

    if result.relevant_chunks:
        lines.append("**Technical Context:**")
        lines.append(f"```\n{result.relevant_chunks[0].strip()}\n```")

    lines.append("\n---\n")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# HTML (For Viewing)
# ═══════════════════════════════════════════════════════════════

def _html_finding_card(result: AuditResult, mode: Persona, index: int) -> str:
    f = result.finding
    content = getattr(result, mode)

    sev   = f.severity.upper()
    color = SEVERITY_COLOR.get(sev, "#94a3b8")
    bg    = SEVERITY_BG.get(sev, "rgba(148,163,184,0.08)")
    emoji = SEVERITY_EMOJI.get(sev, "⚪")

    # Fixed code block
    fixed_code_section = ""
    if content.fixed_code:
        fixed_code_section = f"""
        <div class="section">
            <div class="section-label">Fixed Code</div>
            <pre><code>{html_lib.escape(content.fixed_code.strip())}</code></pre>
        </div>"""

    # ✅ Only show the single most relevant chunk (index 0), collapsed for all personas
    code_section = ""
    if result.relevant_chunks:
        chunk = html_lib.escape(result.relevant_chunks[0].strip())
        label = "View vulnerable code" if mode != "ceo" else "View technical evidence (for developers)"
        code_section = f"""
        <details class="code-toggle">
            <summary>{label}</summary>
            <pre><code>{chunk}</code></pre>
        </details>"""

    return f"""
    <div class="card" id="finding-{index}">
        <div class="card-header" style="border-left: 3px solid {color}; background: {bg};">
            <div class="card-header-left">
                <span class="badge" style="color:{color}; border-color:{color};">{emoji} {sev}</span>
                <span class="card-title">{html_lib.escape(Path(f.path).name)}</span>
            </div>
            <span class="card-line">line {f.stLine}</span>
        </div>
        <div class="card-body">
            <div class="section">
                <div class="section-label">Analysis</div>
                <p>{html_lib.escape(content.explanation)}</p>
            </div>
            <div class="section">
                <div class="section-label">Recommendation</div>
                <p>{html_lib.escape(content.fix)}</p>
            </div>
            {fixed_code_section}
            {code_section}
        </div>
    </div>"""


def build_html(results: list[AuditResult], mode: Persona, repo_name: str = "repo") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    persona_labels = {
        "ceo":       "💼 Executive Summary",
        "public":    "🌍 General Public",
        "technical": "🛠 Technical Auditor",
    }

    total    = len(results)
    errors   = sum(1 for r in results if r.finding.severity.upper() == "ERROR")
    warnings = sum(1 for r in results if r.finding.severity.upper() == "WARNING")
    infos    = sum(1 for r in results if r.finding.severity.upper() == "INFO")

    cards = (
        "\n".join(_html_finding_card(r, mode, i + 1) for i, r in enumerate(results))
        if results
        else '<p class="empty">✅ No vulnerabilities detected.</p>'
    )

    md_content = "\n".join([_md_finding_block(r, mode, i + 1) for i, r in enumerate(results)])
    md_b64     = base64.b64encode(md_content.encode("utf-8")).decode("ascii")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Pragma Audit — {html_lib.escape(repo_name)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg:        #080b0f;
    --surface:   #0e1318;
    --surface-2: #141a22;
    --border:    #1e2a35;
    --text:      #cbd5e1;
    --text-dim:  #4a5a6a;
    --text-muted:#2a3a4a;
    --accent:    #38bdf8;
    --font-ui:   'Syne', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
  }}

  body {{
    font-family: var(--font-ui);
    background: var(--bg);
    color: var(--text);
    padding: 2.5rem 2rem;
    line-height: 1.65;
    max-width: 860px;
    margin: 0 auto;
  }}

  /* ── Header ── */
  .header {{
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
  }}
  .header-top {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1.25rem;
  }}
  .repo-name {{
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #f1f5f9;
  }}
  .repo-name span {{ color: var(--accent); }}
  .meta {{
    font-size: 0.75rem;
    color: var(--text-dim);
    font-family: var(--font-mono);
    margin-top: 0.25rem;
  }}

  /* ── Stats bar ── */
  .stats {{
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }}
  .stat {{
    font-family: var(--font-mono);
    font-size: 0.75rem;
    padding: 0.3rem 0.75rem;
    border-radius: 4px;
    border: 1px solid var(--border);
    color: var(--text-dim);
  }}
  .stat.error   {{ border-color: rgba(248,113,113,0.3); color: #f87171; }}
  .stat.warning {{ border-color: rgba(251,146,60,0.3);  color: #fb923c; }}
  .stat.info    {{ border-color: rgba(96,165,250,0.3);  color: #60a5fa; }}

  /* ── Download button ── */
  .btn-download {{
    font-family: var(--font-mono);
    font-size: 0.75rem;
    background: transparent;
    color: var(--accent);
    border: 1px solid rgba(56,189,248,0.3);
    padding: 0.4rem 0.9rem;
    border-radius: 4px;
    cursor: pointer;
    white-space: nowrap;
    transition: background 0.15s, border-color 0.15s;
    flex-shrink: 0;
  }}
  .btn-download:hover {{
    background: rgba(56,189,248,0.08);
    border-color: var(--accent);
  }}

  /* ── Cards ── */
  .card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 1rem;
    overflow: hidden;
  }}
  .card-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    gap: 0.75rem;
  }}
  .card-header-left {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 0;
  }}
  .badge {{
    font-family: var(--font-mono);
    font-size: 0.65rem;
    font-weight: 500;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
    border: 1px solid;
    white-space: nowrap;
    flex-shrink: 0;
  }}
  .card-title {{
    font-size: 0.85rem;
    font-weight: 600;
    color: #e2e8f0;
    font-family: var(--font-mono);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}
  .card-line {{
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--text-dim);
    white-space: nowrap;
    flex-shrink: 0;
  }}

  /* ── Card body ── */
  .card-body {{
    padding: 1rem 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.875rem;
    border-top: 1px solid var(--border);
  }}
  .section {{ display: flex; flex-direction: column; gap: 0.3rem; }}
  .section-label {{
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-dim);
    font-family: var(--font-mono);
  }}
  .section p {{
    font-size: 0.875rem;
    color: var(--text);
    line-height: 1.6;
  }}

  /* ── Code blocks ── */
  pre {{
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 0.875rem 1rem;
    overflow-x: auto;
    font-family: var(--font-mono);
    font-size: 0.78rem;
    line-height: 1.6;
    color: #94a3b8;
    margin-top: 0.4rem;
  }}
  code {{ font-family: inherit; }}

  /* ── Collapsible code toggle ── */
  .code-toggle {{
    margin-top: 0.25rem;
  }}
  .code-toggle summary {{
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-dim);
    cursor: pointer;
    user-select: none;
    padding: 0.35rem 0;
    list-style: none;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    transition: color 0.15s;
  }}
  .code-toggle summary::-webkit-details-marker {{ display: none; }}
  .code-toggle summary::before {{
    content: '▶';
    font-size: 0.55rem;
    transition: transform 0.15s;
    display: inline-block;
  }}
  .code-toggle[open] summary::before {{ transform: rotate(90deg); }}
  .code-toggle summary:hover {{ color: #94a3b8; }}

  /* ── Empty state ── */
  .empty {{
    text-align: center;
    color: var(--text-dim);
    padding: 3rem;
    font-size: 0.9rem;
    border: 1px dashed var(--border);
    border-radius: 8px;
  }}
</style>
</head>
<body>

  <div class="header">
    <div class="header-top">
      <div>
        <div class="repo-name"><span>pragma</span> / {html_lib.escape(repo_name)}</div>
        <div class="meta">{persona_labels.get(mode, mode)} · {now}</div>
      </div>
      <button class="btn-download" onclick="downloadMd()">↓ .md</button>
    </div>
    <div class="stats">
      <div class="stat">{total} findings</div>
      {"<div class='stat error'>" + str(errors) + " errors</div>" if errors else ""}
      {"<div class='stat warning'>" + str(warnings) + " warnings</div>" if warnings else ""}
      {"<div class='stat info'>" + str(infos) + " info</div>" if infos else ""}
    </div>
  </div>

  {cards}

  <script>
    function downloadMd() {{
      const b64 = "{md_b64}";
      const a = document.createElement("a");
      a.href = "data:text/markdown;base64," + b64;
      a.download = "pragma_report_{mode}.md";
      a.click();
    }}
  </script>
</body>
</html>"""


# ═══════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════

def generate_report(
    results: list[AuditResult],
    mode: Persona,
    repo_name: str = "repo",
    output_dir: str = "reports",
) -> Path:
    """Writes the persona-based HTML report to the output directory."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    slug      = repo_name.replace("/", "_").replace(" ", "_")
    html_path = out / f"pragma_{mode}_{slug}.html"
    html_path.write_text(build_html(results, mode, repo_name), encoding="utf-8")
    return html_path