# Implementation Plan: Estrutural de vagas — uma declaração só

**Branch**: `claude/vagas-publicacao-apuracao-2753fa` | **Date**: 2026-09-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/027-estrutural-de-vagas/spec.md`

---

## Summary

A quantidade de vagas de um recorte passa a ser declarada **uma vez**. Enquanto o Perfil não declara
lista reservada, a linha geral do quadro é materializada a partir de "Vagas imediatas" e o bloco
"Quadro de vagas" não é desenhado; declarada a primeira lista reservada, o bloco aparece com a linha
geral já preenchida e pede a repartição. O que o sistema não conseguia dizer passa a ser dito: duas
advertências na composição e na Revisão, a Revisão mostrando total e quadro lado a lado, e a
Ocupação e a Convocação nomeando o ato que declara a quantidade em vez de terminarem em constatação.
O acervo publicado muda por Retificação, e quem supervisiona passa a ver quais Editais precisam
dela.

**A abordagem técnica cabe numa frase: não há estrutura nova em lugar nenhum.** O quadro é conteúdo
publicado desde o degrau 12, `generalCompetitionModalityId` desde o 13, a Retificação já acrescenta
linha a Edital publicado, a validação já distingue erro de advertência e já encaminha cada pendência
para a etapa que a resolve, e a supervisão já monta sinais por Edital com destino e alcance.

Isso decide o formato do plano: **nenhuma migration, nenhum degrau de schema, nenhum módulo novo,
nenhuma permissão nova.** O que muda é quem escreve um valor que a forma já admite, e o que o
sistema diz sobre ele. O risco não está na engenharia — está em três lugares nomeados na §*Ordem de
execução*: a identidade da linha derivada, o ato que a conferência está aferindo, e o alvo fora de
banda do htmx que hoje pode não existir.

**Duas coisas o plano encontrou.** A primeira está resolvida e entra: a conferência de igualdade da
`FR-161` da `025` **nunca roda** no formato de Edital mais comum, porque a completude conta também a
Modalidade declarada como ampla — que por norma não tem linha. Com a `FR-317` ela fecha, e sem
fechá-la esta feature deixaria viva, por outro caminho, a divergência que existe para eliminar
([research.md](research.md), `T-002`). A segunda é uma armadilha evitada: uma exigência impeditiva
escrita sem recorte de ato bloquearia **toda** Retificação de **todo** Edital do acervo (`T-003`).

---

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 5.2, Django REST Framework 3.16. **Nenhuma dependência nova**

**Storage**: PostgreSQL 16. **Nenhuma migration.** A tabela `LinhaDoQuadroDeVagas` já existe com as
duas constraints parciais de que esta feature depende — uma linha geral por Perfil, uma linha por
Modalidade —, e nenhuma coluna é acrescentada, alterada ou removida

**Testing**: pytest + pytest-django, contra PostgreSQL (`make test-pg`). Unidade em
`tests/unit/editais/`; contrato em `tests/contract/`; interface em `tests/interface/`; aceitação em
`tests/acceptance/`; integração em `tests/integration/` para o `seed_demo`

**Target Platform**: servidor web; interface administrativa server-side com htmx, sem SPA e sem build
de front

**Project Type**: monólito Django conduzido por especificação

**Performance Goals**: a derivação é uma passada sobre os Perfis da mesma carga que já é percorrida
para persistir; o sinal do acervo lê o conteúdo vigente que a supervisão **já** carrega por Edital.
**Nenhuma consulta nova por Perfil e nenhuma por Edital**

**Constraints**: nenhum byte de conteúdo publicado é reescrito; nenhuma leitura de conteúdo publicado
passa a inferir o que ele não diz; nenhuma advertência desta feature bloqueia submissão ou publicação

**Scale/Scope**: o maior caso do alvo continua sendo 7 Perfis × 4 linhas. O acervo varrido pelo sinal
é o dos Editais publicados de um Processo

---

## Constitution Check

*GATE: verificado antes da Fase 0 e reavaliado depois da Fase 1. Ambas as passadas: aprovado.*

| Princípio | Como a feature se posiciona | Veredito |
|---|---|---|
| **I — Linguagem ubíqua** | Nenhum termo novo. "Vagas imediatas", "Quadro de vagas", "ampla concorrência" e "lista de concorrência" são os que a tela e os Editais já usam; o plano só deixa de usar dois deles para a mesma coisa | ✅ |
| **II — Integridade normativa e imutabilidade** | É o princípio que **motiva** a feature, e literalmente: *"Vagas [...] NÃO DEVEM existir como dados independentes e divergentes"*. A fonte única passa a existir. Nada publicado é reescrito — sem migration e sem degrau, o acervo fica como está até que uma Retificação o alcance (`FR-333`), e a `FR-330` proíbe inferir na leitura o que o conteúdo não diz | ✅ |
| **III — Segurança e proteção de dados** | Nenhuma permissão nova e nenhum ator novo. O sinal do acervo herda a porta e a supressão por alcance que a supervisão já aplica; nada aqui toca dado pessoal — quadro é contagem de vagas, e a `FR-340` proíbe atribuir pessoa a linha | ✅ |
| **IV — Regras explícitas e consistência** | A derivação vive no domínio e é aplicada pelo command, não pelo serializer nem pelo template: é o que faz a `FR-316` valer para a API tanto quanto para a tela. As duas advertências são achados classificados pela mesma validação que já classifica todas as outras | ✅ |
| **V — Qualidade, rastreabilidade e simplicidade** | Cada FR tem cenário no [quickstart.md](quickstart.md). A simplicidade é o eixo: **zero migration, zero degrau, zero módulo novo**. O que o plano acrescenta de estrutura é uma função pura, uma espécie de sinal e um parâmetro de ato | ✅ |
| **VI — Completude de jornada** | O cenário demonstrável percorre os dois lados: compor e publicar um Edital que apura, e **retificar um do acervo até ele apurar** — os dois pela interface administrativa, sem shell, sem API e sem banco. A `FR-338` corrige a demonstração oficial, que hoje ensina o defeito | ✅ |

### Invariantes do domínio tocados

| Invariante da Constituição | Efeito |
|---|---|
| "Cada informação normativa estruturada DEVE possuir uma única fonte autoritativa" | passa a ser verdade para vagas, que é onde ela não era |
| "Editais, relatórios, telas e PDFs DEVEM derivá-los da fonte estruturada quando tecnicamente aplicável" | a linha geral passa a derivar do total declarado, que é a fonte |
| "Um Edital publicado NÃO PODE ser sobrescrito, apagado ou silenciosamente modificado" | nenhuma migration, nenhuma conversão, nenhuma inferência de leitura (`FR-330`, `FR-333`) |
| "Registros normativos NÃO DEVEM ser fisicamente excluídos" | nada é excluído. A re-derivação da `FR-322` reafirma a quantidade de uma linha do **rascunho**, e nunca alcança conteúdo publicado |
| "Entidades DEVEM possuir identificadores estáveis" | é a razão de a linha derivada ser persistida e não calculada na saída (`T-001`) |
| "APIs DEVEM ter contratos explícitos" | a forma não muda; o comportamento sim, e está em [contracts/estrutural-de-vagas.md](contracts/estrutural-de-vagas.md) |

**Sem violações. A tabela de Complexity Tracking fica vazia.**

---

## Project Structure

### Documentation (this feature)

```text
specs/027-estrutural-de-vagas/
├── plan.md              # Este arquivo
├── research.md          # Fase 0 — T-001 a T-011
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/
│   └── estrutural-de-vagas.md
├── checklists/
│   └── requirements.md
├── rastreabilidade.md   # Fase 9 — cada requisito, onde foi feito e onde é verificado
└── tasks.md             # Fase 2 — do $speckit-tasks, não deste comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── domain/
│   │   ├── perfis.py           # a derivação, como função pura (T-001, T-002)
│   │   └── validation.py       # o ato conferido, as duas advertências, a completude (T-002/3/4)
│   └── application/
│       └── draft.py            # aplica a derivação antes de persistir as linhas
├── publicacoes/application/
│   └── retificacoes.py         # confere pelo ato de Retificação; mostra o não impeditivo (T-003, T-006)
├── interface/
│   ├── forms.py                # o quadro do formulário sem o campo que não deve existir
│   ├── revisao.py              # total e quadro lado a lado (FR-326)
│   ├── supervisao.py           # a sexta espécie de sinal (T-005, UX-046)
│   ├── views.py                # o fragmento da Modalidade e o destino das pendências (T-007)
│   └── templates/interface/
│       ├── _perfil.html                 # o bloco do quadro condicionado à lista reservada
│       ├── _secao_do_quadro.html        # a seção, extraída para o fragmento poder entregá-la
│       ├── _linha_do_quadro.html        # a ajuda deixa de ser `.oculto` (UX-041)
│       ├── _modalidade_com_linha.html   # entrega a seção quando ela ainda não existe
│       ├── compor_revisao.html          # o par total × quadro
│       ├── ocupacao.html                # a segunda metade da frase (UX-045)
│       ├── convocacao.html              # idem
│       ├── retificacao_confirmar.html   # os achados não impeditivos
│       └── supervisao.html              # o sinal novo, se o template enumerar espécies
├── ocupacao/application/emissao.py      # a segunda metade da frase no ato (FR-332)
├── convocacao/application/convocar.py   # idem
└── processos/management/commands/seed_demo.py   # o quadro da demonstração (T-010)

backend/tests/
├── unit/editais/                # derivação, completude, advertências
├── contract/                    # o ato conferido; a forma publicada inalterada
├── interface/                   # composição, Revisão, htmx, supervisão, Retificação
├── acceptance/                  # os dois percursos do quickstart
└── integration/test_seed_demo.py
```

**Structure Decision**: monólito Django existente, sem diretório novo. Cada camada recebe exatamente
a sua parte: a regra no domínio, a aplicação no command, a fala na interface.

---

## Ordem de execução

A ordem importa porque três passos, feitos fora de lugar, produzem defeito silencioso.

**1. A derivação, no domínio e no command.** Função pura em `editais/domain/perfis.py`, aplicada por
`replace_draft`. É o passo que torna a linha geral real, e tudo o que vem depois depende dela
existir.

> **Armadilha 1 — a identidade.** A linha derivada tem de nascer com identidade preservada entre
> gravações. `replace_draft` apaga e recria o rascunho inteiro: uma linha que ganhasse `uuid4()` a
> cada POST seria inalcançável pela Retificação e faria o resumo canônico mudar sem o conteúdo
> mudar. O `id` recebido é preservado; quando não há, nasce um e **viaja no formulário como campo
> oculto** a partir daí.

**2. A completude que passa a contar a ampla declarada.** `_coerencia_do_quadro_de_vagas`. Feito
depois da derivação, porque é a derivação que dá à conferência o que conferir.

**3. O ato conferido.** O parâmetro em `validate_for_publication`, e a exigência impeditiva da linha
geral só no ato de publicação.

> **Armadilha 2 — o acervo preso.** `retificacoes.py` afere o conteúdo produzido com
> `blocking_findings(validate_for_publication(content))`. Escrever a exigência sem o recorte do ato
> bloquearia toda Retificação de todo Edital do acervo, inclusive as que nada têm com vagas. O teste
> que fixa isso — retificar a descrição de um Edital sem quadro e ver o ato passar — entra **junto**
> com a exigência, e não depois.

**4. As duas advertências**, com destino para as etapas que as resolvem.

**5. A composição.** O bloco condicionado, o fragmento htmx e a ajuda que deixa de ser `.oculto`.

> **Armadilha 3 — o alvo fora de banda.** Com o bloco condicionado, `#quadro-{{ indice }}` deixa de
> existir no Perfil sem lista reservada. O `hx-swap-oob` que hoje entrega a linha não acha o alvo,
> não erra, e a linha se perde. O fragmento passa a entregar a seção inteira na primeira vez.

**6. A Revisão**, lado a lado.

**7. As duas frases que terminavam em constatação** — Ocupação e Convocação, no ato e na tela.

**8. O sinal do acervo** na supervisão.

**9. A conferência da Retificação** mostrando o não impeditivo.

**10. A demonstração.** `seed_demo` por último, porque é quem prova que os nove anteriores se
encontram.

**11. A suíte inteira.** O passo 1 muda o conteúdo publicado de todo Edital composto por fixture sem
quadro (`T-008`). A conta é esperada e é paga aqui, de uma vez, com cada queda lida — e não
silenciada.

---

## Complexity Tracking

> Sem violações da Constituição. Nada a justificar.
