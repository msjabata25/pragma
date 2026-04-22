"""
agent/reporter.py
Generates persona-based security audit reports (CEO, Public, Technical).
"""

from __future__ import annotations
import base64
import html as html_lib
from datetime import datetime
from pathlib import Path

# Fixed: Absolute import
from app.agent.models import AuditResult, Persona

# ─────────────────────────────────────────────
# UI Constants
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

# ═══════════════════════════════════════════════════════════════
# MARKDOWN (For Download)
# ═══════════════════════════════════════════════════════════════

def _md_finding_block(result: AuditResult, mode: Persona, index: int) -> str:
    f = result.finding
    # Dynamically select the persona-specific content (CEO, Public, or Technical)
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

    # Always include code in MD for record-keeping, regardless of persona
    if result.relevant_chunks:
        lines.append("**Technical Context:**")
        for chunk in result.relevant_chunks:
            lines.append(f"```\n{chunk.strip()}\n```")
    
    lines.append("\n---\n")
    return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════
# HTML (For Viewing)
# ═══════════════════════════════════════════════════════════════

def _html_finding_card(result: AuditResult, mode: Persona, index: int) -> str:
    f = result.finding
    content = getattr(result, mode) 
    
    sev = f.severity.upper()
    color = SEVERITY_COLOR.get(sev, "#718096")
    emoji = SEVERITY_EMOJI.get(sev, "⚪")
    
    # Logic for Option B: Hide code chunks for CEOs using an accordion
    code_section = ""
    if result.relevant_chunks:
        chunks_html = "".join(f"<pre><code>{html_lib.escape(c.strip())}</code></pre>" for c in result.relevant_chunks)
        
        if mode == "ceo":
            code_section = f"""
            <details style="margin-top: 1rem; border: 1px solid #2d3748; padding: 0.5rem; border-radius: 6px;">
                <summary style="cursor:pointer; color:#a0aec0; font-size:0.8rem;">View technical evidence (for developers)</summary>
                <div style="margin-top:0.5rem;">{chunks_html}</div>
            </details>"""
        else:
            code_section = f"""<div class="section"><h4>Technical Context</h4>{chunks_html}</div>"""

    return f"""
    <div class="card" id="finding-{index}">
        <div class="card-header" style="border-left: 4px solid {color};">
            <span class="badge" style="background:{color};">{emoji} {sev}</span>
            <span class="card-title">{index}. {html_lib.escape(Path(f.path).name)}</span>
            <span class="card-meta">Line {f.stLine}</span>
        </div>
        <div class="card-body">
            <div class="section">
                <h4>Analysis</h4>
                <p>{html_lib.escape(content.explanation)}</p>
            </div>
            <div class="section">
                <h4>Recommendation</h4>
                <p><strong>{html_lib.escape(content.fix)}</strong></p>
            </div>
            {code_section}
        </div>
    </div>"""

def build_html(results: list[AuditResult], mode: Persona, repo_name: str = "repo") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Persona labeling for the report header
    persona_labels = {
        "ceo": "💼 Executive Summary",
        "public": "🌍 General Public",
        "technical": "🛠 Technical Auditor"
    }

    cards = "\n".join(_html_finding_card(r, mode, i + 1) for i, r in enumerate(results)) if results else '<p class="empty">✅ No vulnerabilities detected.</p>'
    
    # Generate MD for the embedded download button
    md_content = "\n".join([_md_finding_block(r, mode, i+1) for i, r in enumerate(results)])
    md_b64 = base64.b64encode(md_content.encode("utf-8")).decode("ascii")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Pragma Audit — {html_lib.escape(repo_name)}</title>
<style>
  body {{ font-family: sans-serif; background: #0f1117; color: #e2e8f0; padding: 2rem; line-height: 1.6; }}
  .card {{ background: #1a202c; border-radius: 10px; margin-bottom: 1.5rem; border: 1px solid #2d3748; overflow: hidden; }}
  .card-header {{ display: flex; align-items: center; gap: 1rem; padding: 1rem; background: #171923; }}
  .card-body {{ padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }}
  .badge {{ padding: .2rem .6rem; border-radius: 4px; font-weight: bold; font-size: 0.75rem; color: white; }}
  h4 {{ color: #a0aec0; text-transform: uppercase; font-size: 0.75rem; margin-bottom: 0.25rem; }}
  pre {{ background: #0d1117; padding: 1rem; border-radius: 6px; overflow-x: auto; font-size: 0.85rem; border: 1px solid #2d3748; }}
  .btn-download {{ background: #2d3748; color: white; border: 1px solid #4a5568; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }}
</style>
</head>
<body>
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 2rem;">
    <div>
        <h1>Pragma Audit: {html_lib.escape(repo_name)}</h1>
        <p style="color: #a0aec0;">Mode: {persona_labels.get(mode, mode)} | {now}</p>
    </div>
    <button class="btn-download" onclick="downloadMd()">Download .md</button>
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

    slug = repo_name.replace("/", "_").replace(" ", "_")
    html_path = out / f"pragma_{mode}_{slug}.html"
    html_path.write_text(build_html(results, mode, repo_name), encoding="utf-8")

    return html_path