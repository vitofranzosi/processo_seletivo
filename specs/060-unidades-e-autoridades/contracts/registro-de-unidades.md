# Contrato — o registro de Unidades

O registro é declarado num arquivo versionado e aplicado por comando (research R-003, `D-002`).
Nenhuma tela escreve nele.

## O arquivo — `backend/processo_seletivo/unidades/unidades.json`

```json
{
  "cefor": {
    "sigla": "Cefor",
    "nome": "Centro de Referência em Formação e em Educação a Distância",
    "cabecalho": ["Centro de Referência em Formação", "e em Educação a Distância"],
    "local": "Vitória (ES)",
    "ativa": true
  }
}
```

- **A chave é o código**, e é o valor de `institution_scope` (FR-1107). Minúsculas, letras, dígitos
  e hífen.
- `cabecalho` tem uma ou duas linhas. Quebrar o nome é decisão editorial: as linhas são impressas
  como estão, sem refluxo.
- `ativa` é obrigatório.
- A entrada do Cefor reproduz o que o compositor imprime hoje (FR-1111, FR-1114).

## O comando — `manage.py sincronizar_unidades`

| Situação no arquivo | Efeito | Auditoria |
|---|---|---|
| código novo | cria a Unidade | `REGISTRAR_UNIDADE`, `detalhe.depois` |
| código existente, algum campo diferente | atualiza os campos | `ALTERAR_UNIDADE`, `detalhe.antes` e `.depois` |
| código existente, nada diferente | nada | nenhuma |
| código que está no banco e saiu do arquivo | **recusa**, sem gravar nada | — |
| arquivo malformado (campo faltando, 0 ou 3+ linhas de cabeçalho, código inválido) | **recusa**, sem gravar nada | — |

- Tudo numa transação: ou o arquivo inteiro se aplica, ou nada.
- O ator da trilha é `implantacao`, e o escopo do evento é o código da própria Unidade.
- A saída diz quantas foram criadas, alteradas e mantidas, no formato
  `Unidades: C criadas, A alteradas, M sem mudança.`
- Roda no `make preparar`, depois da segunda passada do provisionamento.

## Recusas

| Código | Quando |
|---|---|
| `unidade_retirada` | uma Unidade registrada não está no arquivo — *"desative-a com `ativa: false`; nenhuma Unidade é excluída"* |
| `unidade_malformada` | o arquivo viola uma das regras acima, nomeando o código e o campo |
