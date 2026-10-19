# Implementation Plan: As telas dos avisos aos candidatos, quinto grupo da etapa 4

**Branch**: `claude/wizardly-hermann-1b3a8b` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

## Summary

Só apresentação, em seis templates. A trilha sobe ao cabeçalho de contexto nos Avisos aos candidatos,
no histórico de um aviso, na prévia, na conferência da interrupção, nos Modelos de aviso e na edição
de um modelo, pelo bloco que a `077` criou: as quatro telas de um Edital passam pelo Processo, como o
detalhe do Edital; a prévia diz a porta por onde se chegou; os modelos começam na seção da barra. Os
três estados vazios passam ao desenho comum, os botões de dois formulários ao rodapé comum, e "Novo
modelo" à faixa de ações da lista de Processos. Nenhuma migration, nenhuma permissão, nenhum
endereço, nenhuma view, nenhuma regra na folha comum, nenhuma classe nova.

## Technical Context

Django 5 sobre PostgreSQL; nada de servidor muda. Templates apenas, e as quatro views de um Edital já
entregam o Processo, o Edital, o aviso e — no reenvio — o aviso anterior que a trilha lê: nenhuma
consulta a mais. A linha de base visual é o inventário refeito em 18/10 sobre `cf6d7372`, no banco
`ps_inventario_086` (cópia do `ps_inventario_telas`), nos dois estados da barra, guardado em
`doc/inventario-visual-da-gestao-2026-10-16/depois-da-086/antes/`; ele é igual, variante a variante,
ao `depois-da-080/`. A decisão de cada mudança e as alternativas descartadas estão em
[research.md](research.md). Não há entidade nem contrato externo: `data-model.md` e `contracts/` não
se aplicam.

## Constitution Check

- **Negar por padrão (III, IV)**: nenhuma condição de template muda de sentido; cada região continua
  saindo das mesmas variáveis da view, e cada link da trilha leva a uma tela que já condiciona o
  acesso. A trilha não oferece nem esconde nível conforme quem lê (`FR-1946`).
- **Linguagem ubíqua (I)**: os rótulos da trilha são os que as telas já usavam; o único que mudou de
  destino é o do reenvio, que dizia uma tela e levava a outra (D-001).
- **Publicação é ato (II)**: o aviso continua não sendo o ato, e a frase que o diz continua a
  primeira depois do título (D-003). O envio continua no despacho.
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`. A `FR-1803` da `080`, que fixava estas telas com o cabeçalho
  da `076`, é anotada como emendada.
- **Simplicidade (V)**: blocos de template e classes que já existem. Nenhum script, nenhuma classe
  nova, nenhuma regra nova na folha.
- **Completude de jornada (VI)**: o percurso é provado no navegador a 1280 e a 375 px, pelo teclado,
  e o inventário inteiro é refeito nos dois estados da barra e comparado campo a campo.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/templates/interface/avisos_do_edital.html` | o bloco `caminho_do_contexto` com a trilha; os dois estados vazios em `.vazio` (R-001, R-004) |
| `aviso.html` | o bloco com a trilha, pelos Avisos aos candidatos (R-001) |
| `aviso_interromper.html` | o bloco com a trilha, pelos Avisos aos candidatos e pelo aviso; os botões em `p.salvar` (R-001, R-005) |
| `aviso_previa.html` | o bloco com a trilha da porta — reenvio, chamada ou resultado (R-002) |
| `modelos_de_aviso.html` | o bloco com a seção como página atual; "Novo modelo" em `p.acoes-do-painel`; o estado vazio em `.vazio` (R-003, R-004, R-005) |
| `modelo_de_aviso.html` | o bloco com a seção e o modelo; os botões em `p.salvar` (R-003, R-005) |
| `specs/080-*/spec.md` | `FR-1803` anotada como emendada pela `086` |
| `doc/inventario-visual-da-gestao-2026-10-16.md` e `depois-da-086/` | o inventário de antes e o de depois nos dois estados da barra, a comparação e as capturas das telas do escopo |

## Testes que mudam, e por quê

Nenhum teste existente muda (R-006). Testes novos em `tests/interface/test_telas_dos_avisos.py`.

## Verificação

`make lint check test-pg` com `DB_NAME=ps_086`; o percurso do [quickstart](quickstart.md) no navegador,
a 1280 e a 375 px, pelo teclado; o inventário refeito com `BARRA=expandida` e `BARRA=recolhida`,
comparado por `comparar.py` e por `medidas.py` com o de antes.
