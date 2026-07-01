import sys
from pathlib import Path


def resource_path(relative_path):
    """Caminho absoluto de um arquivo em assets/, tanto em modo de
    desenvolvimento quanto em um executável empacotado pelo PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent
    return base / relative_path
