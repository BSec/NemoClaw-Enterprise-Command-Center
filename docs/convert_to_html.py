#!/usr/bin/env python3
"""
Markdown to HTML Converter for NemoClaw Documentation
Converts all .md files to .html with consistent styling
"""

import markdown
import os
import re
from pathlib import Path

def md_to_html(input_file, output_file):
    """Convert a single markdown file to HTML"""
    
    # Read markdown content
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'toc', 'nl2br']
    )
    
    # Extract title from first h1 or filename
    title_match = re.search(r'<h1>(.*?)</h1>', html_content)
    if title_match:
        title = title_match.group(1)
    else:
        title = Path(input_file).stem.replace('-', ' ').replace('_', ' ').title()
    
    # Create full HTML document with styling
    full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{ margin: 0; font-size: 2em; }}
        .content {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #1e3c72; border-bottom: 3px solid #2a5298; padding-bottom: 10px; }}
        h2 {{ color: #2a5298; margin-top: 30px; border-bottom: 2px solid #eee; padding-bottom: 8px; }}
        h3 {{ color: #444; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            background: white;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: #1e3c72;
            color: white;
            font-weight: 600;
        }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 6px;
            overflow-x: auto;
            line-height: 1.4;
        }}
        pre code {{
            background: transparent;
            color: inherit;
            padding: 0;
        }}
        a {{ color: #2a5298; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        ul, ol {{ padding-left: 30px; }}
        li {{ margin: 8px 0; }}
        blockquote {{
            border-left: 4px solid #2a5298;
            margin: 20px 0;
            padding: 15px 20px;
            background: #f8f9fa;
            font-style: italic;
        }}
        .nav {{
            background: #1e3c72;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }}
        .nav a {{
            color: white;
            margin-right: 20px;
            font-weight: 500;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            border-top: 1px solid #ddd;
            margin-top: 40px;
        }}
        @media print {{
            body {{ background: white; }}
            .header {{ background: #1e3c72 !important; -webkit-print-color-adjust: exact; }}
            .content {{ box-shadow: none; }}
        }}
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .content {{ padding: 20px; }}
            .header {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="index.html">← Documentation Index</a>
        <a href="../README.html">README</a>
    </div>
    
    <div class="header">
        <h1>📄 {title}</h1>
    </div>
    
    <div class="content">
        {html_content}
    </div>
    
    <div class="footer">
        <p>NemoClaw Enterprise Command Center v2.1.0</p>
        <p>© 2026 | Author: <a href="https://www.linkedin.com/in/bhaskerkpatel/" target="_blank">Bhaskar Puppala</a></p>
    </div>
</body>
</html>'''
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✓ Converted: {input_file} → {output_file}")

def main():
    """Convert all markdown files to HTML"""
    
    # Define file mappings (source md → target html)
    conversions = [
        # Root level files (these will be gitignored)
        ('../PROGRESS.md', '../PROGRESS.html'),
        ('../SECURITY.md', '../SECURITY.html'),
        ('../CHANGELOG.md', '../CHANGELOG.html'),
        
        # Docs folder files
        ('DATA_FLOW_DIAGRAMS.md', 'data-flow-diagrams.html'),
        ('DATABASE_SCHEMA.md', 'database-schema.html'),
        ('ARCHITECTURE_OVERVIEW.md', 'architecture-overview.html'),
        ('COMPONENT_DOCUMENTATION.md', 'component-documentation.html'),
        ('API_SPECIFICATIONS.md', 'api-specifications.html'),
        ('OPERATIONAL_RUNBOOKS.md', 'operational-runbooks.html'),
    ]
    
    base_dir = Path(__file__).parent
    
    for md_file, html_file in conversions:
        input_path = base_dir / md_file
        output_path = base_dir / html_file
        
        if input_path.exists():
            md_to_html(str(input_path), str(output_path))
        else:
            print(f"⚠ Not found: {input_path}")
    
    print("\n✅ Conversion complete!")

if __name__ == '__main__':
    main()
