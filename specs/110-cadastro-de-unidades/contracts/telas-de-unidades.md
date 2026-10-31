# Contrato: as telas de `/gestao/administracao-de-unidades`

## Quem chega

| Situação | Resposta |
|---|---|
| sem identidade | o pedido de identificação de sempre |
| sem `unidade:administrar` no escopo ativo, ou com escopo ativo que não é o institucional — inclusive o Administrador institucional de acessos sem o papel do registro (EC-16) e toda sessão de demonstração, que nunca tem a permissão | **403**, a recusa explicada da `033`, nomeando a base "administrar o registro de unidades" (FR-3309, FR-3311, EC-8) |
| sessão de demonstração que um dia tenha a permissão | **403**, recusa `so_entrada_institucional` (FR-3312, EC-10) |
| autorizado, código inexistente em rota com `<codigo>` | **404** (FR-3315) |
| autorizado | a tela |

As duas recusas vêm nesta ordem, a da `107` (`_ator_do_nivel`), e as duas antes de qualquer leitura
do registro.

Métodos fora dos listados: 405.

## Lista — `GET /gestao/administracao-de-unidades`

- título "Unidades";
- tabela com sigla, nome, código, local e situação ("Ativa", "Desativada"), por sigla; cada linha
  leva à ficha;
- "Cadastrar unidade";
- sem formulário que grave.

## Cadastrar — `GET|POST /gestao/administracao-de-unidades/cadastrar`

**Campos**: `codigo`, `sigla`, `nome`, `cabecalho_1`, `cabecalho_2` (opcional), `local`,
`atendimento` (opcional), `motivo`, `acao` (`conferir` ou `confirmar`), `versao` (só na edição).

| `acao` | Efeito |
|---|---|
| ausente (GET) | o formulário vazio |
| `conferir` | valida; com erro, o formulário com a mensagem no campo; sem erro, a **conferência**: a prévia (D-010), os campos, o aviso de que o código não muda, e — quando o ato muda a identificação das telas sem unidade — o aviso da moldura (FR-3330). Nada é gravado |
| `confirmar` | chama `registrar`; sucesso → **302** para a ficha, com "Unidade cadastrada." ; recusa → a conferência com a mensagem, **200** |

## Ficha — `GET /gestao/administracao-de-unidades/<codigo>`

- os campos, a situação, a prévia do cabeçalho (as linhas, a sigla no anúncio do ato, o local; o
  aviso de linha que não cabe);
- "Editar", e "Desativar" ou "Reativar", conforme a situação;
- "Conceder o Administrador de acessos desta unidade", que leva à concessão da `107` (a unidade
  pré-escolhida, se a tela da `107` aceitar; senão, a tela dela) — só para quem também tem
  `acesso:administrar`, porque a concessão é do outro papel (D-002);
- o histórico (D-009), pela leitura `ficha` da aplicação e nunca por consulta da view, mais recente
  primeiro: quando, o ato, quem, a situação, o motivo, o antes → depois.

## Editar — `GET|POST /gestao/administracao-de-unidades/<codigo>/editar`

Como cadastrar, sem o campo `codigo`. O código da rota é a unidade; um `codigo` enviado no corpo é
ignorado (EC-9). A conferência mostra o antes e o depois de cada campo mudado, e carrega `versao`
(D-007). Sem mudança: a recusa `nada_mudou` no formulário (FR-3322). `confirmar` com `versao`
diferente da atual: a recusa `unidade_alterada`, sem gravar (FR-3325).

## Desativar e reativar — `GET|POST /gestao/administracao-de-unidades/<codigo>/{desativar|reativar}`

| `acao` | Efeito |
|---|---|
| ausente (GET) | as consequências (FR-3326, FR-3327), o número de Processos não encerrados da unidade, o aviso da moldura quando couber (FR-3330), o campo `motivo` e a `versao` em que tudo isso foi calculado |
| `confirmar` | chama `desativar` ou `reativar`; sucesso → **302** para a ficha; recusa → a mesma tela com a mensagem |

Transição já feita (`unidade_ja_desativada`, `unidade_ja_ativa`): a recusa, sem gravar (FR-3328).
`versao` diferente da atual: `unidade_alterada`, sem gravar (D-007).

## Barra

"Unidades", em `SECOES_DE_ACESSO`, logo depois de "Administração de acessos", só para quem tem
`unidade:administrar` no escopo ativo. A demonstração nunca a vê.

## Comum a todas

Nenhum `style=`, `<style>`, `<script>` nem `on*=` (CSP); estilo em `telas/unidades.css`; toda classe
citada tem regra na folha; os rótulos em português, com `for`/`id`; a recusa volta à mesma tela com
os valores digitados.
