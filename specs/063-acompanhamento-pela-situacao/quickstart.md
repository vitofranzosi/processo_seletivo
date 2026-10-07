# Quickstart: verificar a `063`

## Pré-requisitos

- `backend/.env` presente (copiado do checkout principal) e `uv sync --extra dev` feito.
- PostgreSQL local de pé, com `LC_ALL` exportado.
- `DB_NAME` próprio (`ps_063`) se outra suíte estiver rodando.

## 1. Os testes da feature

```bash
cd backend && make test-pg DB_NAME=ps_063 PYTEST_ADDOPTS="tests/unit/portal/test_situacao_da_inscricao.py tests/portal/test_acompanhamento_pela_situacao.py tests/portal/test_acompanhamento_resultado.py tests/interface/test_portal_caminho_da_convocacao.py tests/test_vocabulario_da_convocacao.py tests/test_vocabulario_do_requerimento.py"
```

Esperado: todos passando. A matriz de estados é a do [data-model](data-model.md) §1.1, e as
invariantes são as do [contrato](contracts/bloco-de-situacao.md) §3.

## 2. A verificação completa

```bash
cd backend && make lint check test-pg DB_NAME=ps_063
```

Esperado: lint e check limpos; a suíte com os mesmos onze pulados do `AGENTS.md` e nenhuma falha.

## 3. A demonstração, pelo portal

Banco `ps_063_demo`, cópia de `ps_062_demo`, migrada (`createdb -T ps_062_demo ps_063_demo`, depois
`migrate` e as duas passadas de `provisionar_papeis`). Servidor com `PORTAL_IDENTIDADE_DEMO=true` e
`INTERFACE_SELETOR_IDENTIDADE=true`; o código de acesso sai no log do servidor.

| Caso | Quem | O que conferir |
|---|---|---|
| (a) duas listas | `edson.silva.ciclo@exemplo.test`, Edital 72/2026 | topo "Aguardando chamada"; porquê com "Ampla concorrência: 8º lugar…" e a lista da reserva com "2º lugar…"; dois cartões de título distinto |
| (b) classificação sem ocupação | o mesmo | nenhuma palavra de ocupação; "Nada por enquanto" e a frase neutra de novas chamadas |
| (c) cadastro reserva | o mesmo (Perfil com cadastro reserva limitado a 9) | "O Edital prevê cadastro reserva de até 9 pessoas para este Perfil." — e nada de "você está no cadastro reserva" |
| (d) convocação aberta | `mariana.reis.ciclo@exemplo.test`, Edital 72/2026 | topo "Convocado"; ação "Preencher o Requerimento de Matrícula"; prazo 09/10/2026 às 18h00; a frase "você perderá esta convocação" |
| (e) desfecho | `ana@exemplo.test`, Edital 51/2026, depois de a gestão registrar o *Aceite* na tela da convocação | topo "Vaga aceita", com fundamento e data; nada de "matriculado" |

Em cada caso, a 1280 × 900 e a 375 px: a largura de rolagem do documento é igual à da tela.
