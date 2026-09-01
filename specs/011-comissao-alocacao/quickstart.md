# Fase 1 — Como demonstrar e validar

**Feature**: 011 — Gestão da Comissão e Alocação por Etapa | **Data**: 2026-09-01

A condição de merge de cada entrega é o **percurso navegado**, não a contagem de testes (princípio
VI da Constituição). Esta feature tem uma particularidade: metade do que ela promete só se demonstra
**pela recusa**. Um percurso feliz que ninguém tentou furar não prova nada aqui.

São duas janelas, porque são dois atores e eles não compartilham sessão — mas, ao contrário da 009,
os dois entram pelo mesmo canal.

---

## Pré-requisitos

Quatro particularidades do ambiente, todas conhecidas, nenhuma da feature.

**PostgreSQL local precisa de `LC_ALL`, e a role padrão da máquina não existe no cluster** —
sobrescreva `DB_USER`.

**`TEST_DB_ENGINE=postgresql` é obrigatório e é o que se esquece.** Sem ela a suíte cai para SQLite
em memória **sem avisar**. Nesta feature o custo é preciso: as duas `UniqueConstraint` parciais — o
vínculo ativo único por Processo e a alocação ativa única por membro e Etapa — não são exercidas, e
`EC-001` e `EC-002` passam sem teste.

**Um banco de teste por worktree**, senão duas suítes em paralelo se destroem:

```bash
cd backend && TEST_DB_ENGINE=postgresql LC_ALL=en_US.UTF-8 DB_USER="$(whoami)" DB_NAME=ps011 \
  uv run pytest -q
```

**A interface administrativa exige o seletor de identidade ligado**; sem a variável, `/gestao/`
devolve 503. Ele continua recusado em produção — e nesta feature isso deixa de ser detalhe de
ambiente e vira o gate de `PC-005`: com o seletor ligado, qualquer pessoa se declara presidente.

```bash
cd backend && INTERFACE_SELETOR_IDENTIDADE=true DB_USER="$(whoami)" \
  uv run python manage.py runserver 8011
```

---

## O cenário-base

A demonstração de segurança da seção 49 da spec precisa de dois Processos e de duas Etapas no
primeiro. A seed já entrega um Processo publicado com duas Etapas; rode-a duas vezes:

```bash
cd backend && DB_USER="$(whoami)" uv run python manage.py seed_demo \
  --codigo PS-011-A --numero 11
cd backend && DB_USER="$(whoami)" uv run python manage.py seed_demo \
  --codigo PS-011-B --numero 12
```

Isso dá exatamente o que a seção 49 pede:

| Objeto | Papel na demonstração |
|---|---|
| Processo A, Etapa A1 | João é alocado |
| Processo A, Etapa A2 | João **não** é alocado — mesma comissão, mesmo Edital |
| Processo B, Etapa B1 | João não é sequer membro |

O Edital das duas seeds já nasce publicado e retificado, que é a precondição de `FR-032`: sem versão
vigente não há o que alocar.

---

## Entrega 1 — a vertical inteira, no caminho feliz e no infeliz

**Como gestor** (identidade `carlos`, papel Gestor), em `/gestao/processos/<A>/comissao`:

1. adicionar `maria` como **Presidente**;
2. adicionar `joao` como Membro;
3. ir a `/gestao/processos/<A>/alocacoes` e alocar `joao` à Etapa A1.

**Como membro** (segunda janela, identidade `joao`, sem papel de gestão), em
`/gestao/minhas-etapas`:

4. ver **A1, e só A1**, com o Edital nomeado;
5. abrir a atribuição e ler o contexto: Edital, período previsto, "Você está alocado nesta Etapa";
6. colar na barra de endereço a URL de A2, obtida da janela do gestor: **404**;
7. colar a URL de B1: **404**;
8. trocar um dígito do UUID de A1: **404**.

O que se deve ver: nada de candidato, nada de nota, nenhum botão `Avaliar` — a demonstração de
fronteira da seção 50 é feita nesta mesma tela, olhando o que **não** existe nela.

**A entrega só está pronta quando 6, 7 e 8 acontecem.** É o contrato arquitetural da feature.

### As duas recusas de governança, na mesma entrega

9. como gestor, num Processo com comissão **sem presidente**, tentar alocar: recusa nomeando o
   caminho (`FR-030`);
10. no Processo A, tentar rebaixar `maria` a Membro havendo alocação ativa: recusa, e o texto diz
    para designar outro presidente antes.

---

## Entrega 2 — gestão, visão e trilha

**Como gestor**, em `/gestao/processos/<A>/alocacoes`:

1. ver a organização **por Edital**, com Etapa A2 marcada como sem membros — e conferir que a marca
   não depende só de cor (`FR-076`);
2. alocar `maria` a A1 e A2, e ver a mesma pessoa em duas Etapas sem duplicar o vínculo;
3. remover `joao` **da Etapa** A1 e conferir, na outra janela, que `Minhas Etapas` de `joao` esvazia
   e a URL de A1 passa a devolver 404 — sem que ninguém tenha mexido em papel global;
4. remover `joao` **da comissão** e conferir que o rótulo da ação era outro (`SC-UX-002`).

**Como presidente** (identidade `maria`, **sem** o papel Gestor):

5. abrir `/gestao/processos/<A>/comissao` e alterar a função de alguém — a presidência autoriza
   sozinha (`SC-020`);
6. abrir `/gestao/minhas-etapas` e conferir que `maria` vê apenas as Etapas em que **está alocada**:
   presidir não injeta Etapa nenhuma (`FR-012`, `SC-008`).

**Como auditor**, na trilha do Processo:

7. conferir os cinco eventos, e conferir que o `permission` de cada um diz a base real —
   `comissao:gerir` nos atos de `carlos`, `comissao:presidir` nos de `maria` (`FR-016`).

---

## Entrega 3 — as bordas

1. **Dois Editais no mesmo Processo**: criar e publicar um segundo Edital em A, com uma Etapa de
   nome igual ao de A1. A tela nomeia o Edital antes da Etapa, e as duas são objetos distintos para
   alocação e para acesso (`EC-012`).
2. **Alocação órfã**: retificar o Edital de A removendo a Etapa A1 alocada. A Retificação é aplicada
   normalmente; a alocação não é apagada; `Minhas Etapas` deixa de listá-la; a tela do gestor a
   mostra como órfã, com a ação de removê-la (`FR-084`, `SC-017`, `EC-011`).
3. **Alterar sem substituir identidade**: retificar mudando o **nome** de A2. Ninguém fica órfão e
   quem está alocado continua alocado — é a metade do `FR-084` que costuma passar despercebida.
4. **Escopo institucional**: com identidade de outro escopo, abrir a comissão de A: **404**, e não
   403 (`SC-016`).
5. **Reenvio**: apertar duas vezes o botão de adicionar o mesmo membro, e de alocar a mesma Etapa.
   Nada duplica e nada quebra (`EC-001`, `EC-002`).
6. **Edital não publicado**: num Processo cujo Edital está em elaboração, abrir as alocações. A tela
   explica por que não há o que alocar, em vez de listar Etapas desabilitadas (`EC-014`).

---

## Verificação manual de acessibilidade

O que a suíte prende: marcação nativa, rótulo ligado ao campo, ausência de largura fixa, contraste
da paleta. O que **não** dá para prender está em [checklist-ux.md](./checklist-ux.md), e três itens
são desta feature e precisam ser percorridos à mão a cada entrega que mexa nas telas:

- percorrer constituir → designar presidente → alocar → remover **só pelo teclado**;
- conferir que "Remover desta Etapa" e "Remover da comissão" têm nomes acessíveis que se
  distinguem sem depender do contexto visual (`FR-077`);
- em 375 px, conferir que a organização por Etapa agrupa em vez de virar tabela horizontal, e que
  a marca de "sem membros" continua legível em escala de cinza.

---

## Como rodar os testes desta feature

```bash
cd backend && TEST_DB_ENGINE=postgresql LC_ALL=en_US.UTF-8 DB_USER="$(whoami)" DB_NAME=ps011 \
  uv run pytest tests/unit/comissoes tests/integration/comissoes tests/authorization \
                tests/interface tests/acceptance -q
```

Os quatro grupos, e o que cada um responde:

| Grupo | Responde |
|---|---|
| `unit/comissoes` | o resolvedor de Etapas, o invariante de presidência, a derivação de órfã |
| `integration/comissoes` | os comandos, as constraints parciais e a concorrência de `select_for_update` |
| `authorization` | as quatro negações: outro Processo, outra Etapa, outro escopo, sem vínculo |
| `acceptance` | o percurso da seção 49, ponta a ponta, com dois atores |

O teste de regressão que prova D-002 mora em `integration`: a Retificação que remove Etapa alocada
não pode falhar nem apagar alocação.
