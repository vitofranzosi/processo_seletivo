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

A coluna do cadastro, ao lado, não muda: `limitado em 15` / `ilimitado` / `não há` na redação 1, e
`até 15 (quinze) classificados` / `sem limite` / `Não há` na redação 2.

## 2. A nota

- Texto: `CR: cadastro de reserva.`
- Sai logo abaixo da última linha da tabela, ou do último par da ficha, quando **pelo menos uma**
  célula dela é `CR`. Não sai em tabela ou ficha sem `CR`.
- Corpo de tabela, regular, alinhada à esquerda da tabela, presa à linha anterior na paginação.
- Não tem número, não é tabela e não entra em `tabelas_do_documento`.

## 3. A linha de total da tabela de Perfis

Soma `immediateVacancies` de todos os Perfis, o que é o mesmo que somar só as células numéricas. Sai
só quando a soma é maior que zero (`FR-997` da `054`).

## 4. Exemplo, cenário B, apresentação plana

```text
Tabela N — Perfis de vaga
Perfil                       Localidade   Vagas   Cadastro de reserva   Carga horária
TP-AFC — Tutor presencial    Afonso…      CR      até 15 (quinze)…      20 h
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
