# Data Model: Relatório consolidado da unidade

Nenhuma tabela, nenhuma migration. As formas abaixo são estruturas de leitura, montadas na requisição
e descartadas com ela; a única gravação é o evento de auditoria da emissão.

## Pendencia (`099`, nova)

| Campo | Tipo | Regra |
|---|---|---|
| `tipo` | um de `RESULTADO_NAO_DIVULGADO`, `DEFINITIVO_NAO_PUBLICADO`, `REAVALIACAO_PENDENTE`, `PROVIDENCIA_PENDENTE`, `APURACAO_DESATUALIZADA`, `CONVOCACAO_AGUARDANDO`, `CONVOCACAO_VENCIDA`, `RECURSO_AGUARDANDO` | os oito da FR-2524 da `099` |
| `perfil_id` | `str` ou `None` | `None` só em `RECURSO_AGUARDANDO`, que é do Edital |
| `quantidade` | `int` | ocorrências (convocações, recursos); 1 nos demais |
| `marco` | `str` | nome publicado do marco, nos dois tipos de resultado |
| `ate` | instante ou `None` | prazo mais distante, em `CONVOCACAO_AGUARDANDO` |
| `publica` | derivado | `True` nos dois tipos de resultado; os demais são fato não público |

## FatosDoEdital (`099`, nova)

| Campo | Conteúdo |
|---|---|
| `edital`, `referencia`, `especie`, `desfecho_em` | o Edital, o instante, a espécie (FR-2523 da `099`), a data do ato |
| `perfis` | `LinhaDoPerfil` de cada Perfil publicado, como hoje |
| `pendencias` | `tuple[Pendencia]`, na ordem em que a `099` as redige |
| `vagas`, `vagas_reservadas` | soma das vagas imediatas; das em listas de modalidade |
| `inscricoes`, `inscricoes_com_vaga`, `rascunhos` | enviadas; nos Perfis com vaga imediata; iniciadas |
| `periodo_aberto`, `prorrogado` | do conteúdo vigente |
| `envios` | os instantes de envio, em ordem |
| `marcos_declarados`, `marcos_definitivos`, `datas_definitivas` | sem os marcos de Perfil sem inscrição (R-008) |
| `vagas_habilitadas`, `vagas_apuradas`, `vagas_desatualizadas` | apurações vigentes, por Perfil: atualizada, desatualizada |
| `convocacoes`, `recursos` | `Convocacoes` e `Recursos` totais |
| `retificacoes` | quantidade publicada até a referência |
| `posteriores` | `(rótulo, n, primeira)` da trilha, depois do desfecho |
| `perfis_abaixo` | `(nome, inscrições, vagas)` dos Perfis com a marca de procura da `040` |
| `omitidos`, `total_omitido` | Perfis omitidos pela supressão complementar; se os totais não públicos do Edital também o são |
| `cadastros_distintos` | como hoje |

`Relatorio` (a `099` de hoje) continua existindo e é montado de `FatosDoEdital` mais as leituras do
anexo.

## Conjunto (nova)

| Campo | Conteúdo |
|---|---|
| `criterio` | `publicacao`, `numero` ou `manual` |
| `inicio`, `fim` / `ano` | o intervalo da primeira publicação, ou o ano do número |
| `rotulo` | "Editais com primeira publicação entre 01/01/2026 e 30/06/2026" etc. |
| `alcancados` | Editais do escopo que o critério alcança, com a primeira publicação |
| `incluidos` | os elegíveis marcados |
| `retirados` | elegíveis do critério não marcados (com `escolha=1`) |
| `fora` | `(edital, motivo)` dos não elegíveis |
| `escolha_manual` | `True` quando a lista foi alterada à mão ou o critério é `manual` |

## Consolidado (nova)

| Grupo | Campos |
|---|---|
| Identificação | `referencia`, `conjunto`, `unidade`, `editais` (contagem), `por_situacao`, `por_especie`, `cancelados` |
| Universo | `universo` (não cancelados), `fora_dos_nao_publicos` (Editais com total omitido) |
| Oferta e procura | `vagas`, `vagas_reservadas`, `perfis`, `perfis_so_reserva`, `inscricoes` (`Numero`), `numerador`, `razao` (`Numero`), `envios_por_mes`, `linhas` (por Edital), `perfis_abaixo` |
| Execução | `retificacoes`, `editais_retificados`, `prorrogados`, `recursos`, `marcos_declarados`, `marcos_definitivos`, `editais_definitivos`, `editais_com_resultado_previsto` |
| Resultados | `vagas_habilitadas`, `vagas_apuradas`, `vagas_desatualizadas`, `vagas_nao_apuradas`, `convocacoes` |
| Providências | `pendencias_por_tipo` (tipo → Editais, ocorrências), `pendencias_por_edital`, `posteriores_por_edital`, `encerrados_com_pendencia` |
| Texto | `frases`, `indicadores` (seis), `pontos_de_atencao` |

Os números não públicos (`recursos`, `vagas_habilitadas`, `vagas_apuradas`, `vagas_desatualizadas`,
`convocacoes`, pendências não públicas) somam só os Editais do universo sem `total_omitido`.

## Evento de emissão

`RegistroAuditoria`, `aggregate_type="Unidade"`, `aggregate_id` = id da Unidade do escopo, `operation =
"EMITIR_RELATORIO_CONSOLIDADO"`, `permission = "visao:consultar"`, `detalhe`:

```json
{
  "referencia": "2026-10-24T17:00:00+00:00",
  "numero": 1,
  "sha256": "…",
  "criterio": {"modo": "publicacao", "inicio": "2026-01-01", "fim": "2026-06-30"},
  "incluidos": [{"id": "…", "edital": "07/2026"}],
  "retirados": [{"id": "…", "edital": "12/2026"}],
  "fora": [{"id": "…", "edital": "20/2026", "motivo": "EM_ELABORACAO"}]
}
```
