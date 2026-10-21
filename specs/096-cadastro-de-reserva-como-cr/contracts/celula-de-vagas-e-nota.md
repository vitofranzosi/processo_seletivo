# Contrato: a célula de vagas, a nota e o bloco do portal

**Feature**: [spec.md](../spec.md) · **Research**: [research.md](../research.md)

Este contrato diz o que o documento e o portal mostram para cada Perfil. Os textos estão entre
crases, como saem.

## 1. A célula de vagas do documento

Vale para os quatro pontos de escrita do mapa da [research.md](../research.md): a tabela "Perfis de
vaga" e a ficha do Perfil único, na apresentação plana; e as tabelas de avulsos e de grupo, na
apresentação por perguntas. Vale nas duas redações.

| Perfil | Célula |
|---|---|
| 0 vaga, nenhuma linha positiva, cadastro `LIMITED` ou `UNLIMITED` | `CR` |
| 0 vaga, cadastro `NONE` | `0` |
| 0 vaga, alguma linha positiva (incoerente) | `0` |
| N > 0 vagas, com ou sem cadastro | `N` |

A coluna do cadastro, ao lado, não muda: `limitado em N` / `ilimitado` / `não há` na redação 1, e
`até N (por extenso) classificados` / `sem limite` / `Não há` na redação 2. O N é o limite que quem
elabora declara no Perfil; o sistema não o deriva de nada.

## 2. A nota

- Texto: `CR: cadastro de reserva.`
- Sai logo abaixo da última linha da tabela, ou do último par da ficha, quando **pelo menos uma**
  célula dela é `CR`. Não sai em tabela ou ficha sem `CR`.
- Corpo de tabela, regular, alinhada à esquerda da tabela, na posição logo depois da grade. Se a
  tabela terminar no pé da página, a nota pode abrir a seguinte, como a frase de reversão (D-007).
- Não tem número, não é tabela e não entra em `tabelas_do_documento`.

## 3. A linha de total da tabela de Perfis

Soma `immediateVacancies` de todos os Perfis, o que é o mesmo que somar só as células numéricas. Sai
só quando a soma é maior que zero (`FR-997` da `054`).

## 4. Exemplo, cenário B, apresentação plana

O cenário B é fictício (auditoria de 08/10/2026). O limite 15 do cadastro é o padrão do roteiro
`cenario_b.py`, e não dado de Edital real: o 140/2025, que o cenário imita, não declara limite.

```text
Tabela N — Perfis de vaga
Perfil                       Localidade   Vagas   Cadastro de reserva   Carga horária
TP-01 — Tutor presencial     Afonso…      CR      até 15 (quinze)…      20 h
…                                                  (16 linhas em CR)
TD-ADM — Tutor a distância   —            6       até 15 (quinze)…      20 h
TD-INFO-EDU — …              —            4       até 15 (quinze)…      20 h
Total                                     10
CR: cadastro de reserva.
```

## 5. O bloco do Perfil no portal

| Perfil | Destaque | Detalhe | Linha secundária |
|---|---|---|---|
| 0 vaga, cadastro `LIMITED` com limite N | `Cadastro reserva` | `até N classificados, para convocação futura` | **nenhuma** (antes: `0 vagas imediatas agora`) |
| 0 vaga, cadastro `UNLIMITED` | `Cadastro reserva` | `sem limite declarado, para convocação futura` | **nenhuma** |
| N > 0 vagas | `N` | `vagas imediatas` | o cadastro, se houver, como hoje |
| 0 vaga, cadastro `NONE` | `0` | `vagas imediatas` | como hoje |

O portal nunca mostra `CR`.

## 6. O fim da prévia (D-012, D-013)

| | Publicado | Prévia |
|---|---|---|
| última seção | no bloco do fecho, como desde a `069` | no bloco do espaço reservado |
| linha do local e data | `Vitória (ES), 8 de outubro de 2026.` | `Fecho do ato: local, data, autoridade e verificação, na publicação.` |
| demais linhas do fecho | autoridade, cargo, ato de nomeação, verificação | um espaço em cada uma, com a mesma altura |
| régua da verificação | desenhada | não desenhada (não tem altura) |
| páginas, linhas por página e sumário | — | **iguais** às do publicado com a autoridade prevista |
