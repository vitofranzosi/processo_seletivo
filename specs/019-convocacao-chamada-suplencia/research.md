# Pesquisa — `019` Convocação, Chamada e Suplência

**Fase 0 do plano.** Cada decisão abaixo foi tomada contra o código medido em `34b5b13`, e nenhuma
delas é escolha de gosto: todas resolvem uma pergunta que o plano não podia deixar para a
implementação. Onde houve medição, o número está aqui.

---

## R-001 — A contagem de titulares, e por que a exclusão sozinha não bastava

**Decisão.** `apurar` passa a receber a **sequência ordenada** dos que progrediram, e não o
conjunto. Titular inicial é a Inscrição que está entre as primeiras `efetivas` posições dessa
sequência, contadas **por pessoa**. `ocupadas = |titulares habilitados − excluídos ∪ incluídos|`,
limitado a `efetivas`.

**Racional.** Medido chamando a função real, com 40 vagas, faixa de 70 e 67 habilitadas:

```
                                            hoje    com R-001
ninguém desistiu                              40           40
uma titular desiste                           40           39
essa vaga é chamada e a suplente aceita       40           40
cinco desistem, ninguém aceitou ainda         40           35
vinte e sete desistem                         40           13
```

O `min(|faixa ∩ habilitadas|, efetivas)` conta **capacidade**, não ocupação: enquanto sobrarem
habilitados na faixa, o número satura no alvo. Eram necessárias **28** desistências para ele se
mover, e cada uma das 27 anteriores era uma suplente promovida em silêncio.

**Alternativas consideradas.**

- *Manter o conjunto e subtrair a contagem de exclusões* — recusada: o número resultante não é
  reproduzível a partir dos atos, e duas exclusões da mesma pessoa dariam −2.
- *Contagem própria na `019`* — recusada pelo usuário na `Q-1`: a pergunta *"quantas vagas estão
  ocupadas"* passaria a ter duas respostas.
- *Modelar vaga individual* (`Vaga` com ocupante) — recusada pela `D-011`, por escrito. Resolveria a
  contagem trivialmente e custaria uma entidade que o Edital não publica, mais a pergunta de qual
  vaga numerada cada pessoa ocupa — que nenhum Edital lido responde.

## R-002 — O empate residual que atravessa a fronteira do alvo

**Decisão.** Onde houver **empate residual não julgado** atravessando a fronteira do alvo, a
apuração **recusa** determinar titulares, com código próprio (`empate_na_fronteira_do_alvo`), em vez
de escolher.

**Racional.** A `014` trata o empate na última posição **da faixa** — `alvo + excedente` —, e o
Edital declara `tieOutcome` para ela. Titular inicial é contado até o **alvo**, que é outra
fronteira, e para essa a norma publicada não diz nada. As duas saídas fáceis afirmariam regra que
ninguém escreveu: incluir todos os empatados faria `ocupadas > efetivas` e a constraint da `016`
recusaria o ato; escolher por ordem de chegada inventaria desempate. Recusar é o que a `014` já faz
quando o Edital publicou alvo estrito e o empate cruza a faixa.

**Consequência operacional.** O caso só aparece com empate residual real, e o caminho de saída já
existe: julgar o desempate na `015`. A recusa nomeia isso na mensagem.

## R-003 — A porta de efeitos: onde mora e por que não é FK

**Decisão.** `EfeitoDeOcupacao` é tabela **append-only em `ocupacao`**, escrita pela `019` através
de `ocupacao.application.efeitos.registrar_efeito(...)`. O ato de origem entra como **UUID opaco
mais rótulo**, nunca FK.

**Racional.** A `D-006` fixou que a exclusão chega por porta que a `016` define, para a seta
continuar `ocupacao → classificacao` e nunca o contrário. Uma FK de `ocupacao` para `convocacao`
inverteria a dependência **no grafo de migrations**, que é onde ela é irreversível: a `016` passaria
a não poder migrar sem a `019`. O precedente está na própria `016`, que guarda `perfil_id` e
`marco_id` como UUID por razão parecida — *"Retificação acrescenta e remove itens sem criar ou
apagar a linha do rascunho"*.

**Alternativas consideradas.**

- *Guardar os efeitos em `convocacao` e a `016` lê* — recusada: `ocupacao` importaria a feature
  nova.
- *Sinal/evento em memória* — recusada: efeito de ocupação é fato auditável, e precisa sobreviver ao
  processo.
- *Coluna na apuração* — recusada: apuração é append-only, e efeito posterior mudaria linha gravada.

## R-004 — O vencimento informado, e o que o sistema confere

**Decisão.** A convocação grava o **vencimento explícito** informado por quem convoca. O sistema não
calcula dias úteis e não mantém calendário; confere apenas que o vencimento é **posterior ao
envio**.

**Racional.** `D-011`. Os Editais contam em dias úteis a partir do recebimento (77/58/59, 8.3), e
calendário de expediente é matéria que a `018` já deixou fora por decisão. Sem calendário, calcular
"2 dias úteis" seria inventar feriado — e errar por um dia num prazo que decide vaga.

**O que fica verificável de todo modo.** Que o prazo não corre sem envio (`FR-269a`), que o
vencimento não precede o envio (`FR-269b`), e que o decurso não produz desfecho (`FR-274`).

## R-005 — A quinta linha legítima do Resultado, para a regularização

**Decisão.** `resultados.ResultadoEtapa.Origem` ganha `REGULARIZACAO`, e `ck_resultado_origem` ganha
a quinta linha: `origem=REGULARIZACAO`, `avaliacao` nula, `resultado_anterior` presente, e **fonte
jurídica própria** — a referência ao ato de regularização, e não a `DecisaoRecurso`.

**Racional.** A `D-008` manda a regularização suceder o Resultado pelo mecanismo da `018`. Medido no
código: a constraint tem hoje quatro linhas legítimas, e a docstring diz que a `decisao` é *"a fonte
jurídica do sucessor, obrigatória em todo sucessor, qualquer que seja a origem"*. Afrouxar a
constraint para admitir sucessor sem fonte destruiria a garantia que ela existe para dar; estendê-la
com fonte nova a preserva.

**Alternativas consideradas.**

- *Reusar `DecisaoRecurso` com um recurso sintético* — recusada: registraria recurso que ninguém
  interpôs — o mesmo tipo de mentira que a decisão de origem da `018` recusou ao proibir Resultado
  por recurso citando Avaliação inexistente.
- *Ato próprio da `019` sem tocar `resultados`* — recusada pelo usuário na `Q-3`: criaria segundo
  caminho de habilitação, invisível para a contagem da `016`.

## R-006 — Os sete desfechos, e o que cada um faz na porta

**Decisão.** Um desfecho por convocação, e o efeito de cada um na contagem é declarado, nunca
inferido:

| Desfecho | Efeito na porta | Observação |
|---|---|---|
| aceite | **inclusão** | é o que recompõe o número (`FR-278b`) |
| regularização | **inclusão** | e produz o Resultado sucessor (`R-005`) |
| indeferimento | exclusão, se era titular | não é eliminação da ordem |
| desistência expressa | exclusão | |
| não atendimento à convocação | exclusão | ato humano sobre vencimento decorrido |
| cancelamento de matrícula por inércia | exclusão | exige atestado de fato externo |
| reclassificação | exclusão, e move na fila | não afirma perda de habilitação |

**Racional.** `D-011` manda os dois últimos de exclusão serem distintos. E a tabela mostra por que a
inclusão era indispensável: sem ela, quatro linhas descem o número e nenhuma o sobe.

**Nota de leitura.** Exclusão de quem **não era** titular não desconta nada — a suplente só entra na
contagem depois de aceitar (`FR-278d`). Isso evita o número negativo que uma subtração cega
produziria.

## R-007 — A forma de comunicar como conteúdo publicado: degrau 15

**Decisão.** Campo normativo novo no Perfil publicado, com **degrau 15** (`SCHEMA_VERSION` medido em
14), caminho de leitura das versões anteriores, presença no documento e entrada no catálogo de
Retificação por identidade.

**Racional.** `D-009` e a §1.1 da spec: a amostra tem duas formas incompatíveis — publicação (69,
7.2) e mensagem individual com prazo do recebimento (77/58/59, 8.3) —, e as duas são normais.
Inferir pelo texto do Edital é o erro que a `R-006` da `025` recusou por escrito para a ampla
concorrência.

**A declaração da coleção precede a primeira emissão.** É a lição que a `025` registrou como *"o
detalhe que não teria conserto"*: endereço de retificação não se conserta depois.

## R-008 — A revisão da `FR-084` da `010`

**Decisão.** A revisão é **fase própria** (fase 7), anterior a qualquer envio individual, e produz
texto na `010` — não uma exceção silenciosa aqui.

**Racional.** A `FR-084` diz que o sistema envia mensagem em exatamente duas situações e que
*"acrescentar uma terceira situação exige revisar esta regra"*. A convocação é a terceira.
Implementar o envio sem a revisão deixaria duas regras vigentes e contraditórias no mesmo
repositório.

## R-009 — O estado "convocado, prazo não iniciado"

**Decisão.** Estado de leitura derivado, não coluna: existe convocação praticada e não existe
comunicação com envio bem-sucedido.

**Racional.** `D-009` separa o ato do relógio. Sem o estado, falha de infraestrutura fica
indistinguível de silêncio da pessoa — e o desfecho que decorre disso é perda de vaga. Derivado, e
não gravado, pela mesma razão que a `016` calcula obsolescência em vez de guardá-la: coluna exigiria
`UPDATE` em tabela append-only.

## R-010 — O custo de abrir a tela

**Decisão.** A leitura do recorte carrega convocações, desfechos e efeitos em consulta por conjunto,
com `prefetch_related`, e a medição entra em `tests/performance/test_convocacao.py`.

**Racional.** `SC-090`, e o precedente medido no #107: a tela do corte com 10.000 participantes
custou 0,277 s contra teto de 3 s, e a contagem de consultas ficou intacta de 5 a 20.000. O modo de
errar aqui é uma consulta por convocação — e é invisível com 40 pessoas.

---

## O que esta pesquisa não resolveu, e nem devia

- **Qual vaga numerada cada pessoa ocupa** — não existe vaga individual (`D-011`).
- **Se o Edital pode declarar prazo em dias úteis contados pelo sistema** — não nesta feature
  (`R-004`); criar calendário é incremento próprio.
- **Como a turma entra** (`P-10`) — fora de escopo por spec.
- **Recurso contra a chamada** — `D-010`, e a hipótese futura está na §7 da spec.
