from __future__ import annotations
from datetime import datetime

from backend.sessions.models import Session

_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
_SEVERITY_EMOJI = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}


def generate_markdown(session: Session) -> str:
    target = session.target_config
    target_str = target.ip or target.domain or "Not set"
    created = session.created_at.strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = [
        f"# Bodach Report — {session.name}",
        "",
        f"**Date:** {created}  ",
        f"**Target:** {target_str}  ",
    ]
    if target.ports:
        lines.append(f"**Ports:** {target.ports}  ")
    if target.notes:
        lines.append(f"**Notes:** {target.notes}  ")
    lines.append("")

    # Findings
    lines.append("---")
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    sorted_findings = sorted(session.findings, key=lambda f: _SEVERITY_ORDER.get(f.severity, 99))
    if sorted_findings:
        lines.append("| Severity | Title | Description |")
        lines.append("|----------|-------|-------------|")
        for f in sorted_findings:
            emoji = _SEVERITY_EMOJI.get(f.severity, "")
            desc_short = f.description.replace("\n", " ")[:120]
            lines.append(f"| {emoji} {f.severity.upper()} | {f.title} | {desc_short} |")
        lines.append("")
        for f in sorted_findings:
            emoji = _SEVERITY_EMOJI.get(f.severity, "")
            lines.append(f"### {emoji} [{f.severity.upper()}] {f.title}")
            lines.append("")
            lines.append(f"**Description:** {f.description}")
            lines.append("")
            if f.evidence:
                lines.append(f"**Evidence:**")
                lines.append(f"```")
                lines.append(f.evidence)
                lines.append(f"```")
                lines.append("")
            if f.recommendation:
                lines.append(f"**Recommendation:** {f.recommendation}")
                lines.append("")
    else:
        lines.append("*No findings recorded.*")
        lines.append("")

    # Tool timeline
    lines.append("---")
    lines.append("")
    lines.append("## Tool Execution Timeline")
    lines.append("")
    tool_msgs = [m for m in session.messages if m.role == "tool_start"]
    if tool_msgs:
        for m in tool_msgs:
            ts = m.timestamp.strftime("%H:%M:%S") if m.timestamp else ""
            args_str = ""
            if hasattr(m, "name") and m.name:
                args_str = f" ({m.name})"
            lines.append(f"- `{ts}` **{m.content}**{args_str}")
    else:
        lines.append("*No tools executed.*")
    lines.append("")

    # Chat transcript
    lines.append("---")
    lines.append("")
    lines.append("## Chat Transcript")
    lines.append("")
    visible = [m for m in session.messages if m.role in ("user", "assistant")]
    for m in visible:
        ts = m.timestamp.strftime("%H:%M") if m.timestamp else ""
        role_label = "**User**" if m.role == "user" else "**AI Agent**"
        lines.append(f"**[{ts}] {role_label}:**")
        lines.append("")
        lines.append(m.content)
        lines.append("")

    return "\n".join(lines)


def generate_html(session: Session) -> str:
    import mistune
    md = generate_markdown(session)
    body = mistune.html(md)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pentest Agent 2.0 Report — {session.name}</title>
<style>
  @media print {{ body {{ background: #fff; color: #000; }} a {{ color: #000; }} }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #0d1117;
    color: #e6edf3;
    padding: 40px 20px;
    font-size: 14px;
    line-height: 1.6;
  }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ color: #58a6ff; border-bottom: 2px solid #21262d; padding-bottom: 12px; margin-bottom: 24px; font-size: 24px; }}
  h2 {{ color: #58a6ff; margin: 32px 0 12px; font-size: 18px; border-bottom: 1px solid #21262d; padding-bottom: 6px; }}
  h3 {{ color: #79c0ff; margin: 20px 0 8px; font-size: 15px; }}
  p {{ margin: 8px 0; }}
  strong {{ color: #e6edf3; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
  th {{ background: #161b22; color: #8b949e; padding: 8px 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #21262d; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #21262d; }}
  tr:hover {{ background: #161b22; }}
  code {{ background: #161b22; color: #79c0ff; padding: 2px 6px; border-radius: 4px; font-family: 'Cascadia Code', monospace; font-size: 12px; }}
  pre {{ background: #161b22; padding: 16px; border-radius: 6px; overflow-x: auto; border: 1px solid #21262d; margin: 8px 0; }}
  pre code {{ background: none; padding: 0; color: #e6edf3; }}
  hr {{ border: none; border-top: 1px solid #21262d; margin: 24px 0; }}
  ul, ol {{ padding-left: 24px; margin: 8px 0; }}
  li {{ margin: 4px 0; }}
  blockquote {{ border-left: 3px solid #58a6ff; padding-left: 12px; color: #8b949e; margin: 8px 0; }}
</style>
</head>
<body>
<div class="container">
{body}
</div>
</body>
</html>"""


def generate_pdf(session: Session) -> bytes:
    from weasyprint import HTML
    html = generate_html(session)
    return HTML(string=html).write_pdf()
