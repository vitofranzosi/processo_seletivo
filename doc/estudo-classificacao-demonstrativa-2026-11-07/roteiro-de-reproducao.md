# Roteiro de reprodução — Edital 900/2026 (demonstrativo)

Como reconstruir, num banco isolado, o certame do
[estudo de caso](../estudo-classificacao-demonstrativa-2026-11-07.md), e como conferir que ele saiu igual.
Nada aqui toca o banco de desenvolvimento compartilhado nem envia e-mail para fora. O backend de
e-mail é o de console, e os avisos aos candidatos ficam desligados.

## O que está na pasta `reproducao/`

| Arquivo | Para quê |
|---|---|
| `elenco.py` | **A fonte única dos números**: 18 candidatos fictícios, modalidade, nascimento, Requisitos, Currículo, Prova e Entrevista; o recurso de C10; os motivos das ausências |
| `edital-900-publicado.json` | O conteúdo do Edital como foi publicado depois da configuração à mão: Perfil, Etapas, marcos, Cronograma, documentos |
| `reproduzir.py` | O certame inteiro, fase a fase, pelos **mesmos comandos** que as telas chamam, com o relógio no dia de cada ato |
| `conferir.py` | A mesma conta sem banco, com as funções puras do motor (`combinar`, `ordenar`, `faixa.calcular`). Serve para desenhar o caso e para conferir a execução |
| `servidor.py` | `runserver` com o relógio da aplicação posto num instante (`RELOGIO=2026-12-09T10:00`) |
| `capturar.py` | Capturas das telas com Playwright, a partir de um plano JSON |

## 1. Banco próprio

A partir de `backend/`, com o PostgreSQL local no ar (no macOS com Homebrew, `LC_ALL` exportado):

```bash
export LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development \
       DB_NAME=ps_estudo_classif DB_USER=$USER DB_RUNTIME_USER=$USER DB_RUNTIME_PASSWORD= \
       ARQUIVOS_CANDIDATOS_RAIZ=/tmp/ps-arquivos-estudo-classif AVISOS_AOS_CANDIDATOS=false
```

```bash
createdb ps_estudo_classif && uv run python manage.py migrate -v0 && uv run python manage.py semear_unidades
```

O superusuário faz as vezes das duas roles. As garantias append-only continuam valendo, porque são
gatilhos.

## 2. O certame inteiro, de uma vez

```bash
uv run python ../doc/estudo-classificacao-demonstrativa-2026-11-07/reproducao/reproduzir.py tudo
```

Leva menos de um minuto. As fases, na ordem, e o que cada uma deixa no banco:

| Fase | Datas | Resultado esperado |
|---|---|---|
| `f0` | 09/11/2026 | Processo PS-DEMO-CLASSIF-2027 e Edital 900/2026 publicados, com o conteúdo de `edital-900-publicado.json` |
| `f1` | 16–27/11 | 18 inscrições enviadas, cada uma com Diploma, Currículo e data de nascimento |
| `f2` | 28/11–01/12 | Comissão (demo.presidente, demo.avaliadora, demo.avaliador); Requisitos: 17 Deferidos, C05 Indeferida |
| `f3` | 02–08/12 | Currículo de 17; Ocorrência de C04; Prova de 16 (C03 e C14 eliminados) |
| `f4` | 09/12 | 3 ordens do marco 1 e 3 preliminares |
| `f5` | 10–13/12 | Recurso de C10, correção 68 → 76, ordem sucessora da ampla |
| `f5b` | 14/12 | 3 definitivas e 3 cortes do marco 1: 12 pessoas na Entrevista |
| `f6` | 15–21/12 | Ocorrência de C18; Entrevista de 11 (C15 eliminada); 3 ordens do marco 2 e preliminares |
| `f7` | 22–28/12 | Recurso de C07 indeferido; 3 definitivas |
| `f8` | 28–29/12 | 3 cortes do marco 2; apuração: ampla 4/4/4, PcD 1/1/1, PPI 1/1/1 |
| `f9` | 04–06/01/2027 | Convocações; conferência (C06 pendente e depois conforme); aceites; desistências de C02 e C13; reversão da vaga PcD; convocação de C09 e C08. Final: ampla 4 publicadas / 5 efetivas / 5 ocupadas; PcD 1/0/0; PPI 1/1/1 |

Cada fase também roda sozinha (`reproduzir.py f6`), desde que as anteriores tenham rodado. As
subdivisões `f4a`, `f4b`, `f5a`, `f5j`, `f5s` e `f9a`–`f9e` existem para parar no meio de uma fase e
praticar o gesto seguinte pela tela, como o estudo fez.

**Alternativa a `f0`.** O estudo configurou o Edital à mão, pela interface. Para refazer esse percurso,
siga o [diário](diario.md), itens C01–C12. Depois rode a partir de `f1`. Os identificadores serão outros,
então regenere `edital-900-publicado.json` com o conteúdo vigente antes de `f1`.

## 3. Conferir

Os números esperados, sem banco:

```bash
uv run python ../doc/estudo-classificacao-demonstrativa-2026-11-07/reproducao/conferir.py
```

O estudo comparou o banco do estudo com uma reprodução do zero (`ps_ec_repro`) por uma consulta que lista:

- as posições e notas dos atos vigentes;
- as apurações vigentes;
- as convocações.

As 51 linhas saíram **idênticas**.

## 4. Ver na tela

O servidor do estudo lê o instante do arquivo `reproducao/.relogio` (fora do controle de versão) e serve
na porta 8140. A entrada `estudo-classificacao` do `.claude/launch.json` já faz isso.

```bash
echo "2027-01-06T10:00" > ../doc/estudo-classificacao-demonstrativa-2026-11-07/reproducao/.relogio
```

Entre por `/gestao/identificar/demonstracao`. A comissão aparece no topo (demo.presidente,
demo.avaliador, demo.avaliadora); os papéis vêm abaixo.

**Armadilha do ambiente.** Com o relógio deslocado, a sessão da demonstração cai cerca de 30 segundos
depois de cada ato, ou quando o servidor reinicia. Entre de novo. Para automatizar, faça login e ato na
mesma requisição, como `capturar.py` faz.

Para ver um momento intermediário (a ordem obsoleta depois do recurso, por exemplo):

1. rode as fases até ali num banco à parte;
2. ponha o relógio no dia;
3. use a entrada `estudo-classificacao-fase` (porta 8141, banco `ps_ec_fase`, relógio em
   `reproducao/.relogio-fase`).

## 5. Capturas

Com o Playwright do checkout principal (`backend/.venv` de lá tem o Chromium):

```bash
PLANO=plano.json SAIDA=../capturas /caminho/do/checkout/backend/.venv/bin/python capturar.py
```

Para o portal do candidato, crie a sessão no banco com o relógio do dia (`SessionStore` com
`portal_identidade`), porque o código de acesso só chega pelo console. Passe `sessao:<chave>` como
`quem` no plano.
