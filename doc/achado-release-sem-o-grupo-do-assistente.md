# Achado — a release de produção não traz a biblioteca do tokenizer

Encontrado em 14/10/2026, ao escrever a §10.4 do guia de implantação (`073`).

> **Não vira escopo por estar escrito aqui.** O que se registra é uma lacuna entre o guia de
> implantação e o piloto do assistente, o que ela custa, e as correções possíveis. A correção é
> decisão explícita do usuário, e não define o próximo incremento.

## O que se observou

**O script que constrói a release instala só as dependências base.** O `ps-construir` do guia
(§8.3) roda `uv sync --locked --python 3.13`, sem grupo opcional. A biblioteca `tokenizers` está no
grupo `assistente` do `backend/pyproject.toml`, e não entra.

**Sem ela, o assistente não chama o modelo.** A aplicação conta os tokens antes de cada pergunta, e
sem a biblioteca, ou sem o `tokenizer.json` no caminho configurado, toda pergunta termina em
`SEM_TOKENIZER` ("falta o tokenizer do modelo"), sem chamada ao serviço
(`backend/processo_seletivo/duvidas/infrastructure/tokens.py`). A verificação do serviço acusa o
mesmo, como divergência "sem tokenizer".

**Hoje não há efeito.** O piloto do assistente roda na máquina da equipe, onde o
`uv sync --extra assistente` está no quickstart da `071`. E produção herda o padrão
`ASSISTENTE_PILOTO=false`. A lacuna só morde no dia em que alguém ligar o piloto numa máquina
construída pelo guia.

## O que a 073 já fez, e só isso

A §10.4 do guia, no passo 1, diz que a release precisa de `--extra assistente` e do
`tokenizer.json`. A tabela de falhas tem a linha "sem tokenizer". **O `ps-construir` não foi
alterado**: mudar o que toda release instala não estava no recorte, e é a decisão abaixo.

## As correções possíveis

| Opção | O que muda | Custo |
|---|---|---|
| **A — sempre com o grupo** | o `ps-construir` passa a `uv sync --locked --extra assistente` | toda release leva a `tokenizers` (binária, com dependências próprias), mesmo sem o piloto ligado. É a menor mudança, só no guia |
| **B — com o grupo, por escolha** | o `ps-construir` lê uma variável, por exemplo de `/etc/processoseletivo/`, e acrescenta o grupo quando ela pede | uma variável a mais no guia, e duas formas de release |
| **C — nada além do aviso** | continua o passo 1 da §10.4 | quem ligar o piloto precisa ler o passo 1. É o estado atual |

Em qualquer das três, **o `tokenizer.json` continua sendo arquivo de implantação**, fora da
release: ele vem do repositório do modelo, e não do projeto.

## O que a decisão precisa responder

- O piloto do assistente vai rodar numa máquina construída pelo guia, ou só na máquina da equipe?
  O relatório da L4 da `071` é que diz.
- Se for rodar, quem mantém o `tokenizer.json` do modelo em produção, e como ele é trocado quando o
  modelo muda?
