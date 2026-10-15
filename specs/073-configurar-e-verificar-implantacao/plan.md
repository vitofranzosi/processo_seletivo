# Implementation Plan: Configurar, verificar e testar o correio e o Ollama na implantação

**Branch**: `claude/073-configurar-e-verificar` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: a spec da 073, com o recorte aprovado pelo usuário em 14/10/2026.

**Dependências**:

- o [#281](https://github.com/vitofranzosi/processo_seletivo/pull/281), que escreveu o §16.5 que esta
  feature incorpora;
- o [#282](https://github.com/vitofranzosi/processo_seletivo/pull/282), que traz a spec e a
  auditoria.

A branch nasce sobre a do #282 e recebe a do #281 por merge, como a `072` nasceu sobre a do #276.

## Summary

**Documentação, mais duas correções pequenas de código. Sem comando novo, sem modelo, sem
migration.**

O guia de implantação ganha uma seção única, a §10.4, que leva a TI de "preencher o `app.env`" a
"correio e Ollama comprovados". Ela usa só o que existe:

- o pré-voo `check --deploy`;
- exemplos de `shell -c` que leem a configuração sem imprimir segredo, testam conexão, segurança e
  conta do correio sem enviar, e consultam versão e modelos do Ollama sem inferência;
- o `sendtestemail`;
- a `verificar_servico_de_inferencia`.

Uma tabela curta liga a última linha de cada falha às causas possíveis, sem concluir por nenhuma.

O código muda em dois pontos:

- `production.py` recusa o backend SMTP com `EMAIL_HOST` vazio;
- a verificação do serviço de inferência separa "nenhum serviço configurado" de "serviço
  desconhecido".

## Technical Context

**Language/Version**: Python 3.13, Django 5.2. Markdown no guia e no README.

**Primary Dependencies**: nenhuma nova.

**Storage**: nenhuma mudança. A feature não lê nem grava o banco.

**Testing**: pytest + pytest-django, contra PostgreSQL (`make test-pg` com `DB_NAME` próprio).

**Target Platform**: a VM Ubuntu do guia de implantação, pelos scripts `ps-manage`.

**Project Type**: monólito web. O que esta feature entrega é procedimento de operação.

**Performance Goals**: não se aplica. Cada teste de conexão termina dentro do `EMAIL_TIMEOUT` (20 s)
ou do `ASSISTENTE_TEMPO_LIMITE_SEGUNDOS`.

**Constraints**:

- nenhum segredo na saída de nenhum exemplo;
- nenhum passo de conexão envia mensagem ou pede inferência;
- os exemplos rodam pelo `ps-manage`, como o usuário da aplicação, sem dependência a instalar.

**Scale/Scope**:

- uma seção nova no guia (§10.4), mais remissões no §16 e no §25;
- um parágrafo no README;
- dois arquivos de código, com uma regra e uma mensagem;
- três arquivos de teste, um deles novo.

## Constitution Check

| Princípio | Como a feature o atende |
|---|---|
| I. Linguagem ubíqua | Sem termo de domínio novo. A seção usa o vocabulário do guia |
| II. Integridade normativa | Não toca em ato publicado nem em regra de Edital |
| III. Segurança, dados e auditoria | Nenhum exemplo imprime segredo, e um teste verifica isso com segredos plantados (SC-621). A regra nova é recusa de inicialização, que é negar por padrão. Sem dado pessoal (LGPD na spec) |
| IV. Regras explícitas | A recusa nova nomeia a variável e a ação, como as demais |
| V. Rastreabilidade e simplicidade | Nenhum comando novo (D-002). Cada FR tem tarefa e verificação na matriz |
| VI. Jornada demonstrável | O ator é a TI, e o canal dela é o terminal do servidor. A jornada se demonstra por ele (quickstart, roteiro A) |

**Gate**: passa. Sem violação a justificar.

## Project Structure

### Documentation (this feature)

```text
specs/073-configurar-e-verificar-implantacao/
├── spec.md
├── plan.md               # este arquivo
├── research.md           # as decisões de forma, com as medições de 14/10
├── contracts/
│   └── secao-do-guia.md  # os passos, os exemplos e a tabela que a §10.4 promete
├── quickstart.md         # como validar
├── checklists/requirements.md
├── tasks.md              # /speckit-tasks
└── rastreabilidade.md    # FR/SC → tarefa → verificação
```

Sem `data-model.md`: a feature não tem entidade nem estado. A "Pendência" e o "Resultado de teste"
da primeira redação da spec saíram com o comando agregador (D-002).

### Source Code — arquivos afetados

```text
backend/config/settings/production.py                                      # FR-1660: a recusa nova
backend/processo_seletivo/duvidas/management/commands/verificar_servico_de_inferencia.py  # FR-1661
doc/implantacao-em-producao-ubuntu.md                                      # FR-1650 a FR-1657: a §10.4
README.md                                                                  # FR-1658
```

### Testes

```text
backend/tests/test_configuracao_producao.py         # EMAIL_HOST no ambiente mínimo, e os casos vazios
backend/tests/unit/duvidas/test_verificar_servico.py # serviço desconhecido × vazio
backend/tests/test_guia_configurar_verificar.py      # novo: o guia contra o código
```

O teste novo lê a §10.4 e prende três propriedades:

- toda variável dos blocos de exemplo é lida pelas settings;
- os exemplos de `shell -c`, executados com segredos plantados, não imprimem nenhum deles e
  terminam na linha esperada;
- toda última linha de erro que a tabela cita é a que o exemplo produz contra servidores falsos
  locais.

Os servidores falsos não entregam mensagem a ninguém.

## Riscos concretos

- **O ambiente mínimo da suíte não tem `EMAIL_HOST`.** A recusa nova derrubaria todos os casos de
  `test_configuracao_producao.py`, inclusive os de subprocesso. A correção é acrescentá-lo ao
  `AMBIENTE_MINIMO`, no mesmo commit da regra.
- **Instalações já implantadas sem `EMAIL_HOST`** deixam de subir. É o efeito desejado: hoje elas
  sobem e não entregam nada. A seção avisa disso no passo de pré-voo.
- **As mensagens de erro são do Python e do `smtplib`**, e podem mudar de versão. O teste que roda
  os exemplos contra servidores falsos acusa a mudança antes de o guia mentir.
- **O exemplo de `shell -c` vive no Markdown.** Se alguém o editar com aspas simples dentro, o
  `ps-manage` quebra. O teste o executa a partir do próprio guia, e não de uma cópia.

## Como cada jornada será verificada

| História | Verificação automática | Verificação manual |
|---|---|---|
| US1 — correio | os casos da regra nova; o teste do guia contra servidores falsos (conexão recusada, nome inexistente, silêncio, sem STARTTLS, conta recusada, aceita) | o quickstart, roteiro A, em homologação, com caixa da equipe |
| US2 — Ollama | a mensagem do serviço desconhecido; o teste do guia com um Ollama falso local (versão, modelo ausente, modelo presente) | o quickstart, roteiro B, contra a L4 quando houver acesso |

## Necessidade de ampliar escopo

Nenhuma. A recusa de `EMAIL_HOST` vale só para o backend SMTP (FR-1660). Backend de terceiros não
existe no projeto, e não é antecipado.

## Complexity Tracking

Sem violação a justificar.
