# Research: Ações disponíveis

As decisões de produto estão em [spec.md](spec.md) (D-001 a D-010). Aqui ficam as escolhas técnicas.

## Inventário de cobertura dos tipos de trabalho humano

| Domínio | Objeto | Situação que permite | Permissão | Impedimentos | Navegação hoje | Descoberta hoje | Conclusão refletida | Na faixa? |
|---|---|---|---|---|---|---|---|---|
| Edital — elaborar | Edital | `EM_ELABORACAO` | `edital:elaborar` | nenhum | Lista ("Elaborar o Edital"), detalhe | coluna da Lista | situação muda | **sim**, "Continuar a elaboração" |
| Edital — submeter | Edital | `EM_ELABORACAO` | `edital:submeter` | pendência impeditiva (validação inteira) | detalhe, confirmação | coluna da Lista, sem previsão | situação `EM_REVISAO` | não: o item do Edital é elaborar (D-004) |
| Edital — homologar / devolver / revogar | Edital | `EM_REVISAO` / `HOMOLOGADO` | `edital:homologar` | nenhum previsto | detalhe | coluna da Lista | situação muda | **sim**, "Homologar o Edital" |
| Edital — publicar | Edital | `HOMOLOGADO` | `edital:publicar` | segregação (lote); pendência (só no detalhe) | detalhe | coluna da Lista | `PUBLICADO` | **sim**, sem segregação; pendência no detalhe (D-004) |
| Edital — encerrar, cancelar, retificar | Edital | publicado etc. | gestor, elaborador | — | Lista, detalhe | coluna | — | não: gestos raros, sem espera de ninguém |
| Retificação — submeter, editar | Retificação | `EM_ELABORACAO` | `retificacao:elaborar`/`submeter` | nenhum previsto | detalhe (103) | marca da Lista | situação muda | **sim**; devolvida dita "Corrigir" |
| Retificação — homologar / devolver | Retificação | `EM_REVISAO` (devolver também de `HOMOLOGADA`) | `retificacao:homologar` | nenhum | detalhe | marca | — | **sim**, um item |
| Retificação — publicar | Retificação | `HOMOLOGADA` | `retificacao:publicar` | segregação (`ofertas`) | detalhe | marca | `PUBLICADA` | **sim**, sem segregação |
| Retificação — cancelar | Retificação | `EM_ELABORACAO` | `retificacao:cancelar` | — | detalhe | — | `CANCELADA` | não: não é o ato principal (103, D-003) |
| Recursos | Recurso | sem juízo, ou admitido sem decisão | `recurso:julgar` (julgador) | — | tela de recursos do Edital | coluna, com número | contagem cai | **sim**, um item por Edital |
| Avaliação | Atribuição em Etapa | alocação ativa, avaliação não concluída | vínculo de comissão | progressão (013) | Minhas Etapas, mesa | Minhas Etapas, com carga | carga cai | **sim**, um item por Etapa com pendentes |
| Classificação — conduzir, emitir ordem, corte, convocação | marco do Edital | Edital publicado, marco com recortes | presidência ou permissões de classificação | regras do marco | detalhe do Edital (Classificação), conduzir o marco | seção do detalhe | ato emitido | **não** (D-002): exige ler o conteúdo publicado e os atos de cada marco |
| Resultados — divulgar | ato de classificação emitido | ato sem divulgação | `resultado:publicar` | — | detalhe do Edital, prévia | seção do detalhe | divulgação | **não** (D-002): não há derivação pronta de "emitido e não divulgado" por Edital |
| Avisos aos candidatos | ato publicado | — | `aviso:enviar` | LGPD (chave) | detalhe do Edital | seção do detalhe | aviso enviado | **não**: é complemento, não ato pendente |

## R-001 — A derivação, `interface/trabalho.py`

**Decision**: `do_ator(ator, editais)` devolve uma lista de `ObjetoDeTrabalho` (natureza, título, ato,
situação, detalhe, desde, url, edital). Ela recebe os Editais que a tela já carregou, e lê:
`atos.disponiveis` (Edital), as ofertas de `atos_retificacao.em_curso_por_edital` (uma consulta),
`impede_por_segregacao` sobre participantes em lote (duas consultas, só para Editais em revisão ou
homologados), recursos agregados por Edital (uma consulta, só com a permissão) e
`comissao_selectors.minhas_etapas` mais `carga_nas_etapas` (o custo de Minhas Etapas). Ordena e
deduplica por (natureza, id).

**Rationale**: FR-2801 a FR-2806. Nenhuma regra nova: cada item é a resposta de uma função que já
decide o botão do detalhe.

**Alternatives considered**: uma consulta por Edital com `do_edital` completo (pendências) — custo da
validação inteira por linha; tabela de tarefas — proibida (FR-2829).

## R-002 — A faixa, `_acoes_disponiveis.html`

**Decision**: `section` com `h2` "Ações disponíveis para você", o total, uma `ul` dos cinco
primeiros e um `details` com "Mostrar as outras N". Cada item: o título como link (o destino), a
situação, o detalhe (justificativa ou motivo), "desde dd/mm", e o rótulo do ato. Sem itens, uma linha
`p` discreta. A nota de cobertura fecha a faixa.

## R-003 — Contagens da coluna em lote

**Decision**: `acoes.contagens_da_lista(editais)` faz duas agregações (inscrições submetidas e
recursos aguardando, agrupadas por Edital) e `do_edital(..., contagens=…)` as lê; sem o argumento,
o comportamento do detalhe não muda. A mesma agregação de recursos serve à faixa.

## R-004 — Participantes em lote

**Decision**: `selectors.participantes_em_lote(editais)` devolve `{edital_id: participantes}` com a
mesma forma de `participantes_do_edital`, em duas consultas (`RevisaoEdital` mais recente por Edital;
`Homologacao` não revogada dessas revisões). A Lista passa `segregacao=` a `do_edital`, e "Publicar"
sai desabilitado com o motivo, como no detalhe (FR-2816).

## R-005 — "Conferir e submeter", "Conferir e publicar"

**Decision**: `acoes.para_a_lista(conjunto, edital)` troca, nas ações disponíveis, o destino de
`submeter` e `publicar` para o detalhe (âncora das pendências) e o rótulo para "Conferir e
submeter"/"Conferir e publicar". A chave não muda, e por isso `test_listagem_e_detalhe_nao_divergem`
continua valendo.

## R-006 — O ato da Retificação na coluna

**Decision**: a coluna desenha, além de `edital.grupo`, um link por Retificação em curso cujo resumo
tem `meu_ato`, com o rótulo do ato da faixa. A marca sob a situação passa a dizer só a situação da
Retificação e, quando o ato não é da pessoa, quem age a seguir. O "Nenhuma ação disponível" passa a
olhar as duas listas.

## R-007 — "O que fazer agora" do Edital

**Decision**: quando `grupo` está vazio, o cartão lê `retificacoes_em_curso` (a derivação da `103`):
com `meu_ato`, "Uma Retificação deste Edital aguarda você" e o link; sem, "A Retificação … aguarda
<papel>". Só sem Retificação em curso volta a frase "Nenhum ato disponível". O aviso de imutável da
`037` (FR-541b) não muda.

## R-008 — Devolvida, reenviada, espera

**Decision**: `atos_retificacao.resumo` ganha `devolvida` (`EM_ELABORACAO` com `return_reason`),
`reenviada` (`EM_REVISAO` com `return_reason`), `rotulo_situacao` e `desde` (`submitted_at` ou
`homologated_at`). `_CAMPOS_DO_RESUMO` passa a trazer `return_reason`, `submitted_at`,
`homologated_at`.

## R-009 — Advertências separadas

**Decision**: `retificacoes.advertencias_do_vigente(retificacao)` calcula, com a mesma validação e a
mesma topologia, as advertências do conteúdo vigente sem as alterações, e devolve o conjunto de
pares (código, caminho). A confirmação mostra primeiro as que não estão nele e recolhe as outras num
`details` "Avisos que já valiam no Edital vigente (N)". A tabela de alterações passa a aparecer em
`homologar` e `devolver`, com o título "O que esta Retificação altera".

## R-010 — Minhas Etapas

**Decision**: o estado vazio mantém "Você não possui Etapas atribuídas no momento" (três testes de
autorização o usam) e acrescenta "Esta área é da avaliação nas comissões; atos de Edital e de
Retificação aparecem em Processos Seletivos", com o link. O
rótulo da barra não muda (D-007).

## R-011 — Testes

**Decision**: jornadas A a I em `tests/interface/test_acoes_disponiveis.py`, com os auxiliares da
`103`; escala em `tests/performance/test_trabalho_em_escala.py`, medindo a derivação e a Lista com
0, 3, 30 e 300 Editais publicados por `publicar_direto`.
