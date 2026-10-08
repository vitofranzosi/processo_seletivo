# Data Model: As atribuições idênticas saem uma vez no documento do Edital

**Feature**: [spec.md](spec.md) · **Plano**: [plan.md](plan.md)

**Nenhuma entidade, coluna, migration ou campo de conteúdo muda** (FR-1195, 2º ajuste). Este arquivo
existe para dizer isso com a precisão de quem vai implementar, e para descrever a única estrutura
nova — que é transitória e não sai da composição.

---

## O que é lido, e não muda

| Onde | O quê | Uso nesta feature |
|---|---|---|
| `PerfilVaga.duties` | texto livre | Não é lido: a composição lê o snapshot. |
| snapshot, `profiles[].duties` | string, `""` quando ausente | A fonte do agrupamento (D-002). |
| snapshot, `profiles[].code` | string única no Edital | Nomeia o Perfil no título da subseção comum. |
| snapshot, ordem de `profiles` | por `code` | Ordem dos Perfis, dos grupos e das subseções comuns (D-003). |

O conteúdo canônico, a impressão digital da versão, `Publicacao`, `VersaoConsolidada` e
`DocumentoPublicado` não são tocados. O documento de uma Publicação já feita continua com os mesmos
bytes (FR-1196).

---

## A estrutura transitória: o grupo de atribuições

Existe só dentro de uma chamada de composição. Não é registrada, não tem identidade, não vai ao
snapshot nem a tela alguma.

| Atributo | O quê | Regra |
|---|---|---|
| chave | tupla dos parágrafos, cada um reduzido às palavras | FR-1187, D-002. Nunca vazia. |
| perfis | os Perfis de mesma chave, na ordem do snapshot | Dois ou mais (FR-1188). |
| número | `{s}.{N+k}` | `N` = quantidade de Perfis; `k` = posição do grupo, a partir de 1 (FR-1189, D-003). |

**Invariantes**, que o FR-1191 cobra no documento:

- cada Perfil está em, no máximo, um grupo;
- Perfil de texto vazio não está em grupo nenhum;
- Edital de um Perfil não tem grupo;
- os números dos grupos são contíguos, começam em `N+1` e não colidem com nenhum número de Perfil.
