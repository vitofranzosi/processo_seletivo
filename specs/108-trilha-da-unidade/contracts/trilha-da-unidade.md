# Contrato: `GET /gestao/trilha-da-unidade`

## Pedido

| Parâmetro | Valores | Efeito |
|---|---|---|
| `assunto` | `unidade`, `autoridades`, `modelos`, `avisos`, `acessos`; ausente ou outro valor | o filtro; desconhecido vale como todos (D-009) |
| `cursor` | o valor que a página anterior ofereceu | os atos anteriores ao último mostrado |

Nenhum parâmetro escolhe a unidade (`FR-3154`). `POST` e demais métodos: 405.

## Respostas

| Situação | Resposta |
|---|---|
| sem identidade | o pedido de identificação de sempre (página de acesso, ou a tela sem acesso da `107`) |
| sem `auditoria:consultar` na unidade ativa, ou escopo ativo institucional | **403**, a recusa explicada da `033`, nomeando a base "consultar a trilha de auditoria da unidade" |
| cursor adulterado | **400**, `invalid_cursor`, como em `consultar` |
| autorizado | **200**, a página |

Não há 404: a página não recebe identificador (D-008).

## A página

- título "Trilha da unidade" e a unidade ativa pelo nome;
- o filtro por assunto, com "Filtrar" e, quando filtrado, "Limpar";
- a lista ordenada `ol.auditoria`, do mais recente para o mais antigo, vinte por página, cada item
  com: data e hora; o ato; o assunto; sobre o quê; "por" quem; a situação; o motivo entre aspas; e,
  na alteração da unidade, a lista dos dados mudados (antes → depois);
- "Ver atos anteriores", quando houver, preservando o `assunto`;
- sem atos: "Nenhum ato administrativo registrado para esta unidade.", ou, filtrado, "Nenhum ato
  corresponde ao filtro.";
- nenhum formulário que grave; nenhum `style=`, `<style>` ou `<script>`.

## Barra

"Trilha da unidade", no grupo "Unidade", para quem tem `auditoria:consultar`; o ícone `i-trilha`.
