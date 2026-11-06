# Data Model: Correções de orientação e segurança operacional (P0)

**Nenhuma entidade, tabela, coluna ou migration nova** (FR-4040). Tudo abaixo é leitura derivada no
instante da tela.

## Recorte sem inscrito (derivado)

| Campo | Origem |
|---|---|
| `lista_id` | a derivação canônica de recortes do Perfil (`recortes_do_perfil`); `None` é a ampla |
| inscrições encerradas | `recusa_por_inscricoes_em_curso(conteudo, agora, consequencia=CONGELAR_A_RELACAO) is None` |
| elegíveis | `projecao.elegiveis(submetidas_do_perfil, lista_id=..., habilitadas=None)` |
| congelada | `relacao_vigente(...) is not None` |

**Regra**: marco que sorteia **e** inscrições encerradas **e** elegíveis vazio **e** não congelada (D-002).

## Estado da convocação (do domínio, sem mudança)

`convocacao/domain/prazo.estado` → `DESFECHADO`, `CONVOCADO_PRAZO_NAO_INICIADO`,
`CONVOCADO_PRAZO_EM_CURSO`, `CONVOCADO_VENCIMENTO_DECORRIDO`.

| Estado | Espécie da pendência | Frase |
|---|---|---|
| prazo não iniciado | `CONVOCACAO_SEM_COMUNICACAO` (**nova**) | "N convocação(ões) sem comunicação enviada" |
| prazo em curso | `CONVOCACAO_AGUARDANDO` | "N convocação(ões) aguardando resposta, até dd/mm/aaaa" |
| vencimento decorrido | `CONVOCACAO_VENCIDA` | "N convocação(ões) com prazo encerrado sem registro de resposta" |
| desfechado | — | conta em aceitas ou em outras respostas |

`Convocacoes` (dataclass do relatório) ganha `sem_comunicacao: int = 0`; o dicionário de convocações do
consolidado ganha `"sem_comunicacao"`, e "outras respostas" passa a descontá-lo.

## Resumo da conferência da ordem (derivado)

Saída de `conferencia_da_ordem.resumo(proposta)`:

| Campo | Significado |
|---|---|
| `consideradas` | posições + sem posição |
| `sem_resultado` | sem posição, não eliminadas, sem Resultado vigente em ao menos uma Etapa enumerada |
| `por_etapa` | `[(nome publicado da Etapa, quantas sem Resultado nela)]`, na ordem do marco, só as com contagem > 0 |
| `nenhuma_com_resultado` | há consideradas, e nenhuma tem Resultado vigente em Etapa enumerada alguma |
| `grupos` | `[(motivo, consequência, [protocolos])]` dos sem posição, na ordem de aparição |

## Prévia do sorteio

`congelar_agora_inviavel` ganha `inclui_congelamento: bool` — algum recorte não congelado, com
`projetados > 0` e sem diagnóstico. A condição de existência do dicionário não muda (`102`).
