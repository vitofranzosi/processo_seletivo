# Quickstart: O limite do cadastro de reserva lido do corte

**Feature**: [spec.md](spec.md) · **Contratos**: [contracts/documento.md](contracts/documento.md), [contracts/telas.md](contracts/telas.md)

Roteiro para provar a feature de ponta a ponta. Os passos automatizados são os da suíte; os manuais,
os da gestão e do portal.

## Pré-requisitos

- Banco preparado (`make preparar`) e migrations aplicadas (`manage.py migrate --check`).
- `INTERFACE_SELETOR_IDENTIDADE=true` para abrir `/gestao/`.
- Um `DB_NAME` próprio da worktree para a suíte.

## 1. A suíte da feature

```bash
cd backend && PYTEST_ADDOPTS="tests/unit/editais/test_cadastro_de_reserva.py tests/unit/publicacoes/test_cadastro_de_reserva_no_documento.py tests/integration/editais/test_cadastro_de_reserva_na_publicacao.py tests/interface/test_cadastro_de_reserva.py" make test-pg PYTEST_WORKERS=0
```

Esperado: tudo verde. Os nomes dos arquivos são os do plano.

## 2. O documento não se contradiz (US2, SC-2299, SC-2302)

1. Semeie a demonstração num banco vazio (`seed_demo`).
2. Abra o PDF do Edital da demonstração.
3. Confira:
   - Perfil `DOC-INFO`: `cadastro de reserva de até 2 (dois) classificados em cada lista de
     concorrência`, e não "até 6";
   - Perfil `TEC-LAB` (só de reserva, ilimitado): a unidade do corte começa por `Compõem o cadastro de
     reserva todos os classificados, sem limite.`, e não por "Seguem no processo".

## 3. A recusa da combinação incoerente (US1, SC-2300)

1. Na gestão, num rascunho, marque um Perfil como "Cadastro reserva limitado". Confira que não há
   campo de número, e que a linha de ajuda diz de onde o número vem.
2. Na Classificação, dê ao marco que convoca um corte com continuação admitida.
3. Abra a Revisão: o impedimento `reserve_limited_with_continuation` aparece, com o Perfil e o marco
   nomeados, e a publicação fica indisponível.
4. Tire a continuação: o impedimento some, e a Revisão diz `Limitado: até N`.

## 4. O Edital legado (US4, SC-2301)

1. Publique pela suíte, ou pelo helper `levar_a_publicacao` num shell, um Edital cujo conteúdo traga
   `reserveType: LIMITED` com `reserveLimit: 6` — o caso que a fixture de legado monta.
2. Abra a ocupação e a convocação do Perfil: a nota da FR-6947 aparece, com 6 e com o alcance do
   corte.
3. O PDF e o portal continuam dizendo 6.

## 5. A Retificação (US5, SC-2303)

1. Num Edital publicado depois da feature, com Perfil limitado, retifique o excedente do marco que
   convoca de 3 para 5.
2. A conferência mostra a linha `Cadastro de reserva` com `Limitado: até 3` → `Limitado: até 5`.
3. Retifique o excedente para que o número chegue a zero: a Retificação é recusada com
   `reserve_limited_to_nobody`.

## 6. A verificação inteira

```bash
cd backend && make lint check test-pg
```

## 7. O critério humano (SC-2304)

Uma pessoa da equipe que não participou da feature lê o PDF do passo 2 e responde, sem ajuda, quantos
podem ser chamados em cada Perfil. Registrar o resultado em `verificacao.md`.
