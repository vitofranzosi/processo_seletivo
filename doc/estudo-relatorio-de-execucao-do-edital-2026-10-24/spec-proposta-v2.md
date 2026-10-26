# Proposta de spec v2 — Relatório do Edital

Revisão de 24/10/2026, depois da [rodada 2](rodada-2.md). **Substitui a §6 do
[estudo](../estudo-relatorio-de-execucao-do-edital-2026-10-24.md).** A §7 (MVP) e a §8 (questões)
do estudo foram absorvidas pela §12 abaixo e pela §G da rodada 2.

> Proposta para avaliação, e não `spec.md`. A numeração `FR-`/`SC-`/`D-` nasce no
> `/speckit-specify --number N`; aqui os identificadores são locais (`R-`, `RL-`, `RNF-`, `CA-`).

## 1. Nome e objetivo

**Relatório do Edital.** É um documento gerencial, emitido sob demanda, que diz a quem não
participou da operação **o que foi oferecido, quanta procura houve, o que foi publicado, o que
falta e onde conferir**. Tudo sai de fatos registrados no GPS, e cada número é rastreável à sua
fonte.

Há duas espécies, derivadas e não declaradas (§6): **de acompanhamento** e **de encerramento**. O
Edital cancelado tem uma terceira, **de interrupção**.

## 2. Problema e hipótese

**Problema verificado.**

- Os fatos do ciclo de um Edital estão em sete telas, com quatro portas diferentes.
- Quem presta contas à direção não tem uma leitura única.
- Quem está na direção não tem acesso ao GPS.

**Hipótese a validar.** Um documento de duas páginas executivas responde à direção sem que a
presidência precise montar a resposta à mão. A validação é a conversa com destinatários reais
(G-1 da rodada 2).

## 3. Públicos e casos de uso

| Público | Caso de uso | Camada |
|---|---|---|
| **Principal:** direção-geral, direção de ensino, coordenações de curso e de programa | conhecer o resultado; saber se algo ainda exige providência; planejar a próxima seleção; levar a reunião de gestão | executiva, que se entende sozinha |
| **Secundário:** presidência da comissão e gestão | responder *"como foi?"*; conferir pendências antes e depois de encerrar | executiva + anexo; também na tela |
| **Secundário:** controle interno e auditoria | conferir documentos, regras aplicadas e números | anexo técnico |

## 4. Escopo e exclusões

**Dentro:**

- uma página e um PDF por Edital, com a mesma leitura;
- espécie derivada;
- a emissão registrada na auditoria.

**Fora:**

- estado ou transição nova, e bloqueio de ato;
- texto por modelo de linguagem;
- juízo sobre regularidade ou eficácia;
- recomendação;
- relação nominal;
- atraso inferido;
- *"aprovado"*;
- matrícula;
- série entre Editais, que é da `040`;
- relatório por Processo, que é a Evolução 2;
- guarda dos bytes do PDF (G-5).

## 5. Estrutura

**Camada executiva**, com meta de duas páginas:

1. Identificação, com duas situações: no GPS e das providências.
2. Visão geral por regras.
3. Seis indicadores.
4. Pontos de atenção.
5. Resultados por perfil de vaga.
6. Procura ao longo do período.
7. Alterações e recursos.
8. Datas principais.
9. Documentos oficiais.

**Anexo técnico:**

- A. etapas por Perfil;
- B. classificação e vagas por lista;
- C. recursos por Perfil;
- D. cronograma previsto × retificado × registrado;
- E. documentos e SHA-256;
- F. como cada número foi obtido;
- G. o que o GPS não registra;
- H. sobre a emissão.

A forma de referência é a [maquete v2](maquete-v2.pdf).

## 6. Comportamento conforme a situação

| Situação do Edital | Pode emitir? | Espécie | O que muda |
|---|---|---|---|
| em elaboração, em revisão, homologado | **não** | — | não há fato público a relatar |
| publicado | sim | acompanhamento | seções sem fato dizem *"ainda não disponível"* |
| encerrado, **com** pendência | sim | acompanhamento | a capa diz *"ainda há providência em curso"* |
| encerrado, **sem** pendência | sim | **encerramento** | — |
| cancelado | sim | interrupção | só o que foi publicado até o cancelamento, e o ato |

**Pendência** é qualquer uma destas, avaliada no instante de referência:

- marco sem resultado definitivo vigente;
- recurso aguardando admissibilidade ou julgamento;
- providência pendente de marco;
- apuração vigente com causa de desatualização;
- convocação sem desfecho e com prazo de resposta em curso.

**Registro posterior ao encerramento.** Todo ato do Edital com instante depois do
`AtoAdministrativo` de encerramento é contado e dito nos pontos de atenção. A leitura usa a mesma
reunião de `trilha_do_edital`, completada com os atos que ela não traz: publicação de resultado,
recurso, ordenação e corte.

## 7. Linguagem

- **RL-1.** O rótulo de cada fato MUST ser, nesta ordem de preferência: o que o produto já mostra
  a quem não é da gestão; o termo do domínio, explicado na primeira menção; e só então expressão
  nova. A [matriz](rodada-2.md#b-matriz-de-terminologia) é a referência.
- **RL-2.** Os rótulos de desfecho de convocação e de decisão de recurso MUST ser **importados**
  de `portal/situacao.py` (`DESFECHOS`) e `recursos/application/selectors.py` (`ESPECIES`,
  `SITUACOES`), e nunca copiados.
- **RL-3.** O relatório MUST NOT usar *"aprovado"*, *"vaga ocupada"* sem qualificação,
  *"participaram"*, *"concluído"* como situação do Edital, *"marco"* ou *"corte"* na camada
  executiva.
- **RL-4.** Totais do Edital MUST falar em **inscrições**. Dentro de um Perfil, MAY falar em
  **candidatos**: a unicidade é por identidade e Perfil.
- **RL-5.** Texto livre do Edital (título, descrição, justificativa) MUST NOT decidir situação. A
  justificativa da Retificação aparece entre aspas e como registrada.
- **RL-6.** A visão geral MUST ser composta só por frases cuja condição é verdadeira, cada uma com
  fonte (rodada 2, §C.2), e MUST NOT conter juízo, causa ou recomendação.

## 8. Indicadores

| Indicador | Fonte | Fórmula | Unidade | Limitação dita no anexo |
|---|---|---|---|---|
| Vagas imediatas | `VersaoConsolidada` vigente, `vacancyTable`/`immediateVacancies` (`visao_geral.vagas_do_conteudo`) | soma por Perfil, desdobrada por lista | vaga | é a da versão vigente, com retificações |
| Inscrições enviadas | `Inscricao` `SUBMETIDA` (`visao_geral.contagens_por_edital`) | contagem | inscrição | — |
| Iniciadas e não enviadas | `Inscricao` `RASCUNHO` | contagem | inscrição | não há data de abandono |
| Pessoas | `Inscricao.identity_subject` distintos das enviadas | contagem distinta | cadastro de acesso | duas contas da mesma pessoa contam duas vezes (G-6) |
| Candidatos por vaga | idem + vagas | Σ enviadas nos Perfis com vaga ÷ Σ vagas desses Perfis; por Perfil e nunca média | razão, uma casa | não se aplica a Perfil só de reserva |
| Com classificação publicada | `SituacaoDivulgada` `CLASSIFICADA` da `PublicacaoResultado` `DEFINITIVA` vigente | inscrições distintas **por Perfil**, unindo as listas | inscrição = candidato no Perfil | listas não se somam |
| Resultados definitivos publicados | `vigente_do_marco` | marcos com `DEFINITIVA` vigente ÷ marcos declarados | marco | — |
| Vagas com candidato classificado e habilitado | `recortes_do_marco` (`ApuracaoDeOcupacao.ocupadas`) | soma das apurações vigentes não obsoletas | vaga | não é matrícula; obsoleta vira *"não apurada"* |
| Vagas aceitas | `DesfechoDaConvocacao` `ACEITE` das convocações raiz vigentes | contagem | vaga | não é matrícula |
| Convocações aguardando resposta | `Convocacao` sem desfecho e com `vencimento` futuro | contagem | convocação | — |
| Retificações | `Retificacao` `PUBLICADA` + `alteracoes_legiveis` (antes e depois) | lista | ato | sem avaliação de impacto |
| Recursos | `Recurso`, `JuizoDeAdmissibilidade`, `DecisaoRecurso` | por Perfil: apresentados, não admitidos, indeferidos, deferidos, aguardando | recurso | deferido agrupa três espécies, como o portal |
| Avaliados, habilitados e eliminados por Etapa | `ResultadoEtapa.vigentes`, por Perfil (**não** `panorama_da_etapa`, ver rodada 2 §A.2) | contagem por consequência e origem | inscrição | sem presença |
| Inscrições no período prorrogado | `submitted_at` > `endAt` original | contagem | inscrição | só quando houve prorrogação |

Ausência segue as grafias da `040`: *não se aplica*, *ainda não disponível*, *não publicado*,
*parcial*. A rodada 1 acrescentou *não registrado pelo GPS*. Falha de leitura interrompe a emissão
e nunca vira ausência.

## 9. Autorização

- **R-1.** A página e o PDF MUST seguir a porta `pode_supervisionar`, isto é, gestão do escopo
  ou presidência do Processo. A recusa MUST ser o 404 uniforme, com linha no inventário de
  negativas da `033`.
- **R-2.** Nenhuma permissão nova no MVP. A leitura pelo `auditor` e um papel de Direção são G-3.

## 10. Dados pessoais

- **R-3.** O relatório MUST NOT conter nome, CPF, e-mail, protocolo ou identificador de candidato.
  A relação nominal é a do resultado publicado, referida pela seção de documentos.
- **R-4.** **Fato público** — vagas, e classificados por lista em resultado publicado — MAY
  aparecer desdobrado por lista de cota. **Fato não público** — eliminação, ocorrência, recurso,
  rascunho — MUST aparecer só por Perfil, sem cruzar com modalidade de cota.
- **R-5.** Nenhuma célula é suprimida. A regra de R-4 é que impede a reconstrução por diferença
  (G-4).
- **R-6.** A resposta MUST ser privada (`marcar_como_privada`), e o PDF MUST trazer em toda página
  a natureza gerencial e o instante dos dados.

## 11. Emissão, referência temporal e versionamento

- **R-7.** Toda leitura MUST acontecer numa transação de leitura só, com o instante de referência
  tomado no início. A página e o PDF dizem *"dados até DD/MM/AAAA, HHhMM"*.
- **R-8.** Emitir o PDF MUST gravar `record_event` com o Edital, o instante, o ator e o SHA-256 dos
  bytes. O número da emissão (*"emissão nº N"*) é a contagem desses eventos para o Edital.
- **R-9.** O relatório MUST NOT reconstruir o passado: ele emite o presente e o data. Uma nova
  emissão MAY divergir da anterior, e o anexo H o diz.
- **R-10.** Mesmos fatos e mesmo instante MUST produzir os mesmos bytes, porque o motor de PDF já é
  determinístico.

## 12. Requisitos funcionais

- **R-11.** Visão geral por regras (RL-6).
- **R-12.** Duas situações na capa (§6), e a espécie derivada.
- **R-13.** Pontos de atenção: pendências e registros posteriores ao encerramento, no máximo três
  itens. Os demais vão para o anexo.
- **R-14.** Resultados por perfil de vaga: vagas, candidatos, por vaga, com classificação
  publicada e situação das vagas.
- **R-15.** Procura diária, com o fim original do prazo marcado quando houver prorrogação, e
  equivalente textual.
- **R-16.** Datas principais, cada uma marcada como publicação, registrado, previsto ou prazo.
- **R-17.** Anexo técnico A a H (§5).

**Limites do MVP:** um Edital; a camada executiva e o anexo; página + PDF; sem relatório por
Processo, sem papel novo, sem guarda de bytes, sem comparação entre Editais.

## 13. Requisitos não funcionais

- **RNF-1.** O número de consultas MUST ser independente do número de inscrições. Medido no cenário:
  145 consultas com 38 e com 362 inscrições.
- **RNF-2.** Síncrono, sem fila.
- **RNF-3.** PDF pelo motor existente (`pdf.py`), sem dependência nova.
- **RNF-4.** Página dentro da CSP; folha estática; tabelas com cabeçalho; gráfico com equivalente
  textual; 375 px sem rolagem horizontal.

## 14. Critérios de aceitação

Os doze critérios da avaliação, tornados verificáveis:

| # | Critério da avaliação | Como se verifica |
|---|---|---|
| CA-1 | gestor não especialista entende o panorama | conversa com 3 destinatários sobre a v2: cada um diz, sem ajuda, o que foi oferecido, o que saiu e o que falta (G-1) |
| CA-2 | indicadores sem conceito interno | varredura do texto executivo sem os termos de RL-3 |
| CA-3 | nenhuma leitura enganosa por omissão | *"vagas aceitas"* e *"classificado e habilitado"* sempre juntos de *"não é matrícula"*; teste de composição |
| CA-4 | situação do Edital ≠ conclusão | fixture do cenário: Edital encerrado com convocação em prazo → espécie *acompanhamento* e ponto de atenção |
| CA-5 | resumo entendido isoladamente | a página 1 traz identificação, as duas situações, a visão geral, os indicadores e os pontos de atenção, sem remeter ao anexo |
| CA-6 | detalhe acessível sem sobrecarregar | pesos, corte, listas e hashes só no anexo; teste de presença por seção |
| CA-7 | todo número com fonte e definição | cada indicador da §8 tem entrada no anexo F; teste que cruza número da página e número da tela dona |
| CA-8 | nada inventado | matrícula, presença e homologação aparecem só em *"o que o GPS não registra"* |
| CA-9 | cronologia coerente | o cenário roda pelos commands, com o relógio na data; recusa = cenário inválido |
| CA-10 | referências e rastreabilidade | cada documento publicado aparece com data e SHA-256 iguais aos de `DocumentoPublicado` e `DocumentoDoResultado` |
| CA-11 | exposição fundamentada | varredura do texto do PDF sem nome, CPF ou protocolo do banco de teste; fato não público só por Perfil (R-4) |
| CA-12 | compatível com a arquitetura | sem migration, sem dependência, sem permissão nova; `make lint check test-pg` verde |

E quatro critérios próprios:

- **CA-13.** Recusa em 404 a quem não tem a porta.
- **CA-14.** Evento de auditoria com o hash dos bytes entregues.
- **CA-15.** O mesmo número de consultas com 38 e com 380 inscrições.
- **CA-16.** Perfil só de reserva: *"candidatos por vaga"* diz *"não se aplica"*, e nunca 0 nem ∞.

## 15. Estratégia de testes

- **Unidade:** ausências, espécie, frases da visão geral (condição verdadeira e falsa), agregação
  por Perfil e união de listas.
- **Integração:** com o cenário coerente como fixture, cada CA de dado.
- **Autorização:** CA-13.
- **Desempenho:** CA-15.
- **Conteúdo:** CA-2, CA-11 e o template na varredura de vocabulário.
- **Determinismo:** R-10.
- **Cenário demonstrável**, Princípio VI: pelo navegador.

## 16. Dependências identificadas no código

- `interface/views.py::_alteracoes_legiveis`, com antes e depois, a mover para `publicacoes`.
- `inscricoes/application/consulta.py::_contagens`, hoje privada.
- Contagens novas e pequenas: `ResultadoEtapa` por Perfil; recursos por Perfil e espécie.
- `trilha_do_edital` não reúne publicação de resultado, recurso, ordenação e corte (rodada 1). O
  relatório os lê nas fontes, e não amplia a trilha.
- A camada de resultado da `040` (indicadores 7–13) deve consumir a mesma derivação, e não ter
  outra.
