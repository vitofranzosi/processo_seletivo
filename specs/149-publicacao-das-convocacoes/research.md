# Research: A publicação das convocações no GPS (149)

O diagnóstico e as decisões de desenho. As dez primeiras respondem, na ordem, às dez perguntas de
arquitetura do pedido; as três últimas, ao que o diagnóstico encontrou além delas. Em cada uma, a
alternativa mais simples que preserva os requisitos jurídicos, funcionais e de integridade.

## Diagnóstico: o que existe, e onde está a lacuna

Lido na `main` em `d3e98a89`, em 11/11/2026.

| Pergunta do pedido | O que o GPS tem hoje | Onde |
|---|---|---|
| 1. Specs | `019` (convocação, comunicação, desfecho), `050` (gestos por recorte), `115`/`117` (documentos), `120` (correção), `121` (mensagem), `125` (canal), `140` (conferência), `143` (tela do recorte), `066` (avisos) | `specs/` |
| 2. Modelos | `Convocacao`, `DesfechoDaConvocacao`, `ComunicacaoEmitida`, `AtestadoDeFatoExterno`, mais os três da `115` — todos append-only. Vigente = ninguém sucedeu; correção é sucessão com motivo | `convocacao/models.py` |
| 3. Preparar, conferir, efetivar | Por recorte (Perfil × marco × lista): prévia com assinatura do alcance, conferência do texto (`140`), confirmação por `comando_de_comissao` com idempotência | `convocacao/application/fluxo.py`, `interface/views.py` |
| 4. Modalidade | `callForm` do Perfil publicado: `PUBLICATION` ou `INDIVIDUAL_MESSAGE`; a convocação lê a da versão que citou | `publicacoes/domain/vocabulario_da_regra.py` |
| 5. Referência externa | `ComunicacaoEmitida.referencia_da_publicacao`, texto livre obrigatório na forma publicação (`ck_comunicacao_publicacao_com_referencia`), gravado pelo gesto *"Registrar a publicação"* | `comunicar.py`, `emitir_pendentes` |
| 6. Marcos e prazos | O vencimento é informado no ato; o prazo corre de `enviado_em` da comunicação bem-sucedida, nas duas formas (`R-009` da `019`, mantido pela `125`) | `convocacao/domain/prazo.py` |
| 7. Visibilidade ao candidato | A convocação por publicação é invisível até haver comunicação bem-sucedida na cadeia (FR-3981 da `125`) | `portal/situacao.py`, `selectors.py` |
| 8. Página pública | `/selecoes/<edital>/`: resultados por Perfil → etapa → lista, sorteio, vagas, cronograma, documentos. Nenhuma seção de convocação | `portal/views.py::selecao` |
| 9. Ato imutável, PDF, retificação | `PublicacaoResultado` (`017`): bytes canônicos, resumo, documento PDF gerado uma vez, sucessão, autoridade da `060`, página em endereço estável. O compositor de PDF (`Composicao`) é comum | `divulgacao/` |
| 10. Chamadas, vagas, listas, sucessão | Cada pessoa tem `chamada` (1, 2…) por recorte; correção é sucessão; a lista da chamada pertence à raiz. Não há entidade de lote (`D-011` da `019`, decisão de lote da `050`) | `convocacao/models.py` |

**A lacuna é uma só.** O GPS sabe fazer o ato de convocar e sabe fazer ato público imutável, mas não
junta os dois: na forma por publicação, o comentário de `ComunicacaoEmitida` diz que a referência
*"existe porque o sistema não publica no site do certame"*. Fechar essa lacuna é escrever o ato
público da convocação no molde da `017`, e fazê-lo gravar a comunicação que a comissão hoje grava à
mão.

## D-001 — Reutilizar a estrutura da divulgação do resultado, e não criar subsistema

**Decisão.** A publicação de convocados é um ato no molde da `PublicacaoResultado` da `017`: bytes
canônicos congelados (`canonical_bytes`) e o resumo deles, documento PDF gerado uma vez pelo mesmo
compositor (`Composicao`, `render_documento`), autoridade e unidade pelo `contexto_do_ato` da `060`,
página pública em endereço estável pela identidade do ato e o PDF num endereço irmão com `ETag`. Três
tabelas novas no app `convocacao`, append-only nas três camadas.

**Alternativas.** (a) Estender `PublicacaoResultado` com uma natureza *convocação*: ela é presa a
`AtoDeOrdenacao` e a um marco, e a publicação de convocados cruza recortes. (b) Um app
`publicacoes_genericas`: nenhum terceiro caso o pede (pedido, §11, *"mecanismos sofisticados de
publicação sem necessidade comprovada"*).

## D-002 — Uma modalidade, dois veículos: o ato grava a comunicação que a comissão gravaria

**Decisão.** Nenhuma forma nova de comunicar. A convocação por publicação continua `PUBLICATION`, e a
comunicação continua `ComunicacaoEmitida` com resultado *enviada* e referência obrigatória. O que muda
é **quem** a grava: na publicação externa, a comissão, pelo gesto das pendentes, com a referência que
digita; na nativa, a publicação de convocados, com a referência que identifica o ato no GPS. As três
situações do pedido viram dois efeitos por pessoa:

| Situação do pedido | Forma citada | Comunicação antes | Efeito na publicação |
|---|---|---|---|
| A. Mensagem individual | `INDIVIDUAL_MESSAGE` | enviada | *divulga* — nada é gravado |
| B. Publicação nativa | `PUBLICATION` | nenhuma | *convoca* — a comunicação nasce do ato |
| C. Publicação externa | `PUBLICATION` | registrada com referência | *divulga* — nada é gravado |

**Alternativas.** (a) Uma terceira forma `PUBLICATION_GPS` no `callForm`: exigiria degrau de schema,
Retificação e texto no Edital, e duplicaria a regra do prazo e da visibilidade. (b) Um campo
`veiculo` em `ComunicacaoEmitida`: tabela append-only compartilhada, e a informação já está no
vínculo com o ato (`ConvocacaoPublicada.comunicacao`).

**A referência gravada na nativa** é a frase *"página pública da seleção no GPS, ‹data› às ‹hora› —
‹N›ª publicação de convocados"*. Ela satisfaz a constraint, lê-se bem depois de *"Publicada em"* no
portal (FR-3998 da `125`), e é o que agrupa a chamada publicada nos avisos da `066` (FR-5735).

## D-003 — O evento oficial é o `commit` da confirmação, e um instante só

**Decisão.** A publicação acontece na transação da confirmação, dentro de `comando_de_comissao` (trava
do Processo, idempotência). O instante é o `now` do comando, e é o mesmo em `publicado_em`, em cada
`enviado_em` e na trilha. Ou tudo é gravado — o ato, os vínculos, as comunicações, o documento —, ou
nada é.

**Por que a comunicação nasce dentro da transação, ao contrário da `050`.** A decisão de envio
depois do `commit` da `050` existe porque o SMTP é efeito externo: um `rollback` desfaria o registro
sem desfazer a mensagem. Aqui não há efeito externo: o ato **é** a publicação, e ela só existe depois
do `commit`. Gravar as comunicações em transações separadas, como `comunicar_cada` faz, abriria a
janela em que a página pública existe e o prazo de parte dos convocados ainda não começou.

**Alternativa recusada.** Chamar `comunicar()` para cada convocação depois do ato: N transações, N
reservas de chave, e a possibilidade de um ato publicado com prazos não iniciados.

## D-004 — A semântica do prazo por canal fica onde está

**Decisão.** Nenhuma regra de prazo nova. O prazo corre de `enviado_em` da comunicação bem-sucedida,
nas duas formas, e a visibilidade ao candidato é a FR-3981 da `125`. A publicação nativa só **grava**
a comunicação; quem decide o prazo e a visibilidade é o código de sempre. No *divulga*, a publicação
não grava comunicação, e por isso não tem como mexer em prazo — a garantia é estrutural, e o teste a
confere (SC-1851).

**As guardas do envio valem no convoca.** As que `comunicar()` aplica — desfecho registrado,
vencimento anterior ao envio, emissão indeterminada, forma não declarada — são aplicadas pela prévia,
e conferidas de novo dentro da transação pela assinatura.

## D-005 — A relação histórica são os bytes do ato, e o vínculo é de integridade

**Decisão.** O que a página e o documento mostram sai **só** de `conteudo_publico`, composto na
confirmação e nunca recomposto (FR-5719): nomes, protocolos, rótulos de vaga e lista lidos da versão
que cada convocação citou, vencimentos, a autoridade e a unidade como estavam. A tabela
`ConvocacaoPublicada` não é lida para exibir: ela existe para o banco garantir que cada convocação
está em no máximo uma publicação (FR-5707), para a área do candidato achar a publicação da sua
comunicação, e para a correção posterior achar a publicação que corrige.

**Alternativa recusada.** Compor a página das tabelas a cada leitura: um nome corrigido na inscrição,
ou uma Retificação do rótulo da lista, reescreveria em silêncio o que foi publicado.

## D-006 — A correção é da convocação; a publicação seguinte a leva, e a anterior aponta

**Decisão.** A publicação não se retifica nem se sucede. Quem corrige é a **convocação** (`120`), por
sucessão com motivo; a sucessora nasce sem comunicação e entra na publicação seguinte com efeito
*convoca*, marcada *"corrige a convocação divulgada na ‹N›ª publicação"* — a marca é congelada no ato
seguinte, que sabe o número do anterior. A página da publicação anterior **deriva**, da cadeia de
convocações, o aviso de que uma linha dela foi corrigida depois (FR-5720), sem tocar os bytes nem o
PDF.

**Por que não uma sucessão de publicações, como o resultado.** O resultado é uma lista inteira que se
substitui; a convocação é um conjunto de atos por pessoa, cada um com o seu prazo. Suceder a
publicação inteira para corrigir uma pessoa reabriria o prazo das outras, ou exigiria explicar por que
não reabriu.

**O motivo da correção não vai a público**, pela mesma razão que a `120` o tirou do portal: é texto
livre da comissão e pode citar terceiro.

## D-007 — A seção entra na página da seleção depois dos resultados, e a relação tem página própria

**Decisão.** A página da seleção ganha a seção *Convocações*, só quando há publicação, logo depois de
*Resultados divulgados*: é o passo seguinte do certame, e é onde quem procura o resultado procura a
convocação. A seção é compacta — uma linha por publicação, as três mais recentes à vista e as
anteriores recolhidas, a orientação dita uma vez — e a relação mora na página própria da publicação,
como a ordem do resultado mora na dela e a relação de habilitados na sua.

**Alternativa recusada.** A relação inteira na página da seleção: com três publicações de quarenta
pessoas, a página da seleção passaria a ser uma lista de nomes.

## D-008 — O mínimo público: nome, protocolo, vaga e lista, mais o vencimento

**Decisão** (3ª decisão do usuário). Os quatro identificadores que a divulgação do resultado e a
relação de habilitados já publicam, e o vencimento, que é o prazo do ato. Fica fora tudo que o
cadastro tem e a identificação não pede, e — com atenção — três coisas que parecem inofensivas:

- **A espécie da convocação.** *"Para regularizar o indeferimento"* diz em público que a documentação
  da pessoa foi indeferida antes. A relação diz quem foi convocado, e não por quê.
- **O fundamento.** É texto livre, e a `125` mostrou que ele pode citar terceiro.
- **O desfecho e a situação documental.** Estar convocado não é ter a documentação aceita (pedido,
  §6); e o desfecho é posterior ao ato.

**A lista de concorrência.** Revela que a pessoa concorre por reserva (PPI, PcD), o que pode indicar
dado sensível. Mas a divulgação do resultado já publica, por lista e com nome, a ordem de cada
reserva: escondê-la aqui não protegeria ninguém e tiraria a conferência de que a ordem da reserva foi
respeitada.

**CPF nem mascarado.** O protocolo da inscrição já desambigua homônimos, e o padrão do GPS — resultado,
sorteio — não publica CPF em forma nenhuma.

## D-009 — Publicações sucessivas, numeradas por Edital; grupos por vaga e lista

**Decisão.** O número é sequencial por Edital, atribuído dentro da trava do Processo, com
`UniqueConstraint(edital, numero)` como segunda guarda. Uma publicação reúne quantos recortes a
comissão escolher, em grupos por vaga e lista (FR-5714); a 2ª chamada de uma pessoa (suplência,
reclassificação) é outra convocação, e entra na publicação em que for publicada. O recorte é a chave
`(perfil, marco, lista)`; quando dois grupos de uma publicação teriam o mesmo rótulo (dois marcos da
mesma vaga e lista), o nome do marco os distingue.

**Alternativa recusada.** Uma publicação por recorte, como o gesto das pendentes: obrigaria a
comissão a fazer N atos para a 1ª chamada de um Edital com N vagas e listas, que é o retrabalho que o
pedido quer eliminar.

## D-010 — Compatibilidade: nada antigo muda, e o antigo pode ser divulgado

**Decisão.** Nenhuma migração de dados. As comunicações registradas antes desta feature continuam
como estão, e o portal continua dizendo *"Publicada em ‹referência›"* sem caminho para elas
(SC-1861). Uma convocação comunicada antes pode entrar numa publicação do GPS como *divulga*. O gesto
das pendentes continua aceitando a referência externa, e a mensagem individual continua saindo como
hoje (FR-5734).

## D-011 — *Publicação de convocados*, e não *chamada*

**Decisão.** O ato se chama *publicação de convocados*, numerada (*"1ª publicação de convocados"*), e
a seção pública, *Convocações*. A palavra *chamada* não nomeia o ato: no GPS ela já é a convocação de
uma pessoa — o campo `chamada`, a seção *"Chamadas praticadas"* da `143`, a *"2ª chamada"* de quem foi
reclassificado. Chamar a publicação de *"1ª chamada"* faria a mesma tela dizer *"a 2ª chamada de Ana
saiu na 1ª chamada"*.

## D-012 — A declaração do veículo, no ato, só quando a publicação convoca

**Decisão** (1ª decisão do usuário). Campo de texto no formulário de confirmação, obrigatório quando
alguma pessoa tem efeito *convoca*, gravado em `declaracao_do_veiculo` e na trilha. É o molde da
declaração de encerramento do prazo recursal da `017`: quem pratica o ato declara o que o sistema não
verifica, e a declaração fica com autor. Sem efeito *convoca*, o campo não aparece e o comando grava
vazio — aceitá-lo ali registraria afirmação sem objeto.

## D-013 — A autoridade da `060`, e o documento no compositor comum

**Decisão** (4ª decisão do usuário). `contexto_do_ato(edital, autoridade, agora)`, a mesma conferência
da publicação do Edital, da Retificação e do resultado. O documento é o quarto que entra pela costura
do compositor (Edital, comprovante, resultado): timbre da unidade, identificação, um bloco por grupo
com as pessoas em tabela, as orientações, a autoridade e o resumo dos bytes do conteúdo. Determinístico
— o instante impresso é o da publicação —, e por isso o mesmo conteúdo produz o mesmo arquivo.
