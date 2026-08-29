# Data Model: Interface Administrativa

**Esta feature não tem esquema de persistência.** Nenhuma migration foi criada, nenhum model novo
existe. O que segue são os **modelos de apresentação**: as estruturas que traduzem entre o que a
pessoa vê na tela e o que os commands do domínio exigem.

Escrito depois da implementação, descrevendo o que existe em
`backend/processo_seletivo/interface/`.

## A regra que organiza tudo

O domínio fala em snapshots e commands; a tela fala em campos e cliques. Cada estrutura aqui existe
para fazer uma dessas traduções, **em uma direção só**:

```text
tela ──── forms.py ────► payload do command ────► domínio
tela ◄─── selectors ─── agregados                 (a fronteira: autoriza, audita, transaciona)
```

Nenhuma dessas estruturas decide autorização, valida regra normativa ou grava. Quando algo aqui
parece uma regra, é explicação antecipada do que o command responderia — nunca a regra em si.

## 1. Ator (`identidade.py`)

A fronteira de autenticação da Decisão 4 do plano. Tudo que a interface sabe sobre quem está usando
passa por aqui, e nada mais sabe como esse dado é produzido.

| Elemento | O que é |
|---|---|
| `PAPEIS` | Cinco papéis fixos — elaborador, homologador, publicador, gestor, auditor — cada um com as permissões que o backend reconhece |
| `ator_da_sessao(request)` | Lê pessoa, escopo e permissões da sessão e devolve o Ator que os commands esperam; `None` quando não há identidade |
| `identificar(request, subject, papeis, escopo)` | Grava a identidade na sessão |
| `seletor_disponivel()` | `INTERFACE_SELETOR_IDENTIDADE`; quando falsa, a rota devolve 503 e nenhum papel aparece no HTML |
| `contexto_identidade(request)` | Context processor: põe a identidade em toda página, para o cabeçalho |

**Quando o LDAP entrar, só `ator_da_sessao` muda.** É o que a fronteira existe para garantir.

## 2. Linhas indexadas de formulário (`forms.py`)

Perfis e Eventos são listas que crescem enquanto a pessoa preenche, e o HTMX insere linhas sem
recarregar a página. Um `formset` do Django não serve: ele numera por posição e exige um campo de
gestão que o HTMX teria de manter sincronizado.

**Solução**: cada linha carrega um índice próprio no nome dos seus campos —
`perfil-<indice>-code`, `evento-<indice>-startAt`. O índice nasce no cliente
(`Date.now()`) e nunca é reaproveitado.

| Função | Direção | O que faz |
|---|---|---|
| `ler_perfis(dados)` / `ler_eventos(dados)` | tela → command | Agrupa os campos por índice e converte tipos |
| `perfis_do_edital(edital)` / `eventos_do_edital(edital)` | agregado → tela | Serializa para reexibir no formulário |
| `perfis_persistidos(edital)` / `eventos_persistidos(edital)` | agregado → command | O que já está salvo, para não perder ao gravar outra etapa |

**Três decisões que o código carrega:**

- **Buracos são esperados.** `_indices` aceita índices não contíguos: remover a segunda de três
  linhas deixa a sequência furada, e isso é normal.
- **Instantes são de Brasília.** `ZONA = ZoneInfo("America/Sao_Paulo")`. O campo
  `datetime-local` não tem fuso; interpretar como UTC deslocaria toda data de Edital em três horas.
- **Modalidade sem separador vira código e nome iguais**, e a serialização de volta não repete os
  dois — senão "Ampla concorrência" volta como "Ampla concorrência — Ampla concorrência".

## 3. Etapas do assistente (`views.py`)

`ETAPAS_COMPOSICAO` define quatro etapas: identificação, perfis, cronograma e revisão.

**Identificação é somente leitura.** Não existe command que altere título ou descrição depois da
criação — é a lacuna `ETAPAS_SEM_BACKEND` registrada no plano. A etapa existe para mostrar o que
foi criado, não para editar.

Cada etapa grava sozinha. Ao salvar uma, as outras vão junto pelo `*_persistidos`, porque o command
de rascunho substitui o conteúdo inteiro.

**A leitura vem antes da gravação.** `_ler_etapa` monta os dados a partir do que foi enviado, e só
então `_gravar_etapa` chama o command: se o domínio recusar, o que a pessoa digitou continua na mão
para ser reexibido. Fazer o inverso perdia o conteúdo na recusa.

## 4. Tabelas de atos (`atos.py`, `atos_retificacao.py`, `atos_processo.py`)

Uma tabela em vez de uma cadeia de condicionais, porque a tela precisa das mesmas respostas para
todos os atos.

| Campo | Para que serve |
|---|---|
| `chave`, `rotulo` | Identidade e o que a pessoa lê |
| `permissao` | Qual permissão o command exigirá |
| `situacao_exigida` / `situacoes` | De que situação o ato parte |
| `command` | A função do domínio que pratica o ato |
| `consequencias` | O que o ato provoca, dito **antes** da confirmação (FR-010, FR-011) |
| `irreversivel`, `interrupcao` | Peso visual: interromper não é o mesmo que concluir |
| `exige_motivo`, `exige_signatario` | Campos que a confirmação precisa pedir |

Duas funções derivam da tabela:

- **`disponiveis(agregado, ator)`** — os atos que cabem: permissão que o ator tem, situação em que o
  agregado está. É o que monta a lista de ações.
- **`impedimento(agregado, ator, ato)`** — por que um ato não cabe agora. Existe porque a tela de
  confirmação é alcançável por URL direta e oferecia "Confirmar" para atos que o command recusaria.

**Nada aqui autoriza.** A tabela explica o que o command responderia; quem recusa é ele.

## 5. Composição de Retificação por diferença (`retificacao.py`)

Uma Retificação é um conjunto de Alterações Normativas com `targetPath` em JSON Pointer. Pedir isso
à pessoa seria pedir que ela escrevesse `/profiles/0/immediateVacancies`.

**Solução**: a tela mostra o conteúdo vigente em campos editáveis; o que ela **não tocar** não vira
alteração.

- `campos_editaveis(conteudo)` — quais campos do snapshot são editáveis, com rótulo, tipo e o
  JSON Pointer correspondente. Hoje: título e descrição do Edital, e de cada Perfil e Evento, os
  campos de valor.
- `diferencas(conteudo, dados)` — compara o enviado com o vigente e produz as Alterações Normativas,
  mais um resumo legível de cada mudança.

**Limite conhecido**: só edita campos de valor. Acrescentar ou remover um Perfil por Retificação —
`ADD` e `REMOVE`, que o domínio suporta — não tem tela.

**`_mesmo_instante`** compara datas com tolerância: o `datetime-local` tem precisão de minuto e o
armazenado tem microssegundos; sem isso, abrir e salvar sem mudar nada geraria alteração espúria.

## 6. Apresentação de valores (`templatetags/interface_extras.py`)

| Filtro | Por que existe |
|---|---|
| `situacao` | `EM_REVISAO` não é o que a pessoa lê. Tem as formas masculina e feminina: Edital e Processo são "Homologado", Retificação é "Homologada" |
| `plural` | Plural em português não se resolve com sufixo — o `pluralize` do Django produzia "2 Editalis" |
| `dicionario` | Lê o que foi enviado para reexibir sem perder o digitado |

`OPERACOES` e `AGREGADOS`, em `views.py`, traduzem a trilha de auditoria. Há teste que lê os
literais `operation=` passados a `record_event` em todo o application layer e falha se algum não
tiver rótulo — foi assim que `ALTERAR_RASCUNHO` deixou de aparecer cru na tela.

## 7. Recusa do domínio (`erros.py`)

`RecusaDoDominioMiddleware` converte `DomainError` em página renderizada, com o mesmo status HTTP e
a mensagem que o domínio escreveu.

Existe porque o handler de exceções do DRF só alcança views do DRF: numa view Django comum, uma
`DomainError` viraria 500 — inclusive quando ela diz apenas "você não tem essa permissão".

## 8. O que fica no navegador

O rascunho local do assistente, em `localStorage`, sob a chave
`ps:rascunho:<edital>:<etapa>:<pessoa>` — a pessoa entra na chave para que quem usar o mesmo
computador depois não veja o rascunho alheio.

O valor é `{em, dados}`, onde `dados` é a forma canônica do formulário:

```text
{ simples: {campo: valor},           // campos fora de linha
  linhas:  [{campo: valor}, ...] }   // uma entrada por Perfil ou Evento, na ordem da tela
```

**Canônica porque o nome dos campos não serve para comparar.** O índice de cada linha nasce no
cliente e o servidor renumera ao reexibir; comparar `perfil-1788002895219-code` com `perfil-0-code`
acusaria diferença logo depois de um salvamento bem-sucedido.

O template entrega ao script o que ele precisa saber, e nada além: `data-rascunho` com a chave,
`data-lista` com o contêiner das linhas e `data-fragmento` com a rota que reconstrói uma linha. Sem
permissão de elaborar, os atributos não são renderizados e nada é guardado.

**Não é fonte normativa** e não substitui o rascunho estruturado do Edital, que continua no backend.
Some sozinho quando o conteúdo guardado coincide com o renderizado — isto é, quando o domínio já
recebeu o que estava pendente.

## Divergências da estrutura desenhada no plano

O `plan.md` desenhou uma estrutura que a implementação não seguiu à risca. As diferenças são de
tamanho, não de arquitetura, e ficam registradas para quem comparar os dois documentos:

| Plano | Realidade | Por quê |
|---|---|---|
| `views/` como pacote | `views.py`, um módulo | Um arquivo comporta as 16 views sem ficar difícil de ler; dividir agora seria antecipar uma estrutura que ainda não pesa |
| `forms/` como pacote | `forms.py`, um módulo | Idem |
| — | `atos.py`, `atos_retificacao.py`, `atos_processo.py` | Não previstos: as tabelas de atos apareceram como resposta a FR-010 e FR-011, e são três porque os agregados têm ciclos de vida distintos |
| — | `erros.py`, `retificacao.py` | Idem: o middleware de recusa e a composição por diferença |
| `static/` na raiz do backend | `interface/static/interface/` | O Django não varre a raiz do backend. Colocar ali custou um 404 silencioso e todos os botões dinâmicos — ver research.md §2 |
| `tests/acessibilidade/` | `tests/interface/test_acessibilidade.py` | Um arquivo entre os demais testes de interface; um diretório para três testes seria cerimônia |
