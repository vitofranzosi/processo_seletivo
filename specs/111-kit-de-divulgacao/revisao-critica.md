# Revisão crítica independente

**Data:** 31/10–01/11/2026 · **Sobre:** a primeira versão de `spec.md`, `research.md`, `plan.md`,
`data-model.md`, `contracts/kit.md`, `tasks.md` e `rastreabilidade.md`.

**Como foi feita.** Um revisor sem o contexto da escrita leu os artefatos, o estudo e a POC, e
confrontou cada afirmação com o código da `main` em `4ca16b1d`. O pedido listava nove classes de
defeito:

- duplicação de regra;
- acoplamento com a publicação;
- função sem valor demonstrado;
- excesso sobre o MVP;
- divulgação incorreta;
- divergência entre texto e imagem;
- Retificação de vigência futura;
- autorização;
- custo de dependência.

Foram **26 achados: 3 bloqueantes, 17 importantes e 6 menores**. Todos foram conferidos no código
antes de entrar, e todos mudaram os artefatos. A tabela diz como.

| # | Gravidade | Achado | O que mudou |
|---|---|---|---|
| 1 | Bloqueante | A proveniência lia `ProvenienciaConteudo` pelo caminho exato. É a leitura que `duvidas/domain/origem.py` documenta como errada: a tabela só acrescenta, e Perfil substituído inteiro guarda registro antigo | FR-3408 exige a regra da `070` (`origens`, `acrescimos`), movida para `publicacoes/domain/origem.py` (D-002, T002); três casos novos na T005; cenário 15 |
| 2 | Bloqueante | A ficha no portal importaria `interface/agenda.py` e `interface/relatorio_do_edital.py`, que carrega classificação, convocação e ocupação: portal → interface, contra a própria D-002 | As leituras descem para `publicacoes/application/selectors.py` (D-002, T002); a ficha só importa `vagas_do_conteudo` da interface |
| 3 | Bloqueante | "O mesmo ZIP byte a byte" contradizia o manifesto e as notas, que carregam instantes | FR-3438 em dois níveis: peça e textos publicáveis idênticos em qualquer instante; ZIP idêntico no mesmo instante de referência. US4, SC-1056 e quickstart ajustados |
| 4 | Importante | Host local na peça e na legenda; host na impressão dava falso alarme | FR-3447 e D-020 (regra `_host_local` da `099`); host fora da impressão (FR-3411, D-018); P-9; EC-28 |
| 5 | Importante | "Busque por 01/2026" é ambíguo, porque o número é único só por unidade | FR-3418 com a sigla; EC-24; cenário 16 |
| 6 | Importante | Cancelar depois de exportar não avisava | FR-3445; US3 cenário 5; teste na T014 |
| 7 | Importante | Comparar só com a última exportação escondia material antigo | FR-3439 compara todas, agrupadas por impressão; US3 cenário 4 |
| 8 | Importante | Impressão sem versão: evoluí-la dispararia faixa falsa em massa | FR-3448 e D-018 |
| 9 | Importante | Diff de ofertas sem identidade; a ordem mudava a impressão | `perfil_id` nos campos, ordenados por identidade (FR-3411, D-018); EC-10 ampliado |
| 10 | Importante | Prorrogação seria a terceira cópia da regra; o texto errava quando só a hora muda | `prorrogacao(original, vigente)` extraída **sem mudar** (D-002, T002, com teste de regressão). Conferido depois: a regra da `099` já compara instantes; o erro era do texto da POC, que a FR-3417 e a EC-25 corrigem no kit (T007/T008); cenário 14 |
| 11 | Importante | Regras existentes não usadas: `do_ato`, `vagas_do_conteudo`, `TIPOS_COM_RESERVA`, a numeração por `published_at` | Tabela "O que existe" e FR-3406 as nomeiam; EC-17 ampliado |
| 12 | Importante | O total de vagas contradizia a FR-1607 da `072` sem dizer por quê | Exceção declarada na FR-3425: sempre "N vagas em K opções" |
| 13 | Importante | A manchete livre com filtros deixava passar afirmação não comprovada | Manchete por **lista fechada** derivada da ficha (FR-3427, D-013); o parâmetro vira índice (contrato) |
| 14 | Importante | A FR-3414 era impossível sobre valor literal ("São Marcos", "faixa etária") | A FR-3414 vale para frases fixas, composição e manchete; o valor literal é apontado (EC-26) |
| 15 | Importante | A P-2 subestimava a exposição: Retificações em curso, pendências, participantes, Agenda e prévia | P-2 ampliada e passa a bloquear a **atribuição do papel a qualquer pessoa**; opção de entrada própria registrada; R-3 do plano |
| 16 | Importante | O papel novo quebra `len(PAPEIS) == 8` e cruza `LIMIAR_DA_BUSCA = 8` | T004 os atualiza e decide o limiar; plano, tabela de integração |
| 17 | Importante | O evento cru na trilha, como transição, diluindo os atos | FR-3436: não é transição, tem rótulo e não conta no relatório da trilha; T015, T016 (guardião estendido a `interface/`) |
| 18 | Importante | Precedente errado na D-005 e consulta não especificada | D-005 cita o `APLICAR_A_TODOS`; data-model com a consulta e o índice |
| 19 | Importante | Tela, prévia e exportação são três requisições, e podiam divergir | FR-3446 e D-019: a impressão conferida viaja, e a mudança dá 409; EC-27 |
| 20 | Importante | O SVG não embutia a fonte e desenharia diferente fora do GPS | FR-3422 e D-021: fonte embutida (OFL); política própria do anexo (D-014); T022 |
| 21 | Menor | Medida sobre texto normalizado, desenho do texto cru; quebra partindo palavra | FR-3430 (desenha o normalizado), FR-3429 (palavra partida não cabe), D-009 |
| 22 | Menor | Ação pela ficha no detalhe; resposta ambígua para não publicado | FR-3401 pelo estado; FR-3402 e contrato com 409, como a `099` |
| 23 | Menor | EC-4 promovia inscrição de Processo encerrado | P-8; enquanto não respondida, sem material |
| 24 | Menor | Teto de quatro na peça e de cinco na legenda | Teto único de quatro (FR-3425) |
| 25 | Menor | Lacunas entre matriz, tarefas e D-001; FR-3434 sem critério; nomes de pasta iguais; teste depois do código | Matriz e tarefas reescritas; D-001 realinhada; FR-3434 com 35% da folga; `tests/fixtures/kit_referencias/`; testes antes do código, inclusive a autorização (T010 antes da T011) |
| 26 | Menor | Renomear `_quebrar` tocava o compositor do ato | Apelido público, sem renomear (D-009, T019). O grupo opcional de dependência sugerido **não** foi adotado: a peça em produção precisaria do grupo instalado, e a D-007 já condiciona a dependência à verificação |

## O que a revisão confirmou

- A arquitetura (ficha única, formas fechadas, trilha sem tabela, chave de ambiente) é adequada.
- A D-005 se sustenta com os ajustes dos achados 17 e 18.
- O incremento A pode começar depois destas correções.

## O que continua do usuário

As pendências **P-1 a P-9** da spec. A P-2, ampliada aqui, é a de maior consequência: enquanto não for
respondida, o papel não é atribuído a ninguém.
