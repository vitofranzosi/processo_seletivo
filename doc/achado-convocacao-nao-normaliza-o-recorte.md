# Achado — a convocação não confere o recorte que recebe

Encontrado em 27/09/2026, no passo 0 da ordem adotada naquele dia (correções diretas, parte A), ao dar
porta à tela da convocação.

> **Situação: corrigido em 27/09/2026**, nas sobras do passo 0 — ver *O que foi feito*, no fim.
>
> **Não virou escopo por estar escrito aqui.** A parte A ligou a convocação à página do Edital e
> pôs nela a navegação entre recortes. O que se registra abaixo é da mesma tela, mas é
> outro defeito. Priorizar é do usuário.

## O que se observou

Com a presidência de um certame semeado, o mesmo `?lista=` com uma identidade que não é Modalidade
nenhuma do Perfil, nas três telas do marco:

| Tela | Resposta |
|---|---|
| ordenação | 404 |
| corte | 404 |
| convocação | **200** |

A ordenação e o corte passam por `_recorte_pedido` (`interface/views.py`), que reduz o pedido à
grafia canônica pela derivação única (`editais/domain/recortes.py`, `normalizar_recorte`). A
convocação só confere se o valor é uma identidade (`_identidade_ou_404`) e o entrega a
`leitura_do_recorte` como veio.

## Por que importa

- **Recorte inexistente parece recorte vazio.** A `034` separou os dois de propósito: *"Pedido por
  recorte que não corresponde a Modalidade alguma do Perfil MUST responder como objeto inexistente —
  e não como recorte vazio"* (`FR-499`). A convocação mostra a tela de um recorte que não existe, sem
  ninguém chamado e sem apuração, e isso se lê como "ainda não começou".
- **A grafia-armadilha abre um recorte próprio.** Pedida a Modalidade que o Perfil aponta como sendo a
  ampla, a ordenação a reduz ao recorte nulo (`FR-503`), e a convocação a trata como recorte à parte,
  sem apuração, onde convocar é recusado.
- **Com a navegação nova, o cabeçalho fica vazio nesse caso.** A tela passou a dizer *"Recorte: …"*, e
  num recorte que não está na lista derivada não há rótulo a mostrar.

Nenhum dos dois caminhos é oferecido pela interface: a porta da página do Edital abre a ampla, e a
navegação entre recortes vem da derivação única. Só se chega a eles pelo endereço, ou por link antigo.

## O que a correção seria

A mesma porta das outras duas telas: `_recorte_pedido` no lugar de `_identidade_ou_404` em
`convocacao` e em `convocacao_historico`. Como o comando `convocar` também recebe o recorte, vale
conferir se ele o normaliza — a `034` registrou o mesmo cuidado na emissão da ordem, em que fechar só
a view deixaria o comando alcançável por formulário antigo.

## O que foi feito

Em 27/09/2026, nas sobras do passo 0, a correção descrita acima, e só ela:

- **`convocacao`** passou por `_recorte_pedido`. O recorte que o Perfil não tem responde 404, como na
  ordenação e no corte (`FR-499`); a Modalidade apontada como ampla abre a ampla (`FR-503`), com o
  rótulo dela no cabeçalho.
- **`convocacao_historico`, só onde não há série.** A primeira versão desta correção o normalizava
  também, e a revisão pegou o erro: os atos guardam o recorte pela identidade do dia em que foram
  praticados, e uma Retificação que depois removesse a Modalidade, ou a apontasse como a ampla, faria o
  histórico dela responder 404 ou abrir a ampla — escondendo a série que explica aqueles atos. O
  histórico procura primeiro pela identidade pedida; só sem série alguma a pergunta vai à norma de
  agora. É o cuidado que `ocupacao-historico` já tem com o marco removido.
- **`convocar_view`** também. O comando `convocar` não normaliza por conta própria, mas não chegava a
  gravar: sem ato vigente para o recorte pedido, ele recusa com `ORDEM_NAO_VIGENTE` (409). A porta da
  view fecha o caminho do formulário antigo antes disso, como na emissão da ordem, e a Modalidade
  apontada como ampla passa a convocar na ampla, em vez de ser recusada.
- **O inventário das negativas da `033`** ganhou as três funções, classificadas como objeto
  inexistente.
- **`desfechar_view` e `comunicar_view` ficaram como estavam.** Elas agem sobre a convocação pelo
  identificador dela, e o `?lista=` só compõe o endereço de volta — que, sendo de recorte inexistente,
  cai no 404 da tela.

Os casos estão em `tests/interface/test_navegacao_entre_recortes.py` e, o da Retificação que remove a
Modalidade depois da convocação, em `tests/interface/test_historico_da_convocacao.py`.
