# Implementation Plan: Exportação de matrículas

**Branch**: `claude/spec-031-exportacao-de-matriculas` · **Spec**: [spec.md](./spec.md)

**Status**: plano completo. A implementação **não começa** antes de `Q-1` ser respondida — ver
*Riscos do plano*.

## Summary

Um app novo que **só lê**, e por isso não pode criar ciclo de importação com ninguém.

`matriculas/` recebe a população, junta o que a `029` coletou com o que a identidade, a oferta e a
classificação já sabem, aplica **um serializador por coluna** e escreve um `.xlsx` de uma aba. Junto
do arquivo sai o relatório de lacunas, e da geração fica um registro append-only.

**A decisão de arquitetura é o serializador por coluna.** A tentação é mapear os 34 campos por
dicionário e aplicar `legivel()` em cima — e ela é a forma exata de o erro entrar: `legivel()` serve
à leitura humana das duas telas da `029`, formata data em `dd/mm/aaaa` para quem lê e traduz código
em texto de gente. Metade disso é o que o destino quer, e a outra metade não. Trinta e quatro
funções pequenas, cada uma dizendo de onde tira, o que faz e o que devolve quando não há dado, são
mais longas de escrever e impossíveis de errar em silêncio (`FR-445`).

## Technical Context

**Linguagem e versões**: Python 3.13, Django 5.2, PostgreSQL 16 — sem mudança.

**Dependência nova, e é a única**: `openpyxl`. O projeto tem **três** dependências no total, e
acrescentar a quarta precisa de razão escrita.

A alternativa é montar o OOXML à mão: um `.xlsx` é um `.zip` com XML dentro, e gerar um de uma aba
cabe em duzentas linhas. **Recusada.** O que se ganharia é a contagem de dependências; o que se
arrisca é produzir um arquivo que o Excel abre — porque o Excel é tolerante — e que o importador
rejeita, num formato em que a única prova é o importador real. Escrever por conta própria trocaria
uma dependência madura por um bug que só aparece no destino, e o `FR-437` depende de detalhe
(formato de célula `@`) que é onde implementações caseiras erram primeiro.

**Escrita em fluxo**: `openpyxl` em modo `write_only`. Um Edital de porte real tem centenas de
convocados, não milhões — mas o modo de fluxo custa a mesma linha de código e tira a questão da
mesa.

**Armazenamento**: o arquivo **não é persistido**. Ele é gerado, entregue na resposta e descartado;
o que fica é o registro da geração. Guardar o binário criaria um acervo de dado pessoal concentrado
com política de retenção própria — decisão que esta feature não precisa tomar para funcionar.

**Ordem determinística** (`FR-446`): as linhas saem ordenadas por `CLASSIF_CURSO_FINAL` e, no
empate, por protocolo. Sem ordem explícita, duas gerações do mesmo conjunto saem em ordens
diferentes e o `SC-148` não fecha.

## Constitution Check

*GATE: verificado antes da Fase 0. Uma observação, nenhuma violação.*

| Princípio | Como a feature se posiciona | Veredito |
|---|---|---|
| **I — Linguagem ubíqua** | "Requerimento", "convocação", "modalidade" e "classificação" já são do domínio. O conceito novo é **lacuna** — a coluna que sai vazia com razão declarada —, e ele é do domínio desta feature, não jargão técnico | ✅ |
| **II — Integridade normativa e imutabilidade** | A exportação **lê**, e a `FR-449` escreve isso. O `code` da Modalidade publicada não é reescrito na saída (`D-003`): corrigir grafia de ato publicado é retificação, não formatação. O registro da geração é append-only (`FR-447`) | ✅ |
| **III — Segurança, proteção de dados e auditoria** | É o princípio que governa a feature. Permissão **nova** e própria (`matricula:exportar`), porque o arquivo concentra CPF, RG, filiação e endereço de toda a população numa peça só — ler um dossiê por vez é outro ato e tem outra permissão. O arquivo não é persistido. A `D-006` mantém a amostra real fora do repositório | ✅ |
| **IV — Regras explícitas e consistência** | A recusa mora na aplicação, e a tela só a antecipa. Quem chamar a geração sem permissão, ou com população incompleta, encontra a mesma recusa por qualquer caminho | ✅ |
| **V — Qualidade, rastreabilidade e simplicidade** | **Aqui está a observação.** A feature acrescenta uma dependência e 34 serializadores — é mais código do que o mínimo concebível. A justificativa de ambos está no *Technical Context*, e a alternativa mais curta foi nomeada e recusada por escrito. Nenhuma entidade nova além do registro de auditoria | ⚠️ ✅ |
| **VI — Completude de jornada** | Quatro histórias, e a que **relata a lacuna** é P1 junto com a que gera o arquivo: entregar o arquivo sem o relatório deixaria a jornada pela metade, porque quem recebe completaria as células vazias à mão | ✅ |

### Invariantes do domínio tocados

| Invariante | Efeito |
|---|---|
| "Dados pessoais DEVEM obedecer a necessidade, finalidade e minimização" | a finalidade é o destino, demonstrada coluna a coluna; os três campos eleitorais entram por ela (`D-007`) |
| "Nada é excluído" | o registro de geração é append-only; o arquivo não é guardado, e por isso não há o que excluir |
| "Entidades com ciclo de vida relevante DEVEM possuir estados e transições explícitos" | a geração **não tem ciclo de vida**: ela acontece ou é recusada. Nenhum estado novo |
| "APIs DEVEM ter contratos explícitos" | [contracts/arquivo-de-importacao.md](contracts/arquivo-de-importacao.md), as 34 colunas com serializador nomeado |

**A tabela de Complexity Tracking tem uma linha**, e ela é a dependência nova.

## Project Structure

```text
backend/processo_seletivo/matriculas/
├── __init__.py
├── apps.py
├── models.py                       # GeracaoDeArquivo — append-only (FR-447)
├── domain/
│   ├── nomes.py
│   ├── colunas.py                  # as 34, cada uma com origem, serializador e ausência
│   ├── flexao.py                   # ESTADO_CIVIL por SEXO — a tabela da D-004
│   └── lacuna.py                   # o que é lacuna, e a razão de cada uma
├── application/
│   ├── populacao.py                # quem entra, e a recusa de quem não declarou
│   └── exportar.py                 # o comando: permissão, montagem, registro
├── infrastructure/
│   └── planilha.py                 # openpyxl, write_only, formato @ em tudo
└── migrations/0001_geracao.py

backend/tests/
├── unit/matriculas/                # os 34 serializadores, a flexão, as lacunas
└── integration/matriculas/         # a geração ponta a ponta, a recusa, a reprodutibilidade
```

**Por que app novo, e não um módulo em `requerimentos/`.** A `029` custou uma sessão a um ciclo de
importação — `inscricoes → requerimentos → convocacao → inscricoes` —, resolvido com um módulo que
não podia importar `convocacao.application`. Um app que **ninguém importa** não pode entrar em ciclo
nenhum, e este não será importado por ninguém: ele é a ponta da leitura. A regra fica verificável
sozinha — se algum dia outro app importar `matriculas`, é sinal de que a feature deixou de ser ponta.

## Ordem sugerida

| Fase | O quê | Por que nessa ordem |
|---|---|---|
| 1 | `Q-1` respondida | o resto depende da forma que ela confirma |
| 2 | `029`: os três campos eleitorais (`D-007`) | a coluna precisa do dado antes de existir o serializador |
| 3 | As 34 colunas em `domain/colunas.py`, com teste unitário cada | é onde o erro silencioso mora; testá-las isoladas é barato |
| 4 | A população e as recusas | sem isso o arquivo sai com linha faltando |
| 5 | A planilha e o formato `@` | precisa das colunas prontas para ter o que escrever |
| 6 | O relatório de lacunas | depende das colunas saberem dizer por que estão vazias |
| 7 | Permissão, rota, tela, registro | a superfície, por último |
| 8 | Transversais e a verificação com o importador real (`SC-143`) | fecha contra o destino, não contra a leitura da planilha |

## Riscos do plano

| Risco | Efeito no plano | Mitigação |
|---|---|---|
| **`Q-1` sem resposta** | a Fase 1 não fecha, e o resto é construído sobre suposição | **não começar.** É a única dependência externa, e ela custa uma hora |
| `Q-2` e `Q-3` sem resposta | duas colunas ficam sem serializador definido | as demais 32 seguem; as duas viram lacuna declarada até haver resposta |
| A `029` não aceitar campo novo sem atrito | a Fase 2 empaca | são três colunas de texto num modelo que já tem 21 campos; o gatilho de imutabilidade não muda |
| `openpyxl` recusado na revisão | a Fase 5 refaz | a alternativa está nomeada, e o custo de trocá-la é uma camada só (`infrastructure/planilha.py`) |

## Complexity Tracking

| O quê | Por que é necessário | Alternativa recusada |
|---|---|---|
| Dependência `openpyxl` | o formato de destino é `.xlsx`, e o detalhe que importa — formato de célula `@` — é onde implementação caseira erra primeiro | montar o OOXML à mão: trocaria uma dependência madura por um defeito que só aparece no importador |
