# Script exploratório para depurar o merge entre planilhas .xlsx e arquivos
# -ids ao investigar dados de um lote específico. Não é um teste automatizado
# — edite PASTA_DADOS abaixo antes de rodar localmente.
import pandas as pd
from pathlib import Path

PASTA_DADOS = Path(r"caminho/para/dados")  # ← troca pelo caminho real


# ---------------------------------------------------------------------- #
# EXPLORAÇÃO E DEPURAÇÃO DE DADOS                                        #
# ---------------------------------------------------------------------- #

# ---- LEITURA DOS DEMFILES (XLSX) ---- #
dfs = []
for f in PASTA_DADOS.iterdir():
    if f.name.endswith(".xlsx"):
        dfs.append(pd.read_excel(f, dtype=str))

df_total_dem = pd.concat(dfs, ignore_index=True)
df_total_dem["Specimen-code"] = df_total_dem["Specimen-code-prefix"] + df_total_dem["Specimen-code-number"]
df_total_dem_resumo = df_total_dem[["Specimen-code", "Plate-ID", "Position"]].copy()

# ---- LEITURA DO CLUSTER LIST (-IDS) ---- #
dfs_cluster = []
for f in PASTA_DADOS.iterdir():
    if f.name.endswith("-ids"):
        dfs_cluster.append(pd.read_csv(f, sep="\t", dtype=str, engine="python", quoting=3))

df_total_cluster = pd.concat(dfs_cluster, ignore_index=True)
df_total_cluster.columns = ['clusterCode', 'especime']
df_total_cluster['specimenCodeCluster'] = df_total_cluster['especime'].str.split('_').str[1]
print(f"Clusters únicos no ids: {df_total_cluster['clusterCode'].nunique()}")

# ---- DIAGNÓSTICO ---- #
print(f"Total xlsx: {len(df_total_dem_resumo)}")
print(f"Total -ids: {len(df_total_cluster)}")
print(f"\nExemplos Specimen-code do xlsx:")
print(df_total_dem_resumo['Specimen-code'].head(5).tolist())
print(f"\nExemplos specimenCodeCluster do -ids:")
print(df_total_cluster['specimenCodeCluster'].head(5).tolist())

# ---- MERGE ---- #
df_final = pd.merge(df_total_dem_resumo, df_total_cluster, left_on="Specimen-code", right_on="specimenCodeCluster", how="outer")
df_final["Specimen-code"] = df_final["Specimen-code"] + "_" + df_final["Position"]
df_final = df_final.drop(columns=["especime", "specimenCodeCluster", "Position"])
df = df_final.dropna(subset=["clusterCode"])
df = df.sort_values(["clusterCode", "Plate-ID", "Specimen-code"])

print(f"\nTotal após merge: {len(df_final)}")
print(f"Total após dropna: {len(df)}")
print(f"Clusters únicos: {df['clusterCode'].nunique()}")

# Specimens no -ids sem par no xlsx
nao_encontrados = df_total_cluster[
    ~df_total_cluster['specimenCodeCluster'].isin(df_total_dem_resumo['Specimen-code'])
]
print(f"\nSpecimens no -ids sem par no xlsx: {len(nao_encontrados)}")
print(nao_encontrados['specimenCodeCluster'].head(10).tolist())
