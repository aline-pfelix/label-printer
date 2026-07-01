import os
import traceback
from datetime import datetime
from pathlib import Path

from escpos.printer import Win32Raw

from utils import resource_path

_LOG_PATH = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "LabelPrinter" / "erro_impressora.log"


# ---------------------------------------------------------------------- #
# IMPRESSÃO DO MAPA DE ETIQUETAS                                         #
# ---------------------------------------------------------------------- #

def print_maps(df, cluster, config):
    try:
        impressora = Win32Raw(config["printer_name"])
        p = impressora
        df_cluster = df[df["clusterCode"] == cluster]
        n_ind = len(df_cluster)

        # ---- CABEÇALHO ---- #
        p.set(align='center', bold=True, width=1, height=1)
        p.text("="*48 + "\n")
        p.image(str(resource_path("assets/logo_biodossel.jpg")))
        p.set(align='center', bold=False, width=1, height=1)
        p.text(f"{config['institution_name']}\n")
        p.set(align='center', bold=True, width=1, height=1)
        p.text("="*48 + "\n\n")

        # ---- INFORMAÇÕES ---- #
        p.set(align='left', bold=False)
        p.text(f"DATA: {datetime.now().strftime('%d/%m/%Y')}\n\n")
        p.text(f"{config['sorting_label']}\n")
        p.text(f"Dúvidas contatar: {config['contact_email']}\n")
        p.text("-"*48 + "\n")

        # ---- CLASSIFICAÇÃO ---- #
        p._raw(b'\x1b\x40')
        p.set(align='center', bold=True)
        p.text(f"** Preenchimento Exclusivo - {config['institution_name']} **\n")
        p.set(bold=False)
        p.text("Aus=Ausente  Mut=Múltiplos  Rem=Removido\n\n")

        # ---- CLUSTER ---- #
        p._raw(b'\x1b\x40')
        p.set(align='center', bold=True, width=2, height=2, invert=True)
        p.text(f"CLUSTER: {cluster} - {n_ind} indivíduos\n\n")
        p._raw(b'\x1b\x40')

        # ---- CONTEÚDO ---- #
        for placa, grupo in df_cluster.groupby("Plate-ID"):
            p.set(align='left', bold=True)
            p.text(f"PLACA: {placa}{' ' * 10}Aus | Mut | Rem\n")
            p.set(bold=False)
            for ind in grupo["Specimen-code"]:
                nome = f"{ind[:22]:22}"
                p.text(f"{nome} [ ]   [ ]   [ ]\n")
            p.text("\n")

        p.text("-"*48 + "\n\n")
        p.cut(mode='PART')
        p.close()

        return n_ind  # ← retorna para a UI usar na produção diária

    except Exception:
        _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_LOG_PATH, "a") as f:
            f.write("\n--- ERRO ---\n")
            traceback.print_exc(file=f)
        raise
