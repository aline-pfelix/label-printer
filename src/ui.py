import tkinter as tk
import os
import re
import pandas as pd

from tkinter import messagebox, simpledialog, filedialog
from pathlib import Path

from printing import print_maps
from data import carregar_dados, DadosInvalidosError
from history import HistoryManager
from utils import resource_path
from config import carregar_config, salvar_config


# ---------------------------------------------------------------------- #
# INTERFACE GRÁFICA (TKINTER)                                            #
# ---------------------------------------------------------------------- #

class App:

    def __init__(self, root):
        self.root = root
        self.df = None
        self.clusters = []
        self.idx = 0
        self.placa_minima = None  # filtro em memória

        # ---- DIRETÓRIO DE DADOS ---- #
        app_data = Path(os.environ.get("LOCALAPPDATA", Path.home()))
        self.data_dir = app_data / "LabelPrinter"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.parquet_path = self.data_dir / "df_salvo.parquet"

        # Remove pickle legado se ainda existir
        pkl_legado = self.data_dir / "df_salvo.pkl"
        if pkl_legado.exists():
            pkl_legado.unlink()

        # HistoryManager é a única fonte do caminho dos arquivos de histórico
        self.history = HistoryManager(self.data_dir)
        self.historico_local = self.history.carregar_tudo()

        # Configuração editável (nome da impressora, textos da etiqueta)
        self.config = carregar_config(self.data_dir)

        root.iconbitmap(str(resource_path("assets/tag.ico")))
        self.build_ui()

        # ---- CARREGAR DADOS DO ÚLTIMO USO ---- #
        try:
            self.df = pd.read_parquet(self.parquet_path)
            self.clusters = self._filtrar_clusters(self.df)  # ← usa filtro

            ultimo = self.history.ultimo_cluster()
            if ultimo and ultimo in self.clusters:
                self.idx = self.clusters.index(ultimo) + 1
                if self.idx >= len(self.clusters):
                    self.idx = len(self.clusters) - 1
            else:
                self.idx = 0

            self.status.config(
                text=f"✔ Dados carregados do último uso ({len(self.df)} registros)",
                fg="green"
            )

        except FileNotFoundError:
            self.status.config(text="Nenhum dado salvo encontrado", fg="red")

        except Exception:
            # Arquivo corrompido ou incompatível — apaga e pede novo carregamento
            if self.parquet_path.exists():
                self.parquet_path.unlink()
            self.status.config(
                text="⚠ Dados salvos corrompidos — carregue os dados novamente",
                fg="orange"
            )

        if self.df is not None and self.clusters:
            self.atualizar()

    # ---- INTERFACE ---- #

    def build_ui(self):
        frame_carregar = tk.Frame(self.root)
        frame_carregar.pack(pady=10)
        tk.Button(
            frame_carregar, text="Carregar dados",
            command=self.carregar_dados_ui,
            bg="blue", fg="white"
        ).pack(side="left")
        tk.Button(
            frame_carregar, text="Input esperado",
            command=self.mostrar_ajuda_arquivos
        ).pack(side="left", padx=5)

        self.label = tk.Label(self.root, font=("Arial", 16, "bold"))
        self.label.pack(pady=10)

        # Busca
        frame_busca = tk.Frame(self.root)
        frame_busca.pack()
        self.entry = tk.Entry(frame_busca)
        self.entry.pack(side="left")
        tk.Button(frame_busca, text="Buscar", command=self.buscar).pack(side="left")

        # Navegação e impressão
        frame_btn = tk.Frame(self.root)
        frame_btn.pack(pady=20)
        tk.Button(frame_btn, text="< Anterior",  command=self.anterior, width=10, height=3).pack(side="left")
        tk.Button(frame_btn, text="Imprimir",    command=self.imprimir, width=20, height=3, bg="green", fg="white").pack(side="left")
        tk.Button(frame_btn, text="Posterior >", command=self.proximo,  width=10, height=3).pack(side="left")

        # Histórico
        frame_hist = tk.Frame(self.root)
        frame_hist.pack()
        scroll = tk.Scrollbar(frame_hist)
        scroll.pack(side="right", fill="y")
        self.hist = tk.Text(frame_hist, height=8, width=60, yscrollcommand=scroll.set)
        self.hist.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.hist.yview)

        # Ações
        tk.Button(
            self.root, text="Resetar Histórico",
            bg="red", fg="white",
            command=self.resetar_historico
        ).pack(pady=5)

        tk.Button(
            self.root, text="Produção do dia",
            bg="purple", fg="white",
            command=self.mostrar_producao
        ).pack(pady=5)

        tk.Button(
            self.root, text="Configurações",
            command=self.abrir_configuracoes
        ).pack(pady=5)

        # ---- FILTRO DE PLACA MÍNIMA ---- #
        frame_filtro = tk.Frame(self.root)
        frame_filtro.pack(pady=5)
        tk.Label(frame_filtro, text="Placa mínima:").pack(side="left")
        self.entry_filtro = tk.Entry(frame_filtro, width=10)
        self.entry_filtro.pack(side="left", padx=5)
        tk.Button(
            frame_filtro, text="Aplicar filtro",
            command=self.aplicar_filtro
        ).pack(side="left")
        self.label_filtro = tk.Label(frame_filtro, text="sem filtro", fg="gray")
        self.label_filtro.pack(side="left", padx=8)

        self.status = tk.Label(self.root)
        self.status.pack()

    # ---- ATUALIZAR ---- #

    def atualizar(self):
        if self.df is None or self.df.empty or not self.clusters:
            self.label.config(text="Nenhum cluster carregado")
            self.hist.delete("1.0", tk.END)
            return

        cluster = self.clusters[self.idx]
        self.label.config(text=f"Cluster: {cluster}\n{self.idx + 1} de {len(self.clusters)}")

        self.hist.delete("1.0", tk.END)
        for h in self.historico_local[-10:]:
            self.hist.insert(tk.END, h + "\n")
        self.hist.see(tk.END)

    # ---- NAVEGAÇÃO ---- #

    def proximo(self):
        if self.idx < len(self.clusters) - 1:
            self.idx += 1
            self.atualizar()

    def anterior(self):
        if self.idx > 0:
            self.idx -= 1
            self.atualizar()

    def buscar(self):
        nome = self.entry.get().strip()
        if nome in self.clusters:
            self.idx = self.clusters.index(nome)
            self.atualizar()
        else:
            self.status.config(text="Cluster não encontrado", fg="red")
            self.root.after(1000, lambda: self.status.config(text=""))

    # ---- IMPRESSÃO ---- #

    def imprimir(self):
        if not self.clusters:
            return

        cluster = self.clusters[self.idx]
        erro_impressao = None

        n_ind = len(self.df[self.df["clusterCode"] == cluster])

        try:
            print_maps(self.df, cluster, self.config)
        except Exception as e:
            erro_impressao = e

        linha = self.history.salvar(cluster)
        self.history.atualizar_producao(n_ind, cluster)
        self.historico_local.append(linha)

        if self.idx < len(self.clusters) - 1:
            self.idx += 1

        self.atualizar()

        if erro_impressao:
            messagebox.showerror(
                "Aviso de Impressão",
                f"Cluster {cluster} pode ter sido impresso, mas houve um erro:\n{str(erro_impressao)}"
            )

    # ---- PRODUÇÃO ---- #

    def mostrar_producao(self):
        clusters, individuos, reimp = self.history.ler_producao_hoje()
        messagebox.showinfo(
            "Produção do dia",
            f"Clusters únicos: {clusters}\n"
            f"Indivíduos processados: {individuos}\n"
            f"Reimpressões: {reimp}"
        )

    # ---- CONFIGURAÇÕES ---- #

    def abrir_configuracoes(self):
        janela = tk.Toplevel(self.root)
        janela.title("Configurações")
        janela.resizable(False, False)
        janela.grab_set()  # janela modal

        campos = [
            ("printer_name", "Nome da impressora:"),
            ("institution_name", "Instituição (impressa na etiqueta):"),
            ("contact_email", "E-mail de contato:"),
            ("sorting_label", "Texto de sorting:"),
        ]

        entradas = {}
        for i, (chave, rotulo) in enumerate(campos):
            tk.Label(janela, text=rotulo).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry = tk.Entry(janela, width=45)
            entry.insert(0, self.config.get(chave, ""))
            entry.grid(row=i, column=1, padx=10, pady=5)
            entradas[chave] = entry

        def salvar():
            novo_config = {chave: entrada.get().strip() for chave, entrada in entradas.items()}

            if not novo_config["printer_name"]:
                messagebox.showerror("Erro", "O nome da impressora não pode ficar vazio.", parent=janela)
                return

            self.config = novo_config
            salvar_config(self.data_dir, self.config)
            janela.destroy()
            self.status.config(text="✔ Configurações salvas", fg="green")

        frame_botoes = tk.Frame(janela)
        frame_botoes.grid(row=len(campos), column=0, columnspan=2, pady=10)
        tk.Button(frame_botoes, text="Salvar", bg="green", fg="white", command=salvar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Cancelar", command=janela.destroy).pack(side="left", padx=5)

    # ---- RESET ---- #

    def resetar_historico(self):
        if not messagebox.askyesno("Confirmação", "Deseja resetar?"):
            return

        texto = simpledialog.askstring(
            "Confirmação final",
            "Isso afetará a continuação da identificação dos clusters já analisados.\n"
            "Digite RESET para confirmar:"
        )
        if texto != "RESET":
            return

        self.history.resetar()
        self.historico_local.clear()

        if self.parquet_path.exists():
            self.parquet_path.unlink()

        self.df = None
        self.clusters = []
        self.idx = 0

        self.status.config(text="✔ Histórico e dados resetados", fg="green")
        self.atualizar()

    # ---- CARREGAR DADOS ---- #

    def mostrar_ajuda_arquivos(self):
        janela = tk.Toplevel(self.root)
        janela.title("Input esperado")
        janela.resizable(False, False)
        janela.grab_set()  # janela modal

        tk.Label(
            janela, text="A pasta selecionada deve conter:",
            font=("Arial", 10, "bold"), anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        secoes = [
            (
                "1. Demultiplexing (.xlsx) — um ou mais arquivos",
                "Colunas obrigatórias:",
                "Specimen-code-prefix, Specimen-code-number,\nPlate-ID, Position",
            ),
            (
                "2. Cluster (arquivo terminado em \"-ids\") — apenas 1 arquivo",
                "Formato:",
                "Texto separado por TABULAÇÃO, 2 colunas:\ncódigo do cluster e espécime",
            ),
        ]

        row = 1
        for titulo, rotulo, valor in secoes:
            tk.Label(
                janela, text=titulo, font=("Arial", 9, "bold"), anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=15)
            row += 1
            tk.Label(janela, text=rotulo, anchor="w").grid(row=row, column=0, sticky="w", padx=30)
            row += 1
            tk.Label(
                janela, text=valor, font=("Consolas", 9), justify="left", anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=30, pady=(0, 12))
            row += 1

        tk.Label(
            janela, text="Todos os arquivos devem estar na mesma pasta.",
            font=("Arial", 9, "italic"), anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=15, pady=(0, 15))
        row += 1

        tk.Button(
            janela, text="Entendi", width=12, command=janela.destroy
        ).grid(row=row, column=0, pady=(0, 15))

    def carregar_dados_ui(self):
        self.status.config(text="⏳ Carregando dados…", fg="blue")
        self.root.update_idletasks()

        pasta = filedialog.askdirectory(title="Selecione a pasta com os dados")
        if not pasta:
            self.status.config(text="")
            return

        try:
            df = carregar_dados(Path(pasta))
        except DadosInvalidosError as e:
            messagebox.showerror("Arquivos inválidos", str(e))
            self.status.config(text="")
            return
        except Exception as e:
            messagebox.showerror(
                "Erro inesperado",
                f"Ocorreu um erro ao carregar os dados:\n{e}\n\n"
                "Verifique se a pasta selecionada contém os arquivos corretos "
                "(veja \"Quais arquivos usar?\")."
            )
            self.status.config(text="")
            return

        self.df = df
        self.clusters = self._filtrar_clusters(self.df)  # ← usa filtro
        self.idx = 0

        messagebox.showinfo("Sucesso", f"{len(self.clusters)} clusters carregados")
        self.status.config(
            text=f"✔ {len(self.clusters)} clusters carregados ({len(self.df)} registros)",
            fg="green"
        )
        self.atualizar()

        self.df.to_parquet(self.parquet_path, index=False)

    # ---- FILTRO DE PLACA ---- #

    def _placa_valida(self, placa, minima):
        """Retorna True se placa >= minima, comparando letra depois número."""
        if minima is None:
            return True
        pat = re.compile(r"^BI([A-Z])(\d+)$")
        m_p = pat.match(str(placa))
        m_m = pat.match(str(minima))
        if not m_p or not m_m:
            return False
        letra_p, num_p = m_p.group(1), int(m_p.group(2))
        letra_m, num_m = m_m.group(1), int(m_m.group(2))
        if letra_p != letra_m:
            return letra_p > letra_m  # N > M > L etc.
        return num_p >= num_m

    def _filtrar_clusters(self, df):
        """Retorna clusters cujos Plate-ID passam no filtro de placa mínima."""
        if self.placa_minima is None:
            return sorted(df["clusterCode"].unique())
        mask = df["Plate-ID"].apply(lambda p: self._placa_valida(p, self.placa_minima))
        return sorted(df[mask]["clusterCode"].unique())

    def aplicar_filtro(self):
        nova = self.entry_filtro.get().strip().upper()

        # Valida formato
        if nova and not re.match(r"^BI[A-Z]\d+$", nova):
            messagebox.showerror(
                "Formato inválido",
                "Use o formato BIN065, BIM100, etc.\nOu deixe em branco para remover o filtro."
            )
            return

        placa_str = nova if nova else "sem filtro"

        # Confirmação obrigatória antes de aplicar
        if not messagebox.askyesno(
            "Confirmar filtro",
            f"Aplicar filtro: {placa_str}?\n\nA lista de clusters será atualizada."
        ):
            return

        self.placa_minima = nova if nova else None
        self.label_filtro.config(
            text=placa_str,
            fg="blue" if self.placa_minima else "gray"
        )

        if self.df is not None:
            self.clusters = self._filtrar_clusters(self.df)
            self.idx = 0
            self.atualizar()
            self.status.config(
                text=f"Filtro aplicado: {placa_str} — {len(self.clusters)} clusters visíveis",
                fg="blue"
            )
