# Pesquisa técnica — 024 Descoberta e Transparência no Portal Público

**Data:** 2026-09-09 · **Spec:** [spec.md](spec.md)

Onze questões, todas resolvidas contra o código desta árvore. Nenhuma ficou como
NEEDS CLARIFICATION.

O fio comum: **esta feature não inventa dado**. Toda questão abaixo é sobre onde ler o que já
existe, e onde pôr o que passa a ser lido por duas telas em vez de uma.

---

## T-001 — De onde o portal lê o histórico de atos publicados

**Decisão.** Um selector próprio em `publicacoes/application/selectors.py`, que devolve as
Publicações do Edital e as Retificações **publicadas**, em ordem cronológica, sem cursor.

**Racional.** O `public_history` existente serve à API pública e faz três coisas que a página não
quer: mescla um terceiro tipo — a Versão Consolidada —, pagina por cursor e devolve `limit` linhas
do conjunto misturado. Filtrar a versão consolidada **depois** de paginar produziria páginas curtas
ou vazias por acaso: um Edital com muitas versões consolidadas devolveria uma primeira página só de
versões, e a Retificação que interessa cairia na segunda.

E há uma razão de domínio, não só de mecânica: a Versão Consolidada é a máquina que produz o
conteúdo vigente, não um ato que alguém praticou. Numa página pública ela é ruído — a `D-006`
decide que a página mostra o vigente e explica como se chegou nele pelos **atos**.

Um Edital tem uma publicação de abertura e um punhado de Retificações. Sem cursor, sem paginação.

**Alternativas descartadas.**

- *Consumir a API pública por HTTP a partir da view* — acoplaria a página ao próprio servidor e
  transformaria uma leitura em requisição de rede. O portal já lê selectors diretamente.
- *Reusar `public_history` filtrando* — o problema de paginação acima.

---

## T-002 — Como dizer, em linguagem do domínio, o que a Retificação alterou

**Decisão.** Um tradutor de `target_path` → *onde* e *o quê*, novo, em
`publicacoes/domain/`, cobrindo as coleções do conteúdo publicado: Perfil, Evento do cronograma,
Etapa, Documento Exigido, Anexo, Seção — e o campo de topo do Edital. Ele devolve **onde** a
alteração caiu, nomeado pelo rótulo daquela entidade no conteúdo-base, e **qual campo** mudou. Não
devolve valor anterior nem novo.

**Racional.** `AlteracaoNormativa.target_path` é endereçamento estrutural
(`/profiles/id=<uuid>/immediateVacancies`). Publicá-lo cru violaria a `D-005` e o Princípio I: é
vocabulário do sistema, não do domínio.

A gestão já tem um tradutor parcial — `_alteracoes_legiveis` em `interface/views.py` —, e ele
humaniza **apenas** `/attachments/`; todo o resto cai no caminho cru. Ele também calcula *antes* e
*depois*, que a tela de homologação precisa e a página pública não: quem aprova confere valores;
quem se candidata precisa saber **que** as vagas do Perfil X mudaram, e o documento da Retificação
diz o resto.

Por isso o tradutor novo é mais estreito e vive no domínio de publicações, de onde as duas telas
podem chamá-lo. **A tela da gestão não é alterada nesta feature** — reaproveitá-la é achado
registrado, não escopo (§7 da spec).

**Caminho não previsto** cai num rótulo genérico que nomeia a seção do Edital quando reconhecível, e
é omitido quando não é. Omitir é a única saída coerente com a `D-009`: inventar rótulo para um
caminho desconhecido afirmaria algo sobre o Edital.

**Alternativas descartadas.**

- *Mostrar o `target_path` cru* — `D-005`.
- *Mover `_alteracoes_legiveis` para o domínio e usá-lo nos dois lugares* — arrastaria a gestão para
  dentro desta feature, com o cálculo de antes/depois que a página pública não usa. Fica registrado.
- *Derivar o que mudou comparando duas versões consolidadas* — reimplementaria o diff que a
  Retificação já declara, e produziria diferença onde o ato não declarou alteração.

---

## T-003 — Onde vive o cronograma, agora que duas telas o mostram

**Decisão.** `_cronograma` sai de `portal/views.py` e vira função pública de um módulo de leitura do
portal, chamada pelas duas views. A situação do Evento continua calculada onde está — a regra não
muda, muda o endereço.

**Racional.** A função já existe e já é correta, inclusive na parte sutil: situação descreve o
Evento e não a pessoa (`FR-126`, e a `FR-076` da `010` que a originou). Duplicá-la para a página
pública criaria duas verdades sobre "em curso" — que é exatamente o defeito que a `011` registrou
ao ter duas ordenações por nome no mesmo arquivo.

**Alternativa descartada.** *Chamar `views._cronograma` a partir da outra view* — função privada
usada de fora é acoplamento sem contrato; e o `_` deixaria de dizer a verdade.

### O que o compartilhamento **não** alcança: a ausência

A área do candidato, quando não há cronograma publicado, escreve `O Edital não publicou cronograma.`
A página pública não pode escrever isso: a `FR-128` e a `D-009` mandam **omitir a seção**.

Não é inconsistência a corrigir, e sim contexto diferente. Quem já se inscreveu está numa tela sobre
a **própria inscrição**, e o bloco vazio ali seria um buraco sem explicação; quem está decidindo lê
uma página cujo assunto é o Edital, e uma frase sobre o que ele não publicou afirma uma omissão.

**Consequência para o desenho:** o parcial compartilhado renderiza **a lista de Eventos**, e nada
mais. O caso vazio fica com cada chamador — a área do candidato mantém a frase que já tem, a página
pública não desenha seção alguma.

**E um cuidado de execução:** `tests/integration/portal/test_acompanhamento.py` afirma sobre a
substring `class="marco em_curso"`. A extração do parcial tem de preservar a marcação exatamente,
ou quebra um teste que nada tem a ver com esta feature.

---

## T-004 — A forma da consulta da vitrine

**Decisão.** `GET` com parâmetros nomeados, sem sessão e sem script:

| Parâmetro | Valores | Ausente significa |
|---|---|---|
| `busca` | texto livre | sem busca |
| `unidade` | escopo institucional publicado | todas |
| `situacao` | `aberta`, `futura`, `encerrada`, `sem-prazo` | todas |
| `perfil` | denominação de Perfil publicada | todos |
| `ordem` | `prazo` (padrão), `recentes` | `prazo` |

Valor não reconhecido é tratado como ausência do filtro — nunca como erro. O formulário é um
`<form method="get" role="search">`, como o da tela de inscrições da gestão.

**Racional.** É o padrão já estabelecido no repositório (`interface/views.py`, inscrições recebidas:
`busca`, `perfil`, `modalidade`, com `_querystring` montando o filtro que viaja nos links). Reusar a
forma conhecida é mais barato que inventar outra, e o `role="search"` já é o que a base de
acessibilidade do projeto espera.

`GET` também é o que satisfaz `FR-143` e `UX-017` sem esforço: a consulta **é** o endereço, e a
página funciona sem JavaScript.

**Sobre valor inválido.** Recusar com erro daria a um endereço colado um comportamento pior do que o
de não filtrar, e abriria uma superfície de mensagem de erro numa página anônima. Ignorar é o que a
`FR-142` já pede para o caso vizinho — consulta sem resultado não é erro.

**Alternativa descartada.** *Filtro por JavaScript no cliente* — quebraria `UX-017` e `FR-143`, e
faria a lista depender de o navegador executar script para mostrar o que o servidor já sabe.

---

## T-005 — Busca que ignora acento e caixa

**Decisão.** Uma função de dobra — NFKD, remoção de combinantes, `casefold` — em
`processo_seletivo/shared/`, usada pela busca da vitrine. A `comissoes/application/selectors.py`
passa a delegar a dela para essa função, sem mudar comportamento.

**Racional.** A dobra já existe duas vezes na árvore com finalidades diferentes: `comissoes` a usa
para ordenar nomes, e `sorteios/domain/normalizacao.py` a usa para produzir material canônico de
sorteio. A terceira cópia é o risco real — o comentário da `comissoes` registra que **duas**
implementações no mesmo arquivo já foram o defeito.

**`sorteios` não é tocado.** A normalização de lá é regra auditável do sorteio, com forma canônica
própria e prova pública dependendo dela. Unificá-la com uma dobra de exibição confundiria dois
propósitos e mexeria em código cuja saída é verificável por terceiros.

**Alternativa descartada.** *Importar a de `comissoes` no portal* — dependência entre apps sem
razão de domínio; comissão não tem nada a dizer sobre a vitrine.

---

## T-006 — Qual instante é "mais recente"

**Decisão.** `valid_from` da versão consolidada vigente — o início de vigência do que está sendo
mostrado.

**Racional.** É o instante do que a página exibe. `published_at` da publicação de abertura diria
quando o Edital nasceu, e um Edital retificado ontem apareceria como antigo; `materialized_at` é
quando o sistema montou a versão, que é dado de máquina e pode mudar sem ato nenhum.

A vitrine já ordena por `-valid_from, -materialized_at` ao escolher a versão vigente por Edital, e a
ordenação de exibição passa a usar a mesma chave.

**Alternativa descartada.** *`published_at` da publicação mais recente do Edital* — equivalente na
maioria dos casos e divergente justamente no caso que interessa: a Retificação com vigência futura,
publicada hoje e vigente na semana que vem.

---

## T-007 — Preservar a consulta ao voltar

**Decisão.** O link do cartão carrega a consulta corrente; a página da seleção lê o que veio e monta
com ela o caminho de volta. Nada é gravado.

**Racional.** É a mesma técnica do `_querystring` da gestão, e o comentário que ele carrega descreve
exatamente o defeito a evitar: *"o filtro viaja em todo link da tela… foi como o cartão acabou
perdendo a busca que o formulário preservava"*.

Guardar a consulta em sessão seria a alternativa aparentemente mais simples e é a que a `D-002`
recusa: duas abas na mesma vitrine passariam a mostrar listas diferentes sem explicação na tela.

**O que a página da seleção faz com um parâmetro estranho:** nada além de devolvê-lo ao link de
volta, e só depois de conferir que ele é uma consulta reconhecida da vitrine. Repassar texto
arbitrário para dentro de um endereço é como se abre redirecionamento — o portal já trata disso em
`_destino_seguro`, e o critério aqui é mais estreito ainda: só os parâmetros da T-004 sobrevivem.

---

## T-008 — Onde ficam os testes, e em que camada

**Decisão.**

| Camada | Onde | O que prova |
|---|---|---|
| Integração do portal | `tests/integration/portal/` | as duas telas contra o servidor real, com conteúdo publicado e Edital retificado |
| Domínio | `tests/unit/` ou junto do módulo | o tradutor de `target_path` e a dobra de texto |
| Acessibilidade | `tests/interface/test_acessibilidade_do_portal.py` | rótulo do formulário de busca, foco, situação sem depender de cor |

Os arquivos existentes que a feature amplia: `test_vitrine.py`, `test_detalhe_selecao.py`. O
histórico ganha arquivo próprio, porque exige a fixture de retificação.

**Racional.** É a divisão que o repositório já usa, e a fixture `retify` de
`tests/fixtures/publicacao.py` já existe — `test_aviso_de_versao.py` a usa para provar que o Edital
mudou depois do envio. É a mesma montagem que a `US2` precisa.

---

## T-009 — O custo de trocar dois grupos por quatro

**Decisão.** A view deixa de calcular `abertas` e `outras` e passa a agrupar pelas quatro situações
que `periodo_de_inscricoes` já devolve, preservando a ordem de urgência dentro de cada grupo.

**Racional.** É a mudança mais barata da feature: o domínio já distingue `ABERTO`, `FUTURO`,
`ENCERRADO` e a ausência de período designado. O que existe hoje é a tela fundindo três em um.

**A ausência não vira estado novo.** O `periodo.py` é explícito: *"a ausência não é um quarto estado
da inscrição: é o Edital que não recebe inscrição por este sistema"*. O agrupamento da vitrine
reflete isso — o grupo existe na tela, e nenhuma frase de prazo é escrita para ele (`FR-149`).

---

## T-010 — Onde a frase do cadastro reserva é montada, e o que não muda

**Decisão.** Só o portal muda. O mapa `RESERVA` de `portal/views.py` ganha a leitura que a `D-007`
pede, e o destaque tipográfico passa da quantidade para a oferta quando não há vaga imediata.

**O que NÃO muda:** o mapa `RESERVA` de `publicacoes/infrastructure/pdf.py`. Aquele texto é o do
**documento publicado**, e documento publicado não se reescreve — mudá-lo faria documentos futuros
divergirem dos já publicados pelo mesmo conteúdo, contra o Princípio II.

Também não muda `interface/revisao.py` nem `interface/forms.py`: são a tela de quem elabora, que
nomeia a forma que está escolhendo.

**Consequência aceita e declarada:** a página passa a dizer da reserva algo que o PDF diz com outras
palavras. Não é divergência normativa — o fato é o mesmo, `UNLIMITED`, e a fonte é a mesma. É a
diferença entre o texto do ato e a leitura de quem decide, que o repositório já pratica ao traduzir
`UNLIMITED` de formas diferentes nos dois canais.

---

## T-011 — O que a busca varre

**Decisão.** O texto público que a própria vitrine já monta para o cartão: título do Processo,
título e número do Edital, unidade e denominação dos Perfis. Nada além disso.

**Racional.** É o que `FR-138` declara, e tem uma propriedade que importa: **o que se busca é o que
se vê**. Varrer descrição, requisitos ou o texto das seções faria a lista devolver cartões em que o
termo procurado não aparece em lugar nenhum — o resultado pareceria erro.

E há o custo: buscar dentro das seções obrigaria a percorrer o conteúdo inteiro de cada versão
publicada a cada tecla, que é a porta para o índice que a `D-003` adiou.

**Alternativa descartada.** *Busca em todo o conteúdo publicado* — vira a feature de índice, que
está fora de escopo.

---

## Riscos residuais

| Risco | Mitigação |
|---|---|
| O tradutor de `target_path` não reconhecer um caminho legítimo e omitir a linha | teste cobrindo cada coleção do conteúdo publicado; a omissão é preferível ao rótulo inventado (`D-009`) |
| A consulta na querystring virar superfície de redirecionamento | só os parâmetros da T-004 atravessam para o link de volta (T-007) |
| A busca em memória tornar-se lenta sem ninguém perceber | o sinal está nomeado na `D-003`; não há alarme automático, e não se constrói um agora |
| Divergência de redação entre o PDF e a página sobre o cadastro reserva | declarada e aceita na T-010 |
