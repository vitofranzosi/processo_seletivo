# Verificação: Convocar do cadastro de reserva, na ordem publicada

**Feature**: [spec.md](spec.md) · **Tarefas**: [tasks.md](tasks.md)

## Ponto de partida

Medido em 21/10/2026 sobre `1671a749` (a `main` em `717fc057` mais os artefatos desta spec), contra
PostgreSQL com `DB_NAME=ps_097` e 4 workers:

```text
tests/unit/ocupacao tests/integration/ocupacao tests/integration/convocacao
tests/interface/test_ocupacao.py tests/interface/test_convocacao_em_fluxo.py
tests/unit/editais/test_reserva_convocada_fora.py tests/test_vocabulario_da_ocupacao.py
tests/test_dependencia_da_convocacao.py

413 passed in 27.71s
```

## Ordem dos testes

**A US1 não teve a fase vermelha que as tarefas pedem.** O módulo `ocupacao/application/acrescimo.py`
foi escrito antes de os testes de T014 e T015 rodarem pela primeira vez, e eles já rodaram verdes.
Os da Phase 2 e o de convocação (T016) falharam primeiro pelas razões esperadas — `ImportError` e,
em T016, a recusa `fundamento_obrigatorio` da convocação individual, que levou o teste a conferir o
fundamento pela prévia do gesto. Registrado por honestidade: a cobertura é a mesma, mas não houve
prova de que cada teste reprovaria sem o código.

## A suíte inteira

Medida em 21/10/2026 sobre `2cf2e15d`, contra PostgreSQL com `DB_NAME=ps_097`, 4 workers e
`worksteal`, **sem** o grupo `assistente`:

```text
12677 passed, 13 skipped in 436.70s (0:07:16)
```

Os 13 pulados são os doze de antes (sem o grupo) e **um novo, esperado**: a varredura de vocabulário
da composição passou a ler `ocupacao_acrescimo.html` e pula o par *conferência × «geração»*, porque a
tela não usa o termo. Os pulados foram agrupados por arquivo e motivo com `-rs`; nenhuma outra linha
mudou. `make lint` e `make check` (com o superusuário, porque a worktree não tem `.env`) passaram.

## Demonstração

Pela interface, em 21/10/2026, num banco novo `ps_097_demo`, servido por uma entrada temporária do
`.claude/launch.json` (porta 8097), desfeita no fim — o arquivo é versionado, e a entrada dependeria
de um banco que só existe nesta máquina. A preparação — Edital publicado com Perfil de 0 vagas, cadastro
de reserva sem limite e só a linha geral, marco por sorteio com corte de alvo fixo 20 que não governa
Etapa, oito inscritos fictícios, relação, ocorrência, sorteio e corte — foi feita pelos commands da
aplicação, com os helpers dos testes, por um roteiro no scratchpad da sessão. Daí em diante, só a
tela, entrando como **maria, presidência da comissão** — o que prova também a `D-004`: quem preside
acrescenta sem capacidade nova.

1. A ocupação mostrou *0 Publicadas*, *Ocupação ainda não apurada* e o formulário do acréscimo, com a
   orientação de não nomear pessoas do outro Edital.
2. Acréscimo de 1 vaga, origem *"Edital Multicampi nº 20/2026, Campus Vitória"*. A conferência disse
   *0 publicadas, 0 acrescidas, 1 efetiva depois*, *"Amanda Lisboa, na 1ª posição da ordem"* e que a
   apuração seguinte seria emitida pelo ato, em nome de quem confirmava.
3. Confirmado: *"Vaga acrescida: 1 vaga. A apuração seguinte foi emitida por este ato"*; o recorte
   passou a *0 · 1 acrescida · 1 efetiva · 1 ocupada · 0 a ocupar*, com a lista do ato.
4. Na convocação, *"Convocar a 1"* com Amanda Lisboa; o fundamento derivado cita a apuração e não a
   origem. Praticado: a convocação nasceu com o prazo à espera do registro da publicação, como o
   7.2 do 69/2026 manda.
5. Desfazer a vaga de Amanda: recusado, *"Há 1 pessoa(s) já chamada(s) para as vagas deste recorte
   [...] Registre antes o desfecho de quem não vai ocupá-la."*
6. Segunda vaga, do Campus Serra, e o desfazimento dela antes de qualquer chamada, com motivo: aceito;
   as duas linhas ficaram na lista, e o recorte voltou a 1 efetiva.

Nenhum erro no console, nenhuma violação de política de conteúdo. **O que a demonstração não
percorreu**: a Revisão antes de publicar (o Edital foi publicado pelo roteiro; o aviso novo está
provado pelo teste de interface `test_a_revisao_diz_como_a_reserva_e_convocada`) e o não atendimento
pela tela (provado em `test_reserva.py` com a desistência).

**Corrigido depois da demonstração**: a lista *"Quem a ordem alcança"* da conferência mostra a janela
inteira de titulares depois do ato — inclusive quem já foi chamado —, e não só quem a vaga nova
alcança. Era verdadeira e podia ser lida como "estas pessoas serão chamadas"; ganhou a nota que diz o
que ela é.
