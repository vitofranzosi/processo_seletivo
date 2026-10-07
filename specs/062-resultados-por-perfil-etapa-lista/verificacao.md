# Verificação — 062 · Resultados divulgados por Perfil, etapa e lista

Medido em 07/10/2026 no navegador do painel, numa cópia (`ps_062_demo`) do banco de demonstração
`ps_apresentacao_grafico`, migrada para a `main` da época. É o mesmo Edital 72/2026 da captura que
motivou a feature: dois Perfis, três listas cada, preliminar sucedido por definitivo em todas.

## 1. A página do Edital, a 1280 × 900

| O que se mediu | Resultado |
|---|---|
| Títulos do bloco | `h2` Resultados divulgados → `h3` Professor Substituto — Matemática → `h4` Classificação final — Matemática → `h3` Técnico de Laboratório — Química → `h4` Classificação final — Técnico de Laboratório |
| Links do bloco | 13 (6 vigentes, 6 sucedidos, 1 convite), **13 nomes acessíveis distintos** |
| Nome acessível, exemplo | "Ampla concorrência — Classificação final — Matemática — Professor Substituto — Matemática" |
| Nome acessível no histórico | "Ampla concorrência — Resultado preliminar, publicado em 14/09/2026 — Classificação final — Matemática — Professor Substituto — Matemática" |
| Histórico | um "Publicações anteriores (3)" por etapa — dois na página, contra seis antes |
| Convite | depois dos dois Perfis, fora deles: "Participou deste processo seletivo? / Consulte sua classificação e situação individual. / Entrar para ver minha situação" |
| Peso dos títulos | `h3` 16 px / 600 (o mesmo da seção Vagas); `h4` 15 px / 600 |

**Ajuste feito durante a verificação.** O `h4` saía no negrito padrão (700), e a etapa pesava mais
que o Perfil que a contém. Passou a 15 px / 600.

## 2. A 375 px

| O que se mediu | Resultado |
|---|---|
| `scrollWidth` do documento | 375, igual à largura da tela |
| Natureza e data | abaixo do nome da lista, sem alargar a linha |

## 3. A ida e volta pelo convite

Pessoa da demonstração com inscrição enviada no Edital (`edson.silva.ciclo@exemplo.test`, Perfil
Técnico de Laboratório, lista PPI):

1. "Entrar para ver minha situação" → `/selecoes/acesso?destino=%2Fselecoes%2F<edital>%2F`.
2. E-mail, código lido do log do servidor → volta a `/selecoes/<edital>/#resultados-titulo`.
3. O convite passou a "Ver minha situação".
4. Um clique → `/selecoes/inscricoes/<id>/acompanhamento`, com as duas situações divulgadas.

**Defeito encontrado e corrigido aqui.** A primeira versão mandava "Ver minha situação" para
`portal:inscricao`, que mostra o que foi enviado e **não** a situação; a situação divulgada mora no
acompanhamento. O teste de convite cobrava o destino que o código produzia, e por isso passava. O
destino, o teste, o contrato, o data-model e a `FR-1162` foram corrigidos juntos.

## 4. O que a verificação confirmou do achado registrado

No acompanhamento da mesma pessoa aparecem duas seções idênticas — "Classificação final — Técnico de
Laboratório / Resultado definitivo" —, uma com **8º lugar** e outra com **2º lugar**, sem dizer qual
lista é qual. É o achado de `acompanhamento.html` registrado na spec, fora do escopo desta feature.

## 5. A suíte

Ver o final deste arquivo, preenchido em T024.
