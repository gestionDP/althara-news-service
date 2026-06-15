#!/usr/bin/env python3
"""
Genera un PDF combinado de toda la documentación wiki.
Uso: python docs/wiki/generate_pdf.py
Requiere: pip install markdown weasyprint
"""
import os
import re
import markdown
from weasyprint import HTML, CSS

REPO_TITLE = "News Service"

WIKI_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PDF = os.path.join(WIKI_DIR, "documentation.pdf")

# Orden de archivos según README.md
def get_ordered_files():
    readme_path = os.path.join(WIKI_DIR, "README.md")
    files = []
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            for line in f:
                match = re.search(r'\((?:\./)?([\w\-]+\.md)\)', line)
                if match:
                    fname = match.group(1)
                    if fname != "README.md":
                        files.append(fname)
    if not files:
        files = sorted([f for f in os.listdir(WIKI_DIR) if f.endswith(".md") and f != "README.md"])
    return files

CSS_STYLES = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

@page {
    margin: 2.5cm 2cm;
    @bottom-right { content: counter(page); font-size: 10px; color: #888; }
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1a1a2e;
    max-width: 100%;
}

h1 { font-size: 22pt; color: #0f3460; border-bottom: 3px solid #0f3460; padding-bottom: 8px; margin-top: 40px; page-break-before: always; }
.cover + .wiki-page h1 { page-break-before: avoid; }
h2 { font-size: 16pt; color: #16213e; border-bottom: 1px solid #dde; padding-bottom: 4px; margin-top: 28px; }
h3 { font-size: 13pt; color: #1a1a2e; margin-top: 20px; }
h4 { font-size: 11pt; color: #333; margin-top: 16px; }

code {
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    background: #f4f6f9;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 9.5pt;
    color: #c7254e;
}

pre {
    background: #1e1e2e;
    color: #cdd6f4;
    padding: 16px 20px;
    border-radius: 8px;
    overflow-x: auto;
    font-size: 9pt;
    line-height: 1.5;
    margin: 16px 0;
}

pre code {
    background: none;
    color: inherit;
    padding: 0;
    font-size: inherit;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    font-size: 10pt;
}

th {
    background: #0f3460;
    color: white;
    padding: 8px 12px;
    text-align: left;
    font-weight: 600;
}

td {
    padding: 7px 12px;
    border-bottom: 1px solid #e8eaf0;
}

tr:nth-child(even) td { background: #f8f9fc; }

blockquote {
    border-left: 4px solid #0f3460;
    margin: 16px 0;
    padding: 8px 16px;
    background: #f0f4ff;
    color: #444;
    border-radius: 0 6px 6px 0;
}

a { color: #0f3460; text-decoration: none; }

hr {
    border: none;
    border-top: 1px solid #dde;
    margin: 32px 0;
}

.page-separator {
    page-break-after: always;
}

.cover {
    text-align: center;
    padding: 120px 40px;
    page-break-after: always;
}

.cover h1 {
    font-size: 32pt;
    border: none;
    color: #0f3460;
    page-break-before: avoid;
}

.cover .subtitle {
    font-size: 14pt;
    color: #666;
    margin-top: 16px;
}

.cover .date {
    font-size: 11pt;
    color: #999;
    margin-top: 40px;
}
"""

def build_html():
    from datetime import date
    files = get_ordered_files()
    
    parts = [f"""
    <html><head>
    <meta charset="utf-8">
    </head><body>
    <div class="cover">
        <h1>{REPO_TITLE}</h1>
        <div class="subtitle">Documentación técnica completa</div>
        <div class="date">Generado: {date.today().strftime('%d/%m/%Y')}</div>
    </div>
    """]
    
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'attr_list'])
    
    for fname in files:
        fpath = os.path.join(WIKI_DIR, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        md.reset()
        html_content = md.convert(content)
        parts.append(f'<div class="wiki-page">{html_content}</div>')
    
    parts.append("</body></html>")
    return "\n".join(parts)

if __name__ == "__main__":
    print(f"Generando PDF para {REPO_TITLE}...")
    html_content = build_html()
    css = CSS(string=CSS_STYLES)
    HTML(string=html_content).write_pdf(OUTPUT_PDF, stylesheets=[css])
    size_mb = os.path.getsize(OUTPUT_PDF) / 1024 / 1024
    print(f"PDF generado: {OUTPUT_PDF} ({size_mb:.1f} MB)")
