# Achado — a marca de CPF repetido põe a linha das Inscrições em duas

Encontrado em 30/09/2026, na `055` (*Polish da folha e dos componentes*), ao medir o critério do G2
da [auditoria de polish](auditoria-polish-ui-2026-09-30.md): a linha das Inscrições do Edital 51/2026
de 70 para **≤ 45 px**.

> **Não vira escopo por estar escrito aqui.** Priorizar é do usuário.

## O que se observou

O novo preenchimento de célula (`.5rem .75rem`) levou a linha de 69,2 para 62,8 px — e não para
≤ 45. A causa é a marca "⚠ CPF repetido neste Perfil" ao lado do CPF (`.coincidencia`, com
`white-space:nowrap`), presente nas **cinco** inscrições do Edital 51/2026 do seed: as cinco
candidatas de demonstração compartilham o mesmo CPF.

Medido a 1280 × 900, no banco da auditoria, escondendo só a marca:

| | Com a marca | Sem a marca |
|---|---:|---:|
| Preenchimento antigo (`.7rem 1.25rem`) | 69,2 px | 68,4 px |
| Preenchimento novo (`.5rem .75rem`) | 62,8 px | **39,5 px** |

O preenchimento é o que põe a linha numa linha só; a marca é o que a devolve a duas. Com a marca, as
sete colunas pedem 1.316 px sem quebrar, e a tabela tem 1.232.

## Por que a `055` não resolveu

Resolver pede mexer na marca — encurtar o texto, ou levá-la para baixo do CPF —, e a `055` não muda
texto nem reorganiza tela. A decisão foi registrada no research dela (D-021).

## O que ponderar

- **No uso real a marca é exceção.** CPF repetido no mesmo Perfil é o que a marca existe para
  apontar, e o seed o tem em todas as linhas por construção. Numa lista real, as linhas sem a marca
  já têm 39,5 px.
- **Se a marca continuar como está, a linha dela tem duas linhas** — e talvez deva: é a linha que
  pede atenção.
- Encurtar para "⚠ CPF repetido" (sem "neste Perfil") cabe, mas o Perfil é o que distingue a
  coincidência que importa da que não importa, e o `title` já diz a frase inteira.
