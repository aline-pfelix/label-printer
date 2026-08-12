import pandas as pd
from pathlib import Path


# ---------------------------------------------------------------------- #
# PIPELINE DE CARREGAMENTO E MERGE DOS DADOS                             #
# ---------------------------------------------------------------------- #

class DadosInvalidosError(Exception):
    """Erro amigável, com mensagem pronta para exibir ao usuário na UI."""


COLUNAS_XLSX_OBRIGATORIAS = {"Specimen-code-prefix", "Specimen-code-number", "Plate-ID", "Position"}


def carregar_dados(pasta):
    pasta = Path(pasta)

    # ---- ETAPA 1: LEITURA DOS DEMFILES (XLSX) ---- #
    arquivos_xlsx = [f for f in pasta.iterdir() if f.name.endswith(".xlsx")]
    if not arquivos_xlsx:
        raise DadosInvalidosError(
            f"Nenhum arquivo .xlsx encontrado em:\n{pasta}\n\n"
            "A pasta selecionada deve conter os arquivos de demultiplexação (.xlsx) "
            "e os arquivos de cluster (terminados em \"-ids\")."
        )

    dfs = []
    for f in arquivos_xlsx:
        df_xlsx = pd.read_excel(f, dtype=str)
        faltando = COLUNAS_XLSX_OBRIGATORIAS - set(df_xlsx.columns)
        if faltando:
            raise DadosInvalidosError(
                f"O arquivo \"{f.name}\" não tem as colunas esperadas: {', '.join(sorted(faltando))}.\n\n"
                "Verifique se este é realmente um arquivo de demultiplexação (.xlsx) "
                "e não outro tipo de planilha."
            )
        dfs.append(df_xlsx)

    df_total_dem = pd.concat(dfs, ignore_index=True)
    df_total_dem["Specimen-code"] = (df_total_dem["Specimen-code-prefix"] + df_total_dem["Specimen-code-number"])
    df_total_dem_resumo = df_total_dem[["Specimen-code", "Plate-ID", "Position"]].copy()

    # ---- ETAPA 2: LEITURA DO CLUSTER LIST (-IDS) ---- #
    arquivos_ids = [f for f in pasta.iterdir() if f.name.endswith("-ids")]
    if not arquivos_ids:
        raise DadosInvalidosError(
            f"Nenhum arquivo \"-ids\" encontrado em:\n{pasta}\n\n"
            "A pasta selecionada deve conter o arquivo de cluster (terminado em \"-ids\"), "
            "separado por tabulação, com 2 colunas: código do cluster e especime."
        )

    if len(arquivos_ids) > 1:
        nomes = "\n".join(f"- {f.name}" for f in arquivos_ids)
        raise DadosInvalidosError(
            f"Foram encontrados {len(arquivos_ids)} arquivos \"-ids\" em:\n{pasta}\n\n"
            f"{nomes}\n\n"
            "Apenas 1 arquivo de cluster é permitido por pasta. Remova os arquivos extras "
            "e mantenha somente o correto."
        )

    f = arquivos_ids[0]
    try:
        df_ids = pd.read_csv(f, sep="\t", dtype=str, engine="python")
    except Exception as e:
        raise DadosInvalidosError(
            f"Não foi possível ler o arquivo \"{f.name}\" como um arquivo -ids válido.\n\n"
            "Ele parece estar corrompido, não separado por tabulação, ou não é o tipo de "
            "arquivo esperado (verifique se não é um .xlsx renomeado ou um arquivo de outro formato).\n\n"
            f"Detalhe técnico: {e}"
        ) from e

    if df_ids.shape[1] != 2:
        raise DadosInvalidosError(
            f"O arquivo \"{f.name}\" tem {df_ids.shape[1]} coluna(s) após a leitura, mas eram "
            "esperadas exatamente 2 (código do cluster e especime), separadas por tabulação.\n\n"
            "Verifique se este é o arquivo -ids correto."
        )

    df_total_cluster = df_ids
    df_total_cluster.columns = ['clusterCode', 'especime']
    df_total_cluster['specimenCodeCluster'] = (df_total_cluster['especime'].str.split('_').str[1])

    # ---- ETAPA 3: MERGE E LIMPEZA ---- #
    df_final = pd.merge(df_total_dem_resumo, df_total_cluster, left_on="Specimen-code", right_on="specimenCodeCluster", how="outer")
    df_final["Specimen-code"] = (df_final["Specimen-code"] + "_" + df_final["Position"])
    df_final = df_final.drop(columns=["especime", "specimenCodeCluster", "Position"])
    df = df_final.dropna(subset=["clusterCode", "Specimen-code"])

    df = df.sort_values(["clusterCode", "Plate-ID", "Specimen-code"])

    # ---- ETAPA 4: DIAGNÓSTICO ---- #
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
