# Implementation Plan: A tela do sorteio como a jornada de quem o conduz

**Branch**: `claude/142-jornada-do-sorteio-d8b95f` | **Date**: 2026-11-10 | **Spec**: [spec.md](spec.md)

## Summary

A view `sorteio` passa a ler o andamento da `127` para o Perfil do marco e entrega ao template, além
do contexto de hoje, a **jornada**: os quatro passos, cada um com o conceito do Centro
(`conceitos.py`) e as células da derivação — por lista, ou do marco na semente. Um módulo de
apresentação novo, `interface/jornada_do_sorteio.py`, só agrupa: lê as células, conta, ordena por
urgência e lê as posições do ato gravado. `sorteio.html` é reescrito em quatro seções, na ordem dos
passos; os formulários de ato mudam de lugar, nunca de condição. Em `andamento.py`, uma linha muda: a
célula do sorteio aponta para a âncora da execução da lista (`sorteio-<lista>`), e a juntada dela,
para a seção da execução.

## Technical Context

**Language/Version**: Python 3.12, Django 5 (monólito)
**Primary Dependencies**: as de hoje; nenhuma nova
**Storage**: PostgreSQL; **nenhuma migration**
**Testing**: pytest contra PostgreSQL (`make test-pg`); Playwright para as capturas e a medição
**Target Platform**: a gestão (`/gestao/`), sob a CSP da `091`/`092`
**Constraints**: sem script nem estilo no template; classe nova com regra na folha; os guardiões de
vocabulário (recorte, faixa e geração definidos no primeiro uso), de acessibilidade, de estáticos e de
citação
**Performance**: uma derivação do Perfil a mais por abertura da tela (D-001 da spec); o "Próximo nesta
lista" reaproveita a mesma leitura e deixa de fazer a dele

## Constitution Check

- **Publicação e ato imutáveis**: nenhum ato muda; a tela lê o ato de ordenação já gravado.
- **Nada é excluído**: nada é gravado nem apagado.
- **Negar por padrão**: a porta da tela é a de hoje (`_edital_para_classificar`); os formulários só
  aparecem sob `pode_emitir`, como hoje (FR-4903). A jornada não autoriza nada.
- **Uma regra, um lugar**: a situação vem de `andamento.py`; os nomes, de `conceitos.py`; o template
  não decide situação.
- **Rastreabilidade**: cada FR, SC e UX tem linha em `rastreabilidade.md`.

Sem violação. Reavaliado depois do desenho: idem.

## O desenho

### 1. `interface/jornada_do_sorteio.py` (novo, puro na maior parte)

- `Passo`: `chave`, `numero`, `simples`, `termo`, `curta`, `porque`, `ancora`, `do_marco` (bool),
  `listas` (`[(rótulo, Celula)]`), `celula` (a do marco), `contagem` (`"1 de 2 listas fixadas"`),
  `situacao` (a mais urgente, D-003), `agora` (bool).
- `da_tela(andamento, marco_id, recortes, *, conduz)` → `[Passo]` ou `None` sem derivação. Procura o
  Perfil cujos pontos têm o marco; lê as células `RELACAO`, `SEMENTE`, `SORTEIO` e `RESULTADO` por
  lista, na ordem dos recortes da tela. O passo 4 é leitura: a situação por lista é a da célula do
  sorteio (feito → a ordem existe), e a divulgação vem de `Celula.divulgado` da célula do resultado.
- `URGENCIA`: `OBSOLETO`, `PENDENTE`, `IMPEDIDO`, `AGUARDA`, `DEPOIS`, `FEITO`, `NAO_SE_APLICA`.
- `agora`: o primeiro passo, na ordem, com célula em `A_PRATICAR` — só para quem conduz.
- `ordem_gravada(sorteio)` → `[{posicao, numero, nome, protocolo}]`, das `PosicaoNaOrdem` do ato do
  sorteio, com o número público da relação daquele sorteio; quem ficou sem posição vem depois, com o
  motivo.
- O texto do passo 4 ("Consultar a ordem sorteada") e as frases de ligação entre os passos moram aqui,
  e não em `conceitos.py`: são da tela, e o Centro não os usa (`conceitos.py` não muda).

### 2. `interface/andamento.py` (uma mudança)

- `ancora_do_sorteio(lista)` → `sorteio-<lista|ampla>`; `_SECAO_DAS_ANCORAS["sorteio-"] =
  "titulo-execucao"`; em `_sorteio`, `url_do_sorteio(lista)` passado a `situacao_do_sorteio`. As
  âncoras da relação e da semente não mudam.

### 3. `interface/views.py` — a view `sorteio`

- Lê `andamento.do_edital(edital, ator, perfis=[perfil_id])` uma vez; passa `jornada` e, por recorte,
  `ordem` (só dos sorteados) ao template; `_proximo_nesta_lista` ganha o parâmetro `atual`, para
  reaproveitar a leitura.
- Nada muda nos comandos nem nas outras views.

### 4. `sorteio.html` e `telas/sorteio.css`

```
h1 Sorteio — <marco> · contexto (Perfil · Edital · N listas: A, B)
[termos desta tela]  [erro | sucesso | Próximo nesta lista]  [frase de quem conduz]
nav "Os passos do sorteio" — ol de 4 cartões: número, nome, (no GPS: …), situação + contagem,
                              listas com sinal; "Agora" no passo da vez; link para a seção
[método ausente — fora de tudo]
section #titulo-recortes  1. Fixar os participantes — o que é, por quê, depois; avisos do marco;
        article.recorte #recorte-<lista>: situação; conferência (antes) ou registro (depois);
        tabela (aberta antes, recolhida depois); diagnóstico da 102; fixar | suceder
section #titulo-ocorrencia 2. Obter a semente pública — vale para as N listas; ocorrência; observar;
        descartadas; recusas; details "Método declarado no Edital" (inteiro, Conferir na Caixa)
section #titulo-execucao  3. Realizar o sorteio — div.execucao #sorteio-<lista>: situação/razão;
        botão de hoje; registro do ato; details "Anular este sorteio"
section #titulo-resultado 4. Consultar a ordem sorteada — o que é cada coisa (relação, ordem,
        classificação divulgada, corte); por lista sorteada: divulgação, details da ordem,
        verificar, publicar a classificação, corte
section #titulo-historico-excedente (122), como hoje
```

As classes de situação são as do Centro (`situacao-do-andamento s-<situação>`, de `andamento.css`),
carregada também por esta tela; as novas (`passos-do-sorteio`, `passo`, `passo-agora`,
`conferencia-do-ato`, `ordem-sorteada`, …) ganham regra em `sorteio.css`.

### 5. Os testes

- Unidade: `tests/unit/interface/test_jornada_do_sorteio.py` — agrupamento, contagem, urgência,
  "agora", sem derivação.
- Integração: `tests/interface/test_jornada_do_sorteio.py` — os dez cenários da validação sobre o
  `certame_de_sorteio` e o `certame_com_ac`, contra PostgreSQL; a coerência com o Centro (SC-1541); os
  formulários antes e depois (SC-1542).
- Os existentes que liam a prosa antiga são ajustados para ler o controle (o formulário), e não o
  texto: `test_tela_do_sorteio.py` (o "Realizar o sorteio" virou nome de passo) e o que mais a suíte
  acusar. `test_chegada_e_volta_nos_cenarios.py` continua valendo para a relação.

## Achados registrados, fora do escopo

- **A conferência em dois passos do congelamento** (M-12): com resumo do universo conferido e recusa
  se ele mudar até o clique, como a `140`. Pede rota, resumo e recusa novos; a tela já mostra a
  lista e a numeração antes do botão (D-005 da spec). Para decisão do usuário.
- **A frase do conceito da relação** em `conceitos.py` ("depois dela, a relação é recusada") não
  corresponde ao comportamento com a fonte que publica a hora (F-1 do estudo: o congelamento é aceito;
  o sorteio é que é recusado). A tela da 142 não a usa. Corrigi-la toca o Centro e a decisão sobre a
  semente; fica registrada.

## Maquete e comparação

A maquete é o próprio template, renderizado pelo servidor sobre o banco descartável `ps142_dev`
(C06 e C07 da `134`), nos estados da validação. O roteiro `capturas/capturar.py` pratica os atos e
captura o antes (na `main`) e o depois (nesta branch) a partir da mesma cópia do banco.

## Project Structure

```text
backend/processo_seletivo/interface/
├── jornada_do_sorteio.py          # novo
├── andamento.py                   # a âncora da célula do sorteio
├── views.py                       # a view `sorteio` e `_proximo_nesta_lista`
├── templates/interface/sorteio.html
└── static/interface/telas/sorteio.css
backend/tests/
├── unit/interface/test_jornada_do_sorteio.py
└── interface/test_jornada_do_sorteio.py
specs/142-jornada-do-sorteio/
├── spec.md · plan.md · research.md · data-model.md · contracts/tela-do-sorteio.md
├── quickstart.md · tasks.md · rastreabilidade.md · verificacao.md
└── capturas/                      # antes-*.png, depois-*.png, capturar.py
```
