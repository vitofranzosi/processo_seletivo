# Modelo de dados: o piloto do design system

*Nada aqui é tabela do produto. São as estruturas do instrumento do piloto: o catálogo, a
fotografia, o inventário, a comparação e o registro da validação. Moram em arquivo, fora do banco.*

## Estado do catálogo

Um item do catálogo de D-004, em `tests/navegador/piloto/estados.py`.

| Campo | O que é | Regra |
|---|---|---|
| `codigo` | `C-01` a `C-12`, `O-01` a `O-18`, `R-01` a `R-12`, `K-01` a `K-09`, `L-01` a `L-12` | único; 63 ao todo |
| `tela` | `confirmacao`, `ocupacao`, `conferencia-acrescimo`, `conferencia-nao-preenchida`, `lista` | um dos cinco templates |
| `papeis` | a identidade e os papéis de quem abre a tela, e o vínculo de comissão quando houver | o mesmo antes e depois |
| `montar` | a função que monta o estado pelas fixtures e devolve o endereço | um estado por caso |
| `gesto` | para R-NN, K-05 e K-09: o botão a clicar na tela anterior, e os campos a preencher | só nos retornos e recusas |
| `prova` | o trecho literal que só aparece no estado pedido | a jornada falha sem ele (FR-7718) |
| `acao_principal` | o rótulo da ação principal, quando o estado tem uma | serve à dobra (FR-7731) |

## Fotografia

Por estado e largura, numa pasta de trabalho: `<pasta>/<codigo>/<largura>.png` e
`<pasta>/<codigo>/<largura>.json`. A pasta tem um `fotografia.json` com o commit, a data, as
larguras e a versão do Chromium.

## Inventário de conteúdo

O formato está em [contracts/inventario.md](contracts/inventario.md). Em resumo: `blocos`,
`quantidades`, `associacoes`, `acoes`, `ordem_documento`, `ordem_visual`, `linhas`, `dobra`,
`violacoes_de_csp`. Todo bloco tem um identificador estável dentro do inventário, que é o resumo do
texto normalizado mais o número da ocorrência, para que dois blocos de mesmo texto (o "Publicadas" de
cada recorte) não se confundam.

**Normalização** antes de comparar: UUID, data e hora de registro, chaves de idempotência, leitura
assinada e token de CSRF.

## Sequência declarada

Em `doc/auditoria-design-system-2026-11-14/piloto/scripts/sequencias.toml`, uma entrada por
sequência da spec (T-S1 a L-S5):

| Campo | O que é |
|---|---|
| `id` | o da spec |
| `telas` | onde vale |
| `antes` | o trecho que identifica o primeiro termo (ou a lista de trechos, quando é um grupo) |
| `depois` | o trecho do segundo termo |
| `escopo` | `pagina` ou o item da estrutura (o recorte, o Processo), quando a sequência vale dentro de cada um |

A sequência vale **onde os dois termos existem** no estado. Termo ausente não aprova nem reprova:
fica registrado como "não se aplica".

## Comparação

Por estado e largura, o resultado de `comparar.py`:

| Campo | O que é |
|---|---|
| `faltaram`, `sobraram` | blocos de texto presentes só antes, ou só depois |
| `quantidades` | número com rótulo diferente, ausente ou novo |
| `associacoes` | bloco que mudou de item da estrutura |
| `acoes` | destino, método ou campo diferente |
| `sequencias` | por id: `aprovada`, `invertida no documento`, `invertida na tela` ou `não se aplica` |
| `ordem_fora_das_sequencias` | os blocos que mudaram de posição relativa, para o registro (FR-7715) |
| `linhas_acima_de_80` | os blocos de prosa com linha acima de 80 caracteres (FR-7730) |
| `dobra` | se a ação principal está acima da dobra a 1280 × 800 |

O estado **passa** quando as quatro primeiras listas estão vazias, nenhuma sequência está invertida,
nenhuma linha passa de 80 e, havendo ação principal, ela está acima da dobra ou anunciada.

## Registro da validação

Em `specs/172-piloto-do-design-system/validacao.md`, uma tabela por pessoa:

| Campo | O que é |
|---|---|
| `pessoa` | código (P1, P2, P3), nunca nome (FR-7739) |
| `ordem` | `antiga→nova` ou `nova→antiga` |
| `tarefa` | V1 a V6 |
| `versao` | antiga ou nova |
| `registro` | o Edital ou o Processo usado (o original ou a duplicata) |
| `resposta` | o que a pessoa disse, com as palavras dela |
| `acerto` | certo, parcial ou errado, pelo gabarito |
| `impedimento_notado` | nas tarefas de prevenção: se notou antes de procurar o botão |
| `hesitacao` | onde parou, voltou ou rolou à procura |
| `tempo` | diagnóstico, sem valor de aprovação |
| `le_e_pula` | o que disse que lê e o que pula, perguntado no fim |
