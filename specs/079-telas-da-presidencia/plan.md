# Implementation Plan: As telas da presidência da comissão, terceiro incremento

**Branch**: `claude/gallant-kepler-eabdb2` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

## Summary

Só apresentação, em quatro templates. A trilha sobe ao cabeçalho de contexto na Comissão, na
conferência da inclusão, na Alocação por Etapa e na Distribuição, pelo bloco que a `077` criou; na
Distribuição, a faixa dos lugares da Etapa sobe para logo abaixo do título; na Comissão, os membros
ganham uma seção com título e quantidade, e a comissão vazia perde o filtro e ganha o estado vazio
que leva à inclusão; na Alocação, o botão da matriz passa a dizer "Salvar alocação". Nenhuma
migration, nenhuma permissão, nenhum endereço, nenhuma view, nenhuma regra na folha comum.

**Base.** A `078` está no PR 293, ainda aberto, e mexe na mesma folha comum. Esta feature parte da
branch dela (`e781dfb3`) e não toca a folha comum; antes do PR, ela se atualiza com a `main` depois
do merge da `078`, ou o PR diz que depende do 293.

## Technical Context

Django 5 sobre PostgreSQL; nada de servidor muda. Templates apenas. A linha de base visual é o
inventário no estado `depois-da-078`
(`doc/inventario-visual-da-gestao-2026-10-16/depois-da-078/resultados.json`, barra expandida, e
`depois-da-078/recolhida/resultados.json`), reproduzido em 17/10 sobre `e781dfb3` sem diferença
nenhuma — largura, altura, título e `h1`, variante a variante —, no banco `ps_inventario_telas`. O
teto da Distribuição no cenário de escala está em 95 144 caracteres (95 610 bytes) antes. A decisão
de cada mudança e as alternativas descartadas estão em [research.md](research.md). Não há entidade
nem contrato externo: `data-model.md` e `contracts/` não se aplicam.

## Constitution Check

- **Negar por padrão (III, IV)**: nenhuma condição de template muda de sentido; cada região continua
  saindo das mesmas variáveis da view, e cada link da trilha leva a uma tela que já condiciona o
  acesso. O filtro da Comissão vazia deixa de vir por uma condição sobre a contagem que a view já
  entrega, e não sobre permissão.
- **Linguagem ubíqua (I)**: os rótulos da trilha são os que as telas já usavam. "Salvar alocação"
  alinha o botão ao nome da tela e à mensagem de sucesso, pela decisão de vocabulário da própria tela
  (Alocação põe pessoas em Etapas; Distribuição põe inscrições em avaliadores).
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`. A arquitetura do manual, que registra o rótulo antigo como
  divergência, é atualizada.
- **Simplicidade (V)**: blocos de template e regiões que trocam de lugar. Nenhum script, nenhuma
  classe nova, nenhuma regra nova na folha.
- **Completude de jornada (VI)**: o percurso da presidência é provado no navegador a 1280 e a
  375 px, só pelo teclado, e o inventário inteiro é refeito nos dois estados da barra e comparado
  campo a campo.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/templates/interface/comissao.html` | o bloco `caminho_do_contexto` com a trilha; a seção "Membros (N)" com o filtro e a lista; sem membro, sem filtro e com o estado vazio que leva a "Adicionar membro" (R-001, R-003) |
| `comissao_confirmar.html` | o bloco com a trilha (R-001) |
| `alocacoes.html` | o bloco com a trilha; "Salvar alocação" (R-001, R-004) |
| `distribuicao.html` | o bloco com a trilha; a faixa dos lugares da Etapa logo depois do título e das mensagens do último envio (R-001, R-002) |
| `doc/manual/00-arquitetura-do-manual.md` | o rótulo atual da Alocação (R-004) |
| `specs/078-telas-de-quem-elabora/spec.md` e `rastreabilidade.md` | `FR-1769` anotada como emendada pela `079` |
| `doc/inventario-visual-da-gestao-2026-10-16.md` e `depois-da-079/` | o inventário refeito nos dois estados da barra, a comparação e as capturas das telas que mudaram |

## Testes que mudam, e por quê

Ver o R-005 da pesquisa. Testes novos em `tests/interface/test_telas_da_presidencia.py`: a trilha no
cabeçalho, e só uma, nas quatro telas; a Alocação com a barra no topo e a trilha; a faixa da
Distribuição antes da ficha, com os mesmos links, e as ações no lugar; a seção dos membros e o estado
vazio da Comissão; o rótulo da Alocação.

## Verificação

`make lint check test-pg` com `DB_NAME` próprio; o teto da Distribuição medido de novo; o percurso do
[quickstart](quickstart.md) no navegador, a 1280 e a 375 px, só pelo teclado; o inventário refeito
com `BARRA=expandida` e `BARRA=recolhida`, comparado por `comparar.py` e campo a campo com
`depois-da-078/`.
