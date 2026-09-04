# Achados de Editais externos

Registro do que a leitura de Editais reais revelou sobre o domínio, **fora do briefing de qualquer
feature**. O briefing da 013 começou a virar depósito disto, e depósito é onde achado vira
requisito por acúmulo.

## A disciplina deste documento

Edital é **evidência**, nunca especificação. O que se registra aqui não é o mecanismo que um
Edital usa, e sim **a pergunta que o domínio precisa saber responder** — e a pergunta não pode
nomear Edital nenhum. O mecanismo entra como prova de que a pergunta existe.

O teste é simples e vale para toda spec que nascer daqui: se a frase que governa a feature só faz
sentido citando um Edital, ela particularizou.

> "Como o Edital declara quem é chamado em seguida" passa.
> "Implementar a tabela de ordem de convocação do 173/2025" reprova.

Quando duas evidências diferentes colapsam na mesma pergunta, a generalização pegou. Quando uma
evidência exige pergunta própria, ela é de fato nova.

## Editais lidos

| Edital | Natureza | O que ele trouxe de novo |
|---|---|---|
| 14/2026 — Orientador de TFC | pessoal, títulos + entrevista | perfis com código, grupos com prioridade, desempate por idade |
| 35/2026 — Especialização | discente, sorteio | cotas, heteroidentificação, análise documental após sorteio |
| 57/2026 — Aperfeiçoamento (unificado) | discente, sorteio, 2 cursos | dois cursos num Edital, sem remanejamento entre eles |
| **173/2025 — Designer Educacional** | **pessoal, cadastro de reserva** | ordem de convocação por modalidade, quatro subgrupos, autopontuação vinculante |
| **28/2026 — Informática na Educação** | discente, sorteio | 280 vagas em 7 polos, reversão dentro do polo |
| **76/2026 — Secretaria Escolar** | discente, chamada pública | cadastro de reserva sem número, impugnação, deriva de outro Edital |
| **77/2026 — FIC, vagas remanescentes** | discente, sorteio | validade do processo, suplente convocável para turma futura |

## O achado que mais custa: a família não define o que o Edital exige

O **173/2025 é seleção de pessoal** — bolsista, prova de títulos, desempate por idade, mesma
natureza do 14/2026 — **e tem cotas e heteroidentificação**: ampla concorrência, PcD, pretos e
pardos, indígenas e quilombolas, com verificação por comissão em videoconferência.

Isso desfaz uma separação que a amostra anterior sugeria, e que quase virou premissa de roadmap:

```
premissa errada:  família pessoal  → sem cota
                  família discente → com cota

o que se observa: cota é escolha do Edital, e atravessa as duas famílias
```

**Consequência:** escolher um vertical de seleção de pessoal não retira cotas do caminho crítico.
Retira do *primeiro Edital escolhido*, que é outra coisa. Qualquer justificativa de priorização
precisa dizer "este Edital não exige", nunca "esta família não exige".

## As perguntas

### P-1 · Como o Edital declara quem é chamado em seguida?

Duas formas observadas — e **elas não são independentes: P-2 escolhe qual se usa.**

```
quantidade conhecida    quantidade por modalidade + destinos do que sobrar
quantidade desconhecida ordem nominal publicada: 1ª AC · 2ª PcD · 3ª PPIQ · 4ª AC · …
```

Sem número de vagas não há sobre o que aplicar proporção, e resta declarar a **sequência do
chamamento**, posição por posição. Foi assim em todo Edital lido: os que têm quadro de vagas
declaram quantidade; o de cadastro de reserva declara ordem.

O domínio precisa do lugar onde essa regra é declarada e executada — que é o que
`RegraNormativa.call_rules` reservou como JSON e nunca consumiu —, e **não** de dois motores
nomeados. Registrá-los como dois motores foi erro de leitura desta análise, corrigido quando os
dois Editais ficaram lado a lado.

*Evidência: 35/57 e 28 (percentual); 173 (ordem nominal).*

### P-2 · A oferta tem quantidade conhecida?

Nem sempre. Há Edital cujo quadro de vagas traz `CR` no lugar do número, e Edital inteiramente de
cadastro de reserva, convocado conforme a necessidade da Administração durante a validade.

`PerfilVaga.reserve_type` já admite `LIMITED` e `UNLIMITED` — **o modelo antecipou e nada
executa**. Ocupar sem quantidade é caso normal, não borda.

*Evidência: 76 (`CR` em cinco polos); 173 (cadastro de reserva puro).*

### P-3 · Por quanto tempo uma classificação produz efeito, e sobre qual oferta?

Processos têm prazo de validade, prorrogável, e dentro dele a classificação **sobrevive ao próprio
processo**: um Edital prevê que, havendo nova oferta do mesmo curso no prazo, os suplentes sejam
convocados para compor a **turma seguinte**.

Isso é mais que "validade": a classificação passa a ser insumo de uma oferta que ainda não existia
quando ela foi produzida.

*Evidência: 77 (6 meses, suplente em nova turma); 173 (2 anos); 76 (prazo do calendário acadêmico).*

### P-4 · Quem pode contestar qual ato publicado, e em que janela?

Três contestações observadas, com alcances diferentes:

```
contra o Edital        qualquer cidadão, até 5 dias úteis após a publicação
contra uma listagem    o candidato que não se encontra na lista de inscritos
contra um resultado    o candidato, na janela do cronograma
```

A primeira **não exige inscrição** — o legitimado não é candidato, é qualquer pessoa. Tratar
recurso como "ato do candidato contra resultado" deixaria essa fora por definição.

*Evidência: 76 (impugnação); 173 (recurso contra a lista de inscritos); todos (recurso contra
resultado).*

### P-5 · Qual é a unidade sobre a qual vagas são contadas, ocupadas e revertidas?

Não é o Edital, e nem sempre é o curso. Há Edital com vagas distribuídas por **polo**, cada polo
com seu próprio quadro de modalidades, e a reversão de vaga não preenchida acontece **dentro do
polo** — não no total.

A lacuna já registrada como "campus" é mais geral do que o nome sugere: a unidade é a **oferta
localizada**, e a matriz é bidimensional.

*Evidência: 28 (280 vagas em 7 polos, reversão por polo); 76 (5 polos com CR); 57 (dois cursos sem
remanejamento entre si).*

### P-6 · Um processo pode derivar de outro, e o que herda dele?

Há Edital cujo objeto declarado é preencher as vagas **não preenchidas por um Edital anterior**,
citando-o pelo número.

Hoje cada Processo é uma ilha. A relação existe no texto publicado e não no domínio, o que
significa que ninguém consegue perguntar quantas vagas sobraram de onde.

*Evidência: 76 (vagas não preenchidas pelo 52/2026); 77 (vagas remanescentes, sem citar a origem).*

### P-7 · O que o candidato declara pode limitar o que a banca atribui?

Sim, em pelo menos um caso: o candidato preenche a expectativa de pontuação na ficha, e o Edital
determina que **não se atribua pontuação que exceda a informada por ele**.

A autopontuação deixa de ser campo de formulário e vira regra de avaliação — teto declarado pelo
próprio avaliado.

*Evidência: 173 (ficha com expectativa vinculante); 14 (ficha com expectativa, sem a cláusula de
teto).*

### P-8 · O sistema é sempre a porta de entrada da inscrição?

Não. Há Edital cuja inscrição ocorre em sistema institucional distinto, com o Edital apenas
apontando o endereço.

A pergunta não é qual sistema vence, e sim se o domínio admite inscrição **originada fora** — e o
que isso faz com protocolo, comprovante e versão aceita.

*Evidência: 76 (inscrição pelo SIGAA).*

### P-9 · Há requisitos que o sistema registra mas não verifica?

Sim, e são comuns em Editais de bolsa: cadastro ativo em sistema de fomento, currículo em
plataforma externa, adimplência fiscal e trabalhista, residência em determinado estado.

São condições de elegibilidade **inverificáveis pelo sistema**. O domínio precisa saber a
diferença entre requisito que ele confere e requisito que ele apenas declara.

*Evidência: 173 (Fapes, Lattes, adimplência, residência); 14 (anuência da chefia imediata).*

## O que estes Editais **confirmaram**, em vez de acrescentar

Vale registrar, porque confirmação é sinal de que a generalização anterior estava certa:

- **Modalidade é dado publicado, não enumeração.** O 173 traz quilombolas como modalidade,
  fundada em legislação de 2025. Se a taxonomia fosse enum, cada lei nova seria migração.
- **A classificação é a mesma capacidade em marcos diferentes.** O 173 publica resultado de etapa,
  recebe recurso e republica — como o 14 já mostrava.
- **Retificação é rotina, não exceção.** Cinco dos sete Editais lidos são versões retificadas.

Duas formas **novas de regra**, que não são categorias e sim estrutura:

- **reversão hierárquica** — vaga não preenchida num subgrupo vai para os outros subgrupos da mesma
  reserva, e só depois para a ampla concorrência;
- **percentual como faixa** — mínimo e máximo, em vez de valor único, contra o
  `RegraNormativa.percentage` que é um decimal só.

## O Edital grande, e por que ele entra sem ser alvo

O **46/2026 — Exame de Seleção dos cursos técnicos integrados** é de outra ordem de grandeza: 3.587
vagas, mais de vinte campi, prova objetiva, nove modalidades de concorrência.

**Ele não é objetivo do produto**, e nada aqui propõe que passe a ser. Entra por um motivo só: ele
exibe, por escrito, a forma completa de um mecanismo que os Editais pequenos usam **colapsado** — e
é isso que permite modelar os pequenos sem escolher uma forma que não cresce.

### A forma completa da modalidade

Cada modalidade é uma **conjunção de fatos sobre a pessoa**, e não um rótulo:

```
AA1 = escola pública ∧ renda ≤ 1 SM      AA2 = escola pública
                    ×
              { PPI | Q | PCD | EP }      EP = o resíduo, sem atributo adicional
```

Nove ao todo, contando a ampla concorrência. O `AC / PPI / PcD` dos Editais pequenos é o caso de
**uma dimensão** disso.

### A forma completa do remanejamento

Cada modalidade declara, **em ordem**, para onde vai a vaga que não preencher:

```
AA1-PPI → AA1-Q → AA1-PCD → AA1-EP → AA2-PPI → AA2-Q → AA2-PCD → AA2-EP → AC
AC      → AA1-PPI → AA1-Q → AA1-PCD → AA1-EP → AA2-PPI → AA2-Q → AA2-PCD → AA2-EP
```

E aqui está a razão de registrar isto:

```
"não preenchida vai para a ampla concorrência"   →  lista de UM destino
reversão entre subgrupos, depois ampla            →  lista de DOIS destinos
a matriz acima                                    →  lista de OITO destinos
```

**É a mesma declaração com profundidades diferentes.** Um Edital pequeno modelado como "sobra vai
para AC" grava no domínio uma regra que era do Edital; modelado como "o Edital declara os destinos,
e aqui há um só", custa o mesmo e não trava.

### O que isso esclarece nos Editais pequenos

Esta é a utilidade concreta, e é o motivo de o achado existir:

| Dúvida que os Editais pequenos deixavam | O que a forma completa mostra |
|---|---|
| "sobra vai para a ampla concorrência" é regra do domínio ou declaração do Edital? | **declaração** — e a lista de um destino é o caso raso da matriz |
| por que 15 suplentes num Edital, 20 noutro, 30 noutro? | é **corte da análise documental**, não propriedade da vaga: o grande analisa "até o triplo das vagas" |
| e quem fica além do corte, o que é? | tem nome: **lista de espera** — classificado, documentação não analisada. Os pequenos têm essa população e não a nomeiam |
| "concorrência concomitante" é regra ou ordem de execução? | **ordem**: classificação geral primeiro, por modalidade depois — que é a formulação executável |
| desempate é campo ou regra? | **lista ordenada de critérios**, aqui com seis, terminando em maior idade |

### O que é do Edital grande e fica fora

Registrado para que ninguém o leia como requisito:

- prova objetiva, gabarito e **recurso de efeito coletivo** (questão anulada dá ponto a todos —
  o provimento reemite o resultado inteiro da Etapa, e não o de um candidato);
- **taxa de inscrição**, isenção com comprovação e recurso próprio, compensação bancária;
- **treineiro** — participante que faz a prova, não concorre e não aparece nos resultados;
- **nome social** e **atendimento especial** com doze condições;
- **aproveitamento de lista de espera entre cursos do mesmo campus**, com manifestação de interesse
  e desistência implícita do curso original;
- a unidade de vaga descendo a `campus × curso × turno`.

Dois desses tocam perguntas já registradas — o aproveitamento entre cursos é P-6 vista de outro
ângulo, e a unidade fina é P-5 — mas nenhum é exigido pelos Editais que estão em vista.

### O que ele confirma

- **impugnação por qualquer pessoa**, em até 5 dias úteis: segundo Edital independente a trazê-la,
  o que a tira da categoria de exceção (P-4);
- **recurso contra atos muito diferentes** — isenção, pagamento, atendimento especial, gabarito,
  análise documental, entrevista (P-4);
- **modalidade como dado publicado**, agora com nove valores em vez de três.

## Onde estas perguntas incidem

Sem virar fila, e sem numeração:

| Pergunta | Incide sobre |
|---|---|
| P-1, P-2, P-5 | ocupação de vagas e modalidades |
| P-3 | convocação e chamadas |
| P-4 | recurso, e um ato anterior a ele que nenhuma spec cobre |
| P-6 | processo e edital |
| P-7 | conclusão de avaliação e inscrição |
| P-8, P-9 | inscrição |

**P-4 é a única que aponta para fora do arco de features previsto**: impugnação acontece entre a
publicação do Edital e o fim das inscrições, é movida por quem não é candidato, e não tem ator no
modelo de autorização.
