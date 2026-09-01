# Rastreabilidade — 011: Gestão da Comissão e Alocação por Etapa

**Feature**: [spec.md](./spec.md) | **Tarefas**: [tasks.md](./tasks.md) | **Data**: 2026-09-01

O princípio V da Constituição exige que requisito crítico seja rastreável entre especificação,
plano, tarefa, implementação e teste. Esta é a ponta final: para cada requisito, **o teste que
falharia se ele fosse quebrado** — e não o teste que passa perto.

## Cobertura

| | |
|---|---:|
| Requisitos funcionais (FR) | 84 |
| Com teste que os prende | 79 |
| Declarativos, sem teste possível | 5 |
| Critérios de sucesso (SC) | 29 |
| Edge cases (EC) | 14 |

## Por onde procurar

Os testes citam o identificador do requisito na docstring ou no comentário, então a busca é
direta:

```bash
cd backend && grep -rn "FR-047" tests/
```

| Grupo | Onde vive |
|---|---|
| O resolvedor de Etapas e a fonte única | `tests/unit/comissoes/test_etapas_vigentes.py` |
| As duas bases de autorização | `tests/unit/comissoes/test_autorizacao.py`, `tests/authorization/test_gestao_da_comissao.py` |
| A permissão que não pode virar papel | `tests/unit/comissoes/test_permissao.py` |
| A sentinela do registrador | `tests/unit/comissoes/test_record_event.py` |
| As invariantes de banco | `tests/integration/comissoes/test_constraints.py` |
| O invólucro transacional e o estado final do Processo | `tests/integration/comissoes/test_comando.py` |
| Idempotência dos cinco comandos | `tests/integration/comissoes/test_idempotencia.py` |
| Constituir, alterar, remover | `tests/integration/comissoes/test_adicionar_membro.py`, `test_remover_membro.py` |
| Alocar e desalocar | `tests/integration/comissoes/test_alocar.py`, `test_remover_alocacao.py` |
| A governança da presidência | `tests/integration/comissoes/test_presidencia.py` |
| A órfã e a regressão de D-002 | `tests/integration/comissoes/test_retificacao_com_alocacao.py` |
| A trilha e a base registrada | `tests/integration/comissoes/test_auditoria.py` |
| A corrida que zera a presidência | `tests/integration/comissoes/test_concorrencia.py` |
| A fronteira de escrita em runtime | `tests/integration/comissoes/test_fronteira_de_escrita.py` |
| **A demonstração de segurança (§49)** | `tests/authorization/test_acesso_a_etapa.py` |
| **Os dois eixos de identidade (§32)** | `tests/authorization/test_eixos_de_identidade.py` |
| As quatro telas | `tests/interface/test_comissao.py`, `test_alocacoes.py`, `test_atribuicao.py` |
| **A fronteira com a 012 (§50)** | `tests/interface/test_atribuicao.py`, `test_fronteira_012.py` |
| O percurso inteiro | `tests/acceptance/test_comissao_e_alocacao.py` |
| A migration que não toca outros apps | `tests/migrations/test_migrations.py` |

## Os cinco requisitos sem teste, e por quê

Não são lacunas de cobertura: são requisitos que **nada nesta feature pode falsificar**, e
declará-los aqui evita que voltem como achado numa próxima análise.

| Requisito | Por que não há teste |
|---|---|
| **FR-023** | Descreve o que substitui FR-018 a FR-022 **quando o diretório existir**. Não há diretório; o requisito governa a feature que o integrar. |
| **FR-028** | Preserva a possibilidade de a 012 manter autoria histórica de avaliação. A 011 não implementa `Avaliacao`, então não há o que verificar — o que ela precisa é não impedir, e não impedir não se testa. |
| **FR-060** | Diz que a 011 **não** implementa ciclo de vida de conta institucional. Um teste disso seria um teste de ausência de código. |
| **FR-063** | Proíbe fundir os dois eixos por coincidência de CPF ou e-mail. Nada no código funde; `tests/authorization/test_eixos_de_identidade.py` cobre a consequência observável. |
| **FR-080** | Notificação está fora de escopo. A 011 registra a atribuição, e isso é o que os testes de auditoria prendem. |

## O que continua pendente de verificação humana

**T075** — o percurso manual do [checklist-ux.md](./checklist-ux.md) nas quatro telas: teclado do
início ao fim, leitor de tela nos anúncios de sucesso e recusa, e 375 px em aparelho real. A suíte
prende marcação nativa, rótulo associado, contraste da paleta e ausência de largura fixa; o resto
depende de alguém percorrer. **Não foi feito nesta entrega.**
