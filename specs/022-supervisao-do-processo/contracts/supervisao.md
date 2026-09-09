# Contrato — Supervisão do Processo

A feature expõe **uma rota de leitura** na interface administrativa. Não há API pública, não há
comando, não há formulário. Este contrato descreve o que a rota devolve, a quem, e o que ela recusa.

---

## 1. A rota

| | |
|---|---|
| Método | `GET` |
| Alvo | a supervisão de **um** Processo Seletivo |
| Efeito colateral | **nenhum** — nem escrita, nem trilha de auditoria |
| Idempotência | total; duas leituras seguidas produzem a mesma página, salvo mudança de fato |

**Por que não gera evento de auditoria.** A trilha registra ato sensível, e ler um agregado do
próprio Processo que se preside não é ato: nenhuma das telas de leitura existentes registra, e
registrar aqui inflaria a trilha com o que ninguém audita.

---

## 2. Autorização

| Condição | Resposta | Requisito |
|---|---|---|
| Presidência ativa deste Processo | 200, página completa | `FR-002` |
| Permissão sistêmica de gerir comissão, mesmo escopo | 200, página completa | `FR-002` |
| Escopo institucional diferente | **404 uniforme** | `FR-003` |
| Sem vínculo e sem permissão | **404 uniforme** | `FR-003`, `SC-012` |
| Processo inexistente | **404 uniforme** | `FR-003` |

As **três** últimas linhas devolvem **a mesma resposta**. Distinguir "não existe" de "você não pode"
diria a quem não alcança que o Processo existe.

---

## 3. O que a página entrega

### 3.1 Pulso — presente sempre

| Elemento | Condição | Requisito |
|---|---|---|
| Total de inscrições submetidas no Processo | sempre | `FR-010` |
| Total de rascunhos, como grandeza distinta | sempre | `FR-012` |
| Desdobramento por Edital, com o Edital nomeado | sempre | `FR-011`, `FR-020` |
| Submetidas nas últimas 24 horas, **no Processo** | havendo período em curso | `FR-013` |
| Série diária de submissões, **uma por Edital** | havendo período declarado | `FR-014`, `FR-015` |
| Equivalente textual da série | sempre que houver série | `FR-016`, `UX-008` |
| Período de inscrições e tempo restante, por Edital | havendo Evento marcado | `FR-019` |
| Próximos marcos, por Edital, em ordem, sem os cancelados | havendo cronograma | `FR-021` |
| Declaração de ausência de período | quando nenhum Edital tem período em curso | `FR-018` |
| Declaração de cronograma ausente | por Edital sem cronograma ou sem período | `FR-022` |
| Instante da leitura | sempre | `FR-009` |

**Nunca entregue:** percentual de avanço de inscrição (`FR-017`), percentual global do Processo,
data apresentada como sendo do Processo (`FR-020`), carga por membro (`FR-034`), e **nenhuma
identificação de candidato** — nome, CPF ou protocolo (`FR-004a`).

**O Pulso não é suprimido por alcance** (`FR-004a`). A supressão silenciosa vale para os sinais, que
têm destino; os agregados do Pulso não têm destino nem dado pessoal, e a base que os autoriza é a do
próprio Processo. É a proibição acima que sustenta esta permissão: se um dia o Pulso passar a exibir
identificação de candidato, esta linha cai junto.

### 3.2 Atenção — presente apenas quando há

| Sinal | Condição de emissão | Medida | Destino |
|---|---|---|---|
| `UX-001` | Etapa sem Evento vinculado | — | composição do Edital |
| `UX-002` | `status` declarado incompatível com a posição temporal | — | cronograma do Edital |
| `UX-003` | Etapa com inscrição carente de avaliador | carentes / submetidas | distribuição da Etapa |
| `UX-004` | ato vigente confirmado obsoleto | — | ordenação do marco |
| `UX-005` | recurso pendente com a comissão inteira impedida | — | recursos do Edital |

| Situação | Resposta | Requisito |
|---|---|---|
| Nenhum sinal | uma linha declarando ausência | `FR-025`, `SC-011` |
| Sinal cujo destino o ator não alcança | sinal ausente, sem menção | `FR-004`, `SC-013` |
| Sinal fora dos cinco | **não existe** | `FR-024`, `D-002` |
| Percentual sem par | **não existe** | `FR-032` |

---

## 4. Encaminhamento

| Regra | Requisito |
|---|---|
| Cada sinal conduz à tela da feature dona | `FR-035` |
| O destino aplica a própria autorização, e a supervisão não a antecipa como permissão | `FR-036` |
| A supervisão **não** lista os registros que o sinal conta | `FR-037`, `D-009` |
| Na dona, o recorte existente permanece o caminho — os números são o filtro | `D-009` |

**O que "não antecipa" significa.** A supervisão decide **se oferece** o destino consultando o
alcance (`FR-004`); quem **recusa** continua sendo a tela de destino. É a mesma separação que o
catálogo de ações do Edital já pratica: desabilitação é previsão, não autorização.

---

## 5. O que este contrato proíbe

| Proibição | Requisito |
|---|---|
| Qualquer escrita originada na supervisão | `FR-006` |
| Estrutura persistente nova — tabela, coluna, migration | `FR-007`, `SC-014` |
| Segunda derivação do conjunto de atos do Edital | `FR-008` |
| Estado de Etapa (aberta, encerrada, atrasada, bloqueada) | `D-003` |
| Alterar a semântica declarada do estado de um Evento | `FR-023`, `D-004` |
| Iterar o guardião individual de impedimento por par | `FR-031`, `D-008` |
| Afirmar impossibilidade de julgamento | `FR-030a` |
| Classificar desempenho de membros | `FR-034` |

---

## 6. Contrato de leitura assistiva

| Exigência | Requisito |
|---|---|
| A série tem equivalente textual com os mesmos valores | `FR-016`, `SC-015` |
| Nenhuma informação depende exclusivamente de cor | `UX-008` |
| Conteúdo largo rola no próprio contêiner; o corpo da página não rola na horizontal | `FR-016` |
| Cada região é anunciada como região, com título próprio | `UX-006` |
