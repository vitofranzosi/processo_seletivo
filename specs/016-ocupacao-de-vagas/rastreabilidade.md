# Rastreabilidade — Ocupação de Vagas (`016`)

Cada requisito desta feature contra o teste que o prova. **Medido, e não afirmado**: a tabela foi
gerada varrendo `backend/tests/**/*.py` pelos identificadores, e é a mesma varredura que
`tests/test_citacoes_de_requisito.py` faz no sentido contrário — ela reprova citação para requisito
que nenhuma spec define; esta responde pelo requisito que teste nenhum cita.

**Por que a matriz existe separada dos artefatos.** A `T062` foi escrita depois de a revisão da US5
apontar que a contagem "N de M tarefas" não diz nada sobre cobertura: tarefa concluída é trabalho
feito, e requisito coberto é afirmação verificada. São duas medidas, e confundi-las foi o que
produziu, três vezes nesta feature, um relatório mais otimista que o repositório.

**Cobertura: 39 de 39.** Dez requisitos chegaram ao fim da implementação provados por teste que
**não os citava** — a prova existia, o rótulo não. Eles estão marcados com ▲ abaixo, porque a
diferença importa: rotular depois é registro, e teria sido defeito silencioso se a matriz não
tivesse sido feita.

## Requisitos funcionais

| Requisito | O que exige | Onde é provado |
|---|---|---|
| `FR-239` ▲ | as **quatro** quantidades por recorte | `integration/ocupacao/test_leitura.py` |
| `FR-239a` | publicada inalterada por movimento | `unit/ocupacao/test_soma_constante.py` · `unit/ocupacao/test_apuracao.py` · `integration/ocupacao/test_reversao.py` |
| `FR-240` | publicada lida da **linha** do quadro | `unit/ocupacao/test_apuracao.py` |
| `FR-241` | ampla é a linha geral; a Modalidade declarada é idêntica a ela | `unit/ocupacao/test_apuracao.py` |
| `FR-242` | sem quadro publicado, recusa — e ausência não é zero | `integration/ocupacao/test_emissao.py` |
| `FR-243` | recusa sobre ordem não vigente | `integration/ocupacao/test_reversao.py` |
| `FR-244` | apuração reproduzível | `unit/ocupacao/test_apuracao.py` · `integration/ocupacao/test_emissao.py` |
| `FR-245` | o Edital pode declarar reversão; ausência é "não reverte" | `integration/ocupacao/test_reversao.py` |
| `FR-246` | a reversão vai da Modalidade para a linha geral | `integration/ocupacao/test_reversao.py` |
| `FR-247` | soma constante sob reversão | `unit/ocupacao/test_soma_constante.py` · `integration/ocupacao/test_reversao.py` |
| `FR-248` | origem, destino, quantidade e causa registrados | `integration/ocupacao/test_reversao.py` |
| `FR-249` | a espécie do gatilho é declarada | `unit/editais/test_reversao_declarada.py` |
| `FR-250` | conteúdo publicado: degrau, leitura anterior, documento, Retificação | `unit/editais/test_reversao_declarada.py` · `contract/test_documento_publicado.py` · `interface/test_retificar_reversao.py` |
| `FR-251` | declarada sem espécie, publicação recusada | `unit/editais/test_reversao_declarada.py` · `unit/ocupacao/test_reversao.py` |
| `FR-252` | quem ocupa pela ampla não é computado na reservada | `unit/ocupacao/test_apuracao.py` · `integration/ocupacao/test_concomitancia.py` |
| `FR-253` ▲ | a vaga reservada **permanece** no recorte reservado | `integration/ocupacao/test_concomitancia.py` |
| `FR-253a` ▲ | ocupadas não excede efetivas | `unit/ocupacao/test_apuracao.py` |
| `FR-254` ▲ | a ocupação é registrada pela ampla | `integration/ocupacao/test_concomitancia.py` |
| `FR-255` | o déficit é entregue à `014` como causa | `integration/ocupacao/test_causar_faixa.py` |
| `FR-256` | déficit zero recusa faixa seguinte | `integration/ocupacao/test_causar_faixa.py` · `interface/test_ocupacao.py` |
| `FR-257` | a `016` não seleciona, ordena, desempata nem convoca | `test_dependencia_da_ocupacao.py` (prova de import) · `test_vocabulario_da_ocupacao.py` |
| `FR-258` ▲ | nenhuma superfície afirma convocação, aceite ou matrícula | `test_vocabulario_da_ocupacao.py` |
| `FR-259` | cada número rastreável a ato, versão e movimentos | `integration/ocupacao/test_auditoria.py` · `integration/ocupacao/test_leitura.py` |
| `FR-260` | nada alterado nem excluído; correção é sucessão | `unit/ocupacao/test_apuracao_append_only.py` · `integration/ocupacao/test_emissao.py` |
| `FR-261` | ler não apura | `integration/ocupacao/test_leitura.py` · `interface/test_ocupacao.py` |
| `FR-262` | a anterior fica sucedida e legível | `integration/ocupacao/test_auditoria.py` · `integration/ocupacao/test_emissao.py` |
| `FR-263` | obsolescência com causa nomeada | `integration/ocupacao/test_obsolescencia.py` · `integration/ocupacao/test_causar_faixa.py` |

## Critérios de sucesso

| Critério | Onde é provado | Ressalva |
|---|---|---|
| `SC-078` ▲ | `interface/test_ocupacao.py` | o teste cobre **dois** recortes numa tela; o Perfil de três listas do critério é o Cenário 1 do [quickstart](./quickstart.md), percorrido na `T065` |
| `SC-079` | `unit/ocupacao/test_apuracao.py` · `unit/ocupacao/test_soma_constante.py` | os números 28 + 10 + 2 e o saldo 7 são os do teste, por construção |
| `SC-080` ▲ | `integration/ocupacao/test_reversao.py` | o teste prova que nenhum caminho **de aplicação** cruza Perfil; *"em nenhum percurso da interface"* é a `T065` |
| `SC-081` | `integration/ocupacao/test_causar_faixa.py` | a metade de domínio do ciclo do 77/2026; *"pela interface"* é a `T065` |
| `SC-082` | `performance/test_ocupacao.py` | 7 Perfis × 3 listas × 1.000 participantes, contra a emissão da ordem no mesmo volume |
| `SC-083` ▲ | `integration/ocupacao/test_auditoria.py` | prova a existência da proveniência; a exibição dela é a `T058` |
| `SC-084` | `integration/ocupacao/test_obsolescencia.py` · `integration/ocupacao/test_reversao.py` | — |

## Requisitos de interface

| Requisito | Onde é provado |
|---|---|
| `UX-031` | `interface/test_ocupacao.py` · `integration/ocupacao/test_leitura.py` |
| `UX-032` | `interface/test_ocupacao.py` · `integration/ocupacao/test_leitura.py` · `integration/ocupacao/test_emissao.py` |
| `UX-032a` | `interface/test_ocupacao.py` · `integration/ocupacao/test_leitura.py` |
| `UX-033` | `interface/test_ocupacao.py` |
| `UX-034` ▲ | `test_vocabulario_da_ocupacao.py` |

## As decisões, e onde cada uma vive

`D-001` a `D-005` são herdadas e não geram teste próprio. As três do usuário, sim:

| Decisão | Onde vive |
|---|---|
| `D-006` — a cascata do 14/2026 é alvo derivado da `014` | fora desta feature, por decisão: nenhum teste da `016` a exercita |
| `D-007` — duas espécies de gatilho, declaradas pelo Edital | `unit/ocupacao/test_reversao.py` · `unit/editais/test_reversao_declarada.py` |
| `D-008` — a apuração é ato append-only por recorte, com sucessão | `unit/ocupacao/test_apuracao_append_only.py` · `integration/ocupacao/test_emissao.py` |

## O que esta matriz não mede

- **Que o teste seja bom.** Ela responde "existe teste que cita", não "a asserção é forte". Dois
  testes fracos meus foram substituídos nesta feature antes de entrar, e a matriz teria ficado
  verde com os dois.
- **O caminho conduzido pela interface.** Quatro critérios acima dependem dele, e é a `T065`.
- **Contrato de API.** Não há nenhum nesta feature além da declaração da reversão no `openapi.yaml`
  da `001`: a §2 do [contrato](./contracts/ocupacao.md) é de **aplicação**, e descreve o que os
  selectors devolvem. A `T061` pedia acrescentar três endpoints que não existem, e foi encerrada
  convergindo a seção.
- **Requisito que nenhum teste cita porque nenhum teste o cobre.** Não há nenhum agora, mas a
  varredura mede citação, e citação é o que o autor escreve. A `FR-250` é o exemplo de como isso
  falha: ela exige a declaração como conteúdo publicado *"com presença no documento"*, e a forma
  publicada não a conferia — o defeito ficou de pé com a `FR-250` citada por quatro testes, e quem
  o encontrou foi o confronto entre o contrato e a transcrição (`T060`), não esta matriz.
