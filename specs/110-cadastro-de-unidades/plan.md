# Implementation Plan: Cadastro de unidades administrado pela aplicação

**Branch**: `claude/110-cadastro-de-unidades` | **Date**: 2026-10-31 | **Spec**: [spec.md](spec.md)

**Input**: a spec, com D-001 a D-019 no [research.md](research.md), a
[estratégia de migração e reversão](migracao.md) e a
[revisão arquitetural de 30/10](../../doc/revisao-arquitetural-multiunidade-2026-10-30.md).
**Aprovação**: o pedido de 31/10/2026 autoriza especificar e planejar; a revisão final do mesmo dia
reviu D-002, D-003 e D-017 e acrescentou D-018 e D-019. Nenhum dos dois autoriza implementar nem
fazer merge.

## Summary

O registro de Unidades passa a ser escrito pela aplicação, e não mais pelo arquivo. Quatro casos de
uso no `unidades` — registrar, alterar, desativar, reativar —, com conferência que não grava,
validação única no domínio (D-005), trava e versão conferida (D-007), e evento no escopo da unidade
com os nomes que a trilha da `108` já lê (D-008). Uma permissão nova, num papel institucional
próprio concedido só pela implantação (D-002). Cinco telas num módulo próprio da `interface`
(D-011), com prévia pelas linhas do compositor (D-010) e histórico pela tradução da `108` (D-009). O
comando de sincronização vira semente, que só se aplica a registro vazio, com o nome anterior como
apelido (D-001, D-003, D-004). Um par de gatilhos torna imutável o escopo de Processo e de Edital
(D-013). E um adaptador de homologação, só no código de teste, leva pessoas às telas antes do SSO
(D-017, D-018).

**Onde está o risco**: na troca da sincronização pela semente, porque ela está em três roteiros de
implantação e no `seed_demo`, e um erro ali impede subir o contêiner, deixa banco novo sem o Cefor
ou deixa um ambiente sem como cadastrar unidade. Por isso a troca entra **no mesmo PR** que as telas
e o papel (D-019), com teste que lê os roteiros e um apelido que não deixa um roteiro antigo
falhar.

## Verificação de dependência

Feita em 31/10/2026 antes de especificar, sobre a `main` em `77f35fd3` com os dois PRs abertos, e
**refeita na revisão final do mesmo dia, depois do merge dos dois**:

| Item | Estado | Consequência |
|---|---|---|
| `main` | `81ce6e94` (merge do #349) | base da implementação |
| #348 (`108`) | **integrado** em `cf048007`, com as correções da revisão de código (`c76dca30`) | `linhas(registros, *, nome_da_unidade)` sem mudança de assinatura; a trilha deixou de ser oferecida no escopo institucional — a ficha desta feature continua com a leitura própria (D-009) |
| #349 (`109`) | **integrado** em `81ce6e94`, depois de integrar a `108` | `Unidade.atendimento`, a validação em `sincronizacao.validar` e `identificacao.py` como descritos abaixo |
| integração das duas | `25460040` | o rótulo do canal em `CAMPOS_LEGIVEIS["Unidade"]` **já existe**: a tarefa que o acrescentaria saiu, e ficou a conferência |
| comandos de implantação da `107` | `conceder_`, `retirar_` e `substituir_administracao_institucional`, todos com o papel fixo no código de aplicação | recebem `--papel` (D-002) |
| `processos/migrations` | última é a `0004`; nenhuma branch aberta cria `0005` em 31/10 | o incremento A cria a `0005` |

**Contratos de que esta feature depende**, conferidos na `main` em `81ce6e94`:

- `109`: `Unidade.atendimento` (`CharField(255)`, vazio = não declarado); a validação dele (uma
  linha, até 255, ausente ou preenchido); `identificacao.da_unidade`, `da_implantacao` e a regra de
  "uma unidade ativa", lidas do banco a cada pedido.
- `108`: os assuntos por `aggregate_type`, com `Unidade` → `REGISTRAR_UNIDADE` e `ALTERAR_UNIDADE`;
  as situações `ATIVA`/`DESATIVADA`; a leitura de `detalhe.antes`/`detalhe.depois`; `linhas(registros,
  *, nome_da_unidade)`; o autor `implantacao` mostrado como "Implantação"; o canal de atendimento
  entre os campos legíveis da Unidade.
- `106`/`107`: `PAPEIS_INSTITUCIONAIS` lido por `catalogo()` e `permissoes_dos_papeis`, que ignora
  papel desconhecido (o que torna a reversão segura, ver a [migração](migracao.md)); `_autoridade`
  recusa o papel institucional pela tela; `Vinculo.papel` é texto sem restrição no banco — o papel
  novo não pede migration; `production.py` e `provedor_configurado` recusam adaptador de `tests.` e
  adaptador que se declara de teste.
- `avisos`: `garantir_modelos_iniciais(*, correlation_id="sincronizar-unidades")`, sem unidade e com
  o ator `implantacao` — a extração da D-006 continua necessária.

**Regra para a implementação.** Cada incremento começa numa branch nova a partir da `main` do dia, e
a primeira tarefa dele reconfere os contratos acima; se um deles mudou, a spec volta ao
`/speckit-analyze`.

## Technical Context

**Language/Version**: Python 3.13 · **Primary Dependencies**: Django; Playwright (grupo opcional
`navegador`, já instalado pela `107`), só para teste.

**Storage**: PostgreSQL. **Uma migration**, `processos/0005`, com os dois gatilhos (D-013), no
incremento A. Nenhuma em `unidades` nem em `seguranca`: o papel novo é catálogo, e `Vinculo.papel` é
texto. Nenhuma tabela append-only nova: o `M` do `provisionar_papeis` continua **46**.

**Testing**: pytest contra PostgreSQL; os gatilhos e a recusa de privilégio só se observam em casos
transacionais com a role de runtime, como os da `060`. Jornada em `tests/navegador/`.

**Target Platform**: `/gestao/administracao-de-unidades` e as quatro rotas filhas; o comando
`semear_unidades` e o apelido `sincronizar_unidades`; a opção `--papel` dos três comandos de
implantação; o adaptador de homologação, só fora de produção.

**Performance Goals**: as telas leem uma unidade por chave e a lista inteira (dezenas de linhas);
o histórico é uma consulta mais a tradução da `108`, que tem custo constante por tipo. As telas que
já existem não fazem consulta a mais: a barra pergunta a permissão ao ator, que já está na
requisição.

**Constraints**: CSP sem `unsafe-inline` — estilo em `telas/unidades.css`, nenhum script; toda classe
nova com regra na folha; nenhum 404 novo sem linha no inventário das negativas da `033`; a varredura
de vocabulário e a de acessibilidade valem para as telas novas.

**Scale/Scope**: ~26 unidades no horizonte; uma ou duas pessoas com cada papel institucional.

## Constitution Check

*Antes do Phase 0, e de novo depois do desenho.*

| Princípio | Como se cumpre |
|---|---|
| I. Linguagem ubíqua | "Unidade", "registro de Unidades", "desativar" — os nomes da `060`; a tela diz "semente" só onde fala de instalação |
| II. Imutabilidade e temporalidade | o ato publicado guarda a unidade do dia (`060`) e não é tocado (FR-3323, SC-1045); unidade não se exclui e código não muda (gatilhos da `060`, inalterados); escopo de Processo e Edital passa a ser imutável no banco (D-013) |
| III. Negar por padrão; auditoria | a permissão é conferida na aplicação e de novo na confirmação (FR-3309, FR-3325); a demonstração é recusada antes de ler (FR-3312); todo ato tem pessoa, motivo, antes e depois, na mesma transação (FR-3313, FR-3332); LGPD avaliada (D-012) |
| IV. Regras no domínio; concorrência | validação única no domínio (D-005); trava e versão conferida contra perda de atualização (D-007); trava global na semente (D-004); consequências ditas antes da desativação (FR-3326, FR-3330) |
| V. Rastreabilidade e simplicidade | nenhuma tabela, nenhuma coluna, nenhuma FK; reaproveita a validação, a tradução da trilha, as linhas do compositor e o padrão de telas da `107`; [matriz](rastreabilidade.md) requisito a requisito, inclusive os casos-limite |
| VI. Jornada e valor demonstrável | a jornada no navegador, de unidade inexistente a Processo criado (D-015, SC-1041), prova as regras; a validação por pessoas antes do SSO usa a entrada de homologação, numa instância controlada (D-017, D-018, SC-1048) |
| Governança do usuário | P-1 a P-6 continuam perguntas; a revisão da decisão de produto 3 (D-002) foi confirmada em 31/10 |

**Sem violação.** A complexidade nova é proporcional: uma migration de gatilho (mesmo molde da
`060`) e uma opção de exportação no comando, que só serve à reversão (D-016).

**Reavaliação depois do desenho**: o desenho não acrescentou entidade, serviço nem dependência. Um
ponto mereceu segunda leitura, e mudou na revisão final: a versão anterior ampliava o papel
institucional de acessos, o que tocava o princípio III por ampliar privilégio no deploy, sem ato. O
papel próprio da D-002 cumpre o menor privilégio sem estrutura de autorização nova. O que falta —
quem audita o institucional — é a P-4, de governança, e não violação. O adaptador de homologação
(D-018) também mereceu leitura pelo princípio III: é uma subclasse do provedor simulado, não muda
o contrato da `106`, não traz criptografia própria, e produção o recusa pelas duas barreiras que já
recusam o simulado. A barreira do ambiente é o perímetro, e a exposição dele é a P-6.

## Project Structure

### Documentação (esta feature)

```text
specs/110-cadastro-de-unidades/
├── spec.md
├── research.md            # D-001 a D-019
├── plan.md                # este arquivo
├── data-model.md
├── migracao.md            # migração e reversão
├── quickstart.md
├── contracts/
│   ├── telas-de-unidades.md
│   └── registro-e-semente.md
├── checklists/requirements.md
├── rastreabilidade.md
└── tasks.md
```

### Código (o que muda)

```text
backend/
├── Makefile                                           # alvo `unidades` → semear_unidades
├── processo_seletivo/
│   ├── seguranca/acessos.py                           # o papel `administrador-de-unidades` (D-002)
│   ├── seguranca/application/acessos.py               # papel institucional recebido; recusa pela tela de todo papel institucional
│   ├── seguranca/application/suspensao.py             # suspensão só pela implantação para todo papel institucional
│   ├── seguranca/management/commands/{conceder,retirar,substituir}_administracao_institucional.py  # `--papel`
│   ├── unidades/
│   │   ├── domain/registro.py                         # NOVO: a regra de validação (D-005)
│   │   ├── domain/nomes.py                            # permissão, recusas novas
│   │   ├── application/registro.py                    # NOVO: os casos de uso (D-006–D-008)
│   │   ├── application/semente.py                     # era sincronizacao.py (D-001, D-004, D-016)
│   │   ├── management/commands/semear_unidades.py     # era sincronizar_unidades.py (D-003)
│   │   └── management/commands/sincronizar_unidades.py # o apelido, com o aviso (D-003)
│   ├── avisos/application/modelos.py                  # os modelos de uma unidade, com o ator recebido (D-006)
│   ├── processos/migrations/0005_escopo_imutavel.py   # NOVO: os gatilhos (D-013)
│   ├── processos/management/commands/seed_demo.py     # chama a semente
│   └── interface/
│       ├── unidades.py                                # NOVO: as telas (D-011)
│       ├── navegacao.py                               # "Unidades" em SECOES_DE_ACESSO
│       ├── urls.py
│       ├── static/interface/telas/unidades.css        # NOVO
│       └── templates/interface/
│           ├── unidades.html                          # NOVO: lista
│           ├── unidades_ficha.html                    # NOVO
│           ├── unidades_formulario.html               # NOVO: cadastrar e editar
│           ├── unidades_conferencia.html              # NOVO: prévia e confirmação
│           └── unidades_situacao.html                 # NOVO: desativar e reativar
├── tests/
│   ├── homologacao/provedor.py                        # NOVO: subclasse do provedor simulado (D-018)
│   ├── homologacao/test_entrada_de_homologacao.py     # NOVO: as recusas de produção e a entrada
│   ├── seguranca/test_papel_do_registro.py            # NOVO: `--papel`, a recusa da tela, a suspensão
│   ├── unidades/test_semente.py                       # substitui test_sincronizacao.py
│   ├── unidades/test_regra_da_unidade.py              # NOVO
│   ├── unidades/test_administrar_unidades.py          # NOVO
│   ├── unidades/test_compatibilidade_do_registro.py   # NOVO
│   ├── authorization/test_administrar_unidades.py     # NOVO
│   ├── authorization/test_isolamento_entre_unidades.py # NOVO (D-014)
│   ├── integration/test_escopo_imutavel.py            # NOVO
│   ├── interface/test_telas_de_unidades.py            # NOVO
│   ├── navegador/test_jornada_de_unidades.py          # NOVO (D-015)
│   ├── integration/agenda/test_fonte.py               # cria o Edital na outra unidade
│   ├── seguranca/test_vinculos.py                     # importa a regra do domínio
│   ├── conftest.py                                    # marcador que dispensa o Cefor da suíte
│   └── migrations/test_migrations.py                  # processos: 4 → 5
scripts/docker/entrypoint.sh                           # semear_unidades
specs/033-navegacao-por-capacidade/inventario-das-negativas.md  # o 404 da ficha
AGENTS.md, README.md, doc/implantacao-em-producao-ubuntu.md,
doc/ativacao-do-sso-institucional.md                   # a semente e a linha nova (FR-3307)
doc/auditoria-edital-pdf-2026-10-08/cenarios/comum.py,
docs/libras/ferramentas/exportar_corpus.py             # citam a sincronização (D-003)
```

**Structure Decision**: monólito Django existente; nada de app novo. A regra fica no `unidades`,
dono da Unidade; as telas, na `interface`, ao lado das da `107`.

## Ordem de implementação

Três incrementos, cada um num PR, com a suíte verde (D-019):

- **A — Integridade do escopo** (US6; FR-3333–FR-3336). Os gatilhos, o teste da agenda e os testes
  de isolamento. Não depende de nada, e pode começar já.
- **B — Entrada de homologação** (US7; FR-3342, FR-3343). Só código de teste e documentação. Não
  depende de nada; em paralelo com A.
- **C — Fonte oficial e administração** (US1–US5; o resto dos requisitos). **Um PR só**: a troca da
  sincronização pela semente não entra na `main` sem as telas e o papel, para que nenhum ambiente
  que usa unidade fique sem como cadastrá-la. Dentro dele, cinco passos com a suíte verde em cada um:
  regra e papel; semente com o apelido; casos de uso; telas e jornada; documentação. Espera a
  confirmação da revisão da decisão de produto 3, e é validado por pessoas com B.

## Os quinze testes obrigatórios do pedido

| # | Pedido | Onde |
|---|---|---|
| 1 | O Cefor continua sem alteração | `test_compatibilidade_do_registro.py::test_o_cefor_continua_sem_acao`; a suíte inteira |
| 2 | Segunda unidade pela aplicação | `test_administrar_unidades.py::test_registrar_uma_unidade`; a jornada |
| 3 | Permanece no banco sem estar no JSON | `test_semente.py::test_unidade_fora_do_arquivo_permanece` |
| 4 | Reinicialização não altera nem remove | `test_semente.py::test_a_inicializacao_nao_altera_o_registro`, `test_os_roteiros_chamam_a_semente` |
| 5 | Nome e atendimento não revertidos pelo deploy | `test_semente.py::test_a_semente_nao_desfaz_a_tela` |
| 6 | Sem `unidade:administrar` não modifica | `authorization/test_administrar_unidades.py` (matriz de papéis, inclusive o Administrador institucional de acessos sem o papel do registro; demonstração; escopo de unidade; envio forjado); `seguranca/test_papel_do_registro.py` (a tela não concede o papel) |
| 7 | Código imutável | `test_administrar_unidades.py::test_o_codigo_enviado_na_alteracao_e_ignorado`; regressão `test_o_codigo_da_unidade_nao_muda` da `060` |
| 8 | Escopo de Processo e Edital imutável no banco | `integration/test_escopo_imutavel.py` |
| 9 | Desativar impede novos e preserva existentes | `test_administrar_unidades.py::test_desativada_nao_recebe_processo_e_conduz_o_existente` |
| 10 | Reativar restaura | `test_administrar_unidades.py::test_reativada_volta_a_receber_processo` |
| 11 | Duas unidades não compartilham autorização, autoridade nem Edital | `authorization/test_isolamento_entre_unidades.py`; `test_administrar_unidades.py::test_unidade_nova_nao_herda_autoridade_nem_acesso` |
| 12 | Publicações históricas preservadas | `test_compatibilidade_do_registro.py::test_editar_a_unidade_nao_muda_o_publicado` |
| 13 | Trilha correta | `test_administrar_unidades.py::test_cada_ato_grava_o_evento_no_escopo_da_unidade`, `test_a_trilha_da_unidade_le_os_atos` |
| 14 | Modelos iniciais uma vez | `test_administrar_unidades.py::test_os_modelos_iniciais_nascem_uma_vez`; `test_semente.py::test_modelos_iniciais_idempotentes` |
| 15 | Homologação com o seletor | `test_telas_de_unidades.py::test_a_demonstracao_e_recusada_e_nao_ve_o_item`; `test_compatibilidade_do_registro.py::test_seed_demo_continua`. A validação por pessoas, que o seletor não alcança, é a da entrada de homologação: `homologacao/test_entrada_de_homologacao.py` e o roteiro G (SC-1048) |

## Riscos

| Risco | Efeito | Mitigação |
|---|---|---|
| A `main` mudar os contratos entre a revisão e o início de um incremento | contrato desta spec desatualizado | a primeira tarefa de cada incremento reconfere (§Verificação de dependência) |
| Roteiro de produção instalado de cópia antiga chama `sincronizar_unidades` | nenhum: o apelido roda a semente e avisa (D-003, EC-17) | `test_semente` chama o apelido; o guia diz quando o retirar |
| Release desta feature levar mudança no `unidades.json` | a mudança nunca se aplica, sem aviso | regra 2 da [migração](migracao.md); `test_semente` confere que o arquivo continua só com o Cefor |
| Desativação por engano | novos certames e acessos bloqueados na unidade | confirmação com consequências; reversível pela tela; trilha |
| Teste de isolamento revelar vazamento | escopo da feature cresce | a correção entra aqui (D-014), registrada no `verificacao.md` |
| **Sem SSO, a VM de homologação e a produção não têm a tela** | o critério "sem PR nem deploy por campus" só se exerce em produção depois do SSO | é a limitação de toda a gestão (B-1 do guia), e não desta feature; a validação por pessoas usa a entrada de homologação numa instância controlada (D-017, D-018) |
| O provedor de homologação chegar a produção | autenticação sem provedor | as duas recusas que já valem para o provedor simulado (pacote `tests.`, declaração de teste), no *boot* e em execução, com teste para a subclasse (D-018) |
| Ambiente de homologação funcional exposto | quem passa pelo perímetro escolhe como quem entrar | só `localhost` até a P-6; depois, rede fechada e autenticação básica no *proxy* (D-018); nunca a VM de homologação; só dado sintético |
| *Proxy* HTTPS diante das settings de desenvolvimento | a conferência de origem do CSRF recusa todo POST | o *proxy* não termina TLS; o transporte cifrado é a VPN (D-018) |
| A troca da fonte entrar sem o mecanismo novo | ambiente que usa unidade sem como cadastrá-la | a troca e as telas no mesmo PR (D-019) |
| Ninguém receber o papel do registro | a tela existe e recusa todos | é o estado seguro; a designação é a P-5 |
| Concessão do papel do registro pela tela, por engano de código | o poder de mudar o registro sai do ato de implantação | `_autoridade` recusa todo papel institucional; teste dedicado (FR-3339) |
| Reverter para uma release que não conhece o papel do registro | vínculos com papel desconhecido | `permissoes_dos_papeis` ignora papel desconhecido: não dá permissão nenhuma; ver a [migração](migracao.md) |
| Testes de banco em paralelo | a semente trava por *advisory lock*, que é por banco; os papéis de conformidade são do cluster | cada worker tem o seu banco; T026 não roda `provisionar_papeis` nem `migrate` dentro do caso |
| A troca da moldura com a segunda unidade ativa surpreender o candidato | mensagens e telas passam a dizer "Ifes" | aviso na confirmação (FR-3330); a decisão é a P-1 |

## Complexity Tracking

Nenhuma violação constitucional a justificar.
