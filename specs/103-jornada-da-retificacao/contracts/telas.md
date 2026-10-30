# Contrato das telas: Jornada operacional da Retificação

Todas sob `/gestao/`, com o seletor de identidade ligado em desenvolvimento. Nenhuma rota de API
nova.

## `GET /gestao/` — Lista

Na célula de situação de cada Edital com Retificação em curso, uma marca por Retificação:

- com o ato da pessoa: link ao detalhe da Retificação com o texto `Retificação <situação> · <ato>`
  (por exemplo, "Retificação em revisão · Homologar");
- sem: link ao detalhe com `Retificação <situação> · aguarda <papel>`.

## `GET /gestao/editais/<id>/` — detalhe do Edital

Seção `Retificações em curso` (`id="retificacoes-titulo"`): o parcial `_retificacoes_em_curso.html`;
estado vazio "Nenhuma Retificação em curso." quando o Edital está publicado e não há nenhuma.

## `GET|POST /gestao/editais/<id>/retificar` — criar

Antes do formulário, quando há Retificação em curso: aviso com o mesmo parcial e, para a que está em
elaboração, a quem pode elaborar, o link "Continuar a elaboração" para a edição. A criação não muda.

## `GET /gestao/retificacoes/<id>/` — detalhe da Retificação

- passagem de bastão: "O próximo ato é seu: …" ou "Aguardando <papel> para …"; finais: "Esta
  Retificação está encerrada (<situação>)";
- em elaboração com motivo de devolução: "Devolvida para correção. Motivo: …";
- "Editar a Retificação" a quem pode elaborar, em elaboração;
- cada ato: `<a class="botao …">rótulo</a>`, ou `<span class="botao desabilitado" aria-disabled="true"
  aria-describedby="motivo-<chave>">rótulo</span>` com o motivo;
- "Quem atuou": criou, submeteu, homologou, publicou.

## `GET|POST /gestao/retificacoes/<id>/atos/<acao>` — confirmação

- `impedimento.motivo == "segregacao"`: "Uma pessoa não pode elaborar, homologar e publicar a mesma
  Retificação…", sem "Confirmar", com status 403 se enviada;
- submeter, homologar e devolver: "Depois deste ato, a Retificação fica aguardando <papel>.";
- homologar por quem submeteu: aviso de que a publicação ficará com outra pessoa.

## `GET|POST /gestao/retificacoes/<id>/editar` — edição (nova)

| Situação | Resposta |
|---|---|
| fora do escopo | 404 |
| sem `retificacao:elaborar` | 403, "Editar uma Retificação exige a permissão retificacao:elaborar…" |
| fora de `EM_ELABORACAO` | 409, a situação atual e a saída |
| `revisao` do POST diferente da atual | 412, a página de recusa, sem ler o formulário e sem gravar |
| a revisão muda entre a leitura e a gravação | 200, o formulário com a mesma recusa, nada gravado |
| `POST` sem `confirmar` | 200, a conferência "O que muda em relação ao rascunho (N)" |
| `POST` com `confirmar=1` válido | 302 para o detalhe com `?ato=editar`; mesma Retificação, revisão + 1 |
| a edição desfaz tudo | 200 com "Com esta edição a Retificação não mudaria conteúdo nenhum…" e nada gravado |

Campos do formulário: os de Retificar, mais `revisao` (oculto) e `desfazer-remocao` (um por remoção
declarada, com o índice da alteração).
