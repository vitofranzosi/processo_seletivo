# Verificação: cenários de treinamento e homologação

**Spec**: [spec.md](spec.md) · 08/11/2026, worktree `gps-training-staging-scenarios-bc947c`,
sobre a `main` em `86cd0ee0`.

## Testes da feature

`tests/unit/treinamento/` e `tests/integration/treinamento/`, contra PostgreSQL: **54 casos**.

| O que se prova | Onde | Requisitos |
|---|---|---|
| As três barreiras, para os quatro comandos, sem gravar nada | `test_ambiente.py` | FR-4601, FR-4602, FR-4604, FR-4605 |
| Pré-visualização com destino e plano; sorteio recusado sem a fonte | `test_ambiente.py` | FR-4604, FR-4643 |
| Sem autoridade vigente, recusa sem criar; nunca usada, só com `--autoridade` | `test_ambiente.py`, `test_carga_e_restauracao.py` | FR-4615, FR-4616 |
| Carga sobre o banco do `seed_demo` sem alterar **nenhuma** linha, em **todas** as tabelas | `test_carga_e_restauracao.py` | SC-1451, FR-4611 |
| A segunda carga não grava nenhuma linha | idem | SC-1452, FR-4611 |
| Sorteio feito **pela tela** no C07; o C04 continua intacto; a carga não desfaz o exercício | idem | SC-1453, FR-4617 |
| Restaurar sem `--confirmar` (ou com outro código) não muda nada; com ele, só mudam o Processo, o Edital e o manifesto da rodada anterior; a rodada nova sorteia de novo | idem | SC-1454, FR-4620 a FR-4626 |
| Falha no meio de um cenário não deixa rastro e não impede os outros | idem | FR-4612 |
| Processo com código reservado e sem manifesto: relatado, intocado, restauração recusada | idem | FR-4614 |
| Propriedade que não se comprova bloqueia a restauração | idem | FR-4613, FR-4622 |
| Os quinze juntos, cada um no seu Processo | idem | FR-4650, FR-4651 |
| A próxima ação de cada um dos quinze, executada pelo ator da ficha; e recusada a quem a ficha não nomeia | `test_proxima_acao.py` | SC-1455, FR-4655, FR-4642 |
| CPF válido iniciado por 000, nomes e e-mails fictícios, PDF válido e marcado, atores sem permissão além do papel | `tests/unit/treinamento/` | FR-4630 a FR-4633, FR-4642 |
| A chave nasce desligada e produção recusa subir com ela | `tests/test_configuracao_producao.py` | FR-4601 |

O C04 confere a ordem emitida: os candidatos 01 e 02, empatados no total, saem em 1º e 2º pelo
desempate da prova; 03 e 04 dividem o 3º lugar; 08, eliminado na prova, fica fora da ordem.

## Achados da própria verificação

1. **A carga congelava uma autoridade da unidade.** O instantâneo linha a linha acusou a autoridade
   da suíte alterada: a primeira publicação com uma autoridade grava `usada_em`, e a partir dali o
   cadastro dela é imutável. Corrigido pela FR-4616.
2. **Os atores do gerador tomavam as sugestões da página de acesso.** Visto no navegador:
   "Elaborador como treino.elaboracao". `treino.` passou a ser sujeito fora da equipe, como `cand:`.
3. **Conforme exige abertura registrada pela tela** — o C12 deixou de nascer com item conforme
   (D-007).
4. **O mesmo arquivo reenviado não conta como entrega nova** — o roteiro de correção do C11 usa
   um arquivo diferente.

## No navegador

Banco `ps_demo_134`, com o `seed_demo` no papel de dados preexistentes, e os quinze cenários
carregados pelo comando (entrada `cenarios-134` do `.claude/launch.json`):

- a carga dos quinze levou **8 segundos**; a segunda carga, `MANTER` em todos;
- a página de acesso lista `treino.presidencia` e `treino.avaliacao1` em **Comissões**, com os
  Processos de cada uma;
- o Edital `SIM04/2026` mostra uma só providência: **SUA — Emitir a ordem**;
- o Edital `SIM07/2026` mostra **SUA — Observar a extração**; na tela do sorteio, a fonte é a
  **Fonte de demonstração** e o concurso 80701 diz "cenário de treinamento, sem valor legal";
  **Observar a ocorrência** e **Realizar o sorteio** funcionaram, e a tela passou a mostrar
  "Sorteio realizado … por treino.presidencia" com semente e manifesto;
- a verificação acusou o C07 como `EXERCITADO` (ato de ordenação, 10 posições, sorteio) e o C04
  como `INTACTO`; a restauração criou `SIM-TREINAMENTO-007-R2`, e a rodada 1 foi para
  **Cancelados**;
- os documentos do convocado 02 do C11 mostram o diploma **Pendente** e a residência **A
  apresentar**; o PDF fictício é servido íntegro, com a marca de treinamento.

- depois das correções, a página de acesso voltou a sugerir a equipe ("Elaborador como
  ana.elaboradora"), e o Edital de sorteio restaurado (`SIM07R3`) deixou de declarar as duas Etapas
  do molde que nenhum ato usa. Continua a providência de distribuir a "Análise de títulos", que é a
  Etapa enumerada pelo marco de sorteio do molde do `seed_demo`; o sorteio não depende dela, e o
  guia a anota como observação para o exercício.

## Suíte completa

`make test-pg` com `DB_NAME=ps_treino_wt`, 4 workers, antes das três correções finais:
**17 417 passando, 20 pulados, 1 falha, em 758 s**. A falha é
`tests/performance/test_ocupacao.py::test_a_apuracao_cabe_no_dobro_do_tempo_da_emissao_da_ordem`,
o teste de tempo que o `AGENTS.md` registra como oscilante sob carga — a suíte rodou ao lado do
servidor de demonstração e da carga dos cenários. Isolado, passou três vezes em três; esta feature
não toca a ocupação.

Depois das correções finais (sugestões da página de acesso, travessão do PDF, Etapas do Edital de
sorteio): `ruff check`, `ruff format --check`, `manage.py check` e `makemigrations --check` limpos,
e os 108 casos afetados — a feature, a entrada da gestão, o `seed_demo`, as citações, o README e a
configuração de produção — passando.

## Pendente

- **SC-1456 (humana):** uma pessoa da comissão percorrer um cenário só com o guia.
- **A carga na homologação compartilhada** é do administrador, depois do backup e do ensaio do
  [manual](../../doc/cenarios-de-treinamento/manual-de-operacao.md). Nada foi carregado lá.
