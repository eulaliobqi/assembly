"""
Gera roteiro-apresentacao-minicurso.docx a partir do .md homonimo.
Reutiliza o parser Markdown->DOCX de gerar_artigo_docx.py (mesmo estilo:
Times New Roman 12pt, ~1.5 linha, tabelas com cabecalho sombreado).
"""
from pathlib import Path

from gerar_artigo_docx import create_word

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "roteiro-apresentacao-minicurso.md"
OUTPUT = ROOT / "roteiro-apresentacao-minicurso.docx"

if __name__ == "__main__":
    create_word(SOURCE, OUTPUT)
