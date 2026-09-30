# Modelo — 056 · Polish do assistente de composição

**Não há entidade de domínio nova nem alterada**, nenhuma migration e nenhum campo de formulário novo
ou renomeado. O que esta feature trata são elementos da tela; o contrato visual de cada um está em
[contracts/assistente.md](contracts/assistente.md).

## Elementos

| Elemento | Onde | O que muda |
|---|---|---|
| Stepper | `compor_base.html`, `ol.assistente` | disposição: grade de colunas iguais; número ao lado do nome |
| Cartão de item | `_evento`, `_etapa`, `_documento`, `_modalidade` | ações ao lado da legenda; legenda com categoria, posição e nome |
| Faixa do Evento | `_evento.html` | Tipo, Descrição, Início, Término; "Onde acontece" no fim |
| Seção do Conteúdo | `compor_conteudo.html` | largura de leitura; vazia com 2 linhas; gerada sem caixa |
| Linha da Revisão | `revisao.py`, `origens.py` | a linha rotulada carrega o rótulo; a apresentação vira `dl` |
| Campo de texto longo | `_perfil`, `_documento`, `retificacao.py` | `input` para `textarea`, mesmo `name` |

## A linha rotulada

`Rotulada(rotulo, valor)` é uma `str` cujo texto é `f"{rotulo}: {valor}"`, e que expõe `rotulo` e
`valor`. Invariantes:

- `str(Rotulada(r, v)) == f"{r}: {v}"` — a linha continua a mesma cadeia (FR-1034);
- `com_origem(Rotulada(r, v), o)` devolve `Rotulada(r, f"{v} ({o})")` quando há origem, e a própria
  linha quando não há;
- linha que não nasce por `Rotulada` não tem rótulo, e a apresentação não o procura nela (FR-1033).
