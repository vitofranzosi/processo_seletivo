# Implementation Plan: Os mesmos recortes no sorteio, na divulgação, na ocupação e na Supervisão

**Branch**: `claude/classification-links-review-bade10` | **Date**: 2026-11-05 | **Spec**: [spec.md](spec.md)

**Input**: a spec desta pasta, com as decisões do usuário de 05/11/2026 (1ª a 13ª) e D-001 a D-007
aprovadas.

## Summary

O sorteio deixa de ter derivação própria de recortes, e a Modalidade que o Perfil aponta como a ampla
deixa de produzir relação, sorteio e ato. Seis superfícies passam a contar pela mesma derivação: tela do
sorteio, condução do marco, resumo da página do Edital, ocupação, Supervisão e relatório do Edital.
Congelar, sortear e divulgar recusam o recorte excedente no comando, com uma frase só. O acervo
excedente fica numa seção de histórico, com a frase da origem dele: nascido excedente ou tornado
excedente por Retificação. Uma Retificação que devolve o recorte à operação mostra o ato antigo como
obsoleto, com causa nomeada. A página do Edital troca os N links por ato por um caminho de divulgação
por marco, e a célula de divulgação do quadro passa a levar à prévia.

O plano foi escrito depois de ler o código (`research.md`, R-1 a R-11). A pesquisa corrigiu a spec em
dois pontos, as duas correções já aplicadas nela: a FR-3900 (a emissão computada normaliza, e não
recusa) e a FR-3916 (o relatório do Edital é a sexta superfície).

## Technical Context

**Language/Version**: Python 3.13, Django (monólito do repositório)

**Primary Dependencies**: as do projeto; nenhuma nova

**Storage**: PostgreSQL. **Sem migration**, sem tabela, sem coluna (FR-3914)

**Testing**: pytest contra PostgreSQL (`make test-pg`), com o grupo `navegador` para a jornada da
SC-1165

**Target Platform**: o servidor da instalação; a gestão em navegador

**Project Type**: aplicação web, renderizada no servidor

**Performance Goals**: a página do Edital **perde** uma consulta (R-3); a Supervisão não ganha nenhuma
(R-8); a tela do sorteio ganha a leitura do histórico, uma consulta por espécie, medida e fixada no
teste de orçamento dela

**Constraints**: append-only (nada se reescreve); CSP sem `inline` (as frases vão em template, e o
estilo, se houver, em folha); vocabulário pela lista literal da varredura

**Scale/Scope**: onze lugares de código (R-1), três comandos, sete casos temporais (R-11)

## Constitution Check

| Princípio | Leitura | Situação |
|---|---|---|
| I — linguagem ubíqua | "recorte", "ampla concorrência", "Modalidade apontada como a ampla" são os termos que o código e os Editais já usam; "excedente" aparece só na gestão, e a frase diz o que ele é | ✅ |
| II — imutabilidade e temporalidade | nenhum registro se reescreve, sucede ou anula (FR-3902); a vigente decide a operação, e a versão de origem explica o registro (FR-3911); Retificação não reabilita ato (FR-3912) | ✅ |
| III — negar por padrão; auditoria | a recusa mora no comando, sob a trava (R-4); nenhum caminho novo é oferecido a quem não o alcança; a porta da condução não muda (R-2) | ✅ |
| III — LGPD | nenhum dado pessoal novo; o levantamento imprime contagens e identificadores, nunca nomes (quickstart, passo 0) | ✅ |
| IV — regra explícita, consistência operacional | uma derivação para seis superfícies (FR-3893, FR-3916); uma frase de recusa (D-003); o papel é pergunta, e não marca (D-002) | ✅ |
| V — simplicidade e rastreabilidade | sem tabela, rota ou tela nova; a causa de obsolescência entra no mecanismo de divergências que existe (R-6) | ✅ |
| VI — jornada demonstrável | a SC-1165 é percorrida no navegador, pela gestão, com o Publicador puro e a presidência (quickstart, passo 2) | ✅ |

Nenhuma entrada em *Complexity Tracking*. Reavaliado depois do desenho: sem mudança.

## Project Structure

### Documentation (this feature)

```text
specs/122-recortes-alinhados-no-sorteio/
├── spec.md
├── plan.md               # este arquivo
├── research.md           # R-1 a R-11
├── data-model.md         # conceitos derivados; nenhuma tabela
├── quickstart.md         # passo 0 (levantamento), suíte, jornada, matriz
├── contracts/
│   └── recorte-excedente.md
├── checklists/
│   └── requirements.md
└── tasks.md              # /speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/domain/recortes.py              # papel_do_recorte, exigir_recorte_operacional, frases
├── sorteios/application/
│   ├── previa.py                           # recortes operacionais × registros excedentes
│   ├── relacao.py                          # recusa ao congelar
│   ├── sorteio.py                          # recusa ao sortear
│   └── selectors.py                        # marcos_sorteados_em_todos_os_recortes (herda)
├── classificacao/application/selectors.py  # divergência papel_do_recorte (dois ramos)
├── divulgacao/application/publicar.py      # recusa ao divulgar
└── interface/
    ├── views.py                            # _destinos_do_marco: um caminho por marco
    ├── conducao_do_marco.py                # célula de divulgação → prévia
    ├── supervisao.py                       # listas_do_marco sem o ramo do sorteio
    ├── relatorio_do_edital.py              # linhas pelos recortes operacionais
    ├── previa_do_sorteio.py                # frase da Modalidade apontada
    ├── acoes.py                            # ações do ato excedente
    └── templates/interface/
        ├── sorteio.html                    # seção de histórico; sem botão no excedente
        ├── marco.html                      # âncora #divulgacao
        ├── previa_de_publicacao.html       # frase no lugar do botão
        ├── ato_ordenacao.html              # tela do ato: frase, sem publicar
        └── publicacoes_do_marco.html       # marca fora da operação

backend/tests/
├── unit/editais/test_papel_do_recorte.py
├── integration/sorteios/test_recorte_excedente_recusado.py
├── integration/classificacao/test_recortes_alinhados_temporal.py   # T1–T7
├── interface/test_recortes_alinhados.py    # superfícies, portas, Publicador puro
└── navegador/test_jornada_dos_recortes.py  # SC-1165
```

**Structure Decision**: o monólito existente. As funções de domínio novas ficam ao lado de
`recortes_do_perfil` e `normalizar_recorte`, que já são a derivação única da `034`. Os nomes dos
templates se confirmam por `ls` na implementação.

## Design

### 1. O papel do recorte, num lugar só (FR-3893, FR-3894, FR-3911; R-5)

`editais/domain/recortes.py` ganha:

- `papel_do_recorte(conteudo, *, perfil_id, lista_id)`, que devolve `OPERACIONAL`, `EXCEDENTE` ou
  `AUSENTE`;
- `exigir_recorte_operacional(conteudo, *, perfil_id, lista_id)`, que levanta a recusa do contrato §1;
- `origem_do_registro(versoes, *, perfil_id, lista_id, versao_do_registro)`, que devolve `NASCIDO` ou
  `TORNADO` e, para `TORNADO`, a versão que o tornou. As `versoes` do Edital são lidas uma vez por
  quem chama.

`recortes_do_perfil` não muda. As três funções novas se definem por ela: `OPERACIONAL` é estar na lista
dela.

### 2. O sorteio (FR-3895, FR-3896; R-1 b, c, k)

`sorteios/application/previa.py`, `recortes_do_marco`, passa a montar `listas` a partir de
`recortes_do_perfil`, mantendo o rótulo da ampla que a tela usa hoje (*"Todos os inscritos do recorte
de vaga…"*). Ao lado, ele devolve `registros_excedentes`: relações, sorteios, atos e publicações do
marco cujo papel vigente é `EXCEDENTE`, com a origem (§1), em uma consulta por espécie.
`marcos_sorteados_em_todos_os_recortes` herda os recortes sem mudança de código. A frase da
`previa_do_sorteio.py` passa a dizer que a Modalidade não tem sorteio próprio.

### 3. As recusas (FR-3897 a FR-3900; R-4)

Uma chamada a `exigir_recorte_operacional` em cada comando:

- `publicar_relacao`: logo depois de `effective_version` dentro da trava, antes de `exigir_metodo`. A
  conferência da Caixa, que roda antes da trava (116), não é recusada por isso. Ela é de rede e não
  grava, e a recusa sob a trava é a que vale.
- `constituir_sorteio`: depois de ler a relação, sobre a versão vigente, antes de
  `_recusar_o_que_nao_pode_sortear`.
- `publicar_resultado`: depois de ler o ato, sobre a versão vigente.

A emissão computada não muda (FR-3900).

### 4. As portas (FR-3901, FR-3904; contrato §2)

- **Tela do sorteio**: os recortes vêm de §2; o registro excedente fica na seção de histórico, sem
  botão.
- **Tela do ato** (`acoes.py`): para ato de papel vigente `EXCEDENTE`, nenhuma ação de publicar; a
  frase da origem no lugar.
- **Prévia de publicação**: a mesma frase no lugar do botão; o POST cai na recusa do comando.
- **Resultados divulgados**: cada linha de publicação excedente traz a marca e a frase.
- **Supervisão**: §6.
- **Página do Edital**: §5.

### 5. A página do Edital e o quadro (FR-3906 a FR-3908; R-2, R-3)

- `_marcos_publicados` deixa de chamar `atos_vigentes_por_marco`. `_destinos_do_marco` recebe
  `tem_ordem = resumo["ordem"] > 0` e, se o ator divulga e há ordem, acrescenta **um** destino
  *divulgar o resultado* para `interface:marco` + `#divulgacao`.
- `marco.html` ganha `id="divulgacao"` na parte do quadro e dos gestos de divulgação.
- `_celula_da_publicacao` aponta para a prévia do ato quando o estado é *falta* ou *obsoleto* e o ator
  divulga (contrato §5).

### 6. A Supervisão (FR-3909, FR-3910; R-8, D-007)

`listas_do_marco` perde o ramo `sorteia` e devolve os recortes de `recortes_do_perfil` para todo marco.
A docstring troca a citação da decisão de escopo da `034` por esta feature.

### 7. A obsolescência por papel (FR-3912, FR-3913; R-6, D-004)

`_divergencias_do_sorteio` e o ramo computado de `estado_do_marco` acrescentam a divergência
`papel_do_recorte` quando o papel na versão do ato difere do papel na vigente e o vigente é
`OPERACIONAL`. Com isso, `aferir` (a publicabilidade) recusa a divulgação, e a condução mostra
*obsoleto*. O caminho seguinte é a sucessão que já existe.

### 8. O relatório do Edital (FR-3916; R-7)

As linhas de lista de cada marco vêm de `recortes_do_perfil`. A publicação excedente já feita entra
numa linha própria, com a marca *fora da operação atual*, fora de `definitivo_em_todas`. O ato
excedente não divulgado não aparece.

## Validação planejada

### Por camada

| Camada | O que prova | Requisitos |
|---|---|---|
| unidade: `papel_do_recorte`, `origem_do_registro` | os três papéis; nascido e tornado; a Retificação nomeada; a identificação pelo apontamento e não pelo texto | FR-3894, FR-3911 |
| integração: recusas | os três comandos recusam com o código e não gravam; o pedido repetido devolve o anterior; a emissão computada normaliza | FR-3897 a FR-3900, SC-1169 |
| integração: matriz temporal | T1 a T7 de R-11 | FR-3911 a FR-3913, SC-1171 |
| interface: superfícies | a mesma contagem nas seis superfícies; a seção de histórico; as quatro portas sem botão; a frase por origem | FR-3893, FR-3895, FR-3901 a FR-3904, FR-3916, SC-1166 |
| interface: Publicador puro | página do Edital → quadro → prévia de cada recorte; marco sem ato sem caminho | FR-3906 a FR-3908, SC-1167 |
| interface: Supervisão | zero sinal de registro excedente; o sinal do recorte operacional continua | FR-3909, FR-3910, SC-1168 |
| público | as páginas de verificação do acervo, iguais byte a byte depois de normalizar os identificadores de sessão | FR-3905, SC-1170 |
| navegador | a jornada da SC-1165 | SC-1165 |

Cada caso-limite da spec ganha uma linha própria na matriz de rastreabilidade.

### Antes de implementar

1. **O levantamento** (quickstart, passo 0), por quem tem acesso à instalação. Com publicação
   excedente, os números vão ao usuário antes de seguir.
2. **A lista dos testes que mudam de expectativa** (R-9), com `grep`, para que a mudança de cada um
   seja deliberada e esteja descrita no commit.

## Riscos

| Risco | Mitigação |
|---|---|
| O levantamento não ser feito antes, e a implementação esconder do gestor uma publicação excedente que o candidato vê | o passo 0 é a primeira tarefa e bloqueia as tarefas de tela; sem acesso à VM, a tarefa fica aberta e é dita no PR |
| A tela do sorteio, com a seção de histórico, estourar o orçamento de consulta | uma consulta por espécie; medido e fixado no teste da tela |
| Um teste antigo prender o comportamento do bloco da Modalidade apontada e for "corrigido" para passar | R-9: a lista é feita antes, e cada mudança de expectativa cita esta spec |
| `candidato_a_obsoleto` deixar de admitir o ato de papel mudado | ele admite toda versão diferente da vigente, e a Retificação sempre cria versão; T2 e T3 o provam |
| O vocabulário das frases novas escapar da varredura | as telas entram na lista literal (R-9) |

## Complexity Tracking

Nenhuma violação a justificar.
