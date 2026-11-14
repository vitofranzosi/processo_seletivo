# Teste com a equipe — roteiro do facilitador

*13/11/2026 · `main` em `a4b5446e`. As tarefas vêm do protocolo da seção E da auditoria de autonomia
operacional (commit `c7232947`, na branch `origin/claude/operation-vs-task-execution-5e2d5c`, ainda
fora da `main`). Cada uma foi percorrida na tela, num banco isolado com os dezessete cenários de
treinamento e na combinação de papéis descrita abaixo. O gabarito cita o que a tela disse.*

## Para que serve

Uma pergunta só: **uma pessoa da equipe, sem o guia e sem ajuda, descobre o que fazer, por que, e
quando terminou?**

Até agora, ninguém de fora do desenvolvimento foi observado usando o GPS.
- O estudo do Centro de Controle (09/11) mediu a tela com Playwright e inspeção, e registra: *"Não
  houve teste com operadores … A validação humana segue em aberto, como a de toda a série
  126–133."*
- A auditoria de 13/11 diz o mesmo: *"Nenhuma pessoa da equipe foi observada."*

Este teste mede o sistema **como está hoje**, sem comparar com protótipo. O resultado diz qual das
três intervenções da auditoria vem primeiro, ou se nenhuma é necessária.

**O que ele não mede:** velocidade, satisfação, portal do candidato, celular, sorteio e retificação.

## Os arquivos

| Arquivo | Para quem | Na mesa? |
|---|---|---|
| este roteiro | quem conduz | não |
| [cartoes.md](cartoes.md) | a pessoa testada — um cartão por folha | **sim**, um de cada vez |
| [gabarito.md](gabarito.md) | quem conduz e quem anota | **nunca** |
| [ficha.md](ficha.md) | quem anota — uma ficha por pessoa, mais a planilha final | não |

## Quem participa

**Participantes: duas ou três pessoas da equipe de seleção.**

- O ideal é que não tenham participado do desenvolvimento nem feito os exercícios do
  [guia da equipe](../cenarios-de-treinamento/guia-da-equipe.md).
- Numa equipe de duas ou três pessoas, talvez ninguém atenda a isso. Nesse caso, teste com quem
  houver e marque a familiaridade na ficha. O resultado continua valendo, mas é **otimista**: quem já
  viu as telas acerta mais do que alguém que chega sem tê-las visto.

**Quem conduz** entrega os cartões, controla o tempo e não explica o sistema.

**Quem anota** preenche a ficha.
- Se houver uma pessoa só para os dois papéis, grave a tela e a voz (com consentimento) e anote
  depois, pela gravação.
- Se puder, não deixe a condução com quem construiu o GPS. Quem construiu ajuda sem perceber: aponta
  com os olhos, respira aliviado quando a pessoa acerta. Se não houver alternativa, a regra de
  intervenção vale em dobro.

**Uma pessoa por vez**, em horários que não se cruzem e sem conversa entre as sessões. Quem já fez
não pode contar como foi para quem ainda vai fazer.

## Duração

**60 minutos por pessoa:** 5 de abertura, cerca de 45 de tarefas e 10 de conversa final. Os tetos de
cada tarefa estão no gabarito.

## Ambiente

- Homologação com os cenários carregados, ou um banco local isolado (veja *Preparação*).
- Navegador de computador, janela com 1440 px de largura ou mais, sem extensões.
- Uma aba aberta no início. O link **Abrir** de um documento abre outra aba, e isso é esperado.

### A identidade: a mesma para todos

Todos entram como **`treino.presidencia`, com os papéis Gestor e Publicador**, pelas opções
avançadas da página de demonstração. Três razões:

1. **É a acumulação mais provável numa equipe de duas ou três pessoas**: presidir, gerir e
   publicar. Julgar recursos fica de fora de propósito, porque quem julga não pode ter consolidado nem
   publicado o que é atacado.
2. **As seis tarefas são de condução do certame**, e só `treino.presidencia` preside as comissões dos
   cenários.
3. **Uma combinação única torna as pessoas comparáveis.**

A auditoria sugeria a combinação real de cada pessoa. Se a equipe já sabe quem terá o quê, pode
trocar, mas a comparação entre pessoas fica mais fraca, e a ficha precisa registrar a combinação.

**Quem conduz faz a entrada antes de a pessoa sentar.** Entrar não é tarefa:

1. **Área de gestão** → **Acessar ambiente de demonstração**.
2. Abra **Opções avançadas de demonstração**.
3. Em **Nome na auditoria**, escreva `treino.presidencia`.
4. Marque **Gestor** e **Publicador**.
5. Clique em **Entrar com esta combinação**.
6. Confira:
   - no rodapé da barra lateral, o nome `treino.presidencia` e, abaixo dele, *"Gestor, Publicador"*;
   - na página inicial, *"Você integra a comissão de 13 Processos"*.

## Preparação

### Uma vez, antes da primeira pessoa

1. **Carregue e verifique os cenários**, como no
   [manual de operação](../cenarios-de-treinamento/manual-de-operacao.md). Num banco local
   descartável, a sequência usada para este roteiro foi:

   ```bash
   cd backend
   export LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development \
     DB_NAME=ps_roteiro_equipe DB_USER=$USER DB_RUNTIME_USER=$USER \
     ARQUIVOS_CANDIDATOS_RAIZ=/caminho/fora/do/repositorio \
     CENARIOS_DE_TREINAMENTO=true SORTEIO_FONTE_DE_DEMONSTRACAO=true
   createdb ps_roteiro_equipe
   uv run python manage.py migrate
   uv run python manage.py semear_unidades
   uv run python manage.py seed_demo
   uv run python manage.py carregar_cenarios_de_treinamento --banco ps_roteiro_equipe
   ```

   - Sem `ARQUIVOS_CANDIDATOS_RAIZ`, só o C01 carrega. Os outros dezesseis dão `ERRO` com
     `ImproperlyConfigured`, e nada deles é gravado.
   - O `seed_demo` vem antes porque o gerador só assina com uma autoridade já usada.
   - O servidor local é a entrada `roteiro-equipe` do `.claude/launch.json`, na porta 8197.

2. **Ensaio.** Quem conduz faz as seis tarefas sozinho, com o gabarito ao lado e cronometrando, e
   depois restaura os cenários. Serve para duas coisas:
   - conferir que as telas ainda dizem o que o gabarito diz, porque a `main` anda todo dia;
   - não descobrir no meio da sessão onde fica cada coisa.

### Antes de cada pessoa (5 minutos)

As tarefas 3, 4 e 5 gravam atos, e a 2 e a 6 podem gravar. **Restaure sempre os cinco**, mesmo que a
pessoa anterior não tenha agido neles:

```bash
for c in C09 C11 C12 C15 C16; do
  uv run python manage.py restaurar_cenario_de_treinamento --cenario $c --banco <banco> --confirmar $c
done
uv run python manage.py verificar_cenarios_de_treinamento
```

Os cinco levaram 3 segundos, e a verificação deve listar os dezessete como `INTACTO`.

**O que muda depois de restaurar:**
- **O código do Edital.** O `SIM09` passa a `SIM09R2`, depois `SIM09R3`, e o anterior vai para
  *Cancelados*. Os cartões já avisam disso.
- **As datas.** Os prazos recomeçam da restauração, e por isso o gabarito dá as datas como
  distância da carga, e não como dia do mês.

**Depois de restaurar:**
- faça a entrada com a combinação e pare na página **Processos Seletivos**;
- feche as outras abas;
- tire o guia da equipe da sala;
- se houver consentimento, comece a gravação.

## A sessão

### Abertura (leia como está escrito)

> Obrigado por vir. Não estamos testando você: estamos testando o sistema. Se algo não ficar claro, a
> falha é dele, e é exatamente isso que precisamos ver.
>
> Vou te dar seis tarefas, uma de cada vez, num papel. Peço que você pense em voz alta: diga o que
> está procurando, o que espera encontrar e o que achou estranho.
>
> Eu não vou responder perguntas sobre o sistema. Não é falta de educação: na operação de verdade,
> ninguém vai estar do seu lado. Se travar, diga. Se ficar muito tempo parado, eu ajudo, e isso também
> é informação para nós.
>
> Os dados são fictícios, e nada do que você fizer atinge ninguém. Você pode parar quando quiser.
>
> Você entrou como presidente das comissões dos Editais de treinamento e também como Gestor e
> Publicador da unidade, como deve acontecer na operação real.

Se for gravar, pergunte antes e registre a resposta na ficha:

> Posso gravar a tela e a sua voz? A gravação fica só com a equipe do projeto e é apagada depois da
> análise.

### Durante cada tarefa

1. Entregue o cartão e peça que a pessoa o leia em voz alta. Comece o cronômetro.
2. **Frases permitidas, sempre as mesmas:**
   - "O que você está pensando?"
   - "O que você esperava ver aqui?"
   - "Continue falando."
   - "O que você faria agora?"
   - "Me diga quando achar que terminou."
3. **Proibido:**
   - apontar ou dizer o nome de uma tela;
   - dizer se está certo, dizer "quase" ou "olhe ali em cima";
   - reagir quando a pessoa acerta.

   A pergunta sobre o sistema volta como pergunta: "O que você acha?"
4. **A escada de ajuda**, que é o que se registra:

   | Nível | O que aconteceu |
   |---|---|
   | 0 | nenhuma ajuda |
   | 1 | a pessoa pediu confirmação ("é aqui, né?"), recebeu a pergunta de volta e seguiu sozinha |
   | 2 | depois de **2 minutos** de impasse, quem conduz deu a pista da tarefa, escrita no gabarito, palavra por palavra |
   | 3 | quem conduz mostrou o caminho ou fez |

   A pista do nível 2 é fixa por tarefa. É ela que torna duas pessoas comparáveis.
5. **Estourou o teto da tarefa:** "Vamos parar aqui. Se você continuasse, o que faria?" Registre como
   abandono e anote a resposta.
6. **No fim de cada tarefa**, a pergunta fixa: **"De 1 a 5, quanto você confia que fez certo?"** A
   confiança alta junto com a tarefa errada é o achado mais grave do teste: é o caso em que ninguém
   pergunta nada a ninguém.
7. **Não corrija nada entre as tarefas.** Um erro numa tarefa não atrapalha as outras, porque cada uma
   é num Edital diferente.

### Conversa final (10 minutos)

Faça as quatro perguntas, nesta ordem:

1. Em que momento você se sentiu mais perdida?
2. Teve alguma palavra que você não entendeu, ou que entendeu de um jeito e depois viu que era outro?
3. Se começasse a usar o GPS amanhã, sozinha, o que te preocuparia?
4. Em que parte você confiaria no que a tela disse, e em que parte conferiria com alguém?

**Só depois de tudo registrado**, e se a pessoa quiser, mostre o que ela não encontrou.

## Depois das sessões

### Pontuação

**Uma tarefa conta como autônoma** quando há, ao mesmo tempo:
- ajuda 0 ou 1;
- nenhum erro de decisão;
- o acerto que o gabarito descreve.

**O GPS conduz** quando ao menos duas de três pessoas são autônomas em cinco das seis tarefas. Com
duas pessoas, as duas precisam ser. O critério é o da auditoria, mantido sem ajuste para que o
resultado não se negocie depois.

**Duas regras particulares:**
- **Tarefa 5.** Se a pessoa erra só o *destino* da vaga da cota, a tarefa conta como **capacidade
  ausente**, e não como falha de orientação. Esse destino ainda não existe no GPS: as specs `155`
  (incompleta) e `158` (bloqueada) são de onde ele viria.
- **Falsa confiança.** Confiança 4 ou 5 numa tarefa não autônoma vai para uma linha própria da
  planilha.

### Do resultado à decisão

| Onde a pessoa falhou | Aponta para |
|---|---|
| T1 — chegada | **Intervenção 1**: uma só resposta para "o que é meu agora" |
| T2 — entrar num Edital | **Intervenção 2**: peso e momento em "O que fazer agora" |
| T3 — passar o trabalho adiante | **Intervenção 3**: a passagem de mão dita por extenso |
| T4, na conferência ou no desfecho | a tela do ato, e não a orientação |
| T4, em "o que fica esperando" | **Intervenção 2** |
| T5 | **Intervenção 2**, ou capacidade ausente (regra acima) |
| T6 | **Intervenção 3**, e a 2 se a pessoa achou que acabou |
| termo que travou | a lista do vocabulário, que a auditoria deixou fora das três |

**Qual vem primeiro.** A intervenção da tarefa com mais pessoas não autônomas. Em empate, a que não
reabre decisão escrita:
- a **3** não conflita com nada;
- a **2** esbarra na D-007 da `160` e na frase "o GPS não escolhe a ordem";
- a **1** reabre a D-004 e o FR-6862 da `160`.

Essa escolha é sua. **Se todas passarem**, não há intervenção a fazer nesta frente: registre o
resultado e encerre.

### Onde registrar

**O resultado** vai em `resultado.md`, nesta pasta, com:
- a planilha da [ficha](ficha.md);
- as frases literais;
- os termos que travaram.

**Os dados das pessoas:**
- as pessoas aparecem como P1, P2 e P3, sem nome;
- as gravações se apagam depois da análise;
- as fichas em papel, depois de transcritas.

## Limites

- **Duas ou três pessoas não dão estatística.** Dão os lugares onde quem vai operar trava, e é para
  isso que o teste serve.
- **A ordem das tarefas é fixa**, e o que a pessoa aprende na 1 ajuda na 2. Aceito: a operação real
  também é cumulativa.
- **A lista de cota vazia está em 9 dos 13 Editais da presidência.** Isso é artifício dos cenários na
  frequência, mas não no tipo: num Edital pequeno, cota sem inscrito acontece.
- **O gabarito é a tela de 13/11, na `a4b5446e`.** Se a `main` mudar antes do teste, o ensaio é o que
  acusa a diferença.

## O que a preparação encontrou

São registros para a governança, e não escopo deste teste. Nenhum foi corrigido.

1. **A página inicial ainda contradiz *Minhas atividades*.** Na mesma combinação, a página inicial
   diz *"Nenhum ato de Edital ou de Retificação, recurso ou avaliação aguarda você agora."*, e
   *Minhas atividades* diz *"Para fazer agora · 22 atos em 13 Editais"*. É a causa 1 da auditoria,
   sem mudança.
2. **A ordem de lista vazia não é só formalidade.** A auditoria esperava, na tarefa 6, que a pessoa
   dissesse "a ordem vazia é formalidade". No SIM15 ela é o primeiro elo da vaga da cota. Emitida, a
   tela diz *"Próximo nesta lista: Publicar o resultado"*. O Centro passa a mostrar o corte da PPP
   esperando o prazo de recurso. Só depois disso a vaga da cota entra na apuração. O gabarito da
   tarefa 6 foi corrigido por isso, e o argumento da proposta de 13/11, que pedia para rebaixar essa
   ação a "operação separada", perde força.
3. **Depois de distribuir a análise documental, a tela diz só *"6 atribuídas."*** Não diz que agora
   são os avaliadores, nem que a presidência volta para consolidar. O Centro mostra *"Com outros
   papéis — Os avaliadores alocados: avaliar 6 inscrições distribuídas"*, sem o nome de ninguém. É a
   causa 4 da auditoria, sem mudança.
4. ***Minhas atividades* omite *"Definir os documentos que vão ao setor"*.** Depois dos três aceites
   no SIM12, o Centro lista essa ação como *"Sua Conclusão"*, e *Minhas atividades* conta 1 ato
   nesse Edital — a ordem vazia. Na mesma tela, a fase Conclusão diz *"Ainda não começou"* com
   *"Agora: 1 sua"*. É mais um caso da causa 1 e da causa 3.
5. **O "Entenda o ato" do corte manda esperar um prazo que o SIM09 não tem.** Nele, *"Com o prazo de
   recurso aberto, a recomendação é esperar"* aparece num Edital cujo marco não admite recurso. O
   texto é o mesmo em todo Edital. Pode causar hesitação na tarefa 3, e a ficha tem campo para isso.
6. **O guia da equipe ainda inverte o C09.** Ele manda concluir a "Análise documental" antes do
   corte, e o GPS só distribui a análise depois do corte. A auditoria já registrava isso. O guia fica
   fora da sala justamente por isso.
7. **O guia diz "4 vagas" no C15.** A tela reparte 3 na ampla e 1 na PPP, e a da PPP não aparece em
   número nenhum até a cadeia do item 2.
8. **O fim do Edital tem três definições no SIM16.**
   - O Centro diz *"O Edital se encerra quando nenhuma lista tiver ato em aberto"*.
   - A tela **Encerrar** bloqueia só pelo prazo de recurso (*"Antes de encerrar, resolva 1
     pendência"*). Ela põe a exportação ao setor entre o que *"Continuam depois do encerramento"*.
   - A mesma tela não menciona a ordem da lista PPP, que o Centro apresenta como *"Sua próxima
     ação"*.

   Pode ser deliberado: o encerramento do A-11 (#362) admite o que continua depois dele. Não
   conferi a regra. Mas a pessoa que pergunta "acabou?" recebe três respostas.
