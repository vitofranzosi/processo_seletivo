# Verificação da 153 (11/11/2026)

## A suíte

`make lint` passou (`ruff check` e `ruff format --check`). `manage.py check` e `makemigrations --check`
também: nenhuma migration.

A suíte rodou contra PostgreSQL, com 4 workers e `worksteal`: **18489 passaram, 24 foram pulados, sem
falha**, em 540s. A worktree tinha só o grupo `dev`, sem o `assistente` e sem o `navegador`, e é daí
que vêm os pulados a mais que os do CLAUDE.md.

Depois da suíte, uma mudança de template entrou: o "a quem pedir" nas advertências da confirmação de
encerrar, em `confirmar.html`. Para ela, rodaram de novo os testes da tela e os guardiões dela, com
1175 passando:

- `interface/test_passagem_ao_setor.py`;
- `interface/test_confirmacao_do_encerramento.py`;
- `interface/test_advertencia_do_encerramento_do_processo.py`;
- `test_gramatica_das_portas.py`;
- `interface/test_acessibilidade.py`.

Os testes anteriores que mudaram, todos por consequência da pendência nova (D-009):

- **Os cenários do relatório** (`tests/fixtures/relatorio.py`) gravam a definição sem documento. Eles
  têm aceite e não tratam da formalização.
- **Os orçamentos de consulta**: o relatório passou de 120 para 128; a confirmação do Edital, de 23 para
  25; a do Processo, de 145 e 142 para 153 e 150. Os números são iguais com 1 e com 10 vezes as
  inscrições.

## No navegador (SC-1950, UX-560)

O banco descartável `ps_demo_153` foi montado com o cenário de treinamento C12 e uma autoridade de
demonstração. Duas convocações tiveram os documentos conferidos e o aceite gravado pelo shell, com os
helpers dos testes: são **duas pessoas aptas**, com a definição vazia e ninguém designado. O que se viu:

1. **Como `treino.presidencia`, na página do Edital.**
   - "Onde estamos" nomeia a conclusão.
   - O mapa marca "1 sua" na Conclusão.
   - "O que fazer agora" lista *Definir os documentos que vão ao setor*, com a razão "2 pessoas aptas
     para formalização; nenhum documento definido para o setor".
   - O link leva a `…/formalizacao#documentos-definidos`.
2. **A fase Conclusão**: o bloco "Disponibilizar ao setor" mostra as três linhas em texto ("Em aberto
   ·") e a frase do limite.
3. **A definição gravada pela tela** (dois documentos, com motivo). Na volta:
   - a linha da definição está "Feito";
   - a providência passa a *Quem administra os acessos da unidade: designar quem recebe os
     documentos*, de outro papel e sem link, com a frase de conceder antes o papel.
4. **Como `demo.gestor`, a confirmação de encerrar**: sob "Continuam depois do encerramento", aparece
   "2 inscrições aptas para formalização ainda sem documentos disponibilizados ao setor (falta designar
   quem recebe). Peça a quem administra os acessos da unidade."
5. **A 375 px**: o bloco cabe na largura (330 px), sem rolagem horizontal.

Não foi verificado no navegador: a exportação pelo setor e o bloco com tudo disponibilizado. O seletor
de demonstração não designa (UX 06 do estudo), e os dois casos estão cobertos por
`test_com_todas_disponibilizadas_o_bloco_diz_o_ultimo_pacote`.
