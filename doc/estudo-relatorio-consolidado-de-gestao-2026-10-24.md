# Relatório Consolidado de Gestão dos Processos Seletivos — viabilidade e proposta de spec

**Data**: 24/10/2026 · **Base**: `main` em `5a08f409`, e a branch do PR
[#330](https://github.com/vitofranzosi/processo-seletivo/pull/330)
(`claude/gps-executive-closure-report-2d9457`, relatório do Edital, **aberto e sem merge**) ·
**Natureza**: investigação. Nenhum código, migration ou spec foi alterado.

Artefatos deste estudo, em
[`estudo-relatorio-consolidado-de-gestao-2026-10-24/`](estudo-relatorio-consolidado-de-gestao-2026-10-24/):

- [`maquete.pdf`](estudo-relatorio-consolidado-de-gestao-2026-10-24/maquete.pdf) — relatório consolidado
  do 1º semestre de 2026, seis páginas, **dados fictícios**, e o mesmo conteúdo em `maquete.html`;
- [`roteiro/gerar_maquete.py`](estudo-relatorio-consolidado-de-gestao-2026-10-24/roteiro/gerar_maquete.py)
  — monta a maquete a partir de doze Editais inventados e **calcula os totais pelas regras propostas
  aqui**, com asserções de coerência. Nenhum número da maquete foi digitado no total.

Os caminhos de código são relativos a `backend/processo_seletivo/`. Os da `099` existem só na branch
do PR #330.

---

## 0. Em uma página

**A pergunta já tem dois terços de resposta no código, e o terço que falta é o mais caro.**

1. **A consolidação de Editais já existe, e se chama Visão Geral** (`040`, `041`, `042`;
   `interface/visao_geral.py`). Ela reúne os Editais do escopo por ano, situação, período de
   inscrições e busca, e diz Editais, vagas imediatas, inscrições enviadas e inscrições por vaga,
   com as quatro grafias de ausência, em **cinco consultas fixas**, atrás da capacidade
   `visao:consultar` do Gestor. A `040` também **definiu e adiou** os indicadores de resultado —
   classificadas, convocadas, ocupação, requerimentos — e **recusou** PDF, unidade, tipo de processo
   e intervalo livre de datas, cada um com a razão escrita.
2. **O relatório do Edital (`099`) é a regra de cada número de resultado, de pendência e de
   espécie**, mas ele não é uma camada de indicadores reutilizável: é uma derivação por Edital
   (`montar`) que devolve números estruturados **misturados com frases já redigidas** — as pendências
   e a situação das providências são `str`. Para somar pendências entre Editais, é preciso que a
   derivação as devolva como código antes de redigi-las. É uma refatoração pequena, mas é mudança
   na `099`, e a `099` ainda não está na `main`.
3. **O custo da derivação por Edital foi medido aqui**: 120 consultas e ~0,3 s por Edital de dois
   Perfis, iguais com 38 e com 362 inscrições (bancos `ps_maquete_v2` e `ps_maquete_escala`). O
   número de consultas cresce com Perfis × marcos × listas, e não com inscrições. Um consolidado que
   chame a derivação Edital a Edital custa **linear no número de Editais** — aceitável para dezenas,
   e não medido acima disso.
4. **"Unidade" é o escopo do ator, e o ator tem um só.** A `Unidade` (`060`) materializa o
   `institution_scope`, só `cefor` está cadastrada, nada aponta para ela por chave estrangeira, e
   não existe campus, polo, curso, programa ou tipo de processo como entidade. Consolidar "por
   unidade" dentro do escopo é trivial — é o próprio escopo —; consolidar **entre** unidades
   (a Reitoria olhando os campi) não existe e exige papel e autorização novos (`G-014` e `G-010` da
   `040`, ainda abertos).
5. **O GPS não tem "data efetiva" de evento**, não tem estado de inscrição além de rascunho e
   enviada, não registra matrícula e não sabe contar pessoas. Cada ato registrado tem carimbo de
   tempo — e é isso que tornaria possível, numa evolução, a visão de atividades do período.

**Veredito: executar um MVP reduzido, mas não agora.** O MVP é a Visão Geral emitida como
documento, com a camada de resultados e pendências da `099` somada por Edital — *conjunto de
Editais*, e não *atividades do período*. Ele depende de três coisas, nesta ordem: o merge da `099`;
uma refatoração da derivação da `099` que devolva pendências como código, com prova de que o PDF
individual sai byte a byte igual; e a validação da demanda com destinatários reais, que pode ser
feita junto da SC-932 da `099`, ainda aberta. Nenhuma infraestrutura nova é necessária: nem tabela,
nem fila, nem dependência. A seção *Veredito*, no fim, dá os trade-offs, e a §I lista as decisões
que são suas.

---

## A. Diagnóstico técnico

### A.1 O que existe, e em que nível

| Superfície | Nível | O que responde | Porta | Estado |
|---|---|---|---|---|
| Visão Geral (`040`/`041`/`042`) | escopo | Editais, vagas imediatas, inscrições enviadas, em preenchimento, inscrições por vaga, por Edital e por Perfil, e duas marcas (sem procura; procura abaixo da oferta) | `visao:consultar` (só `gestor`) | `main` |
| Supervisão / Pulso (`022`/`038`) | Processo | o que está parado dentro de um Processo | gestão ou presidência | `main` |
| Relatório do Edital (`099`) | Edital | espécie, duas situações, seis indicadores, pendências, registros posteriores, anexo técnico; PDF com emissão auditada | `pode_gerir_comissao` (gestão do escopo ou presidência do Processo) | **PR #330, sem merge** |
| Ocupação, Convocação, Resultados, Publicações do marco | recorte / Etapa / marco | cada número na tela dona | portas próprias | `main` |
| Vitrine do portal (`024`) | público, entre escopos | seleções publicadas, com filtro por unidade | pública | `main` |

**Não existe área de relatórios**, e não existe exportação genérica: a única é o `.xlsx` de matrícula
(`matriculas/infrastructure/planilha.py`), com papel próprio, que não guarda o arquivo.

### A.2 O domínio, como o código o representa

| Conceito do pedido | Existe? | O que existe de fato | Evidência |
|---|---|---|---|
| Processo seletivo | ✅ | `ProcessoSeletivo`: `institution_scope`, `institutional_code`, `title`, `status` (`EM_ELABORACAO`/`ATIVO`/`ENCERRADO`/`CANCELADO`). Sem data, sem vaga, sem prazo | `processos/models.py:6-32` |
| Edital | ✅ | `Edital` (no app `processos`, não em `editais`): `number` (texto livre), `year`, `title`, seis estados; único por (`institution_scope`, `number`, `year`) | `processos/models.py:35-127` |
| Unidade | ⚠️ | `Unidade.codigo` **é** o `institution_scope`; nenhuma FK aponta para ela; só `cefor` declarada | `unidades/models.py:1-50`, `unidades/unidades.json` |
| Edital em mais de uma unidade | ❌ | um único `institution_scope` por Edital e por Processo | `processos/models.py:14,46` |
| Hierarquia campus > setor > curso | ❌ | recusada por escrito: o Reitor que responde por um campus é "uma linha a mais naquele campus, e não uma hierarquia a inferir" | `unidades/models.py:9-11` |
| Curso, programa, função | ❌ | só o texto do Perfil (`code`, `name`) | `editais/models/perfis.py:9-112` |
| Polo, campus | ❌ | `PerfilVaga.locality`, texto livre | idem |
| Tipo ou modalidade do processo | ❌ | "O sistema não tem taxonomia de natureza do Processo" | `processos/models.py:74-77` |
| Oferta | — | **Perfil de vaga**. "Oferta" foi recusada como segundo nome (`040`, §3.1; D-008 da `099`) | — |
| Vagas imediatas | ✅ | do **conteúdo publicado vigente** (`profiles[].immediateVacancies`), e não de `PerfilVaga` | `interface/visao_geral.py:442-478` |
| Vagas por lista | ✅ | `LinhaDoQuadroDeVagas`, `modalidade` nula = ampla concorrência | `editais/models/perfis.py:131-194` |
| Cadastro de reserva | ✅ | só a declaração do Perfil: `reserve_type` (`NONE`/`LIMITED`/`UNLIMITED`), `reserve_limit`; "só CR" por `cadastro_sem_vaga_imediata` | `editais/domain/quadro.py:134` |
| Vagas acrescidas | ✅ | `AcrescimoDeVagas` (`097`), fato operacional, não retificação | `ocupacao/models.py:284-345` |
| Inscrição | ✅ | **dois estados**: `RASCUNHO` e `SUBMETIDA`; uma por Perfil por identidade | `inscricoes/models.py:23-26,73-76` |
| Cancelamento, desistência, homologação de inscrição | ❌ | não existem | — |
| Pessoa | ⚠️ | `CandidateIdentity`: única por e-mail confirmado, não por pessoa; `cpf_normalizado` declarado e **não único** | `identidade/models.py:35-90` |
| Etapa e resultado | ✅ | `ResultadoEtapa` append-only, vigência por sucessão (`.vigentes`) | `resultados/models.py:41-215` |
| Resultado preliminar / definitivo | ✅ | `PublicacaoResultado` por (Perfil, marco, lista), `natureza`, sucessão | `divulgacao/models.py:35-129` |
| Classificação | ✅ | `AtoDeOrdenacao` + `PosicaoNaOrdem`; **as listas se sobrepõem**: quem concorre por reserva continua na ampla | `classificacao/application/calculo.py:28-32` |
| "Aprovado" | ❌ | não existe no domínio, e a varredura de vocabulário o proíbe | `tests/test_vocabulario_do_resultado.py` |
| Recurso | ✅ | `Recurso` + `JuizoDeAdmissibilidade` + `DecisaoRecurso`; situação **derivada**, sem coluna | `recursos/models.py:35-188` |
| Convocação e resposta | ✅ | `Convocacao` (chamadas sucessivas) + `DesfechoDaConvocacao` (sete espécies). "Sem resposta" é ausência de desfecho | `convocacao/models.py:84-303` |
| Ocupação | ✅ | `ApuracaoDeOcupacao` (`publicadas`, `efetivas`, `ocupadas`), com obsolescência | `ocupacao/models.py:25-135` |
| Matrícula efetivada | ❌ | **por decisão**: `GeracaoDeArquivo` registra que um arquivo foi gerado, e nada além | `matriculas/models.py:1-27` |
| Retificação, prorrogação | ✅ / ⚠️ | `Retificacao` + `AlteracaoNormativa` por caminho; prorrogação é uma Retificação que troca `/schedule/id=…/endAt`, sem modelo próprio | `publicacoes/models_retificacao.py:36-69` |
| Data efetiva de evento do cronograma | ❌ | só `PLANEJADO` e `CANCELADO` são declaráveis; a fase é derivada do relógio | `editais/domain/cronograma.py:16`, `editais/domain/fase_do_evento.py` |
| Encerramento | ✅ | ato `ENCERRAR`/`CANCELAR` em `AtoAdministrativo`, lido por `desfechos()`; **não congela** e **não confere pendência** | `processos/domain/finalizacao.py`, `processos/application/selectors.py:56-130` |
| Suspensão, revogação, anulação | ❌ | só `CANCELADO` | — |
| Trilha de auditoria | ⚠️ | `RegistroAuditoria` genérico, mas sem coluna de Edital; `trilha_do_edital` não reúne julgamento de recurso, publicação de resultado, sorteio nem corte | `auditoria/selectors.py:86-160` |

### A.3 A pergunta central: a `099` criou uma camada de indicadores reutilizável?

**Em parte — e a parte que falta é justamente a que o consolidado precisa somar.**

O que **é** reutilizável, e foi feito para isso:

- **A gramática dos números.** `Numero` e `Ausencia` (`interface/visao_geral.py:59-118`) carregam
  valor, parcialidade e as quatro grafias de ausência da `040`; a `099` acrescentou duas
  (`nao-registrado`, `omitido`). Um consolidado que some `Numero` herda a regra *"ausência não é
  zero"* sem reescrevê-la.
- **As leituras compartilhadas.** A `099` não recalcula vagas, contagens nem razão: chama
  `visao_geral.vagas_do_conteudo`, `contagens_por_edital` e `_razao` (a `040`), e as leituras donas
  de cada fato — `vigente_do_marco`, `recortes_do_marco`, `convocacao.vigentes`, `desfechos`. É a
  regra `FR-582` da `040` — uma derivação por número — aplicada de verdade.
- **As estruturas por Perfil.** `LinhaDoPerfil`, `Convocacoes`, `Recursos` e `LinhaDaEtapa` são
  dataclasses de números (`relatorio_do_edital.py:118-180`, na branch do PR).
- **O instante único.** `leitura_consistente()` põe a transação de fora em `REPEATABLE READ`
  (`relatorio_do_edital.py:265-277`) e funciona igual para um ou para cinquenta Editais.
- **A emissão.** Número pela trilha, SHA-256 dos bytes, `select_for_update` no agregado, documento
  determinístico (R-003 e R-004 da `099`).

O que **não** é reutilizável sem mudança:

| Peça | Por que não serve ao consolidado como está |
|---|---|
| `Relatorio.pendencias: list[str]` | as pendências saem **redigidas** — *"Professor de Informática: resultado definitivo de “Classificação final” ainda não publicado"* (`montar`, linhas 553-560). Contar "quantos Editais têm convocação aguardando resposta" exigiria ler a frase, que é exatamente o que a Constituição e a `040` proíbem: texto não decide situação |
| `situacao_no_gps`, `providencias`, `frases` | prosa pronta; o consolidado precisa do fato, e escreve a própria prosa |
| espécie | calculada **dentro** de `montar` a partir da lista de frases; está certa, mas não é função que se chame com os fatos |
| `_indicadores` | devolve `Indicador` com a base já escrita; o consolidado precisa dos termos da soma (numerador e denominador recortados), não do texto |
| custo | `montar` lê também cronograma, datas, documentos, série diária e registros posteriores, que o consolidado não usa ou usa só em contagem |

**Conclusão:** a arquitetura da `099` pode atender a múltiplos Editais **sem duplicar lógica**, desde
que a derivação seja separada em dois passos — *fatos do Edital* (números e pendências como código)
e *redação* (o que vira texto no relatório individual). O consolidado consome o primeiro passo. É a
única mudança de código que o MVP exige fora do arquivo novo, e ela tem uma prova de não regressão
barata e forte: a `099` é determinística (FR-2520), de modo que **o PDF do cenário coerente tem de
sair byte a byte igual antes e depois da refatoração**.

### A.4 Custo medido

Medição deste estudo, 24/10/2026, código da branch do PR #330, PostgreSQL local, leitura completa
(`relatorio_do_edital.ler`) de cada Edital com relatório:

| Banco | Edital | Perfis | Inscrições | Consultas | Tempo |
|---|---|---|---|---|---|
| `ps_maquete_v2` | 61/2026, encerrado | 2 | 38 | 120 | 0,32 s |
| `ps_maquete_escala` | 61/2026, encerrado | 2 | 362 | 120 | 0,32 s |
| `ps_demo_099_pendente` | 61/2026, encerrado | 2 | 38 | 120 | 0,29 s |

O teste da `099` (`tests/performance/test_relatorio.py`) prende 119 dentro da transação do caso.

**O que a medição permite dizer, e o que não permite.** Ela confirma que o custo **não** cresce com
inscrições. Ela **não** diz quanto custa um Edital de vinte Perfis com três marcos e quatro listas
cada: `montar` faz, dentro dos laços, uma leitura de `vigente_do_marco` e uma de `SituacaoDivulgada`
por (Perfil, marco, lista), duas por marco nas pendências de recurso e duas por Perfil na ocupação.
Multiplicar 0,3 s por cinquenta Editais daria 15 s — **a conta não é medição**, e os bancos de
demonstração não têm Edital grande. O teste proporcional está na §E.5.

A Visão Geral, por contraste, é **fixa**: cinco consultas para 3 ou 60 Editais
(`tests/performance/test_visao_institucional.py`, T-20).

### A.5 Lacunas

| # | Lacuna | Efeito sobre o consolidado |
|---|---|---|
| L-1 | Pendências da `099` são texto | impede somar pendência por tipo; resolvida pela refatoração da §A.3 |
| L-2 | Não há escopo acima da unidade, nem papel de Direção | "a Reitoria vê os campi" e "o diretor de ensino lê o relatório no sistema" não existem; o PDF chega a eles por quem conduz |
| L-3 | Não há campus, polo, curso, programa nem tipo de processo | os filtros C do pedido, abaixo do escopo, não são confiáveis; só o Processo agrupa Editais, e a seleção manual cobre o resto |
| L-4 | Não há data efetiva de evento | "etapas realizadas no prazo" e qualquer métrica de cumprimento de cronograma não têm fonte |
| L-5 | Não há pessoa | "pessoas distintas" tem erro não mensurável; a `099` decidiu não afirmá-la (D-004 da `099`) |
| L-6 | Não há catálogo comum de modalidades | "vagas para pessoas com deficiência em todos os Editais" exige casar nomes de modalidade entre Editais; a `039` discutia o catálogo |
| L-7 | `Publicacao.published_at`, `Inscricao.submitted_at` e `AtoAdministrativo.occurred_at` sem índice | irrelevante para o MVP, que filtra por Edital antes; relevante para a visão de atividades (`G-008` da `040`) |
| L-8 | A trilha do Edital não cobre todos os atos | a visão de atividades não pode sair da trilha; tem de sair do carimbo de cada tabela de domínio |
| L-9 | `Edital.number` é texto | a ordenação `-year, -number` põe "9" depois de "10"; vale corrigir na apresentação da relação dos Editais |

### A.6 Riscos e dependências

- **A `099` não está na `main`.** Tudo o que o consolidado reusa de resultado e pendência mora no
  PR #330. Implementar antes do merge seria construir sobre código que ainda pode mudar na revisão.
- **O valor da `099` também não foi validado.** A SC-932 — três destinatários de fora da operação
  entendendo a primeira página sem ajuda — está aberta. O consolidado repousa na mesma hipótese
  (*"quem dirige quer um documento"*) e acrescenta outra (*"quem dirige quer o conjunto"*).
- **A regra de encerramento pode mudar.** Se a decisão D-007 da `099` vier a conferir pendência ao
  encerrar, a espécie e os pontos de atenção do consolidado mudam junto — sem retrabalho, porque o
  consolidado lê a regra da `099` e não a copia.
- **O número da `040` e o do consolidado têm de ser o mesmo.** Se o consolidado contar vagas por um
  caminho e a Visão Geral por outro, o gestor verá 385 na tela e 383 no PDF.

### A.7 Achados registrados durante a investigação (não são escopo)

Governança é do usuário: os itens abaixo ficam registrados, e nenhum deles foi corrigido.

1. **Diferença entre totais na `099` (privacidade).** A FR-2551 da `099` omite os fatos não públicos
   de Perfil com menos de cinco inscrições e **mantém os totais do Edital contando-os**
   (`convocacoes_total = _somar_convocacoes(convocacoes_por_perfil.values())`). Num Edital de dois
   Perfis com um omitido, o número omitido volta por subtração: total da primeira página menos a
   linha do outro Perfil. É o mecanismo que a própria D-006 da `099` descreve como a razão de não
   esconder células. Se é aceitável — os destinatários são internos, e o limiar já é provisório —, é
   decisão sua e do encarregado de dados.
2. **Perfil sem nenhuma inscrição pode virar pendência perpétua (a verificar).** Em `montar`, marco
   sem nenhuma publicação gera *"resultado ainda não divulgado"*. Se o produto não emite ato de
   ordenação para Perfil vazio, o Edital com um Perfil sem procura nunca chegaria à espécie de
   encerramento. A leitura de `classificacao/application/` não foi conclusiva; um teste com o
   cenário coerente e um Perfil vazio responde.
3. **Ordenação do número do Edital como texto** (L-9). Afeta a Visão Geral hoje.

---

## B. Avaliação de produto

### B.1 Problema

*"Quanto o setor fez, e como terminou o que fez?"* hoje se responde abrindo a Visão Geral — que diz
oferta e procura, mas não resultado — e, para cada Edital, cinco telas de resultado, ocupação,
convocação e recurso. O relatório do Edital (`099`) resolve isso **para um Edital**. O consolidado o
resolveria para o conjunto.

### B.2 Destinatários e casos de uso, contra o que o GPS sustenta

| Caso de uso do pedido | Sustentável? | Por quê |
|---|---|---|
| Relatório anual de atividades do setor | ✅ como **conjunto de Editais publicados no ano**; ⚠️ como **atividades do ano** | o segundo exige a visão de atividades (§D.3), que fica para a evolução 2 |
| Diretor-geral conhece os resultados do seu campus | ✅ **se o campus for uma unidade cadastrada** e o relatório for emitido pela gestão dela | não há "campus" abaixo da unidade; o diretor não tem papel no GPS |
| Diretor de ensino conhece o panorama do semestre | ✅ semestre **de publicação** | semestre letivo ou de ingresso não existe (`G-005` da `040`) |
| Coordenador consolida os Editais do seu curso ou programa | ⚠️ por **seleção manual** ou pelo **Processo** | não há curso nem programa como entidade |
| Responsável escolhe cinco Editais e faz um balanço | ✅ | seleção manual dentro do escopo |
| Unidade usa os dados no relatório de gestão | ⚠️ | depende de quais indicadores oficiais o relatório de gestão pede — não verificado (§B.5) |

**Os destinatários finais não são usuários do GPS.** Isso é o argumento mais forte a favor de um PDF,
como na `099`: é o único veículo que chega a quem não tem papel no sistema.

### B.3 Valor esperado

- **Trabalho manual eliminado**: a soma de N relatórios individuais, ou de N passagens por cinco
  telas, feita à mão em planilha. A magnitude depende de quantos Editais a unidade publica por
  período — **dado que este estudo não tem** e que a validação precisa trazer.
- **Coerência**: o mesmo número na tela, no relatório individual e no consolidado, por construção.
- **Prestação de contas factual**: o que foi oferecido, procurado e apurado, com as ausências ditas.

### B.4 Hipóteses não validadas

| # | Hipótese | Como falsear |
|---|---|---|
| H-1 | O setor produz relatório periódico (semestral ou anual) e hoje o monta à mão | perguntar e pedir o último exemplar |
| H-2 | Quem dirige lê um consolidado e não só os individuais | mostrar as duas maquetes lado a lado |
| H-3 | O recorte por data de publicação corresponde ao que a instituição chama de "editais de 2026" | mostrar a ficha "Conjunto analisado" e perguntar o que esperavam ver |
| H-4 | A quantidade de Editais por período cabe numa emissão síncrona | contar os Editais do último ano |
| H-5 | Os indicadores pedidos pelo relatório de gestão ou pelo PDI são os que o GPS tem | ler o modelo do relatório de gestão e a ficha dos indicadores oficiais |

### B.5 Indicadores institucionais e PDI

**Não verificado, e não deve ser presumido.** A Rede Federal publica indicadores de gestão — a
Plataforma Nilo Peçanha e os indicadores pedidos pelos órgãos de controle incluem uma relação entre
inscritos e vagas —, mas a definição oficial (unidade de contagem, recorte por curso e ciclo,
tratamento de cadastro de reserva) não foi conferida neste estudo. **"Inscrições por vaga" do GPS não
deve ser apresentada como o indicador oficial** até a ficha dele ser lida e comparada. O mesmo vale
para qualquer meta do PDI do Ifes. A pergunta entra na validação (§15 do pedido; §B.6).

### B.6 Validação da demanda — perguntas

**Responsáveis pelos processos seletivos (quem emitiria):**
1. Hoje vocês fazem relatório do setor? Com que periodicidade, para quem, e em que formato? Podem
   mostrar o último?
2. Quanto tempo leva para montá-lo, e de onde vêm os números?
3. Quantos Editais a unidade publicou em 2025? Quantos Perfis tem um Edital grande?
4. "Editais de 2026" quer dizer publicados em 2026, numerados em 2026, ou com inscrições em 2026?
5. Um Edital cancelado entra no balanço? Com as inscrições que recebeu?
6. O relatório precisa ser "do dia 31/12", ou pode ser "dados até o dia da emissão"?

**Diretores-gerais e de ensino (quem lê):**
1. Que decisão vocês tomaram no último ano que dependeu de dado de seleção? Que dado faltou?
2. Com a primeira página da maquete, digam o que foi oferecido, o que saiu e o que falta.
3. O que vocês esperam ler e não está aí? (Atenção ao que o GPS não tem: matrícula, pessoas, causa.)
4. A comparação entre Editais de natureza diferente ajuda ou atrapalha?

**Coordenadores de curso ou programa:**
1. Como identificam "os Editais do meu curso"? Pelo título, pelo Processo, por outra coisa?
2. Um consolidado de três ou quatro Editais é útil, ou o relatório individual basta?

**Equipes de relatório institucional (relatório de gestão, PDI, PNP):**
1. Quais indicadores de seleção o relatório de gestão pede, com que definição? Podem passar a ficha?
2. A relação inscritos/vaga que vocês informam é calculada como? Por curso, por ciclo, com cadastro
   de reserva?
3. O dado sai hoje de onde? O GPS substituiria essa fonte, ou seria mais uma?

**Sinal de que vale implementar**: H-1 confirmada com exemplar, e ao menos um destinatário que use
o consolidado sem pedir o individual. **Sinal de que não vale**: o setor publica poucos Editais por
período, e os individuais já respondem.

---

## C. Matriz de indicadores

**Agregabilidade**: **A** aditivo · **R** agregável com regras · **N** não comparável (não gera total)
· **X** não disponível. **Confiabilidade**: alta, média, baixa. **Esforço**: **0** já calculado e
consolidável · **1** existe por Edital, falta a soma · **2** exige leitura nova · **3** exige dado que
o GPS não tem.

### C.1 Produção

| Indicador | Definição e fórmula | Unidade | Fonte | Agreg. | Limitações e risco de leitura | Recortes | Esf. | Conf. | MVP |
|---|---|---|---|---|---|---|---|---|---|
| Editais no conjunto | contagem dos Editais do critério, publicados, encerrados ou cancelados | Edital | `Edital` | A | **não é produtividade**: um Edital de 1 vaga e um de 200 valem 1 | situação, espécie, Processo | 0 | alta | ✅ |
| Editais por situação no GPS | contagem por `Edital.status` no instante de referência | Edital | `Edital.status` | A | "encerrado" é inscrições fechadas, não seleção concluída | — | 0 | alta | ✅ |
| Editais por espécie | regra da `099`: interrupção, encerramento, acompanhamento | Edital | derivação da `099` | A | depende da lista de pendências; muda se a D-007 da `099` mudar | — | 1 | alta | ✅ |
| Processos representados | `COUNT(DISTINCT processo_id)` | Processo | `Edital.processo` | R | não soma entre relatórios: o mesmo Processo pode estar em dois semestres | — | 0 | alta | anexo |
| Perfis de vaga publicados | contagem dos `profiles` do conteúdo vigente | Perfil | `VersaoConsolidada.content` | A | Perfil não é curso: o mesmo curso em três polos são três Perfis | só CR / com vaga | 0 | alta | ✅ |
| Cursos ou funções contemplados | — | — | — | **X** | não há entidade; contar nomes distintos de Perfil seria classificar texto livre | — | 3 | — | ❌ |
| Distribuição por unidade | contagem por `institution_scope` | Edital | `Edital` | A | dentro do escopo é constante: só faz sentido entre unidades, que não existe | — | 3 | — | ❌ |
| Distribuição por tipo ou modalidade de seleção | — | — | — | **X** | não há taxonomia, e o modelo diz que criá-la seria inventar eixo | — | 3 | — | ❌ |
| Retificações publicadas | contagem de `Retificacao` `PUBLICADA` dos Editais do conjunto | Retificação | `publicacoes` | A | conta atos, não importância: corrigir uma vírgula e mudar o número de vagas valem 1 | — | 1 | alta | ✅ |
| Editais com prazo de inscrição prorrogado | término vigente do período posterior ao original (regra da `099`) | Edital | conteúdo original × vigente | R | só o período de inscrições; outras mudanças de data ficam no individual | — | 1 | alta | ✅ |

### C.2 Demanda e participação

| Indicador | Definição e fórmula | Unidade | Fonte | Agreg. | Limitações e risco de leitura | Recortes | Esf. | Conf. | MVP |
|---|---|---|---|---|---|---|---|---|---|
| Inscrições enviadas | `COUNT(Inscricao WHERE status = SUBMETIDA)` | inscrição | `Inscricao` | A | **não é pessoa**; parcial enquanto houver período aberto | Edital, Perfil | 0 | muito alta (CHECK) | ✅ |
| Inscrições iniciadas e não enviadas | `status = RASCUNHO` | inscrição | idem | A | operacional; nunca no número principal | Edital | 0 | alta | anexo |
| Cadastros de candidato distintos | `COUNT(DISTINCT identity_subject)` **sobre a união** do conjunto | cadastro | `Inscricao` | R | **não soma entre Editais** — recalcula-se sobre a união; a mesma pessoa pode ter dois cadastros | — | 1 | média | anexo, se decidido (Q-05) |
| Pessoas distintas | `COUNT(DISTINCT cpf_normalizado)` | CPF declarado | `Inscricao` | **X** (confiável) | CPF declarado, nunca provado, não único; erro não mensurável | — | 3 | baixa | ❌ |
| Vagas imediatas | Σ `immediateVacancies` do conteúdo vigente | vaga | `VersaoConsolidada` | A | só Edital com conteúdo publicado; cadastro de reserva não é vaga | Edital, Perfil | 0 | alta | ✅ |
| Vagas em listas reservadas | Σ `vagas_imediatas` das linhas com `modalidade` não nula | vaga | `LinhaDoQuadroDeVagas` no conteúdo | R | **total só**: as modalidades não se casam entre Editais (L-6) | — | 1 | alta | ✅ |
| Vagas por modalidade (PcD, PPI…) entre Editais | — | — | — | **N** | sem catálogo comum, somar por nome erra em silêncio | — | 3 | — | ❌ |
| Perfis só de cadastro de reserva | Perfis com 0 vaga imediata e reserva declarada | Perfil | conteúdo | A | o limite de CR não se soma: `UNLIMITED` não tem número | — | 0 | alta | ✅ |
| Inscrições por vaga | Σ inscrições nos Perfis com vaga ÷ Σ vagas desses Perfis, uma casa | razão | derivado (`D-012` da `040`) | R | nunca média das razões; parcial com período aberto; **não comparável entre naturezas** (cursista × bolsista) | Edital, Perfil | 0 | alta | ✅ |
| Perfis com procura menor que a oferta | razão < 1 com período encerrado; e sem procura | Perfil | marcas da `040` | A | fato aritmético; **não diz causa** | — | 0 | alta | ✅ |
| Envios por mês | `submitted_at` agrupado por mês, nos Editais do conjunto | inscrição | `Inscricao` | R | meses do calendário; sem índice em `submitted_at`, mas a consulta filtra por Edital antes | — | 2 | alta | ✅ |
| Ranking de Perfis por procura | — | — | — | **N** | ordenar razões de naturezas diferentes produz comparação falsa | — | — | — | ❌ |

### C.3 Execução

| Indicador | Definição e fórmula | Unidade | Fonte | Agreg. | Limitações e risco de leitura | Recortes | Esf. | Conf. | MVP |
|---|---|---|---|---|---|---|---|---|---|
| Resultados previstos | marcos de classificação declarados por Perfil, no conteúdo vigente | marco × Perfil | conteúdo | A | estruturas de etapas diferentes: o número cresce com a complexidade do Edital | — | 1 | alta | ✅ |
| Resultados definitivos vigentes | marcos com definitivo vigente em todas as listas | marco × Perfil | `vigente_do_marco` | R | preliminar sucedido conta uma vez | — | 1 | alta | ✅ |
| Editais com todos os resultados definitivos | marcos definitivos = marcos declarados | Edital | idem | A | — | — | 1 | alta | ✅ |
| Etapas com resultado registrado | pares (Perfil, Etapa) com `ResultadoEtapa` vigente | par | `resultados` | **N** | etapas de Editais diferentes não são a mesma coisa; fica no individual | — | 1 | alta | ❌ |
| Recursos por situação | apresentados, não admitidos, indeferidos, deferidos, aguardando | recurso | `recursos` | A | contra etapas e atos diferentes: soma-se o pedido, **não** se calcula taxa de deferimento do conjunto | — | 1 | alta | ✅ |
| Editais com providência em curso | Editais com ≥ 1 pendência da `099` | Edital | derivação da `099` | A | exige pendência como código (L-1) | tipo de pendência | 1 | alta | ✅ |
| Pendências por tipo | contagem das pendências da `099`, por código | pendência | idem | A | idem | — | 1 | alta | ✅ |
| Registros posteriores ao encerramento | registros da trilha do Edital depois do ato de desfecho | registro | `relatorio_trilha.posteriores` | A | a trilha não cobre todos os atos (L-8): é piso, não total | tipo | 1 | média | ✅ |
| Atividades por mês (publicações, resultados, recursos, convocações) | carimbo de cada ato, agrupado por mês | ato | `published_at`, `publicado_em`, `interposto_em`, `decidido_em`, `criado_em`, `registrado_em` | R | **é outra visão** (§D.3); sem índice nos carimbos | tipo de ato | 2 | alta | ❌ evolução 2 |
| Cumprimento do cronograma | — | — | — | **X** | não há data efetiva de evento (L-4); a diferença entre previsto e ato registrado **não é atraso** | — | 3 | — | ❌ |
| Tempo médio entre etapas, produtividade da comissão | — | — | — | **X** / **N** | métrica falsa de eficiência: depende de prazo legal, volume e natureza | — | — | — | ❌ |

### C.4 Resultados

| Indicador | Definição e fórmula | Unidade | Fonte | Agreg. | Limitações e risco de leitura | Recortes | Esf. | Conf. | MVP |
|---|---|---|---|---|---|---|---|---|---|
| Inscrições classificadas em resultados divulgados | `DISTINCT inscricao` com `CLASSIFICADA` em publicação vigente, por Edital | inscrição | `SituacaoDivulgada` | R | **listas se sobrepõem** (ampla + reservada): distinct dentro do Edital, soma entre Editais; inclui marcos intermediários (`G-012` da `040`) — não é "classificação final" | — | 1 | alta | anexo |
| Vagas com inscrição classificada e habilitada | Σ `ocupadas` das apurações vigentes e atualizadas do último marco de cada Perfil | vaga | `ApuracaoDeOcupacao` | R | denominador = vagas **apuradas**, não vagas publicadas; **não é matrícula nem aceite** | — | 1 | alta | ✅ |
| Vagas sem apuração atualizada | vagas em recorte não apurado ou com apuração desatualizada | vaga | idem | A | "não apurada" não é "vaga vazia" | — | 1 | alta | ✅ |
| Convocações por desfecho | realizadas, aceitas, aguardando, prazo encerrado sem registro, outros | convocação | `Convocacao` + `DesfechoDaConvocacao` | A | a mesma inscrição chamada duas vezes conta duas; "prazo encerrado" não é "não atendida" | — | 1 | alta | ✅ |
| Taxa de aceite | aceitas ÷ convocações com desfecho | razão | idem | R | mistura cursista, bolsista e professor; leitura de "atratividade" sem base | — | 1 | média | ❌ |
| Requerimentos de matrícula enviados | `RequerimentoDeMatricula.enviado_em` não nulo | requerimento | `requerimentos` | R | só Editais que declaram `requerimento_momento` | — | 2 | alta | ❌ evolução 2 |
| Cadastro de reserva "formado" | — | — | — | **X** | CR não é estado de pessoa; só existe a declaração do Perfil | — | 3 | — | ❌ |
| Matrículas efetivadas / vagas preenchidas | — | — | — | **X** | **proibido** (`FR-592` da `040`; FR-2533 da `099`) | — | 3 | — | ❌ |
| "Aprovados" | — | — | — | **X** | o termo não existe no domínio | — | — | — | ❌ |

### C.5 Os oito casos difíceis de agregação

1. **Inscrições × pessoas.** Inscrições somam. Cadastros distintos **não** somam: recalculam-se
   sobre a união dos Editais, e ainda assim não são pessoas. Pessoas não entram (D-004 da `099`).
2. **Vagas ofertadas × reservadas.** Vagas imediatas somam. Reservadas somam **no total**, pela
   modalidade não nula; por modalidade, não. Cadastro de reserva não é vaga e nunca entra na soma.
3. **Classificados em listas sobrepostas.** `DISTINCT inscricao` dentro do Edital; a soma entre
   Editais é legítima porque a inscrição é de um Edital só. Nunca somar por lista.
4. **Cadastro de reserva.** Conta-se o Perfil (só CR, ou com CR), nunca o limite: `UNLIMITED` não
   tem número, e somar `reserve_limit` produziria um total sem significado.
5. **Concorrência.** Σ/Σ recortado aos Perfis com vaga, em todos os níveis, e marcado parcial com
   período aberto. Por Edital, aparece na tabela; **não se ordena** por ela entre naturezas.
6. **Preliminar × definitivo.** Só o vigente; o indicador é "marcos com definitivo vigente". Marco
   só com preliminar é pendência.
7. **Recursos de etapas diferentes.** Somam-se como pedidos, por situação. Nenhuma taxa.
8. **Encerrados com movimentação posterior.** Contam-se Editais e registros; a espécie é a da `099`,
   e o consolidado diz quantos encerrados ainda têm providência.

---

## D. Modelo de seleção e filtros

### D.1 Os critérios temporais não são equivalentes

| Critério | Fonte | Partição? | Inclui não publicado? | Retificação move? | Custo | Quando serve |
|---|---|---|---|---|---|---|
| **Ano do número** (`Edital.year`) | coluna | ✅ cada Edital em um ano | ✅ | não | uma coluna | é o recorte da Visão Geral hoje (`D-004` da `040`) |
| **Primeira publicação no período** | `Publicacao.published_at` com `publication_order = 1` | ✅ cada Edital em um período | ❌ | não | junção por Edital do escopo | **"o que o setor lançou no período"** |
| Encerrado no período | `AtoAdministrativo` (`desfechos()`) | ✅, mas só para os encerrados | ❌ | não | idem | balanço de fechamento; deixa de fora o que segue publicado |
| Com atividade no período | união dos carimbos dos atos | ❌ — o mesmo Edital entra em dois anos | ❌ | — | várias tabelas sem índice | visão de atividades, não de conjunto |

**A propriedade que importa é a partição.** Com ela, o relatório de 2026 e o de 2027 não contam o
mesmo Edital duas vezes, e somar dois semestres dá o ano. *"Com atividade no período"* não tem essa
propriedade e, por isso, não pode definir **conjunto** — só pode definir **atividades** (§D.3).

**Recomendação para o MVP: dois critérios, e só dois** — *ano do número* (o da Visão Geral, já
existente) e *primeira publicação entre duas datas*, com atalhos para ano, 1º semestre e 2º
semestre. O primeiro responde "o que temos com número de 2026, inclusive o que ainda está em
elaboração"; o segundo responde "o que lançamos em 2026". Qual deles é o padrão é a decisão Q-01 —
é a `G-005` da `040`, aberta desde 21/09.

**O semestre é de publicação, e o relatório o diz.** Semestre letivo ou de ingresso não existe no
domínio.

### D.2 Data de referência

**O relatório mostra cada Edital do conjunto no estado do instante da emissão**, e não no fim do
período. Um relatório do 1º semestre emitido em 24/10 mostra convocações registradas em setembro.
É a FR-2521 da `099` — *o relatório não reconstitui estado passado* — e vale aqui pela mesma razão:
o domínio é append-only e permitiria, em tese, reconstituir o passado, mas cada regra de vigência
teria de ganhar um parâmetro de instante, e o cronograma daquele dia misturado com os números de hoje
produziria um documento que nunca existiu. A ficha da primeira página diz isso por extenso
(maquete, página 1).

**Quem precisa do retrato de 31/12 emite em 31/12.** A emissão fica registrada, com o resumo do
arquivo, e é ela o retrato.

### D.3 As duas perspectivas

| | Visão por conjunto de Editais | Visão de atividades do período |
|---|---|---|
| Pergunta | como estão os Editais que lançamos? | o que o setor fez no período? |
| Universo | Editais (partição) | atos com carimbo no intervalo |
| Um Edital de 12/2025 com resultado em 03/2026 | entra em 2025 | o resultado entra em 2026 |
| Fonte | derivação por Edital (`040` + `099`) | carimbo de cada tabela de domínio (L-8) |
| Custo | linear nos Editais | uma agregação por tipo de ato, sem índice nos carimbos |
| Risco de leitura | "como estão" muda a cada emissão | contar atos parece produtividade |

**Recomendação: só a visão por conjunto no MVP.** A de atividades é útil e factível, mas é outro
produto: muda o universo, a fonte e a unidade de contagem, e acrescenta o risco de virar placar de
produtividade. Entra na evolução 2, como seção própria, com as contagens por tipo de ato e mês, e só
depois de a validação dizer que o relatório anual do setor é contado em atos, e não em Editais.

### D.4 Seleção manual

A seleção manual é **retirar ou acrescentar Editais ao conjunto que os filtros mostram**, com caixa de
seleção por linha na tabela da Visão Geral. Ela cobre o coordenador de curso (§B.2) sem inventar
curso. Os identificadores escolhidos viajam no formulário; nada é gravado.

Filtros que já existem e servem à seleção: número e título (busca), Processo (busca por título e
código institucional), situação, ano. **Unidade, curso, programa e modalidade não entram como
filtro** (L-3).

### D.5 Quem entra, e como cada caso é tratado

| Caso | Tratamento |
|---|---|
| Em elaboração, em revisão, homologado | **não entra**, e a relação diz quantos ficaram fora e por quê — não há fato público antes da publicação (FR-2513 da `099`) |
| Cancelado | entra na contagem de Editais e na relação, com a espécie *interrupção*; **fora** dos totais de vagas, inscrições, razão e resultados, dito na base de cada número (decisão Q-02) |
| Publicado com inscrições abertas | entra; inscrições e razão marcadas *parcial*; resultados dizem *ainda não disponível* |
| Resultado incompleto | entra; os números de resultado têm denominador explícito ("19 de 22") e a pendência aparece |
| Edital sem conteúdo publicado | não pode ocorrer entre os publicados; se ocorrer, *não publicado* (grafia da `040`) |
| Conjunto vazio | não há emissão; a página diz o critério e que nenhum Edital o satisfaz |
| Conjunto acima do limite | a emissão recusa e diz o limite (Q-11), até a medição da §E.5 |

### D.6 Unidade

- **Dentro do escopo**: o relatório é da unidade de quem emite. Não há filtro, porque teria uma opção.
- **Entre unidades**: não existe. Um relatório da Reitoria sobre os campi exige escopo acima da
  unidade, papel próprio e decisão institucional (`G-010`, `G-014` da `040`). **Não se resolve
  acrescentando filtro** — isso furaria o escopo, que a FR-583 da `040` e o princípio de negar por
  padrão protegem.
- **Duplicidade**: não há como um Edital ser contado em duas unidades, porque ele tem um escopo só.

---

## E. Arquitetura recomendada

### E.1 O fluxo

```
Registros do GPS (append-only, por Edital)
   │
   ├─ leituras em lote da 040 ── versoes_vigentes · contagens_por_edital · vagas_do_conteudo
   │                              (fixas, para todo o conjunto)
   │
   └─ fatos_do_edital(edital)  ── a derivação da 099, sem a redação
          (números, pendências como código, espécie)
   │
   ▼
consolidar(fatos)              ── somas com as regras da §C, ausências preservadas
   │
   ├──► página do consolidado (gestão)
   ├──► PDF (escritor da 099/Edital)          ── a mesma derivação, D-001 da 099
   └──► (futuro) colunas de resultado da Visão Geral, painel
```

**Nenhum PDF é fonte.** O consolidado nunca lê um relatório individual emitido: lê os fatos.

### E.2 A mudança na `099`: separar fatos de redação

Hoje `montar` faz três coisas: lê, decide e redige. A proposta é extrair, sem mudar comportamento:

- `fatos_do_edital(edital, *, agora)` → um dataclass com os números por Perfil que `montar` já calcula
  e as pendências como `(codigo, perfil_id, quantidade)` — os códigos são os oito da FR-2524 da
  `099`;
- `especie(fatos, status)` → a regra da FR-2523, como função;
- `montar` passa a chamar os dois e a redigir, como hoje.

**Prova de não regressão**: o PDF do cenário coerente da `099` (`tests/fixtures/relatorio.py`) com o
instante fixo tem de sair **byte a byte igual** antes e depois. A FR-2520 da `099` existe e
transforma a refatoração numa comparação de resumo SHA-256.

**Isto é alteração do relatório individual, e o pedido diz para não fazê-la sem autorização.** A
justificativa: sem ela, o consolidado ou lê frases, ou duplica as regras de pendência — e as duas
saídas são proibidas pela própria `099` (FR-2547: texto não decide situação; D-001: uma derivação).
A decisão é Q-08.

### E.3 Onde mora

`interface/relatorio_consolidado.py` (derivação) e a composição do PDF ao lado de
`interface/relatorio_pdf.py`, pelo mesmo motivo da R-001 da `099`: as leituras que ele consome moram
em `interface/`, e nenhum app de domínio importa de `interface`. Rotas sob a Visão Geral.

### E.4 Consistência temporal

- **Um instante para o conjunto inteiro**: `leitura_consistente()` da `099` envolve a leitura de
  todos os Editais. Em `REPEATABLE READ`, todas as consultas veem o banco do começo da transação; um
  desfecho gravado no meio da leitura entra na emissão seguinte. Uma transação só de leitura não sofre
  falha de serialização.
- **Emissão registrada** na trilha, como a da `099`, com `detalhe` contendo: critério e parâmetros,
  identificadores e número/ano dos Editais incluídos, os que ficaram fora e por quê, instante de
  referência, número da emissão e SHA-256 dos bytes. O agregado é a **Unidade** do escopo; o número
  é a contagem das emissões consolidadas anteriores dela mais um, sob `select_for_update` na linha da
  Unidade (o idioma da R-003 da `099`).
- **Sem tabela nova e sem guarda dos bytes** (D-005 da `099`). Guardar só se justificaria se alguém
  precisasse baixar uma emissão antiga.
- **Determinismo**: mesmos fatos, mesmo critério e mesmo instante produzem os mesmos bytes, como na
  `099`.

### E.5 Desempenho

- **Leitura**: camada de oferta e procura em lote (fixa, como a Visão Geral); camada de resultados e
  pendências por Edital (linear). Para o MVP, **linear é aceitável se a medição disser que é**.
- **Teste proporcional, antes de decidir o limite**: um cenário de N Editais com estrutura realista —
  Perfis, marcos e listas na proporção do maior Edital real que a validação trouxer (H-4) —, medindo
  consultas para N = 1, 10 e 40, e afirmando que o número cresce exatamente N vezes o de um Edital,
  mais uma constante. É a forma de igualdade que o projeto já usa (`test_visao_institucional.py`), e
  pega a consulta por inscrição que se infiltrar.
- **Limite do conjunto**: até a medição, um teto explícito (Q-11). A emissão síncrona é o idioma do
  projeto — não há fila (Constituição, princípio V: mensageria exige necessidade demonstrável).
- **Se a medição reprovar**: trocar as leituras por Edital da camada de resultados por leituras em
  lote (`edital__in=`), mantendo as regras como funções puras sobre as linhas lidas — as consultas
  5 a 8 da §20 da `040` já estão desenhadas. Isso só se faz com medição na mão.
- **Índices**: nenhum no MVP. A visão de atividades (evolução 2) é que pede índice nos carimbos.
- **Falha parcial**: não há. Um Edital que falhe na derivação faz a emissão inteira falhar, com o
  Edital nomeado — um consolidado que omitisse em silêncio o Edital problemático seria pior que nenhum.

### E.6 Permissões e privacidade

- **Porta**: `visao:consultar`, a mesma da Visão Geral, só do `gestor`. Como o gestor passa em
  `pode_gerir_comissao` em todo Processo do escopo (`comissoes/domain/autorizacao.py:65-81`), **todo
  Edital que ele consolida é um Edital cujo relatório individual ele pode abrir**. O consolidado não
  revela nada que o relatório individual não revele.
- **Presidência de comissão** passa na porta da `099` só para o próprio Processo, e não tem
  `visao:consultar`. Um consolidado restrito aos Processos que ela preside é possível, mas fica fora
  do MVP (Q-03).
- **Nada pessoal**: nome, CPF, e-mail, protocolo ou identificador de candidato não aparecem (FR-584
  da `040`, FR-2549 da `099`).
- **Fatos não públicos** — recurso, convocação, apuração — aparecem no total do conjunto e, nas
  providências, **por Edital**, que é o nível em que o relatório individual já os mostra; nunca por
  Perfil ou por lista. Edital com menos de cinco inscrições enviadas tem o detalhe não público
  omitido com a frase da D-006 da `099`, e continua nos totais. O risco de diferença entre totais é
  o mesmo da `099` (achado 1, §A.7), e o limiar é o mesmo, pendente do encarregado de dados.
- **Grupos pequenos no conjunto**: um consolidado de um Edital só repete os totais do individual — a
  exposição é a mesma, não maior.

### E.7 Reuso futuro por um painel

A derivação devolve dataclasses de números com `Numero`; a página da gestão é a primeira consumidora.
As colunas de resultado que a `040` adiou (`D-011` da `040`) passam a ter fonte: são os mesmos
`fatos_do_edital`, mostrados por linha na Visão Geral. **Nenhum painel é construído agora**; a
possibilidade fica por desenho, sem custo adicional.

---

## F. Maquete conceitual

[`maquete.pdf`](estudo-relatorio-consolidado-de-gestao-2026-10-24/maquete.pdf) — *Relatório
Consolidado de Gestão dos Processos Seletivos, 1º semestre de 2026*, **dados fictícios**, marcados em
toda página. Seis folhas:

| Folha | Conteúdo | O que ela testa com o destinatário |
|---|---|---|
| 1. Panorama | ficha do conjunto e da data de referência; duas situações; visão geral factual; seis números com a base embaixo; três pontos de atenção | se a primeira página basta; se "dados até 24/10, e não a de 30/06" é entendido |
| 2. Oferta e procura | vagas (ampla × reservadas), Perfis só CR, envios por mês, tabela por Edital, Perfis com procura menor que a oferta | se a tabela por Edital sem ordenação é aceita; se a ausência de comparação entre naturezas incomoda |
| 3. Execução e resultados | Editais por espécie, Retificações e prorrogações, recursos por situação, resultados publicados, vagas por situação de apuração, convocações por desfecho | se "classificada e habilitada, não é matrícula" é lido certo |
| 4. Pontos de atenção | pendências por tipo e por Edital; registros depois do encerramento; o que o relatório não diz | se a lista orienta ação |
| 5–6. Anexo técnico | relação dos Editais com espécie; critério e o que ficou fora; definição de cada número; limitações; emissão | se o controle interno consegue conferir |

O que a montagem da maquete mostrou:

- **A regra de privacidade precisa de um nível.** A primeira versão dizia "fato não público só no
  total do conjunto" e, na mesma página, listava as convocações aguardando resposta por Edital. A
  regra coerente é a da §E.6: o consolidado nunca desce abaixo do nível que o individual já mostra.
- **Um Perfil sem inscrição quase virou pendência de resultado** na maquete, pela regra da `099` — o
  que levou ao achado 2 da §A.7.
- **Inscrições por vaga de 33,0** (um Perfil de designer, uma vaga) ao lado de 0,5 (curso de
  extensão) é o argumento visual para não ordenar nem comparar entre naturezas.

---

## G. Spec proposta

> Rascunho para o `/speckit-specify`. Os identificadores abaixo são **provisórios** (`RC-`, `CA-`) e
> não pertencem à faixa global de `FR-`/`SC-`: a faixa se toma no dia da spec, sobre todas as
> worktrees (a da `099` termina em FR-2553 e SC-938).

### G.1 Nome e objetivo

**Relatório consolidado da unidade.** Um documento gerencial que descreve, para um conjunto de
Editais da unidade escolhido por critério explícito, o que foi oferecido, procurado e apurado, o que
segue em curso e o que o GPS não sabe — com cada número igual ao da tela e do relatório individual
de onde vem.

### G.2 Escopo e exclusões

| Cobre | Fora |
|---|---|
| Conjunto por ano do número, por primeira publicação entre datas, e seleção manual | Visão de atividades do período |
| Camada executiva, anexo técnico, PDF, emissão auditada | Guarda dos bytes; envio periódico; CSV |
| Unidade do ator | Consolidado entre unidades; papel de Direção |
| Indicadores da §C marcados MVP | Pessoas, matrícula, taxas, rankings, cumprimento de cronograma |
| Reuso da derivação da `099` | Mudança de comportamento da `099` |

### G.3 Requisitos funcionais (provisórios)

**Acesso**
- **RC-01**: A Visão Geral MUST oferecer "Relatório consolidado" a quem tem `visao:consultar`, sobre o
  conjunto que os filtros e a seleção definem.
- **RC-02**: O conjunto MUST conter só Editais do escopo do ator; identificador de Edital de outro
  escopo enviado no formulário MUST ser ignorado como inexistente, sem distinção.
- **RC-03**: Página e PDF MUST ser respostas privadas, sem cache compartilhado.

**Conjunto**
- **RC-04**: O critério MUST ser um de: ano do número; primeira publicação entre duas datas (com
  atalhos para ano e semestres). O padrão é decisão Q-01.
- **RC-05**: A seleção manual MUST permitir retirar e acrescentar Editais do escopo, e o relatório
  MUST dizer que houve escolha manual e quais Editais ela tirou ou pôs.
- **RC-06**: Só Editais publicados, encerrados ou cancelados MUST entrar; os demais MUST ser contados
  como "fora do conjunto" com o motivo.
- **RC-07**: Edital cancelado MUST entrar na relação e na contagem de Editais, e MUST ficar fora dos
  totais de vagas, inscrições, razão e resultados, com a exclusão dita (sujeito a Q-02).
- **RC-08**: Conjunto vazio MUST NOT ser emitido; conjunto acima do limite MUST ser recusado com o
  limite dito.

**Instante e emissão**
- **RC-09**: A leitura do conjunto inteiro MUST ver um instante só, e o documento MUST dizer "dados até
  DD/MM/AAAA, HHhMM" em toda página, e que a situação é a desse instante, e não a do fim do período.
- **RC-10**: O relatório MUST NOT reconstituir estado passado.
- **RC-11**: Cada emissão MUST gravar evento de auditoria na Unidade com critério, Editais incluídos e
  excluídos, instante, ator, número e SHA-256 dos bytes; o documento MUST dizer o número.
- **RC-12**: Mesmos fatos, critério e instante MUST produzir os mesmos bytes.

**Números**
- **RC-13**: Todo número MUST sair das mesmas funções que produzem o da Visão Geral e o do relatório
  individual; nenhuma regra de pendência, espécie, vaga ou razão MUST ser reimplementada.
- **RC-14**: A camada executiva MUST trazer seis números com a base escrita: vagas imediatas;
  inscrições enviadas; inscrições por vaga; Editais com todos os resultados definitivos; vagas com
  inscrição classificada e habilitada, sobre as vagas apuradas; convocações aceitas, sobre as
  realizadas.
- **RC-15**: Inscrições por vaga MUST ser Σ/Σ recortado aos Perfis com vaga imediata, e MUST NOT ser
  média de razões; MUST ser marcada parcial se algum Edital do conjunto tiver período aberto.
- **RC-16**: O relatório MUST NOT afirmar pessoas, matrícula, vaga preenchida, aprovado, taxa de
  deferimento, taxa de aceite nem cumprimento de cronograma.
- **RC-17**: Ausência MUST ser grafada pela `040` e pela `099`; zero só quando a fonte produziu zero.
- **RC-18**: Vagas MUST ser desdobradas em ampla e reservadas só no total; MUST NOT ser somadas por
  modalidade entre Editais.
- **RC-19**: A tabela por Edital MUST NOT ser ordenada por inscrições por vaga.

**Situação e atenção**
- **RC-20**: O relatório MUST contar os Editais por situação no GPS e por espécie da `099`.
- **RC-21**: As pendências MUST ser contadas por tipo e listadas por Edital, com os tipos da `099`.
- **RC-22**: Os pontos de atenção MUST ser no máximo três, nesta ordem: Editais encerrados com
  providência; Editais com registros posteriores ao encerramento; ausência de matrícula.
- **RC-23**: Fato aritmético de atenção (procura menor que a oferta) MUST vir sem causa, e com a
  frase de que o GPS não registra causa.

**Privacidade**
- **RC-24**: Nenhum dado pessoal ou identificador de candidato.
- **RC-25**: Fatos não públicos MUST aparecer só no total do conjunto e por Edital, nunca por Perfil
  ou lista; Edital com menos de cinco inscrições enviadas MUST ter o detalhe não público omitido, e
  continuar nos totais.

**Anexo e forma**
- **RC-26**: O anexo MUST trazer a relação dos Editais (número/ano, título, primeira publicação,
  situação, espécie, endereço público da seleção), o critério, os excluídos, a definição de cada
  número, as limitações e os dados da emissão.
- **RC-27**: O PDF MUST usar o escritor da `099` (determinístico, links, marcadores), com a natureza
  gerencial e a paginação em toda página.
- **RC-28**: A página MUST seguir a CSP vigente, ter tabelas com cabeçalho associado e não exigir
  rolagem horizontal a 375 px.

### G.4 Contratos de indicador

Cada número da camada executiva é declarado, no código, com: rótulo; fórmula; unidade de contagem;
fonte (função dona); regra de agregação (A ou R da §C); ausências possíveis; base escrita. É o
formato da §C, e a spec o transforma em `contracts/indicadores.md`, com teste que confere que todo
indicador emitido tem contrato.

### G.5 Critérios de aceitação (provisórios)

- **CA-01**: Para todo Edital de um conjunto de teste, a soma de cada número do consolidado é igual à
  soma do mesmo número nos relatórios individuais (zero divergência).
- **CA-02**: Vagas, inscrições e razão do consolidado são iguais às do consolidado da Visão Geral para
  o mesmo conjunto.
- **CA-03**: O PDF do relatório individual do cenário coerente sai com o mesmo SHA-256 antes e depois
  da refatoração da `099`.
- **CA-04**: Nenhum documento gerado nos testes contém nome, CPF, e-mail ou protocolo do banco de
  teste, nem fato não público por Perfil ou lista.
- **CA-05**: O número de consultas cresce exatamente com o número de Editais, e não com inscrições.
- **CA-06**: Duas emissões deixam dois eventos com resumos dos bytes entregues e números 1 e 2.
- **CA-07**: Pelo navegador, a gestão filtra a Visão Geral, retira um Edital, emite e baixa o PDF sem
  banco nem shell (princípio VI).
- **CA-08**: Em conversa com ao menos três destinatários de fora da operação, cada um diz, só com a
  primeira página, quantos Editais, o que foi oferecido, o que saiu e o que falta.

### G.6 Casos de borda a cobrir em teste

Conjunto só de cancelados; conjunto com período aberto; Edital só de cadastro de reserva; Edital sem
retificação, sem recurso, sem convocação ("nenhuma", e não 0 no lugar de fato); Edital com apuração
desatualizada; Edital encerrado com registro posterior; Edital com menos de cinco inscrições; Edital
de outro escopo forjado no formulário; registro gravado durante a leitura.

---

## H. Roadmap incremental

| Etapa | Conteúdo | Pré-condição |
|---|---|---|
| **0. Portão** | merge da `099`; validação com destinatários (§B.6), junto da SC-932 da `099`; decisões Q-01 a Q-11 | — |
| **1. MVP** | refatoração fatos × redação na `099` (com prova de bytes iguais); derivação consolidada; página a partir da Visão Geral; PDF; emissão auditada; teste proporcional de custo | portão |
| **2. Evolução** | visão de atividades do período (atos por tipo e mês, pelos carimbos de domínio, com índices medidos); colunas de resultado na Visão Geral pela mesma derivação; requerimentos de matrícula onde declarados; consolidado da presidência sobre os próprios Processos | uso real do MVP |
| **3. Evolução** | consolidado entre unidades, com papel de Direção e escopo acima da unidade; catálogo comum de modalidades, que permitiria somar reservadas por modalidade; registro de emissões consultável na tela | decisões institucionais (`G-010`, `G-014` da `040`) |
| **Longo prazo** | painel gerencial lendo a mesma derivação; alinhamento com indicadores oficiais (PNP, relatório de gestão) depois de conferidas as fichas; matrícula efetivada **só** com integração validada com o registro acadêmico | demanda demonstrada |

**Fora de qualquer etapa sem nova decisão**: data warehouse, ferramenta de BI, dependência nova,
texto por modelo de linguagem, previsão, recomendação, placar de produtividade.

---

## I. Questões pendentes — decisões suas

| # | Decisão | Opções | Recomendação deste estudo |
|---|---|---|---|
| **Q-01** | Critério temporal padrão (é a `G-005` da `040`) | ano do número · primeira publicação no período | oferecer os dois; padrão "primeira publicação", porque é o que a instituição lançou |
| **Q-02** | Edital cancelado nos totais | dentro · fora, dito | fora dos totais, na relação e na contagem |
| **Q-03** | Quem emite | só `gestor` (`visao:consultar`) · também a presidência, sobre os próprios Processos | só `gestor` no MVP |
| **Q-04** | Consolidado entre unidades | não agora · papel de Direção e escopo acima da unidade | não agora; registrar quando o segundo campus entrar |
| **Q-05** | Cadastros distintos no anexo | não · sim, com a definição | não; a `099` já os traz por Edital, e somá-los entre Editais confunde mais do que informa |
| **Q-06** | Limiar de privacidade por Edital | 5 (o da `099`) · outro | o da `099`, e a mesma consulta ao encarregado de dados |
| **Q-07** | Visão de atividades no MVP | sim · evolução 2 | evolução 2 |
| **Q-08** | Autorizar a refatoração da `099` (fatos × redação) | sim, com prova de bytes iguais · não | sim; sem ela o consolidado duplica regra ou lê frase |
| **Q-09** | Validar antes de implementar | sim, junto da SC-932 · implementar já | validar antes |
| **Q-10** | Achado 1 da §A.7 (diferença entre totais na `099`) | aceitar · mudar a regra da `099` | decisão sua e do encarregado de dados; o consolidado segue a regra da `099` |
| **Q-11** | Limite de Editais por emissão | número fixo até a medição · sem limite | fixo, decidido com o resultado da §E.5 e com H-4 |

---

## Veredito

**Executar um MVP reduzido, condicionado — não implementar agora, e não adiar indefinidamente.**

Os fundamentos:

- **Viabilidade técnica: alta, e sem infraestrutura nova.** Dois terços do produto já existem — a
  consolidação de oferta e procura (`040`) e as regras de resultado, pendência, espécie, emissão e
  PDF (`099`). O que falta é uma refatoração de separação na `099` e um arquivo de derivação.
- **Dependência real: a `099`.** Ela não está na `main`, e o consolidado depende dela para tudo o que
  não é oferta e procura. Construir antes do merge seria construir sobre código em revisão.
- **Valor: plausível e não demonstrado.** O valor da `099` também não foi demonstrado (SC-932
  aberta). O consolidado acrescenta a hipótese de que quem dirige quer o conjunto. Uma conversa com
  as duas maquetes valida as duas.
- **Risco de errar: baixo, se o MVP for o reduzido.** O MVP proposto não cria estado, papel,
  dimensão nem métrica que o domínio não tenha, e cada número tem dono. O risco está nas alternativas
  maiores — visão de atividades, comparação entre naturezas, entre unidades — e elas ficam fora.

**Comparação das alternativas do pedido:**

| | A — consolidação simples | B — relatório de gestão completo | C — camada gerencial reutilizável |
|---|---|---|---|
| Conteúdo | seleção manual, indicadores básicos, PDF | período, unidade, oferta, temporal, síntese | serviços de agregação para relatório e painéis |
| O que já existe | quase tudo (`040`) — falta o PDF | metade: unidade e atividades não existem | a gramática (`Numero`) e as leituras; falta o contrato |
| Esforço | baixo | alto | médio a alto |
| Valor | baixo — sem resultado, repete a Visão Geral em papel | alto, se a demanda existir | nenhum por si; é meio |
| Risco | pouco | métricas falsas, filtros sem dado, decisões institucionais | abstração antes do segundo consumidor |
| Dependências | nenhuma | `099`, papel de Direção, índices | `099` |

**O MVP recomendado é A + a camada de resultados da `099` + a semente de C**: a separação de fatos e
redação é exatamente o contrato que uma camada gerencial teria, feito porque o consolidado precisa
dele, e não por antecipação. B entra por partes, cada uma quando a anterior mostrar uso.

**A pergunta do pedido** — *como transformar os registros operacionais de vários processos seletivos
numa visão consolidada, confiável e compreensível* — tem, no GPS, esta resposta: **pela mesma
derivação que já descreve cada Edital, somada com regras escritas, sobre um conjunto definido por um
critério que se diz por extenso, num instante só, e sem afirmar nada que um registro não sustente.**
