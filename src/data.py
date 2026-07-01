import pandas as pd
from pathlib import Path


def carregar_dados(pasta):
    pasta = Path(pasta)

    # Leitura e Dataframe de dados
    dfs = []
    for f in pasta.iterdir():
        if f.name.endswith(".xlsx"):
            dfs.append(pd.read_excel(f, dtype=str))

    df_total_dem = pd.concat(dfs, ignore_index=True)
    df_total_dem["Specimen-code"] = (df_total_dem["Specimen-code-prefix"] + df_total_dem["Specimen-code-number"])
    df_total_dem_resumo = df_total_dem[["Specimen-code", "Plate-ID", "Position"]].copy()

    dfs_cluster = []
    for f in pasta.iterdir():
        if f.name.endswith("-ids"):
            dfs_cluster.append(pd.read_csv(f, sep="\t", dtype=str, engine="python"))

    df_total_cluster = pd.concat(dfs_cluster, ignore_index=True)
    df_total_cluster.columns = ['clusterCode', 'especime']
    df_total_cluster['specimenCodeCluster'] = (df_total_cluster['especime'].str.split('_').str[1])

    df_final = pd.merge(df_total_dem_resumo, df_total_cluster, left_on="Specimen-code", right_on="specimenCodeCluster", how="outer")
    df_final["Specimen-code"] = (df_final["Specimen-code"] + "_" + df_final["Position"])
    df_final = df_final.drop(columns=["especime", "specimenCodeCluster", "Position"])
    df = df_final.dropna(subset=["clusterCode", 'Specimen-code'])

    df = df.sort_values(["clusterCode", "Plate-ID", "Specimen-code"])

    print(f"Total xlsx: {len(df_total_dem_resumo)}")
    print(f"Total -ids: {len(df_total_cluster)}")
    print(f"Total após merge: {len(df_final)}")
    print(f"Total após dropna: {len(df)}")
    print(f"Clusters únicos: {df['clusterCode'].nunique()}")

    # verifica se há specimens no -ids que não batem com o xlsx
    nao_encontrados = df_total_cluster[
        ~df_total_cluster['specimenCodeCluster'].isin(df_total_dem_resumo['Specimen-code'])
    ]
    print(f"Specimens no -ids sem par no xlsx: {len(nao_encontrados)}")
    print(nao_encontrados['specimenCodeCluster'].head(10))

    return df


def obter_clusters(df):
    return list(df["clusterCode"].unique())
