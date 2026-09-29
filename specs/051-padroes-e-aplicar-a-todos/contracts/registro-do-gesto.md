# Contrato — o registro do gesto na trilha

Uma linha de `RegistroAuditoria` por gesto confirmado, na mesma transação da gravação da etapa.

| Campo | Valor |
|---|---|
| `operation` | `APLICAR_A_TODOS` |
| `aggregate_type`, `aggregate_id` | `Edital`, o Edital |
| `permission` | `edital:elaborar` |
| `reason` | frase legível: *"Classificação — marco do Perfil LP01 aplicado a 6 Perfis"* |
| `detalhe` | ver abaixo |

```json
{
  "etapa": "classificacao",
  "unidade": "marco",
  "origem": {"perfil": "<uuid>", "codigo": "LP01"},
  "destinos": [
    {"perfil": "<uuid>", "codigo": "LP02", "efeito": "NASCE", "impressao": "<sha256>"},
    {"perfil": "<uuid>", "codigo": "LP03", "efeito": "SUBSTITUI", "impressao": "<sha256>"}
  ]
}
```

Para a Modalidade, `unidade = "modalidade"` e `origem.modalidade = "<código>"`. Para o controle do
Edital, `unidade = "callForm"` ou `"vacancyReversion"`, sem `origem.perfil`.

Só os destinos **alcançados** (incluídos e não fora do alcance) entram em `destinos`. A impressão é a da
unidade normalizada do destino depois do gesto — a mesma função que a Revisão aplica ao conteúdo atual.

**Leitura** (`FR-934`, `FR-935`): para cada destino e unidade, vale a linha mais recente que o alcançou;
a Revisão atribui o valor ao gesto só se a impressão atual for a gravada.

A linha é append-only, como toda a trilha. A trilha exibe `reason`; `detalhe` não é exibido.
