#!/usr/bin/env python3
"""Convert root-level markdown files to HTML"""

import markdown
from pathlib import Path

def convert_md_to_html(md_path, html_path, title):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])
    
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 30px 40px; border-radius: 8px; margin-bottom: 30px; }}
        .content {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #1e3c72; border-bottom: 3px solid #2a5298; padding-bottom: 10px; }}
        h2 {{ color: #2a5298; margin-top: 30px; border-bottom: 2px solid #eee; padding-bottom: 8px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #1e3c72; color: white; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: Consolas, Monaco, monospace; }}
        pre {{ background: #2d2d2d; color: #f8f8f2; padding: 20px; border-radius: 6px; overflow-x: auto; }}
        a {{ color: #2a5298; }}
        .nav {{ background: #1e3c72; padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
        .nav a {{ color: white; margin-right: 20px; text-decoration: none; }}
        .footer {{ text-align: center; padding: 30px; color: #666; border-top: 1px solid #ddd; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="docs/index.html">← Documentation Index</a>
        <a href="README.html">README</a>
    </div>
    <div class="header">
        <h1>{title}</h1>
    </div>
    <div class="content">
        {html_content}
    </div>
    <div class="footer">
        <p>NemoClaw Enterprise Command Center v2.1.0</p>
        <p>Author: <a href="https://www.linkedin.com/in/bhaskerkpatel/" target="_blank">Bhaskar Puppala</a></p>
    </div>
</body>
</html>"""
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f'Converted: {md_path} -> {html_path}')

# Convert root level files
files = [
    ('PROGRESS.md', 'PROGRESS.html', 'Progress Tracking'),
    ('SECURITY.md', 'SECURITY.html', 'Security Hardening Guide'),
    ('CHANGELOG.md', 'CHANGELOG.html', 'Version Changelog'),
]

for md, html, title in files:
    if Path(md).exists():
        convert_md_to_html(md, html, title)

print('Root-level conversion complete!')
