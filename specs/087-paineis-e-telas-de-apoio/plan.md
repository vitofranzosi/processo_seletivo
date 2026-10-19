# Implementation Plan: Os painéis e as telas de apoio da gestão, nono incremento

**Branch**: `claude/funny-cohen-c98a85` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

## Summary

Só apresentação, em oito templates. A trilha sobe ao cabeçalho de contexto, pelo bloco que a `077`
criou, na Visão Geral e nas Autoridades da unidade (a seção, como página atual), na Supervisão e na
conferência dos atos do Processo (pelo Processo), nas Respostas do assistente de dúvidas, no
Assistente do Edital e na conferência dos atos do Edital (pelo Processo e pelo Edital), e em Criar
Processo Seletivo. "Perguntar" ganha o desenho de ação principal no Assistente. Nenhuma migration,
nenhuma permissão, nenhum endereço, nenhuma view, nenhuma consulta nova, nenhuma regra na folha
comum, nenhuma classe nova, nenhum número novo nos painéis.

## Technical Context

Django 5 sobre PostgreSQL; nada de servidor muda. Templates apenas. As views já entregam o Processo
(Supervisão, conferência do Processo) ou o Edital com o Processo carregado junto (`obter_edital` faz
`select_related("processo")`; as duas telas do assistente o passam como `processo`), de modo que o
código do Processo na trilha não custa consulta. A linha de base visual é o inventário refeito em
18/10 sobre `cf6d7372`, no banco `ps_inventario_087` (cópia do `ps_inventario_080`), nos dois estados
da barra, guardado em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-087/antes/`. Ele é igual
ao `depois-da-080/` em todas as medidas, variante a variante. A decisão de cada mudança e as
alternativas descartadas estão em [research.md](research.md). Não há entidade nem contrato externo:
`data-model.md` e `contracts/` não se aplicam.

## Constitution Check

- **Negar por padrão (III, IV)**: nenhuma condição de template muda de sentido; cada região continua
  saindo das mesmas variáveis da view, e cada link da trilha leva a uma tela que já condiciona o
  acesso.
- **Linguagem ubíqua (I)**: os rótulos da trilha são os que as telas já usavam como página atual, e
  o dos painéis de seção é o da barra (D-002).
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`.
- **Simplicidade (V)**: blocos de template. Nenhum script, nenhuma classe nova, nenhuma regra nova na
  folha.
- **Completude de jornada (VI)**: o percurso é provado no navegador a 1280 e a 375 px, pelo teclado,
  e o inventário inteiro é refeito nos dois estados da barra e comparado campo a campo.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/templates/interface/visao_geral.html`, `autoridades.html` | o bloco `caminho_do_contexto` com a seção como página atual (R-001) |
| `supervisao.html`, `processo_confirmar.html` | o bloco com a trilha pelo Processo; sai a trilha do conteúdo (R-001) |
| `duvidas.html`, `confirmar.html` | o bloco com a trilha pelo Processo e pelo Edital; sai a do conteúdo (R-001, R-003) |
| `assistente.html` | o mesmo, e "Perguntar" como `botao` (R-001, R-002) |
| `processo_criar.html` | o bloco com *Processos Seletivos › Criar*; sai a do conteúdo (R-001) |
| `tests/interface/test_shell_da_gestao.py` | o guardião da Visão Geral lê a trilha, e não o texto da `076` (R-004) |
| `doc/inventario-visual-da-gestao-2026-10-16.md` e `depois-da-087/` | o inventário de antes e o de depois nos dois estados da barra, a comparação e as capturas das telas do escopo |

## Testes que mudam, e por quê

Ver o R-004 da pesquisa. Testes novos em `tests/interface/test_paineis_e_telas_de_apoio.py`.

## Verificação

`make lint check test-pg` com `DB_NAME=ps_087`; o percurso do [quickstart](quickstart.md) no
navegador, a 1280 e a 375 px, pelo teclado; o inventário refeito com `BARRA=expandida` e
`BARRA=recolhida`, comparado por `comparar.py` e por `medidas.py` com o de antes; a contagem do
fechamento (R-005) refeita depois de trazer a `main`.
