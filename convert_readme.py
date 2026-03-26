#!/usr/bin/env python3
"""Convert README.md to HTML"""
import markdown

with open('README.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NemoClaw Enterprise Command Center</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 40px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
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
        .footer {{ text-align: center; padding: 30px; color: #666; border-top: 1px solid #ddd; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NemoClaw Enterprise Command Center v2.1.0</h1>
        <p>Enterprise AI Agent Orchestration Platform</p>
    </div>
    <div class="content">
        {html_content}
    </div>
    <div class="footer">
        <p>Author: <a href="https://www.linkedin.com/in/bhaskerkpatel/" target="_blank">Bhaskar Puppala</a></p>
    </div>
</body>
</html>"""

with open('README.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print('README.html created successfully!')
