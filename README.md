# Label Printer - Biodossel

Aplicativo desktop para gerar e imprimir mapas de etiquetas de clusters de espécimes, usado no fluxo de trabalho do projeto Biodossel/INPA. Lê planilhas `.xlsx` e arquivos `-ids`, faz o merge dos dados por cluster, e envia o mapa formatado para uma impressora térmica EPSON via ESC/POS.

## Funcionalidades

- Carregamento e merge de planilhas `.xlsx` (dados de espécimes) com arquivos `-ids` (clusters).
- Navegação entre clusters (anterior/próximo/busca).
- Impressão do mapa de um cluster em impressora térmica (Win32Raw / ESC-POS).
- Histórico local de impressões e contagem de produção diária.
- Filtro por placa mínima.
- Persistência dos dados carregados entre sessões (`%LOCALAPPDATA%\LabelPrinter`).

## Estrutura de dados esperada

Ao clicar em **Carregar dados**, selecione uma pasta contendo dois tipos de arquivo: um ou mais **demfiles** (planilhas com os dados de cada espécime) e um ou mais arquivos de **cluster list** (que dizem a qual cluster cada espécime pertence). O programa lê todos os arquivos da pasta que casam com cada padrão e faz o merge entre eles.

### Demfiles (`.xlsx`)

Um ou mais arquivos `.xlsx` na pasta — qualquer arquivo com essa extensão é lido e todos são concatenados em um único conjunto de dados. Cada linha representa um espécime. Colunas obrigatórias:

| Coluna | Exemplo | Descrição |
|---|---|---|
| `Specimen-code-prefix` | `BI` | Prefixo do código do espécime |
| `Specimen-code-number` | `00123` | Número do espécime |
| `Plate-ID` | `BIN065` | Placa onde o espécime está |
| `Position` | `A1` | Posição do espécime na placa |

O programa concatena `Specimen-code-prefix` + `Specimen-code-number` para formar o código único do espécime (ex: `BI00123`).

### Cluster list (arquivos terminados em `-ids`)

Um ou mais arquivos cujo **nome termina exatamente em `-ids`, sem extensão** (ex: `lote2026-ids`, não `lote2026-ids.txt`). É um arquivo de texto separado por tabulação (`\t`) com duas colunas — a primeira linha é ignorada:

1. **Código do cluster** (ex: `Cluster_001`)
2. **Identificador do espécime**, no formato `algumtexto_CODIGODOESPECIME` — o programa usa tudo depois do primeiro `_` como o código do espécime, para casar com o `Specimen-code` do demfile (ex: `amostra_BI00123` → `BI00123`)

Esse arquivo normalmente é a saída de uma ferramenta de clusterização (agrupamento de espécimes por similaridade, ex: código de barras genético), listando a qual cluster cada espécime pertence.

### Como os dados são combinados

Os dois conjuntos são unidos (merge) pelo código do espécime. O código final exibido e impresso é `Specimen-code_Position` (ex: `BI00123_A1`). Espécimes sem correspondência entre os dois arquivos (presentes só no demfile ou só no cluster list) são descartados do resultado e reportados no console ao carregar os dados.

Exemplo de pasta válida:

```
dados/
├── placas_lote1.xlsx     # demfile
├── placas_lote2.xlsx     # demfile
└── clusterizacao-ids     # cluster list (sem extensão)
```

## Download

Para apenas usar o programa (sem mexer no código), baixe o instalador mais recente na aba [Releases](https://github.com/aline-pfelix/label-printer/releases/latest) e rode o `.exe` de instalação. As seções abaixo são voltadas para desenvolvimento a partir do código-fonte.

## Estrutura do projeto

```
Label_Printer/
├── src/            # código-fonte
│   ├── main.py     # ponto de entrada
│   ├── ui.py       # interface Tkinter
│   ├── data.py     # leitura e merge das planilhas
│   ├── printing.py # geração e envio do mapa para a impressora
│   ├── history.py  # histórico de impressões e produção diária
│   └── utils.py    # utilitário de resolução de caminhos (assets)
├── assets/         # ícone e logo usados na UI e na impressão
├── scripts/        # scripts auxiliares de exploração/depuração de dados
├── Label_Printer.spec  # build do executável com PyInstaller
└── requirements.txt
```

## Instalação (a partir do código-fonte)

Requer Python 3.8+ e Windows (usa `pywin32`/`Win32Raw` para a impressora).

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
cd src
python main.py
```

1. Clique em **Carregar dados** e selecione a pasta com as planilhas `.xlsx` e os arquivos `-ids`.
2. Navegue entre os clusters com **Anterior**/**Posterior** ou pela busca.
3. Clique em **Imprimir** para enviar o mapa do cluster atual para a impressora configurada em **Configurações**.
4. Use **Produção do dia** para ver quantos clusters/indivíduos já foram processados hoje.
5. Use **Configurações** para ajustar impressora/textos da etiqueta pela interface, sem editar arquivos.

## Gerando o executável

O build usa [PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller Label_Printer.spec
```

O executável final fica em `dist/Label_Printer.exe`. O instalador publicado nas Releases é gerado separadamente a partir desse executável e enviado manualmente.

## Configuração

Na primeira execução, o programa cria `%LOCALAPPDATA%\LabelPrinter\config.json` com valores de **exemplo** (nome da impressora, instituição, e-mail de contato, texto de sorting) — cada instalação deve ajustá-los para os dados reais de quem for usar.

A forma recomendada de editar é pelo botão **Configurações** dentro do próprio app — abre uma janela com um campo para cada valor, sem precisar mexer em arquivos. `printer_name` deve bater com o nome da impressora configurado no Windows. As mudanças salvas valem a partir da próxima impressão.

Também é possível editar `config.json` diretamente com um editor de texto, se preferir:

```json
{
  "printer_name": "Nome da impressora (Windows)",
  "institution_name": "Nome da instituição",
  "contact_email": "contato@example.com",
  "sorting_label": "Sorting: EXEMPLO - Mês/Ano"
}
```

## Observações

- Erros de impressão são registrados em `%LOCALAPPDATA%\LabelPrinter\erro_impressora.log`.
- A licença (MIT) e a autoria estão no arquivo [LICENSE](LICENSE).

## Como citar

Félix, A. P. (2026). *Label Printer* (Versão 1.5.0) [Software]. https://github.com/aline-pfelix/label-printer
