# Inventário — o subsistema de classificação do GPS

**Data:** 07/11/2026 · **Base:** `main` em `f5fc1c5d` · Entrega preliminar do
[estudo de caso](../estudo-classificacao-demonstrativa-2026-11-07.md), feita antes de escolher o cenário.

Os caminhos são relativos a `backend/processo_seletivo/`. **Estado** indica três coisas:

- **implementado:** o código existe, e o caso o exercitou ou um teste o cobre;
- **parcial:** há o mecanismo, com lacuna nomeada;
- **ausente:** não há código.

## 1. Configuração (antes de publicar)

| Recurso | O que representa | Como se configura | Aplica-se a | Restrições | Dependências | Exemplo | Estado |
|---|---|---|---|---|---|---|---|
| **Etapa de Avaliação** | Um momento do certame (prova, entrevista, análise) | Composição › Etapas de Avaliação. Modelo em `editais/models/etapas.py`; validação em `editais/domain/etapas.py` | Todos os Perfis do Edital | Peso > 0; mínima ≥ 0; mínima ≤ máxima; ordem e identidade únicas | Evento do Cronograma (opcional, só datas) | "Prova escrita", 0–100, mín. 60, peso 3 | implementado |
| **Forma da conclusão** | `PONTUADA` (nota) ou `DECISORIA` (sentido + rótulos) | "Como esta Etapa é concluída" (`avaliacoes/domain/formas.py`) | Cada Etapa | Decisória precisa ser eliminatória; senão `REGRA_INSUFICIENTE` (`resultados/domain/regra.py`) | — | "Análise dos requisitos", Deferido/Indeferido | implementado |
| **Caráter** | Eliminatória e/ou classificatória (caixas independentes) | Etapas | Cada Etapa | Pontuada eliminatória sem mínima → `REGRA_INSUFICIENTE`. Mínima em Etapa não eliminatória não elimina ninguém | O marco só aceita Etapa classificatória (`milestone_stage_not_classificatory`) | Currículo: só classificatória | implementado |
| **Nota da Etapa** | Um decimal (7,4) por avaliação | Lançada na mesa (`avaliacoes/application/avaliacao.py`: `gravar`, `concluir`) | Etapa pontuada | **Não há nota por critério (barema).** A Etapa copia a única avaliação (`resultados/domain/regra.py`) | Máxima publicada cobrada na conclusão | 76 | implementado (sem barema) |
| **Avaliações por inscrição** | Quantas leituras independentes | Etapas | Etapa | Mais de 1 → `REGRA_DE_COMBINACAO_AUSENTE`: a Etapa não consolida, e a publicação bloqueia se for eliminatória ou usada por marco (`doc/achado-duas-avaliacoes-sem-regra-de-combinacao.md`) | — | — | **ausente** (combinação) |
| **Peso** | Multiplicador da nota da Etapa no marco | Na Etapa, "opcional até um marco enumerar esta Etapa" | Todos os marcos que enumeram a Etapa | Um peso por Etapa, igual em todos os marcos. Sem peso, a Etapa enumerada bloqueia (`milestone_stage_without_weight`) | Marco | Prova peso 3 | implementado |
| **Dependência (progressão)** | Quem chega a cada Etapa | **Sem campo:** decorre da `order` (`resultados/domain/progressao.py`; `resultados/application/prontidao.py`) | Toda Etapa | 1) eliminado em qualquer anterior sai; 2) a **imediatamente** anterior precisa habilitar, depois de ter Resultado e se puder habilitar (RC-112) | Corte que governa a Etapa (regra 3) | Currículo antes da Prova | implementado |
| **Etapa paralela ou condicional** | Duas Etapas independentes; Etapa só para alguns | — | — | A ordem é total. Não há condição por modalidade nem por resultado | — | — | **ausente** |
| **Marco classificatório** | Uma ordem de um Perfil | Composição › Classificação, cartão por marco (`interface/templates/interface/_marco.html`; modelo `editais/models/perfis.py`) | Um Perfil | Só Etapas classificatórias; código único no Perfil | Etapas, fatos, quadro | "Classificação para a entrevista" | implementado |
| **Produção da ordem** | Pela pontuação ou por sorteio | "Como a ordem deste marco é produzida" | Marco | Declaração obrigatória (`order_production_nao_declarada`) | Sorteio: método publicado | Pela pontuação | implementado |
| **Combinação** | Soma ou média ponderada; normalização pela soma dos pesos | Cartão do marco; **só aparece com 2 ou mais Etapas** (com 1, é derivada) | Marco | Divisor zero recusado; sem nota numa Etapa enumerada a pessoa fica sem posição, nunca zero (`classificacao/domain/combinacao.py`) | Pesos das Etapas | `(CUR + 3·PRO)/4` | implementado |
| **Porta** | Etapa decisória enumerada: não soma, só filtra | Marcar a Etapa decisória no marco | Marco | Marco só com portas tem pontuação nula: um grupo só | — | (não usado: a eliminação anterior já filtra) | implementado |
| **Arredondamento** | Escala 0–4; meio para cima, meio para par, truncar | Cartão do marco | Marco | **Uma vez**, sobre o total | — | 92,666… → 92,67 | implementado |
| **Nota final mínima** | Corte por nota no marco | — | — | — | — | — | **ausente** |
| **Critérios de desempate** | Maior nota numa Etapa; maior ou menor valor de um fato | Cartão do marco: ordem, critério, alvo, "quando o valor não existe" (`classificacao/domain/desempate.py`) | Marco | **Só 3 tipos.** Idade só como fato. O que sobra fica dividido (1, 1, 3); não há ato para "julgar o empate" | Fatos declarados; Etapas (inclusive não enumeradas, desde a 114) | Entrevista › Prova › nascimento | implementado |
| **Fato declarado** | Dado que o candidato informa na inscrição (data ou inteiro) | Perfis › "Fatos exigidos do candidato" | Perfil | Congelado no envio; autodeclarado; não verificado (`inscricoes/models.py`, `ValorDeFato`) | Critério de desempate | Data de nascimento | implementado |
| **Regra de corte** | Quem avança: alvo fixo ou do quadro, suplentes, empate na última posição, Etapa governada, faixa seguinte | Cartão do marco (`classificacao/domain/faixa.py`) | Marco, **aplicada por lista** | Alvo fixo = o mesmo número em cada lista; empate estrito recusa a emissão; Etapa governada não pode ser enumerada pelo próprio marco | Quadro (alvo do quadro) | Fixo 8 → Entrevista; quadro + 2 | implementado |
| **Janela recursal** | Admite, não admite ou não declarada; N dias corridos | Cartão do marco | Marco | Só dias corridos; conta da 1ª publicação do ato (`recursos/domain/janela.py`) | Publicação | 3 dias | implementado |
| **Modalidades** | Listas de concorrência livres (código, nome, regra normativa com percentual e arredondamento) | Perfis | Perfil | O sistema não conhece "PcD/PPI" por nome; "qual é a ampla" é declarado | Quadro | AC, PcD 5 %, PPI 20 % | implementado |
| **Quadro de vagas** | Vagas por lista; linha geral = ampla | Perfis › Quadro de vagas, com sugestão pelo percentual | Perfil | Soma conferida na publicação; a lista declarada como ampla não tem linha própria | Modalidades | 4 / 1 / 1 | implementado |
| **Reversão** | Vaga reservada não preenchida vai à ampla | Perfis: "só quando esgota" / "a quantidade que ficou sem preencher" (`ocupacao/domain/reversao.py`) | Perfil com reservadas | Lista reservada sem inscrito não reverte (`doc/achado-reservada-vazia-nao-reverte.md`) | Ocupação | `ON_BALANCE` | implementado |
| **Cadastro de reserva** | Limite de pessoas além das vagas | Perfis | Perfil | Sem efeito no cálculo; o acréscimo de vagas (097) só em Perfil sem lista reservada | — | limitado em 6 | implementado |
| **Validação antes de publicar** | Impeditivos e avisos | Revisão ("O que falta para submeter"); `editais/domain/validation.py` (`validate_for_publication`) | Edital | Impeditivos `milestone_*`, `tiebreaker_*`, `cut_rule_*`, `profile_without_*`, `vacancy_*`, `stage_result_unreachable` | Todas as etapas da composição | — | implementado |
| **Frases normativas** | O que o documento vai dizer de cada decisão | Revisão (`interface/revisao.py`) e PDF | Edital | Corte fixo: "os N primeiros", sem "de cada lista" | — | — | implementado (com o achado D2) |

## 2. Simulação

| Recurso | O que representa | Como se usa | Restrições | Estado |
|---|---|---|---|---|
| **Prévia da classificação (094)** | O motor oficial sobre candidatos fictícios | Botão "Simular classificação" no cartão do marco → painel lateral; "Explorar classificação e desempate" | 20 fictícios, ou um de 11 casos-limite. Até 4 Etapas com nota. Um marco por vez. Nada gravado. Equivalência com o caminho oficial testada (`tests/integration/classificacao/test_previa_equivale_ao_oficial.py`) | implementado |
| **Prévia por lista e ocupação (095)** | Ordem e corte de cada lista; concorrência simultânea; 1 rodada de ocupação; reversão | Mesmo painel | Sem convocação, desistência, faixa seguinte, cascata; "hipótese" | implementado |
| **Simulação com notas reais** | "E se eu mudar isto, o que acontece com estas pessoas?" | — | — | **ausente** |

## 3. Execução

| Recurso | Comando / tela | Restrições | Estado |
|---|---|---|---|
| Inscrição (rascunho → enviada; documentos; fatos) | Portal; `inscricoes/application/rascunho.py`, `submissao.py` | Não há homologação de inscrição como ato; requisitos são texto | implementado |
| Comissão (presidente, membros) e alocação por Etapa | `/gestao/processos/<id>/comissao`, `alocacoes` | — | implementado |
| Distribuição, rodízio, impedimento | `/gestao/editais/<id>/distribuicao/<etapa>` | Só com o período de inscrições encerrado | implementado |
| Mesa: gravar, concluir, reabrir | `minhas-etapas/…` | Parecer obrigatório abaixo da mínima em Etapa eliminatória, e no desfavorável | implementado |
| Ocorrência (ausência) | `…/distribuicao/<etapa>/ocorrencia` | Sempre "eliminada", com motivo | implementado |
| Consolidação | `…/distribuicao/<etapa>/consolidar`; `resultados/application/consolidacao.py` | A presidência confirma um cálculo, sem digitar nota | implementado |
| Emitir a ordem (por lista), sucessão com motivo | `/gestao/editais/<id>/marcos/<marco>`; `classificacao/application/emissao.py` | Exige confirmação do cálculo; recusa ordem sem nenhum Resultado | implementado |
| Corte, continuação, histórico | `…/marcos/<marco>/corte`; `classificacao/application/corte.py` | Exige ordem vigente não obsoleta; corte obsoleto trava a Etapa governada | implementado |
| Publicação preliminar e definitiva | `…/atos/<ato>/publicar`; `divulgacao/application/publicar.py` | Por marco e lista. Definitiva recusada com recurso pendente ou janela aberta | implementado |
| Publicação de uma Etapa isolada | — | — | **ausente** |
| Recurso: interpor, admitir, instruir, julgar (4 espécies) | Portal `…/recorrer`; gestão `/gestao/recursos/<id>` | Segregação (quem julga não pode ter avaliado, consolidado, emitido ou publicado); não reforma para pior | implementado |
| Apuração de ocupação, sucessão, faixa seguinte, acréscimo | `…/marcos/<marco>/ocupacao`; `ocupacao/application/emissao.py` | "Ocupada" conta titular desde a apuração | implementado |
| Convocação (lote, individual), comunicação, desfechos | `…/marcos/<marco>/convocacao`; `convocacao/application/` | 7 desfechos; a apuração seguinte sai no mesmo ato, salvo quando moveria vaga pela reversão | implementado |
| Documentos na convocação, conferência | `…/convocacao/<id>/documentos` | "Conforme" exige abrir a versão; aceite exige a lista conferida | implementado |
| Formalização, Requerimento de Matrícula, exportação | `/gestao/formalizacao/`, portal `requerimento`, `/gestao/editais/<id>/matriculas` | — | implementado (não exercitado aqui) |

## 4. Achados anteriores que tocam a classificação

| Achado | Situação |
|---|---|
| `doc/achado-duas-avaliacoes-sem-regra-de-combinacao.md` | Validação e aviso feitos; a regra de combinação continua ausente |
| `doc/achado-empate-estrito-tem-tres-leituras.md` | Aberto: tela, documento e motor leem o empate estrito de três jeitos |
| `doc/achado-reabilitado-antes-do-marco-nao-alcanca-o-corte.md` | Aberto |
| `doc/achado-corte-nasce-obsoleto-apos-recurso.md` | Corrigido pela 061 |
| `doc/achado-reservada-vazia-nao-reverte.md` | Aberto (lista sem inscrito) |
| Estudo do sorteio, Q6–Q8 | Aberto: a fila da ampla não exclui quem aceitou a reservada |
