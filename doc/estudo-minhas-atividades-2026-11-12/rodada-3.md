# Rodada 3: a revisão da rodada 2, o custo medido da página otimizada, a Agenda e o esforço (12/11/2026)

O usuário trouxe uma revisão da rodada 2, com quatro pontos e um cuidado de linguagem. Pediu duas
avaliações: o esforço de desenvolvimento, e se "Minhas atividades" atrapalha o propósito da Agenda
(101).

## 1. Os quatro pontos da revisão, conferidos no código

| # | Ponto | Procede? | O que muda no estudo |
|---|---|---|---|
| 1 | O Gestor que também preside perderia o trabalho dele. `pode_gerir_comissao` verifica `comissao:gerir` antes da presidência (`comissoes/domain/autorizacao.py:92-96`), e a base devolvida é a sistêmica | **Sim** | A página escolhe os Editais pela presidência lida direto em `MembroComissao` (`funcao=PRESIDENTE`), e não pela base. Isso resolve o ponto e a D-2 juntos: a derivação só roda onde a pessoa preside, e lá tudo o que é seu de conduzir é seu por vínculo. O `Alcance` não precisa mudar |
| 2 | A pessoa do setor da formalização pode estar designada sem integrar a comissão (`formalizacao/domain/autorizacao.py:77`) | **Sim** | A formalização fica fora do MVP e é nomeada na nota de cobertura. A pessoa do setor já tem uma lista própria: "Formalização", na barra (`views_formalizacao.lista`). Entrar na página depois é uma consulta a `designacoes_vigentes(pessoa=…)` |
| 3 | A melhoria de desempenho não estava demonstrada | **Sim** | Medida agora (seção 2). Para a presidência, a redução é modesta |
| 4 | "Cache é outra fonte de verdade" é excessivo | **Sim, em parte** | A frase valia para cache **entre requisições**, que precisa ser invalidado a cada ato. Reler a mesma leitura dentro de uma requisição não cria estado, e é a redução 2. A rodada 2 misturou os dois na mesma frase |

**O cuidado de linguagem procede.** A rodada 1 o previa para a faixa, e não para a página. Enquanto
famílias ficarem de fora (formalização, publicação das inscrições e das convocações, avisos,
Requerimento, o Publicador na unidade inteira), a página diz o que cobre. "Nada para fazer agora"
não pode virar "você não tem nada a fazer no GPS".

## 2. O custo da página otimizada, medido

[`validacao/custo_otimizado.py`](validacao/custo_otimizado.py), saída em
[`validacao/custo-otimizado.txt`](validacao/custo-otimizado.txt). As reduções foram simuladas sem
mudar o código. A versão vigente foi memorizada por Edital, e a faixa da 104 foi lida uma vez. Em cada
montagem, a medição conferiu que os itens "seus" são os mesmos da montagem atual. Foram.

| Identidade | Atual | R1 (só onde preside) | R1 + R2 (versão vigente uma vez) | R1 + R2 + R3 (104 uma vez) |
|---|---|---|---|---|
| presidência (11 Editais presididos) | 1080 · 1,2 s | 1081 · 0,8 s | **873 · 0,6 s** | 865 · 0,6 s |
| avaliador (membro de 11, preside 0) | 1697 · 1,6 s | **56 · 0,08 s** | 38 · 0,08 s | — |

**O que os números dizem:**
- **R1 resolve o membro, e não a presidência.** O avaliador cai de 1697 para 56 consultas, com o
  mesmo item. A presidência preside os onze Editais, e para ela R1 não muda nada: a queda de tempo
  dessa coluna é cache aquecido do PostgreSQL, e não redução.
- **R2 dá −19% para a presidência.** É útil, mas não muda a natureza do custo.
- **R3 é desprezível.** Sai da proposta.
- **O custo da presidência é a própria derivação:** cerca de 79 consultas por Edital presidido,
  linear. As tabelas mais lidas depois de R2 são `resultados_resultadoetapa`, `classificacao_corte`,
  `inscricoes_inscricao` e `classificacao_atodeordenacao`, lidas por marco e por lista. Reduzir isso
  é leitura em lote dentro da 127, e é trabalho grande.

**O que isso significa na prática.** Mudar de página não reduz o custo da presidência, como a revisão
diz: ele se concentra em quem abre a página. A conta é cerca de 80 consultas por Edital presidido e
em andamento:
- com 5 Editais, cerca de 400 consultas, menos de meio segundo local;
- com 11, cerca de 870 consultas e 0,6 s;
- com 30, cerca de 2400 consultas, na casa de 2 s.

**Quantos Editais uma presidência real conduz ao mesmo tempo não foi medido.** A equipe inicial é
de 2–3 pessoas. A spec precisa de um teto por Edital presidido, no molde de
`test_andamento_em_escala.py`. Se o número real passar de uma dezena, a página carrega cada Edital
como bloco próprio, depois da primeira tela. Isso não muda a regra, e não é otimização prematura.

## 3. "Minhas atividades" atrapalha a Agenda?

**Não. Ela tira da Agenda a pressão de virar lista de tarefas.**

A Agenda é **projeção do cronograma publicado** (D-001 da 101): o que o Edital declarou, para toda
identidade (D-004). Ela diz "data passada", e nunca "concluído", porque "previsto não é executado"
(D-006). A spec deixou fora, por decisão do usuário de 29/10:
- controle de tarefa;
- atribuição de responsável;
- o prazo efetivamente aberto pela publicação de um ato.

"Minhas atividades" lê o oposto. Ela lê os **atos**: o que foi praticado, o que falta e o que espera.
Não lê o cronograma (D-4 deste estudo). As duas respondem perguntas que não se sobrepõem:

| | Agenda | Minhas atividades |
|---|---|---|
| Fonte | cronograma da versão vigente | atos (derivação da 127) |
| Pergunta | o que está previsto, e quando | o que eu tenho a fazer agora |
| Para quem | toda identidade, a unidade inteira | a pessoa, nos Editais em que ela tem vínculo |
| Data | a do Edital | o fim de uma espera, aberta por um ato |

**Dois cuidados, para que uma não contradiga a outra:**
1. **Dois prazos de recurso com datas diferentes.** A Agenda mostra o "prazo de recurso" do
   cronograma. "Minhas atividades" mostra o fim da janela aberta pela publicação (`janela_aberta_ate`),
   que pode ser outro dia. A frase da espera diz de onde vem a data: "o prazo de recurso aberto pela
   publicação corre até 17/11". Nunca só "prazo até 17/11".
2. **A Agenda não recebe atividade, e "Minhas atividades" não recebe evento.** Cada espera pode levar
   à Agenda filtrada pelo Edital (o filtro existe: D-007 da 101), mas a página não lista evento de
   cronograma.

## 4. O esforço de desenvolvimento

**É médio, e não pequeno: vai além da troca de nome, como a revisão diz. Mas não toca em nada do que
é caro no projeto:**
- nenhum modelo, nenhuma migration, nenhuma tabela append-only;
- nenhuma regra de autorização nova;
- nenhuma mudança na derivação da 127.

| Peça | Tamanho | Por quê |
|---|---|---|
| Escolher os Editais: presidência por `MembroComissao`, alocação à conferência | P | duas consultas, já medidas |
| Montar a página: as providências suas dos Editais presididos, a avaliação pela carga, o agrupamento entre Editais, a nota de cobertura, o Edital que não pôde ser lido | M | função pura de agrupamento, com teste unitário; a view e o template existentes ganham seções |
| R2: a versão vigente uma vez por requisição | M | atravessa várias features que chamam `effective_version` direto. Pode ficar para um segundo PR, porque dá −19% |
| Trocar o nome visível; a nota da faixa da Lista apontando para a página | P no código, M nos documentos | a barra, os títulos e as trilhas; os testes que fixam "Minhas Etapas" e a frase `FORA_DA_FAIXA`; o guia da equipe e o manual |
| Testes | **M, a maior parte** | coerência: cada linha da página é a mesma célula SUA do Centro; o membro que não preside não faz a derivação rodar; o Gestor que preside vê o seu e o Gestor que não preside não vê; o teto de consultas por Edital presidido; a nota de cobertura |

**Ordem de grandeza: uma spec, um PR principal e um PR de documentação**, mais o R2 se a medição
real pedir. O risco está concentrado em dois lugares:
- o custo da presidência, que é linear e não tem otimização barata;
- a disciplina de não escrever regra nova na página. O teste de coerência é a guarda.

## 5. Decisões, depois da rodada 3

- **D-1:** mantida ("Minhas Etapas" renomeada).
- **D-2:** realizada pela escolha dos Editais por presidência. Não exige mudar o `Alcance`.
- **D-7 (nova): a formalização no MVP.** O estudo sugere (a): fica fora, nomeada na cobertura,
  porque já tem lista própria. A alternativa (b) é entrar pela designação vigente.
- **D-8 (nova): o teto de Editais presididos.** O estudo sugere (a): medir quantos Editais uma
  presidência real conduz ao mesmo tempo antes de fixar o teto. A alternativa (b) é carregar por
  Edital desde o início.
