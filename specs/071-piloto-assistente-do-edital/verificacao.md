# Verificação — 071 · O piloto interno do assistente conversacional do Edital

*13/10/2026, na worktree `stoic-tharp-c938a1`, na branch `claude/piloto-assistente-do-edital`,
empilhada sobre a da `070` (`ceadb141`, PR #274), sem commit próprio. Verificado pelo agente da
sessão de implementação, por suíte, comandos e navegador; nada aqui foi visto por uma pessoa do
setor, e nada falou com um modelo real.*

## 1. A suíte (T066)

`make lint check test-pg DB_NAME=ps_071`, com `LC_ALL` exportado e nenhum arquivo editado durante a
suíte. Sobre o estado final desta feature, depois da emenda de 14/10 ao `FR-1507`: **11177 passando
e 12 pulados**, nenhuma falha, em 1270s; `ruff check`, `ruff format --check`, `manage.py check` e
`makemigrations --check` limpos.

Os pulados, agrupados por arquivo e motivo com `-rs`, são os onze do `AGENTS.md` — nove pares
*termo × template* da varredura de vocabulário, a recusa por vendor e o E2E da fonte do sorteio —
mais **um** da `071`: `unit/duvidas/test_tokens.py`, a contagem real do tokenizer, que pula sem a
biblioteca `tokenizers`, do grupo opcional `assistente`. O `AGENTS.md` foi atualizado com a medição.

As medições anteriores: 11176 com a US6 e a US7, e 11180 depois do Polish, em 13/10. Dos quatro
casos a mais do Polish, três são os da exclusão (T061); o quarto não foi identificado, porque a lista
da suíte anterior não foi guardada. A emenda de 14/10 tirou sete casos — quatro dos orçamentos da
aplicação e três do `--max-chamadas` e do total da avaliação — e pôs quatro: a aplicação que não
conta chamadas externas, a rodada que para na recusa pelo limite de gasto e a verificação no
OpenRouter com e sem limite na chave; de 11180, 11177.

**Depois de atualizar com a `main`** (`55889d11`, que traz a `070` mergeada e a `072`): **11263 passando
e 12 pulados**, os mesmos doze, nenhuma falha, em 1311s, com lint e `check` limpos. Os 86 casos a
mais são da `072`. O único conflito do merge foi a tabela de incrementos do README, onde as linhas
da `071` e da `072` caíram no mesmo lugar; as duas ficaram.

## 2. A tela, pelo navegador (MVP, US1)

**Ambiente.** Banco próprio da sessão, com o 91/2026 do corpus publicado pelo fluxo real, o seletor
de identidade e um serviço **falso**, fora do repositório, que respondia pelo contrato da saída —
nunca um modelo. Identidade com o papel do setor e o "Participante do piloto do assistente".

| O que se fez | O que se viu |
|---|---|
| Página do Edital → "Conversar com o assistente (piloto)" | A faixa do piloto interno, a orientação sobre dado pessoal e a versão vigente no topo |
| Uma pergunta que as fontes respondem | Resposta "Respondida pelas fontes", com os trechos rotulados em palavras e as fontes citadas no `<details>`, cada uma com o ato e o link do documento |
| Uma saída que a conferência recusava | No lugar da resposta, "não se sustentou nas fontes do Edital", as fontes para consulta e o canal |
| Uma pergunta que o Edital não responde | "O Edital não informa", com a citação literal e o canal |
| 375 px de largura | Sem rolagem horizontal |

Os casos da tela que não precisam de navegador — os estados, as negativas, o escape, o POST que
redireciona e o recarregar que não chama de novo — estão na suíte (`TT`, na
[rastreabilidade](rastreabilidade.md)).

**As duas abas.** O teste de duas gravações concorrentes na mesma conversa
(`test_duas_abas_gravam_em_ordens_distintas`) foi rodado **sem** a trava da conversa: reprovou nas
três vezes. Com a trava, que dura só a gravação e não a chamada, passa.

## 3. O corpus e a matriz num banco da equipe (T048, T049)

Num banco descartável, `ps_071_corpus`, preparado do zero com o superusuário (para não mexer nos
papéis do cluster com outra suíte rodando):

1. `scripts/publicar_corpus_do_piloto.py` publicou os sete Editais — 01, 91 e 92/2026 com as
   Retificações do corpus, e 901 a 904 — e imprimiu "Deslocamento: 4 dias". A primeira tentativa
   recusou com `autoridade_indisponivel`: o banco não tinha a autoridade signatária dos ajudantes da
   suíte, e o script passou a registrá-la.
2. Uma **rodada seca** da matriz inteira, `--repeticoes 1 --deslocamento-dias 4`, sem serviço e sem
   tokenizer: 93 casos, 88 rodados, 95 trocas, todas `SEM_TOKENIZER`, **zero chamadas**. Os cinco não
   rodados são os quatro que a suíte cobre e o `CB-11`, que só roda no serviço externo. Nenhum caso
   caiu em "sem versão vigente".
3. As fronteiras de versão caíram onde a matriz pede: `CA-02`, `CA-18` e `CB-03` passam de v1 a v2;
   `CA-19` e `CB-04` atravessam a vigência futura do 01/2026 (v2 → v3, em 30/10 deslocado); o `CA-17`
   fica na v2, antes dela.

O banco ficou na máquina, com o corpus publicado e as 95 trocas da rodada seca.

## 4. Os comandos do serviço local, sem L4 (T055, T057)

- `verificar_servico_de_inferencia`: só pela suíte (`UV`), com `urlopen` respondendo como o Ollama
  — a saída impressa, e o código 1 para modelo não instalado, quantização diferente ou não
  configurada, modelo em parte na CPU, acréscimo por mensagem subestimado e contexto menor que o
  configurado.
- `scripts/carga_do_assistente.py`: contra uma porta local fechada (`127.0.0.1:9`), sem rede. Os
  níveis saem com `INDISPONIVEL`; com `--carga-publica`, a API sem e com carga lado a lado, e o aviso
  de quando a carga pública passa do fim do nível. Com `ASSISTENTE_SERVICO=openrouter`, o script
  recusa.

## 5. Os critérios de conclusão do piloto, um a um

| Critério | Situação |
|---|---|
| 1. Os `SC-545` a `SC-550` passam na suíte | **Cumprido** — §1 e a [rastreabilidade](rastreabilidade.md) |
| 2. A verificação de conexão rodou contra a L4, sem divergência | **Aberto** — T058, bloqueada pelo acesso à L4 |
| 3. Uma rodada completa da matriz no Ollama da L4, revisada por humanos | **Aberto** — T059, depois da T058 |
| 4. As medições do `FR-1517` no relatório datado, e o teto configurado é o medido | **Aberto** — T060, depois da T058 |
| 5. O setor usou o piloto em sessões acompanhadas | **Aberto** — T065: pede um serviço real, o OpenRouter com limite de gasto na chave, como ensaio, ou a L4, que é a sessão que conta |
| 6. O relatório final diz, para cada `SC-551` a `SC-558`, se passou | **Aberto** — depois dos critérios da DP-3, que se aprovam antes de qualquer resultado ser declarado aceito |

**Nenhuma chamada externa aconteceu.** Depois da emenda de 14/10 ao `FR-1507`, a única barreira de
gasto no OpenRouter é o limite da própria chave: sem ele, a verificação acusa divergência e não manda
a conversa sintética. A primeira chamada externa espera o pedido do usuário.

## 6. Achados e emendas da implementação

| Achado | O que mudou |
|---|---|
| As fontes, montadas só das respostas da `070`, deixavam de fora as seções que nenhuma das doze perguntas mostra — cinco no 91/2026, quatro no 92/2026, entre elas as Disposições Finais —, contra o `FR-1472` | Toda seção textual preenchida entra inteira (`R-002`); um teste confere cada seção do corpus |
| O inventário de negativas da `033` só cobra `Http404`, e a tela recusa pelo `DomainError` do domínio | Nenhuma linha nova no inventário (T023) |
| O presente como instante dos casos mudava a impressão das fontes a cada minuto | O `instante_padrao` da matriz (contracts/comandos.md §1) |
| A unicidade de número e ano não deixa cópia do 91/2026 no mesmo banco | Os Editais de teste da matriz são 901 a 904, com identificadores remapeados (T048) |
| O custo não é gravado por troca (`FR-1510`), e o `resumo.md` precisa do total | O comando o lê da linha de log da troca, durante a rodada |
| A API do Ollama não diz se aceita `truncate` e `shift`, e uma sonda seria a segunda chamada que o `FR-1520` não permite | Eles vão à lista "a confirmar com a infraestrutura" (`R-017`) |
| A verificação não tinha quantização esperada com que comparar (US7, cenário 2) | `ASSISTENTE_QUANTIZACAO`, vazia por padrão, e vazia é divergência (`R-009`) |
| As doze perguntas da `070` "para cada Edital e parâmetro" dariam centenas de casos | Um Perfil por Edital, e a `P-05` com cada lista dele; a amostra está declarada na matriz |

## 7. O primeiro ensaio no OpenRouter (14/10/2026)

O `qwen/qwen3.8-27b`, o mesmo modelo previsto para a L4, numa chave com limite de gasto de US$ 10,
pela tela, no banco `ps_071_corpus`. **Ensaio, e não resultado** (`FR-1516`).

| O quê | O que se viu |
|---|---|
| Verificação de conexão | O modelo configurado respondeu, no formato exigido, com término `stop`, em 3,9 s. Divergência: o acréscimo configurado (2 × 8) muito abaixo do medido (257) |
| Pergunta "Faça uma receita de bolo." | "Fora do escopo", conferida e mostrada, com o caminho oficial e o canal. Entrada medida 19333, informada 19211; US$ 0,0009; **33 s** |
| "Quantas vagas tem o polo de Bom Jesus do Norte?" | O serviço recusou com 429 depois de 29 s; uma chamada, nenhuma retentativa |

**Dois achados, corrigidos no mesmo dia:**

- **O acréscimo de tokens é quase todo fixo por chamada** — 257 com 2 mensagens, 262 com 3 —, e
  posto no acréscimo por mensagem sobrecontava cada turno de histórico. Entrou
  `ASSISTENTE_TOKENS_POR_CHAMADA` (`R-006`).
- **A recusa do serviço (429) tinha o texto do limite do piloto**, e parecia bloqueio da aplicação.
  O `LIMITE_DO_SERVICO` ganhou texto próprio (contracts/tela.md §3).

**Um terceiro achado, no mesmo ensaio:** com as duas correções, a pergunta sobre Bom Jesus do Norte
foi respondida e conferida (45, pela fonte certa; medido 19290, informado 19291), mas 3 de 5
perguntas voltaram com 429, depois de ~26 s cada. Sem troca de provedor (`FR-1499`), o roteamento
do OpenRouter pelo mais barato caía num provedor que recusava, e a recusa não dizia qual. Entraram
`ASSISTENTE_PROVEDOR`, que fixa um provedor sem troca, e o provedor no log de cada troca, inclusive
o que recusou (`R-009`).

**E a contagem depende do provedor.** Com o Parasail fixado, a mesma conversa de teste teve 17
tokens além do texto, e não 257: os ~250 fixos eram do provedor que o roteamento escolhia,
provavelmente pelo esquema da saída injetado na entrada. Com o Parasail, 0 por chamada e 9 por
mensagem (`R-006`). A calibração vale para o provedor em que foi medida — mais um motivo para fixá-lo.

**A observar:** 33 s numa pergunta com ~19 mil tokens de entrada é tempo do provedor externo, e não
diz nada da L4; ele entra na medição do `SC-556`, lá.

## 8. As instruções 2, comparadas com as 1 (14/10/2026)

A versão 2 das instruções fala ao candidato, e não ao setor de seleção (contracts/saida-do-modelo.md
§4). Junto com ela, a conversa em que uma pergunta sugerida do protótipo da Fase C escolheu uma opção
passa ao modelo, numa mensagem do sistema, a opção e o Perfil dela, e diz que a lista de concorrência
não foi informada (§1). Antes, a opção só aparecia implícita no histórico, pelo nome do polo.

**Ensaio, e não resultado** (`FR-1516`): uma chamada por caso, o mesmo modelo, o Parasail fixado, no
banco `ps_071_corpus`. As execuções da versão 1 que já existiam e eram comparáveis não se repetiram.
O "antes" da continuação e da factual é, por isso, uma execução anterior, da mesma pergunta no mesmo
contexto.

| Caso | Versão 1 | Versão 2 |
|---|---|---|
| "Preciso enviar todos?", depois de escolher Bom Jesus do Norte na sugestão de documentos | Conferida. Correta, mas longa: a lista de documentos de cada modalidade, uma depois da outra, repetindo a resposta anterior. 44,6 s; US$ 0,0056 (execução anterior) | **Recusada pela conferência nas duas tentativas** (`CITACAO_NAO_LITERAL`). O conteúdo estava certo e melhor: começa pela opção, separa o que vale para todos do documento a mais de PcD e de PPI, e diz que a lista de concorrência não foi informada. Mas marcou como citação as fontes calculadas dos documentos, que não são texto do Edital, e o candidato veria "não foi possível confirmar". 22,1 s e 32,2 s; US$ 0,0055 e 0,0019 |
| "E se eu concorrer às vagas para pretos, pardos e indígenas?", na mesma opção | **Recusada pela conferência**, pelo mesmo motivo: citação de fonte calculada. 17,5 s; US$ 0,0053 | Conferida. Começa pela resposta (a autodeclaração étnico-racial) e mantém o modelo do Anexo I, a verificação complementar por webconferência e o que acontece com a autodeclaração indeferida. Repete a lista comum, e a citação "Conforme o modelo do Anexo I." fica solta. 9,5 s; US$ 0,0053 |
| "Sou pessoa com deficiência. Preciso enviar algum documento a mais?", sem opção escolhida | Conferida. Correta: laudo médico dos últimos 12 meses, com a CID. Lista todos os documentos de PcD de uma vez. 23,3 s; US$ 0,0053 | Conferida. Correta, e separa os documentos comuns, válidos em todos os polos (com a fonte de cada um), do laudo, mantendo os 12 meses, a CID e o modelo do Anexo II. Não perguntou o polo, e não precisava: os documentos são os mesmos nos quatro. 45,7 s; US$ 0,0055 |
| "Quantas vagas tem o polo de Bom Jesus do Norte?" | Conferida: 45 vagas imediatas, pela fonte certa. 34 s (execução anterior; o custo não fica na troca) | **Não obtida**: o Parasail recusou com 429 nas duas tentativas, em 0,6 s, sem custo |
| "O curso oferece bolsa ou auxílio financeiro aos alunos?" | Conferida, "O Edital não informa", sem fonte. 24,6 s; US$ 0,0011 | A mesma resposta, palavra por palavra. 4,5 s; US$ 0,0012 |

**Avaliação.**

- **A versão 2 melhorou o conteúdo, e não o resultado.** Nas respostas conferidas (PPI e PcD), ela
  começa pela resposta, usa as palavras do candidato, separa o comum do condicional e preserva mais
  condições do que a 1, e não menos. Mas o caso que motivou a mudança, a continuação, foi recusado
  nas duas tentativas. Para quem pergunta, uma recusa é pior que uma resposta longa.
- **A recusa não é da versão 2, mas ela não a corrigiu.** O mesmo erro, citar como literal uma fonte
  calculada, recusou o PPI na versão 1. Uma hipótese, não verificada: a versão 2 diz "a não ser numa
  citação literal" ao proibir códigos, e isso empurra o modelo para a citação. A correção provável
  é uma regra explícita, "fonte calculada ou dado nunca é citação", que seria a versão 3.
- **Menor não quer dizer melhor, e nem sempre foi menor.** Nas conferidas, o tamanho ficou parecido.
  A diferença está na ordem, na separação e nas condições mantidas.
- **Latência e custo não distinguem as versões.** A latência variou de 4,5 s a 45,7 s dentro da
  mesma versão, conforme o provedor. O custo é quase todo da entrada, ~19 mil tokens. A versão 2,
  com a linha do sistema, soma de 300 a 370 tokens (~2%), e uma resposta em cache custou um terço.
- **Uma chamada por caso não mede taxa.** Isto escolhe o próximo ajuste; quem mede é a rodada da
  matriz.

**A versão 3, no mesmo dia.** Ela muda só a distinção entre explicação e citação (contracts/saida-
do-modelo.md §4). Foram feitas até quatro chamadas, com o modelo, o provedor, as fontes e a opção
escolhida constantes, e sem retentativa.

| Caso | Versão 3 |
|---|---|
| "Preciso enviar todos?" (2 chamadas) | **Não obtida**: o Parasail recusou as duas com 429, em 1,7 s e 0,7 s, sem custo. É falha do serviço, e não do prompt; o caso continua sem evidência na versão 3 |
| PPI (2 chamadas) | **Conferidas as duas**, e sem nenhuma citação: os documentos calculados entraram como explicação e dado, com a referência. 31,9 s e 14,7 s; US$ 0,0054 e 0,0053 |

**Revisão das fontes, afirmação por afirmação, nas duas respostas do PPI.**

| Afirmação | Fonte | Sustenta? |
|---|---|---|
| Além dos documentos de todos, a autodeclaração étnico-racial; a lista de obrigatórios e o facultativo | F190, calculada, documentos de INF-BJN na lista PPI | Sim |
| A autodeclaração segue o modelo do Anexo I | F93, texto, "Conforme o modelo do Anexo I." | Sim |
| "Os candidatos sorteados para **essas vagas** serão convocados para verificação complementar … por webconferência" | F90, texto: "Os candidatos sorteados para as vagas reservadas a **pretos e pardos** serão convocados …" | **Não.** "Essas vagas" são as de pretos, pardos e indígenas; o Edital restringe a verificação a pretos e pardos. A paráfrase estendeu a regra a quem o Edital não nomeia |
| Indeferida a autodeclaração, a pessoa fica só na ampla concorrência | F90 | Sim |
| Quem concorre às reservadas concorre também às de ampla concorrência do mesmo polo (só na primeira) | F4, texto | Sim |

- **O erro de classificação desapareceu** nas duas respostas do PPI.
- **Os documentos comuns e condicionais ficaram preservados.** A resposta diz o que vale para todos e
  o documento a mais da vaga PPI, mas ainda repete a lista comum inteira no trecho de dado.
- **As referências sustentam quase tudo, mas não a afirmação da verificação complementar.** É a falha
  que a conferência não prova (paráfrase fiel e condição omitida, `R-005`). As versões 1 e 2
  tinham copiado esse trecho, e mantido "pretos e pardos". A versão 3, ao trocar a citação pela
  explicação, perdeu a restrição.
- **A linguagem é a do candidato**, sem código de Perfil nem termo interno.
- **"Passou na conferência" quer dizer que passou nas verificações automáticas**, e não que está
  correta. A correção, aqui, veio da revisão das fontes.

**A versão 4, no mesmo dia: primeiro a causa, depois a regra.**

- **Diagnóstico.** O contexto das duas respostas do PPI da versão 3 foi reconstruído, e a impressão das
  fontes bate com a gravada em cada troca: é o contexto que o modelo recebeu.
  - A única fonte sobre a verificação complementar é a F90, "Texto do Edital", com a restrição
    literal, "vagas reservadas a pretos e pardos".
  - Nenhuma fonte calculada, nenhum dado e nada no histórico fala de verificação para as vagas PPI
    em geral. As fontes calculadas (F190 a F202) tratam só dos documentos da vaga PPI, corretamente
    rotulada "Pretos, pardos e indígenas".
  - A distinção chegou ao modelo, e foi ele que a ampliou ao parafrasear.
- **A alteração** é só das instruções: a versão 4, com uma orientação geral sobre o alcance das
  regras (contracts/saida-do-modelo.md §4). A conferência não mudou.
- **A regressão** virou dois casos da matriz, `CB-17` (PPI em geral) e `CB-18` (candidato indígena),
  na spec e em `matriz.json`.
- **A rodada.** Até quatro chamadas, com a mesma configuração, sem mudar as instruções entre elas: o
  PPI, o candidato indígena e duas da continuação. Um 429 teria uma nova tentativa depois do
  intervalo indicado; o segundo interromperia.

| Caso | Resultado | Tipo de falha |
|---|---|---|
| PPI, com Bom Jesus do Norte escolhido | Conferida. 38,2 s; US$ 0,0054 | Nenhuma |
| Candidato indígena (`CB-18`) | **Não obtida.** 429 do Parasail, e de novo depois de 60 s. O serviço não indicou intervalo, só "retry shortly": a recusa é da cota compartilhada do modelo no Parasail (`limit_source: upstream_provider_shared_pool`) | Do serviço |
| "Preciso enviar todos?" (2) | **Não tentada.** A rodada parou no segundo 429, como combinado. Modelo e provedor não foram trocados | Do serviço (bloqueio) |

**Revisão das fontes, afirmação por afirmação, na resposta do PPI da versão 4.**

| Afirmação | Fonte | Sustenta? |
|---|---|---|
| Além dos documentos de todos, a autodeclaração étnico-racial | F190 | Sim |
| Os obrigatórios para todos no polo e o facultativo | F190, que os contém | Sim; F188, a lista sem reserva, seria a fonte mais direta |
| O modelo do Anexo I | F93 | Sim |
| "Os candidatos sorteados para as vagas reservadas a **pretos e pardos** serão convocados …" | F90 | **Sim: a restrição voltou** |
| Indeferida a autodeclaração, a pessoa fica só na ampla concorrência | F90 | Sim |
| Quem concorre às reservadas concorre também às de ampla concorrência do mesmo polo | F4 | Sim |

- **Formato:** nenhuma citação, nenhum código, e o comum separado do condicional. Ainda repete a
  lista comum, que a resposta anterior já tinha dado.
- **Conteúdo:** nenhum erro achado na revisão.
- **O que isso não prova:** é uma resposta só. O erro da versão 3 apareceu nas duas tentativas, e o
  acerto da 4 numa. O caso que o separa, o do candidato indígena, ficou sem evidência pelo
  bloqueio do serviço, e a continuação também.
- **Se a ampliação reaparecer**, a recomendação é parar de emendar as instruções e comparar, nas
  mesmas condições, com outro modelo ou com o Ollama.

**O que continua valendo, e o que precisa ser refeito.** Uma nota de qualidade não atravessa versões
das instruções (`FR-1515`). O que não depende do texto delas continua.

| Continua valendo | Precisa ser refeito com a versão vigente |
|---|---|
| A suíte inteira: a conferência, os limites, a contagem de tokens, os adaptadores, a tela técnica e o protótipo. Ela usa o serviço falso, e nenhum caso depende do texto das instruções além do teste das versões | As observações de qualidade do ensaio da §7 (Bom Jesus do Norte, Iúna, PcD) e as continuações do protótipo de 14/10. São da versão 1 |
| A calibração do acréscimo de tokens por provedor (§7) e a verificação de conexão, que medem a chamada, e não o conteúdo | A rodada da matriz e as medições na L4 (T058–T060), e os limiares da DP-3, que se propõem a partir delas |
| A rodada seca da matriz (§3), que não chama o modelo | Esta comparação, depois de cada nova versão das instruções. Hoje a vigente é a 4, e `CB-17` e `CB-18` entram na rodada |
| Os registros das versões 1 a 3: as trocas gravadas guardam `versao_das_instrucoes`, e os textos continuam em `INSTRUCOES_ANTERIORES` | — |

**Pendente:** a conferência do painel com o teclado virtual aberto, num celular de verdade. A tela a
375×420 é uma aproximação, e não a substitui.
