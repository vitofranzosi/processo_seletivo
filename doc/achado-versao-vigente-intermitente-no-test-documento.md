# Achado — o Edital recém-publicado sem versão vigente, uma vez, em `test_documento`

Encontrado em 29/09/2026, na verificação da P2 da `051` (#231), com `make test-pg DB_NAME=ps_051p2`.

> **Não é defeito confirmado, e não vira escopo por estar escrito aqui.** O que se registra é uma
> falha que aconteceu uma vez, o que ela exclui e o que ela não exclui, e como confirmá-la se voltar.
> Priorizar é do usuário.

## O que se observou

A primeira rodada da suíte fechou em `8849 passed, 11 skipped, 1 error`. O erro foi no **preparo** de
um caso só:

```text
ERROR tests/integration/avaliacoes/test_documento.py::test_a_ordem_e_sugerida_e_nao_imposta

processo_seletivo/publicacoes/application/selectors.py:36: DomainError
  ('no_effective_version', 'Não havia conteúdo vigente para este Edital no instante consultado.', 404)
The above exception was the direct cause of the following exception:
processo_seletivo/comissoes/domain/etapas.py:38: DomainError
  ('edital_sem_versao_vigente', 'Este Edital ainda não foi publicado: suas Etapas não são alocáveis.', 409)
```

O caminho é o da fixture `cenario` do arquivo: `edital_com_documentos` publica o Edital 12/2026, e
`alocar_em` aloca um membro da comissão numa Etapa dele. A alocação lê as Etapas da versão vigente
(`comissoes/domain/etapas.etapas_vigentes` → `publicacoes/application/selectors.effective_version`), e
a leitura não achou versão nenhuma.

**Não se repetiu.** O arquivo inteiro passou isolado (20 casos), o caso sozinho passou três vezes, e a
segunda rodada da suíte inteira, **sobre o mesmo commit e sem mudança nenhuma**, fechou em
`8850 passed, 11 skipped`. Os outros 15 casos do mesmo arquivo, que usam a mesma fixture, passaram na
rodada em que este falhou.

## O que a falha exclui

- **O Edital não publicado.** `levar_a_publicacao` exige `201` na publicação (`assert
  published.status_code == 201`), e `publish_edital` cria a `VersaoConsolidada` na mesma transação da
  Publicação. Se a fixture voltou, a versão existe.
- **O código da P2.** Nada no caminho — `publicacoes/application/publish_edital`, `selectors`,
  `comissoes` — foi tocado pelo #231, e o caso não passa pela Retificação.
- **Um relógio falso vazado de outro teste.** Os arquivos que simulam o tempo, pelo que a busca
  por `time_machine`, `freezegun` e `patch` de `timezone.now` encontra
  (`tests/interface/test_convocacao_em_fluxo.py`, `tests/portal/…`, `tests/integration/portal/…`,
  `tests/integration/divulgacao/…`, `tests/integration/convocacao/…`) rodam **depois** de
  `tests/integration/avaliacoes/` na ordem da coleta; a falha foi a 4% da suíte.

## O que ela não exclui — a hipótese

`effective_version` escolhe a versão com `valid_from <= timezone.now()`. E `publish_edital` grava
`valid_from = now`, o `timezone.now()` do início do comando (`shared/application/commands.command_context`).
Os dois instantes vêm do **relógio de parede** do processo, milissegundos um do outro.

Com a versão existindo, a única forma de a consulta não a achar é o segundo `timezone.now()` sair
**menor** que o primeiro — o relógio de parede recuando entre a publicação e a alocação, o que o macOS
faz quando sincroniza a hora (NTP). A consulta ao `log show` da janela da rodada não mostrou ajuste,
mas também não mostrou evento nenhum do `timed`: a ausência não prova nada.

**É hipótese, e não causa confirmada.**

## Por que pode valer uma decisão

Se a hipótese estiver certa, o efeito não é só de teste. Um recuo do relógio logo depois de publicar
faz o Edital publicado parecer **não vigente** por alguns milissegundos para toda leitura que usa
`effective_version` sem `at` — alocação de comissão, inscrição, página pública. A janela é mínima, e
nenhuma leitura grava o que leu; o risco prático parece baixo. O que se registra é que a vigência
depende de dois relógios de parede concordarem na ordem.

As saídas possíveis, sem recomendação:

- **Não fazer nada.** A janela é de milissegundos, e um servidor costuma corrigir a hora aos
  poucos, sem recuo — o que não foi verificado para o ambiente de produção.
- **Tolerância na comparação**, ou `valid_from` truncado ao segundo. Muda a regra de vigência de
  todos os Editais, inclusive a vigência futura de Retificação.
- **Relógio monotônico nos testes**: congelar o tempo na fixture de publicação. Esconderia o efeito
  em vez de decidir sobre ele.

## Como confirmar, se voltar

1. Anotar o horário da falha e rodar
   `log show --start "<início>" --end "<fim>" --predicate 'process == "timed"'`.
2. O banco não guarda a prova: o caso roda numa transação desfeita no fim. Para capturá-la, é
   preciso instrumentar a leitura — por exemplo, fazer `conteudo_vigente` anexar à recusa o
   `valid_from` da versão mais recente do Edital e o `timezone.now()` que ele comparou.
3. Se `valid_from` for posterior ao instante da consulta, a hipótese se confirma.
