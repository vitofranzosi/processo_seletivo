# Implementation Plan: A limpeza dos achados da etapa 4

**Branch**: `claude/limpeza-achados-090-a308bc` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

## Summary

Quatro correções pequenas, cada uma com teste. A marca "irreversível" ganha `id`, e o link do ato
irreversível, `aria-describedby`, nos detalhes do Processo, do Edital e da Retificação. A porta das
consultas da Etapa devolve se quem lê gere a comissão — o que ela já calcula —, e a trilha de
Resultados, Trilha da avaliação e Conclusões preservadas mostra a Alocação e a Etapa como texto para
quem não as abre. A regra comum `.salvar` ganha `flex-wrap`. O link "Avisar candidatos" dos Resultados
divulgados diz a porta no endereço, e a prévia volta, pela trilha e por "Cancelar", aos Resultados
divulgados. Nenhuma migration, nenhuma permissão, nenhum endereço novo, nenhuma mensagem de domínio.

## Technical Context

Django 5 sobre PostgreSQL. A implementação parte da `main` com a `089` (PR 306): a folha comum mora em
`interface/static/interface/gestao.css`, e os guardiões a leem por `tests/interface/folha.py`. A linha
de base visual é o inventário refeito sobre essa `main`, nos dois estados da barra, num banco de
inventário próprio, guardado em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-090/antes/`. O
roteiro ganha uma variante, a prévia aberta pelos Resultados divulgados (`aviso-do-resultado-pelo-marco`),
capturada também no "antes" — onde o parâmetro ainda não significa nada e a trilha é a dos Avisos. A
decisão de cada mudança e as alternativas descartadas estão em [research.md](research.md). Não há
entidade nem contrato externo: `data-model.md` e `contracts/` não se aplicam.

## Constitution Check

- **Negar por padrão (III, IV)**: nenhuma porta muda. A trilha deixa de oferecer link para porta que
  recusaria, e a decisão sai da mesma pergunta que as portas de destino fazem (R-002). A porta da
  prévia dita pelo endereço não concede nada: só escolhe o caminho de volta, e é ignorada para quem
  não abre o destino (R-004).
- **Linguagem ubíqua (I)**: os rótulos da trilha e dos atos não mudam.
- **Imutabilidade (II)**: a marca diz, também a quem não vê, que o ato não se corrige; nada no ato
  muda.
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`; as FRs contrariadas da `080` e da `086` anotadas como
  emendadas (`FR-2072`).
- **Simplicidade (V)**: nenhuma classe nova, nenhum parcial novo; um atributo, uma propriedade de
  folha, um parâmetro de endereço.
- **Completude de jornada (VI)**: as telas tocadas no navegador, a 1280 e a 375 px, com quem preside e
  com quem só audita; o inventário inteiro refeito nos dois estados da barra.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/templates/interface/processo_detalhe.html`, `_acao_do_edital.html`, `retificacao_detalhe.html` | `id="irreversivel-<chave>"` na marca e `aria-describedby` no link do ato irreversível (R-001) |
| `interface/views.py` (`_etapa_para_auditar`, `_pode_auditar_a_etapa` e as três views) | a porta devolve `pode_gerir_a_comissao`, calculado uma vez; as views o entregam ao template (R-002) |
| `interface/templates/interface/resultados.html`, `conclusoes.html`, `auditoria.html` (ramo da avaliação) | Alocação por Etapa e Etapa como link com `pode_gerir_a_comissao`, texto sem ele (R-002) |
| `interface/static/interface/gestao.css` | `flex-wrap:wrap` em `.salvar` (R-003) |
| `interface/templates/interface/publicacoes_do_marco.html` | `de=marco` no link "Avisar candidatos" (R-004) |
| `interface/avisos.py` (`aviso_do_resultado`) | com `de=marco` e quem lê abre os Resultados divulgados: `voltar`, `de` e `pode_ver_a_classificacao` (R-004) |
| `interface/templates/interface/aviso_previa.html` | `de` nos dois formulários; o ramo dos Resultados divulgados na trilha (R-004) |
| `specs/080-…/spec.md`, `specs/086-…/spec.md` | `FR-1800`, `FR-1804`, `FR-1942` e `FR-1946` anotadas como emendadas pela `090`, e a decisão 003 da `080` como substituída |
| `tests/interface/test_limpeza_dos_achados_da_etapa_4.py` (novo) | os testes desta feature |
| `doc/inventario-visual-da-gestao-2026-10-16/capturar.py`, `depois-da-090/` | a variante nova; o inventário de antes e o de depois, nos dois estados da barra |

## Medições previstas

- Consultas por tela, antes e depois, em Resultados, Trilha da avaliação e Conclusões preservadas, com
  quem preside e com quem só audita: iguais (`FR-2064`) — medido, 7, 13 e 7 antes; 7, 13 e 6 depois
  (R-002). Na prévia: igual pelos Avisos; no máximo +1 pelos Resultados divulgados (R-004) — medido,
  10 antes pelas duas portas.
- Inventário: nada muda a 1280 px — a variante nova muda o texto da trilha, não a medida —; a 375 px,
  só as do R-003, e só de altura (`FR-2070`) — medido, quatro.

## Testes que mudam, e por quê

Ver o R-005 da pesquisa.

## Verificação

`make lint check test-pg DB_NAME=ps_090 POSTGRES_USER=$USER`, com `LC_ALL=pt_BR.UTF-8`; o percurso do
[quickstart](quickstart.md) no navegador, a 1280 e a 375 px; o inventário refeito com
`BARRA=expandida` e `BARRA=recolhida`, comparado por `comparar.py` e por `medidas.py` com o de antes.
