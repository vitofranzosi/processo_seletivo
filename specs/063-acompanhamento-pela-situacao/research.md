# Research — 063 · Acompanhamento pela situação do candidato

Nenhuma incógnita técnica ficou aberta depois do `/speckit-clarify` de 07/10/2026: as três que
mudavam o que a tela pode afirmar (ocupação, corte, desfecho *Aceite*) foram decididas pelo
usuário. O que segue são as decisões de desenho, cada uma com a alternativa descartada.

## O que o código já oferece

A view `acompanhamento` (`portal/views.py`) já lê, numa requisição, tudo de que a situação precisa:

| Leitura | De onde | O que traz |
|---|---|---|
| `vigentes_por_inscricao([id])` | `convocacao/application/selectors.py` | a convocação vigente, com `desfechos` e `comunicacoes` por `prefetch` |
| `_convocacao_para_a_tela(chamada, agora)` | `portal/views.py` | `desfecho`, `enviada_em`, `estado` (prazo não iniciado / em curso / vencimento decorrido / desfechado) |
| `_requerimento_da_convocacao(...)` | `portal/views.py` | o chamado `preencher` / `conferir` / `""`, e zero consulta sem convocação (decisão 006 da `059`) |
| `resultados_visiveis(registro)` | `resultados/application/selectors.py` | o Resultado de cada Etapa que a publicação vigente autoriza mostrar: `habilitada`, `etapa`, `motivo`, `pontuacao` |
| `situacoes_do_candidato(registro)` | `divulgacao/application/selectors.py` | uma linha por publicação vigente: marco, natureza, situação, posição, empate, pontuação, motivo — e o cabeçalho congelado, já decodificado |
| `objetos_recorriveis(registro)` | `recursos/application/interpor.py` | o que se pode contestar agora, com `fecha_em` |
| `recursos_do_titular(registro)` | `recursos/...` | as peças interpostas e a situação de cada uma |
| `versao.content` | `selecao_publica` | o conteúdo **vigente** do Edital: Perfis com `reserveType`, `reserveLimit`, `callForm`, `competitionModalities` |

E três peças reaproveitáveis: `nome_da_lista(cabecalho)` (`divulgacao/domain/conteudo.py`), que dá
nome à ampla concorrência; `_chave_da_lista` (`portal/leitura.py`, 062), que ordena as listas como o
Perfil as declara; e `FORMA_DE_CONVOCACAO_POR_EXTENSO` (`publicacoes`), a frase que o PDF do Edital
já usa para a forma de convocação.

---

### D-001 — A situação é uma função pura em `portal/situacao.py`

**Decisão.** Um módulo novo, `portal/situacao.py`, com uma função `situacao_da_inscricao(...)` que
recebe o que a view já leu e devolve a projeção `Situacao` (data-model §1). Não consulta o banco, não
lê relógio (recebe `agora`) e não renderiza nada. O template só apresenta (FR-1167).

**Por quê.** A precedência da FR-1168 é a regra desta feature, e regra em `{% if %}` de template não
se testa caso a caso nem se reusa. Função pura deixa a matriz de estados ser testada sem banco
(dezenas de casos em milissegundos) e deixa a contagem de consultas da view intacta (D-007).

**Alternativas.** (a) Lógica no template — descartada pela razão acima e porque a varredura de
vocabulário teria de ler `if`s. (b) Um *selector* em `divulgacao` ou `convocacao` — descartado: a
situação cruza cinco contextos (divulgação, resultados, convocação, requerimento, recursos), e pô-la
em qualquer um deles faria esse contexto importar os outros quatro, o que os testes de dependência
(`test_dependencia_da_convocacao.py`, `test_dependencia_da_ocupacao.py`) recusam. O portal já é o
lugar onde esses contextos se encontram.

### D-002 — Precedência fechada, a primeira que se aplica vence

**Decisão.** Nesta ordem:

1. desfecho da convocação vigente → rótulo da tabela da FR-1172;
2. convocação vigente sem desfecho → "Convocado";
3. Resultado de Etapa visível *eliminada* → "Eliminado";
4. ao menos uma lista *classificada* em publicação **definitiva** → "Aguardando chamada";
5. ao menos uma lista *classificada*, todas preliminares → "Aguardando resultado definitivo";
6. todas as listas *sem posição* → "Não classificado";
7. nada divulgado → "Inscrição enviada".

**Por quê.** Cada degrau é um ato mais recente no certame que o seguinte, e o mais recente é o que a
pessoa precisa ler primeiro. A convocação precede a eliminação porque a convocação *para
regularizar* existe justamente depois de um indeferimento.

**O degrau 5 é refinamento da FR-1170**, e não estado inventado: a natureza é do ato. "Aguardando
chamada" com resultado só preliminar diria à pessoa que a fase seguinte é a chamada, quando a
seguinte é o definitivo — e o recurso. A spec foi ajustada para nomeá-lo.

**Alternativa.** Um estado por lista, sem síntese — descartada pelo princípio 1: o topo é **uma**
situação.

### D-003 — A lista da convocação sai do conteúdo vigente, e o nome é o de `nome_da_lista`

**Decisão.** `Convocacao.lista_id` nulo → "Ampla concorrência"; senão o `name` da Modalidade em
`competitionModalities` do Perfil no conteúdo vigente; e, se a Retificação a tirou, o nome gravado no
cartão da mesma lista.

**Por quê.** O porquê da convocação nomeia a lista (FR-1173), e a convocação não guarda nome. O
vigente é o mesmo de onde a página do Edital tira o nome (062).

### D-004 — Canal e cadastro reserva vêm do Perfil no conteúdo vigente

**Decisão.** `callForm` → a frase de `FORMA_DE_CONVOCACAO_POR_EXTENSO` ("por publicação no endereço
eletrônico do certame" / "por mensagem individual à pessoa convocada"); vazio → nenhum canal
(FR-1179). `reserveType` `LIMITED` → "O Edital prevê cadastro reserva de até N pessoas para este
Perfil."; `UNLIMITED` → "O Edital prevê cadastro reserva para este Perfil, sem limite de pessoas.";
`NONE` → nada (FR-1180).

**Por quê o vigente, e não a versão aceita.** São fatos sobre o que vai acontecer — como serão as
próximas chamadas —, e o calendário de hoje é o vigente, pelo mesmo raciocínio que já faz o
Cronograma desta tela vir do vigente (docstring da view). A frase do PDF é reaproveitada para que o
Edital e a tela não digam a mesma coisa de duas maneiras.

**Alternativa.** Ler `PerfilVaga` relacional — descartada: o relacional guarda o estado do dia da
publicação e não acompanha Retificação.

### D-005 — As frases neutras e as de canal moram numa tabela só, no módulo

**Decisão.** As duas frases neutras da FR-1177, as frases de canal e de cadastro reserva e os rótulos
das situações são constantes de `portal/situacao.py`. O template não escreve frase de consequência.

**Por quê.** A SC-453 exige provar que nenhuma outra frase de consequência existe; com as frases num
lugar só, a prova é ler um dicionário, e a varredura do template só precisa garantir que ele não
acrescentou nenhuma.

### D-006 — O cartão por lista nasce em `situacoes_do_candidato`, com duas chaves a mais

**Decisão.** `situacoes_do_candidato` passa a devolver também `lista` (`nome_da_lista(cabecalho)`) e
`lista_id`. A ordem dos cartões continua a do marco (FR-058) e, dentro do marco, a de
`_chave_da_lista` (ampla primeiro, depois a ordem do Perfil).

**Por quê.** O cabeçalho já é decodificado ali; acrescentar duas chaves não custa consulta e não muda
quem já lê as outras (`objetos_recorriveis`).

### D-007 — Nenhuma consulta nova, provado por contagem

**Decisão.** A view chama `situacao_da_inscricao` com o que já leu. Um teste conta as consultas do
acompanhamento com uma lista e com três, com e sem convocação, e exige o mesmo número (SC-454).

**Por quê.** O `test_orcamento_de_consulta.py` da `029` já prende o zero do requerimento sem
convocação; esta feature não pode ser a que o quebra, e a regra mais simples é não ler nada novo.
Por isso o porquê do Requerimento enviado não traz data: a política da `029` devolve o estado, e não
o instante (a spec foi ajustada).

### D-008 — O detalhe da convocação fica, sem as frases de situação

**Decisão.** `_convocacao_da_inscricao.html` continua abaixo do topo, reduzido aos dados (espécie,
comunicação enviada em, prazo) e ao link "Ver convocação". As frases de estado (prazo não iniciado,
vencimento decorrido, situação registrada) e o chamado ao requerimento sobem para o topo (FR-1183).

**Por quê.** Duas redações do mesmo estado fazem a pessoa achar que são dois estados — o que o
comentário do próprio parcial já dizia. O parcial continua listado na varredura da `019`.

### D-009 — "Resultado divulgado" vira "Classificação por lista"

**Decisão.** O `h2` passa a "Classificação por lista"; cada cartão é `h3` com "{lista} — {marco}",
uma linha com natureza e data, outra com a posição oficial ("8º lugar", "posição compartilhada") e a
pontuação, ou "Sem posição nesta lista" com o motivo (FR-1181, FR-1182).

**Por quê.** O título antigo valia para um bloco por marco; com uma lista por cartão, o que distingue
um cartão do vizinho é a lista, e ela vem primeiro.

### D-010 — Vocabulário por varredura do HTML renderizado e do código visível

**Decisão.** Um teste novo renderiza o acompanhamento em todos os cenários da matriz e procura, no
HTML, as palavras da UX-158; e o `portal/situacao.py` e o `acompanhamento.html` entram nas listas
literais de `test_vocabulario_da_convocacao.py` e `test_vocabulario_do_requerimento.py`.

**Por quê.** As varreduras do repositório têm lista literal, e tela nova escapa delas em silêncio. O
HTML renderizado não carrega `{% comment %}`, e é o que a pessoa lê — o comentário pode explicar por
que "Classificado" é proibido sem reprovar a varredura.

### D-011 — A frase da tela da convocação sem chamada

**Decisão.** Em `portal/convocacao.html`, "quem está na lista pode ser chamado quando uma vaga vagar"
dá lugar à frase neutra "Novas chamadas, se houver, serão publicadas conforme o Edital." (FR-1184),
tirada da mesma constante.

### D-012 — Os testes que leem a marcação antiga mudam junto, sem afrouxar

**Decisão.** `test_acompanhamento_resultado.py` (títulos "Resultado divulgado", "Você não foi
classificado") e as asserções da `059` sobre as frases do parcial são reescritos para a marcação
nova, com a mesma força: cada asserção removida tem a substituta que prova a mesma coisa no lugar
novo.

### D-013 — A demonstração numa cópia do banco da 062

**Decisão.** `ps_063_demo`, cópia de `ps_062_demo`, migrada. Casos (a), (b) e (c) com Edson no
Edital 72/2026 (8º na ampla, 2º na PPI, cadastro reserva limitado a 9); caso (d) com Mariana Coutinho
Reis no mesmo Edital (convocada, Requerimento em rascunho, prazo 09/10 às 18h); caso (e) com Ana Silva
no Edital 51/2026, com o desfecho *Aceite* registrado pela gestão no fluxo da `050`.
