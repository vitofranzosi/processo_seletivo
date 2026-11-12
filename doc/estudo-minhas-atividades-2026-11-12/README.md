# Estudo: o GPS orientado ao trabalho de cada pessoa (2026-11-12)

**Pergunta.** Um integrante da comissão pode entrar no GPS e entender imediatamente "estas são as
atividades sob minha responsabilidade, estas precisam de atenção agora, e é aqui que clico"? E a
presidência pode coordenar sem uma planilha paralela?

**Resposta curta.** Sim, e quase sem nada novo. O GPS **já deriva** cada providência, de quem ela é,
por que espera e para onde levar. Faz isso um Edital por vez, dentro do Centro de Controle (127, 136,
138, 139). O que falta é **ler junto**, para a pessoa, o que já está marcado como SUA em cada Edital.
A área que já faz isso para alguns casos é a faixa "Ações disponíveis para você", da Lista (104). Ela
exclui por custo exatamente o trabalho da comissão depois da publicação.

Medido nos cenários de treinamento, a presidência tem **20 atos seus em 11 Editais**, e a faixa
mostra **zero**.

**O que o estudo corrige na hipótese.** "Atribuir responsáveis por grupo operacional" não é o atalho
que parece. No GPS de hoje:
- sortear, ordenar, cortar e convocar são atos da presidência;
- publicar o resultado e julgar recursos são papéis da unidade;
- toda designação que existe (alocação à Etapa, alocação à conferência, designação para a
  formalização) **concede** a base para o ato.

Uma designação que não concedesse nada poria na tela de João um sorteio que ele não pode fazer.
Uma que concedesse muda a regra de autorização, o que é decisão de governança, e não de UX.

> **Rodada 2 (mesmo dia).** O usuário propôs pôr a visão pessoal em "Minhas Etapas", renomeada
> "Minhas atividades", e não na faixa da Lista. A [avaliação](rodada-2.md) concorda, e acrescenta
> uma razão mais forte que a navegação: o custo.
> - Na Lista, todos os papéis pagariam a derivação. Na página pessoal, paga só quem abre.
> - O recorte das comissões da pessoa custa 2 consultas.
> - Para quem não preside, a página não precisa da derivação nenhuma vez.
>
> Três ajustes à proposta:
> - o resumo da Lista sem número;
> - seções no lugar de contadores e abas;
> - os textos da própria derivação.
>
> A D-1 mudou, e entrou a D-6 (pouso do login institucional). As seções abaixo são da rodada 1, e a
> rodada 2 prevalece onde diverge.

> **Rodada 3.** A [rodada 3](rodada-3.md) confere uma revisão da rodada 2, e os quatro pontos dela
> procedem. Ela também mede a página otimizada:
> - o membro cai de 1697 para 56 consultas;
> - a presidência cai só de 1080 para 873, porque o custo dela é a própria derivação, ~80 consultas
>   por Edital presidido.
>
> Mostra ainda que a página não conflita com a Agenda, e dimensiona o esforço como médio: uma spec,
> sem modelo, migration nem regra nova.

> **Rodada 4: a visão reconsolidada.** A [rodada 4](rodada-4.md) acolhe uma crítica: o estudo trocou
> a pergunta "como o GPS coordena a comissão" por "o que eu posso executar".
>
> A visão passa a ser explícita: **gestão operacional orientada do processo seletivo**, em três
> entregas:
> 1. Minhas atividades;
> 2. organização do trabalho no Centro;
> 3. responsabilidade e acompanhamento por frente, sem conceder permissão.
>
> A D-3(c) deixa de ser recusa e vira a terceira entrega, condicionada a evidência de uso real. A
> rodada lista o que a primeira entrega preserva desde já para não fechar essa porta.

## Entregas

1. [Análise](analise.md): as seções A a G do pedido:
   - A, diagnóstico;
   - B, mapa das atividades;
   - C, alternativas;
   - D, experiência;
   - E, recomendação;
   - F, MVP;
   - G, riscos.
2. [Validação nos cenários C01–C15](validacao/README.md): a derivação real rodada para seis
   identidades, com os achados V-1 a V-8, o script e a saída integral.
3. [Wireframes](wireframes.html), em quatro abas:
   - a presidência ("Seu trabalho");
   - o avaliador;
   - a presidência coordenando ("Quem faz o quê", no Centro);
   - onde a visão mora.

   As abas 1, 2 e 4 foram atualizadas na rodada 2.
4. [Rodada 2](rodada-2.md):
   - "Minhas Etapas" como lugar da visão;
   - as dependências da página;
   - o custo medido por tabela, e três reduções sem regra nova;
   - os ajustes à proposta e as decisões revistas.

## Recomendação

**A derivação que já existe, lida entre Editais, na faixa que já existe.** Isso é a Frente B que a
129 deixou registrada. Três condições:

1. **Uma fonte só.** Uma linha de "Seu trabalho" existe se, e só se, a mesma célula tem a marca SUA no
   Centro daquele Edital. O teste de coerência da 127 passa a valer para as duas.
2. **"Seu" por vínculo, e não por permissão sistêmica.** Sem isso, o Gestor recebe 22 atos de
   condução como seus (V-4).
3. **O mesmo ato agrupa entre Editais.** Sem isso, sete "ordens de lista vazia" escondem a
   convocação (V-3).

**Não fazer:**
- tarefa persistida;
- prazo inventado a partir de datas que significam outra coisa (`ate` é fim de espera: V-5);
- página inicial nova;
- contador na barra;
- designação informativa sem base.

## Decisões que precisam ser tomadas

*Tabela da rodada 1. A [rodada 2](rodada-2.md#6-decisões-revistas) revê a D-1 ("Minhas Etapas"
renomeada, mesmo endereço) e acrescenta a D-6.*

| # | Decisão | Opções | O que o estudo sugere |
|---|---|---|---|
| D-1 | Onde mora a visão pessoal | (a) a faixa da Lista cresce ("Seu trabalho"); (b) Minhas Etapas vira "Meu trabalho"; (c) página nova | **(a)**. Mantém a entrada e a D-001 da 104, e revisita a D-002 da 104 e a D-005 da 127 |
| D-2 | O que a base sistêmica (`comissao:gerir`) põe na lista do Gestor | (a) nada: o Centro continua mostrando; (b) uma linha "você pode intervir em N Editais"; (c) tudo, como hoje no Centro | **(a)** no MVP. (b) se o Gestor real pedir |
| D-3 | Distribuir a condução entre membros ("João fica com o sorteio") | (a) manter a presidência, e distribuir só o que já se distribui (avaliação, conferência, formalização); (b) delegação de condução por grupo, com base, trilha e revogação, numa spec de domínio própria; (c) responsável informativo sem base | **(a)** agora. (b) só depois de operar com uma comissão real, que no início terá 2–3 pessoas acumulando papéis. **(c) não** |
| D-4 | Prazo da comissão | (a) não mostrar prazo, só "espera até" com o significado certo; (b) derivar prazo do cronograma; (c) prazo administrativo declarado | **(a)**. (b) inventaria prazo a partir de data de evento. (c) é regra nova de domínio |
| D-5 | Sequência depois do MVP | "Quem faz o quê" no Centro; Publicador e Julgador na unidade inteira; atos que hoje são só acesso; "parado há N dias" | nesta ordem. O primeiro pede cenários com alocação à conferência e recurso interposto (V-8) |

## O que não foi feito

- Nenhuma linha de código de produção, migration, modelo ou interface foi alterada. Os únicos
  arquivos são os deste diretório.
- Os wireframes são HTML estático, com os textos e números lidos da derivação real. Não são
  protótipos navegáveis sobre o Django, como os do estudo do Centro.
- Não houve validação com operadores reais. O MVP propõe como fazê-la.
- O banco `ps_minhas_atividades` ficou no cluster local para reprodução.
