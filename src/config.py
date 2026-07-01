import json
from pathlib import Path

DEFAULTS = {
    "printer_name": "Nome da impressora (Windows)",
    "institution_name": "Instituto Nacional de Pesquisas da Amazônia",
    "contact_email": "contato@example.com",
    "sorting_label": "Sorting: EXEMPLO - Mês/Ano",
}


def carregar_config(data_dir):
    """Lê config.json em data_dir, criando com valores padrão se não existir."""
    caminho = Path(data_dir) / "config.json"

    if not caminho.exists():
        caminho.write_text(json.dumps(DEFAULTS, indent=2, ensure_ascii=False), encoding="utf-8")
        return dict(DEFAULTS)

    dados = json.loads(caminho.read_text(encoding="utf-8"))
    config = dict(DEFAULTS)
    config.update(dados)
    return config
