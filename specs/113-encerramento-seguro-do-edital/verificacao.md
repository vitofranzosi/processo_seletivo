# Verificação: Encerramento seguro do Edital (113)

## Linha de base (T001), 01/11/2026

Sobre `b0ff1bac` (a `f60a129d` com a `main` em `4d9e97a9`), PostgreSQL local, 4 workers:
`test_relatorio.py`, `unit/interface/test_relatorio_do_edital.py`, `test_relatorio_consolidado.py`,
`test_retificacao_de_edital_encerrado.py`, `test_us7_finalizacao.py`, `test_finalizacao_api.py`,
`test_finalizacao_concorrente.py` — **84 passando**, em 24 s.

## Depois de mover as leituras (T005)

Os mesmos arquivos da linha de base, mais `test_tres_listas_publicadas.py`, `test_sinais.py`,
`unit/interface/test_relatorio_consolidado.py` e `test_citacoes_de_requisito.py`: **160 passando**,
nenhuma falha nova.

## Suíte inteira (T029), 01/11/2026

`make lint check test-pg` sobre a árvore da implementação, PostgreSQL local, 4 workers:
**14 508 passando, 15 pulados, nenhuma falha**, em 561 s. Lint e formato verdes; `manage.py check`
sem problemas; nenhuma migration.

A primeira rodada (535 s) deu duas falhas, ambas da própria mudança:

- `test_fluxo.py::test_confirmacao_diz_o_que_o_ato_provoca_antes_de_praticar` prendia a frase
  "conclusão regular", que a FR-3542 tira de propósito — a asserção passou a pedir a consequência
  nova;
- `test_gramatica_das_portas.py::test_toda_tela_que_manda_pedir_usa_a_formulacao_canonica` não lia o
  destinatário numa variável do template ("Peça a {{ item… }}"). A frase inteira passou para
  `interface/encerramento.py`, na forma canônica da `033` ("Peça a quem…", "Peça à…").

Os testes que encerravam Edital num estado que a `113` impede (R-008) passaram a usar
`tests/fixtures/encerramento.py:encerrar_antes_da_113`, que roda o comando inteiro sem a conferência
nova: os seis do A-09 (Retificação homologada), quatro da `047` em `test_desfecho_publico.py`, um de
`test_prazo_recursal_publico.py`, um de `test_consultas_da_vitrine.py`, um de
`test_agora_e_proximo.py` e um de `test_fonte.py` (Agenda).

## A trava do Processo é o que prova a concorrência (SC-1070)

Com a linha que trava o Processo trocada por `pass`, numa cópia descartável,
`test_recurso_confirmado_antes_do_encerramento_o_impede` falhou com *"DID NOT RAISE"*: o
encerramento concluiu sem ver o recurso confirmado pela outra transação. Com a trava, recusa.

## Orçamento de consultas (SC-1072)

`performance/test_confirmacao_do_encerramento.py`: **23 consultas** com 38 e com 362 inscrições.

## Tempo da confirmação, isolado (SC-1072, T030)

`encerramento.da_confirmacao` no Edital do cenário da `099` em escala 10 (**362 inscrições**), período
correndo, cinco medições depois de uma de aquecimento, um worker só: **0,007 · 0,007 · 0,007 ·
0,006 · 0,006 s**. O teto da SC-1072 é 1 s.

## Pela aplicação (T030), 01/11/2026

Banco isolado `ps_113_demo` (`migrate`, `semear_unidades`, `seed_demo`), entrada temporária no
`.claude/launch.json` (desfeita), `gustavo.gestor`. Capturas em [capturas/](capturas/):

- **Encerrar o 01/2026** (período com término em 21/11): impedimento do período com "Peça a quem
  elabora Retificações." — o gestor não retifica —, sem "Confirmar"; à parte, os dois resultados não
  divulgados; consequências novas. → `encerrar-com-periodo-em-curso.jpg`
- **Encerrar o 51/2026**: impedimento do prazo recursal contra “Classificação final”, até 06/11; à
  parte, a convocação aguardando resposta e o definitivo não publicado. → `encerrar-com-prazo-recursal-e-convocacao.jpg`
- **Cancelar o 01/2026**: tudo em "Serão atingidos pelo cancelamento", com "Confirmar: Cancelar". →
  `cancelar-o-que-sera-atingido.jpg`
- **A 375 px**: sem rolagem horizontal (largura 375, conteúdo 375). → `encerrar-a-375px.jpg`

Nenhum erro no console.

**Dois defeitos achados aqui, e corrigidos.** Na primeira captura do cancelamento a frase do
período dizia "Encerrar antes disso não é conclusão regular… ou cancele o Edital" — na tela de
cancelar —, e a da Retificação homologada dizia "Publique-a ou devolva-a". O cancelamento passou a
ter frase própria, que diz o efeito, e os itens dele não levam caminho. E a mesma tela misturava
aspas (« » nas frases da `113`, “ ” nas da `099`); ficaram as da `099`. O contrato foi atualizado.

## Suíte inteira sobre a árvore final

Depois das correções das frases do cancelamento e das aspas: `make lint check test-pg`, 4 workers —
**14 508 passando, 15 pulados, nenhuma falha**, em 544 s, saída 0.

## Revisão de código antes do PR (01/11/2026)

Seis achados; cinco corrigidos:

- a confirmação calculava e mostrava as situações do Edital a quem não tem a permissão do ato
  (a tela já dizia "Você não pode praticar este ato") — agora não calcula nem mostra
  (`test_quem_nao_pode_encerrar_nao_ve_as_contagens`);
- no POST aceito ela era calculada antes do ato e descartada no redirect — agora só no GET e na
  recusa;
- a marca da Retificação na Lista de Processos não dizia que ela está parada — agora diz "não pode
  mais prosseguir" (`test_a_marca_da_lista_tambem_diz_que_esta_parada`);
- um `if True:` esquecido no teste da SC-1069 e um literal `"EM_REVISAO"` no lugar do enum.

**Pulado, e registrado:** os atos da Retificação travam Retificação, Edital e Processo num único
`FOR UPDATE` sem `OF`, cuja ordem segue o plano da consulta; o encerramento trava Processo e depois
Edital. Se a Retificação pegar o Edital antes do Processo no instante em que o encerramento segura o
Processo, o PostgreSQL aborta uma das duas com *deadlock* — a janela é a de uma linha só, e os dois
testes de concorrência do A-09 passam. Fechá-la pede que `_retificacao` trave o Processo
explicitamente antes, o que é mudar o código do A-09; fica para decisão.

Suíte inteira depois das correções: **14 510 passando, 15 pulados, nenhuma falha**, em 560 s.
