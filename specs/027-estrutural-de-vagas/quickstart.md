# Quickstart — 027 · Estrutural de vagas

Como provar que a feature funciona, de ponta a ponta, **pelo canal do ator** — que é o que o
Princípio VI da Constituição exige.

São **dois** percursos, e os dois são obrigatórios: o que prova que o defeito deixou de nascer, e o
que prova que o acervo tem saída. Fechar só o primeiro entregaria metade da feature e deixaria sete
Editais reais inertes.

Este arquivo é guia de validação. Modelo e contratos estão em [data-model.md](data-model.md) e
[contracts/estrutural-de-vagas.md](contracts/estrutural-de-vagas.md).

---

## Antes de começar

### O banco desta worktree é próprio

Suítes paralelas disputam `test_processo_seletivo` e se derrubam:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 make DB_NAME=ps_demo_027 POSTGRES_USER="$USER" preparar
```

**A variável vai para o `make`, e não antes dele.** O `Makefile` faz `include .env` seguido de
`export`, e `include` sobrepõe variável de ambiente: `DB_NAME=ps_demo_027 make preparar` prepara o
`ps_demo_016` que está no `.env`, sem avisar, e a suíte desta worktree derruba a de outra. Fora do
`make` — `manage.py` chamado direto, como nos blocos abaixo — o prefixo é a forma certa.

`preparar` são **três** passos nesta ordem — provisionar, migrar, provisionar de novo. A segunda
passada concede privilégio sobre as tabelas que as migrations acabaram de criar; se ela disser
`0 de N protegidas`, ela não rodou.

No macOS com PostgreSQL do Homebrew, `LC_ALL` não é opcional.

### Antes de investigar qualquer erro estranho

```bash
cd backend && DB_NAME=ps_demo_027 uv run python manage.py migrate --check
```

Esta feature **não acrescenta migration nenhuma**. Se `migrate --check` acusar algo, é ambiente, e
não o diff.

### O servidor

**Acrescente** uma entrada ao `.claude/launch.json` — sem reescrever o arquivo, que é versionado e
carrega as entradas de outras sessões:

```json
{
  "name": "vagas-027",
  "runtimeExecutable": "sh",
  "runtimeArgs": ["-c", "cd backend && LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_demo_027 POSTGRES_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver 8027"],
  "port": 8027
}
```

Sem `INTERFACE_SELETOR_IDENTIDADE=true` a `/gestao/` devolve 503. O endereço é `localhost:8027` —
`127.0.0.1` devolve `DisallowedHost`.

### A demonstração

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DB_NAME=ps_demo_027 POSTGRES_USER=$USER uv run python manage.py seed_demo
```

**Semeie duas vezes ao longo da validação**: uma com o `seed_demo` de hoje, que produz o acervo no
estado do defeito e é o insumo do Percurso B, e outra depois da `FR-338`, que é o que o Percurso C
confere. Documento publicado não se regenera — mudou o renderizador, re-semeie.

---

## Percurso A — o defeito deixa de nascer

Pela interface administrativa, com o papel de quem elabora.

| # | Ação | O que tem de acontecer | Requisito |
|---|---|---|---|
| A1 | Abrir um Perfil novo e declarar 2 vagas imediatas, sem Modalidade nenhuma | não existe segundo campo para a mesma quantidade, e não existe bloco "Quadro de vagas" | `FR-316`, `UX-040` |
| A2 | Gravar e reabrir | o Perfil tem linha geral de 2, e ela sobreviveu à gravação com a mesma identidade | `FR-318`, `T-001` |
| A3 | Ir ao Cronograma, gravar, e voltar aos Perfis | a linha geral continua lá — a travessia que apaga o que não é reenviado não a alcança | `FR-318` |
| A4 | Ir à etapa 9 | o bloco do Perfil mostra o total **e** o quadro, lado a lado; nada pendente | `FR-326`, `UX-043` |
| A5 | Publicar e abrir a Ocupação no recorte da ampla concorrência | há quantidade declarada a apurar, e ela é 2 | `SC-105` |
| A6 | No mesmo Perfil, acrescentar a Modalidade PPI | o bloco do quadro **aparece agora**, com a linha geral já preenchida, e com frase visível dizendo por que ele apareceu | `FR-321`, `UX-041` |
| A7 | Declarar PPI 1 e deixar a geral em 2 | a submissão é recusada: soma 3 contra total 2, excesso de 1, dito em números | `025`, `FR-177` |
| A8 | Corrigir a geral para 1 e ir à etapa 9 | passa, e o quadro aparece completo | `FR-321` |
| A9 | Acrescentar a Modalidade PPP e não lhe dar linha | advertência nomeando PPP e dizendo que aquele recorte não terá quantidade a apurar; **não** bloqueia; a etapa 9 deixa de dizer que nada está pendente | `FR-324`, `FR-327`, `UX-044` |
| A10 | Confirmar a publicação | a confirmação repete a advertência, em números | `FR-328` |
| A11 | Num Perfil que declara uma Modalidade chamada "Ampla concorrência" sem apontá-la como tal | advertência **própria**, distinta da de A9 | `FR-325` |
| A12 | Apontá-la, e remover a PPI e a PPP | a linha geral volta a ser o total, e a tela diz que voltou | `FR-322` |

---

## Percurso B — o acervo tem saída

O insumo é o acervo semeado **antes** da `FR-338`: Editais publicados que declaram vagas imediatas e
nenhuma linha.

| # | Ação | O que tem de acontecer | Requisito |
|---|---|---|---|
| B1 | Abrir a Ocupação de um Edital do acervo | a frase de ausência continua verdadeira **e** nomeia o ato que declara a quantidade e o Perfil | `FR-332`, `UX-045` |
| B2 | Abrir a Convocação do mesmo | idem | `FR-332` |
| B3 | Abrir a supervisão do Processo | um sinal por Edital afetado, dizendo quantos recortes ficam sem quantidade, com destino para a Retificação | `FR-331`, `UX-046` |
| B4 | Seguir o destino e retificar **só a descrição** do Edital | o ato passa. Ausência de linha geral não prende Retificação nenhuma | `FR-323`, `T-003` |
| B5 | Retificar acrescentando a linha geral com o total publicado | o ato passa e a Retificação é publicada | `FR-328`, `025 FR-171` |
| B6 | Reabrir a Ocupação | agora há quantidade declarada a apurar | `SC-109` |
| B7 | Conferir a ordem já emitida e o resultado já publicado | inalterados | `FR-334` |
| B8 | Retificar o total de vagas de um Perfil que já tem linha geral e nenhuma lista reservada, mexendo só no total | recusado, com os dois números ditos | `FR-335` |
| B9 | Repetir B8 num Perfil **sem** linha geral | passa, com advertência que nomeia o ato que resolve | `FR-335` |
| B10 | Conferir o resumo canônico dos Editais que ninguém retificou | idêntico ao de antes da feature | `FR-333`, `SC-110` |

---

## Percurso C — a demonstração deixa de ensinar o defeito

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DB_NAME=ps_demo_027 POSTGRES_USER=$USER uv run python manage.py seed_demo
```

| # | O que conferir | Requisito |
|---|---|---|
| C1 | Os três Editais publicam quadro, e a Ocupação apura quantidade em cada recorte publicado | `FR-338`, `SC-107` |
| C2 | Ao menos um Perfil reparte por lista reservada, e ao menos um não declara lista reservada nenhuma | `FR-339` |
| C3 | Onde há Modalidade homônima da ampla concorrência, ela está apontada | `FR-339` |
| C4 | A Convocação tem quem chamar dentro da faixa | `SC-107` |

---

## Verificação

```bash
cd backend && LC_ALL=pt_BR.UTF-8 make DB_NAME=ps_demo_027 POSTGRES_USER="$USER" lint check test-pg
```

`test-pg`, e não `test`: sem o par de variáveis a suíte cai para SQLite, onde dezenas de casos
falham por motivo que nada tem com o diff. `lint` são **dois** passos — `ruff check` e
`ruff format --check` —, e rodar só o primeiro declara verde local e quebra no CI.

**Esta feature muda a conta esperada da suíte.** Toda fixture que compõe Perfil sem quadro passa a
publicar linha geral, e os testes que afirmam `vacancyTable: []` ou comparam resumo canônico mudam
de valor ([research.md](research.md), `T-008`). Cada queda é lida e decidida — nenhuma é silenciada.

E antes de empurrar, mesmo que só documentação tenha mudado:

```bash
cd backend && uv run pytest tests/test_citacoes_de_requisito.py
```
