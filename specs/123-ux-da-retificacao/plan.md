# Implementation Plan: Achar, conferir e voltar — o MVP de UX da Retificação

**Branch**: `claude/upbeat-haslett-9d4178` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/123-ux-da-retificacao/spec.md`

## Summary

Quatro mudanças dentro da tela Retificar que já existe, sem migration, rota, permissão ou regra
nova:

- **M1** — a busca «Encontrar» passa a ler, por campo, a seção, a legenda, o rótulo e o valor curto,
  e lista os campos com «Ir ao campo» (só `retificacao.js` e a folha da tela; R-008).
- **M2** — o servidor marca «na proposta» os cartões que o ato gravaria, pela mesma lista de
  Alterações que vai a `gravar`; cada linha do resumo carrega a referência opaca do campo; a barra
  diz os dois estados (R-005 a R-007).
- **M3** — a versão-base se descreve pelo que incorpora e pela situação de vigência, num fragmento
  usado em cinco telas; "Vigente hoje" sai (R-009, R-010).
- **M4** — «Ver o que vai mudar» chama a mesma conferência de conteúdo que a criação, extraída numa
  função sem escrita, e mostra os impeditivos com link ao cartão (R-001 a R-004).

## Technical Context

**Language/Version**: Python 3.12, Django; JavaScript sem build, servido como estático.

**Primary Dependencies**: as do projeto — Django, htmx (já carregado na tela), `pytest`,
`pytest-django`, `node --test` com o DOM mínimo de `tests/javascript/dom.js`, Playwright no grupo
opcional `navegador`.

**Storage**: PostgreSQL. **Nenhuma** tabela, coluna ou migration. Leituras novas: duas por tela
para a frase da base (R-009); a conferência de conteúdo faz as leituras que a criação já faz
(`topologia_publicada`, `ha_resultado_em` só para corte nascido).

**Testing**: `make lint check test-pg`; `node --test` via `tests/test_javascript.py`; jornada no
grupo `navegador` (`tests/navegador/`).

**Target Platform**: o navegador de quem opera a gestão, a 1280 e a 375 px.

**Project Type**: monólito web Django (gestão server-rendered + scripts estáticos).

**Performance Goals**: nada cresce com o tamanho do Edital. A conferência de conteúdo custa no
máximo **+4 consultas** sobre a conferência de hoje, para o mesmo formulário, no Edital ampliado; a
frase da base, no máximo **+4** por tela, constantes (R-009). Teste com
`django_assert_max_num_queries`.

**Constraints**: CSP sem `unsafe-inline` (estilo em `interface/static/interface/telas/retificar.css`,
script em `interface/static/interface/retificacao.js`); toda classe nova com regra na folha; o HTML
sem caminho normativo (a FR-019 da `002`); vocabulário em português.

**Scale/Scope**: Edital ampliado — 73 cartões, 364 campos, 26.517 px a 1280. Cinco telas tocadas:
Retificar (criação e edição), detalhe da Retificação, confirmar homologar/devolver/publicar.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o atende | Situação |
|---|---|---|
| I. Linguagem ubíqua | "versão-base", "proposta", "impeditivo", "Retificação nº N": termos que o domínio e a tela já usam. Nenhum termo técnico (`REPLACE`, caminho) chega a quem elabora. | ✅ |
| II. Integridade normativa e temporalidade | Nada muda no que se grava nem na base da composição (FR-3936). A conferência não escreve (FR-3943). A validação final continua obrigatória (FR-3944), e um teste prende a regra que muda com o tempo (SC-1180). A frase da base deixa de afirmar vigência que não há. | ✅ |
| III. Segurança e auditoria | Sem permissão nova; a conferência continua exigindo `retificacao:elaborar`; sem evento de trilha novo (conferir nunca foi ato). O HTML não ganha caminho. | ✅ |
| IV. Regras explícitas | Nenhuma regra nova: a conferência chama as funções da criação (R-001, R-002). A 1ª pergunta da auditoria fica com o usuário. | ✅ |
| V. Rastreabilidade e simplicidade | Uma função extraída, chamada pelos dois caminhos; sem segundo cálculo de diferença; matriz em `rastreabilidade.md`, com linha por caso-limite. | ✅ |
| VI. Jornada demonstrável | A jornada de navegador percorre os cenários A, B, C, D, E e G pela interface, sem shell (FR-3949). | ✅ |
| Interfaces: teclado, acessibilidade, prevenção de erro | Percurso só pelo teclado; marcas como palavra; contagens `aria-live=polite`; impeditivo antes do ato. | ✅ |

Nenhuma violação; *Complexity Tracking* vazio.

**Re-check depois do desenho:** o desenho continua sem violação. O único ponto de atenção é o R-001,
que mexe em `_apply_declared_changes`, caminho de toda criação e edição de Retificação: a tarefa
T004 é uma refatoração sem mudança de comportamento, provada pelas suítes de Retificação **antes** de
qualquer uso novo.

## Project Structure

### Documentation (this feature)

```text
specs/123-ux-da-retificacao/
├── spec.md
├── plan.md               # este arquivo
├── research.md           # R-001 a R-013
├── data-model.md         # as estruturas de tela (sem tabela nova)
├── contracts/
│   └── tela-retificar.md # o que cada tela promete: atributos, textos, links
├── quickstart.md         # como ver e medir
├── rastreabilidade.md    # FR/SC/caso-limite → tarefa → teste
├── checklists/
│   └── requirements.md
└── tasks.md              # do /speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── publicacoes/application/retificacoes.py      # conferir_conteudo, impeditivos_do_conteudo (R-001, R-002)
├── interface/
│   ├── retificacao.py                            # cartao_do_caminho, referencias_na_proposta,
│   │                                             # referências no resumo, descrever_versao_base (R-004–R-006, R-009)
│   ├── views.py                                  # _compor_retificacao (proposta, conferência),
│   │                                             # _ultima_versao_publicada, frase da base nas telas
│   ├── templates/interface/
│   │   ├── retificar.html                        # seção de impeditivos, colunas, «Ir ao campo», atributos da barra
│   │   ├── _retificacao_linha.html               # data-na-proposta e o selo
│   │   ├── _retificacao_{perfil,evento,anexo,linha_do_quadro,modalidade,criterio}.html  # id das linhas novas
│   │   ├── _versao_base.html                     # novo fragmento (R-009)
│   │   ├── retificacao_detalhe.html              # frase da base junto de «Antes»
│   │   └── retificacao_confirmar.html            # idem, homologar/devolver/publicar
│   └── static/interface/
│       ├── retificacao.js                        # busca por campo, lista, ir ao campo, duas frases
│       └── telas/retificar.css                   # regras das classes novas
backend/tests/
├── fixtures/edital_da_auditoria.py               # os dois Editais e a Retificação de vigência futura (R-011)
├── unit/publicacoes/test_conferencia_do_conteudo.py
├── unit/interface/test_cartao_do_caminho.py
├── interface/test_retificar_busca_marca_base.py  # HTTP: M2, M3, M4
├── interface/test_retificar_conferencia_impeditivos.py
├── javascript/retificacao.test.js                # casos novos da busca e das duas frases
└── navegador/test_jornada_da_retificacao_123.py  # R-012
```

**Structure Decision**: o monólito existente. Nenhum app, módulo de domínio ou rota nova; a única
função de domínio nova é uma extração (R-001).

## Desenho por item

### M4 — impeditivos na conferência (primeiro, porque mexe no caminho da criação)

1. Extrair `impeditivos_do_conteudo` e `conferir_conteudo` (R-001); reescrever
   `_apply_declared_changes` e `_assert_well_formed` sobre elas, **sem** mudar mensagem, código,
   status nem ordem. As suítes de Retificação inteiras são a prova.
2. Em `_compor_retificacao`, no ramo da conferência (POST sem `confirmar`), depois de `todas` e dos
   gestos: `alteracoes_da_proposta = proposta(todas)` (R-003) e
   `conferencia = conferir_conteudo(edital, conteudo_da_base, alteracoes_da_proposta)`. A conferência
   só roda com proposta não vazia e sem recusa anterior no mesmo envio. Também roda quando `gravar`
   recusa por conteúdo, para que a tela que volta traga a seção com os links (R-013).
3. Converter cada impeditivo em `{mensagem, destino}` com `cartao_do_caminho` (R-004); a recusa de
   guarda vira um item sem destino (a mensagem dela não tem caminho estruturado).
4. Template: seção `#impeditivos` antes do resumo (D-009), título "O que impede criar esta
   Retificação", a frase de FR-3944 e a lista; cada destino um link `href="#cartao-<ref>"` ou
   `#s-<secao>`.

### M2 — marca persistente e caminho de volta

1. `diferencas` acrescenta `cartao` e `campo` a cada item do resumo (R-006); as linhas novas ganham
   `id`.
2. `referencias_na_proposta(grupos, alteracoes_da_proposta)` (R-005) → `data-na-proposta` nos
   cartões e nas linhas novas que produziram Alteração; no GET da edição, sobre
   `alteracoes_declaradas(item)`.
3. O formulário leva o estado em atributos **depois** de `data-conferido` (R-007): `data-modo="edicao"`
   na edição; `data-enviado` em toda resposta a POST; `data-proposta="nao-conferida"` no GET da
   criação, `"recusada"` quando houve recusa e nenhuma proposta, senão `"conferida"` com
   `data-proposta-cartoes=N` e, na edição, `data-proposta-remocoes=K`.
4. `retificacao.js`: `recontar()` compõe as duas frases (FR-3930) num `span.estado-da-proposta`, depois da
   `span.contagem` de hoje; `aplicar()` considera `data-na-proposta` em «Só o que eu alterei»
   (FR-3931); «Ir ao campo»/«Ir ao cartão» das linhas do resumo usa o mesmo `irAoCampo` da busca.
   Sem script, as âncoras funcionam e a marca do servidor continua visível.

### M3 — a versão-base

1. Renomear `_versao_vigente` → `_ultima_versao_publicada` em `views.py` (o único uso é
   `_base_da_composicao`; o `_versao_vigente` de `inscricoes/` é outro e não muda).
2. `descrever_versao_base` e `_versao_base.html` (R-009). Contexto: `versao_base` em Retificar (a
   `base` da criação ou `item.base_snapshot` na edição), no detalhe e na confirmação.
3. Textos da R-010 e de contracts §1.1, §2 e §3; colunas «Na versão-base» / «No rascunho» (D-007);
   numeração "Retificação nº N" pelo `publication_order`, como o detalhe do Edital (D-006).

### M1 — busca por campo

1. `retificacao.js`: índice, normalização, palavras, os dois tipos de resultado, elegibilidade, limiar de 2, teto de 25, lista,
   `irAoCampo`, Enter (R-008). O `placeholder` passa a "campo, valor ou cartão — vagas, remuneração,
   Término…".
2. `retificar.css`: `.resultados-da-busca`, `.ir-ao-campo`, o "mostrando 25 de N" e o estado em
   375 px (a lista quebra linha; nada com largura fixa).

## Testes

| Camada | Arquivo | O que prende |
|---|---|---|
| Unidade (domínio) | `tests/unit/publicacoes/test_conferencia_do_conteudo.py` | `conferir_conteudo` devolve os mesmos impeditivos que a criação junta; a primeira guarda interrompe; não escreve (contagem de linhas antes e depois); os argumentos de `validate_for_publication` são os mesmos nos dois caminhos (R-002). |
| Unidade (tela) | `tests/unit/interface/test_cartao_do_caminho.py` | Os quatro passos de R-004; o `ADD` por identidade; remoção sem cartão na edição. |
| HTTP | `tests/interface/test_retificar_busca_marca_base.py` | `data-na-proposta` nos cartões certos (criação, edição GET e POST, gesto, remoção, linha nova, troca de arquivo como um cartão); `cartao`/`campo` em cada linha do resumo; atributos da barra; recusa sem marca; a frase da base nas três situações e nas cinco telas; ausência de "Vigente hoje"; base inalterada (`input[name=base]` igual ao de antes). |
| HTTP | `tests/interface/test_retificar_conferencia_impeditivos.py` | Quadro 3→4: impeditivo na conferência, link à 1ª linha, nenhuma Retificação; igualdade das frases com a recusa da criação para três formulários (quadro, Perfil sem denominação, Evento sem início); guarda antes dos achados (critério acrescentado inválido); edição sobre o ato fundido; Evento que vence entre conferir e criar (o relógio que `validate_for_publication` lê quando `agora` é `None` — `datetime.now(ZONA)` em `validation.py` — deslocado por `mock.patch`; o projeto não usa `freezegun`) e Resultado registrado entre conferir e criar: a criação recusa (SC-1180); orçamento de consultas. |
| JS | `tests/javascript/retificacao.test.js` | Normalização; várias palavras; limiar; elegibilidade (texto longo, número, data, Sim/Não fora); teto e "mostrando 25 de N"; Enter não envia e foca o 1º resultado; `irAoCampo` desesconde e foca; o valor digitado depois do carregamento é o buscado; as duas frases da barra em cada estado de `data-proposta`; «Só o que eu alterei» com `data-na-proposta`. |
| Navegador | `tests/navegador/test_jornada_da_retificacao_123.py` | Os sete casos de R-012. |
| Regressão | as suítes existentes | `tests/interface/test_retificar*.py`, `test_jornada_da_retificacao*.py`, `test_devolucao*.py`, `test_aplicar_a_todos_na_retificacao.py`, `test_retificacao_parada.py`, `tests/integration/publicacoes/` e `tests/contract/test_retificacoes_api.py`, sem asserção afrouxada; só os dois textos da R-010 mudam, para o texto novo. |

**SC-1174, enumerado.** No `edital_da_auditoria`: «vagas» → `Vagas imediatas` dos 2 Perfis e das 3
linhas do quadro; «remuneração» → `Remuneração` dos 2 Perfis; «prazo» → `Prazo em dias` de cada
marco com janela recursal e, como resultado de cartão, a Seção «Prazo de validade»; «requisito» →
`Requisitos de participação` dos 2 Perfis e, como resultado de cartão, a Seção «Requisitos gerais».
Nenhum termo lista os campos de um cartão só porque o nome dele casou. O teste computa a lista esperada da fixture pelas mesmas regras e a compara com a tela, e um
segundo teste conta os campos de texto longo achados pelo valor: zero.

## Verificação

```bash
cd backend && make lint check test-pg
```

Mais `uv sync --extra dev --extra navegador`, `uv run playwright install chromium` e
`make test-navegador` para a jornada visível. O passo a passo humano está em
[quickstart.md](quickstart.md), e a medição da segunda etapa também.

## Complexity Tracking

Nenhuma violação a justificar.
