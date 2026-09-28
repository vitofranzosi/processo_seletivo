# Achado — a ocupação não pode apontar para a convocação

Encontrado em 27/09/2026, no passo 0 da ordem adotada naquele dia (correções diretas, parte A).

> **Não virou escopo por estar escrito aqui.** O que se registra é uma decisão em aberto, e decidir é
> do usuário.

## O que se observou

A reavaliação de 27/09 pedia a porta da convocação "a partir da ocupação e da página do Edital". A
parte A pôs as duas. A da ocupação era um link por recorte apurado, *"Abrir a convocação deste
recorte"*. Ele reprovou a suíte em `tests/test_vocabulario_da_ocupacao.py`, que varre `ocupacao.html`
atrás de `convoca[çc]`.

A varredura aplica requisito escrito da `016`:

- **UX-034**: *"Termo de convocação MUST NOT aparecer nesta feature, e a proibição é verificável por
  varredura."*
- **FR-258**: nenhuma tela da `016` pode afirmar que alguém foi convocado, aceitou ou se matriculou.

O link não afirma nenhum desses fatos: ele nomeia a tela vizinha. Mas a letra da UX-034 proíbe o
termo, e não só a afirmação. **O link saiu**, por decisão tomada na sessão, e a porta ficou só na
página do Edital. Os recortes reservados se alcançam pela navegação entre recortes que a convocação
ganhou.

## O que continua faltando

Quem termina uma apuração na ocupação não tem caminho para convocar naquele recorte. Precisa voltar à
página do Edital, abrir a convocação do marco e escolher o recorte de novo. É o passo do fluxo em que a
convocação é pedida: sem apuração ela recusa, e a apuração acontece na ocupação.

## O que destravaria

Uma emenda à UX-034 que separe **nomear a tela vizinha** de **afirmar fato da `019`**. Por exemplo,
admitir o nome da tela num link de navegação e manter a proibição em todo o resto do texto. A
varredura precisaria da mesma exceção, dita por extenso, para não virar brecha. É mudança de spec, e
por isso não coube numa correção direta.

O simétrico já existe e não esbarra em nada: a convocação aponta para a ocupação (*"Ir para a apuração
de ocupação"*), porque a `019` conhece a `016`, e não o contrário.

## Decidido e feito (28/09/2026)

O usuário decidiu a emenda proposta acima (RC-137). A `UX-034` da `016` passou a separar nomear a
tela vizinha de afirmar fato da `019`, e admite um elemento só: o link *"Abrir a convocação deste
recorte"*, com destino na rota da convocação. A varredura (`tests/test_vocabulario_da_ocupacao.py`)
tem a mesma exceção por extenso — o elemento inteiro, com esse texto e essa rota —, e um teste afirma
que cada variação dela continua reprovando. O link voltou à ocupação, por recorte apurado.
