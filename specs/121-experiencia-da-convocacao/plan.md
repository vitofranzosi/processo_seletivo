# Implementation Plan: A experiência da convocação, incremento 1

**Branch**: `claude/121-plano` | **Date**: 2026-11-05 | **Spec**: [spec.md](spec.md)
**Input**: a spec da `121`, mergeada no #396 (`de5df85c`): FR-3858 a FR-3892, SC-1150 a SC-1164,
D-001 a D-012. Neste PR, a spec é revista na FR-3889, na FR-3891 e na D-009, e ganha a SC-1172.

> **A D-009 foi decidida sobre este plano.** A prova pedida não fechou: o histórico de implantação não
> identifica a versão exata do modelo usado em cada envio (R-001). O usuário escolheu a **opção A**:
> a comunicação emitida grava o nome do modelo e o SHA-256 dos arquivos que renderizaram o envio
> (R-009). A seção [*A decisão da D-009*](#a-decisão-da-d-009-a-gravação-da-versão-do-modelo)
> registra as três opções e o que a escolha muda.

## Summary

A convocação passa a abrir dizendo, nesta ordem, que a pessoa foi convocada, o que a etapa pede, até
quando, o que falta e onde começar. O plano faz isso com cinco mudanças, nenhuma delas em regra de
domínio:

1. **A chamada no portal.** O título por estado, a etapa, o cartão do prazo, o resumo, a ação, a
   ressalva e o andamento saem da projeção de obrigações da `118` (`portal/obrigacoes.py`), que já é
   pura. A projeção ganha campos, e o `convocacao.html` ganha a ordem nova. A correção aparece no
   cartão do prazo, e a linha *"Convocação substituída"* entra nos dados do ato.
2. **O prazo.** Uma função pura, `convocacao/domain/prazo_apresentado.py`, dá a data, a hora, o dia da
   semana e a contagem no fuso das settings, para o portal e o e-mail (R-003).
3. **O acesso.** Sem identidade na sessão, a view da convocação redireciona ao acesso antes de
   consultar o banco (R-004). Depois do código, a pessoa volta à convocação pela lista fechada de
   `_de_volta_a_vaga`, agora com três rotas (R-005).
4. **O envio.** A volta do envio aceito é `#confirmacao`, com o foco sem script, e a da recusa é o
   cartão do item (R-006). A convocação carrega os três scripts da inscrição. `envio.js` passa a valer
   também para formulário sem htmx (R-007).
5. **A mensagem.** HTML e texto, inicial e da correção, de quatro arquivos de modelo. Uma função pura
   escolhe o modelo e a variante dos registros já gravados (R-002). Na correção, a mensagem cita a
   **última mensagem enviada com sucesso** na cadeia (D-008). O envio continua no
   `comunicar.py`, a mesma situação declarada da FR-084.

6. **A versão do modelo.** Cada envio individual, inclusive o que falha, grava em
   `ComunicacaoEmitida` o nome do modelo e o SHA-256 das fontes dos dois arquivos que o
   renderizaram (FR-3889, R-009).

**Nenhuma rota, tabela, papel, estado, desfecho, comando ou situação de mensagem nova.** A única
coluna e a única migration são as do item 6 (FR-3891).

## Technical Context

**Language/Version**: Python 3.13, Django (monólito do repositório)
**Primary Dependencies**: as do projeto; nenhuma nova. Playwright no grupo opcional `navegador`
**Storage**: PostgreSQL. **Uma migration**: `ADD COLUMN modelo_da_mensagem` em
`convocacao_comunicacaoemitida`, com `default ""`, sem reescrever linha. As tabelas append-only
continuam 53, e a segunda passada continua `53 de 53`
**Testing**: pytest contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio); `node --test` para
`envio.js` e `arquivo.js`; jornadas no navegador com o grupo `navegador`
**Target Platform**: portal do candidato a 375 px e a 320 px, com zoom de 200 %; clientes de e-mail
(SC-1164, humano); CSP `'self'` sem `unsafe-inline`
**Project Type**: monólito web
**Performance Goals**: a convocação com a mesma contagem de consultas com 1 e com 6 itens, como
mede a `118`; zero consultas à inscrição, ao Edital e à convocação antes do redirecionamento sem
sessão (SC-1157)
**Constraints**:
- **CSP**: nenhum estilo nem script embutido no portal. A mensagem de e-mail não é página, e usa
  estilo inline. A varredura da CSP lê `portal/templates`, e por isso os modelos ficam em
  `convocacao/templates/` (R-002, contrato).
- **Varreduras**: as listas de vocabulário são literais, e os templates e modelos novos precisam
  entrar nelas (FR-3892).
- **Folha**: toda classe nova precisa de regra em `portal.css`.
- **FR-084**: o guardião das quatro situações. `EmailMultiAlternatives` só em `comunicar.py`.

**Scale/Scope**:
- uma função de domínio nova (`prazo_apresentado.py`) e uma pura de mensagem (`mensagem.py`);
- a projeção de obrigações estendida;
- três views do portal: `convocacao`, `apresentar_documento_da_convocacao` e `acesso`/`_entrar`;
- o envio em `comunicar.py`;
- quatro modelos de mensagem;
- um template e dois parciais do portal, as duas telas de acesso e um parcial da gestão;
- um script generalizado.

## Constitution Check

| Princípio | Leitura | Situação |
|---|---|---|
| I — linguagem ubíqua | *"convocação corrigida"*, *"prazo válido"*, *"enviamos"*; nada de *"novo prazo"*, *"prorrogação"*, *"recebida"*, *"aceito"* (FR-3751 da `118`, FR-3856 da `120`) | ✅ |
| II — imutabilidade e temporalidade | nada gravado muda; a escolha da mensagem é função de registros append-only e da versão citada (R-002); o prazo é apresentado no fuso das settings, com o instante gravado em UTC | ✅ |
| II — reprodutibilidade | a variante e a mensagem citada se reconstroem (R-002); a versão exata do texto fica gravada na comunicação, conferível contra o Git em qualquer commit (R-009) | ✅ |
| III — negar por padrão, IDOR | sem sessão, a resposta não depende do identificador (R-004); a titularidade é conferida a cada requisição; o destino é reconstruído (R-005) | ✅ |
| III — auditoria | a trilha continua *"enviada"*; a leitura da convocação continua registrada só com sessão titular (FR-3613 da `115`) | ✅ |
| III — LGPD | a mensagem perde dado: sem nome, sem nome de documento, sem número de documentos, sem motivo (FR-3886) | ✅ |
| IV — regra no domínio | nenhuma regra nova; as decisões de texto ficam em funções puras, testadas sem banco | ✅ |
| V — simplicidade e rastreabilidade | sem rota, tabela ou script novos; a coluna da D-009 é uma, na tabela que já existe, e só se grava | ✅ |
| VI — jornada demonstrável | do e-mail à convocação pelo código, e do envio à confirmação, no navegador (SC-1156, SC-1162) | ✅ |

Nenhuma entrada em *Complexity Tracking*. A linha da reprodutibilidade estava ⚠️ na primeira versão
deste plano, à espera da decisão da D-009, e ficou ✅ com a opção A.

## Project Structure

### Documentation (this feature)

```text
specs/121-experiencia-da-convocacao/
├── spec.md
├── plan.md                ← este arquivo
├── research.md            ← R-001 a R-009
├── data-model.md          ← o que se lê, o que se monta, a coluna da D-009
├── contracts/
│   ├── mensagem-da-convocacao.md
│   └── acesso-com-destino.md
├── quickstart.md          ← o roteiro de demonstração
├── checklists/requirements.md
└── tasks.md               ← /speckit-tasks, depois do merge deste plano
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── convocacao/
│   ├── domain/
│   │   ├── prazo_apresentado.py          ← novo, puro: data, hora, dia da semana, contagem (R-003)
│   │   └── mensagem.py                   ← novo, puro: escolha_da_mensagem (R-002) e identificacao_do_modelo (R-009)
│   ├── application/
│   │   ├── comunicar.py                  ← EmailMultiAlternatives, modelos, link da convocação
│   │   └── selectors.py                  ← vigentes_por_inscricao com a anterior no prefetch (R-008)
│   ├── templates/convocacao/mensagem/
│   │   ├── inicial.html, inicial.txt     ← novos
│   │   └── correcao.html, correcao.txt   ← novos
│   ├── models.py                         ← ComunicacaoEmitida.modelo_da_mensagem
│   └── migrations/                       ← a ADD COLUMN da D-009
├── portal/
│   ├── obrigacoes.py                     ← a chamada: título, etapa, resumo, ação, ressalva, andamento;
│   │                                        data/hora/ate delegam ao prazo apresentado
│   ├── views.py                          ← convocacao (redirecionamento, confirmação, recusa no cartão);
│   │                                        apresentar_documento_da_convocacao (destinos);
│   │                                        _de_volta_a_vaga (3 rotas); acesso (destino_e_convocacao)
│   ├── templates/portal/
│   │   ├── convocacao.html               ← a ordem da chamada, os três scripts
│   │   ├── _obrigacoes_da_convocacao.html← bloco 1 sem título repetido; andamento; substituída
│   │   ├── _cartao_do_documento_da_convocacao.html ← a recusa no cartão
│   │   ├── _chamada_da_convocacao.html   ← novo parcial: contexto, título, etapa, prazo, resumo, ação
│   │   ├── acesso_email.html, acesso_codigo.html ← a frase do destino
│   │   └── _vaga_do_destino.html         ← o ramo da convocação
│   └── static/portal/
│       ├── envio.js                      ← o ramo sem htmx (R-007)
│       └── portal.css                    ← regras das classes novas
└── interface/templates/interface/
    └── _correcao_da_convocacao.html      ← a frase da prévia (FR-3890)

backend/tests/
├── unit/convocacao/test_prazo_apresentado.py       ← SC-1154, SC-1155
├── unit/convocacao/test_escolha_da_mensagem.py     ← a tabela da R-002
├── unit/portal/test_obrigacoes_da_convocacao.py    ← a chamada por cenário (SC-1150, SC-1151)
├── integration/convocacao/test_mensagem_da_convocacao.py ← SC-1159, SC-1160, SC-1161, reconstrução
├── integration/convocacao/test_versao_do_modelo.py      ← SC-1172
├── authorization/test_convocacao_alheia.py         ← o redirecionamento idêntico (SC-1157)
├── integration/portal/test_destino_da_convocacao.py← SC-1156, SC-1158
├── interface/test_portal_convocacao.py             ← título, cartão, substituída
├── interface/test_portal_documentos_da_convocacao.py ← #confirmacao, recusa no cartão
├── javascript/envio.test.js, arquivo.test.js
└── navegador/test_jornada_da_convocacao_121.py     ← SC-1152, SC-1153, SC-1156, SC-1162, SC-1163
```

## Design

### 1. A chamada (FR-3858 a FR-3868)

`obrigacoes_da_convocacao` (`obrigacoes.py:532`) já recebe tudo o que a chamada precisa: os itens,
as apresentações, as conferências, a política do Requerimento, o estado e o vencimento. Ela continua
pura, e a projeção ganha:

- `titulo`: da tabela da FR-3858, pelo estado que a projeção já calcula (`_aberta`,
  `_encerrada_pelo_prazo` em `:682`, `_encerrada_pelo_processo` em `:702`, desfecho).
  `titulo_do_fechamento` deixa de ser renderizado como `h2` (D-005).
- `etapa`: da tabela da FR-3860, lida dos itens **obrigatórios** e **facultativos** e do momento do
  Requerimento, e não das apresentações.
- `ressalva`: as duas variantes da FR-3864 (D-003).
- `andamento`: os totais de `:567-574`, só obrigatórios (D-004).
- `acao`: o rótulo *"Ver o que preciso fazer"* e a âncora da primeira tarefa. Hoje `primeira_ancora`
  (`:485`) só olha documentos. Ela passa a devolver a âncora do Requerimento quando ele é a única
  tarefa (FR-3863, SC-1151). `rotulo_do_botao` deixa de existir na chamada.

O `convocacao.html` troca o `<h1>Convocação</h1>` fixo pelo `titulo`. O contexto curto
*"‹Perfil› · Edital ‹NN/AAAA›"* sai de `_perfil_legivel` (`views.py:2253`), que a view já tem. A
ordem da FR-3859 fica num parcial novo, `_chamada_da_convocacao.html`, incluído pelos dois ramos
(com e sem documento, FR-3868). O ramo sem documento perde a frase *"Você foi convocada(o)"* e a
linha do prazo escrita à mão (`convocacao.html:48, 54-60`).

O cartão do prazo usa o **prazo apresentado** (seção 2) e, com a vigente sucedendo outra e a chamada
aberta, a frase *"Convocação corrigida: este é o prazo válido."* (FR-3869). A linha *"Convocação
substituída"* entra em *Sobre esta convocação*, com a leitura da R-008.

A consequência (FR-1177 da `063`) **sai** do bloco *Prazo* (`_obrigacoes_da_convocacao.html:67`) e vai
para depois da ação, uma vez só. O guardião da FR-1177 conta as ocorrências.

### 2. O prazo (FR-3873 a FR-3875)

`apresentar(vencimento, agora, fuso)` devolve o valor do [data-model.md](data-model.md). A contagem:

```text
hoje  = agora.astimezone(fuso).date()
dia   = vencimento.astimezone(fuso).date()
vencido            → sem linha
dia == hoje        → "termina hoje, às HHhMM"
dia == hoje + 1    → "‹dia› · termina amanhã"
dia >= hoje + 2    → "‹dia› · faltam (dia - hoje).days dias"
```

Os dois casos sem linha, comunicação não enviada e sem vencimento, são do chamador, que já os
distingue. `obrigacoes.data`, `hora` e `ate` passam a chamar a função. O e-mail a chama com
`agora = enviado_em`. `_razao_do_vencimento` e os templates da gestão não mudam.

### 3. O acesso (FR-3876 a FR-3881)

O contrato está em [contracts/acesso-com-destino.md](contracts/acesso-com-destino.md). Em resumo:

- `convocacao` começa por `identidade_da_sessao(request)`. Sem identidade, devolve 302 para
  `portal:acesso` com `destino` igual ao caminho, antes de `_inscricao_do_titular` (R-004).
- `_de_volta_a_vaga` aceita `portal:convocacao` e reconstrói o caminho pela rota (R-005).
  `_entrar`, `acesso_reconciliar` e o primeiro acesso já terminam todos em `_entrar`, de modo que um
  ponto cobre os três percursos da SC-1156.
- As telas de acesso recebem `destino_e_convocacao` pelo **nome da rota**, e trocam o título e a
  frase (FR-3880).
- Com sessão já autenticada, `acesso` continua mandando para "Minhas inscrições". O link da mensagem
  vai direto à convocação, que abre com a sessão válida (`S6`).

### 4. O envio de documento (FR-3870 a FR-3872)

`apresentar_documento_da_convocacao` (`views.py:2563`) passa a ter dois destinos:

| Resultado | Sessão | Destino |
|---|---|---|
| aceito, novo | `confirmacao_da_convocacao = {item, apresentacao, ja_recebido: False}` | `convocacao#confirmacao` |
| aceito, o mesmo arquivo | o mesmo, `ja_recebido: True` | `convocacao#confirmacao` |
| recusado (sem arquivo, `DomainError` ≠ 404) | `recusa_da_convocacao = {item, frase}` | `convocacao#item-<id>` |
| 404 | — | relançado, como hoje |

A tela consome os dois registros. A confirmação é o primeiro elemento da chamada, com
`id="confirmacao" tabindex="-1"` e `role="status"`. Ela nomeia o documento pelo item da projeção e a
data pela apresentação. A próxima tarefa é a `acao` da projeção **depois** do envio. A recusa entra no
cartão do item, com `role="alert" tabindex="-1" data-recusa`. `_avisar` e `_recusar` deixam de ser
usados nesta rota. A data e a hora da confirmação usam o prazo apresentado, no formato *"em
DD/MM/AAAA, às HHhMM"*.

`convocacao.html` carrega `arquivo.js`, `envio.js` e `recusa.js`, nessa ordem, por `{% static %}`. O
ramo novo de `envio.js` é o da R-007.

### 5. A mensagem (FR-3882 a FR-3890)

O contrato está em [contracts/mensagem-da-convocacao.md](contracts/mensagem-da-convocacao.md). O
envio, em `comunicar.py`:

1. carrega a cadeia e as comunicações dela com uma consulta, que só parte da convocação que está
   sendo comunicada;
2. chama `escolha_da_mensagem` (R-002);
3. renderiza o par de modelos com o prazo apresentado, a identificação da unidade e o link
   `urljoin(endereco_do_portal, reverse("portal:convocacao", args=[inscricao_id]))`. Com a base
   vazia, como nas fixtures, o link é o caminho;
4. envia por `EmailMultiAlternatives`, contando o retorno como hoje;
5. grava, na `ComunicacaoEmitida` do resultado, `ENVIADA` ou `FALHA`, a identificação do modelo
   calculada no passo 3 (R-009).

**A renderização vem antes da conferência do destinatário.** Hoje, sem endereço, `_enviar` devolve a
falha antes de montar a mensagem. Com a ordem nova, toda tentativa individual tem modelo escolhido e
renderizado, e toda `FALHA` grava a identificação (FR-3889). A ordem não envia nada a mais: sem
endereço, nada sai.

A reserva da chave, a recusa da repetição e o registro `ENVIADA` ou `FALHA` não mudam (FR-3888). A
prévia da gestão (`_correcao_da_convocacao.html`) troca a frase da forma individual (FR-3890).
`CORPO`, `COM_PRAZO` e `SEM_PRAZO` saem de `comunicar.py`.

## Validação planejada

### Por camada

| Camada | O que prova | Critérios |
|---|---|---|
| unidade, `test_prazo_apresentado.py` | o dia da semana nos 365 dias de 2027, contra `calendar.weekday`; 23h30 locais; a contagem a 23h59, a 00h01 e a uma hora do vencimento; *"hoje"* e *"amanhã"*; o mesmo resultado com `TZ` do processo trocado para `UTC` e `Asia/Tokyo` | SC-1154, SC-1155 |
| unidade, `test_escolha_da_mensagem.py` | as sete linhas da tabela da R-002, e as quatro variantes de obrigação com e sem vencimento | SC-1160, FR-3884 |
| unidade, `test_obrigacoes_da_convocacao.py` | por cenário (A, C1, C2, F, G, I1, J, corr): título, etapa, resumo, ação e âncora, ressalva, andamento sem o Requerimento | SC-1150, SC-1151 |
| integração, `test_mensagem_da_convocacao.py` | o envio real pelo `locmem`: as duas partes, as frases do HTML contidas no texto, zero `src=`, zero dado da fixture, a citada certa, a repetição sem envio | SC-1159, SC-1160, SC-1161 |
| integração, reconstrução | depois do envio, `escolha_da_mensagem` chamada só com o banco devolve o mesmo modelo, a mesma variante e a mesma citada | FR-3889, D-009 |
| integração, `test_versao_do_modelo.py` | a gravação, a correspondência e a preservação, nos casos da seção seguinte | SC-1172, FR-3889 |
| autorização | sem sessão, real, inventado e alheio: mesmo status, destino e corpo, e zero consultas às três tabelas, por `CaptureQueriesContext`; sessão alheia continua 404 | SC-1157 |
| integração, destino | outro host, esquema estranho, rota fora da lista, consulta e fragmento acrescentados, tudo vira "Minhas inscrições" ou o caminho reconstruído | SC-1158 |
| interface | `#confirmacao` e o texto da FR-3870; a recusa no cartão; a linha substituída nos três estados; o h1 por estado | FR-3869 a FR-3871 |
| javascript | `envio.js` com e sem htmx; `arquivo.js` diz o nome | SC-1163 |
| navegador | a 375 × 812, a ação dentro da primeira tela com folga; a 320 px, com 150 % e com 200 %, sem rolagem horizontal; do link ao código à convocação nos três percursos; o foco na confirmação **com o script desligado** e na recusa | SC-1152, SC-1153, SC-1156, SC-1162 |
| humano | a matriz de clientes de e-mail e SPF, DKIM e DMARC, antes do uso real | SC-1164 |

### Os cenários da D-008, por extenso

O teste de integração monta cada cadeia pela gestão de teste (`cenarios.comunicar` com o
`locmem`). A falha é provocada por um *backend* de e-mail que devolve `0`, o mesmo caminho de
`entregues == 0` em `comunicar.py`:

1. **A enviada, B falhada, C sucessora de B.** A mensagem de C tem o assunto e o título da correção,
   e o quadro cita o `enviado_em` de A e o `vencimento` de A. Os dados do ato de C, no portal, dizem
   *"Convocação substituída: Não comunicada"*, e se referem a B.
2. **A falhada, B falhada, C sucessora de B.** A mensagem de C é a inicial: sem quadro, sem *"corrigida"*
   no assunto e sem o rótulo *"Prazo válido"*.
3. **A enviada, B enviada, C.** C cita B.
4. **A enviada, C, e C reenviada depois de falhar.** As duas tentativas de C escolhem a mesma mensagem,
   e citam A.
5. **A por publicação, C individual.** Inicial, e os dados do ato dizem *"Publicada em…"*.

Em cada um, o texto do quadro tem *"enviamos"* e não tem *"recebeu"* nem *"recebida"*.

### A versão do modelo, por extenso (SC-1172)

1. **Gravação.** Um envio `ENVIADA` e um `FALHA` (o *backend* que devolve `0`, e o destinatário
   ausente) gravam `inicial:sha256:<64 hex>` ou `correcao:sha256:<64 hex>`. O nome confere com a
   escolha da R-002. A comunicação por publicação grava `""`.
2. **Correspondência.** O resumo gravado é igual ao recalculado, pela regra da R-009, **das fontes
   dos dois arquivos que o carregador entregou para aquele envio**. Ele também é igual ao
   recalculado dos arquivos do repositório, lidos do disco. Os dois resumos são calculados de forma
   independente da função de produção.
3. **Preservação.** Com um diretório de modelos temporário à frente dos do app (`override_settings` de
   `TEMPLATES`), contendo uma cópia alterada do HTML, o envio seguinte grava outro resumo. O envio
   anterior, relido do banco, continua com o resumo original. O `UPDATE` da coluna é recusado pelo
   gatilho, coberto pelo teste parametrizado por `TABELAS_APPEND_ONLY`.
4. **Sem retroatividade.** Uma linha gravada pela forma anterior à `121`, sem a coluna, lê `""`.
   A migration não preenche nada: o teste da migration confere zero linhas alteradas.
5. **Repetição.** A repetição concluída com a mesma chave não grava linha nova, e por isso não grava
   identificação nova (FR-3888).

**Guardiões que a migration toca.** Ela é a primeira da `convocacao` depois da `120`, e o guardião da
contagem de migrations por app, da `022`, ganha uma linha. O `provisionar_papeis` continua
`53 de 53`, porque coluna nova não muda privilégio de tabela.

### Os testes existentes que mudam, e por quê

| Teste | Hoje | Depois |
|---|---|---|
| `authorization/test_convocacao_alheia.py:148` | sem sessão → 404 | sem sessão → o mesmo 302 para real e inventado |
| `interface/test_portal_convocacao.py:107` | *"Você foi convocada(o)"*, `%d/%m/%Y, às %Hh%M` | o título por estado e o cartão do prazo |
| `interface/test_portal_documentos_da_convocacao.py:94` | *"Documento recebido. A comissão vai conferir."* | a frase da FR-3870 em `#confirmacao` |
| `interface/test_portal_caminho_da_convocacao.py:221` | a mensagem aponta "Minhas inscrições" | aponta a convocação (FR-1104, revista) |
| `unit/convocacao/test_mensagem.py:151, 170` | `HH:MM` | `HHhMM`, pela função nova |
| `navegador/test_jornada_dos_documentos_da_convocacao.py:154` | heading *"Convocação"* | o título por estado |

Cada mudança cita a FR que a revê.

## A decisão da D-009: a gravação da versão do modelo

**O que a prova mostrou** (R-001). A variante se reconstrói, e o teste de reconstrução a prova. A
versão exata do texto, não:

- O `implantacoes.log` data cada ativação **depois** do *readiness*. Fica uma janela de cerca de dois
  minutos em que um envio pode ter saído de qualquer das duas versões.
- A linha `FALHOU` não diz o que serviu.
- O arquivo está fora do banco e da trilha, e pode ser editado sem rastro.
- Nenhum teste da suíte o alcança, e fora da VM de produção ele nem existe.

**As opções apresentadas ao usuário.**

| Opção | O que se grava | Prova a versão exata? | Custo |
|---|---|---|---|
| **A — o resumo do modelo na comunicação** *(escolhida em 2026-11-05)* | uma coluna em `ComunicacaoEmitida`, `modelo_da_mensagem` = `inicial:sha256:…` ou `correcao:sha256:…`, o resumo dos dois arquivos, gravado na mesma linha do envio, inclusive na `FALHA` | **sim**: o resumo se confere contra os arquivos em qualquer commit, em qualquer ambiente, e se testa na suíte | uma migration `ADD COLUMN` com `default ""`, sem reescrita de linha; a tabela continua append-only e o `53 de 53` não muda; o guardião da contagem de migrations da `022` ganha uma; revisão da FR-3889 e da FR-3891 |
| B — o commit da release na comunicação | uma coluna com o SHA lido do `REVISION` ao subir | sim, em produção; em desenvolvimento e na suíte o `REVISION` não existe, e a coluna fica vazia ou falsa | a mesma migration e a mesma revisão; e o domínio passa a depender do mecanismo de implantação |
| C — sem coluna | nada; o histórico de implantação, com o script gravando também o instante da troca | **não**: a janela estreita, mas as requisições em curso no worker antigo continuam; o log segue fora da trilha e fora da suíte | revisão da FR-3889, para dizer que a versão é **datada**, e não identificada, e aceitar a janela |

**O que a escolha mudou, neste PR.**

- **Na spec:**
  - a FR-3889 passa a exigir a identificação gravada, também na tentativa falhada e sem
    retroatividade;
  - a FR-3891 admite essa coluna e essa migration, e só elas;
  - a D-009 registra a decisão, com a redação anterior preservada;
  - a SC-1172 mede a gravação, a correspondência e a preservação.
- **No plano:** a R-009, o item 6 do *Summary*, o passo 5 do envio, o data-model, o contrato e os
  testes da seção *A versão do modelo, por extenso*.

## Riscos

- **A consequência no lugar novo.** Movê-la do bloco *Prazo* para depois da ação pode deixá-la duas
  vezes, num estado esquecido. O guardião da FR-1177 conta uma ocorrência por estado.
- **O foco sem script.** Varia entre navegadores. A prova é a do Chromium do Playwright, e a do
  Safari fica na verificação humana da SC-1164. Se o Chromium não focar, a recaída é o `recusa.js`
  generalizado para `[data-confirmacao]`, e a FR-3870 precisará de revisão, porque diz *"sem script"*.
- **O teste de tempo da ocupação** pode oscilar na suíte paralela, como registra o CLAUDE.md. Não é
  desta feature.
- **Clientes de e-mail.** O HTML pode sair diferente em cada cliente. A SC-1164 é humana, e bloqueia o
  uso real, não o merge.

## Registrado, sem desenvolver

- **A convocação não tem `@resposta_privada`** (`views.py:2370`), ao contrário do acompanhamento
  (`:1878`), e `test_respostas_privadas.py` não a lista. É defeito anterior à `121`: fica como achado
  para o usuário.
- **`_dias_ate`** (`views.py:474`) conta blocos de 24 horas no período de inscrições, o que a FR-3874
  proíbe na convocação. Fica como achado.
- **A gestão escreve a hora como `HH:MM`** em seis lugares. A FR-3875 vale só para o candidato.
