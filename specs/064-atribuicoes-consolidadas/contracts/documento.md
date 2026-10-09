# Contrato: o que o documento do Edital imprime sobre atribuições

**Feature**: [spec.md](../spec.md) · **Plano**: [../plan.md](../plan.md)

O documento é a interface pública desta feature: é o que a elaboradora vê na prévia e o que o
candidato lê no ato publicado. Este contrato fixa as frases, para que o teste as prenda.

`{s}` é o número da seção de Perfis; `N`, a quantidade de Perfis; `k`, a posição do grupo.

---

## Perfil de texto próprio — inalterado

```
{s}.{i} {código} — {denominação}
      Atribuições
            {parágrafo 1}
            {parágrafo 2}
```

Como antes desta feature, byte a byte no Edital de um Perfil (FR-1194).

## Perfil agrupado — a remissão (FR-1190, D-004)

```
{s}.{i} {código} — {denominação}
      Atribuições: as descritas no item {s}.{N+k}.
```

- **"Atribuições:"** em negrito, como o rótulo de par do documento; o restante em corpo regular.
- O espaço acima é o de sub-bloco, o mesmo do cabeçalho "Atribuições" do Perfil de texto próprio.
- Uma remissão por Perfil agrupado, na posição em que o bloco de atribuições ficava — entre a
  Descrição e a Remuneração.
- Nenhum outro texto de atribuições no Perfil agrupado.

## Subseção comum (FR-1186, FR-1189, D-005)

Depois da subseção do último Perfil, ainda na seção `{s}`:

```
{s}.{N+k} Atribuições comuns aos Perfis {código A}, {código B} e {código C}
      {parágrafo 1}
      {parágrafo 2}
```

- Título em negrito, com o corpo do título de Perfil; códigos na ordem do documento, enumerados com
  vírgula e "e".
- Título longo quebra **entre** códigos, nunca dentro de um: "ADS - P06" não se parte.
- Se algum código do grupo contém ", " ou " e ", **todos** os códigos do grupo vão entre aspas
  tipográficas: *Atribuições comuns aos Perfis “Tutor e Mediador” e “TEC”*.
- Parágrafos como os de atribuições, justificados, sem acréscimo, supressão nem reordenação.
- Sem tabela (FR-1192).

## O que não muda (FR-1192, FR-1197)

- Os números `{s}.1` a `{s}.N` dos Perfis.
- Os números das seções de topo, inclusive os que as telas de composição, Revisão e Retificação
  mostram.
- As legendas `Tabela n — …`.
- Requisitos, Remuneração, quadros, modalidades, marcos, documentos exigidos e todo o resto de cada
  Perfil.
