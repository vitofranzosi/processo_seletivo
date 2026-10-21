# Pesquisa: Prévia do sorteio

**Feature**: [spec.md](spec.md) · **Plano**: [plan.md](plan.md) · **Data**: 2026-10-21, contra a `main`
em `14efe941`

As decisões da feature estão na spec (D-001 a D-008). Aqui ficam as questões técnicas, em `R-`, e o que
se mediu para respondê-las. Nenhuma ficou aberta.

---

## R-001 — O que o motor faz com a população da história 1, medido

**Pergunta.** A spec diz que, no sorteio, sobrar vaga reservada sem ocupante é *frequente*. Quanto?

**Medição.** [prototipo/medicao.py](prototipo/medicao.py), `historia()`: 20 só na ampla, 6 PPI, 4 PcD;
vagas 10, 3 e 2; alvo do quadro, nenhum suplente; 1.000 rodadas com sementes fictícias; ordem por
`chave.ordem`, faixa por `faixa.calcular`, ocupação por `rodada_da_previa.rodada` — o motor oficial.

| Reversão declarada | PPI | PcD |
|---|---|---|
| nenhuma | sobra vaga em **72%** das rodadas; 1,01 sem ocupante, em média; 2,02 PPI ocupam pela ampla | sobra em **54%**; 0,64 sem ocupante; 1,33 pela ampla |
| por saldo (`ON_BALANCE`) | o mesmo, e cede **1,01** vaga à ampla, em média | o mesmo, e cede 0,64 |
| por esgotamento (`ON_EXHAUSTION`) | o mesmo, e **nunca** cede | o mesmo, e nunca cede |

**O que isso diz.** No sorteio, a DP-1 da `095` não é caso-limite: é a regra. Com 6 PPI entre 30
inscritos, o esperado é 10 × 6/30 = 2 PPI entre os 10 primeiros da ampla — e a medição dá 2,02. Como a
faixa da PPI tem 3 posições e cada um desses 2 tem chance de estar nela, sobra vaga em quase três de
cada quatro rodadas, com 3 PPI ainda esperando fora da faixa. E sob "por esgotamento" nada é cedido nunca,
porque a lista da PPI tem 6 pessoas com posição e a regra conta todas (DP-2 da `095`).

**Consequência para o plano.** O resumo de muitas rodadas (D-002) vai mostrar ao elaborador, logo na
primeira abertura, o comportamento que a DP-1 e a DP-2 registram como pendente. A FR-2507 já obriga a
chamá-lo de comportamento atual; o roteiro de compreensão precisa de uma pergunta sobre isso (SC-925).

**Duas sementes de base diferentes** (`historia()` com `semente-ficticia:` e o primeiro esboço com
outra base) deram 72% e 71% na PPI, 54% e 58% na PcD — diferenças de 1 e 4 pontos, dentro da margem da
SC-929.

## R-002 — Onde a ordem fictícia se calcula, e o que a separa da oficial

**Decisão.** A ordem de cada recorte sai de `sorteios.domain.chave.ordem`, a função que
`constituir_sorteio` usa (via `chaves` + `ordenar`), com quatro entradas:

| Entrada | No sorteio oficial | Na prévia |
|---|---|---|
| `relation_hash` | `RelacaoDeHabilitados.resumo`, o SHA-256 canônico da relação publicada | o resumo de uma **relação fictícia** (R-005) |
| `draw_scope_id` | `chave.recorte(perfil_id, lista_id)` | o mesmo, com o `id` do Perfil do rascunho e o da lista |
| `seed` | `normalizacao.normalizar(material_bruto, regra)` | o mesmo, sobre o material fictício (R-004) |
| `public_numbers` | 1 a N, por protocolo crescente (`projecao`) | 1 a N, na ordem das inscrições fictícias |

**A única entrada que difere é o resumo da relação**, e ela só muda *qual* ordem sai, e não a forma
de calcular. Por isso o teste de equivalência (R-009) injeta o resumo oficial na função da prévia e
compara as ordens: se a forma fosse outra, as ordens divergiriam.

**Onde mora.** Em `sorteios/domain/simulacao.py` (novo, puro): a direção de dependência é
`sorteios → classificacao`, como `classificacao/application/selectors.py` e `editais/domain/marcos.py`
registram por escrito,
e a prévia do sorteio precisa da ordem do sorteio **e** do corte da classificação. A `classificacao`
não importa nada daqui.

**Alternativa recusada.** Pôr a ordem do sorteio dentro de `classificacao/application/previa.py`, ao lado
da ordem por pontuação: inverteria a dependência, que `classificacao/application/selectors.py` diz por
escrito que não se inverte.

## R-003 — Quanto custa, e se as 1.000 rodadas cabem

**Medição.** [prototipo/medicao.py](prototipo/medicao.py), `custo()`, nesta máquina, em 21/10/2026:

| População | Uma rodada | 1.000 rodadas |
|---|---|---|
| 32 inscritos, 2 reservadas | 0,2 ms | 0,09 s |
| **500 inscritos, 6 reservadas** (pior caso da SC-928) | **1,6 ms** | **1,39 s** |

A ordem de 500 números públicos sozinha custa 0,9 ms (`chave.ordem` vinte vezes). A ocupação é a
menor parte.

**Decisão.** **1.000 rodadas, sempre.** O pior caso fica em ~1,4 s, contra o orçamento de 5 s da SC-928,
com folga para a renderização e para máquina mais lenta. A cláusula da FR-2501 que admite reduzir as
rodadas fica como salvaguarda, e o plano não a usa; se a implementação medir acima de 3 s no pior caso,
ela volta à mesa antes de reduzir.

**O resumo calcula sem guardar cada rodada.** Cada rodada produz só os contadores da FR-2503, e o
resumo os soma; não há lista de 1.000 ordens em memória.

**Alternativas recusadas.** Calcular o resumo por fórmula fechada (hipergeométrica), que seria
instantâneo: violaria a FR-2504 — o resumo é a agregação do motor, e não um modelo dele — e deixaria de
mostrar o comportamento atual em DP-1 e DP-2, que fórmula nenhuma reproduz sem reimplementar a regra.
Calcular em segundo plano, por fila: o painel é síncrono desde a `094`, e 1,4 s não pede fila.

## R-004 — A semente fictícia: quem gera, em que formato, e como se prova a origem

**O app do sorteio não pode gerar aleatoriedade, e isso decide onde a semente nasce.**
`tests/unit/sorteios/test_sem_gerador_pseudoaleatorio.py` varre todo arquivo de
`processo_seletivo/sorteios/` e reprova importação de `random`, `secrets`, `numpy` e `os.urandom`
(FR-026 da `021`): a ordem oficial tem de ser reproduzível, e um gerador no app seria a porta para
deixar de ser. **A prévia não abre exceção.** A semente fictícia nasce na **interface**
(`interface/previa_do_sorteio.py`), com `secrets.randbelow`, e entra em `sorteios/domain/simulacao.py`
como parâmetro — o app continua sem gerador, e a varredura continua verde sem emenda.

**Formato.** Cinco números de seis dígitos, separados por espaço — a forma do `listaDezenas` da
Loteria Federal que `LoteriaFederal._bilhetes_premiados` devolve (D-007). A semente é a normalização
desse material pela regra declarada no método; sem regra, `DIGITOS_EM_SEQUENCIA`.

**Prova de origem (FR-2483).** O material viaja no formulário do painel como **token assinado** por
`django.core.signing`, com `salt` próprio da prévia do sorteio e com o Edital, o Perfil e o marco
dentro do conteúdo assinado. O servidor só aceita token que ele assinou para aquele marco; token
ausente gera semente nova; token inválido ou de outro marco é recusa, com o painel dizendo que a
semente não foi reconhecida e oferecendo "Sortear de novo" — e **sem calcular** (SC-931).

**Por que assinar, e não guardar na sessão.** A sessão seria uma escrita a cada "Sortear de novo", e a
FR-2509 proíbe escrita; e duas abas do mesmo Edital disputariam a mesma chave de sessão. O token não
escreve nada e cada aba tem o seu.

**Sem prazo de validade.** O token não carrega segredo nem dado de ninguém: ele só prova que o material
saiu do servidor. Um token de ontem, no mesmo marco, reproduz a mesma prévia — que é o que se quer
quando o elaborador mostra a rodada a alguém.

**Alternativa recusada.** Derivar a semente do instante ou do `id` do marco: seria previsível e
repetiria a mesma semente para todo mundo, que é o defeito da semente fixa que o usuário recusou em
D-001.

## R-005 — A população por lista, os nomes estáveis e a relação fictícia

**Decisão.** A população é uma quantidade por lista — `inscritos-ampla` e `inscritos-<lista_id>` no
formulário do painel. As pessoas fictícias nascem por **vaga de lista**: a i-ésima pessoa só da ampla, a
i-ésima autodeclarada de cada reservada. Assim, aumentar uma quantidade **acrescenta** gente no fim
daquela lista e não renomeia ninguém (FR-2490).

**Os nomes** vêm do mesmo repertório de `classificacao/domain/cenarios_da_previa.py` (`_NOMES`, sem
marca de grupo — FR-2342 da `095`), indexados pela posição da pessoa na população, e não pela lista.
O que muda de lista é a Modalidade, nunca o nome.

**A relação fictícia** de cada recorte é numerada de 1 a N na ordem das inscrições fictícias (a ampla
com todos, cada reservada com os autodeclarados dela), e o resumo dela é o SHA-256 canônico de
`{"previaDoSorteio": true, perfil, lista, participantes: [(número, nome)]}`. A forma é deliberadamente
**outra** que a de `projecao.conteudo_canonico`: o resumo fictício nunca pode coincidir com o de uma
relação real, nem ser confundido com um.

**A sugestão** é o dobro das vagas publicadas na linha de cada lista, e dez para linha sem quantidade
(FR-2487). Com a população da história 1 (10, 3 e 2 vagas), ela sugere 20 só na ampla, 6 PPI e 4 PcD —
a população medida em R-001.

**O limite** é 600 no total (`cenarios_da_previa.TETO`) e seis reservadas
(`previa.RESERVADAS_COBERTAS`) — os mesmos da `094` e da `095`.

## R-006 — Os recortes: a derivação da ocupação, e o que fica de fora

**Decisão.** Os recortes da prévia são os de `editais/domain/recortes.recortes_do_perfil`, a derivação
única da `034` que o fragmento da `095` já usa. A Modalidade apontada como ampla não vira recorte
(D-005).

**O que isso deixa de fora, medido.** `sorteios/application/previa.py::recortes_do_marco`, a derivação
da tela do sorteio, inclui **toda** Modalidade declarada — inclusive a apontada como ampla, que ganha
relação e sorteio próprios. Num Perfil assim, o sorteio oficial tem um recorte a mais que a prévia. O
painel diz isso numa frase (D-005) quando o Perfil aponta uma Modalidade como ampla; nos Perfis que
deixam a ampla na linha geral, que é o caso recomendado desde a `039`, as duas derivações coincidem.

## R-007 — O fragmento, o botão e o painel

**Decisão.** **A mesma rota** da `094` — `fragmentos/perfil/<indice>/marco/<sub>/previa` —, que hoje
devolve "A prévia cobre marcos pela pontuação" para marco por sorteio (`calculo.ForaDaFatia`). Ela passa
a despachar pela forma de produção do marco: pontuação segue para `previa_da_classificacao.contexto`,
sorteio para `previa_do_sorteio.contexto`, e cada uma renderiza o seu template. A autorização, o 204 sem
Edital e o "sem marco" são os da `094`, sem mudança.

**O botão** "Simular sorteio" entra no `_marco.html` ao lado do "Simular classificação", na condição
`orderProduction == "POR_SORTEIO"`, com o mesmo `hx-get`, `hx-include` do cartão do Perfil e
`hx-target` do painel.

**Os parâmetros novos** do fragmento: `semente` (o token da R-004), `sortear=1` ("Sortear de novo"),
`inscritos-ampla` e `inscritos-<lista_id>`, além de `vista` e `recorte`, que são os da `095`.

**O template** é `_previa_do_sorteio.html`, novo, que inclui os parciais da `095` onde eles servem
(`_ocupacao_da_previa.html` e `_marcas_do_recorte.html`) e acrescenta três: a faixa da semente, a
população e o resumo das rodadas. A folha é a da prévia (`telas/previa-da-classificacao.css`),
acrescida — CSP e `FR-2512`.

**Alternativa recusada.** Uma rota nova, só do sorteio: duplicaria autorização, leitura do rascunho e
montagem dos recortes que o fragmento atual já faz, e o botão do cartão teria duas URLs a escolher pela
forma — que é a decisão que o servidor já toma melhor.

## R-008 — O que se reaproveita da `094` e da `095`, e o que precisa ficar público

A ordem do sorteio é nova; o resto **é** o motor da prévia, e não uma cópia dele:

| Peça | Hoje | Na `098` |
|---|---|---|
| corte de um recorte a partir de uma ordem | `classificacao/application/previa.py::_corte`, privada | passa a pública (`corte_da_ordem`), sem mudar de corpo; a `094` continua chamando |
| entrada da rodada de ocupação | `_entrada_da_rodada`, privada | idem (`entrada_da_rodada`) |
| `impedido`, `consequencias` | públicas | chamadas como estão |
| rodada de ocupação | `ocupacao/domain/rodada_da_previa.rodada`, injetada pela interface | injetada do mesmo jeito (`apurar_recortes_com(especie)`) |
| jornada, seletor, marcas, bloco da ocupação | `interface/previa_da_classificacao.py` e parciais | reaproveitados; a jornada ganha o caso do marco por sorteio simulado (FR-2480) |

**A ordem do sorteio entra no formato que essas peças leem**: `{inscricao_id, posicao,
empate_residual: False, numero_publico}`. Sem empate (FR-2495) porque o desempate da chave é pelo
número público (§ 4.2 do contrato do algoritmo), e `faixa.calcular` nunca encontra empate atravessando
o corte.

**Fronteira de dependência.** `sorteios/domain/simulacao.py` importa `sorteios.domain.chave`,
`sorteios.domain.normalizacao` e nada de `classificacao`; `sorteios/application/simulacao.py` importa
o corte público de `classificacao/application/previa.py` (direção permitida); a ocupação chega por
parâmetro, como na `095` — `tests/test_dependencia_da_ocupacao.py` continua valendo.

## R-009 — A equivalência com o caminho oficial

**Decisão.** Dois testes, como a `095`:

1. **Ordem** (unitário, sem banco): para os vetores normativos do algoritmo
   (`contracts/algoritmo-sorteio.md` da `021`) e para relações sintéticas, a ordem de
   `simulacao.ordem_do_recorte` com o resumo injetado é a de `chave.ordenar(chave.chaves(...))`.
2. **Rodada** (integração, PostgreSQL): um Edital com marco por sorteio, PPI e PcD; inscrições
   submetidas por lista; relação publicada por recorte; ocorrência observada pela `FonteDeTeste` com
   `MATERIAL` apontando o material fictício; sorteio constituído, corte e apuração emitidos pelo
   caminho oficial. A prévia, com os mesmos participantes, o mesmo material e os resumos oficiais
   injetados, produz as mesmas ordens, as mesmas faixas, as mesmas quatro quantidades por recorte e as
   mesmas vagas cedidas (SC-927). Uma sentinela muda um dígito do material só na prévia e confere que
   a igualdade **quebra**: sem ela, um teste que comparasse nada com nada passaria.

**O que a implementação mediu, em 21/10/2026.** (a) A sentinela planejada — trocar a regra de
normalização — **não morde**: com material no formato da Loteria Federal, `DIGITOS_EM_SEQUENCIA` e
`TEXTO_LITERAL` dão a mesma semente. A sentinela troca o material. (b) A **lista reservada vazia**
não tem relação no caminho oficial (`relation_would_be_empty`), nem corte (`sem_ato_vigente`), nem
apuração (`ordem_nao_vigente`), e por isso a vaga dela não reverte nem sob "por saldo". A prévia
passou a reproduzir isso, e o achado está em
[doc/achado-reservada-vazia-nao-reverte.md](../../doc/achado-reservada-vazia-nao-reverte.md).
(c) O resumo da relação oficial cobre o `id` dela, que nasce sorteado: cada execução da equivalência
é um caso novo. Seis execuções seguidas, dezoito casos com reversão variada, deram igualdade em
todos.

## R-010 — O que muda na `094`, e o que os testes dela dizem hoje

Três requisitos da `094` dizem que o sorteio não é simulado (FR-2200, FR-2251, FR-2254), e três testes
os prendem:

| Teste | O que afirma hoje | Na `098` |
|---|---|---|
| `tests/interface/test_previa_da_classificacao.py::test_o_botao_nao_aparece_no_marco_por_sorteio` | sem "Simular classificação" em marco por sorteio | continua verdadeiro, e ganha o par: "Simular sorteio" aparece |
| `…::test_marco_por_sorteio_pedido_a_mao_fica_fora_da_fatia` | o fragmento responde "fora da fatia" | **muda**: o fragmento responde a prévia do sorteio |
| `tests/unit/classificacao/test_previa.py::test_sorteio_fica_fora_da_fatia` | `simular` recusa sorteio | continua verdadeiro: `simular` é da pontuação, e o sorteio tem a sua entrada |

A emenda dos três requisitos na `spec.md` da `094`, com a redação anterior registrada, vai no mesmo PR
(D-008). O painel da `094` diz hoje que *"reservas, ocupação, chamadas, recurso e sorteio não são
simulados"* (FR-2254); a frase perde o "sorteio" quando o marco simulado é outro e o Perfil tem marco
por sorteio — que passa a ter prévia própria (FR-2480).
