# Quickstart: Elaboração Completa do Edital

**Feature**: `006-elaboracao-completa-edital` | **Fase**: 1 | **Data**: 2026-08-30

Como validar cada entrega, e como demonstrar a feature inteira. Cada seção diz o que fazer e **o que
precisa acontecer** — o resultado exato, não "deve funcionar". As decisões estão em
[research.md](./research.md), a forma em [data-model.md](./data-model.md) e o comportamento
observável em [contracts/elaboracao.md](./contracts/elaboracao.md).

Esta feature é a primeira sob a Constituição 1.1.1: **nenhuma entrega está pronta sem cenário
demonstrável no canal do ator**. Aqui, o navegador.

## Pré-requisitos

A `005` integrada — a `main` a partir de `829b850`.

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_NAME=processo_seletivo_test DB_USER=$USER DB_PASSWORD= uv run pytest
```

Esperado antes de começar: suíte verde. No PostgreSQL fica um ignorado —
`test_database_permissions.py`, cuja recusa por vendor só existe fora do PostgreSQL.

Para navegar:

```bash
cd backend && uv run python manage.py seed_demo && uv run python manage.py runserver
```

O seed percorre o fluxo normativo real com atores distintos, de modo que a segregação de funções e a
auditoria ficam verdadeiras. A interface pede identidade na entrada; é assim que se troca de ator
durante a demonstração.

---

## O defeito que a Entrega 4 fecha, antes de corrigi-lo

Vale rodar primeiro. É a linha de base, e mostra por que a US3 não é "trocar a caixa de texto por um
formulário".

O seed cria uma modalidade `PPP` com Regra Normativa de 20% pela via do command. Abra o Edital em
elaboração, vá a qualquer etapa do assistente e **salve sem mudar nada**. Depois:

```bash
cd backend && uv run python manage.py shell -c "
from processo_seletivo.editais.models.perfis import ModalidadeConcorrencia
for m in ModalidadeConcorrencia.objects.all():
    print(m.code, m.id, getattr(m, 'regra_normativa', None))
"
```

Esperado **hoje**: as regras sumiram e os identificadores das modalidades mudaram. Esperado depois
da Entrega 4: regras intactas e identificadores idênticos aos de antes do salvamento.

---

## Entrega 1 — Fluxo sem becos sem saída

**No navegador**, com pelo menos um Processo já cadastrado:

1. Abrir o painel. A ação `Novo Processo Seletivo` está visível — não apenas quando a lista está
   vazia.
2. Criar um segundo Processo e entrar no seu Edital.
3. Abrir a etapa `Identificação`, alterar o título, salvar. A alteração persiste, e a pendência de
   título deixa de aparecer como não corrigível.
4. No Cronograma, mover o terceiro Evento para a primeira posição, salvar e recarregar. A ordem
   persiste.
5. Abrir um Edital publicado. Há acesso direto ao documento.

**Verificação que o navegador não mostra**: os identificadores dos Eventos não mudaram ao reordenar.

```bash
cd backend && uv run python manage.py shell -c "
from processo_seletivo.editais.models.cronograma import EventoCronograma
print([(str(e.id)[:8], e.order, e.type) for e in EventoCronograma.objects.order_by('order')])
"
```

**Testes**: `tests/interface/` cobrindo botão presente na lista não vazia, alteração de
identificação com auditoria, reordenação preservando identidade, e link para o documento.

---

## Entrega 2 — Prévia do documento

1. No Edital em elaboração, alterar o título e o Cronograma, salvar.
2. Na etapa de Revisão, acionar `Visualizar Edital`.
3. O documento abre com as alterações. Todas as páginas trazem a marca de prévia; nenhuma traz hash,
   número de publicação ou afirmação de derivação de versão homologada.
4. Voltar e continuar editando.
5. Submeter. Entrar como quem homologa: o detalhe do Edital oferece `Visualizar Edital`.

**O que precisa acontecer, e não se vê na tela**: nenhum registro publicado foi criado.

```bash
cd backend && uv run python manage.py shell -c "
from processo_seletivo.publicacoes.models import Publicacao, RevisaoEdital, DocumentoPublicado
print(Publicacao.objects.count(), RevisaoEdital.objects.count(), DocumentoPublicado.objects.count())
"
```

Os três números antes e depois de visualizar são iguais.

**Teste de regressão obrigatório**: em modo publicado, os bytes gerados continuam idênticos aos de
antes da mudança. É o que garante que o modo não vazou para o documento oficial.

---

## Entrega 3 — Etapas de Avaliação

1. No assistente, abrir `Etapas de Avaliação`.
2. Criar `Análise de títulos` e `Prova didática`.
3. Mover `Prova didática` para a primeira posição.
4. Marcar `Prova didática` como eliminatória e classificatória, peso 2, nota mínima 7.
5. Vincular `Análise de títulos` a um Evento do Cronograma. As datas vêm do Evento; não há campo de
   data para digitar.
6. Salvar, recarregar: ordem e propriedades intactas, identificadores preservados.
7. `Visualizar Edital`: as duas Etapas aparecem na ordem definida.

**Verificação de contrato**: uma Retificação sobre um Edital publicado com Etapas endereça
`/stages/id=<uuid>/name` e é aceita, sem alteração da gramática. Endereçar `/stages/0/name` é
recusado por endereçamento posicional.

---

## Entrega 4 — Modalidades de reserva

1. Em um Perfil, configurar `PPI` com 20% e fundamento, e `PcD` com 5% e fundamento — em campos
   próprios, não em caixa de texto.
2. Salvar. Ir ao Cronograma e salvar de novo.
3. Recarregar o Perfil: as duas modalidades continuam lá, com percentuais, fundamentos e os mesmos
   identificadores.
4. `Visualizar Edital`: as duas aparecem no documento com percentual e fundamento.
5. Informar percentual `0` ou `120` e salvar: recusa com indicação de onde corrigir.

**Verificação que fecha a história**: repetir o comando de linha de base da seção inicial. Regras
intactas, identidades preservadas.

---

## Entrega 5 — Seções do Edital

1. Na etapa de conteúdo, ver as seções em ordem, distinguindo geradas de textuais.
2. Alterar o texto de uma seção institucional, salvar.
3. `Visualizar Edital`: a alteração aparece, junto das seções geradas a partir de Perfis, Cronograma,
   Etapas e modalidades.
4. Alterar o Cronograma e visualizar de novo: a seção correspondente reflete a mudança sem que nada
   tenha sido sincronizado à mão.

**Verificação de contrato**: sobre o Edital publicado, `REPLACE /sections/id=<textual>/content` é
aceito; `REPLACE /sections/id=<gerada>/content` é recusado por caminho inexistente — a seção gerada
não tem esse campo.

---

## A demonstração de ponta a ponta (SC-009)

Cerca de cinco minutos, dois atores, tudo no navegador.

| Passo | Ator |
|---|---|
| Painel → `Novo Processo Seletivo` | quem elabora |
| Identificação: número, ano, título, descrição | quem elabora |
| Perfis: um Perfil com requisitos, vagas e duas modalidades com percentual | quem elabora |
| Cronograma: três Eventos, com a ordem ajustada por botões | quem elabora |
| Etapas: duas Etapas, uma vinculada a Evento | quem elabora |
| Conteúdo: editar uma seção textual | quem elabora |
| Revisão: pendências resolvidas, `Visualizar Edital` | quem elabora |
| Submeter | quem elabora |
| `Visualizar Edital` no detalhe, depois homologar | quem homologa |
| Publicar | quem homologa ou um terceiro |
| Abrir o documento publicado pelo detalhe | qualquer um |

**Dois atores são obrigatórios**: a publicação é recusada quando a mesma pessoa elaborou, homologou
e publicou (`publicacoes/application/publish_edital.py:275-280`). Dois bastam — a recusa exige a
coincidência das três funções.

**O que confirma que a prévia valeu**: o documento publicado no último passo tem o mesmo conteúdo
normativo do que foi visualizado antes de submeter, agora com a declaração de integridade que a
prévia não tinha.

## Regressões a manter verdes

- Suíte inteira, com atenção a `tests/contract/` e `tests/interface/`.
- `test_openapi_conformance.py` depois de aplicar o delta do contrato.
- A verificação da `005` de que toda coleção do snapshot está declarada — ela é quem acusa
  `stages` ou `sections` esquecidas em um dos três registros.
- O documento publicado permanece imutável; nenhuma tabela append-only ganhou escrita.
