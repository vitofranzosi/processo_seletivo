# Verificação: Conferência antes de convocar os titulares (140)

## Suíte

`cd backend && make lint check test-pg`, com `DB_NAME=ps_140`, 4 workers, sem o grupo `navegador`.
A primeira rodada deu **17716 passando, 21 pulados e 2 falhas**, as duas de guardiões de inventário
que precisavam conhecer a tela nova: `test_folha_estatica.py` (a folha `grupos/aviso.css` passou a
ser carregada também pela conferência) e `test_telas_de_resultado_e_atos.py` (o rótulo do botão do
gesto mudou por decisão desta spec, FR-4816). Corrigidos os dois inventários, os arquivos passam; a
rodada final está no PR.

## No navegador, com o C10 da `134`

Banco descartável `ps_demo_140`, migrado, com a unidade semeada, uma autoridade fictícia de ensaio e
`carregar_cenarios_de_treinamento --banco ps_demo_140 --cenario C10 --cenario C15 --autoridade …`
(com `CENARIOS_DE_TREINAMENTO=true` e `ARQUIVOS_CANDIDATOS_RAIZ=/tmp/ps-arquivos-140`). Servidor pela
entrada `conferencia-140` do `.claude/launch.json`, na porta 8140, como `treino.presidencia`.

O passo D3 do estudo, repetido: "Conferir e convocar as 3", **sem prazo e sem complemento**.

| Conferido | Resultado |
|---|---|
| O clique abre a conferência, e não o ato | "Confira antes de convocar", em `…/convocacao/titulares` |
| Nada gravado pela conferência | no banco: 0 convocações, 0 comunicações, 0 chaves da operação `convocacao:convocar_titulares` |
| Quem e para que vaga | as 3 pessoas, "para vaga inicial", com a origem da espécie |
| O texto | o fundamento do portal e a mensagem inteira (assunto e corpo), com o link indicado |
| O prazo | "Nenhum vencimento informado. A mensagem dirá que o prazo para atender é o que o Edital publica." |
| Quem fica de fora | Davi (suplente) e "Mais 2 pessoas da fila" |
| 1440 px e 375 px | sem rolagem horizontal; nenhum erro nem violação de CSP no console |
| A confirmação | "3 convocações praticadas num ato só, uma por pessoa. 3 comunicações enviadas."; no banco, 3 e 3 |
| A mensagem enviada | as 3 do terminal do servidor são, linha a linha, a da conferência, exceto o link (SC-1505) |

O C15 foi carregado no mesmo banco e não foi percorrido: o gesto e a conferência são os mesmos, e o
C10 é o cenário do defeito.
