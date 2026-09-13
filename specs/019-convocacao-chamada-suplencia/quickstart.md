# Guia de validação — `019` Convocação, Chamada e Suplência

**O que este guia prova:** que o ciclo do 77/2026 fecha pela interface, sem shell e sem banco — e
que a desistência de uma titular move o número em **exatamente um** — o defeito medido na §1.0 da
[spec](spec.md).

Este é guia de validação, não de implementação: o passo a passo do código está em `tasks.md`.

## Pré-requisitos

```bash
cd backend && make preparar
```

O provisionamento tem de imprimir `0 de N` na primeira passada e `N de N` na segunda, com `N` maior
que 26 — as tabelas novas desta feature entram na conta. Se o primeiro número não vier `0`, a
segunda passada não rodou.

Variáveis: `INTERFACE_SELETOR_IDENTIDADE=true` (sem ela `/gestao/` devolve 503) e
`PORTAL_IDENTIDADE_DEMO=true` para o Cenário 6. Banco próprio por worktree. Na execução nativa, o
código de acesso do portal é impresso no terminal do `runserver`; no compose, chega em
<http://localhost:8025>.

```bash
cd backend && make runserver
```

**O `seed_demo` não produz este certame.** O Edital precisa ser montado pela tela — quadro por
modalidade, regra de corte com alvo derivado do quadro e excedente de suplentes, e a forma de
comunicar declarada (`callForm`). Os cenários 3 e 5 exigem marco de **sorteio**, como a `016` já
registrou.

## Cenário 1 — O ciclo do 77/2026 (`SC-085`)

1. Componha e publique um Edital com 40 vagas de ampla concorrência, alvo derivado do quadro e 30
   suplentes; emita a ordem e o corte.
2. Conclua a Análise documental de 67 participantes como `HABILITADA` e consolide.
3. Emita a apuração da `016`. **Esperado:** `40 / 40 / 40 / 0`.
4. Convoque as 40 titulares e comunique.
5. Registre **desistência expressa** de uma delas.
6. Emita a apuração de novo. **Esperado:** `40 / 40 / 39 / 1` — e é aqui que o defeito da §1.0
   reprovaria, dizendo `40 / 0`.
7. Convoque a suplente da posição 41, comunique e registre **aceite**.
8. Emita a apuração. **Esperado:** `40 / 40 / 40 / 0`.

**O que provar junto:** entre os passos 5 e 6 a apuração anterior aparece **obsoleta**, com a causa
nomeada; e em nenhum momento a tela afirma número que ninguém emitiu.

## Cenário 2 — Nada é promovido sem ato (`SC-094`)

Repita até o passo 5 e **não convoque ninguém**. A apuração seguinte tem de continuar dizendo 39 —
por mais que existam 26 suplentes habilitados esperando. Se o número voltar a 40 sozinho, a
cardinalidade voltou.

## Cenário 3 — A suplência não atravessa recorte (`SC-086`)

Em certame de **sorteio** com cotas, registre desistência de uma titular de vaga reservada. A
chamada oferecida tem de ser a próxima **daquela** lista, e nunca a da ampla. É o item 8.8 *in fine*
do 28/2026.

## Cenário 4 — O prazo, e o que o sistema não afirma

1. Convoque alguém informando vencimento e **falhe o envio** (backend de e-mail indisponível).
   **Esperado:** estado *"convocado, prazo não iniciado"*; o ato permanece registrado.
2. Informe vencimento **anterior** ao envio. **Esperado:** recusa
   `vencimento_anterior_ao_envio`.
3. Com o envio bem-sucedido, deixe o vencimento decorrer. **Esperado:** a tela mostra o vencimento
   decorrido e **não** produz desfecho; dar por não atendida continua sendo ato de quem conduz.
4. Em toda a tela, procure *"recebido em"*, *"lido em"* e *"entregue em"*. **Esperado:** nenhuma
   ocorrência — só *"enviado em"*.

## Cenário 5 — A regularização sucede o Resultado (`D-008`)

Com uma documentação **indeferida** e vaga sobrando, convoque para regularizar, registre a
regularização e confira:

- o Resultado indeferido continua existindo, **sucedido** e não alterado;
- o sucessor cita o desfecho como fonte jurídica, e não uma decisão de recurso;
- a apuração seguinte conta essa pessoa como ocupante — **sem** reabrir a ordem.

## Cenário 6 — O candidato vê a chamada (`SC-091`)

Entre no portal com a identidade convocada. A tela tem de mostrar a chamada, o que fazer e o prazo,
sem depender de e-mail; e distinguir *"não há convocação"* de *"você não foi chamado"*.

## Cenário 7 — A imutabilidade, pelo shell

Tente `UPDATE` e `DELETE` nas tabelas novas com a role de runtime. **Esperado:** recusa por
**gatilho e** por privilégio ausente — duas camadas independentes. É sobre o banco, e não sobre a
jornada.

## Verificação final

```bash
cd backend && make lint check test-pg
```

`test-pg`, e não `test`: no modo padrão a suíte cai para SQLite, e os casos que dependem de gatilho
e de `select_for_update` falham em vez de serem pulados.

**O que tem de estar verde além da suíte:** a varredura de vocabulário nos dois sentidos — a `016`
continua sem falar de convocação, e esta feature não afirma contagem de ocupação —, a medição da
`SC-090`, e a revisão escrita da `FR-084` da `010` se houver mensagem individual.
