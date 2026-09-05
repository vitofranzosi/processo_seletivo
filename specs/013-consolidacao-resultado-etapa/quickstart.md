# Fase 1 — Como demonstrar e validar

**Feature**: 013 — Consolidação do Resultado da Etapa | **Data**: 2026-09-02

A condição de merge de cada entrega é o **percurso navegado**, não a contagem de testes (princípio
VI). Nesta feature o percurso é curto e a recusa é metade dele: o que a 013 promete é tanto produzir
o Resultado quanto **fechar a porta** por onde a entrada dele mudaria depois.

Duas janelas bastam — quem preside e quem avalia. A terceira, de quem não deveria alcançar nada,
reaparece só na Entrega 4, e por um motivo novo: eliminação passa a ser motivo de 404.

---

## Pré-requisitos

**PostgreSQL local precisa de `LC_ALL`, e a role padrão da máquina não existe no cluster** —
sobrescreva `DB_USER`.

**`TEST_DB_ENGINE=postgresql` é obrigatório.** Sem ela a suíte cai para SQLite **sem avisar**, e
quatro garantias desta feature deixam de ser exercidas: a unicidade `(inscricao, etapa)` sob
concorrência, a trigger append-only do Resultado, a **trigger de coerência** que impede o Resultado
de nascer apontando para Avaliação de outra inscrição, e o bloqueio do Processo herdado de
`comando_de_comissao`, que é inócuo em SQLite e é o que serializa dois lotes.

**Um banco de teste por worktree**, senão duas suítes em paralelo se destroem:

```bash
cd backend && TEST_DB_ENGINE=postgresql LC_ALL=en_US.UTF-8 DB_USER="$(whoami)" DB_NAME=ps013 uv run pytest -q
```

**A interface administrativa exige o seletor de identidade ligado**; sem a variável, `/gestao/`
devolve 503:

```bash
cd backend && INTERFACE_SELETOR_IDENTIDADE=true DB_USER="$(whoami)" uv run python manage.py runserver 8013
```

**Dados**: um Edital publicado com **três** Etapas em ordem — a terceira existe para provar a
transitividade da eliminação —, a primeira declarando **uma** avaliação por inscrição, nota mínima
60, caráter eliminatório; comissão com presidente e um avaliador alocado nas três; e três inscrições
submetidas — Maria, João e Ana.

Para a Entrega 5, um segundo Edital publicado cuja primeira Etapa declare **duas** avaliações.

---

## Entrega 1 — A prontidão aparece no resumo que já existe

**O que se vê**: a organização da Etapa passa a dizer quantas inscrições podem ser consolidadas e
por que as demais não podem, sem tela nova.

1. Distribuir as três inscrições ao avaliador. Concluir a avaliação de Maria (75) e a de Ana (55);
   deixar João sem conclusão.
2. Abrir `editais/<id>/distribuicao/<etapa1>`: o resumo mostra **3 participantes, 2 prontas, 1
   aguardando avaliação, 0 consolidadas**. As contagens fecham: nenhuma inscrição em dois estados.
3. Filtrar por "prontas": exatamente Maria e Ana. Por "aguardando avaliação": exatamente João, com a
   frase, e não a palavra "erro".
4. Conferir que **não existe** segunda página de Resultado com contagem própria (D-004).

**Prova por teste**: unitário sobre a partição (FR-010); integração conferindo que o resumo continua
sendo uma agregação e não um laço; e um teste de `performance` afirmando que o número de consultas
não cresce com o número de inscrições.

---

## Entrega 2 — O Resultado nasce, e é reproduzível

**O que se vê**: uma inscrição pronta vira consequência com origem verificável.

1. Selecionar Maria e consolidar. O resumo passa a **1 consolidada, 1 pronta**.
2. Abrir `.../resultados`: Maria, **75,0000**, `HABILITADA`, com a Avaliação fonte, quem avaliou,
   quem consolidou, quando cada ato ocorreu e sob qual Versão Consolidada.
3. Consolidar Ana: **55,0000**, `ELIMINADA`, e o motivo escrito — "pontuação inferior à nota mínima
   da Etapa (55,0000 < 60,0000)". A causa está no Resultado, não numa nota de rodapé (FR-017).
4. Retificar o Edital mudando algo **fora** da Etapa (a remuneração de um Perfil, por exemplo) e
   remover o avaliador da comissão. Reabrir `.../resultados`: os dois Resultados continuam íntegros,
   com as mesmas autorias e a mesma regra (invariante 7).

**Prova por teste**: a tabela-verdade de T-003 em teste unitário puro, incluindo nota exatamente
igual à mínima e Etapa eliminatória sem nota mínima; integração para a proveniência; um teste que
tenta `UPDATE` direto no Resultado e recebe a recusa da trigger append-only; e um que tenta inserir
Resultado apontando para Avaliação de outra inscrição e recebe a recusa da trigger de coerência.

---

## Entrega 3 — O lote, e a repetição que não duplica

**O que se vê**: mil e duzentas inscrições viram consequência num ato, e reenviar não cria nada.

1. Semear um Edital com muitas inscrições prontas (o comando de demonstração serve). Selecionar até
   mil e consolidar: o desfecho declara **N consolidadas, M recusadas**, com as recusas agrupadas
   por causa — não uma linha por inscrição. Mil é o teto de SC-002, e é o mesmo número em spec,
   plano, contrato e aqui.
2. Reenviar **a mesma chave de idempotência com o mesmo conteúdo**: a resposta é o desfecho
   original, e a trilha não ganha evento nenhum (SC-006).
3. Reenviar **a mesma chave com conteúdo diferente**: conflito, e nada é criado.
4. Consolidar de novo, com chave nova, um lote que inclua Maria: ela é recusada como "já possui
   Resultado nesta Etapa" — recusa nomeada, e não sucesso silencioso (FR-022).
5. Abrir a trilha da Etapa: **um evento por Resultado criado**, cada um dizendo a qual inscrição se
   refere, pelo protocolo.

**Prova por teste**: aceitação do lote com prontas, pendentes e já consolidadas na mesma submissão;
integração para as três formas de repetição; e um teste de concorrência com duas transações
consolidando a mesma inscrição, afirmando exatamente um Resultado e um desfecho explícito para a
perdedora.

---

## Entrega 4 — A porta fechada, e a que continua aberta

**O que se vê**: consolidar torna a entrada da decisão intocável — sem impedir que o sistema registre
o que descobriu.

1. Tentar reabrir a Avaliação de Maria, com motivo e revisão corretos: **recusado**, 409, com a
   frase que nomeia a inscrição e a Etapa. Conferir que a Avaliação continua `CONCLUIDA`, com a mesma
   revisão, e que a trilha não ganhou evento de reabertura (FR-030).
2. Conferir que a recusa **não mostra a pontuação** (FR-033).
3. Registrar impedimento da mesma pessoa alcançando Maria **e** João. O impedimento **é criado** e
   **todas** as Atribuições alcançadas são inativadas, inclusive a de Maria, que fundamenta
   Resultado (FR-031).
4. **A prova que justifica a decisão**: abrir a Mesa como a pessoa impedida e tentar alcançar a
   inscrição de Maria e seus documentos. Nada é alcançado — 404 uniforme. Se a Atribuição tivesse
   sido preservada para proteger a proveniência, este passo passaria, e é exatamente esse buraco que
   a revisão do plano encontrou (SC-009).
5. Abrir o Resultado de Maria: pontuação e consequência **intactas**, e a consulta agora exibe a
   contestação superveniente — quem consulta precisa saber que a origem foi contestada depois
   (FR-032).
6. Reabrir uma avaliação **não** consolidada: continua funcionando exatamente como na 012. Esta é a
   não regressão que mais importa.

---

## Entrega 5 — A progressão, e o gate que a torna segura

**O que se vê**: quem foi eliminado não aparece em nenhuma Etapa seguinte; e quem nunca poderá ser
consolidado não trava a Etapa seguinte de ninguém.

**A ordem importa nesta entrega**, e o passo 1 tem de vir antes de qualquer consolidação — depois
dela, a exigência de habilitação está vigente e a própria spec proíbe distribuir João.

1. **Antes de consolidar a Etapa 1**: abrir a Etapa 2. As três inscrições estão disponíveis, como na
   012. Distribuir João ao avaliador — é a Atribuição antecipada que o passo 5 vai usar.
2. Consolidar a Etapa 1: Maria `HABILITADA`, Ana `ELIMINADA`, João sem conclusão e portanto sem
   Resultado. Reabrir a Etapa 2: só **Maria** compõe participantes; Ana aparece entre "eliminadas
   anteriormente" e João entre "aguardando Etapa anterior".
3. Tentar distribuir Ana na Etapa 2: recusado como **erro do pedido**, e não como recusa de linha.
   Trocar o identificador de Maria pelo de Ana na URL da Mesa: **404 uniforme**, sem revelar dado
   (SC-005).
4. **A transitividade**: sem consolidar nada na Etapa 2, abrir a **Etapa 3**. Ana continua fora —
   eliminada na Etapa 1 vale para todas as posteriores. Maria e João aparecem, porque a exigência de
   habilitação da Etapa 2 está dormente. Este passo é o que distingue as duas regras de D-003, e é o
   cenário que uma redação anterior deixava passar.
5. Abrir a Mesa como o avaliador que recebeu João no passo 1: ele não alcança a inscrição na Etapa
   2, e a navegação de **próxima pendente** não a oferece. O registro antecipado permanece para
   investigação e volta a autorizar se João for habilitado.
6. **O gate**: abrir o segundo Edital, cuja Etapa 1 prevê duas avaliações. A Etapa 1 informa que a
   regra de combinação não foi publicada e não oferece consolidação — e a **Etapa 2 continua
   distribuível com todas as submetidas**. É esta demonstração que prova que a 013 não quebrou o que
   a 012 entregou (D-003, FR-004).

---

## O percurso completo, para o princípio VI

Executado inteiramente pela interface administrativa, sem banco, sem shell e sem chamada manual:

> a presidência abre a Etapa → confere prontidão e as causas dos 27 que não estão prontos →
> consolida os prontos num ato → consulta um Resultado com sua origem → tenta reabrir a fonte e é
> recusada → abre a Etapa seguinte e encontra apenas os habilitados, e a Etapa depois dela sem os
> eliminados de nenhuma das anteriores.

Nenhuma nota é digitada duas vezes, nenhuma planilha entra no caminho, e nenhuma tela afirma
colocação, aprovação final ou direito a vaga (FR-045).

---

## Entrega 6 — o desfecho de quem não foi avaliado (D-1)

*Acrescentada em 04/09/2026, junto da extensão. Ela é curta porque o ato é curto — e é a única do
documento que **não** passa pela Mesa em momento nenhum.*

1. Na Etapa, a presidência clica **Registrar ocorrência**. A tela lista quem participa da Etapa e
   ainda não tem Resultado — inclusive quem não tem avaliação concluída nenhuma, que é justamente
   quem esta tela existe para resolver.
2. Ela marca a inscrição de quem faltou, escreve *"não compareceu à Entrevista (item 6.3 do
   Edital)"* e envia. **Nada é gravado ainda**: a tela devolve a confirmação, nomeando quem será
   eliminado e sob qual motivo.
3. Ela confirma. O Resultado nasce **eliminado, sem Avaliação, sem pontuação e sem sentido**, com a
   versão vigente do Edital como norma e o motivo como causa.
4. Em **Resultados**, a linha aparece com a coluna *Origem* dizendo `Ocorrência`, a conclusão dita
   como "não avaliada" e a coluna de quem avaliou dizendo, por extenso, que ninguém avaliou.
5. Na Etapa **seguinte**, aquela inscrição não está — pelo mesmo caminho de quem foi eliminado por
   nota.

O passo 2 é o que prova o Princípio VI junto com o 1: sem eles, a capacidade existiria no domínio e
nenhuma interface a alcançaria. E o passo 3 é o que a distingue da consolidação: aqui a presidência
**informa** o motivo, porque a constatação é o conteúdo do ato, e não um cálculo a confirmar.

**O caso que vale exercitar depois**, porque é o que a decisão existe para permitir: repetir a
Entrega 6 numa Etapa cuja consolidação está impedida — decisória e não eliminatória, ou de leitura
múltipla. A ocorrência é registrada assim mesmo, e é isso que I-1 afirma.

---

## Cobertura declarada, e não presumida

O percurso acima demonstra os requisitos observáveis pelo canal do ator — a participação, a
prontidão, o Resultado com proveniência, o lote com desfecho, as duas portas e a progressão. Os
demais são invariantes de banco, de comando e de não regressão: unicidade sob concorrência,
imutabilidade por trigger e privilégio, forma do desfecho preservado, ausência de verificação por
linha nas listagens. A cobertura deles é responsabilidade de `tasks.md`, e a rastreabilidade fecha em
`traceability.md` ao final da implementação, como a 011 e a 012 fizeram.

Afirmar aqui que "cada FR tem cenário no quickstart" seria falso, e é o tipo de afirmação que a
revisão do plano da 012 teve de corrigir.
