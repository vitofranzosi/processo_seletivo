# Implementation Plan: A data de nascimento entra no cadastro do candidato

**Branch**: `claude/gps-checklist-validation-66c108` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

## Summary

A identidade do candidato (`identidade.CandidateIdentity`) ganha `data_nascimento`, e o núcleo que
`falta_o_nucleo` confere passa a ser nome, CPF **e** data. Como as duas portas que já levam a "Seus
dados" (a volta do código de acesso e `portal:inscrever`) perguntam a `falta_o_nucleo`, o cadastro
antigo sem data é levado à mesma tela sem rota nova (FR-8302). A tela "Seus dados" ganha um campo; a
validação mora em `credenciais.recusas`, ao lado da do CPF; a data congela com o CPF na primeira
inscrição enviada (D-001), pela mesma `cpf_congelado`.

A `Inscricao` ganha `data_nascimento`, gravada **no envio**, dentro da mesma `compare_and_swap` que
muda o status (FR-8308). O rascunho não precisa da coluna: o valor congelado é o do cadastro no
instante do ato, que é o que "acompanha o rascunho, congela no envio" significa. O envio recusa
quando o cadastro não tem data (FR-8303), e a revisão mostra a data entre os dados "dos seus dados",
com o caminho para corrigi-la.

Na gestão, o detalhe da inscrição ganha a ação "Conferir identidade" (D-002): um `POST` com motivo,
sob a mesma permissão e o mesmo escopo do detalhe (`inscricao_para_consulta`), que responde uma
página privada com o CPF completo e a data congelados na inscrição e grava `CONFERIR_IDENTIDADE` na
trilha — com o motivo, sem os valores. O requerimento de matrícula nasce com a data do cadastro
(D-003), em `abrir_rascunho`.

## Technical Context

**Language/Version**: Python 3.13, Django 5 (monólito existente)
**Primary Dependencies**: nenhuma nova
**Storage**: PostgreSQL; duas migrations de coluna anulável — `identidade/0005` e `inscricoes/0009`
**Testing**: pytest contra PostgreSQL (`make test-pg`); as histórias pelo cliente de teste do Django;
um caso no navegador para o campo no celular (UX-1000) se o grupo `navegador` estiver presente
**Target Platform**: servidor Linux; portal e gestão no navegador, celular incluído
**Project Type**: web, renderização no servidor, sem JavaScript novo
**Performance Goals**: nenhuma consulta nova na jornada do candidato além da leitura da identidade
que o envio já faz; a conferência é uma página sob demanda
**Constraints**: CSP sem inline (estilo em folha); a enviada é imutável pelo gatilho da
`inscricoes/0007`, e a coluna nova só é escrita na transição RASCUNHO→SUBMETIDA; nenhum dado pessoal
na trilha (FR-8311, FR-8316); a data não decide identidade em caminho nenhum (FR-8310)
**Scale/Scope**: dois modelos, uma tela do portal, a revisão, uma ação na gestão, o requerimento;
fixtures de candidato e o `seed_demo`

## Constitution Check

| Princípio | Como esta feature o respeita |
|---|---|
| I. Linguagem ubíqua | "data de nascimento" e "conferir identidade", sem jargão; o candidato lê "Seus dados" como hoje |
| II. Publicação é ato imutável | a enviada guarda a data do dia do envio e não muda; as enviadas antes ficam sem ela (FR-8304); a coluna nasce anulável por `ADD COLUMN`, sem tocar linha |
| II. Nada é excluído | só acréscimo de coluna; nenhum dado sai |
| III. Proteção de dados | finalidade dita na coleta (FR-8314); minimização: a data não vai ao comprovante nem à área pública, e na gestão só aparece por ato com motivo (D-002); trilha referencia e não copia (FR-8316) |
| III. Negar por padrão | a conferência reusa `CONSULTAR` e o escopo do Edital; sem permissão, 404 como o detalhe (FR-8317), com linha no inventário de negativas da `033` |
| IV. Regras explícitas | a recusa do envio é do comando (`enviar_inscricao`), e a tela só a antecipa |
| V. Rastreabilidade | `rastreabilidade.md` cobre FR-8300 a FR-8318, SC-2900 a SC-2907, UX-1000, UX-1001 e cada caso-limite |
| VI. Completude de jornada | as três histórias têm caminho de ida e volta: falta a data → informa → volta à vaga ou ao envio |

Sem violação.

## Project Structure

### Documentation (this feature)

```text
specs/180-data-de-nascimento-no-cadastro/
├── spec.md
├── plan.md               # este arquivo
├── research.md           # as decisões técnicas
├── data-model.md         # as duas colunas e as regras
├── contracts/
│   ├── portal.md         # "Seus dados", a revisão e o requerimento
│   └── gestao.md         # a ação "Conferir identidade"
├── quickstart.md         # o roteiro de verificação
├── tasks.md              # (speckit-tasks)
├── rastreabilidade.md    # (na implementação)
└── checklists/requirements.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── identidade/
│   ├── models.py                         # CandidateIdentity.data_nascimento
│   ├── migrations/0005_data_nascimento.py
│   └── application/credenciais.py        # falta_o_nucleo, recusas, gravar_nucleo, data_congelada
├── inscricoes/
│   ├── models.py                         # Inscricao.data_nascimento
│   ├── migrations/0009_data_nascimento.py
│   ├── domain/pessoais.py                # validar e ler a data (dd/mm/aaaa)
│   └── application/submissao.py          # recusa sem data; grava no ato
├── portal/
│   ├── identidade.py                     # IdentidadeDoCandidato.data_nascimento
│   ├── views.py                          # meus_dados; dados da revisão
│   ├── templates/portal/meus_dados.html
│   └── static/portal/portal.css          # se o campo pedir regra nova
├── requerimentos/application/preencher.py  # abrir_rascunho preenche a data (D-003)
├── interface/
│   ├── views.py                          # conferir_identidade (POST)
│   ├── urls.py                           # inscricoes/<id>/conferir-identidade
│   ├── templates/interface/inscricao_detalhe.html     # o formulário do motivo
│   └── templates/interface/conferencia_de_identidade.html
└── management/commands/seed_demo.py (onde estiver)   # identidades com data

backend/tests/
├── fixtures/candidato.py                 # registrar() grava uma data padrão
├── unit/identidade/test_data_de_nascimento.py
├── integration/inscricoes/test_envio_sem_data.py
├── portal/test_seus_dados_com_nascimento.py
├── interface/test_conferencia_de_identidade.py
├── unit/requerimentos/test_requerimento_com_a_data.py
└── migrations/test_migrations.py         # contagem por app sobe (identidade e inscricoes)
```

**Structure Decision**: o monólito existente; nenhum app novo. A conferência mora em `interface`
porque é tela da gestão, e sua regra (o que revelar, a quem) mora em `inscricoes/application`,
ao lado de `inscricao_para_consulta`, que já decide o mesmo escopo.

## Riscos e como medi-los

- **A regra nova quebra fixtures em bloco.** Toda identidade de teste sem data passa a "faltar o
  núcleo", e todo envio de teste passa a ser recusado. É uma causa só, nas fixtures (`registrar` e as
  que constroem `CandidateIdentity` à mão) — conserta-se a fixture, e não a regra. Rodar a suíte
  inteira logo depois de ligar a recusa e agrupar as falhas por mensagem.
- **O gatilho da enviada.** A coluna nova é escrita só na transição do envio, quando `OLD.status` é
  RASCUNHO; nenhuma escrita depois. Um teste prende que atualizar a data numa enviada é recusado
  pelo banco.
- **Vocabulário e folha.** Classe nova no template exige regra na folha; texto novo no portal passa
  pelas varreduras de vocabulário. Rodar `tests/interface` e `tests/portal` antes da suíte.
- **Negativa nova.** A conferência responde 404 sem permissão: linha no inventário da `033`.

## Complexity Tracking

Nenhuma violação a justificar.
