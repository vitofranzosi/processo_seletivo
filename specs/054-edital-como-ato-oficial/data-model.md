# Data Model — 054

## Publicacao (`publicacoes`) — uma coluna

| Campo | Tipo | Regra |
|---|---|---|
| `signatory_appointment` | texto, até 255, padrão vazio | O ato de nomeação de quem assina, copiado do catálogo no momento do ato (`FR-991`). Append-only, como os demais campos. Vazio nas Publicações anteriores à `054` e enquanto o catálogo não o tiver. |

`signatory_name` passa a poder ser vazio quando a Publicação vem da interface e o catálogo não tem nome
próprio (`FR-992`); pela API continua obrigatório (research R-007).

## Catálogo de seções (código, `editais/domain/secoes.py`)

`Secao(key, title, order, type, source)` — sai `default_text`. 22 entradas; ver `FR-980` e R-001.

## Catálogo de autoridades (código, `publicacoes/domain/autoridades.py`)

`Autoridade(chave, identificador, cargo, nome="", ato_de_nomeacao="")` — cargo obrigatório, os outros
dois opcionais (`FR-992`, R-008).

## Conteúdo publicado — nenhuma mudança de forma

`sections[*].content` da textual pode ser `""` (`FR-982`). Nenhuma chave nova, nenhum degrau canônico.

## Contexto do ato (parâmetros do compositor, não persistido)

| Elemento | Origem | No documento |
|---|---|---|
| autoridade: nome, cargo, ato de nomeação | a Publicação que está nascendo | bloco de autoridade |
| data do ato | `now` da transação, no fuso institucional | fecho |
| consolidação: datas incorporadas e vigência | Publicações do Edital (original + Retificações em vigor na vigência desta) | marca abaixo do anúncio |
