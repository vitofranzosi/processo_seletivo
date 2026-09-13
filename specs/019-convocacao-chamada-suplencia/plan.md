# Implementation Plan: Convocação, Chamada e Suplência

**Feature:** `019` · **Spec:** [spec.md](spec.md) · **Criado:** 2026-09-12
**Base medida:** `34b5b13` — a `main` com a `016` e o #107 integrados, mais os dois commits desta
sessão. Suíte em **5082 passando e 2 pulados**, `SCHEMA_VERSION = 14`, provisionamento `26 de 26`.

## Summary

A feature pratica o ato que alcança a pessoa: convoca quem a ordem indica para a vaga que a `016`
apurou como faltante, registra o que ela respondeu, chama o suplente quando a vaga vaga, e conduz os
quatro desfechos que os Editais nomeiam — regularização, reclassificação, não atendimento e
cancelamento por inércia.

**Seis decisões do usuário governam o plano** (`D-006` a `D-011` da spec), e a última reorganizou
tudo: o `$speckit-plan` anterior achou que a exclusão da `D-006` era **inócua** — num recorte de 40
vagas com faixa de 70 e 67 habilitadas, o `min` do cálculo satura e só a **28ª** desistência move o
número (§1.0 da spec, medido). A `D-011` conserta a definição de *ocupada* e acrescenta a inclusão.

**Três features entregues são tocadas, e isso é o custo real desta:** a `016` passa a contar
titulares iniciais e ganha porta de efeitos; a `018` ganha origem de sucessor que não é recurso; a
`010` tem a `FR-084` revisada por escrito. Nenhuma delas é efeito colateral — cada uma é fase
própria abaixo.

## Technical Context

**Linguagem/versão:** Python 3.13 · Django 5.2 LTS · DRF
**Persistência:** PostgreSQL, e **só** ele para as garantias desta feature — gatilho append-only e
constraint parcial com `NULL` no recorte
**Testes:** pytest, `make test-pg`
**Alvo:** monólito modular, `backend/processo_seletivo/`
**Escala de referência:** 1.000 participantes por recorte; a tela do recorte abre em < 3 s e o custo
é do conjunto, não uma consulta por convocação (`SC-090`)

### O que a feature lê, e de onde

| Entrada | Origem | Leitura |
|---|---|---|
| a ordem do recorte | `AtoDeOrdenacao` vigente, recorte `(perfil_id, marco_id, lista_id)` | recusa se não vigente |
| quem progrediu, e o excedente | `Corte` vigente da geração, `classificacao.domain.faixa` | a faixa é `alvo + excedente`; o excedente é **suplente** |
| quantas vagas faltam | apuração vigente da `016` | recusa sobre apuração obsoleta ou ausente |
| quem está habilitado | `ResultadoEtapa` vigente da Etapa governada | é o que a `016` já lê para contar |
| a forma de comunicar | campo normativo novo no Perfil publicado, **degrau 15** | declarado; ausência não tem padrão |
| feriado, dia útil, expediente | — | **não existe neste sistema**; o vencimento é informado (`D-011`) |

### Onde a feature mora, e a porta que não inverte a seta

**Módulo novo, `convocacao`.** A alternativa era pôr tudo em `ocupacao`, onde a apuração está, e ela
foi recusada pelo mesmo argumento que fez a `016` não morar em `classificacao`: o nome do módulo
ficaria falso. `ocupacao` **conta**; convocar é alcançar pessoa.

```
convocacao ──lê──▶ classificacao (AtoDeOrdenacao, Corte, faixa)
convocacao ──lê──▶ ocupacao      (apuração vigente: déficit e titulares)
convocacao ──lê──▶ resultados    (habilitação vigente)
convocacao ──chama──▶ ocupacao.application.efeitos  (exclusão e inclusão)
convocacao ──chama──▶ resultados/recursos           (o sucessor da regularização)

ocupacao ──▶ convocacao   NUNCA
```

**A porta é uma tabela append-only que mora em `ocupacao`.** `EfeitoDeOcupacao` guarda
`(perfil_id, marco_id, lista_id, inscricao_id, especie, fundamento, ato_de_origem_id, rotulo)`, e a
`019` a escreve chamando uma função de aplicação que a `016` expõe. Duas consequências de desenho,
e as duas são deliberadas:

1. **`ato_de_origem_id` é UUID opaco, não FK.** Uma FK de `ocupacao` para uma tabela de `convocacao`
   inverteria a dependência **no grafo de migrations**, que é onde ela mais dói. É exatamente o que
   a `016` já faz com `perfil_id` e `marco_id`.
2. **A `016` não sabe o que é convocação.** Ela sabe que uma inscrição foi excluída ou incluída, com
   fundamento e proveniência. Quem dá sentido ao fundamento é quem o escreveu.

## Constitution Check

| Princípio | Como este plano o atende |
|---|---|
| **I** Linguagem ubíqua | `Convocacao`, `DesfechoDaConvocacao`, `AtestadoDeFatoExterno`, `ComunicacaoEmitida`, `reclassificacao`, `regularizacao`, `inercia` — vocabulário literal dos Editais (§1.1 da spec) |
| **II** Integridade normativa | a forma de comunicar é conteúdo publicado, com **degrau 15**, caminho de leitura das anteriores e entrada no catálogo de Retificação. Ausência ≠ padrão |
| **II** Imutabilidade | quatro tabelas append-only novas em `convocacao` e uma em `ocupacao`, com gatilho **e** privilégio ausente. Correção é sucessão (`FR-272`) |
| **II** Preservação | nenhuma apuração é reescrita: o efeito entra na **emissão seguinte** (`D-006`), e convocação praticada não se desfaz (`FR-282`, `FR-292a`) |
| **III** Auditoria | cada ato grava ator, estados, fundamento e correlação; `FR-294` exige proveniência de ordem, corte e apuração; `FR-296` exige trilha em linguagem humana |
| **III** Proteção de dados | a mensagem carrega o mínimo (`FR-290`), e o sistema não afirma entrega (`FR-288a`) |
| **IV** Regras explícitas | a forma de comunicar é declarada (`FR-287`); o vencimento é informado (`FR-269`); nenhum desfecho nasce do relógio (`FR-274`) |
| **V** Rastreabilidade | `rastreabilidade.md` na entrega; `FR-264`–`FR-296`, `SC-085`–`SC-094` e `UX-035`–`UX-039` citados em teste |
| **VI** Completude de jornada | o gate da §9 é percurso pela interface; a tela do recorte é a **fase 3**, e a área do candidato (`US6`) é fase própria — não sobra de fim de fila |

### Invariantes do domínio tocados

- **"Nada é excluído"** — desistência, cancelamento e reclassificação são atos motivados; nenhum
  apaga convocação, resultado ou apuração.
- **"Mudança futura NÃO PODE alterar Edital publicado"** — o degrau 15 escreve a ausência de
  declaração para todo Edital anterior, e ausência significa *"não declarou forma"*, não um padrão.
- **"Migrations aplicadas NÃO PODEM ser reescritas"** — quatro migrations novas em `convocacao`, uma
  em `ocupacao` (a porta), uma em `resultados` (a quinta linha legítima da origem). Nenhuma
reescrita.
- **"Negar por padrão"** — convocar, desfechar e atestar exigem permissão explícita e escopo.

### Gate: uma travessia justificada, nenhuma violação

Nenhum princípio exige justificativa. A `Complexity Tracking` registra as duas escolhas que
**adicionam** peso: o módulo novo e a alteração de três features entregues.

## Project Structure

### Documentation (this feature)

```text
specs/019-convocacao-chamada-suplencia/
├── spec.md
├── plan.md              ← este arquivo
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── convocacao.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── convocacao/                      ← módulo novo
│   ├── domain/
│   │   ├── nomes.py                 desfechos, espécies, códigos de recusa — **não** as formas de
│   │   │                             comunicar, que são vocabulário do publicado
│   │   ├── fila.py                  titulares, suplentes, quem é chamável — puro
│   │   └── prazo.py                 vencimento informado × envio — puro
│   ├── application/
│   │   ├── convocar.py              o ato, com as recusas de faixa e de apuração
│   │   ├── desfechar.py             os sete desfechos, e o que cada um faz na porta
│   │   ├── atestar.py               fato externo, com atestante
│   │   ├── comunicar.py             emissão, registro e falha
│   │   └── selectors.py             a leitura do recorte e o histórico
│   ├── models.py                    Convocacao, DesfechoDaConvocacao,
│   │                                ComunicacaoEmitida, AtestadoDeFatoExterno
│   └── migrations/
├── ocupacao/                        ← feature entregue, tocada
│   ├── domain/apuracao.py           titulares iniciais (D-011), exclusão e inclusão
│   ├── application/efeitos.py       ← a porta, nova
│   └── models.py                    EfeitoDeOcupacao, append-only
├── resultados/                      ← feature entregue, tocada
│   └── models.py                    a quinta linha legítima: origem REGULARIZACAO
├── publicacoes/                     ← degrau 15 e catálogo de Retificação
├── portal/                          ← a área do candidato (US6)
└── interface/
    ├── templates/interface/convocacao.html
    ├── templates/interface/convocacao_historico.html
    └── views.py

backend/tests/
├── unit/convocacao/                 fila, prazo, desfechos, append-only
├── unit/ocupacao/                   a contagem de titulares e a SC-093
├── integration/convocacao/          o ciclo do 77 e a suplência por lista
├── interface/                       as telas e a confirmação da UX-036
├── performance/test_convocacao.py   SC-090
└── test_vocabulario_da_convocacao.py  UX-035 e UX-039
```

**Structure Decision**: módulo novo `convocacao`, com a porta de efeitos morando em `ocupacao` —
é o que mantém a seta de dependência num sentido só.

## Ordem de execução

*A ordem é a da §8 da spec, com as fases de travessia postas onde elas bloqueiam. **O executável é
o [tasks.md](tasks.md)**, que agrupa estas dez fases em nove, com a comunicação dentro da US1 e a
revisão da `010` na fase bloqueante; onde divergirem, vale o `tasks.md`.*

| # | Fase | Por que aqui |
|---|---|---|
| 1 | **A contagem de titulares na `016`** | é a correção da §1.0, e sem ela todo o resto conta errado. Fase 1 porque a `SC-093` reprova qualquer coisa construída sobre a contagem antiga |
| 2 | **A porta de efeitos** — `EfeitoDeOcupacao`, migration, privilégio, função de aplicação | a exclusão e a inclusão precisam de destino antes de existir quem as produza |
| 3 | **A convocação como ato** — entidade, privilégio, emissão, recusas, auditoria | |
| 4 | **Os desfechos** — os sete, com o que cada um faz na porta | |
| 5 | **A tela do recorte** — US1 e US2; é o que substitui a planilha | |
| 6 | **A origem `REGULARIZACAO` na `018`** | a regularização é superação de Resultado (`D-008`), e a constraint precisa da quinta linha antes do ato |
| 7 | **A revisão escrita da `FR-084` da `010`** | precede qualquer envio individual; a própria regra manda |
| 8 | **A comunicação** — forma declarada, degrau 15, envio, registro, falha | |
| 9 | **A área do candidato** — US6, pelo canal do ator | |
| 10 | **O atestado de fato externo** — US5 | |

As fases 1 a 5 fecham o ciclo do 77/2026 e a `SC-085`. As fases 6 a 10 alcançam o 58, o 59 e o 69.

### As armadilhas que matam em silêncio

**A saturação volta se a contagem receber conjunto em vez de sequência.** `apurar` hoje recebe
`dentro_da_faixa` como conjunto, e titular inicial depende de **ordem**. Trocar a assinatura sem
trocar quem a chama produz um número plausível e errado — e plausível é o que faz passar. A `SC-093`
existe para isso: uma desistência, um a menos.

**O empate residual pode atravessar a fronteira do alvo, e a `014` não calcula essa fronteira.**
Ela trata o empate na última posição **da faixa** (alvo + excedente). Titular inicial é contado até
o
**alvo**, que é outra fronteira. Onde houver empate residual não julgado atravessando-a, a apuração
**recusa** determinar titulares, nomeando a causa — a mesma disciplina da `014`, que impede publicar
ordem com empate residual quando o Edital publicou alvo estrito. Detalhado na `research.md`.

**A fonte jurídica do sucessor é obrigatória em `resultados`, e a regularização não tem decisão
recursal.** `ck_resultado_origem` tem quatro linhas legítimas e a `decisao` é FK para
`recursos.DecisaoRecurso`. A quinta linha precisa de fonte própria — e afrouxar a constraint em vez
de estendê-la abriria sucessor sem fonte nenhuma, que é o que ela existe para barrar.

**Dois desfechos parecidos, e colapsá-los apaga norma.** *Não atendimento à convocação* e
*cancelamento de matrícula por inércia* têm atores, prazos e fundamentos diferentes (`D-011`). O
segundo depende de atestado de fato externo; o primeiro, do vencimento informado.

**O vocabulário tem três fronteiras agora, não duas.** A `016` não pode falar de convocação
(`UX-034`); a `019` não pode afirmar contagem de ocupação (`UX-035`); e nenhuma superfície desta
feature pode dizer *"recebido em"* (`UX-039`) nem *"direito à vaga"* (`FR-292c`). São quatro
varreduras, e é o que impede a spec de virar prosa.

### A travessia que a `D-011` obriga

Mexer em `ocupacao/domain/apuracao.py` é mexer em domínio entregue com teste que o prende. A ordem
é: primeiro estender a função pura com a definição nova e **manter** o teste antigo do cenário sem
desfecho (o número não muda onde não há desistência); depois trocar quem a chama; só então a porta.
Fazer o contrário deixa a suíte verde com a contagem errada por uma janela — e é a janela em que
alguém constrói a tela sobre ela.

## O que este plano deliberadamente não faz

- **Não modela vaga individual.** A `D-011` a recusa: há quantidade e conjunto de pessoas.
- **Não cria calendário de feriados nem contagem de dias úteis.** O vencimento é informado.
- **Não automatiza desfecho por decurso de prazo.** `D-003`, confirmada pelo usuário.
- **Não integra sistema acadêmico.** Matrícula, aqui, é desfecho registrado.
- **Não cria objeto recursal.** `D-010`.
- **Não reabre a fronteira da `014`.** Faixa e seleção continuam lá.

## Complexity Tracking

| Violação | Por que é necessária | Alternativa simples recusada porque |
|---|---|---|
| módulo novo `convocacao` | mantém a seta de dependência num sentido e o nome de cada módulo verdadeiro | pôr em `ocupacao` faria o módulo que **conta** também **chamar pessoas**, e a porta de efeitos perderia sentido |
| alterar três features entregues (`016`, `018`, `010`) | as três decisões do usuário exigem: contagem de titulares, origem de sucessor, e canal de mensagem | construir por fora produziria segunda contagem de ocupação, segundo caminho de habilitação e mensagem sem a revisão que a `FR-084` exige |
| tabela de efeitos em `ocupacao`, e não em `convocacao` | é o que evita a FK invertida no grafo de migrations | guardar os efeitos na `019` obrigaria `ocupacao` a importá-la para contar |
