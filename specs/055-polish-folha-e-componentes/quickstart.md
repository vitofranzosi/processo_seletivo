# Quickstart — como repetir a medição da 055

## 1. O banco e o servidor

```bash
LC_ALL=pt_BR.UTF-8 createdb -T ps_polish_audit ps_055_polish
```

Se `ps_polish_audit` não existir: `createdb`, `make preparar` e `seed_demo` num banco novo, com o
mesmo nome.

Servidor numa porta livre, com o seletor de identidade e o portal de demonstração ligados — uma
entrada acrescentada ao `.claude/launch.json` e revertida antes do commit (o arquivo é versionado):

```bash
cd backend && DB_NAME=ps_055_polish DB_USER=$USER DB_RUNTIME_USER=$USER \
  INTERFACE_SELETOR_IDENTIDADE=true PORTAL_IDENTIDADE_DEMO=true \
  uv run python manage.py runserver 8055
```

Identidade: `ana.gestora` com todos os papéis. Janela: 1280 × 900.

## 2. As telas e o que medir

| Tela | Caminho (Edital, no seed) | Medida |
|---|---|---|
| Corte | 51/2026, marco `…0051-…a1`, `/corte` | cada valor da faixa dentro do bloco do seu rótulo |
| Ocupação | 51/2026, marco `…a1`, `/ocupacao` | `display` da seção do recorte; os quatro blocos |
| Inscrições | 51/2026, `/inscricoes` | altura de cada `tbody tr` |
| Assistente | 76/2027, `/compor/cronograma` e `/compor/revisao` | altura dos itens de `.navegacao-etapa` |
| Distribuição | 01/2026, Etapa `…0001-…d1` | `top` do select, do input e do "Filtrar" |
| Comissão | Processo 2026, `/comissao` | largura do Identificador; alturas do filtro |
| Matrículas | 51/2026, `/matriculas` | altura de "Ver o que sairá vazio" |
| Convocação e Processo | 51/2026 `…a1/convocacao`; Processo 2026 | `font-size` de todo h2 e h3 |
| Visão Geral | `/gestao/visao-geral` | altura de input e select |
| Ordem do marco | 51/2026, marco `…a1` | `text-align` da pontuação |
| Seleção (portal) | `/selecoes/<Edital 01/2026>/` e `/selecoes/<Edital 26/2026>/` | `top` do Cronograma contra o das Vagas |
| Requerimento (portal) | Minhas inscrições → Continuar inscrição → Preencher o requerimento, **por cliques** | largura do Telefone; alturas; desenho de "Guardar e continuar depois" |

## 3. O teto

```bash
cd backend && set -a && . ./.env && set +a && TEST_DB_ENGINE=postgresql DB_RUNTIME_USER=$POSTGRES_USER \
  DB_NAME=ps_055 uv run pytest tests/performance/test_escala_da_mesa.py -k distribuicao_nao_cresce
```

Para ler o número, e não só o veredito, troque a asserção por um `print` numa cópia temporária do
arquivo — o procedimento de [D-001](research.md).

## 4. A suíte

```bash
cd backend && make lint check test-pg DB_NAME=ps_055
```
