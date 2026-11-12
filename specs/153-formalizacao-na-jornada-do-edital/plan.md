# Implementation Plan: A formalização na jornada guiada do Edital (153)

**Branch**: `claude/eager-snyder-f9441b` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

## Summary

Uma derivação só, **a passagem ao setor**, conta as pessoas aptas do Edital por situação:

- disponibilizadas;
- sem documento a disponibilizar;
- pendentes por causa: sem definição, sem quem receba, a exportar.

Quatro leitores usam essa derivação, e nenhum refaz a pergunta:

1. o andamento da `127`, que vira providências do nível 1, e com elas as da fase Conclusão do Centro
   da `136`;
2. o bloco "Disponibilizar ao setor" da fase Conclusão;
3. os fatos do relatório do Edital da `099`, que viram uma pendência nova;
4. as duas confirmações de encerrar, a do Edital (`113`) e a do Processo (`130`), que repetem as
   pendências do relatório por regra (FR-3535 da `113`, FR-4351 da `130`).

## Technical Context

**Language/Version**: Python 3.13, Django 5 | **Storage**: PostgreSQL (nenhuma migration)
**Testing**: pytest, contra PostgreSQL (`make test-pg`) | **Project**: monólito web

Nenhuma tabela, coluna, evento de trilha ou rota nova.

## Constitution Check

- **Publicação imutável:** não toca ato publicado. Ela lê definição, designação e exportação, que
  são append-only, e não as altera.
- **Nada é excluído:** nada se grava.
- **Negar por padrão:** o link de cada providência vai só a quem a tela real aceita, pelo mesmo
  predicado da tela (FR-6111). Nenhuma tela nova, e nenhuma autorização nova.
- **LGPD:** só contagens do Edital, sem nome de pessoa nem de Perfil (FR-6116).

## Design

### A derivação — `formalizacao/application/passagem.py` (novo)

`da_passagem(edital) -> Passagem | None`. Devolve `None` fora de publicado ou encerrado, e sem
pessoa apta (FR-6100, FR-6130). Ela lê:

- a definição vigente (`definir.vigente`);
- as pessoas aptas pelo **seletor único** da `117` (`conjunto.aptos`, que não lê arquivo,
  FR-3674 da `117`);
- os registros de exportação do Edital;
- as designações vigentes;
- quem tem o papel Formalização vigente na unidade, ativo.

A classificação segue a FR-6106, nesta ordem: disponibilizada, sem definição, sem documento (nenhum
documento incluído no conjunto), sem quem receba, a exportar.

**Ajuste na spec (FR-6104).** "Sem documento a disponibilizar" passa a ser *sem documento incluído
no conjunto do seletor único*, e não *sem requisito aplicável*. O motivo: uma pessoa com documento
"não apresentado" e nenhum incluído não pode ser exportada (o pacote exige arquivo,
`ck_exportacao_formalizacao_com_arquivo`). Contá-la como "a exportar" daria ao setor uma providência
impossível de cumprir.

### O nível 1 — `interface/andamento.py`

- A natureza nova é `FORMALIZACAO`. Os papéis novos são `ACESSOS` ("Quem administra os acessos da
  unidade") e `SETOR` ("O setor da formalização"), no fim de `ORDEM_DOS_PAPEIS` (FR-6114).
- `_Leitor._providencias_da_formalizacao()` gera uma providência *Pendente* por causa com pessoa.
- Uma providência é "sua" pelo predicado da tela de destino, e não por `Alcance.pratica`. O
  encerramento do Processo não fecha a formalização (FR-3710 da `117`), e por isso o `ativo` do
  `Alcance` não entra:
  - **definir**: `alcance.conduz`;
  - **designar**: `acesso:gerir`;
  - **exportar**: a capacidade Formalização e uma designação vigente no Edital.
- O `Andamento` ganha `formalizacao` (a `Passagem`), que o Centro desenha na Conclusão.

### O Centro — `interface/centro.py` e o template

- `_DA_NATUREZA[FORMALIZACAO] = CONCLUSAO` (FR-6115).
- O bloco "Disponibilizar ao setor" na fase Conclusão (FR-6118 a FR-6121), com a frase fixa do
  limite em `conceitos.py`.

### Relatório e encerramento

- O tipo `APTAS_SEM_DISPONIBILIZACAO` fica em `pendencias_do_edital.py`, onde moram os tipos.
- A `Pendencia` ganha `detalhe`, a contagem por causa.
- `fatos_do_edital` a acrescenta, com `perfil_id=None`: é do Edital inteiro, como o recurso aguardando.
- `texto_da_pendencia` a redige; `redigir_pendencias` a põe com as do Edital; o consolidado ganha o
  rótulo dela.
- `encerramento.DA_099` a inclui, e com isso a `130` também. O `Item` dela leva o caminho da
  primeira causa que o ator pratica, ou "Peça a …" (FR-6126). A frase do encerramento acrescenta que
  a exportação continua (FR-6124).

## Riscos

- **Orçamento de consultas.** O Centro e o relatório ganham de 3 a ~10 consultas por Edital,
  constantes no número de pessoas aptas. Os testes de orçamento existentes dizem se cabe.
- **Espécie do relatório.** Um Edital encerrado com pessoa apta pendente passa de "encerramento" a
  "acompanhamento", porque agora tem pendência. É coerente com a FR-3542 da `113`.
