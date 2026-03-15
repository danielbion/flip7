# Flip 7 - Réplica do Jogo de Cartas

Este projeto gera um arquivo PDF contendo as cartas prontas para impressão do jogo **Flip 7**, replicando suas mecânicas e quantidade de cartas. Ele também inclui as cartas adicionais e únicas, permitindo a substituição e customização do jogo.

O sistema desenha as cartas com um formato que lembra o jogo UNO (um círculo oval inclinado no meio) de forma programática utilizando a biblioteca gráfica `Pillow` do Python. Depois gera um arquivo PDF otimizado para impressão (Página A4 com marcas de corte) usando a biblioteca `reportlab`.

## 🛠 Pré-requisitos e Configuração do Ambiente

Este projeto utiliza o [uv](https://github.com/astral-sh/uv) como gerenciador de pacotes e ambientes do Python, por se tratar de uma alternativa extremamente veloz ao pip.

1. **Instale o `uv` (caso não tenha instalado):**
   Veja as instruções completas no [site oficial do uv](https://docs.astral.sh/uv/getting-started/installation/).
   No Windows, você pode instalar rodando no PowerShell:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Acesse o diretório do projeto e inicialize/instale as dependências:**
   ```bash
   cd c:\Projects\flip7
   uv init
   uv add pillow reportlab tqdm
   ```
   *(O projeto já vem configurado se você já possui os arquivos `pyproject.toml` e `uv.lock`. Nesse caso, apenas execute `uv sync`).*

## 🚀 Como gerar o PDF das cartas

Não é necessário ativar um ambiente virtual manualmente com o `uv`. Para rodar o script e gerar as cartas, basta executar o seguinte comando a partir da pasta raiz do projeto (`c:\Projects\flip7`):

```bash
uv run make_cards.py
```

Isso fará com que o script leia o arquivo `cards.json` e gere o arquivo de saída `print_flip7.pdf` contendo as exatas quantidades de cartas prontas para imprimir. Após a geração, basta abrir esse arquivo e mandar para a impressora!

---

## 🎨 Como Personalizar as Cartas (cards.json)

Todas as definições visuais, textos e contagens de cartas estão parametrizadas no arquivo `cards.json`. Ao abrir o arquivo, você notará duas seções principais: `"settings"` e `"cards"`.

### 1. Seção `"settings"` (Configurações Gerais Básicas)
Esta seção altera o visual de **todas** as cartas ao mesmo tempo.

- `width_mm`: Largura da carta em milímetros (padrão 63mm).
- `height_mm`: Altura da carta em milímetros (padrão 88mm).
- `dpi`: Definição e qualidade de impressão da carta (padrão 300).
- `font`: Nome da fonte que as cartas utilizarão. O script tentará usar a fonte que você escrever (precisa estar instalada no seu sistema). Se não encontrar, ele utilizará uma fonte padrão. Ex: `"arialbd.ttf"`, `"impact.ttf"`.
- `bg_color`: Cor de fundo da carta em código Hexadecimal (padrão `"#FFFFFF"` para branco).
- `oval_thickness`: A espessura da linha do anel/círculo central (padrão `8`).
- `font_size_center`: O tamanho da fonte do texto/número que fica no centro do anel oval.
- `font_size_corner`: O tamanho da fonte dos números que ficam nas quinas das cartas.
- `tilt_oval`: O ângulo de inclinação do anel central.

### 2. Seção `"cards"` (Deck e Tipos de Cartas)
A seção de cartas é uma lista, em que cada item define um tipo de carta no jogo. Você pode facilmente alterar quantidade, nome ou adicionar cartas personalizadas.

Exemplo de uma carta na lista:
```json
{ "id": "3", "label": "3", "count": 3, "color": "#FF4500" }
```

**Como alterar atributos:**
- `"label"`: O texto ou número que será impresso efetivamente no centro e nas pontas da carta. Para quebrar linha (como no caso do "Flip Three"), usamos o `\n` (Ex: `"Flip\nThree"`).
- `"count"`: O número de cópias que entrarão no baralho final do jogo. No exemplo acima, existem 3 cópias da carta "3". Se você quer tirar uma carta do jogo para testar, mude o count para `0`.
- `"color"`: A cor específica da carta! É a cor que vai aplicar no texto e no anel/cigarra central. Coloque o código da cor no formato Hexadecimal (`#RRGGBB`).
- **Criar nova carta:** Para criar uma regra de casa (ex: Carta "Pula a Vez"), basta adicionar um novo bloco na lista de `cards`:
  `{ "id": "pula_vez", "label": "Pula a\nVez", "count": 2, "color": "#112233" }`

Após fazer qualquer alteração no `.json`, salve o arquivo e rode novamente o `uv run make_cards.py` para gerar o PDF atualizado.
