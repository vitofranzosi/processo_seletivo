# Reavaliação B — esforço humano para operar um Edital publicado

Código lido: worktree `auditoria-consolidacao-seletivo-8dba99`, HEAD `f77e8aa9` (= `origin/main` `79aeb847` + merge da branch de auditoria, só docs). Somente leitura. Caminhos relativos a `backend/processo_seletivo/` salvo indicação.

Notação de escala: C candidatos (inscrições), P Perfis/polos, R recortes (listas de concorrência por Perfil), E Etapas, M marcos, A avaliadores, Rc recursos, Cv convocados, D documentos exigidos por inscrição.

## 0. Mapa de rotas operacionais (interface/urls.py)


Toda a condução pós-publicação se endereça por uma de seis chaves, e é isso que determina a escala:

| Chave da rota | Telas | Consequência de escala |
|---|---|---|
| **Processo** | comissão, alocações, supervisão (`interface/urls.py:171-185`, `:29-33`) | O(1) por Processo |
| **Edital × Etapa** | distribuição, consolidação, ocorrência, impedimentos, resultados (`interface/urls.py:188-235`) | O(E) telas; dentro delas, páginas de 25 |
| **Edital × marco, recorte em `?lista=`** | ordenação, corte, ocupação, convocação, sorteio (`interface/urls.py:238-375`) | O(Σ_P M·R) — cada recorte é uma visita e um ato |
| **Edital × marco × ato** | prévia/publicação do resultado (`interface/urls.py:379-388`) | uma publicação **por ato**, e há um ato por recorte (`divulgacao/models.py:52-56`: "Três atos raiz num marco exigem três publicações") |
| **peça** | recurso: admitir, instruir, julgar (`interface/urls.py:403-418`) | O(Rc) |
| **inscrição** | Mesa, atestado (`interface/urls.py:338-342`, `:423-444`) | O(C·E·k) |

Os marcos moram **dentro do Perfil** (`classificationMilestones` de cada `profile`, lido em `interface/views.py:2940-2966`), de modo que M não é "marcos do Edital", é "marcos de cada Perfil": num Edital de 16 Perfis com um marco cada, são 16 marcos, e cada um multiplica pelas listas do Perfil.

## 1. Candidato (portal) — autosserviço, custo zero para a gestão

| Passo | Ação humana | Unidade | Evidência |
|---|---|---|---|
| Acesso | e-mail → código de 6 dígitos (`identidade/domain/codigo.py:20`) → (1ª vez) CPF/nome | por pessoa | `portal/views.py:583-615` (solicita e envia código), `:640-680` (confere), `:817-890` (reconcilia CPF), `:1217-1221` (núcleo nome/CPF pedido só na 1ª inscrição) |
| Inscrição | POST "inscrever" abre rascunho; tela única com telefone e Modalidade | por inscrição | `portal/views.py:1207-1229`, `:1234-1330` |
| Documentos | **um POST por arquivo**, persistido na hora | O(D) por inscrição | `portal/views.py:1753-1782` ("Um requisito, uma requisição") |
| Revisão e envio | duas declarações + enviar | 1 | `portal/views.py:1961-2060` |
| Comprovante | tela + PDF | 1 | `portal/views.py:2140-2250` |
| Acompanhamento, resultado, convocação | leitura | — | `portal/views.py:1409-1478`, `:1835-1960`, `:2252-2330` |
| Recurso | formulário com objeto + fundamentação | por objeto atacável | `portal/views.py:1480-1556` |
| Requerimento de matrícula | formulário (CEP etc.) | por pessoa, na inscrição ou na convocação, conforme o Edital declara (`requerimentos/domain/disponibilidade.py:74-92`) | `portal/views.py:2542-2745` |

Para a gestão, o candidato só gera trabalho **indireto**: cada inscrição vira linhas nas filas da Etapa, cada recurso vira uma peça, cada convocado vira um ciclo de convocação. A gestão não digita nada do candidato. Um ponto de atrito conhecido: o código de acesso depende de correio (no nativo, sai no terminal — `CLAUDE.md`), e não há na gestão nenhuma ferramenta de atendimento ("reenviar código", "destravar inscrição") — o que chega por telefone/e-mail é resolvido fora.

## 2. Comissão e alocação — lote bem resolvido

- **Comissão** (`interface/views.py:4432-4563`): inclusão individual (`acao=incluir`, com conferência, `:4444-4464`) **e em lote** (`acao=incluir_lote`, `:4465-4502`), com a conferência da lista inteira ("conferir quarenta um a um não é conferir", `:4466-4468`). Custo: O(1) submissões por Processo, digitando A identificadores (não há diretório institucional — `:4466-4468`).
- **Alocação** (`interface/views.py:4566-4640`): matriz **membro × Etapa** com salvar a matriz inteira (`acao=distribuir`, `coluna_todos`/`coluna_nenhum`, `:4578-4593`), inclusão em lote (`todos`, `:4595-4612`) e remoção em lote (`:4613-4620`). Custo: O(1) a O(E) submissões.
- **Sem Perfil/polo**: a alocação é `Etapa × avaliador` (`comissoes/models.py:76-83`, RC-61/DP-11). Não há como dizer "esta pessoa avalia só o polo X".
- **Remover membro** desativa em cascata as alocações, num clique sem prévia (`interface/views.py:4512-4519`; RC-66).

## 3. Distribuição — proposta automática existe, mas cega a Perfil

- **Rodízio por menor carga** existe: `propor_rodizio`/`confirmar_rodizio` (`interface/views.py:5081-5104`; `avaliacoes/application/distribuicao.py:445-500`). Regra: "para cada inscrição, na ordem do protocolo, as vagas que faltam vão para quem está com menos carga projetada entre as pessoas selecionadas" (`avaliacoes/domain/rodizio.py:17-21`). Não grava até a confirmação, que confere assinatura (`:1-15`). Custo: **2 submissões por Etapa** (propor, confirmar) — O(E), independente de C. A própria docstring registra o antes: "600 inscrições com dupla avaliação custavam 24 telas e cerca de 700 marcações" (`avaliacoes/application/distribuicao.py:12-14`).
- **O rodízio não conhece Perfil**: parte de todas as submetidas participantes (`avaliacoes/application/distribuicao.py:394-419`), sem filtro de Perfil; e a lista da distribuição filtra por cobertura, avaliador e prontidão (`interface/templates/interface/distribuicao.html:110-112`, `:292-303`), nunca por Perfil. Quem quiser "banca do polo X avalia o polo X" (28/2026) ou "banca de cada curso avalia os títulos do seu curso" (140/2025) cai no **caminho manual**: seleção de inscrições por página × avaliadores (`distribuir`, `interface/views.py:5105-5117`), sem filtro que isole o Perfil — ou seja, precisaria reconhecer o Perfil de cada linha a olho, e a tabela não tem coluna de Perfil (`distribuicao.html:343-347`: Participante, Atribuídas, Concluídas, Prontidão, Quem avalia).
- **Impedimento** é por par avaliador × inscrição, com dois passos (alcance e confirmação, `interface/views.py:4689-4735`). O(impedimentos), tipicamente pequeno.
- Recusa enquanto o período de inscrição está aberto (`interface/views.py:5165-5172`, `recusa_por_inscricoes_em_curso`): a distribuição só começa depois do encerramento — não há avaliação em fluxo contínuo.

## 4. Avaliação na Mesa — o custo humano irredutível, e unitário por construção

- **Unidade: inscrição × Etapa × avaliação prevista.** Cada Atribuição é uma tela (`interface/views.py:5221-5285`, `mesa_inscricao.html`). Nela: abrir cada documento (painel lateral ou aba, `mesa_inscricao.html:96-151`), escolher sentido favorável/desfavorável (`:260-271`), digitar **uma** pontuação (`:278-289`) e o parecer (`:300-301`), e "Concluir" — que já leva à próxima pendente (`interface/views.py:5337-5358`, "numa Mesa de 230 são 230 cliques para dizer 'continuo trabalhando'"). O avaliador não volta à lista entre uma e outra (`proxima_pendente`, `:5267-5269`).
- **O que a tela já poupa**: marca de "aberto" por documento, tirada da trilha (`interface/views.py:5282-5310`); foco inicial no primeiro documento quando ainda não se leu nada (`:5262-5266`); lista exigida gravada no envio, com "não se aplicam" (`mesa_inscricao.html:158-165`).
- **O que ela não tem, e não terá por decisão**: juízo por documento (`mesa_inscricao.html:70-76`: "a Avaliação é uma só por inscrição… não há veredito por documento"; RC-56) e **barema** — a pontuação é um número só (`avaliacoes/domain/pontuacao.py`; zero ocorrências de "barema" no código, RC-64). Num Edital de prova de títulos o avaliador soma os itens **fora** do sistema e digita o total; a conferência "item a item contra a expectativa do candidato" que o 140/2025 exige (Anexo IV, coluna "Conferência da pontuação pela banca") não tem onde morar.
- **Parecer obrigatório** quando desfavorável em Etapa eliminatória (`avaliacoes/domain/pontuacao.py:84-137`) — o texto livre é custo por eliminado.
- **Dupla leitura** (k=2) distribui, mas a consolidação recusa a Etapa inteira sem regra de combinação (DP-06; `resultados/domain/regra.py:71-76`), e a `046` passou a impedir a publicação nesse caso. Na prática k=1.
- Escala: **O(C_etapa × D)** leituras de documento e **O(C_etapa)** conclusões, por Etapa. É o termo dominante em todo Edital que tem análise humana, e nenhuma automação o reduziria sem mudar o que o Edital manda fazer — o que o sistema pode fazer é não somar custo em volta dele.

## 5. Consolidação e ocorrência — lote, mas em páginas de 25

- Consolidar pende da **seleção** na tela da distribuição (`distribuicao.html:403-419`, `formaction` para `consolidar-resultados`), e a seleção é da **página**: `POR_PAGINA = 25` (`avaliacoes/application/selectors.py:33`), e a caixa "selecionar todas" é "desta página" (`interface/static/interface/selecao.js:1-5, 29`). O comando exige a lista explícita de ids (`resultados/application/consolidacao.py:247-277`). Há filtro "prontas para consolidar" (`distribuicao.html:110-112`), de modo que o laço é: filtrar prontas → marcar a página → "Consolidar as selecionadas" → conferir o alcance (`consolidacao_confirmar.html`) → confirmar (`interface/views.py:4810-4874`) → repetir. **⌈C/25⌉ rodadas de ~4 cliques por Etapa.** Com 600 inscrições, 24 rodadas.
- A mesma forma na **ocorrência** (quem não foi avaliado — ausente, desistente): `Paginator(pendentes, 25)` (`interface/views.py:4946-4947`), com motivo e confirmação em dois passos (`:4877-4968`).
- Não há "consolidar todas as prontas da Etapa". O argumento da docstring (irreversível, V1 sem anulação — `interface/views.py:4810-4826`) é sobre confirmar, não sobre paginar: a confirmação já declara o alcance e poderia declarar 600 tão bem quanto 25.

## 6. Sorteio — por marco, com um ato por recorte

- Uma tela por marco (`interface/views.py:8049-8100`) lista os recortes "para que ninguém publique dois e esqueça o terceiro" (`:8057-8058`). Por recorte: **publicar a relação** (`:8166-8196`; botão por recorte, `sorteio.html:389-402`) e **realizar** (`:8255-8287`; `sorteio.html:374-379`). Por marco: **observar a ocorrência** na fonte (`:8199-8252`), idempotente por (fonte, referência) (`sorteios/application/ocorrencia.py:42-43`) — o mesmo concurso serve a todos os marcos, mas cada tela de marco pede o seu POST.
- **Recortes do sorteio ≠ recortes da ocupação**: o sorteio oferece "todos os inscritos" + **toda** Modalidade, inclusive a AC declarada (`sorteios/application/previa.py:43-50`); a ocupação exclui a AC declarada (`editais/domain/recortes.py:1-14`). RC-73/FR-491a. Num Perfil com AC/PPI/PcD declaradas, o sorteio mostra 4 recortes, dos quais 1 é excedente.
- Habilitação: se o método declara `qualifyingStageId`, entram só os HABILITADA na Etapa (`sorteios/application/habilitacao.py:15-30`); se não declara, entram todas as submetidas — e o portal já recusa envio sem os documentos obrigatórios (`inscricoes/application/submissao.py:161-169, 216-227`). Para o 78 e o 28, cuja "habilitação" é "dados completos e documentação anexada", **a triagem humana de todos os inscritos pode ser dispensada** sem perder nada que o Edital pede — desde que quem compõe saiba disso.
- Escala: O(M_sorteio) observações + **O(Σ R_sorteio) relações e O(Σ R_sorteio) realizações**, num evento transmitido ao vivo.

## 7. Ordenação, corte e divulgação — o laço marco × recorte

- **Ordenação**: uma tela por (marco, recorte), com o recorte em `?lista=` (`interface/views.py:5757-5770`), e emissão em dois passos — prévia do alcance e confirmação (`:6002-6105`). A navegação entre recortes do marco existe (`_navegacao_do_recorte`, `:5729-5753`), mas o ato é um por recorte.
- **Corte**: idem, uma tela e um POST por recorte (`interface/views.py:6233-6317`, `:6769-6796`); "faixa seguinte" por recorte (`:6799-6828`).
- **Divulgação**: uma publicação **por ato**, e o ato é por recorte (`divulgacao/models.py:52-56`, constraint `uq_publicacao_raiz_por_marco_e_lista` em `:96-100`). Cada publicação: abrir a prévia (`interface/views.py:6925-6997`), escolher natureza (preliminar/definitiva) e autoridade signatária, confirmar (`:7029-7064`). Preliminar e definitiva são duas publicações; um recurso deferido que sucede a ordem pede nova publicação daquele recorte.
- O Edital real divulga **um** "Resultado preliminar" com todas as listas; o sistema produz Σ(P·M·R) documentos, cada um com seu PDF (`divulgacao/application/publicar.py:361-376`).
- Escala: **O(Σ_P M·R) emissões × 2 passos**, **O(Σ_P M·R) cortes**, **O(Σ_P M·R × naturezas) publicações**.
- Onde se entra: a página do Edital lista cada Perfil × marco com os destinos ordenação/sorteio, corte, ocupação e "divulgar" por ato vigente (`interface/views.py:2846-2967`). Num Edital de 16 Perfis são 16 blocos, e os recortes só aparecem **dentro** de cada tela.

## 8. Recursos — por peça, bem resolvido, com cauda a jusante

- Lista por Edital, filtrável por situação (`interface/views.py:7500-7525`). Por peça: **admitir** com motivo e assinatura do estado (`:7938-8002`), **instruir** opcional (`:7816-7868`), **julgar** com espécie, motivação e — na correção fixada — pontuação e sentido (`:8005-8046`). O julgamento grava a decisão e o Resultado sucessor na mesma transação (`recursos/application/julgar.py:1-35`).
- A cauda do deferimento não é automática, por desenho: o Resultado novo torna obsoleta a ordem dos recortes que o marco lê (`interface/supervisao.py:788-816`), e isso pede **reemitir e republicar** aquele recorte (§7). A supervisão avisa (UX-004), mas o sinal leva à ordenação **sem** `?lista=` (`interface/supervisao.py:986` → `:1214-1217`), e a tela sem `?lista=` abre a ampla (`interface/views.py:5760-5763`): o sinal do recorte PPI aterrissa no da AC.
- Escala: **O(Rc)** peças × 2–3 atos com texto, + O(recortes alcançados) reemissões e republicações.

## 9. Ocupação e convocação — o laço mais fino do sistema: por pessoa, com texto

- **Apuração**: uma por recorte (`interface/views.py:6420-6444`; tela por marco, `:6320-6362`). Toda mudança de fato a torna obsoleta — ordem sucedida, corte novo, quadro retificado, movimento de vaga, e **qualquer desfecho de convocação** (`ocupacao/application/selectors.py:67-163`, a quinta causa, "efeito posterior") — e convocar com apuração obsoleta é recusado (`convocacao/application/convocar.py:100-121`). O laço real é: apurar → convocar → registrar desfechos → **reapurar** → convocar o próximo.
- **Convocar é por inscrição**: o formulário escolhe **uma** pessoa (`convocacao.html:106-146`: `select name="inscricao"`, espécie, vencimento `datetime-local`, fundamento obrigatório); o comando recebe um `inscricao_id` (`convocacao/application/convocar.py:36-52`). E **o titular também é convocado um a um**: "com 40 vagas e 40 titulares habilitados… as 40 pessoas precisam ser chamadas" (`convocacao/application/convocar.py:252-257`). O sistema não calcula prazo em dias úteis (`interface/views.py:6720-6733`, R-004): o vencimento é digitado.
- **Comunicar é por convocação** (`convocacao.html:245-256`; quando o Edital comunica por publicação, o sistema não publica — pede "onde a convocação foi publicada", `:240-253`), e envia e-mail individual quando o Edital declarou essa forma (`convocacao/application/comunicar.py:1-12`).
- **Desfecho é por convocação** (`convocacao.html:259-297`: espécie e fundamento obrigatórios). **Atestado de fato externo** (não acessou o AVA, faltou à 1ª semana, não entregou presencialmente — `convocacao/domain/nomes.py:104-106`) é por inscrição (`convocacao.html:308-329`).
- **A tela da convocação não tem entrada.** Nenhum template da gestão aponta para `interface:convocacao`, exceto o breadcrumb do próprio histórico (`convocacao_historico.html:7`); nenhum destino da página do Edital a inclui (`interface/views.py:2846-2908`: ordenação/sorteio, corte, ocupação, divulgar); a ocupação não a oferece (todos os `href` de `ocupacao.html`: `:5, 6, 66, 113, 149`); a supervisão não tem espécie que leve a ela (`interface/supervisao.py:1213-1236`). Só se chega digitando `/editais/<id>/marcos/<id>/convocacao?lista=<uuid>`.
- **Cadastro de reserva não convoca** (RC-58): com 0 vagas imediatas não há titular, e o suplente precisa de déficit — `SEM_DEFICIT` (`convocacao/application/convocar.py:249-289`); `reserveType`/`reserveLimit` não têm consumidor em `ocupacao/`, `convocacao/` nem `classificacao/` (grep vazio).
- **Ordem de convocação intercalada entre listas** (a tabela de 50 posições do 140/2025, estrutura-editais §140.2) não existe: cada recorte tem a sua fila (RC-59). Quem conduz intercala à mão, recorte a recorte.
- Escala: **O(Cv) × 3 formulários com texto** (convocar, comunicar, desfecho) + **O(desfechos) reapurações** + O(R) telas.

## 10. Exportação para matrícula — por marco, e só com convocação de todo mundo

- Uma exportação por população, escolhida explicitamente (`matriculas/application/populacao.py:1-5`: "Não existe 'exportar tudo'"); duas espécies: **convocados de um marco** (`:114-144`) ou **um resultado definitivo divulgado** (`:147-171`). Cada uma: prévia com lacunas + POST com assinatura (`interface/views.py:4186-4278`).
- A população "resultado" leva **todo** classificado (`SituacaoDivulgada.Situacao.CLASSIFICADA`, `matriculas/application/populacao.py:238-262`; `divulgacao/models.py:160-162`) — num sorteio, isso é todo inscrito habilitado, e não os que cabem nas vagas. Para exportar só quem entra, a única população certa é "convocados", que exige ter convocado **cada** titular (§9).
- O rótulo da população "resultado" é só a data: *"Resultado definitivo divulgado em dd/mm/aaaa"* (`matriculas/application/populacao.py:168`, `matriculas.html:43-45`). Com uma publicação por recorte, num Edital de 7 Perfis × 3 recortes divulgados no mesmo dia, o seletor mostra **21 opções idênticas**.
- Um requerimento faltando recusa o arquivo inteiro do marco, nomeando quem falta (`matriculas/application/populacao.py:291-315`) — quem conduz cobra a pessoa ou registra o desfecho.
- **Só existe para Editais que pedem requerimento** (`matriculas/application/populacao.py:68-103`; `interface/acoes.py:137-147`): o 140/2025 (tutores) não tem exportação nenhuma — a vinculação UAB é toda externa.
- Escala: **O(Σ_P M)** exportações (uma por marco com convocados) — 16 no 140, se tivesse.

## 11. Retificação durante a operação

- Quatro atos com segregação (elaborar, submeter, homologar, publicar — `interface/atos_retificacao.py:47-110`), O(1) por Retificação. O preço está no conteúdo: o catálogo aplica `CAMPOS_PERFIL` "a cada Perfil" (`interface/retificacao.py:62`), e mudar uma remuneração ou um requisito comum a 16 códigos são 16 alterações iguais sem conferência de igualdade (`doc/achado-atribuicoes-repetidas-por-polo.md`).
- A jusante, a Retificação muda a versão vigente, e todo ato de ordenação passa a candidato a obsoleto (`interface/supervisao.py:807-808`); quadro retificado torna a apuração obsoleta (`ocupacao/application/selectors.py:133-141`). A conta volta ao laço marco × recorte do §7 e do §9.

## 12. Encerramento

- Edital e Processo têm um ato cada (`interface/atos.py:118-123`, `interface/atos_processo.py:41-55`). Encerrar o Edital exige só estar publicado (`processos/domain/finalizacao.py:55-60`): **nenhuma** conferência de convocação em aberto, recurso pendente ou apuração obsoleta. Encerrar o Processo não fecha o recebimento dos Editais (RC-118). O(1), e raso.

## 13. Condução — o que o painel poupa, e o que não

- O painel (`processo_detalhe`, `interface/views.py:3941-4028`) e a Supervisão leem as mesmas derivações (`interface/supervisao.py`). Oito espécies (`:487-496`): cobertura (UX-003), avaliação parada (UX-063), ordem obsoleta (UX-004), recorte sem apuração (UX-065), ato sem divulgação (UX-066), recurso impedido/aguardando (UX-005/UX-064), vaga sem quadro (UX-046). Cada sinal nomeia o recorte (`:973-975`) e leva à tela dona.
- **Poupa** a varredura "abrir cada recorte para ver se algo envelheceu": é a leitura por recorte que um humano faria em Σ M·R telas.
- **Não cobre** o que ainda não começou — "Sem ato não há ordem que envelheça… isso não é sinal" (`interface/supervisao.py:842-846`): o recorte que ninguém emitiu não aparece, e a primeira passada por marco × recorte continua sendo de memória. Não cobre prontas para consolidar, sorteio vencido, requerimento pendente (RC-85), convocação vencida sem desfecho, nem apuração obsoleta por desfecho (UX-065 é "sem apuração", não "apuração obsoleta", `:870-900`).

## 14. Mapa dos loops humanos

"Para cada X, o operador faz Y". **Lote** = uma submissão cobre o conjunto; **página** = lote limitado a 25; **unitário** = uma submissão por item.

| # | Para cada… | o operador faz… | Forma | Escala | Evidência |
|---|---|---|---|---|---|
| L1 | membro | inclui na comissão | lote (colar lista) | O(1) | `interface/views.py:4465-4502` |
| L2 | membro × Etapa | aloca | lote (matriz) | O(1) | `interface/views.py:4578-4593` |
| L3 | Etapa | propõe e confirma o rodízio | automático + confirmação | O(E) | `avaliacoes/domain/rodizio.py:17-21` |
| L3′ | inscrição, quando a banca é por Perfil/curso | marca a inscrição para o avaliador certo | **unitário**, sem filtro nem coluna de Perfil | O(C) | `distribuicao.html:292-303, 343-347`; RC-61 |
| L4 | inscrição × Etapa | abre D documentos, decide, pontua, escreve parecer se elimina, conclui | **unitário** (irredutível) | O(C·E·D) | `interface/views.py:5221-5358` |
| L4′ | inscrição de prova de títulos | soma o barema **fora** e digita o total | unitário, fora do sistema | O(C·itens) | RC-64; `mesa_inscricao.html:278-289` |
| L5 | página de 25 prontas | filtra, marca, consolida, confirma | **página** | O(C/25·E) | `avaliacoes/application/selectors.py:33`; `selecao.js:1-5` |
| L6 | página de 25 não avaliadas | registra ocorrência com motivo | página | O(ausentes/25) | `interface/views.py:4946-4947` |
| L7 | marco de sorteio | observa a ocorrência | unitário por marco | O(M) | `interface/views.py:8199-8252` |
| L8 | recorte de sorteio | publica a relação e realiza o sorteio | unitário por recorte | O(ΣR_s) | `sorteio.html:374-402` |
| L9 | marco × recorte | emite a ordem (2 passos) | unitário por recorte | O(ΣM·R) | `interface/views.py:6002-6105` |
| L10 | marco × recorte | emite o corte | unitário por recorte | O(ΣM·R) | `interface/views.py:6769-6796` |
| L11 | ato (= recorte) × natureza | abre a prévia, escolhe natureza e signatário, publica | unitário por recorte | O(ΣM·R·2) | `divulgacao/models.py:52-56, 96-100` |
| L12 | recurso | admite, instrui (opcional), julga — cada um com texto | unitário | O(Rc) | `interface/views.py:7816-8046` |
| L12′ | recurso deferido | reemite e republica o recorte alcançado | unitário por recorte | O(Rc_deferidos) | `interface/supervisao.py:788-816` |
| L13 | recorte | apura a ocupação | unitário por recorte | O(ΣM·R) | `interface/views.py:6420-6444` |
| L14 | **convocado, inclusive titular** | convoca (espécie, vencimento digitado, fundamento) | **unitário** | O(Cv) | `convocacao.html:106-146`; `convocacao/application/convocar.py:252-257` |
| L15 | convocação | emite a comunicação | unitário | O(Cv) | `convocacao.html:245-256` |
| L16 | convocação | registra o desfecho com fundamento | unitário | O(Cv) | `convocacao.html:259-297` |
| L17 | desfecho (rodada de desfechos) | reapura o recorte antes de chamar o próximo | unitário por recorte | O(rodadas·R) | `ocupacao/application/selectors.py:150-162`; `convocacao/application/convocar.py:100-121` |
| L18 | fato externo (AVA, 1ª semana, entrega) | registra atestado | unitário | O(inércias) | `convocacao.html:308-329` |
| L19 | marco com convocados | exporta (prévia + gerar) | unitário por marco | O(ΣM) | `matriculas/application/populacao.py:114-144` |
| L20 | Perfil, numa Retificação de campo comum | repete a mesma alteração | unitário por Perfil | O(P) | `interface/retificacao.py:62`; `doc/achado-atribuicoes-repetidas-por-polo.md` |

**Leitura de conjunto.** O sistema tem lote **onde a decisão é de organização** (L1–L3) e é unitário **onde a decisão é sobre uma pessoa** (L4, L12, L14–L16) — e isso é coerente com o Princípio "decisão tem autor". O que não é coerente com ele são três casos em que o unitário não protege decisão nenhuma:

- **L5** (página de 25 na consolidação): a confirmação já declara o alcance; paginá-la só multiplica cliques.
- **L9–L11, L13** (um ato por recorte): a decisão real é do marco — "emita a ordem da Turma 2", "publique o resultado preliminar do polo X" —, e a mesma pessoa confirma R vezes o mesmo gesto, em R telas. A tela do sorteio já prova o contrário (lista os recortes juntos, `interface/views.py:8057-8058`), mas mantém um botão por recorte.
- **L14 para titular**: convocar quem já ocupa a vaga desde a apuração (`convocar.py:252-257`) é formalização, não escolha; a fila e a faixa já decidiram quem é.

## 15. Cenários

**Premissas comuns.** Modelagem como no estudo de 21/09 (`doc/estudo-esforco-de-cadastro-2026-09-21.md:110-112`): 78 = 2 Perfis / 0 Modalidades; 28 = 7 Perfis / 21 Modalidades; 140 = 16 Perfis / 64 Modalidades; um marco por Perfil. Recortes de ocupação = 1 (linha geral) + Modalidades reservadas (`editais/domain/recortes.py:33-60`). k = 1 avaliação por inscrição (DP-06). "Ato" = submissão que decide; cliques ≈ 2× atos. C (inscritos) é faixa **suposta** a partir do porte que o pedido indica; nenhum dos três Editais estima demanda (`estrutura-editais.md` §10 de cada). Tempos por unidade são **estimativa minha**, não medição.

### 15.1 Pequeno — 78/2026 (2 turmas, 61 vagas, sorteio, sem Modalidade; C ≈ 50–100)

R = 1 por Perfil → 2 recortes; M = 2; E = 1 (análise documental, governada pelo corte do sorteio); D = 7. Faixa = vagas + até 30 suplentes por turma (≤ 121) ≥ C, logo a análise documental alcança todo mundo.

| Fase | Conta | Atos |
|---|---|---|
| Comissão + alocação | lote + matriz | ~3 |
| Habilitação | sem Etapa declarada, o portal já exige os anexos (§6) | 0 (ou 50–100 na Mesa, se declarada) |
| Sorteio | 2 observações + 2 relações + 2 realizações | 6 |
| Classificação preliminar | 2 recortes × publicação | 2 (4 cliques) |
| Corte | 2 recortes | 2 |
| Análise documental | rodízio 2 + **50–100 conclusões** (350–700 aberturas de documento) + consolidação ⌈C/25⌉ = 2–4 rodadas | ~60–120 + leituras |
| Recursos | 0–10 peças × 2–3 | 0–30 |
| Ocupação e convocação | 2 apurações + **50–61 titulares × 1–3 formulários** + suplentes (10–25% → 5–15) × 3–4 + 5–15 reapurações | 75–250 |
| Exportação | 2 marcos | 2 (4 cliques) |
| Encerramento | Edital + Processo | 2 |

**Total**: ~150–420 atos, dos quais 50–100 são Mesa. **Tempo**: Mesa 50–100 × 3–6 min ≈ 3–10 h; convocação 75–250 formulários × 1–2 min ≈ 1,5–8 h. **O que domina**: a Mesa e a convocação empatam — a cauda custa tanto quanto a análise, porque cada titular é convocado à mão, e o Edital real nem convoca titular: ele homologa a matrícula de quem passou na análise (e78 L249-253). O laço marco × recorte é desprezível (2 recortes).

### 15.2 Médio — 28/2026 (7 polos × 40 vagas, AC/PPI/PcD, sorteio + CLVA; C ≈ 300–800)

R = 3 por Perfil → 21 recortes (o sorteio oferece 4 por Perfil, 28, dos quais 7 excedentes — RC-73); M = 7; E = 1 no sistema (análise documental); D ≈ 7–10. Faixa por polo ≤ 28+15 (AC) + 10+15 (PPI) + 2+15 (PcD) = 85 → ≤ 595 no Edital; com C entre 300 e 800, faixa ≈ 250–550.

| Fase | Conta | Atos |
|---|---|---|
| Comissão + alocação | lote + matriz (banca única; por polo seria L3′) | ~3–5 |
| Habilitação | 0 (ou 300–800 na Mesa) | 0 |
| Sorteio, ao vivo | 7 observações + 21 relações + 21 realizações | ~49 |
| Classificação preliminar | 21 publicações | 21 (42 cliques) |
| Corte | 21 recortes | 21 |
| Análise documental | rodízio 2 + **250–550 conclusões** (1 900–4 100 aberturas) + consolidação 10–22 rodadas | ~300–640 + leituras |
| Recursos (análise documental) | 5–10% → 15–55 × 2–3 | 30–165 |
| Heteroidentificação | **fora** (70–175 entrevistas CLVA; recurso à CPVA); o efeito entra por desfecho de reclassificação/indeferimento por pessoa | 10–40 desfechos |
| Ocupação e convocação | 21 apurações + **280 titulares × 1–3** + suplentes (15–30% → 40–85; desistência, AVA em 5 dias, reclassificação PPI) × 3–4 + reapurações 40–85 | 460–1 270 |
| Exportação | 7 marcos (o seletor "resultado" teria 21 opções com o mesmo rótulo) | 7 (14 cliques) |
| Encerramento | | 2 |

**Total**: ~900–2 200 atos no sistema, dos quais 250–550 são Mesa. **Tempo**: Mesa 250–550 × 3–6 min ≈ 12–55 h; convocação 460–1 270 × 1–2 min ≈ 8–42 h; CLVA fora, 70–175 entrevistas × 3 membros. **O que domina**: de novo Mesa ≈ convocação, e a convocação cresce com as vagas (280), não com a demanda. O laço de 21 recortes já pesa na navegação: ~21 × 4 telas (corte, ocupação, convocação, publicação) visitadas várias vezes, e as de convocação só por URL.

### 15.3 Grande — 140/2025 (16 códigos, AC/PPIQ/PcD/PTT, prova de títulos + CLVA, cadastro de reserva; C ≈ 200–500)

R = 4 por Perfil → 64 recortes; M = 16; E = 1 no sistema (títulos); D ≈ 8–12 + barema de 5 (Letras) ou 7 (TADS) itens.

| Fase | Conta | Atos |
|---|---|---|
| Comissão + alocação | lote + matriz | ~3–5 |
| Distribuição | banca única: rodízio 2; **bancas por curso** (Letras × TADS): L3′, 200–500 marcações por página sem coluna de Perfil, cruzando com a lista de Inscrições, que filtra por Perfil (`interface/views.py:4123-4136`) | 2 ou 200–500 |
| Prova de títulos | **200–500 conclusões**, 1 600–6 000 aberturas, **1 000–3 500 itens de barema somados fora** e digitados como total | 200–500 + leituras + planilha |
| Consolidação | 8–20 rodadas | 32–80 cliques |
| Ordem preliminar | 64 recortes × 2 passos (muitos vazios: PTT, PcD por polo) | 64 (128 cliques) |
| Publicação preliminar | 64 | 64 (128 cliques) |
| Recursos contra títulos | 10–20% → 20–100 × 2–3; cada deferido pede reemissão + republicação de 1–2 recortes | 40–300 + 40–400 |
| Publicação definitiva | 64 | 64 (128 cliques) |
| Heteroidentificação | **fora** (≤ 48 entrevistas); sem Etapa, o "não confirmada → AC" e o "ausente → desclassificado" (e140 L99-101, L371-372) não têm como entrar antes de uma convocação que não existe | 0 |
| Convocação | **não executável** (RC-58: 0 vagas ⇒ `SEM_DEFICIT`); a tabela intercalada de 50 posições (RC-59), a mobilidade entre perfis e os 2 anos de validade são fora | 0 no sistema |
| Exportação | não existe para tutores (`matriculas/application/populacao.py:86-103`) | 0 |

**Total no sistema**: ~550–1 700 atos, dos quais 200–500 são Mesa. **Tempo**: Mesa 200–500 × 10–20 min (títulos com barema) ≈ 35–165 h. **O que domina**: a Mesa com o barema fora, de longe. O segundo custo é o laço dos 64 recortes: ~200–300 atos e ~400–600 cliques em 64 × 3 telas só para ordenar e publicar duas vezes, sem sinal que diga quais recortes faltam (§13). E a cauda inteira — que num cadastro de 2 anos é o que dura — fica fora.

### 15.4 Como o custo cresce

| Dimensão | Cresce | Por quê |
|---|---|---|
| C (inscritos) | **linear**, na Mesa (O(C·D)) e, a 1/25, na consolidação | L4, L5 — irredutível na Mesa |
| vagas / Cv | **linear, com 3 formulários por pessoa** | L14–L16: titular também é convocado à mão |
| P × R (recortes) | **linear no número de recortes**, em 4–5 atos por recorte e por rodada (ordem, corte, apuração, publicação × 2) | L9–L11, L13 |
| M | multiplica os recortes (marcos moram no Perfil) | `interface/views.py:2940-2966` |
| E | linear e barata no lado da organização (2 atos de rodízio), linear e cara na Mesa | L3, L4 |
| A | quase nada (lote) | L1, L2 |
| Rc | linear, com cauda de reemissão por recurso deferido | L12, L12′ |

## 16. Dependências externas que a operação ainda exige

| Dependência | Editais | Onde o sistema para | Evidência |
|---|---|---|---|
| **Barema** (soma dos itens, conferência "item a item contra a expectativa") | 140 | a Mesa aceita uma pontuação; zero "barema" no código | RC-64; `mesa_inscricao.html:278-289` |
| **Heteroidentificação** (CLVA por vídeo, CPVA no recurso), **indígena por documento**, **elegibilidade PcD**, **Napne** | 28, 140 | não há Etapa aplicável só a quem declarou a Modalidade; zero `heteroidentifica` | RC-65; DP-10 |
| **Cadastro de reserva**: convocar sem vaga apurada, limite, validade, ordem intercalada entre listas, mobilidade | 140 | `SEM_DEFICIT`; `reserveType`/`reserveLimit` sem consumidor | `convocacao/application/convocar.py:249-289`; RC-58, RC-59 |
| **Prazo em dias úteis** | 78, 28 ("2 dias úteis") | o vencimento é digitado | `interface/views.py:6720-6733`; `convocacao.html` (ajuda do vencimento) |
| **Publicação nos sítios do Ifes/Cefor** | todos | o resultado tem página pública no portal; a convocação "por publicação" é registrada com a referência de onde foi publicada | `convocacao.html:240-253` |
| **Transmissão e gravação do sorteio** | 78, 28 | fora (YouTube) | e78 L192-199; e28 L476-480 |
| **Fatos pós-matrícula** (AVA em 5 dias, 1ª semana, colação em 30 dias, matrícula simultânea em outra especialização) | 28, 78 | entram como atestado, por pessoa, depois de verificados fora | `convocacao/domain/nomes.py:104-106` |
| **Registro Acadêmico** | 78, 28 | o sistema gera o arquivo; importar é fora | `interface/views.py:4186-4278` |
| **Vinculação UAB/CAPES** (ficha, termo, acúmulo de bolsa) | 140 | não há exportação para tutores | `matriculas/application/populacao.py:86-103` |
| **Resultado pós-análise documental como lista pública**, num Edital de sorteio | 78, 28 | a publicação projeta as posições do ato de sorteio (`divulgacao/domain/conteudo.py:48-78`), e o ato sorteado não se recalcula por Etapa (`divulgacao/domain/publicabilidade.py:264-269`): o eliminado na análise documental continua posicionado no documento; o candidato lê o próprio Resultado no acompanhamento. **[a confirmar pela tela]** | idem |
| **Atendimento** (e-mail, WhatsApp) | todos | a gestão vê rascunhos (`interface/views.py:4126-4127`) mas não tem ação de suporte; o sistema só envia e-mail em identidade, inscrição e convocação | `grep send_mail`: `identidade/application/mensagem.py`, `inscricoes/application/mensagem.py`, `convocacao/application/comunicar.py` |
| **Aviso à comissão** (trabalho distribuído, recurso chegando) | todos | nenhum | RC-67 |

## 17. Funcionalidades que existem e não formam fluxo

1. **A convocação não tem porta.** Nenhuma tela da gestão leva a `interface:convocacao` (§9). É a tela que a docstring diz substituir "a planilha paralela" (`interface/views.py:6448-6452`), e só se chega a ela digitando o endereço com o UUID do recorte. **Achado novo** — não está na auditoria de 26/09 nem no inventário da `033`. Nunca houve link: o único `{% url 'interface:convocacao' %}` da história dos templates nasceu com a `019` (`bcc8b9f1`), no breadcrumb do histórico; e o percurso E2E da `019` abriu a tela pelo endereço (`doc/e2e/019-convocacao/relatorio.md:62`).
2. **O sinal de ordem obsoleta leva ao recorte errado.** O UX-004 nomeia o recorte (`interface/supervisao.py:973`) e encaminha à ordenação sem `?lista=` (`:986`, `:1214-1217`), que abre a ampla (`interface/views.py:5760-5763`). O UX-066 acerta porque pende do ato. **Achado novo**, pequeno.
3. **A primeira passada por marco × recorte é de memória.** Recorte sem ato "não é sinal" (`interface/supervisao.py:842-846`); a página do Edital lista marcos, não recortes (`interface/views.py:2911-2966`). Num Edital de 64 recortes, saber quais ainda não foram ordenados, cortados, apurados ou publicados é abrir cada um.
4. **Consolidar em páginas de 25**, com a confirmação que poderia declarar o conjunto inteiro (§5).
5. **Distribuição cega a Perfil**, e a tabela sem coluna de Perfil, quando a lista de Inscrições ao lado filtra por Perfil (RC-61, DP-11).
6. **Publicação por recorte** × documento único do Edital real: 21 (28/2026) a 64 (140/2025) documentos para o que o Edital divulga como um "Resultado preliminar".
7. **Exportação**: a população "resultado" leva todo classificado — num sorteio, todo inscrito —, e o rótulo é só a data; a população certa ("convocados") exige convocar cada titular (§10).
8. **Recortes do sorteio ≠ recortes da ocupação** (RC-73): o sorteio oferece um recorte que a ocupação não consome.
9. **Toda mudança de fato envelhece a apuração**, e convocar com apuração obsoleta é recusado; o painel não sinaliza apuração obsoleta (UX-065 só vê a ausente). O operador descobre na recusa.
10. **Encerrar não confere a cauda**: convocação em aberto, recurso pendente e apuração obsoleta não impedem nem avisam (`processos/domain/finalizacao.py:55-60`).

## 18. Achados principais

1. **O custo irredutível é a Mesa, e o sistema já tira dela quase tudo o que não é juízo** (concluir e seguir, marca de aberto, painel do documento, rodízio). O que falta nela é o barema: no Edital de títulos o avaliador soma fora e digita o total (RC-64) — e é aí que mora o maior custo do cenário grande.
2. **A convocação é o segundo maior custo, e é auto-infligido.** Cada titular é convocado à mão, com fundamento digitado, e cada desfecho obriga a reapurar antes da chamada seguinte. Nos Editais de sorteio o titular não é convocado — tem a matrícula homologada —, e a única exportação fiel ("convocados") exige a convocação de todos. No cenário médio, 280 vagas viram 460–1 270 formulários.
3. **O laço marco × recorte** (ordem, corte, apuração, publicação) é linear no número de recortes e sem sinal para o que ainda não começou: irrelevante no 78 (2), sensível no 28 (21), dominante na navegação do 140 (64).
4. **A tela da convocação não tem entrada na navegação** — achado novo, verificado por busca em todos os templates e views.
5. **Cadastro de reserva (RC-58) e heteroidentificação (RC-65) põem a cauda do 140 e o meio do 28 fora do sistema**, e o 140 não tem exportação por não pedir requerimento.
6. **Consolidação paginada e distribuição cega a Perfil** são os dois lotes que param no meio: um por paginação, outro por falta de dimensão.
7. **O painel poupa a varredura de obsolescência, não o percurso**: ele vê o que envelheceu, não o que falta fazer, e um de seus destinos (UX-004) aterrissa no recorte errado.

## 19. Limites

Leitura estática do código em `f77e8aa9`; nada foi executado nem percorrido pela tela. As contagens são de formulários e submissões que o código exige, não de cliques medidos; os tempos por unidade são estimativa. As modelagens dos três Editais seguem o estudo de 21/09 e podem diferir de outra composição legítima (por exemplo, um marco final além do de sorteio). A estrutura dos Editais está em `scratchpad/estrutura-editais.md`, com as linhas dos `.txt`.
