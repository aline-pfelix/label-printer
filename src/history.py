from pathlib import Path
from datetime import datetime


# ---------------------------------------------------------------------- #
# GERENCIADOR DE HISTÓRICO E PRODUÇÃO                                    #
# ---------------------------------------------------------------------- #

class HistoryManager:

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.arquivo = self.data_dir / "history_print.txt"
        self.arquivo_producao = self.data_dir / "daily_production.txt"

    # ---- HISTÓRICO DE IMPRESSÃO ---- #

    def salvar(self, cluster):
        linha = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Cluster: {cluster}"
        with open(self.arquivo, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
        return linha

    def carregar_tudo(self):
        if not self.arquivo.exists():
            return []
        with open(self.arquivo, "r", encoding="utf-8") as f:
            return [l.strip() for l in f.readlines() if l.strip()]

    def ultimo_cluster(self):
        linhas = self.carregar_tudo()
        if not linhas:
            return None
        return linhas[-1].split(" - Cluster: ")[-1].strip()

    # ---- PRODUÇÃO DIÁRIA ---- #

    def _ler_producao(self):
        """Lê o arquivo de produção e retorna dict {data: {...}}."""
        dados = {}
        if not self.arquivo_producao.exists():
            return dados
        with open(self.arquivo_producao, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                partes = linha.split("|")
                if len(partes) < 4:
                    continue
                data = partes[0]
                clusters_set_str = partes[4].split("=", 1)[1] if len(partes) > 4 else ""
                dados[data] = {
                    "clusters":     int(partes[1].split("=")[1]),
                    "individuos":   int(partes[2].split("=")[1]),
                    "reimpressoes": int(partes[3].split("=")[1]),
                    "clusters_set": set(clusters_set_str.split(",")) - {""} if clusters_set_str else set(),
                }
        return dados

    def _salvar_producao(self, dados):
        """Reescreve o arquivo de produção a partir do dict."""
        with open(self.arquivo_producao, "w", encoding="utf-8") as f:
            for data, v in dados.items():
                clusters_set_str = ",".join(sorted(v["clusters_set"]))
                f.write(
                    f"{data}"
                    f"|clusters={v['clusters']}"
                    f"|individuos={v['individuos']}"
                    f"|reimpressoes={v['reimpressoes']}"
                    f"|clusters_set={clusters_set_str}\n"
                )

    def atualizar_producao(self, individuos_cluster, cluster):
        hoje = datetime.now().strftime("%Y-%m-%d")
        dados = self._ler_producao()

        if hoje not in dados:
            dados[hoje] = {
                "clusters": 0,
                "individuos": 0,
                "reimpressoes": 0,
                "clusters_set": set(),
            }

        registro = dados[hoje]
        if cluster in registro["clusters_set"]:
            registro["reimpressoes"] += 1
        else:
            registro["clusters"] += 1
            registro["individuos"] += individuos_cluster
            registro["clusters_set"].add(cluster)

        self._salvar_producao(dados)

    def ler_producao_hoje(self):
        """Retorna (clusters_unicos, individuos, reimpressoes) do dia atual."""
        hoje = datetime.now().strftime("%Y-%m-%d")
        dados = self._ler_producao()
        if hoje not in dados:
            return 0, 0, 0
        v = dados[hoje]
        return v["clusters"], v["individuos"], v["reimpressoes"]

    # ---- RESET ---- #

    def resetar(self):
        if self.arquivo.exists():
            self.arquivo.unlink()
        if self.arquivo_producao.exists():
            self.arquivo_producao.unlink()
