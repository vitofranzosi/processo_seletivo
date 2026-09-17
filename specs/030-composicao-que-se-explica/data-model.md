# Phase 1 — Modelo de dados

Três entidades são tocadas. Nenhuma nasce. **Nenhum dado publicado é reescrito.**

---

## `MarcoClassificatorio` — ganha a forma da ordem

Arquivo: `backend/processo_seletivo/editais/models/perfis.py`

| Campo | Tipo | Nasce como | Por quê |
|---|---|---|---|
| `forma_da_ordem` | `CharField(max_length=30, choices=FormaDaOrdem, blank=True)` | `""` | Vazio é o estado dos marcos compostos antes desta feature. **Não é padrão**: é ausência, e os leitores derivam dela o comportamento de hoje. |

```python
class FormaDaOrdem(models.TextChoices):
    POR_PONTUACAO = "POR_PONTUACAO"
    POR_SORTEIO = "POR_SORTEIO"
```

**Regras de validação**

- `POR_SORTEIO` com `etapas` vazio é **válido** — o sorteio precede a análise documental. Hoje a
  validação exige Etapa, contradizendo a própria ajuda da tela (**FR-432**, que é o ACH-48 da
  reauditoria). A exigência de Etapa passa a ser condicionada à forma da ordem, e não removida:
  `POR_PONTUACAO` continua exigindo ao menos uma.
- `POR_PONTUACAO` com `metodo_de_sorteio` preenchido é **válido no rascunho** e **recusado na
  publicação**: é o campo oculto de R5, que guarda sem publicar.
- `""` só é aceito em marco cujo Edital já estava publicado. Marco novo declara a forma.

**Transição de estado**: trocar `POR_SORTEIO` por `POR_PONTUACAO` (ou o contrário) **não apaga** o
que foi declarado para a forma anterior. O valor viaja oculto no rascunho e não alcança o publicado.

**Migração**: acrescenta coluna com `default=""`. Não percorre linha publicada, não escreve em
tabela append-only. O `N de M` do provisionamento de papéis cresce se a tabela for nova — não é o
caso: `MarcoClassificatorio` já existe.

---

## `Edital` — ganha o método comum do sorteio

| Campo | Tipo | Nasce como | Por quê |
|---|---|---|---|
| `metodo_de_sorteio_comum` | `JSONField(default=dict, blank=True)` | `{}` | Vazio significa **não declarado**, como no marco. Edital sem sorteio nunca o preenche. |

**A resolução, em um lugar só**: o método efetivo de um marco é o dele quando declarado, senão o do
Edital. Um único seletor responde por isso, e os leitores — cálculo, sorteio, serializers,
supervisão — passam a perguntar a ele. Duas implementações dessa regra seriam duas respostas para a
mesma pergunta, que é o que o princípio II proíbe.

**O que não muda**: Edital publicado continua com o método literal em cada marco. A resolução só
alcança marco **sem** método próprio — estado que nenhum Edital publicado tem.

---

## `PerfilVaga` — não muda

Muda **quando** suas declarações sobre ampla concorrência e reversão de vaga reservada são
apresentadas (FR-417), e nada mais. Sem campo novo, sem migração.

**Atenção à grafia-armadilha**: o recorte de ampla concorrência que o sorteio usa é o `NULL` —
a Modalidade "AC" declarada é outra coisa, e não tem vagas. FR-417 condiciona a pergunta à
existência de **ao menos uma Modalidade declarada**, e é a declarada que conta.

---

## Derivação de código e denominação (FR-420)

Não é campo. É valor inicial calculado do Perfil a que o marco pertence, entregue já preenchido e
editável. `uq_marco_perfil_code` continua valendo — a derivação precisa produzir código único dentro
do Perfil, e desempatar quando o Perfil já tiver marco com o código derivado.

**Nunca alcança conteúdo já declarado** (FR-421), inclusive em Retificação.
