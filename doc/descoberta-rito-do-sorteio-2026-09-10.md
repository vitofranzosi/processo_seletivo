# Descoberta — o rito do sorteio, da comissão ao cidadão

Exploração do processo de sorteio tal como ele existe hoje no código, na `021` e nas telas, com o
objetivo de responder a uma pergunta só:

> Como transformar o sorteio num rito operacional simples para a comissão e, ao mesmo tempo,
> extremamente claro, verificável e compreensível para o cidadão comum?

> **Não cria requisito, não decide prioridade e não abre spec.** O que se registra é o rito real, as
> lacunas com evidência, e a classificação de cada achado. Priorizar é do usuário.

> **Estado, em 10/09/2026, depois desta exploração.** Os oito achados classificados como **P0** no
> §M foram corrigidos na mesma data, como Phase 12 da `021` — todos de tela e navegação, nenhuma
> migration, nenhum toque na chave, na ordem, na semente ou no manifesto. São eles: E-01, E-02,
> E-03, E-04, E-05, E-06, E-07, E-12 e E-19 — mais o **E-10**, que o usuário mandou corrigir junto
> por estar na mesma função.
>
> Uma ressalva de honestidade sobre o **E-05**: enquanto esta exploração corria, uma sessão
> paralela o encontrou por outro caminho — a validação da `022` — e o fechou no `main`
> (`40f783d`), em três camadas, junto com o **E-11**. O que esta branch acrescentou ali é a
> leitura, e não a porta. O achado é o mesmo; o mérito da correção é de lá.
>
> O restante do relatório descreve o sistema **como ele
> foi encontrado**, e é assim que fica: o registro do que se mediu, e não do que se corrigiu.

Base: `specs/021-sorteio-publico-auditavel/` (spec, research, data-model, contracts, quickstart),
`backend/processo_seletivo/sorteios/`, `interface/`, `portal/`, `divulgacao/`, `classificacao/`,
`editais/`, `seed_demo`, e a suíte da feature — **216 casos, todos passando** contra PostgreSQL em
10/09/2026. O que segue não é regressão: é o que a suíte verde não cobre.

---

## A · Como o sorteio funciona hoje

O motor está construído e é sólido. Os treze passos que o usuário pediu para distinguir, medidos
contra o código:

| # | Passo | Existe? | Onde |
|---|---|---|---|
| 1 | Preparação do Edital | **sistema** | composição normal do Edital (`001`, `006`) |
| 2 | Definição do método de sorteio | **sistema** | `drawMethod` no marco de classificação, `_marco.html`, validado em `editais/domain/perfis.py` |
| 3 | Encerramento das inscrições | **sistema** | cronograma / `is_registration_period` |
| 4 | Quem está apto a participar | **sistema** | `sorteios/domain/projecao.py` — projeção, nunca digitação |
| 5 | Publicação/congelamento da relação | **sistema** | `publicar_relacao` — publicar **é** congelar |
| 6 | Momento anterior à transmissão | **ausente** | nada no sistema diz que há um sorteio marcado, quando, ou onde |
| 7 | Abertura da transmissão | **fora** | canal externo, por decisão (`D-012`, `FR-065`) |
| 8 | Obtenção da informação externa | **sistema** | `observar_ocorrencia` + adaptador da Loteria Federal |
| 9 | Realização do sorteio | **sistema** | `constituir_sorteio`, um comando atômico |
| 10 | Geração da ordem | **sistema** | `sorteios/domain/chave.py` — SHA-256 sobre bytes canônicos |
| 11 | Conferência | **implícito** | não há passo de conferência; a ordem nasce publicada no ato |
| 12 | Publicação da classificação | **sistema, por outra porta** | fluxo da `017`, alcançado pela tela de ordenação |
| 13 | Verificação posterior pelo cidadão | **sistema** | página de verificação + manifesto + verificador em Node |

**O que é manual:** declarar o método (digitando `2026-11-20T20:00:00-03:00` à mão num campo de
texto), decidir quando congelar, decidir quando observar, decidir quando clicar em sortear, achar a
URL da tela do sorteio, ir até a publicação do resultado por outra tela, e divulgar em qualquer
canal externo que a relação e o sorteio existem.

**O que é implícito:** a data e a hora do sorteio; o local da transmissão; a ligação entre o evento
do Cronograma que diz "Sorteio público" e o marco que sorteia; a conferência antes de publicar; e o
caminho da tela do sorteio para a divulgação.

**O que está ausente:** tudo o que faria uma pessoa de fora saber que existe um sorteio antes de ele
acontecer. Ver §C.

---

## B · Jornada operacional atual, passo a passo

O que a comissão de fato faz hoje, com o custo real de cada passo:

1. **Declarar o método** — na composição do Edital, num `fieldset` com oito campos, entre eles
   `occurrenceAt` em RFC 3339 com fuso, digitado à mão. Publicar o Edital.
2. **Descobrir a URL da tela do sorteio.** `/gestao/editais/<uuid>/marcos/<uuid>/sorteio`. **Nenhum
   link do sistema leva até ela** (§E-04).
3. **Publicar e congelar a relação** — um clique por recorte. A faixa verde confirma corretamente.
4. **Esperar o dia.** Nada no sistema lembra, avisa ou marca.
5. **Observar a ocorrência** — um clique, ao vivo. A faixa que responde diz *"Relação publicada e
   congelada, com  participante. O resumo é ."* (§E-01).
6. **Realizar o sorteio** — um clique. A faixa que responde diz *"Relação publicada e congelada, com
   327 participantes. O resumo é ."* (§E-01). Um duplo clique responde em vermelho *"Não foi possível
   publicar: já existe um sorteio para esta relação"* — depois de ter dado certo (§E-03).
7. **Publicar o resultado** — sair da tela do sorteio, voltar ao Edital, entrar em "Marcos
   classificatórios", abrir a tela de **ordenação**, clicar no ato vigente, abrir o ato, publicar.
   Cinco telas, nenhuma delas linkada a partir do sorteio.

O modelo mental da equipe — *prepara a relação → abre o sorteio → obtém a semente → sorteia →
apresenta a ordem → publica* — **está inteiro no sistema**, e essa é a boa notícia. O que a evolução
introduziu de novo, e o que custou:

| | Antes | Hoje | Efeito |
|---|---|---|---|
| Relação | planilha, publicada em PDF avulso | projetada, numerada, congelada, com resumo | **mais simples**, e é ganho puro |
| Semente | alguém digita | vem da extração declarada no Edital | **mais simples no dia**, mais trabalho na elaboração |
| Sortear | software de terceiro | um botão | igual |
| Ordem | tela do software | ato imutável no sistema | **mais simples** |
| Publicar | copiar e colar a lista | fluxo da `017` | **mais simples**, mas por outra porta |
| Preparar | nada a declarar | oito campos técnicos no Edital, um deles em RFC 3339 | **mais difícil**, e é onde o erro nasce |
| Errar | refazer o sorteio | anular = Retificação + relação nova + ocorrência nova + sucessor | **muito mais difícil**, e é deliberado (`D-017`) |

**Novos riscos humanos, todos concentrados no dia:**

- não achar a tela (§E-04);
- clicar em "Emitir ordem" na tela de ordenação, que é para onde o Edital manda, e travar o sorteio
  antes de ele acontecer (§E-05);
- ler uma mensagem de sucesso falsa no ar (§E-01);
- ler uma mensagem de erro falsa depois de um duplo clique (§E-03);
- um blip de rede de cinco segundos gravar indisponibilidade **definitiva** e mandar o certame para
  a extração seguinte, que talvez só aconteça na semana que vem (§E-08);
- transmitir uma tabela que **não é** a relação congelada (§E-09).

---

## C · Jornada pública atual

**Antes do sorteio.** Nada. A página pública do Edital (`portal/templates/portal/selecao.html`) tem
Vagas, Cronograma e Documentos — e nenhuma seção de sorteio. A relação congelada existe, é pública e
é imutável, e **só responde em `/sorteio/relacoes/<uuid>/`**: nenhuma página do portal a linka
(`grep relacao-de-habilitados` só encontra a tela de gestão, a própria página e o resultado
*depois* do sorteio). O candidato não descobre que está na relação, com que número, nem quando o
sorteio acontece — nem pela vitrine, nem pela página do Edital, nem pela área dele.

**Durante.** Nada. Por decisão correta o vídeo é externo (`FR-065`); mas o sistema também não guarda
o endereço dele. O `location` do Evento do Cronograma existe (`FR-056`, `FR-057`), é texto livre,
não é validado como URL e é renderizado como texto simples — não vira link.

**Depois.** Aqui o sistema entrega: a página do resultado publicado traz a seção *"Esta ordem foi
produzida por sorteio público"* com algoritmo, semente e três resumos, o caminho para a verificação,
o link para a relação, e o PDF oficial. A página de verificação recalcula das entradas e relata em
cinco degraus. O manifesto sai em JSON, e o verificador em Node vem com o `--resumo` já preenchido.

**Ou seja: a jornada pública existe inteira depois do fato e não existe antes dele.** É exatamente o
inverso do que a promessa da feature precisa — a frase que governa a `021` é *"a lista estava fechada
antes de existir a semente"*, e é justamente o "antes" que ninguém consegue ver acontecer.

### As quinze perguntas do cidadão

| # | Pergunta | Responde? | Onde, e o que falta |
|---|---|---|---|
| 1 | Eu estava habilitado? | **parcial** | a relação responde, se a pessoa tiver o UUID. A área do candidato não diz nada |
| 2 | Qual era a lista usada? | **sim** | a relação publicada, com critério escrito |
| 3 | Foi fechada antes da semente? | **tecnicamente sim, cognitivamente não** | o dado existe (dois instantes), mas nenhuma página os compara para o leitor |
| 4 | Quando ocorreu o sorteio? | **sim** | data e hora na verificação e no resultado |
| 5 | Onde acompanhar ao vivo? | **não** | o sistema não guarda o canal |
| 6 | Qual informação externa foi usada? | **não** | a verificação mostra *"Semente usada: 048337 065904…"*. Não diz "Loteria Federal", não diz "concurso 6098" |
| 7 | Já estava definida antes? | **não** | o `occurrence` está no manifesto e em nenhuma página |
| 8 | De onde vieram os números? | **não** | nada explica que são os cinco bilhetes premiados de uma extração da Caixa |
| 9 | Como viraram semente? | **não** | a regra existe (`normalization.text`) e não é exibida em canal público |
| 10 | Como a semente virou ordem? | **parcial** | "o algoritmo produz" — sem uma frase que uma pessoa entenda |
| 11 | Quem realizou o sorteio? | **não** | `executado_por` existe no banco, aparece na gestão, e **não** no portal nem no manifesto |
| 12 | Poderia sortear de novo? | **parcial** | a página diz que o ato é único; não explica o custo de anular |
| 13 | A lista publicada é a produzida? | **sim** | é o que a verificação prova, e bem |
| 14 | Consigo conferir depois? | **sim** | manifesto + verificador + relação |
| 15 | Preciso instalar algo? | **hoje, sim** | a conferência de verdade exige Node e linha de comando |

**Sete perguntas de quinze não têm resposta, e as sete são a cadeia da procedência dos números.** O
sistema responde soberbamente à pergunta do auditor — *"a ordem é reproduzível?"* — e mal à pergunta
do cidadão — *"de onde vieram esses números, e quem escolheu?"*. As duas não são a mesma pergunta.

---

## D · Modelo mental, e onde a interface o embaralha

A cadeia correta, e ela **existe** limpa no domínio:

```text
fonte                Loteria Federal                     ← declarada no Edital, vocabulário fechado
  ↓
ocorrência           concurso 6098, de 06/09/2026        ← declarada no Edital, antes do congelamento
  ↓
material bruto       048337 065904 007642 065308 038572  ← os cinco bilhetes premiados, como a fonte publicou
  ↓
normalização         DIGITOS_EM_SEQUENCIA                 ← regra do método, identificador fechado
  ↓
semente efetiva      "048337 065904 007642 065308 038572"
  ↓
algoritmo            IFES-SORTEIO-SHA256-v1               ← chave = SHA-256(domínio, resumo da relação, recorte, semente, número)
  ↓
ordem                números públicos por chave crescente
  ↓
classificação        PosicaoNaOrdem, 1..N, sem corte
  ↓
publicação           PublicacaoResultado + PDF + página pública
```

O modelo é limpo no código e **colapsa na interface**. Nas três páginas públicas, os sete primeiros
elos aparecem como um só campo:

```text
Semente usada: 048337 065904 007642 065308 038572
```

Fonte, concurso, data da extração, o que aqueles números são e como viraram semente **não aparecem
em página pública nenhuma**. Estão no manifesto — um JSON que se baixa. É a diferença entre ter o
dado e contar a história.

Na tela da comissão a cadeia aparece melhor (método, ocorrência, material bruto, "aconteceu não
antes de"), mas com o vocabulário do domínio: *ocorrência*, *material bruto*, *recorte*, *resumo
canônico*, *constituir*.

---

## E · Lacunas encontradas

Severidade: **crítica** = pode quebrar uma transmissão ao vivo ou o certame; **alta** = compromete a
promessa da feature; **média**; **baixa**.

| # | Achado | Evidência | Impacto | Tipo | Sev. | Freq. | Compl. | Recomendação preliminar |
|---|---|---|---|---|---|---|---|---|
| **E-01** | **A faixa de sucesso mente para três dos quatro comandos.** Uma frase única — *"Relação publicada e congelada, com N participantes. O resumo é X"* — responde a publicar, observar, sortear e anular | `interface/sorteio.html:15` + `views.py:4851,4880,4929,4960`, todos gravando em `session["resultado_do_sorteio"]`. Renderizado com o desfecho real de cada comando: após observar sai *"com  participante. O resumo é ."*; após sortear, *"com 327 participantes. O resumo é ."* | O momento mais visto do certame — o clique de sortear, ao vivo — responde com uma frase factualmente falsa e sem a informação que importa (semente, quantidade sorteada, manifesto) | UX da comissão / defeito | **crítica** | toda execução | baixa | Um desfecho por comando, com a frase do fato que aconteceu |
| **E-02** | **A faixa de erro mente pelo mesmo motivo**: *"Não foi possível publicar:"* prefixa recusas de observação, de sorteio e de anulação | mesmo par de arquivos, `session["erro_do_sorteio"]` | Ao vivo, o operador lê "não foi possível publicar" quando o que falhou foi a fonte externa | UX da comissão / defeito | **alta** | em toda recusa | baixa | Junto com E-01 |
| **E-03** | **Os formulários do sorteio não enviam chave de idempotência.** Cada envio gera `uuid4()` novo | `sorteio.html` — os quatro `form` mandam só identidades; `views.py:4941` `request.POST.get("chave_idempotencia") or uuid4().hex`. A tela de ordenação, ao contrário, envia a chave | Duplo clique no botão de sortear: o segundo pedido não é reconhecido como repetição, cai em `draw_already_constituted` e pinta a tela de vermelho **depois de o sorteio ter dado certo** | UX da comissão / defeito | **crítica** | duplo clique é comum sob pressão | baixa | Emitir a chave no GET e enviá-la no `form`, como a `015` já faz |
| **E-04** | **A tela do sorteio não é alcançável por link nenhum** no fluxo normal | `grep -rn "interface:sorteio" templates/` → zero. Só `supervisao.py:893`, e só quando já existe ato **obsoleto** | No dia, o operador precisa da URL decorada ou de um favorito. É o modo de falha que a Constituição §VI nomeia | UX da comissão / governança | **crítica** | toda execução | baixa | O marco que declara `drawMethod` linka para o sorteio no detalhe do Edital |
| **E-05** | **O detalhe do Edital manda o marco de sorteio para a tela de ordenação, e ela oferece "Emitir ordem"** | `detalhe.html:135` linka todo marco para `interface:ordenacao`; sem ato, `estado_do_marco` devolve `recomputavel=True` (`selectors.py:300`) e `ordenacao.html:82` mostra o botão; `emitir_ordem` não conhece `drawMethod` | Emitido, nasce o ato raiz do recorte; `constituir_sorteio` passa a recusar com `ordering_act_already_exists`, e o caminho de sucessor exige um `sorteio_anterior` que não existe. **O sorteio fica sem saída pela tela** | UX da comissão / defeito | **crítica** | um clique errado basta | média | Marco com método declarado não oferece emissão computada; o link do detalhe aponta para o sorteio |
| **E-06** | **Indisponibilidade transitória é registrada como definitiva e é irreversível** | `loteria_federal.py:29-33` — 3 tentativas **sem espera** entre elas; `ocorrencia.py` grava `indisponivel=True`; `OcorrenciaDaFonte` é append-only nas três camadas; `substituicao.proxima_a_observar` passa a apontar a extração seguinte | Cinco segundos de rede ruim ao vivo queimam para sempre a extração que o Edital declarou e empurram o certame para uma extração que ainda não ocorreu. Não há como desfazer, nem em produção | contingência / defeito | **crítica** | rara, mas catastrófica | média | Separar *"a fonte disse que não há"* de *"não consegui falar com a fonte"*: a segunda não grava nada, e se repete |
| **E-07** | **A tela transmitida mostra a projeção de agora, e não a relação congelada** | `previa.py:_recorte` devolve `participantes` = projetados do instante; `sorteio.html` renderiza essa lista mesmo depois de `congelada` | O que a audiência vê não é o universo comprometido; se um fato de origem mudou, a tabela diverge da relação — e só a contagem avisa | UX da comissão / transparência | **alta** | sempre que algo muda após o congelamento | baixa | Congelada a relação, a tela mostra **a relação** |
| **E-08** | **O botão "Realizar o sorteio" aparece antes de a precedência ser aferida** | `sorteio.html` condiciona a `congelada and ocorrencia and not indisponivel and ocorrida_nao_antes_de`; a comparação com `publicada_em` só acontece dentro do comando (`sorteio.py`) | Congelamento tardio → botão presente, clique ao vivo, recusa `occurrence_precedes_freeze` na frente da audiência | UX da comissão | média | rara | baixa | Aferir na leitura e dizer, antes, por que não dá |
| **E-09** | **`_ocorrencias_disponiveis` não filtra por fonte, Edital nem Processo** | `previa.py` — `OcorrenciaDaFonte.objects.filter(indisponivel=False, sorteios__isnull=True)` | O `select` da anulação lista extrações observadas por **outros certames**; escolher uma leva a `occurrence_not_declared` | UX da comissão / integração | média | só na anulação | baixa | Filtrar pela fonte do método e pela cadeia de substituição |
| **E-10** | **Fallback silencioso para `listaRateioPremio`** | `loteria_federal.py:39` — `corpo.get("listaDezenas") or corpo.get("listaRateioPremio")`. O rateio traz faixas de prêmio (`valorPremio: 500000.0`), não números sorteados | Se a Caixa devolver 200 com `listaDezenas` vazia e rateio preenchido, a semente deriva de **valores monetários**, serializados como `dict` Python, sem que nada acuse. Verificado hoje: concurso inexistente devolve 500 e cai no caminho certo — o risco é a resposta 200 parcial | integração / defeito latente | alta se ocorrer | rara | baixa | Ler só `listaDezenas`; ausência é indisponibilidade |
| **E-11** | **`emitir_ordem` procura o ato vigente sem `lista_id`** | `classificacao/application/emissao.py:54` | Num marco com três listas sorteadas, um ato computado poderia nascer sucedendo o ato de sorteio de outra lista, com motivo de outra natureza | modelo de domínio / defeito latente | alta se ocorrer | rara | média | O mesmo eixo que a `D-015` já abriu na divulgação |
| **E-12** | **Nenhuma porta pública para o sorteio antes do evento** | `selecao.html` não tem seção de sorteio; `relacao-de-habilitados` não é linkada de lugar nenhum público | A garantia central da feature — *a lista fechou antes da semente* — é invisível para quem deveria vê-la | UX do cidadão / transparência | **crítica** | todo certame | média | §J |
| **E-13** | **A procedência dos números não é contada em canal público** | `verificacao_de_sorteio.html` mostra semente e resumos; não mostra fonte, concurso, data da extração, nem o que os números são | O cidadão vê um número grande e uma promessa. É o que a `021` diz combater na prática atual dos Editais | UX do cidadão / transparência | **crítica** | todo certame | média | §H e §K |
| **E-14** | **Não existe vínculo entre o Evento do Cronograma e o marco que sorteia** | `EventoCronograma` tem `type`, `description`, `start_at`, `location` — e nenhuma referência a marco | O sistema não sabe **quando** o sorteio acontece. Não pode anunciar, não pode contar os dias, não pode dizer "aguardando sorteio" | modelo de domínio | **alta** | todo certame | média | §I, e é a decisão de domínio que o usuário precisa tomar |
| **E-15** | **A transmissão não tem lugar no modelo** | `location` é texto único, não validado como URL (`FR-061`), renderizado como texto | Não há como oferecer "Acompanhar transmissão" nem "Assistir à gravação" | modelo de domínio / UX do cidadão | alta | todo certame | média | §I |
| **E-16** | **"Quem realizou o sorteio" não aparece em canal público** | `executado_por` no modelo e na gestão; ausente do `manifesto.derivar` e das três páginas públicas | A pergunta 11 do cidadão não tem resposta pública | transparência | média | todo certame | baixa | Exibir o ator institucional na página do sorteio |
| **E-17** | **O candidato não vê o sorteio na área dele** | `acompanhamento.html` e `inscricao.html` não mencionam relação, número nem sorteio | Quem se inscreveu não descobre pelo sistema que participa de um sorteio | UX do cidadão | **alta** | todo certame | média | §J |
| **E-18** | **Não existe artefato PDF da relação de habilitados** | só `render_edital_pdf`, `render_resultado_pdf`, `render_comprovante_pdf` | Não há o que anexar a um processo, imprimir ou mandar por ofício | UX do cidadão / nice-to-have | média | todo certame | média | §F, e ver a análise da hipótese |
| **E-19** | **Da tela do sorteio não há caminho para publicar o resultado** | `sorteio.html` linka o canal público, e nada mais | Terminado o sorteio, o operador precisa reconstruir a navegação por cinco telas | UX da comissão | alta | toda execução | baixa | Um link "Publicar a classificação" no bloco do sorteio realizado |
| **E-20** | **Vocabulário técnico vazando para o público e para a mesa** | "ocorrência", "material bruto", "recorte", "resumo canônico", "manifesto", "constituir" | Cada um destes é uma palavra que o operador precisa explicar ao vivo | UX / transparência | média | sempre | baixa | §G |
| **E-21** | **Histórico de atos do marco não identifica a lista** | `ordenacao.html:118` — `historico()` não filtra nem rotula lista | Num marco com cotas, três linhas idênticas e nenhuma pista de qual é PPI | UX da comissão | média | certame com cotas | baixa | Rotular a lista |
| **E-22** | **`occurrenceAt` digitado em RFC 3339 à mão** | `_marco.html` — `placeholder="2026-11-20T20:00:00-03:00"` | Quem elabora o Edital não é quem lê RFC 3339. Um erro aqui só aparece no dia do sorteio | UX da comissão | média | toda elaboração | baixa | Campo de data e hora, com o fuso institucional |

---

## F · A hipótese do PDF da relação — análise, e uma discordância parcial

A hipótese proposta: a página pública exibiria situação, quantidade, data, transmissão e um **PDF**
como artefato oficial da relação congelada, evitando reproduzir a tabela inteira.

**O que está certo na hipótese:** a página do Edital precisa de um bloco de sorteio (E-12); a
quantidade, a data e o link da transmissão são exatamente os quatro dados que faltam; e uma tabela de
327 nomes no meio da página do Edital é poluição.

**Onde ela colide com a feature.** O artefato canônico **já existe e não é o PDF**: é o conteúdo
canônico da relação, cujo `canonical_sha256` **é** o resumo publicado. A `FR-006` e a `R-015` fixam
que esse resumo cobre *exatamente* o que o portal mostra — número, nome e protocolo — para que o
leitor **recalcule** em vez de aceitar. `registrationId` já foi retirado dessa projeção por essa
razão exata. Um PDF não é recalculável: PDF não tem serialização canônica, dois renderizadores
produzem bytes diferentes, e um resumo sobre bytes de PDF não fecha com nada que a pessoa possa
refazer.

**O risco de "somente PDF"** é, portanto, maior do que o de duas representações: seria trocar o único
artefato conferível por um que só se pode acreditar — e é essa palavra que a `021` existe para não
pedir.

**Recomendação.** Três representações, uma verdade:

```text
canônico   o conteúdo canônico da relação           → é o que o resumo cobre; é o que fecha
HTML       a página pública                          → renderização fiel do canônico, é dela que se recalcula
JSON       /api/sorteio/relacoes/<id>                → já existe, mesma projeção, sem raspar HTML
PDF (novo) derivado do mesmo canônico, carimbando    → artefato de arquivo, ofício, impressão
           o resumo e o endereço da página
```

**Como impedir divergência:** o PDF não pode ser uma segunda composição. Deve ser derivado do mesmo
`projecao.conteudo_canonico`, trazer o resumo impresso e a frase *"esta é a impressão da relação
publicada em <endereço>; o resumo desta relação é <64 hex>"*. Um teste que renderize os dois e
compare linha a linha resolve o resto — e é o mesmo desenho que o manifesto já usa (`R-007`: derivar,
nunca copiar).

**Sobre a tabela na página do Edital:** a hipótese está certa. O bloco do sorteio na página do Edital
mostra **quantidade e link**; a tabela vive na página da relação, que é o endereço estável e citável.

---

## G · O que simplificar

Elementos que podem desaparecer da primeira leitura, sem perder nada:

1. **Os cinco resumos SHA-256 do primeiro nível público.** Hoje a página do resultado exibe três, a
   verificação exibe quatro e a relação exibe dois. Nenhum deles significa alguma coisa para o
   cidadão comum. Vão para o nível 2/3 (§I).
2. **"Manifesto".** A palavra não precisa aparecer no nível 1. No nível 3 ela é o nome certo.
3. **"Ocorrência da fonte"** vira *"o resultado da Loteria Federal que o Edital escolheu"*, e
   **"material bruto"** vira *"os números que a Caixa publicou"*.
4. **"Recorte"** — nem na tela da comissão. É jargão interno; a tela pode dizer o nome da lista.
5. **"Resumo do método"** na tela do congelamento: é ruído para quem opera. O que importa ali é *qual
   extração vai semear*, e isso já está escrito ao lado.
6. **A linha de comando como via principal de verificação.** Ela deve continuar existindo — é ela que
   sustenta a `SC-001` —, mas não pode ser a única forma de o cidadão conferir. Ver §H.

**O que já está no ponto e não deve ser tocado:** a ausência de campo de semente, a ausência de
"simular", a ausência de "refazer", a exigência de motivo, e o custo alto da anulação. São a feature.

---

## H · O que tornar mais visível

1. **A ordem dos dois instantes.** Uma frase, com as duas datas lado a lado:
   *"A lista foi fechada em 08/09/2026 às 17h02. Os números da Loteria Federal só existiram em
   10/09/2026. Ninguém podia sabê-los quando a lista fechou."* Os dois dados existem; o que falta é
   a frase que os aproxima.
2. **A procedência dos números**, escrita como o usuário propôs na §7 do pedido — e a proposta dele
   está certa. Uma versão ainda mais curta:

   > O Edital, publicado em 12/08/2026, definiu que este sorteio usaria o **concurso 6098 da Loteria
   > Federal**, sorteado em 06/09/2026.
   > A Caixa publicou nele os cinco bilhetes premiados: **048337 065904 007642 065308 038572**.
   > Esses números — e só eles — decidiram a ordem dos **327 candidatos** da lista fechada em
   > 08/09/2026.
   > Ninguém do Ifes escolheu esses números, e a lista não mudou depois deles.

   Quatro frases, nenhum termo técnico, e cada uma verificável.
3. **Quem conduziu** (E-16).
4. **A transmissão**, antes e depois (E-15).
5. **A unicidade, dita como consequência e não como propriedade:** *"O sistema só emite um resultado
   para esta lista e estes números. Refazer exigiria anular publicamente, retificar o Edital para
   escolher outra extração e sortear de novo — tudo registrado, com data e responsável."*
6. **O número do candidato, na área dele** (E-17): *"Você é o número 214 no sorteio de 10/09."*

---

## I · Fluxo operacional recomendado

Do fechamento dos habilitados à publicação, preservando o que a equipe já faz. **Cinco passos, um
por vez, e a tela sabe qual é o próximo.**

```text
Passo 1 · A relação          [ Publicar e congelar ]   → ✓ congelada em DD/MM às HH:MM · 327 participantes
Passo 2 · A extração         [ Consultar o concurso 6098 na Loteria Federal ]
                             → ✓ 048337 065904 007642 065308 038572, extração de 06/09
Passo 3 · O sorteio          [ REALIZAR O SORTEIO ]    → ✓ realizado às 14h07 · ordem de 327
Passo 4 · A conferência      a ordem, na tela, antes de publicar
Passo 5 · A publicação       [ Publicar a classificação ] → leva à prévia da 017, já parametrizada
```

Sobre a proposta de console do usuário (§9 do pedido), item a item:

- **Fica evidente qual é o próximo passo?** Hoje não — a tela é organizada por *entidade* (método,
  ocorrência, recortes) e não por *momento*. A numeração proposta resolve, e é a mudança de maior
  retorno por menor custo.
- **Escolha desnecessária?** Uma: o `select` de ocorrências na anulação (E-09). No fluxo feliz não há
  escolha nenhuma, e isso está certo.
- **Campo que não deveria ser editável?** Nenhum. Esta parte está impecável.
- **Copiar e colar?** Não no fluxo feliz. Sim, hoje, para achar a URL da tela (E-04).
- **Informação técnica que pode ser escondida?** `metodo_hash`, `manifesto_hash`, `resumo` — todos
  para um "ver detalhes técnicos".
- **Informação importante escondida?** Três: **a data e a hora marcadas do sorteio** (o sistema não as
  tem — E-14), **a relação congelada de verdade** (E-07) e **o caminho para publicar** (E-19).
- **Estados que precisam impedir ação:** relação sucedida; ocorrência anterior ao congelamento
  (E-08); ato raiz já existente no recorte; método não declarado; e — proposto — marco de sorteio na
  tela de ordenação (E-05).
- **Mensagens que precisam ser extraordinariamente claras ao vivo:** as quatro de desfecho (E-01), a
  de duplo clique (E-03) e a de fonte indisponível, que hoje é irreversível sem dizer que é (E-06).

### Sobre o intervalo entre sortear e publicar (§10 do pedido)

Respondendo direto, pelo que o código já decide:

- **A ordem já é fato imutável** no instante do clique: `AtoDeOrdenacao` + `PosicaoNaOrdem` são
  append-only nas três camadas. Não há rascunho.
- **A classificação não é uma projeção separada**: no sorteio, ordem e classificação são o **mesmo**
  artefato — `posicao` 1..N, sem pontuação, sem corte (`FR-025`). Cotas **não** transformam ordem em
  classificação: cada lista tem o seu próprio sorteio e a sua própria ordem (`D-006`).
- **A confirmação já existe, e é a publicação.** O fluxo da `017` tem prévia que não grava,
  aferição de publicabilidade, escolha de natureza (preliminar/definitiva) e autoridade signatária —
  e `resultado:publicar` **não** decorre de quem emitiu. Isso já é a homologação administrativa.
- **A confirmação não pode alterar nada**, e está certo assim.
- **O PDF já é gerado automaticamente** na publicação e servido em `/resultados/<id>/documento.pdf`.

**Portanto: não criar máquina de estados nova.** O que falta entre sortear e publicar não é um
estado — é **um link e uma tela de conferência**. O passo 4 acima é leitura, não estado.

---

## J · Fluxo público recomendado

**Antes** — na página do Edital, seção própria, ao lado do Cronograma:

```text
Sorteio público
Aguardando sorteio · 10/09/2026, 14h
327 candidatos habilitados
[ Ver a relação de quem vai participar ]     → a página da relação (canônica)
[ Baixar a relação (PDF) ]                   → derivado, para arquivo
[ Acompanhar a transmissão ]                 → quando declarada
Como este sorteio vai funcionar →            → a mesma página do "como foi", no futuro do verbo
```

**Durante** — o mesmo bloco, com a transmissão em destaque e a frase *"acontecendo agora"*, que o
cronograma já sabe calcular.

**Depois:**

```text
Sorteio realizado
10/09/2026, 14h07 · conduzido por <autoridade>
[ Ver o resultado ]  [ Como este sorteio foi feito ]  [ Assistir à gravação ]
```

E, na área do candidato, uma linha: *"Você participa do sorteio de 10/09 com o número 214."*

**Se não houver transmissão:** o bloco simplesmente não mostra o botão — mesma regra do `location`
hoje, que não escreve "não informado" (`FR-058`). Nada afirma uma omissão.

**Transmissão e gravação devem ser o mesmo atributo?** Não. São dois fatos com tempos diferentes: um
existe antes e o outro depois, e o segundo frequentemente tem outro endereço. Um campo só forçaria
a comissão a sobrescrever o primeiro — e o endereço da transmissão citado num ofício deixaria de
responder. **Onde eles moram** é a decisão de domínio de §L.

---

## K · Wireframe textual

### K.1 · Página pública do Edital — bloco do sorteio

```text
┌─ Sorteio público ────────────────────────────────────────┐
│ Aguardando sorteio                                        │
│ 10 de setembro de 2026, às 14h                            │
│ 327 candidatos habilitados                                │
│                                                            │
│ [ Ver a relação de participantes ]  [ PDF ]               │
│ [ Acompanhar a transmissão ]                              │
│                                                            │
│ A ordem será decidida pelos números da Loteria Federal    │
│ do concurso 6098, que ainda não aconteceu.                │
│ Como este sorteio vai funcionar →                         │
└────────────────────────────────────────────────────────────┘
```

### K.2 · Página "Como este sorteio foi feito" — nível 1

```text
Como este sorteio foi feito
Processo Seletivo 77/2026 · Técnico em Informática (EaD)

1. A lista fechou primeiro
   Em 08/09/2026, às 17h02, o Ifes publicou a lista dos 327 candidatos,
   cada um com um número. Depois disso, a lista não mudou.
   [ Ver a lista ]

2. Os números vieram de fora
   O Edital, publicado em 12/08/2026, já dizia qual sorteio seria usado:
   o concurso 6098 da Loteria Federal.
   Em 06/09/2026, a Caixa publicou os cinco bilhetes premiados:
      048337 · 065904 · 007642 · 065308 · 038572
   Ninguém do Ifes escolheu esses números.        [ Conferir no site da Caixa ]

3. Os números decidiram a ordem
   Uma regra publicada no Edital transforma esses cinco números na ordem
   dos 327 candidatos. A mesma regra, com os mesmos números e a mesma
   lista, sempre produz a mesma ordem — e qualquer pessoa pode refazer.

4. O sorteio aconteceu uma vez
   10/09/2026, às 14h07, transmitido ao vivo, conduzido por <autoridade>.
   [ Assistir à gravação ]      [ Ver o resultado ]

   Não existe "sortear de novo": para trocar este resultado seria preciso
   anular publicamente, retificar o Edital escolhendo outra extração e
   sortear outra vez — com data, motivo e responsável registrados.

── Quero ver os dados exatos que foram usados →   (nível 2)
```

### K.3 · Nível 2 — "os dados exatos"

Tabela sem prosa: lista congelada e resumo; fonte; concurso e data; números observados; regra de
normalização (a frase publicada); semente derivada; algoritmo e versão; instantes de congelamento e
execução; quem conduziu; ordem completa. É, essencialmente, a página de verificação de hoje **mais**
a procedência que hoje só existe no manifesto.

### K.4 · Nível 3 — verificação técnica

A página de verificação atual, praticamente intacta: os cinco degraus, os resumos, o manifesto, o
verificador com `--resumo` preenchido e a advertência da `D-018`. Não precisa mudar — precisa deixar
de ser o **nível 1**.

### K.5 · Console da comissão

```text
Sorteio público — Técnico em Informática (EaD)          10/09/2026, 14h
Ampla concorrência · 327 candidatos                     [ ver detalhes técnicos ]

┌ 1 · A relação de participantes ────────────── ✓ pronta ─┐
│ 327 candidatos · congelada em 08/09 às 17h02            │
│ [ Ver a relação publicada ]                             │
└──────────────────────────────────────────────────────────┘
┌ 2 · Os números da Loteria Federal ─────────── ✓ obtidos ─┐
│ Concurso 6098 · extração de 06/09/2026                   │
│ 048337  065904  007642  065308  038572                   │
│ obtido em 10/09 às 14h03 por paulo.presidente            │
└──────────────────────────────────────────────────────────┘
┌ 3 · Realizar o sorteio ──────────────────────────────────┐
│ 327 participantes · números do concurso 6098             │
│              [ REALIZAR O SORTEIO ]                      │
│ Este ato é único e não se desfaz.                        │
└──────────────────────────────────────────────────────────┘
┌ 4 · O resultado ─────────────────────── aguardando (3) ─┐
└──────────────────────────────────────────────────────────┘
┌ 5 · Publicar a classificação ────────── aguardando (4) ─┐
└──────────────────────────────────────────────────────────┘
```

Os passos futuros aparecem **fechados e nomeados** — é o que responde "qual é o próximo passo?" sem
que ninguém precise perguntar.

---

## L · Contingências

Para cada uma: o que o sistema faz hoje, o que é decisão administrativa, o que precisa estar no
Edital, e o que cada lado lê.

| Situação | Sistema hoje | Decisão administrativa | Precisa no Edital | Operador lê | Público lê |
|---|---|---|---|---|---|
| Loteria atrasa | antes de `occurrenceAt`, recusa com "ainda não chegou" (`FR-077`) — **correto** | esperar | `occurrenceAt` | claro | nada |
| Concurso não ocorreu | idem | esperar ou aplicar substituição | regra de substituição | claro | nada |
| **API fora** | **3 tentativas imediatas → indisponibilidade definitiva e irreversível** (E-06) | nenhuma — o sistema decide sozinho, e erra para o lado pior | — | "a fonte não devolveu" | nada | 
| Site mostra, endpoint não | mesmo caminho de E-06 | idem | — | idem | nada |
| Endpoint com dados incompletos | `listaDezenas` vazia → indisponível; rateio preenchido → **fallback perigoso** (E-10) | — | — | nada acusa | nada |
| Transmissão começou e fonte fora | E-06 ao vivo | suspender e remarcar | — | mensagem técnica | nada |
| **Número corrigido depois pela fonte** | **nada** — a ocorrência é append-only e o sorteio já usou o material antigo | anular + Retificação + novo sorteio | previsão de correção da fonte | nada | nada |
| Relação com erro (antes do sorteio) | relação nova sucede, com motivo — **correto** | corrigir o fato de origem | — | claro | a relação diz que foi sucedida |
| Candidato faltando/sobrando | idem | idem | — | claro | idem |
| **Sorteio ok, transmissão caiu** | nada a fazer — o ato existe e é verificável | decidir se repete a transmissão | — | — | **nada explica** |
| Operador fecha o navegador | nada se perde: cada passo é um ato gravado — **correto** | — | — | ao reabrir, vê o estado | — |
| Erro entre fonte e sorteio | ocorrência fica registrada, sorteio não acontece; reabrir a tela retoma — **correto** | — | — | claro | — |
| Erro entre sorteio e publicação | ato existe, não publicado; a `017` retoma — **correto** | — | — | claro | nada ainda |
| Tentar executar de novo | recusado, mas com mensagem enganosa no duplo clique (E-03) | — | — | **enganoso** | — |
| Anulação | sucessor com relação nova e ocorrência nova; anterior íntegro — **correto** e caro por desenho (`D-017`) | anular é ato administrativo | a nova ocorrência, por Retificação | passos listados na tela | a página diz que foi anulado e por quê |
| Retificação do método após congelar | não alcança relação nem ato; sortear passa a ser recusado — **correto** | — | — | recusa nomeada | — |

**Classificação honesta:** de dezesseis cenários, **onze já estão resolvidos e bem**. Dois são
defeitos a corrigir (E-06, E-10). Dois são decisões administrativas que só precisam de previsão no
Edital (correção posterior pela fonte; queda de transmissão). Um é mensagem a arrumar (E-03).
**Nenhum é feature nova.**

Um vazio que merece registro: **o público não tem canal para saber que algo deu errado.** Toda
contingência hoje é comunicada fora do sistema. Um recado curto no bloco do sorteio — *"o sorteio de
10/09 foi adiado; nova data 17/09"* — cobriria a maioria, e é a diferença entre uma instituição que
avisa e uma que some.

---

## M · Backlog mínimo

**P0 — antes de um sorteio real em produção**

1. Um desfecho por comando, na faixa de sucesso e na de erro (E-01, E-02).
2. Chave de idempotência nos formulários do sorteio (E-03).
3. Link do detalhe do Edital para a tela do sorteio, para o marco que declara método (E-04).
4. Marco com `drawMethod` não oferece emissão computada na tela de ordenação (E-05).
5. Falha de rede ≠ ausência de resultado: a primeira não grava indisponibilidade (E-06).
6. Congelada, a tela mostra **a relação congelada** (E-07).
7. Link do sorteio realizado para a publicação da classificação (E-19).
8. Bloco de sorteio na página pública do Edital, com quantidade, data e link para a relação (E-12).

**P1 — melhora importante**

9. Página "Como este sorteio foi feito", nível 1 (E-13, e §K.2).
10. Data e hora do sorteio como fato do sistema (E-14) e endereço da transmissão (E-15).
11. Console reorganizado em passos numerados (§I).
12. O número do candidato na área dele (E-17).
13. `listaDezenas` apenas (E-10); ocorrências filtradas por fonte (E-09); aferir a precedência na
    leitura (E-08); quem conduziu, no público (E-16).
14. `emitir_ordem` com o eixo da lista (E-11).

**P2 — evolução**

15. PDF derivado da relação (E-18).
16. Verificação sem linha de comando — o mesmo cálculo em página, com o alerta da `D-018` intacto.
17. Vocabulário público revisto (E-20); rótulo da lista no histórico (E-21); campo de data e hora
    para `occurrenceAt` (E-22).
18. Um lugar para a instituição avisar sobre adiamento ou anulação (§L).

---

## N · Decisão sobre nova spec

**1. Existe lacuna funcional suficiente para justificar uma nova spec?** Sim — mas não onde parece.
O **motor** do sorteio está construído, correto e bem defendido: o que a `021` prometeu de garantia
criptográfica e de imutabilidade está entregue e testado. A lacuna é de **rito e de narrativa**: o
sistema sabe provar e não sabe **contar**, e não sabe se **anunciar** antes do fato. Isso são
capacidades novas — data e local do sorteio como fato do domínio, um canal público antes do evento,
uma página de explicação para leigos, a área do candidato ciente do sorteio.

**2. Ou são majoritariamente ajustes da implementação existente?** Os **P0 são todos polish** — oito
correções de tela e navegação, nenhuma tocando domínio, nenhuma exigindo migration. Rigorosamente:
eles são achados de implementação da `021` e cabem numa correção dela, não numa spec. É o que a
governança do projeto costuma separar.

**3. Fronteira da nova spec, se existir.** Sugestão de recorte — *"o sorteio anunciado e explicado"*:

- **data, hora e local do sorteio como fato do sistema**, ligados ao marco que sorteia — incluindo a
  decisão de domínio de onde eles moram (evento do Cronograma tipado? atributo do marco? do
  sorteio?), e a separação entre transmissão e gravação;
- **o bloco público do sorteio** na página do Edital, antes / durante / depois;
- **a página "Como este sorteio foi feito"**, nível 1, com a procedência dos números contada em
  quatro frases;
- **a transparência progressiva em três níveis**, reaproveitando a verificação atual como nível 3;
- **o candidato ciente**: número e data na área dele;
- **o PDF derivado da relação**, se o usuário o quiser como artefato de arquivo.

**4. O que explicitamente NÃO deve entrar:**

- **nada que toque a chave, a ordem, a semente ou o manifesto.** O algoritmo, os vetores normativos
  e o contrato estão fechados; mexer neles é publicar `v2`, e não há motivo;
- **nenhum estado novo entre sortear e publicar.** A `017` já tem prévia, aferição, natureza e
  signatário — é a conferência administrativa, e duplicá-la seria criar uma segunda verdade;
- **nenhuma flexibilização do que a `021` proíbe**: campo de semente, simulação, refazer, edição da
  relação, escolha de ocorrência;
- **integração com API de vídeo** — guardar um endereço não é integrar, e a fronteira da `D-012`
  continua valendo;
- **os oito P0**, que são correção da `021` e não devem esperar por uma spec;
- **ocupação de vagas, cotas, corte e progressão** — continuam sendo `014`/`016`.

---

## Sobre overengineering

Medido pela régua do próprio pedido — *cada mecanismo adicional responde a um risco concreto?* —, a
`021` passa. Cada peça responde a um risco nomeado: a relação congelada ao "escolher a lista depois";
o `metodo_hash` ao "escolher o método depois"; a unicidade de raiz às "duas relações vivas"; a
`D-017` ao "anular até agradar"; o `--resumo` externo ao "manifesto que fecha consigo mesmo". Não há
blockchain, não há cerimônia distribuída, não há nada além de banco transacional, timestamps,
autoria, hash, fonte externa declarada e publicação institucional.

**Dois lugares onde o custo talvez exceda o benefício**, e que valem uma conversa:

- **A cadeia de substituição de cinco elos** (`LIMITE_DA_CADEIA = 5`) automatiza um cenário que, na
  prática, deveria parar na primeira falha e virar decisão humana. Combinada com E-06, ela é mais
  perigosa do que útil: cinco elos automáticos significam cinco extrações queimáveis por acidente.
  Um elo — ou nenhum, exigindo ato administrativo — seria mais honesto e mais seguro.
- **Cinco resumos SHA-256 em páginas públicas.** Cada um é justificável no nível 3; nenhum é
  legível no nível 1. O custo não é técnico, é de confiança: uma página coberta de hexadecimal
  comunica "isto não é para você", que é o oposto do objetivo.

---

## Teste de compreensão

**Candidato — "como sei que não escolheram quem seria sorteado?"**

> A lista com o seu número foi publicada em 08/09 e ficou congelada. Os números que decidiram a
> ordem vieram da Loteria Federal, do concurso 6098, sorteado em 06/09 — e o Edital já dizia, desde
> 12/08, que seria esse concurso. Ninguém do Ifes escolheu esses números, e a lista não mudou depois
> deles.

*Fica claro?* Sim. **Mas hoje ele não consegue montar essa frase**: precisaria baixar o manifesto e
saber lê-lo. Falta a página que a conta — e é a lacuna E-13.

**Comissão — "estou ao vivo, o que clico?"**

> Passo 1, publicar a relação. Passo 2, consultar os números. Passo 3, realizar o sorteio. Passo 4,
> conferir. Passo 5, publicar.

*Fica claro?* Como sequência, sim — o desenho é simples. **Na tela de hoje, não**: a tela não é
numerada, não é alcançável por link, responde com mensagens que não correspondem ao que aconteceu, e
o passo 5 não está nela. São E-01 a E-05 e E-19 — todos de tela, nenhum de domínio.

**Auditor — "como reproduzo sem confiar no sistema?"**

> Baixe o manifesto, copie o resumo publicado na página, rode `node sorteio-cli.js --resumo <valor> <
> manifesto.json`. Depois abra a relação publicada e recalcule o resumo dela a partir do número, do
> nome e do protocolo. As duas conferências juntas fecham o círculo.

*Fica claro?* **Sim, e essa parte está exemplar** — inclusive a honestidade da `D-018` sobre o que o
programa **não** prova sem a âncora externa. É a única das três personas plenamente atendida hoje.

---

## O princípio orientador, respondido

> *"A lista de participantes estava fechada antes de existir a semente. A comissão não escolheu os
> números. A regra já estava publicada. O sistema executou essa regra uma única vez. Eu consigo ver
> de onde vieram os números, qual ordem foi produzida e, se quiser, consigo reproduzir."*

**Cada uma dessas frases é verdadeira no sistema de hoje.** Todas são provadas por constraint, por
trigger, por privilégio ausente e por teste. E **nenhuma delas está escrita em lugar nenhum que uma
pessoa comum vá ler.** A distância entre o sistema e a percepção legítima que ele merece produzir
não é criptográfica — é editorial e de navegação.

Do lado da comissão, a resposta é mais dura: **hoje o rito não se conduz com segurança numa
transmissão pública.** Não por falta de garantia, que existe de sobra, mas porque a tela não é
encontrável, não numera os passos, responde com frases falsas e não leva à publicação. São seis
correções pequenas, nenhuma delas de domínio — e é o trabalho de melhor retorno que este relatório
encontrou.
