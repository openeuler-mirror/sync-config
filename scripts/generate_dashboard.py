#!/usr/bin/env python3
"""
Generate a static HTML dashboard from mirror-results JSON files.

Reads one or more mirror-results.json files (produced by check_sync_status.py)
and produces a single self-contained index.html suitable for GitHub Pages.

Usage:
    python generate_dashboard.py results/*.json -o public/index.html
"""

import argparse
import json
import os
from datetime import datetime
from string import Template
from typing import Dict, List


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="300">
<title>Mirror Sync Status</title>
<style>
  :root {
    --bg: #f6f8fa;
    --card-bg: #ffffff;
    --text: #24292f;
    --muted: #656d76;
    --border: #d0d7de;
    --success: #1a7f37;
    --success-bg: #dafbe1;
    --danger: #cf222e;
    --danger-bg: #ffebe9;
    --warn: #9a6700;
    --warn-bg: #fff8c5;
    --info: #0969da;
    --info-bg: #ddf4ff;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.5;
    padding: 24px;
  }
  .container { max-width: 960px; margin: 0 auto; }
  h1 { font-size: 24px; margin-bottom: 8px; }
  .subtitle { color: var(--muted); font-size: 14px; margin-bottom: 24px; }
  .summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
  }
  .card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    text-align: center;
  }
  .card .number { font-size: 32px; font-weight: 600; }
  .card .label { color: var(--muted); font-size: 13px; margin-top: 4px; }
  .card.success .number { color: var(--success); }
  .card.danger .number { color: var(--danger); }
  .card.warn .number { color: var(--warn); }
  .card.info .number { color: var(--info); }
  .workflow-section {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 20px;
    overflow: hidden;
  }
  .workflow-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
  }
  .workflow-header h2 { font-size: 16px; }
  .workflow-time { color: var(--muted); font-size: 12px; }
  .workflow-body { padding: 16px 20px; }
  .status-bar {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }
  .status-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
  }
  .dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    display: inline-block;
  }
  .dot.green { background: var(--success); }
  .dot.red { background: var(--danger); }
  .dot.yellow { background: var(--warn); }
  .repo-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
  }
  .repo-tag {
    font-size: 12px;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: ui-monospace, SFMono-Regular, monospace;
  }
  .repo-tag.failed {
    background: var(--danger-bg);
    color: var(--danger);
    border: 1px solid #ffb3b8;
  }
  .repo-tag.skipped {
    background: var(--warn-bg);
    color: var(--warn);
    border: 1px solid #f0d66e;
  }
  .repo-tag.success {
    background: var(--success-bg);
    color: var(--success);
    border: 1px solid #8bd89d;
  }
  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: var(--muted);
  }
  .empty-state .icon { font-size: 48px; margin-bottom: 12px; }
  .footer {
    text-align: center;
    color: var(--muted);
    font-size: 12px;
    margin-top: 32px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
  }
  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
  }
  .badge.ok { background: var(--success-bg); color: var(--success); }
  .badge.err { background: var(--danger-bg); color: var(--danger); }
  @media (max-width: 600px) {
    body { padding: 12px; }
    .summary-cards { grid-template-columns: repeat(2, 1fr); }
  }
</style>
</head>
<body>
<div class="container">
  <h1>&#x1F504; Mirror Sync Status</h1>
  <p class="subtitle">Last updated: $last_updated</p>

  <div class="summary-cards">
    <div class="card info">
      <div class="number">$total_repos</div>
      <div class="label">Total Repos</div>
    </div>
    <div class="card success">
      <div class="number">$total_success</div>
      <div class="label">Synced</div>
    </div>
    <div class="card danger">
      <div class="number">$total_failed</div>
      <div class="label">Failed</div>
    </div>
    <div class="card warn">
      <div class="number">$total_skipped</div>
      <div class="label">Skipped</div>
    </div>
  </div>

  $workflow_sections

  <div class="footer">
    Generated by <a href="https://github.com/openeuler-mirror/sync-config">sync-config</a>
    &middot; Auto-refreshes every 5 minutes
  </div>
</div>
</body>
</html>"""

WORKFLOW_SECTION = """<div class="workflow-section">
  <div class="workflow-header">
    <h2>{workflow_name}</h2>
    <span class="workflow-time">{timestamp}</span>
  </div>
  <div class="workflow-body">
    <div class="status-bar">
      <span class="status-item"><span class="dot green"></span> {success} synced</span>
      <span class="status-item"><span class="dot red"></span> {failed} failed</span>
      <span class="status-item"><span class="dot yellow"></span> {skipped} skipped</span>
      <span class="badge {overall_class}">{overall_label}</span>
    </div>
    <p style="font-size:13px;color:var(--muted);margin-bottom:6px;">
      {src} &#8594; {dst}
    </p>
    {failed_section}
    {skipped_section}
    {success_summary}
  </div>
</div>"""


def format_timestamp(ts: str) -> str:
    """Convert ISO timestamp to a human-readable form."""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except (ValueError, AttributeError):
        return ts


def build_repo_tags(repos: List[str], tag_class: str, max_show: int = 50) -> str:
    """Build HTML tag elements for a list of repo names."""
    if not repos:
        return ""
    shown = repos[:max_show]
    suffix = (
        f' <span style="color:var(--muted);font-size:12px;">'
        f'and {len(repos) - max_show} more...</span>'
    ) if len(repos) > max_show else ""
    tags = "".join(f'<span class="repo-tag {tag_class}">{r}</span>' for r in shown)
    return f'<div class="repo-list">{tags}{suffix}</div>'


def generate_dashboard(result_files: List[str]) -> str:
    """Read all result JSON files and produce the full HTML dashboard."""
    workflows = []
    for fpath in result_files:
        try:
            with open(fpath) as f:
                data = json.load(f)
            workflows.append(data)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"::warning::Skipping {fpath}: {e}")

    if not workflows:
        workflows = [{
            "workflow": "No data yet",
            "timestamp": "N/A",
            "src": "?",
            "dst": "?",
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "failed_list": [],
            "skipped_list": [],
            "success_list": [],
        }]

    # Sort by workflow name
    workflows.sort(key=lambda w: w.get("workflow", ""))

    # Aggregate totals
    total_repos = sum(w.get("total", 0) for w in workflows)
    total_success = sum(w.get("success", 0) for w in workflows)
    total_failed = sum(w.get("failed", 0) for w in workflows)
    total_skipped = sum(w.get("skipped", 0) for w in workflows)

    # Latest timestamp
    timestamps = [w.get("timestamp", "") for w in workflows if w.get("timestamp")]
    last_updated = max(timestamps) if timestamps else "N/A"
    last_updated = format_timestamp(last_updated)

    # Build each workflow section
    sections = []
    for w in workflows:
        failed = w.get("failed", 0)
        failed_list = w.get("failed_list", [])
        skipped_list = w.get("skipped_list", [])
        success_count = w.get("success", 0)

        # Failed repos section
        if failed_list:
            failed_section = (
                '<p style="font-size:13px;font-weight:600;color:var(--danger);'
                'margin-top:12px;">&#x26A0; Failed repos:</p>'
                + build_repo_tags(failed_list, "failed")
            )
        else:
            failed_section = ""

        # Skipped repos section (collapsible)
        if skipped_list:
            skipped_section = (
                '<details style="margin-top:12px;font-size:13px;">'
                '<summary style="cursor:pointer;color:var(--warn);">'
                f'Skipped repos ({len(skipped_list)})</summary>'
                + build_repo_tags(skipped_list, "skipped")
                + '</details>'
            )
        else:
            skipped_section = ""

        # Success repos section (collapsible when there are many)
        success_list = w.get("success_list", [])
        if success_list:
            success_summary = (
                '<details style="margin-top:12px;font-size:13px;">'
                '<summary style="cursor:pointer;color:var(--success);">'
                f'&#x2705; {success_count} repos synced successfully</summary>'
                + build_repo_tags(success_list, "success")
                + '</details>'
            )
        elif success_count > 0:
            success_summary = (
                f'<p style="font-size:13px;color:var(--success);margin-top:8px;">'
                f'&#x2705; {success_count} repos synced successfully</p>'
            )
        else:
            success_summary = ""

        overall_class = "err" if failed > 0 else "ok"
        overall_label = "HAS FAILURES" if failed > 0 else "ALL GOOD"

        section = WORKFLOW_SECTION.format(
            workflow_name=w.get("workflow", "Unknown"),
            timestamp=format_timestamp(w.get("timestamp", "")),
            success=w.get("success", 0),
            failed=failed,
            skipped=w.get("skipped", 0),
            overall_class=overall_class,
            overall_label=overall_label,
            src=w.get("src", ""),
            dst=w.get("dst", ""),
            failed_section=failed_section,
            skipped_section=skipped_section,
            success_summary=success_summary,
        )
        sections.append(section)

    # Use Template for HTML_TEMPLATE ($$ delimiters avoid CSS {} conflicts)
    html = Template(HTML_TEMPLATE).substitute(
        last_updated=last_updated,
        total_repos=str(total_repos),
        total_success=str(total_success),
        total_failed=str(total_failed),
        total_skipped=str(total_skipped),
        workflow_sections="\n".join(sections),
    )
    return html


def generate_markdown(result_files: List[str]) -> str:
    """Read all result JSON files and produce a Markdown status table."""
    workflows = []
    for fpath in result_files:
        try:
            with open(fpath) as f:
                data = json.load(f)
            workflows.append(data)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"::warning::Skipping {fpath}: {e}")

    if not workflows:
        return (
            "> ⚠️ No sync status data available yet. "
            "Data will appear after the next scheduled mirror run.\n"
        )

    workflows.sort(key=lambda w: w.get("workflow", ""))

    total_repos = sum(w.get("total", 0) for w in workflows)
    total_success = sum(w.get("success", 0) for w in workflows)
    total_failed = sum(w.get("failed", 0) for w in workflows)
    total_skipped = sum(w.get("skipped", 0) for w in workflows)

    timestamps = [w.get("timestamp", "") for w in workflows if w.get("timestamp")]
    last_updated = max(timestamps) if timestamps else "N/A"
    last_updated = format_timestamp(last_updated)

    # Overall status
    if total_failed > 0:
        overall = f"⚠️ **{total_failed} repo(s) failed**"
    else:
        overall = "✅ All repos synced"

    lines = [
        f"<!-- Generated by sync-config status-deploy workflow -->",
        f"",
        f"**Last updated:** {last_updated} &nbsp;|&nbsp; {overall}",
        f"",
        f"| | Total | Synced | Failed | Skipped |",
        f"| --- | ---: | ---: | ---: | ---: |",
        f"| **All workflows** | **{total_repos}** | **{total_success}** | **{total_failed}** | **{total_skipped}** |",
    ]

    for w in workflows:
        failed = w.get("failed", 0)
        icon = "⚠️" if failed > 0 else "✅"
        name = w.get("workflow", "Unknown")
        lines.append(
            f"| {icon} {name} | {w.get('total', 0)} | {w.get('success', 0)} "
            f"| {failed} | {w.get('skipped', 0)} |"
        )

    lines.append("")

    # List failed repos
    all_failed: List[tuple] = []
    for w in workflows:
        for repo in w.get("failed_list", []):
            all_failed.append((repo, w.get("workflow", "")))

    if all_failed:
        lines.append("### ❌ Failed Repos")
        lines.append("")
        for repo, wf in all_failed:
            lines.append(f"- `{repo}` ({wf})")
        lines.append("")

    # List successful repos (collapsible — can be very long)
    all_success: List[tuple] = []
    for w in workflows:
        for repo in w.get("success_list", []):
            all_success.append((repo, w.get("workflow", "")))

    if all_success:
        lines.append("<details>")
        lines.append(
            f"<summary><b>✅ Successful Repos ({len(all_success)})</b></summary>"
        )
        lines.append("")
        for repo, wf in all_success:
            lines.append(f"- `{repo}` ({wf})")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    lines.append(
        f"[📊 View full dashboard](https://openeuler-mirror.github.io/sync-config/)"
        f" &nbsp;|&nbsp; "
        f"[🔧 View workflow runs](https://github.com/openeuler-mirror/sync-config/actions)"
    )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate mirror sync status dashboard")
    parser.add_argument(
        "result_files", nargs="*", default=[],
        help="One or more mirror-results.json files"
    )
    parser.add_argument(
        "--output", "-o", default="index.html",
        help="Output file path (default: index.html)"
    )
    parser.add_argument(
        "--format", "-f", choices=["html", "markdown"], default="html",
        help="Output format (default: html)"
    )
    parser.add_argument(
        "--input-dir", default="",
        help="Directory containing mirror-results-*.json files"
    )
    args = parser.parse_args()

    result_files = list(args.result_files)

    # Also scan input-dir if provided
    if args.input_dir and os.path.isdir(args.input_dir):
        import glob
        result_files.extend(
            sorted(glob.glob(os.path.join(args.input_dir, "mirror-results*.json")))
        )

    if not result_files:
        print("::warning::No result files provided, generating empty dashboard")

    if args.format == "markdown":
        output = generate_markdown(result_files)
    else:
        output = generate_dashboard(result_files)

    # Write output
    out_dir = os.path.dirname(args.output) or "."
    os.makedirs(out_dir, exist_ok=True)
    with open(args.output, "w") as f:
        f.write(output)
    print(f"Dashboard written to {args.output} ({len(output)} bytes)")


if __name__ == "__main__":
    main()
