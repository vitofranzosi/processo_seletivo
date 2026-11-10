# Achados funcionais — separados do escopo do estudo

O pedido manda separar a inconsistência de negócio da melhoria de experiência. Estes cinco achados
tocam a derivação, a regra ou o cenário, e **nenhum foi corrigido nem decidido aqui**. Cada um traz a
evidência, o que se sabe e o que não se sabe, e uma proposta de investigação.

> **Não viram escopo por estarem escritos aqui.** Governança é do usuário.

> **Triagem de F-1 a F-3 em 10/11** ([07](07-triagem-f1-f3.md)):
> - **F-1a** é intencional (102, D-006);
> - **F-1b** é particularidade da fonte de demonstração e não ocorre com a Loteria Federal;
> - **F-2** é falha confirmada na derivação;
> - **F-3** é intencional (127, D-019).
>
> O texto abaixo é o de antes da triagem.

## F-1 — No sorteio, a semente observada antes da segunda lista condena a segunda lista em silêncio, e o Centro continua oferecendo o sorteio dela

**Jornada A, C06 rodada 1** (`a04`–`a11`).

**O que aconteceu, na ordem.**
1. A presidência congelou a ampla.
2. O retorno da tela apontou "Próximo nesta lista: **Observar a extração**". O Centro listou "Obter a
   semente pública" antes de "Fixar os participantes · PPP", e disse "Todas já podem ser feitas … o GPS
   não escolhe a ordem entre elas".
3. Ela observou a ocorrência. Depois congelou a PPP, e o congelamento foi aceito sem aviso nenhum.
4. O sorteio da ampla saiu. O da PPP foi recusado: "a fonte situa a extração … antes disso. Para
   sortear: (1) retifique o Edital…; (2) publique a relação nova…; (3) observe a nova ocorrência".
5. Depois da recusa, a tela do sorteio continuou mostrando "Realizar o sorteio" na PPP, sem o
   diagnóstico da relação condenada (102). E o Centro continuou oferecendo **"Realizar o sorteio · PPP"
   como ação sua**.

**O que o código diz.**
- O aviso prévio "congelar agora condena o sorteio" (102, FR-2659) vem de
  `sorteios/application/previa.py::_congelar_agora_inviavel`. Ele usa o instante **declarado**
  (`occurrenceAt`) e `viabilidade.limite_previsto`, que só prevê para fonte que **publica só a data**
  (D-006 da 102): "para fonte que publica a hora não há previsão a fazer aqui".
- A fonte de demonstração publica a hora. Por isso o aviso não dispara nela, nem antes nem **depois**
  da observação — quando o instante já é conhecido ("Aconteceu não antes de 10/11/2026 05:16").
- A Loteria Federal publica só a data. **Em produção, com ela, o aviso deve disparar**: congelar no
  dia da extração, ou depois, já é acusado antes do clique. Não foi verificado no navegador, porque
  nenhum cenário usa a fonte real.

**Por que importa mesmo assim.**
- A `134` existe para treinar a equipe, e o C06 ensina exatamente esta ordem. No treinamento, o GPS
  deixa a pessoa cair na armadilha que o guia manda evitar.
- O Centro oferecer um ato que a tela sempre recusará é independente da fonte: a derivação da 127 não
  consulta a viabilidade da relação ao marcar "Realizar o sorteio" como *Pendente*.

**Proposta de investigação** (sem decidir a D-5):
1. Com a Loteria Federal, num banco de teste: observar e depois congelar a segunda lista. O aviso da
   102 aparece? E o diagnóstico da relação?
2. Para fonte que publica a hora, depois da observação: usar o instante **observado** no aviso e no
   diagnóstico, como já se usa na recusa?
3. Na derivação: uma relação que o diagnóstico da 102 condena deve ficar *Impedida*, com a razão, em
   vez de *Pendente*?

Relação com a **D-5**: a D-5 pergunta se o GPS deve impedir, confirmar em duas fases ou só alertar a
observação antes de congelar todas as relações. O F-1 é anterior a ela: mesmo o alerta que já existe
(102) não cobre a fonte do treinamento, e a derivação não sabe da condenação.

## F-2 — Depois do recurso que reabilita, o Centro oferece a ordem sucessora antes da avaliação que falta

**Jornada C, C08** (`c09`, `c10`).

**O que aconteceu.** O recurso do candidato 08 foi deferido (Prova objetiva de 5,0 para 6,0). O Centro
da presidência passou a mostrar, como paralelas, "Distribuir 1 inscrição sem avaliador suficiente —
Análise de títulos" e "Classificar a lista · no GPS: emitir a ordem sucessora", com "o GPS não escolhe
a ordem entre elas". A prévia da ordem sucessora mostra o reabilitado **"Sem posição — Sem pontuação
nas Etapas enumeradas: Análise de títulos"**.

**Consequência, se seguido.** Uma ordem sucessora emitida agora sairia sem o reabilitado. Depois da
avaliação dos títulos, precisaria ser sucedida de novo, com motivo, e cada sucessão é um ato imutável
na trilha.

**Proposta de investigação.** Na derivação (`andamento.py`), a ordem sucessora de uma lista em que um
participante reingressou deveria ficar *Depois* enquanto as Etapas enumeradas pelo marco não tiverem o
Resultado dele? Conferir com o achado [reabilitado antes do marco](../achado-reabilitado-antes-do-marco-nao-alcanca-o-corte.md),
que trata de um caso vizinho.

## F-3 — O resultado de um marco por sorteio pode ser publicado com a Etapa enumerada pelo marco sem nenhuma consolidação

**Jornada A, C06 rodada 2** (`a16`, `a17`).

O marco do sorteio do C06 enumera a "Análise de títulos". Com 0 de 10 consolidadas, o Publicador
recebeu "Publicar o resultado" como próxima ação, e publicou. O guia da `134` diz que o **sorteio** não
depende da Etapa; não diz se o **resultado** depende.

**Proposta de investigação.** O que a Etapa enumerada significa num marco por sorteio: requisito do
resultado, ou só da progressão? Se for do resultado, a publicação deveria esperar. Se não for, o Centro
e a tela poderiam dizer que ela não segura o resultado, como já dizem do sorteio ("Paralela ao sorteio").

## F-4 — A convocação é oferecida, sem aviso, com o prazo recursal do resultado aberto

**Jornada D, C10, C12, C15** (`d01`, `d08`).

Nos três cenários, o Centro oferece "Convocar N titulares" ao lado de "Publicar o resultado definitivo
— aguarda até 15/11 (prazo recursal aberto)". A tela do **corte** recomenda esperar o fim do prazo
("um recurso deferido tornaria o corte obsoleto"); a da **convocação** não diz nada parecido, e um
recurso deferido depois da convocação muda quem deveria ter sido chamado.

**Proposta de investigação.**
1. O estado dos cenários (corte e apuração emitidos antes do fim do prazo) é o do certame real, ou
   artefato do gerador da `134`?
2. Se for real: a convocação deveria levar a mesma recomendação do corte?

## F-5 — "Pedir a faixa seguinte" é oferecido quando não há ninguém depois da faixa

**Jornada D, C15** (`d09`).

Com 3 inscritos, 1 inabilitado e 4 vagas, a ocupação oferece "Pedir a faixa seguinte com este déficit".
Não há classificado além da faixa. Não foi praticado.

**Proposta de investigação.** Praticar num banco descartável. Se o gesto produzir uma faixa vazia, a
tela deveria dizer que não há a quem chamar, como a convocação já diz quando a fila acaba.
