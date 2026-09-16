"""
Script para converter relatorio_tecnico.md em relatorio_tecnico.pdf
Utiliza o mecanismo Chromium do Microsoft Edge para renderização impecável com CSS e paginação.
"""
import os
import subprocess
import markdown

def gerar_pdf():
    md_file = "relatorio_tecnico.md"
    html_file = "relatorio_tecnico.html"
    pdf_file = "relatorio_tecnico.pdf"

    with open(md_file, "r", encoding="utf-8") as f:
        md_text = f.read()

    html_content = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "codehilite", "toc"]
    )

    full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Técnico - Arquitetura e Desenvolvimento de APIs - UNINTER</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm 20mm 15mm;
            @bottom-right {{
                content: counter(page);
            }}
        }}
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
            color: #1a1a1a;
            line-height: 1.6;
            font-size: 11pt;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }}
        h1 {{
            color: #0d3b66;
            font-size: 20pt;
            border-bottom: 2px solid #0d3b66;
            padding-bottom: 6px;
            margin-top: 25px;
            margin-bottom: 12px;
            page-break-after: avoid;
        }}
        h2 {{
            color: #1e3d59;
            font-size: 15pt;
            border-bottom: 1px solid #d0d7de;
            padding-bottom: 4px;
            margin-top: 22px;
            margin-bottom: 10px;
            page-break-after: avoid;
        }}
        h3 {{
            color: #17252a;
            font-size: 12pt;
            margin-top: 16px;
            margin-bottom: 8px;
            page-break-after: avoid;
        }}
        h4 {{
            color: #2b7a78;
            font-size: 11pt;
            margin-top: 12px;
            margin-bottom: 6px;
            page-break-after: avoid;
        }}
        p, li {{
            font-size: 10.5pt;
            text-align: justify;
        }}
        strong {{
            color: #0b2545;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 9.5pt;
            page-break-inside: avoid;
        }}
        th, td {{
            border: 1px solid #d0d7de;
            padding: 8px 10px;
            text-align: left;
            vertical-align: middle;
        }}
        th {{
            background-color: #f1f5f9;
            color: #0f172a;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        pre, code {{
            font-family: 'Consolas', 'Courier New', monospace;
            background-color: #f6f8fa;
            border-radius: 4px;
        }}
        code {{
            padding: 2px 4px;
            font-size: 9.5pt;
            color: #0969da;
        }}
        pre {{
            padding: 12px;
            border: 1px solid #e1e4e8;
            overflow-x: auto;
            font-size: 9pt;
            line-height: 1.45;
            page-break-inside: avoid;
        }}
        pre code {{
            padding: 0;
            background: none;
            color: #24292e;
        }}
        hr {{
            border: 0;
            height: 1px;
            background: #e1e4e8;
            margin: 20px 0;
        }}
        blockquote {{
            margin: 15px 0;
            padding: 8px 16px;
            color: #57606a;
            background-color: #f6f8fa;
            border-left: 4px solid #0969da;
            page-break-inside: avoid;
        }}
        .header-box {{
            background: linear-gradient(135deg, #0d3b66, #001e3d);
            color: #ffffff;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 25px;
        }}
        .header-box h1, .header-box h2 {{
            color: #ffffff;
            border: none;
            margin: 0 0 8px 0;
            padding: 0;
        }}
        a {{
            color: #0969da;
            text-decoration: none;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"[+] HTML intermediário gerado: {html_file}")

    # Localiza o executável do Microsoft Edge
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    edge_exe = None
    for p in edge_paths:
        if os.path.exists(p):
            edge_exe = p
            break

    if not edge_exe:
        raise FileNotFoundError("Executável do Microsoft Edge não encontrado nos caminhos padrão.")

    abs_html = os.path.abspath(html_file)
    abs_pdf = os.path.abspath(pdf_file)

    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={abs_pdf}",
        f"file:///{abs_html.replace(os.sep, '/')}"
    ]

    print("[*] Renderizando PDF via Chromium Headless...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
        size_kb = os.path.getsize(pdf_file) / 1024
        print(f"[V] PDF gerado com sucesso: {pdf_file} ({size_kb:.1f} KB)")
    else:
        print(f"[X] Falha ao gerar PDF: {result.stderr}")

if __name__ == "__main__":
    gerar_pdf()
