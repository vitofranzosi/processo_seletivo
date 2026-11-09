# Entrega 2 — O mapa real da jornada

## O ponto de partida: atos, não uma máquina de estados

O GPS não tem um "status do processo" que avança. Ele tem **atos** imutáveis: congelar uma relação,
observar a semente, emitir uma ordem, emitir um corte, apurar, publicar um resultado, convocar,
conferir. Cada ato vale para um escopo próprio — o Edital, o Perfil, o marco ou a lista.

A 127 já lê esses atos e devolve, para cada **ponto da jornada** em cada **lista**, uma de sete
situações. O mapa abaixo foi tirado do código (`interface/andamento.py`, `sequencia_do_perfil`,
`_pontos_do_marco`) e não da hipótese do pedido.

### As quatro dimensões de estado, que a tela atual mistura

| Dimensão | O que é | De onde vem | Exemplo |
|---|---|---|---|
| **Estado administrativo** | O ciclo de vida do objeto | `Edital.status`, `ProcessoSeletivo.status` | Publicado, Ativo, Encerrado, Cancelado |
| **Fase operacional** | Onde estão os atos de cada lista | As células do `Andamento` (127), agrupadas pelo protótipo | Classificação: ação disponível em 1 de 2 listas |
| **Situação temporal** | O que um prazo decide | Período de inscrições; o `ate` das células; `publicabilidade.aferir` | Prazo recursal até 14/11; resposta dos convocados até 09/12 |
| **Estado da providência** | Quem age, e se pode agir agora | `Providencia.grupo` e `situacao` (127) | Sua, de outro papel, aguarda, impedida, recomendação |

O protótipo dá a cada uma um lugar próprio no cabeçalho: situação administrativa, inscrições e o
papel da pessoa, mais a frase "Onde estamos".

## As macrofases propostas

A hipótese do pedido tinha seis macrofases. A investigação propõe **oito**, por três motivos:

1. **Avaliação separada de Classificação.** As Etapas (prova, títulos) são trabalho dos avaliadores,
   distribuído e consolidado. A ordem é ato de quem conduz. E no sorteio a Etapa é **paralela**:
   nada a lê, salvo a de habilitação (`qualifyingStageId`, D-011 da 127). Juntar as duas esconderia
   o caso do C06 (A-04).
2. **Vagas separada de Resultado e recursos.** Corte e apuração correm em paralelo com o prazo
   recursal (R2 da 133: esperar é recomendação, e não impedimento), e o resultado definitivo não é
   pré-requisito da convocação (manual, §B).
3. **"Preparação e publicação" vira "Edital".** Depois da publicação, ela é histórico mais
   Retificações. As Retificações podem acontecer **em qualquer fase**, por isso aparecem como faixa
   sobre a página, e não como etapa.

| # | Macrofase | Pergunta que responde | Pontos da 127 que reúne | Escopo |
|---|---|---|---|---|
| 1 | **Edital** | O Edital está publicado e vigente? | `Edital.status`, Publicações, Retificações em curso | Edital |
| 2 | **Inscrições** | Quem se inscreveu, e o período acabou? | `inscricoes` do `Andamento` (período e enviadas) | Edital |
| 3 | **Avaliação** | As Etapas foram avaliadas e consolidadas? | pontos `etapa` do grupo "Etapas · valem para o Perfil" | Perfil (repetido por lista) |
| 4 | **Classificação** | Em que ordem cada lista ficou? | `relacao`, `semente`, `sorteio` (sorteio) **ou** `ordem` (pontuação) | lista; a semente é do marco |
| 5 | **Resultado e recursos** | O resultado foi divulgado, e cabe recurso? | `resultado`, mais as providências `recurso` (104) | lista |
| 6 | **Vagas** | Quem a faixa alcança, e que vaga cada um ocupa? | `corte`, Etapa governada pela faixa (documental), `apuracao` | lista |
| 7 | **Convocação** | Quem foi chamado, entregou e foi conferido? | `convocacao`, providência `conferir` | lista |
| 8 | **Conclusão** | Tudo tem desfecho, e o Edital pode ser encerrado? | `Edital.status == ENCERRADO`; `matricula_fora()` | Edital |

**A situação de uma macrofase é derivada, não guardada.** O protótipo agrega as células com uma regra
pura e fixa (`centro.agregar`):
- há ato a praticar → **ação disponível**;
- senão, impedimento → **com impedimento**;
- senão, espera → **aguardando**;
- feito ao lado de *Depois* → **em andamento**;
- tudo feito → **concluída**.

Entre listas vale a mais urgente, e "1 de 2 listas concluídas" acompanha. **Várias macrofases podem
estar em curso ao mesmo tempo**, e a trilha marca todas. É a diferença em relação à barra de fases
que a 127 recusou: não existe "a" fase do Edital.

## A matriz da jornada

Legenda das fontes, com o detalhe no relatório do agente que mapeou o código:
- `AtoDeOrdenacao` vigente: `classificacao`
- `RelacaoDeHabilitados`: `sorteios`
- `OcorrenciaDaFonte`: semente
- `Corte`: `classificacao`
- `ApuracaoDeOcupacao`: `ocupacao`
- `PublicacaoResultado`: `divulgacao`
- `Recurso`, `DecisaoRecurso`: `recursos`
- `Convocacao`, `DesfechoDaConvocacao`, `ComunicacaoEmitida`: `convocacao`
- `ApresentacaoDeDocumento`, `ConferenciaDeDocumento`: documentos da convocação

| Macrofase | Marco | Significado | Pré-requisitos | Estado derivável | Responsável | Próxima ação | Dependências | Escopo |
|---|---|---|---|---|---|---|---|---|
| Edital | Publicação original | O Edital vira ato público imutável | Elaboração → homologação → publicação, com segregação | `Edital.status`; `Publicacao` | Elaborador, Homologador, Publicador | — | Autoridade vigente na unidade | Edital |
| Edital | Retificação | A única forma de corrigir o publicado | Edital publicado; permissão de retificar | `atos_retificacao.em_curso` (103) | Elaborador → Homologador → Publicador | Elaborar, homologar, publicar | Pode mudar prazos, vagas e regras de **qualquer** fase | Edital |
| Inscrições | Período | Recebe inscrições | Edital publicado; período designado | `periodo.estado` (FUTURO, ABERTO, ENCERRADO) | Candidato | — | Data ou Retificação que encerra | Edital |
| Avaliação | Distribuir | Atribuir inscrições a avaliadores alocados | Inscrições encerradas; comissão alocada à Etapa | Célula `etapa`: "Distribuir N sem avaliador" | Quem conduz | Distribuir | Alocação por Etapa (Processo) | Perfil |
| Avaliação | Avaliar | Registrar nota ou parecer | Distribuição | Célula `etapa` + objeto 104 "avaliacao" | Avaliadores alocados | Avaliar N | — | Perfil |
| Avaliação | Consolidar | Fechar o resultado da Etapa | Todas as avaliações | Célula `etapa`: "Consolidar N prontas" | Quem conduz | Consolidar | A regra da Etapa (impedimento) | Perfil |
| Classificação (sorteio) | Relação congelada | Publicar, para cada lista, quem participa e com que número, antes da semente | Inscrições encerradas; habilitação, se o método a declara | `recortes_do_marco` → `congelada` | Quem conduz | Congelar a relação | **Antes** da extração (com a Caixa, num dia anterior) | lista |
| Classificação (sorteio) | Semente observada | Os números da extração declarada | **Todas** as relações do marco congeladas; extração já ocorrida | `OcorrenciaDaFonte` válida | Quem conduz | Observar a extração | Fonte pública; não se digita à mão | marco (todas as listas) |
| Classificação (sorteio) | Sorteio | O algoritmo aplica a semente à relação | Relação e semente | `AtoDeOrdenacao` vigente | Quem conduz | Realizar o sorteio | — | lista |
| Classificação (pontuação) | Ordem | A classificação calculada pelas notas, pesos e desempates | Etapas que a ordem lê consolidadas (senão *Depois*); ao menos um resultado (128) | `AtoDeOrdenacao` vigente; obsoleta se o universo mudar | Quem conduz | Emitir a ordem (ou sucessora) | Recurso deferido → obsoleta | lista |
| Resultado e recursos | Preliminar | A ordem tornada pública, abrindo o prazo de recurso | Ordem vigente | `PublicacaoResultado` (natureza) — **hoje só na nota** (G-3) | Publicador | Publicar resultado | — | lista |
| Resultado e recursos | Recursos | Pedidos de revisão no prazo | Preliminar publicado; prazo aberto | `Recurso` + juízo + decisão (104) | Julgador | Decidir N recursos | Reavaliação por **outro** avaliador | Edital (objeto 104) |
| Resultado e recursos | Definitivo | O resultado depois do prazo e dos recursos | Prazo encerrado; recursos decididos | `publicabilidade.aferir` (JANELA_ABERTA, RECURSO_PENDENTE) | Publicador | Publicar o definitivo | Não é pré-requisito do corte nem da convocação | lista |
| Vagas | Corte | A faixa: até que posição cada lista segue | Ordem vigente; regra de corte no marco | `Corte` (`estado_do_corte`) | Quem conduz | Emitir o corte | Com prazo recursal aberto: **recomendação** de esperar (133) | lista |
| Vagas | Etapa governada | A análise documental de quem a faixa alcançou | Corte | Célula `etapa` do grupo "governada" | Avaliadores, quem conduz | Distribuir, avaliar, consolidar | — | Perfil (pela faixa) |
| Vagas | Apuração | Que vaga cada pessoa alcançada ocupa, cruzando as listas | Corte; Etapa governada; linha no quadro de vagas; marco **terminal** (133, R1) | `ApuracaoDeOcupacao` vigente; obsoleta por desistência ou corte | Quem conduz | Apurar / Pedir a faixa seguinte | Esgotar a faixa → faixa seguinte | lista |
| Convocação | Convocar | Chamar com prazo quem a apuração indicou | Apuração vigente | `leitura_do_recorte` + `previa_dos_titulares` | Quem conduz | Convocar N titulares | — | lista |
| Convocação | Comunicar | Emitir e registrar a comunicação | Convocação | `ComunicacaoEmitida` | Quem conduz | Emitir N comunicações | Canal da convocação (125) | lista |
| Convocação | Entregar documentos | O convocado envia os documentos | Comunicação | `ApresentacaoDeDocumento` | **Candidato** | — (espera, com prazo) | Prazo da convocação | convocação |
| Convocação | Conferir | Cada documento conforme ou pendente | Entrega; quem confere **abriu** o arquivo | `ConferenciaDeDocumento`; `leituras_por_chamada` | Quem conduz ou confere | Conferir os documentos de N | Alocação à conferência por Perfil | convocação |
| Convocação | Desfecho | Ocupou, não atendeu, desistiu | Tudo conforme, ou prazo vencido | `DesfechoDaConvocacao` | Quem conduz | Registrar desfecho / não atendimento; chamar a próxima | A fila anda; apuração refeita | lista |
| Conclusão | Encerrar o Edital | Fim de ciclo do Edital | Nada pendente (advertências da 130 e da A-11) | `Edital.status`; `pendencias_do_edital.situacoes()` | Gestor | Encerrar | Prazos, recursos, Retificações e rascunhos em curso | Edital |
| Conclusão | Matrícula / formalização | Fora do GPS / área própria | Convocações com desfecho | `matricula_fora()`; `views_formalizacao` | Formalização, a unidade | Documentos para a formalização | — | Perfil |
| Conclusão | Encerrar o Processo | Fim de ciclo do Processo | Todos os Editais encerrados | `pending_editais` | Gestor | Encerrar o Processo | — | Processo |

## Variações por modalidade

| Família | O que muda na jornada | Visto com dado real? |
|---|---|---|
| **Sorteio sem habilitação** | Classificação = relação → semente → sorteio. Uma Etapa enumerada é **paralela** | Sim: C06 e C07 |
| **Sorteio com habilitação** (`qualifyingStageId`) | A Etapa de habilitação vem **antes** da relação (D-011) e a segura | Não: provado só pelas funções puras da 127 (família S3) |
| **Pontuação: prova e títulos** | Avaliação → ordem. A ordem fica *Depois* enquanto as Etapas que ela lê não consolidam | Sim: C04, C05, C08, C12 |
| **Eliminatória** | Uma Etapa desfavorável tira a pessoa da ordem | Sim: C04, candidato 08 |
| **Vários marcos no Perfil** | O marco intermediário não apura nem convoca: *Não se aplica* (133, R1) | Não: família P3, só nas funções puras |
| **Corte opcional** | Sem `cutRule`, o ponto Corte não existe e a fase Vagas é só a apuração | Não visto |
| **Lista sem inscritos** | Pontuação: emitir a ordem vazia declara que ninguém concorreu. Sorteio: *Não se aplica* (126) | Sim: PPP do C08, C12, C14 |

## Escopos: Processo, Edital, Perfil (oferta) e lista

- **Processo.** Agrega Editais; é dono da comissão, da alocação por Etapa, da supervisão e do
  encerramento. **Não** tem fase operacional própria: a do Processo é a soma da dos Editais.
- **Edital.** Publicação, Retificação, período de inscrições. É a unidade do Centro de Controle.
- **Perfil** (`PerfilVaga`, a "oferta" do pedido). As Etapas valem para o Perfil, e cada Perfil tem os
  seus marcos. Um Edital com dois Perfis tem duas jornadas lado a lado, e o protótipo mostra um bloco
  por Perfil.
- **Marco.** A semente é do marco, uma só para todas as listas.
- **Lista** (recorte: ampla e cada cota). Relação, sorteio, ordem, corte, apuração, resultado e
  convocação são por lista. **É a lista que avança, e não o Edital.**

## O que já é derivável, e o que exige ajuste

**Derivável hoje, sem tocar no domínio:** as macrofases e as situações agregadas, "onde estamos", a
fase aberta por padrão, a frente paralela do sorteio, a sequência de cada fase, as esperas com data,
os impedimentos com quem resolve e o "agora nesta lista". O protótipo faz tudo isso **só** a partir do
`Andamento` da 127 (`prototipo/centro.py`).

**Lacunas.** Cada uma precisa de ajuste em spec, e nenhuma pede tabela nova:

| Lacuna | O que falta | Onde resolver | Pede decisão? |
|---|---|---|---|
| G-1 | A providência não sabe que a lista não tem inscritos | Acrescentar a contagem da lista à célula da ordem (o indicador da condução já a sabe) | Não |
| G-2 | O Processo não agrega as providências dos Editais | "Frente B" da 129: leitura em lote com orçamento de consulta | Não |
| G-3 | O preliminar publicado não muda a situação da célula, só a nota | Um campo estruturado (`divulgado: preliminar/definitivo`) na `Celula` | Não |
| G-4 | Recursos são objetos do Edital (104), não células por lista | Aceitável na fase "Resultado e recursos"; a ligação recurso → lista afetada não é derivada | Sim, se quiser por lista |
| G-5 | O efeito de uma Retificação em curso sobre cada fase | Não derivável hoje: o protótipo só avisa que ela existe | Sim |
| G-6 | Tela e derivação divergem na semente (A-03) | Bloquear, confirmar em duas fases, ou só alertar | **Sim (D-5)** |
| G-7 | A contagem de providências do Perfil omite as de Etapa (A-07) | Somar as do Edital, ou dizer o escopo | Não |
| G-8 | Matrícula e formalização não são pontos | Fora do GPS por decisão (D2a do estudo de 06/11); mantido como nota | Não |
