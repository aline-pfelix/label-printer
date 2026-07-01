# Label Printer - Biodossel

Aplicativo desktop (Tkinter) para gerar e imprimir mapas de etiquetas de clusters de espécimes, usado no fluxo de trabalho do projeto Biodossel/INPA. Lê planilhas `.xlsx` e arquivos `-ids`, faz o merge dos dados por cluster, e envia o mapa formatado para uma impressora térmica EPSON via ESC/POS.

## Funcionalidades

- Carregamento e merge de planilhas `.xlsx` (dados de espécimes) com arquivos `-ids` (clusters).
- Navegação entre clusters (anterior/próximo/busca).
- Impressão do mapa de um cluster em impressora térmica (Win32Raw / ESC-POS).
- Histórico local de impressões e contagem de produção diária.
- Filtro por placa mínima.
- Persistência dos dados carregados entre sessões (`%LOCALAPPDATA%\LabelPrinter`).

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
3. Clique em **Imprimir** para enviar o mapa do cluster atual para a impressora `Nome da impressora (Windows)`.
4. Use **Produção do dia** para ver quantos clusters/indivíduos já foram processados hoje.

## Gerando o executável

O build usa [PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller Label_Printer.spec
```

O executável final fica em `dist/Label_Printer.exe`. O instalador publicado nas Releases é gerado separadamente a partir desse executável e enviado manualmente.

## Observações

- O nome da impressora (`Nome da impressora (Windows)`) está fixo em `src/printing.py` — ajuste conforme o nome configurado no Windows.
- Erros de impressão são registrados em `%LOCALAPPDATA%\LabelPrinter\erro_impressora.log`.
