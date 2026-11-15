# Research: A orientação da verificação da autodeclaração

As decisões técnicas do plano. As de domínio estão na spec (`D-001` a `D-007`); as daqui são `T-`.
Cada uma diz o que se escolheu, por quê e o que se descartou.

## T-001 — Os passos se derivam na view, de uma vez, e a situação continua pura

**Decisão.** Um módulo novo, `portal/passo_da_etapa.py`, com `passos_da_inscricao(inscricao,
conteudo, resultados_visiveis, agora)`. Ele percorre as Etapas do conteúdo vigente que a view já leu,
e só para as que são restritas e alcançam a inscrição (`editais/domain/alcance.py`, puro) consulta:

1. a participação, por `prontidao.participa_da_etapa`, que passa a aceitar `conteudo=` e
   `modalidade=` e deixa de reler a versão e a Modalidade (de ~9 para ~4 consultas);
2. se há parecer concluído (`ConclusaoAvaliacao`) e se há Resultado vigente (`ResultadoEtapa.vigentes`),
   numa consulta cada.

A visibilidade sai de `resultados_visiveis`, que a view já paga: há dict com aquele `etapa_id`. O
resultado é uma lista de `Passo` (data-model), ordenada pelo início do período (sem período por
último), que a view passa a `situacao_da_inscricao`.

**Por quê.** `situacao_da_inscricao` é pura e o teste de custo a prende em zero consultas. Derivar fora
dela e entregar o fato pronto é o mesmo padrão de `convocacao`, `desfecho` e `estado`.

**Descartado.** `participacao_detalhada`, que trabalha sobre a população inteira; reler a participação
pelo panorama da Etapa, que custa por Etapa e não por inscrição; guardar o estado do passo.

## T-002 — O período sai do conteúdo já lido, por uma função só

**Decisão.** A função pura `periodo(conteudo, etapa)` da `166` (`verificacao/application/
disponibilidade.py`) muda para `editais/domain/cronograma.py` como `periodo_da_etapa`, e a `166`
passa a importá-la. O degrau, as células do Centro e a linha de avaliar a usam com o conteúdo que cada
leitor já tem.

**Por quê.** É o achado A-2: a `166` escreveu o leitor geral dentro do app do vídeo. Mover a função é a
menor mudança que dá um leitor só a esta entrega. `evento_vigente` (`comissoes/domain/etapas.py`)
relê a versão a cada chamada e fica onde está: trocar a Mesa de leitor seria a refatoração geral que o
pedido exclui.

## T-003 — O degrau entra entre a eliminação e as classificadas

**Decisão.** Em `situacao_da_inscricao`, depois do bloco `ELIMINADO` e antes de `classificadas`, o
primeiro passo da lista vira a situação, com o código `PASSO` e três rótulos (contracts). Na
convocação, cada passo entra como linha do porquê. Os outros passos, quando há mais de um, entram como
linha do porquê do primeiro.

A `Acao` existente basta:

- `principal`: o quando e o como, com as datas no texto;
- `consequencia`: a frase da ausência (`efeito_da_ausencia`, `resultados/domain/efeito.py`);
- `secundaria`, `secundaria_link` e `secundaria_rotulo`: "No Edital, veja a etapa {nome}." e "Ver o
  Edital vigente", para `portal:selecao`.

O campo `prazo` **não** é usado: o template o escreve como "Prazo desta convocação".

**Descartado.** Um template novo para o degrau (a situação já tem o seu) e a âncora
`#documentos-titulo`, que só existe quando houve Retificação ou anexos.

**Com o vídeo** (FR-7312): o degrau diz as duas formas no texto, com o mesmo peso ("Você pode gravar
um vídeo curto ou fazer a entrevista ao vivo. As duas formas valem igual."), e leva por "Ver como
funciona" à página da `166`, onde estão os dois botões. Dois botões no degrau seriam um segundo lugar
de escolha para a mesma coisa, e "Prefiro entrevista ao vivo" não grava nada (não escolher já é o ao
vivo, pela `166`).

## T-004 — A origem `PASSO` cita a Etapa, e não um marco

**Decisão.** Na migration `avisos/0004_origem_passo`:

- `Aviso.marco_id` passa a aceitar nulo, e entra `Aviso.etapa_id` (UUID, nulo);
- o CHECK da origem exige `etapa_id` e `marco_id` nulo em `PASSO`, e o contrário nas outras três;
- `natureza` e `referencia_da_publicacao` vazios em `PASSO`, como em `PENDENCIA`.

Um gesto grava **um Aviso por Etapa**, com `perfil_id` também nulo no passo. *Revisto na
implementação:* o plano previa um Aviso por Perfil para manter `perfil_id` não nulo, mas nenhuma
leitura dos avisos agrupa por Perfil — a lista do Edital lê a origem e o marco —, e um gesto que
gravasse vários avisos pediria várias prévias e várias assinaturas para o mesmo ato. O CHECK exige
`etapa_id` e `marco_id` nulo no passo, e `marco_id` e `perfil_id` nas outras três.

O fluxo é o da `RESULTADO`:

- a porta é `aviso:enviar` ou a presidência ativa (`comando.base_do_aviso`), escrita de forma
  explícita;
- prévia, confirmação, `REENVIO_DE_FALHAS` e `REENVIO_JUSTIFICADO`, com o despacho sem ramo novo.

O universo (`destinatarios.universo_do_passo`) é o dos participantes da Etapa sem Resultado, tirado
do panorama da Etapa. "Já avisado" é existir destinatário de aviso `PASSO` daquela Etapa e inscrição
que o despacho não interrompeu, no molde de `_chamada_ja_avisada`.

**Por quê.** Os gatilhos append-only não mudam: a migration só mexe em nulabilidade, coluna nova e
CHECK, como a `0002` da `PENDENCIA` mexeu em CHECK. Pôr a Etapa em `marco_id` daria ao campo dois
significados, e um leitor do marco leria uma Etapa.

**Descartado.**

- O caminho da `PENDENCIA`, com texto fixo, sem modelo e um aviso por pessoa: o pedido é um aviso com
  prévia e modelo da unidade.
- Um Aviso por Perfil: o plano original; ver acima.

## T-005 — O modelo inicial do passo tem marca própria

**Decisão.** `ModeloDeAviso` ganha `chave_inicial` (texto, vazio por padrão). Os três modelos de hoje continuam
regidos pela regra de hoje: nenhum é criado quando a unidade já tem algum modelo inicial **sem**
chave. O quarto, `chave_inicial="PASSO"`, é criado quando a unidade não tem modelo com essa chave.
Sem escolha na prévia, o aviso do passo abre com esse modelo, e os outros avisos nunca com ele (ele
usa uma variável que só o passo tem). O
comando `semear_unidades` continua imprimindo "Modelos de aviso: C criados". Num banco que já existe,
a primeira passada depois da migration cria um por unidade; depois disso, zero.

**Por quê.** A guarda pelo nome recriaria o modelo da unidade que o renomeou, e a regra "algum inicial
existe" nunca criaria o quarto. Os modelos não têm origem (servem a qualquer uma), e a marca é a forma
mínima de saber que este já nasceu.

**Consequência.** Os testes que contam três modelos passam a contar quatro num banco novo. O
`CLAUDE.md` muda a frase "três na primeira vez".

## T-006 — As pendências da Etapa restrita são células da Etapa, com uma natureza nova só para o aviso

**Decisão.** Em `_Leitor._etapas_no_edital`, só quando a Etapa é restrita, os fatos ganham quatro
entradas:

| Fato | De onde vem |
|---|---|
| `faltam_por_membro` | `carga_por_avaliador`, filtrada pelos participantes do panorama, para coincidir com a Mesa (FR-7328) |
| `nao_avisadas` | participantes sem Resultado, menos os já avisados, numa consulta |
| `sem_desfecho_vencido` | participantes sem conclusão elegível e sem Resultado, quando `agora > fim` |
| `fim` | `periodo_da_etapa` |

`situacoes_da_etapa` monta as células a partir deles.

- A nota da célula AVALIAR "dos outros" passa a trazer "Bruno 2, Carla 2" quando a lê a presidência,
  com o `ate` do fim do período.
- Entra a célula `AVISAR`, natureza nova, de quem conduz, que leva à confirmação do aviso do passo.
- Entra a célula DISTRIBUIR "Registrar a ausência ou os pareceres de N inscrições", que leva à
  distribuição, onde a Ocorrência se registra.
- A natureza `AVISAR` entra em `centro._DA_NATUREZA` (fase de avaliação), em `conceitos.CONCEITOS` e em
  `NATUREZAS_CONHECIDAS`, e ganha marcador no teste de coerência.

**Por quê.** São a Etapa e as telas de hoje; a única ação sem natureza que a descreva é avisar.

**Descartado.** Uma natureza "verificação" (Q-1) e uma página de pendências da verificação.

**Risco.** A Etapa `SEM_EFEITO` sai cedo em `NAO_SE_APLICA` (`andamento.py`, ramo da expectativa). A
Etapa restrita lida pelo marco (`164`) não é `SEM_EFEITO`, e um teste prende isso.

## T-007 — O encaminhamento ao vivo conta pelo plano da consolidação, só onde o vídeo é admitido

**Decisão.** Quando `admissao.admite_video(etapa)` é verdadeiro, que é puro, o `_Leitor` conta as
recusas `ENCAMINHAR_AO_VIVO` de `consolidacao._planejar` sobre o panorama já calculado. A célula
CONSOLIDAR "Encaminhar N inscrições à entrevista ao vivo" leva à conferência da consolidação. Com a
chave desligada, a célula continua aparecendo quando há o que encaminhar (achado I1 da `166`).

**Por quê.** É a mesma conta que a conferência faz, sem a consulta da `a_encaminhar`, que recalcula o
panorama. Na Etapa que não admite vídeo, nada é calculado.

## T-008 — O fim do período chega à linha de avaliar pelo item da Atribuição

**Decisão.** `comissoes/application/selectors._atribuicoes` já tem o dict da Etapa do conteúdo vigente.
Passa a guardar `fim` (`periodo_da_etapa`) no item, e `atividades.linhas_de_avaliacao` o põe em
`Providencia.ate`. O `_atividade.html` passa a escrever "até dd/mm" como o Centro escreve, e com
isso vale para toda Etapa com período (Q-5).

**Por quê.** É zero consulta a mais. `evento_vigente` custaria uma por Etapa.

## T-009 — A advertência do nome é uma `WARNING` da validação de publicação

**Decisão.** `validation._nome_com_termo_tecnico`, junto de `_coerencia_do_alcance`, gera
`ValidationFinding(Severity.WARNING, "nome_da_etapa_restrita_com_termo_tecnico", …)` para a Etapa
restrita cujo nome case com os termos da FR-7330. A mensagem nomeia o termo e diz que o candidato lê o
nome no acompanhamento; não sugere nome. Ela aparece nas pendências do passo das Etapas na composição,
como `_etapa_sem_evento`.

**Por quê.** É o mecanismo de advertência que a composição já tem. Não há "advertência ao gravar"
separada, e criar uma seria estrutura nova.

## T-010 — O cenário C18 usa o molde dos cenários de avaliação, com dois avaliadores

**Decisão.** A `montar_c18` reaproveita `Montagem`: elabora com uma Etapa decisória restrita a uma
Modalidade reservada, colegiada com `evaluationsPerRegistration = 2` e a regra "confirma só por
unanimidade". A unanimidade admite número par (`165`), e `constituir_comissao` dá a presidência e dois
avaliadores. O período começa no dia da carga e vai até sete dias depois.

O cenário monta quatro alcançados:

- um não avisado;
- um avisado, por aviso confirmado e não despachado;
- um com um parecer de dois;
- um com os dois pareceres, à espera da consolidação.

Monta também um inscrito só na ampla. A distribuição a dois avaliadores é um passo novo da `Montagem`
(`distribuir(avaliadores=2)`). O teste do cenário (FR-7334) confere os estados no Centro e no
acompanhamento.

**Por quê.** É o menor cenário que mostra todas as pendências que um período em curso permite. O
período vencido e o Resultado visível precisam de tempo ou de marco publicado, e ficam na suíte.

**Consequência.** Os três testes que contam 17 cenários passam a contar 18.
