# Relatório do Edital — rodada 2: comunicação executiva, semântica e maquete v2

24/10/2026, sobre a `main` em `5a08f409`. Responde à avaliação do usuário sobre a
[maquete v1](maquete.pdf). O veredito dela: fundamentação técnica boa e comunicação executiva
insuficiente.

> **Não abre spec, não cria requisito e não implementa nada.** Nenhuma linha de produção mudou, e
> não há migration. Os identificadores (`R-`, `CA-`, `G-`) continuam locais e provisórios. A spec
> revisada está em [`spec-proposta-v2.md`](spec-proposta-v2.md) e substitui a §6 do
> [estudo](../estudo-relatorio-de-execucao-do-edital-2026-10-24.md).

**Entregáveis**, na ordem pedida:

- A. avaliação crítica da v1 (§A);
- B. matriz de terminologia (§B);
- C. estrutura revisada (§C);
- D. [maquete v2](maquete-v2.pdf), sobre um cenário coerente (§D), com o quadro de alterações (§D.3);
- E. [spec revisada](spec-proposta-v2.md);
- F. plano do MVP (§F);
- G. decisões pendentes (§G).

---

## A. Avaliação crítica da maquete v1

Concordo com os cinco problemas da avaliação. A causa comum é que a v1 foi escrita **a partir do
modelo de dados**, e não da pergunta do leitor. Cada seção correspondia a uma tela de gestão, e
cada rótulo, ao nome de uma coluna. É o defeito que a proposta original pedia para evitar,
*"transcrição de telas"*.

A avaliação não podia ver três defeitos meus, que corrijo aqui:

1. **Eu disse que o sistema não tem "deferido". Está errado.** O enum de `DecisaoRecurso` não tem,
   mas o produto já diz ao candidato *"Recurso deferido — o resultado foi corrigido"*
   (`recursos/application/selectors.py`, `ESPECIES`). O portal também tem rótulos em linguagem
   simples para cada desfecho de convocação: *"Vaga aceita"*, *"Desistência registrada"*,
   *"Convocação não atendida"* (`portal/situacao.py`, `DESFECHOS`, da `063`). **A linguagem simples
   já existe no produto e foi revisada para o candidato.** O relatório deve reaproveitá-la, e não
   inventar uma terceira (Princípio I).
2. **"Participaram" vinha de uma tela que mistura Perfis.** `panorama_da_etapa` conta como
   participante da *Análise documental* as inscrições do Perfil Técnico, cujo marco nem tem essa
   Etapa, e as dá como *"não consolidáveis"*. Na maquete v2, os 6 do Técnico aparecem ali.
   O relatório tem de contar **por Perfil**, a partir de `ResultadoEtapa`. Registro isto como
   observação sobre a contagem da tela, e não como defeito: o domínio declara Etapas por Edital, e
   a pergunta "esta Etapa é deste Perfil?" tem resposta pelo marco, que a tela não lê.
3. **"Seleção concluída" não era meu: era o título do Edital do semeador** (*"Edital 51/2026 —
   seleção concluída"*). Isso ensina uma regra: **texto livre do Edital nunca decide a situação
   dita pelo relatório.** O título aparece como título, e a situação sai de ato e de pendência.

A v1 também tinha um defeito de dado: a cronologia impossível, apontada no Problema 4. A causa é
que o `seed_demo` grava as inscrições direto no banco, fora do caminho do candidato. A v2 não usa o
semeador nessa parte (§D).

---

## B. Matriz de terminologia

**Critério.** Para cada termo, a recomendação segue esta ordem de preferência:

1. o rótulo que o produto **já mostra** a quem não é da gestão, isto é, o portal do candidato ou
   o documento publicado;
2. o termo do domínio, explicado uma vez;
3. só então uma expressão nova.

Termo jurídico ou do Edital — *cadastro de reserva*, *resultado definitivo*, *indeferido* — não é
trocado: é explicado.

| Termo da v1 | O que é no GPS | Risco de leitura | Na v2 | Preserva a precisão? |
|---|---|---|---|---|
| **Perfil** | `PerfilVaga`: cada cargo ou função com vagas próprias; termo da Constituição | "Perfil" sozinho não diz nada ao diretor | **"Perfil de vaga"** no cabeçalho, e o **nome do Perfil** na linha (*Professor de Informática*) | sim. *"Oferta"*, *"função"* e *"curso"* foram recusados, ver G-2 |
| **Marco** | `MarcoClassificatorio`: um resultado com regra de ordenação própria | jargão interno puro | o **nome do marco** como o Edital o publica (*Classificação final*); no executivo, *"resultado"* | sim |
| **Vagas ocupadas** | `ApuracaoDeOcupacao.ocupadas`: titular, dentro das vagas, habilitado na Etapa governada | **alto**: lido como matrícula | **"vagas com candidato classificado e habilitado"**, com *"ainda não é matrícula"* no próprio indicador; e **"vagas aceitas"** como indicador separado | sim. São dois fatos, e cada um tem nome |
| **Vagas efetivas** | publicadas ± reversão e acréscimo | jargão | só no anexo, como *"na apuração"* | sim |
| **Corte** | `Corte`: faixa que passa à Etapa governada | *"corte"* soa como eliminação | *"passam à análise documental 2 classificados mais 1 excedente, por lista"*, com o **nome da Etapa governada** | sim |
| **Com posição / sem posição** | `SituacaoDivulgada`: `CLASSIFICADA` / `SEM_POSICAO` | opaco | **"com classificação publicada"**. *Sem posição* só no anexo, quando houver | sim |
| **Participaram** | participante do panorama da Etapa (§A.2) | **alto**: sugere presença | **"avaliados"**, isto é, com avaliação registrada, mais *"eliminados por ocorrência"* em coluna própria | sim. A presença é declarada como não registrada |
| **Titular habilitado** | ocupante na apuração | jargão | absorvido em *"classificado e habilitado"* | sim |
| **Desfecho da convocação** | `DesfechoDaConvocacao`, sete espécies | jargão. *"Resposta"*, sugerido na avaliação, **não serve a todas**: inércia e não atendimento são registros da comissão, não respostas | **os rótulos do portal**: *Vaga aceita*, *Desistência registrada*, *Convocação não atendida*… E *"aguardando resposta, até DD/MM"* enquanto o prazo corre | sim |
| **Recursos inadmitidos** | `JuizoDeAdmissibilidade.admitido=False` | jargão processual | **"não admitido"**, que é o rótulo do produto, com *"sem análise do pedido"* na primeira menção | sim |
| **Indeferidos** | `DecisaoRecurso.INDEFERIDO` | baixo | mantido | sim |
| *(novo)* **Deferidos** | as três espécies favoráveis | — | **"deferido"**, agrupando-as como o produto já faz para o candidato | sim |
| **Cadastro de reserva** | declaração do Perfil; a pertença por pessoa **não** é registrada | baixo como termo; **alto** se o relatório afirmar quem está nele | mantido, explicado: *"os 6 classificados podem ser chamados se surgir vaga"*. Nunca *"6 pessoas no cadastro"* | sim |
| **Resultado definitivo** | `PublicacaoResultado` `DEFINITIVA` | baixo | mantido; *"resultados finais"* foi recusado porque não é o nome do ato publicado | sim |
| **Inscrições enviadas** | `SUBMETIDA` | baixo | **mantido**: é o rótulo do portal (*"Inscrição enviada"*). *"Concluídas"* seria um quarto nome. Os rascunhos aparecem como *"iniciadas e não enviadas"* | sim |
| **Pessoas distintas** | cadastros de acesso (`identity_subject`) distintos | médio: duas contas da mesma pessoa contam duas vezes | *"38 inscrições, de 36 pessoas"*, com a definição no anexo | **parcial**, ver G-6 |
| **Inscrições por vaga** | razão da `040` | lido como "pessoas por vaga" | **"candidatos por vaga"**, só **dentro de um Perfil**, onde inscrição e pessoa coincidem (unicidade por Perfil) | sim, e mais preciso que antes |
| **Encerrado** | `Edital.Status.ENCERRADO`: só o recebimento para | **alto**: lido como "terminou" | **duas linhas**: *Situação no GPS* e *Situação das providências* | sim |
| **Ocorrência** | `ResultadoEtapa` de origem `OCORRENCIA`, com motivo em texto livre | *"ausente"* seria inferir do texto | *"eliminado por ocorrência registrada"*. O motivo não é lido nem resumido | sim |
| **Apuração** | `ApuracaoDeOcupacao` | jargão | só no anexo | sim |
| *(não usado)* **Aprovado** | inexistente no domínio, e proibido nas telas de resultado pelas varreduras | **alto** | **evitado de propósito**, também em *"aprovado na etapa"* (a v2 diz *"habilitados na etapa"*) | — |

---

## C. Estrutura revisada

### C.1 Um documento, duas camadas

**Um documento só**, com o executivo nas primeiras páginas e o anexo técnico depois. Não proponho
dois relatórios: seriam duas derivações dos mesmos números, que podem divergir (`FR-582` da
`040`), e duas emissões para auditar.

| Camada | Páginas no cenário | Pergunta que responde | Leitor |
|---|---|---|---|
| **Executiva** | 2 | o que foi oferecido, quanta procura houve, o que saiu, o que falta | direção e coordenações |
| **Anexo técnico** | 2 | como cada número foi obtido, regra a regra, e onde conferir | equipe, controle, auditoria |

A executiva, na ordem:

1. **Identificação** e **duas situações**: no GPS e das providências.
2. **Visão geral**: um parágrafo produzido por regras (§C.2).
3. **Seis indicadores**, cada um com a base escrita embaixo.
4. **Pontos de atenção**, só fatos e no máximo três.
5. **Resultados por perfil de vaga**.
6. **Procura ao longo do período**: o único gráfico, porque mostra o efeito da prorrogação, o que
   um número sozinho não mostra.
7. **Alterações e recursos**.
8. **Datas principais**, cada uma marcada como *publicação*, *registrado*, *previsto* ou *prazo*.
9. **Documentos oficiais**, sem hash.

O anexo traz:

- A. etapas, por Perfil;
- B. classificação e vagas, por lista;
- C. recursos, por Perfil;
- D. cronograma previsto × retificado × registrado;
- E. documentos com SHA-256;
- F. como cada número foi obtido;
- G. o que o GPS não registra;
- H. sobre a emissão.

### C.2 A visão geral, por regras e sem modelo de linguagem

Cada frase tem uma **condição** e uma **fonte**. Frase sem condição verdadeira não é escrita;
frase com fonte ausente é trocada pela grafia de ausência. Para o cenário:

| Frase | Condição | Fonte |
|---|---|---|
| *"ofereceu N vagas imediatas para P (k de ampla e j reservadas a M)"* | N > 0 | quadro de vagas da versão vigente |
| *"e abriu cadastro de reserva para Q"* | Perfil com 0 vaga imediata e reserva declarada | idem |
| *"Recebeu I inscrições, de X pessoas, entre D1 e D2"* | sempre que I > 0; *"de X pessoas"* conforme G-6 | `Inscricao`, primeiro e último `submitted_at` |
| *"O prazo foi prorrogado R vez(es), e K inscrições chegaram no período acrescentado"* | Retificação que alterou o `endAt` do período para depois | `AlteracaoNormativa` + `submitted_at` |
| *"Os resultados definitivos de [todos os perfis / k dos n perfis] saíram em D"* | marcos com `DEFINITIVA` vigente | `vigente_do_marco` |
| *"depois do julgamento de R recursos, [nenhum deferido / d deferidos]"* | R > 0 | `DecisaoRecurso`, `JuizoDeAdmissibilidade` |
| *"As V vagas imediatas têm candidato classificado e habilitado"* | apuração vigente e não obsoleta | `recortes_do_marco` |
| *"a vaga já foi aceita / a pessoa convocada tem prazo até D"* | desfecho `ACEITE` / convocação sem desfecho com vencimento futuro | `Convocacao`, `DesfechoDaConvocacao` |

A frase **não interpreta**. *"13 inscrições chegaram no período acrescentado"* é contagem; dizer
que *"a prorrogação foi eficaz"* seria juízo, e não entra.

### C.3 A espécie do relatório: acompanhamento ou encerramento

A avaliação pediu para não tratar `ENCERRADO` como garantia de conclusão. A regra proposta é
**determinística e não cria estado**. O relatório é **de encerramento** quando valem as cinco
condições abaixo, e **de acompanhamento** em qualquer outro caso:

1. Edital `ENCERRADO`;
2. todo marco declarado tem resultado `DEFINITIVA` vigente;
3. nenhum recurso aguarda admissibilidade ou julgamento, nem há providência pendente;
4. toda apuração vigente está atualizada (`causas_de_obsolescencia` vazia);
5. nenhuma convocação tem o prazo de resposta em curso.

Edital cancelado tem espécie própria, *"de interrupção"*: o ato de cancelamento e o que havia sido
publicado até ali.

**O cenário cai no caso que motivou a regra**: o Edital está encerrado e o relatório sai **de
acompanhamento**, porque a convocação PPP está no prazo. A capa diz isso na segunda linha, e o
anexo H explica a regra.

---

## D. Maquete v2

### D.1 O cenário

[`roteiro/cenario_coerente.py`](roteiro/cenario_coerente.py), num banco próprio
(`ps_maquete_v2`). **Todo fato passa pelos commands da aplicação, com o relógio posto na data do
ato.** As inscrições seguem o **caminho do candidato** (`abrir_inscricao` → `gravar_dados` →
`enviar_inscricao`), e não a gravação direta do semeador. Se a cronologia estivesse errada, o
command recusaria. Foi o que aconteceu duas vezes durante a montagem, com razão: uma definitiva
sobre marco sem prazo recursal, e um empate na fronteira da vaga.

| Data | Fato | Coerência conferida pelo sistema |
|---|---|---|
| 03/08 | Edital 61/2026 publicado; inscrições de 10/08 a 30/08 | publicação recusa período já vencido (`028`) |
| 25/08 | Retificação prorroga o fim para 04/09 | publicada **antes** do fim original |
| 10/08–04/09 | 38 inscrições enviadas, 4 rascunhos | `enviar_inscricao` recusa fora do período |
| 15–17/09 | prova corrigida; 1 ocorrência | — |
| 20/09 | títulos consolidados | — |
| 24–25/09 | ordens emitidas; preliminares publicados | — |
| 26–29/09 | 3 recursos; julgados em 02/10 | `interpor` recusa fora da janela de 5 dias |
| 06/10 | definitivos | a definitiva recusa marco sem prazo recursal |
| 08–10/10 | corte por lista, análise documental, apuração | a apuração recusa empate na fronteira |
| 13/10 | 2 convocações para vaga inicial | a espécie é derivada da posição (`050`) |
| 20/10 | Edital encerrado, com a convocação PPP no prazo até 30/10 | **nada impede** (achado do estudo, §1.2) |
| 21/10 | aceite da ampla registrado, dentro do prazo, que ia até 23/10 | **aceito depois do encerramento** |

As duas situações excepcionais, isto é, a pendência e o registro posterior, **são plausíveis**, e
não artefatos.

### D.2 Os dados

[`roteiro/extrair_v2.py`](roteiro/extrair_v2.py) lê só agregados. Ele **não** usa
`recursos_do_edital` + `resumo`, que trazem nome e protocolo, e conta por espécie.

**Desempenho.** Com o mesmo cenário em escala 10 (`ESCALA=10`: 362 inscrições, 360 pessoas), a
leitura completa fez **145 consultas, as mesmas do cenário de 38**. O número de consultas cresce
com *Perfis × marcos × listas*, e não com inscrições. O tempo foi de 0,12 s com 38 e 0,17 s com
362, em três rodadas cada.

Isto **não** prova desempenho com milhares de inscrições. Prova que a forma da leitura não é
linear no volume. O teste de orçamento de consultas proposto no plano (§F) prende essa forma.

### D.3 Quadro de alterações (v1 → v2)

| O que mudou | Por quê | Problema resolvido | Muda regra de negócio? | Exige implementação adicional? |
|---|---|---|---|---|
| Visão geral em texto no topo, por regras | o diretor lia seis números soltos | 1 | não | sim: as regras da §C.2 (módulo de leitura) |
| Seis indicadores com nomes do que medem; *"vagas aceitas"* separado de *"classificado e habilitado"* | *"vagas ocupadas"* era lido como matrícula | 2 | não | não: as fontes são as mesmas |
| Rótulos do portal para convocação e recurso | linguagem simples já revisada no produto | 2 | não | não: reuso de `DESFECHOS` e `ESPECIES` |
| *"Situação no GPS"* × *"Situação das providências"*, e a espécie *acompanhamento/encerramento* | *"encerrado"* não é *"concluído"* | 3 | **não**: nenhum estado novo; a espécie é derivada | sim: a regra da §C.3 |
| Cenário coerente pelo caminho do candidato | cronologia impossível da v1 | 4 | não | não para o produto; o roteiro vira fixture de teste |
| *"Avaliados"* + *"eliminados por ocorrência"*, contados por Perfil | *"participaram"* sugeria presença e misturava Perfis | 4 | não | sim: contagem por Perfil a partir de `ResultadoEtapa` |
| Anexo técnico: pesos, corte, listas, hashes, definições | excesso de detalhe no corpo | 5 | não | não |
| Fatos não públicos só por Perfil, sem cruzar com cota; nenhuma célula suprimida | supressão por célula se desfaz por diferença | §9 da avaliação | não | não; é regra de composição |
| Emissão numerada (*"emissão nº 1"*) | rastrear reemissões | §3 da avaliação | não | sim: contar as emissões na auditoria (G-5) |
| *"Deferido"* passa a existir no relatório | correção do meu erro (§A.1) | 2 | não | não |

---

## F. Plano de implementação do MVP

*Plano para avaliação, e não `plan.md`: o formal sai do `/speckit-plan` se a spec for aberta.*

### F.1 Onde mora cada parte

| Parte | Lugar proposto | Por quê |
|---|---|---|
| Derivação: dataclasses, ausências, espécie, frases | `processos/application/relatorio_do_edital.py` | uma derivação, lida pela página e pelo PDF. O precedente é `interface/visao_geral.py`, mas o PDF não deve importar de `interface` |
| PDF | `processos/infrastructure/relatorio_pdf.py`, sobre `Composicao`, `render_documento` e `_tabela` de `publicacoes/infrastructure/pdf.py` | é o que `divulgacao/infrastructure/documento.py` e o comprovante já fazem. Sem dependência nova |
| Página | view em `interface/views.py`; template `interface/relatorio_do_edital.html`; folha em `interface/static/interface/telas/` | CSP sem inline (`091`/`092`) |
| Rotas | `editais/<id>/relatorio` e `editais/<id>/relatorio.pdf` | ao lado de `editais/<id>/auditoria` |
| Ação | entrada em `interface/acoes.py` (`Acao`) no detalhe do Edital | padrão de *nem oferecido, nem escondido* |
| Emissão | `record_event` com `operation="EMITIR_RELATORIO"`, o instante de referência e o SHA-256 em `detalhe` | sem tabela nova (G-5) |

### F.2 O que se reaproveita, e o que precisa de ajuste pequeno

| Reaproveita como está | Ajuste pequeno |
|---|---|
| `visao_geral.vagas_do_conteudo`, `contagens_por_edital`, `_razao` | `_alteracoes_legiveis` com antes/depois mora em `interface/views.py`: mover para `publicacoes/application` |
| `supervisao.serie_do_edital` | `inscricoes/application/consulta.py::_contagens` é privada |
| `processos.selectors.desfechos` | contagem por Perfil × Etapa × consequência a partir de `ResultadoEtapa.vigentes`: uma consulta nova |
| `divulgacao.selectors.vigente_do_marco` | contagem agregada de recursos por Perfil e espécie: uma consulta nova, **sem** a listagem nominal |
| `ocupacao.selectors.recortes_do_marco`, `causas_de_obsolescencia` | os rótulos de `portal/situacao.py` e de `recursos/selectors.py` passam a ser importados, e não copiados |
| `publicacoes.selectors.atos_publicados`, `alteracoes_legiveis` | — |
| `portal/situacao.DESFECHOS`, `recursos/selectors.ESPECIES`, `SITUACOES` | — |

### F.3 Sequência

1. **Derivação e testes de unidade**: as cinco grafias de ausência, a espécie (§C.3), cada frase
   da §C.2 com a condição verdadeira e falsa, *"candidatos por vaga"* não aplicável em Perfil só
   de reserva, listas que não se somam.
2. **Fixture do cenário**: o `cenario_coerente.py` vira fixture de teste, nos moldes de
   `tests/fixtures/convocacao.py`.
3. **Página**: autorização com a porta `pode_supervisionar`, 404 com linha no inventário da
   `033`, folha estática, acessibilidade (tabelas com cabeçalho, gráfico com equivalente textual).
4. **PDF e emissão**: o mesmo dataclass, um teste de determinismo (mesmos fatos e mesmo instante,
   mesmos bytes) e o evento de auditoria com o hash.
5. **Guardiões**: template e PDF na varredura de vocabulário (`aprovado`, `ocupada` sem
   qualificação); varredura do texto do PDF sem nome, CPF ou protocolo.
6. **Orçamento de consultas**: o mesmo número com 38 e com 380 inscrições (`CaptureQueriesContext`,
   como em `tests/performance/test_visao_institucional.py`).
7. **Cenário demonstrável** (Princípio VI): gestor abre o Edital, vê o relatório e baixa o PDF,
   pelo navegador.

**Sem migration, sem tabela e sem dependência nova.** A M de append-only não muda.

---

## G. Decisões pendentes

Só as que pedem manifestação humana. As demais estão resolvidas na spec, com a razão.

| # | Decisão | Opções | Recomendação | Por que é humana |
|---|---|---|---|---|
| **G-1** | Abrir a spec formal (`/speckit-specify`) agora, ou depois de mostrar a v2 a destinatários reais? | agora · depois da conversa | **depois**: as respostas da avaliação às quatro perguntas são hipóteses dela, como ela mesma disse | é governança e prioridade |
| **G-2** | Como nomear o Perfil para o leitor externo | *"Perfil de vaga"* (domínio) · *"função/curso/oferta"* | **"Perfil de vaga" + o nome do Perfil**. A `040` recusou *"oferta"* por escrito: segundo termo para o mesmo conceito contraria o Princípio I | tocar o vocabulário é decisão constitucional |
| **G-3** | Quem gera, e se o PDF pode circular fora do GPS | gestão + presidência · + auditor · papel de Direção | gestão + presidência geram; o PDF circula **internamente**. O papel de Direção continua pendente desde a `040` | distribuição é política institucional |
| **G-4** | Política de exposição | supressão por célula · **fatos não públicos só por Perfil, sem cruzar com cota** · nenhuma | a do meio. Os números que já são públicos por ato (vagas, classificados por lista) aparecem; eliminação, ocorrência, recurso e rascunho, só por Perfil | é LGPD; pede o encarregado |
| **G-5** | O que se guarda de cada emissão | **só o hash na auditoria** · os bytes, em tabela nova append-only | o hash basta para provar o que foi emitido. Guardar bytes só se alguém precisar baixar a emissão antiga | retenção de documento |
| **G-6** | *"De X pessoas"* no texto executivo | sim, com a definição no anexo · não | sim, com a definição; já é pendente na `040` (indicador 14) | é a mesma decisão da `040` |
| **G-7** | Encerrar o Edital deve avisar ou bloquear diante de pendência? | não · avisar · bloquear | **fora do escopo do relatório**: é achado sobre a `001`. O relatório funciona nos três casos | muda regra de negócio |
