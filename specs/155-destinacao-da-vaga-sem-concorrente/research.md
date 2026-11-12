# Research: Destinação da vaga reservada sem ocupante

**Feature**: [spec.md](spec.md) · **Plano**: [plan.md](plan.md) · **Data**: 2026-11-11

As questões técnicas do plano, numeradas `R-001` em diante. As decisões de produto estão na spec
(`D-001` a `D-016`); a D-015 continua em aberto e governa só o incremento F.

O levantamento foi feito sobre `d1f6bbf4` (a branch do #482), lendo o código de `ocupacao/`,
`convocacao/`, `divulgacao/`, `recursos/`, `sorteios/`, `classificacao/`, `editais/`,
`publicacoes/`, `portal/` e `interface/`.

---

## R-001 — A destinação é um `MovimentoDeVaga`, gravado por comando próprio

**Decisão.** O ato "Destinar à ampla concorrência" grava o mesmo `MovimentoDeVaga` de espécie
`REVERSAO_DE_COTA` que a apuração grava hoje, por um comando novo,
`ocupacao/application/destinacao.py::destinar_vaga`. O comando segue o molde de
`ocupacao/application/acrescimo.py`:
- prévia com assinatura;
- dois passos;
- `comando_de_comissao`;
- `auditar`;
- emissão da apuração seguinte num *savepoint*.

**Por quê.** A apuração já sabe ler o movimento (`efetivas = publicadas + recebidas − cedidas +
acrescidas`, `ocupacao/domain/apuracao.py`), e o movimento antigo e o novo precisam contar igual
(FR-6316). Uma tabela nova obrigaria a apuração a ler duas fontes para a mesma quantidade.

**O que muda no modelo** (migration `ocupacao/0005`):
- `apuracao` passa a ser **a apuração lida pelo ato**, e não "a que o causou". Ela continua
  obrigatória quando a origem tem apuração; fica nula só na lista de sorteio sem relação (R-007).
- Colunas novas, todas nulas nas linhas antigas:
  - o recorte (`edital`, `perfil_id`, `marco_id`), para o caso sem apuração;
  - `gatilho`;
  - `fundamento`, com a frase publicada e a versão;
  - `versao`, FK da versão lida;
  - `desfaz`, autorreferência (R-005).
- Constraints novas:
  - `ck_movimento_especie`, como a do acréscimo;
  - `ck_movimento_com_recorte`: `apuracao` ou o recorte preenchido;
  - `ck_desfazimento_cita_o_movimento`.
- A trava append-only não muda: são colunas acrescentadas, e o gatilho rejeita `UPDATE`/`DELETE` de
  linha, não DDL.

**A apuração de origem.** Ela leu o recorte sem o movimento novo e passaria a obsoleta por
`movimento_posterior`. O comando emite a sucessora no mesmo *savepoint*, com o motivo "Destinação de
N vaga(s) à ampla concorrência", como `_emitir_seguinte` faz no acréscimo. A apuração da **ampla**
fica obsoleta e é emitida por quem conduz (FR-6313), porque é ela que muda quem é chamado.

**Alternativas recusadas.**
- Tabela própria: duas leituras da mesma quantidade.
- Gravar o movimento sem a sucessora da origem: a reserva mostraria "obsoleta" logo depois do ato
  que a resolveu, o contrário da US1.

## R-002 — A vaga não preenchida é tabela nova, e não acréscimo negativo

**Decisão.** Um modelo novo, `ocupacao.models.VagaNaoPreenchida`, append-only:
- espécie `DECLARACAO` ou `DESFAZIMENTO`, com `desfaz`;
- `quantidade`, `fundamento` não vazio, `versao`, a apuração lida e o recorte;
- ator e instante.

A apuração ganha a coluna `nao_preenchidas` (padrão zero) e o universo `naoPreenchidasLidas`. A
conta passa a ser `faltando = efetivas − ocupadas − nao_preenchidas`, com
`ck_apuracao_ocupadas_no_limite` estendida a `ocupadas + nao_preenchidas ≤ efetivas`. A causa de
obsolescência nova é `declaracao_posterior`, com a frase no template.

**Por quê.**
- Reduzir as efetivas, como um desfazimento de acréscimo, diria que a vaga deixou de existir. A
  D-003 diz que ela existe, e não foi preenchida.
- A soma das efetivas por recorte (FR-6311) só vale para a destinação; a declaração não move nada.

**Custo.** Uma tabela append-only a mais:
- `TABELAS_APPEND_ONLY` vai a 59;
- o `provisionar_papeis` passa a informar `N de 59`;
- `tests/seguranca/test_homologacao_preservada.py` muda a contagem e o recorte das últimas 15;
- o CLAUDE.md ganha "eram 58 … são 59 com a vaga não preenchida da `155`".

## R-003 — A terceira resposta da reversão não entra na tupla que reverte

**Decisão.** Em `ocupacao/domain/nomes.py`:
- `PASSAGEM_ENTRE_COTAS = "THROUGH_OTHER_QUOTAS"` (cabe nas 32 posições da coluna);
- `DECLARACOES_DE_REVERSAO = ESPECIES_DE_REVERSAO + (PASSAGEM_ENTRE_COTAS,)`.

`ESPECIES_DE_REVERSAO` **não muda**, porque `quantidade_a_reverter` cede o saldo de tudo o que estiver
nela. Uma resposta que entrasse ali reverteria como a por saldo. `reversao.declarada` passa a devolver
a declaração (as três), e `reversao.especie_que_move` devolve só as duas que movem.

**O que acompanha** (o mapa completo está nas notas do levantamento):
- validação: `editais/domain/validation.py::_reversao_declarada` aceita a declaração, e a mensagem
  de `kind_required` nomeia as três;
- coluna com `choices`: `editais/models/perfis.py`, migration nova de `editais`, que entra na
  contagem do guardião de migrations da `022` com a justificativa;
- passo Perfis: `_perfil.html` e `compor_perfis.html`, a terceira `<option>`;
- frases: os dois dicionários de `publicacoes/infrastructure/pdf.py`, com "de um código" na redação,
  porque `apresentacao.py` substitui esse trecho;
- Retificação e revisão: `interface/retificacao.py`, `aplicacao_na_retificacao.py`, `revisao.py`,
  `aplicacao.py::_valor_do_campo_em_palavras`;
- dúvidas e prévias: `duvidas/domain/rotulos.py`, `previa_da_classificacao.py`,
  `previa_do_sorteio.py`;
- contrato: `specs/001-processo-seletivo-editais/contracts/openapi.yaml`, o `enum` e a descrição;
- `ocupacao/application/acrescimo.py:74`, que bloqueia o acréscimo na linha geral com qualquer
  declaração, continua bloqueando — a passagem também é declaração sobre a vaga reservada.

**Sem degrau canônico.** Cada degrau de 1 a 21 acrescentou propriedade, coleção ou seção. A elevação
só grava chave ausente com o padrão, e o objeto da reversão foi desenhado para receber valor novo
"sem um novo degrau canônico" (`016`, R-005 da pesquisa dela). Os Editais publicados guardam a
declaração que publicaram (D-016); a troca é por Retificação, que já admite o caminho.

**Testes que prendem as duas respostas e mudam:**
- `interface/test_retificar_reversao.py`;
- `unit/editais/test_reversao_declarada.py`;
- `unit/publicacoes/test_redacao_das_frases.py`;
- `unit/duvidas/test_casos_da_revisao.py`;
- `interface/test_previa_por_recorte.py`;
- `interface/test_correcoes_de_norma_na_revisao.py`;
- `interface/test_compor_quadro.py`.

## R-004 — A condição do esgotamento e os impedimentos

**Decisão.** A conta é pura, em `ocupacao/domain/destinacao.py`:

```text
ainda_podem_ocupar(posicoes, excluidos, ocupam_a_ampla_confirmados, alcancaveis) -> int
impedimentos(fatos) -> [Impedimento(codigo, frase, ate)]
```

Quem a alimenta, e de onde:

| Fato | Fonte | Dono |
|---|---|---|
| posições da ordem da reserva | `ato_vigente(...).posicoes` | `classificacao`, já lido pela ocupação |
| excluídos por desfecho | `EfeitoDeOcupacao` de exclusão no recorte | `ocupacao` |
| ocupa a ampla **com aceite** | `EfeitoDeOcupacao` de inclusão no recorte da ampla, para a inscrição | `ocupacao` |
| ocupa a ampla **sem aceite** (titular da apuração, sem efeito) | `ocupantes_da_ampla` menos os confirmados | `ocupacao` |
| alcançável | dentro dos que progrediram no corte vigente; ou toda a ordem, se `admite_continuacao` | `classificacao` |
| resultado do marco definitivo | `divulgacao.selectors.vigente_do_marco(...).natureza` | `divulgacao` |
| prazo recursal aberto | `publicabilidade.janela_aberta_ate` | `divulgacao` |
| recurso pendente | `recursos.selectors.recursos_pendentes_do_marco` | `recursos` |
| chamada em curso na reserva | `convocacao.selectors` (em aberto) | `convocacao` |

**A fronteira entre módulos.** A ocupação não pode importar a convocação
(`tests/test_dependencia_da_convocacao.py`), e o acréscimo resolveu isso com um *callable* injetado
(`pessoas_chamadas`). A destinação faz o mesmo: o comando recebe `fatos_externos(edital, perfil,
marco, lista) -> FatosExternos`. A interface o compõe a partir de `divulgacao`, `recursos` e
`convocacao` (`interface/destinacao_da_vaga.py`), e o comando o reavalia sob a trava.

**Por quê "com aceite" sai dos efeitos.** O aceite da ampla grava um efeito de inclusão
(`EFEITO_POR_DESFECHO`), e esse efeito é da ocupação. Assim, distinguir titular de ocupante
confirmado não exige ler a convocação.

**A inabilitação** (V-2) não tem efeito próprio. O inabilitado tem posição e não progride, porque o
corte só alcança quem habilita na Etapa governada. Ele conta como "não pode ocupar" quando não está
entre os que progrediram e o prazo recursal da Etapa está encerrado. A verificação V-2 vira teste.

## R-005 — O desfazimento

**Decisão.**
- **A destinação** se desfaz por um `MovimentoDeVaga` de espécie `DESFAZIMENTO_DA_REVERSAO`, com
  `desfaz` apontando o original, origem e destino invertidos e a mesma quantidade. A apuração lê as
  duas espécies como movimento de quantidade, e a soma volta.
- **A não preenchida** se desfaz pela espécie `DESFAZIMENTO` da própria tabela.

Chamada dependente é a convocação no recorte de destino cuja apuração (`Convocacao.apuracao`, FK
obrigatória) leu o movimento em `movimentosLidos`. Ela também chega por *callable* injetado.

**A recusa registrada** (FR-6335). Com chamada dependente, o comando grava o evento de trilha
`OCUPACAO_DESFAZIMENTO_IMPEDIDO`, com as chamadas nomeadas, e devolve 409 por
`ctx.concluir_sem_resultado`, que confirma a transação. Levantar `DomainError` desfaria o registro.

## R-006 — A lista vazia: um gesto e a publicação conjunta

**Decisão.**
- **O gesto.** Uma view nova, `interface:registrar-lista-sem-concorrente`, em dois passos. Ela chama
  `emitir_ordem` e, se o marco tem regra de corte, `emitir_corte`, numa transação só, com chaves de
  idempotência derivadas da chave do gesto. Os dois comandos e os dois registros são os de hoje: o
  gesto não inventa ato (D-010), e a ordem continua sem posição nenhuma (FR-6329).
- **A publicação conjunta.** `divulgacao/application/publicar.py::publicar_resultado` publica um ato
  por vez (`uq_publicacao_por_ato_natureza`). Passa a publicar, **na mesma transação e na mesma
  confirmação**, as ordens vigentes das listas sem concorrente do mesmo marco e da mesma natureza que
  ainda não foram publicadas. A prévia da publicação as lista ("e a lista PPP: ninguém concorreu"), e
  a assinatura da prévia as inclui. Continua um registro por ato; muda o gesto.
- **No andamento**, a célula do resultado da lista vazia passa a dizer que ela sai junto da
  publicação do marco, e deixa de ser providência própria do Publicador.

**Alternativa recusada.** Um ato de publicação com várias listas, que mudaria o modelo da
divulgação e a página pública por inteiro.

## R-007 — O sorteio sem relação, com ausência comprovada

**Decisão.** A lista reservada de sorteio está **comprovadamente sem concorrente** quando três coisas
valem juntas:
- `sorteios.previa.recortes_sem_inscrito` a dá como sem inscrito (período encerrado e ninguém
  declarou a Modalidade);
- a relação vigente da **ampla** do marco existe (`relacao_vigente(lista_id=None)`), que é a relação
  definitiva pertinente;
- nenhum `ParticipanteHabilitado` dela tem `inscricao.modality_id` igual à lista.

Sem a relação da ampla, a lista aparece como "relação não congelada", e o ato não é oferecido
(FR-6333). O movimento nasce sem apuração de origem e com o recorte preenchido (R-001).

## R-008 — Uma derivação para as três telas

**Decisão.** `interface/destinacao_da_vaga.py::situacao(leitura_da_ocupacao, fatos_externos)` devolve
uma situação:
- `sem_vaga_a_destinar`;
- `destinacao_disponivel`;
- `nao_preenchida_disponivel`;
- `impedida`, com o impedimento;
- `passagem_entre_cotas`;
- `aguarda_d015`, só na reversão por saldo, no incremento F.

As três telas a leem:
- a ocupação, onde ficam os atos;
- `interface/andamento.py`, no ramo que hoje diz "Ocupar a vaga — impedida";
- `interface/conducao_da_convocacao.py::_vaga_sem_chamada`, que passa a citar a situação quando a
  fila está vazia.

**Custo de leitura.** O detalhe do Edital tem custo fixo por Edital (FR-4686 da `135`). Os fatos
externos são lidos uma vez por marco, como `_listas_vazias` faz, e não por recorte.

## R-009 — A página pública e o relatório

**Decisão.**
- **Página pública.** Um seletor público,
  `ocupacao.application.selectors.destinacoes_publicas(edital)`, devolve:
  - a lista e o Perfil de origem, pelo nome publicado;
  - o destino, ou "não preenchida";
  - a quantidade, o fundamento e a data;
  - o desfazimento, quando houver, citando o que desfaz.

  O seletor nunca devolve nome nem protocolo. Um parcial, `portal/_destinacao_das_vagas.html`, entra
  em `portal/selecao.html` depois do de convocações, no mesmo molde.
- **Relatório.** `interface/relatorio_do_edital.py` ganha a seção "Destinação das vagas", que hoje
  não lista movimento nenhum.
- **Sem PDF.** O PDF do relatório não muda (FR-6339).

## R-010 — O incremento F, bloqueado pela D-015

Até a D-015, a **reversão por saldo continua como está**: a emissão da apuração da reserva com saldo
ainda grava o movimento, e o ato novo não é oferecido para ela.

Isso **não adota** a opção B: é a ausência de mudança na parte que a decisão governa, e o PR diz isso
como pendência. A emissão passa a mover vaga **só** sob a declaração por saldo. Por esgotamento, deixa
de mover. Sob a passagem entre cotas, nunca moveu.

Fechada a D-015, o incremento F:
- escreve a condição do saldo;
- tira o último ramo de movimento da emissão;
- transforma S-1 a S-4 em teste;
- ajusta as prévias.

## R-011 — As equivalências das prévias

As duas equivalências (`tests/integration/classificacao/test_previa_por_recorte_equivale_ao_oficial.py`
e `tests/integration/sorteios/test_previa_do_sorteio_equivale_ao_oficial.py`) tiram o "cedido" do lado
oficial somando os movimentos que a emissão criou. Por esgotamento, o lado oficial passa a ser o que a
**destinação** faria, lido pela mesma conta pura (R-004) sobre o mesmo estado. A prévia não simula
desfecho nem recurso, e por isso a conta dela usa só posições, concomitância e alcance. O sentinela que
substitui `reversao.ha_quem_ocupar` passa a substituir a função nova.
