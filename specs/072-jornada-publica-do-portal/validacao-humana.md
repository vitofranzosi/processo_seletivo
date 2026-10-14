# Validações humanas da 072 — pendentes

**Situação em 13/10/2026: as duas validações abaixo estão PENDENTES.** Enquanto estiverem, a 072
está com a **implementação técnica concluída**, e **não** validada nem pronta para publicação. Nenhuma
delas pode ser feita pelo agente que implementou a feature.

---

## 1. Percurso conduzido com cinco pessoas (SC-605)

### Objetivo

Verificar, com pessoas de fora do projeto, se as quatro tarefas da jornada pública se cumprem sem
ajuda no celular. **Não mede conversão**: mede compreensão e conclusão de tarefa. Nenhum dado de
navegação é registrado pelo sistema; quem conduz anota à mão.

### Participantes

- Cinco pessoas, nenhuma do projeto nem da equipe que elabora Editais.
- Ao menos duas que nunca se inscreveram num processo seletivo do Ifes.
- Ao menos uma que usa o celular como único acesso à internet.
- Cada uma no **próprio celular**, com o navegador que já usa.

### Preparação

- Banco de demonstração preparado e semeado (`make preparar` + `seed_demo`), servido num endereço que
  o celular alcance; e-mail num coletor que quem conduz consiga ler (o compose tem um, em
  <http://localhost:8025>).
- Termo de consentimento: a pessoa sabe que é observada, que pode parar a qualquer momento, e que o
  que se anota é o que ela faz na tela — não quem ela é.
- **CPF:** a tarefa 3 pede nome e CPF. A pessoa decide se usa o próprio ou um valor de teste
  entregue por quem conduz; o banco é de demonstração e é descartado ao fim. Quem conduz não anota CPF.

### Tarefas (lidas em voz alta, uma de cada vez)

| # | Tarefa dita à pessoa | Conta como sucesso | Requisitos |
|---|---|---|---|
| 1 — Encontrar | "Você soube que o Cefor está com inscrições abertas. Descubra se há vaga para técnico de laboratório e onde é." | Diz o cargo e o lugar (Campus Vitória) sem abrir o PDF do Edital | FR-1600 a FR-1614 |
| 2 — Preparar | "Você poderia se inscrever como professor? O que vai precisar ter em mãos?" | Diz o requisito (mestrado), os documentos e que o Requerimento de Matrícula é pedido na inscrição | FR-1615, FR-1626, FR-1628 |
| 3 — Começar | "Comece a sua inscrição na vaga de professor." | Chega à tela "Sua inscrição" da vaga certa, passando pelo e-mail, pelo código e por "Seus dados", sem voltar atrás nem perguntar | FR-1617 a FR-1625 |
| 4 — Acompanhar | "Você participou do Edital 51/2026. Saiu algum resultado? Ainda dá para recorrer? Até quando?" | A partir da vitrine, diz que há resultado preliminar e a data e a hora do prazo de recurso | FR-1629 a FR-1636 |

### Ficha de registro (uma por pessoa)

| Tarefa | Concluiu sem ajuda? (sim / com ajuda / não) | Tempo aproximado | Onde hesitou (tela e o que disse) |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |

Perguntas abertas ao fim: *"O que foi mais difícil?"* · *"Em algum momento você achou que tinha errado
alguma coisa?"* · *"Alguma frase prometeu algo que você não esperava?"*

### Critério de aceite

Proposto na spec (SC-605): **ao menos quatro das cinco pessoas concluem cada tarefa sem ajuda.** O
responsável pelo produto pode ajustar o limite **antes** de conduzir as sessões; ajustá-lo depois de
ver o resultado tira dele o valor de critério.

### Onde registrar

Uma seção nova em [verificacao.md](verificacao.md), com as cinco fichas (sem dado pessoal), o resultado
por tarefa e o que foi visto de hesitação — e, se uma tarefa ficar abaixo do critério, um achado
registrado, e não uma correção feita às pressas.

---

## 2. Texto de finalidade de nome e CPF (FR-1627)

### O texto em vigor na implementação

Na tela "Seus dados" (`backend/processo_seletivo/portal/templates/portal/meus_dados.html`):

> Seu nome completo e seu CPF identificam você nas inscrições e nos resultados. Pedimos uma única
> vez: nas próximas inscrições, não perguntamos de novo.

Quando a pessoa está a caminho de uma vaga, a tela diz antes: *"Inscrição em **Professor de
Informática** · Edital 01/2026 — <título do Edital>"*.

### O que se pede a quem responde pela proteção de dados

1. **A finalidade está correta e completa?** O texto diz para que nome e CPF servem no sistema —
   identificar a pessoa nas inscrições e nos resultados. Se há outra finalidade (por exemplo,
   conferência de identidade na matrícula, ou envio a outro sistema da instituição), ela precisa
   estar no texto.
2. **Falta alguma informação obrigatória no ponto da coleta?** Base legal, controlador, canal do
   encarregado, link para a política de privacidade. A 072 **não** verificou exigência
   legal específica; o texto foi escrito como boa prática alinhada ao Princípio III da Constituição.
3. **"Resultados" é preciso?** O nome aparece em resultados publicados; o CPF não aparece inteiro.
   Se a frase sugerir que o CPF é publicado, ela precisa mudar.

### Alternativa, se houver política de privacidade publicada

> Seu nome completo e seu CPF identificam você nas inscrições e nos resultados. Pedimos uma única
> vez: nas próximas inscrições, não perguntamos de novo. [Como tratamos seus dados](<endereço da política>).

### Onde registrar

A resposta — aprovado, aprovado com ajuste (com o texto final) ou recusado — em
[verificacao.md](verificacao.md), com a data e quem respondeu (cargo, não nome). Ajuste de texto vira
alteração do template e do teste `integration/portal/test_contexto_do_acesso.py`
(`test_seus_dados_nomeia_a_vaga_e_diz_para_que_servem_nome_e_cpf`).
