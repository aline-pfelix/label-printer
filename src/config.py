import json
from pathlib import Path


# ---------------------------------------------------------------------- #
# CONFIGURAÇÃO DO APLICATIVO                                             #
# ---------------------------------------------------------------------- #

# Valores de exemplo — cada usuário deve ajustá-los pela tela
# "Configurações" do app (ou editando config.json diretamente) para os
# dados reais da sua impressora e instituição.
DEFAULTS = {
    "printer_name": "Nome da impressora (Windows)",
    "institution_name": "Nome da instituição",
    "contact_email": "contato@example.com",
    "sorting_label": "Sorting: EXEMPLO - Mês/Ano",
}


# ---- CARREGAR CONFIGURAÇÃO ---- #

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


# ---- SALVAR CONFIGURAÇÃO ---- #

def salvar_config(data_dir, config):
    """Grava config.json em data_dir."""
    caminho = Path(data_dir) / "config.json"
    caminho.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
