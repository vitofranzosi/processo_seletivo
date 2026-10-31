# Inventário dos pontos fixos de unidade (109)

Levantado em 31/10/2026 na `main` em `ca1e53ed`, antes de especificar. É o item 1 e o item 8 do
pedido: cada ocorrência que pressupõe uma unidade só, classificada, e o que esta feature faz com ela.

A nota de 31/10 da auditoria (PR #347, *Atualização de 31/10/2026*, no resumo executivo de
`doc/auditoria-administracao-institucional-2026-10-30.md`) já confere as quatro premissas do pedido
— o registro só com o `cefor`, os dez arquivos com "Cefor/Ifes", o canal global, o comentário do
`PAPEIS`. Este inventário não as repete: parte delas e procura o resto.

## Classes

| Classe | O que é | O que esta feature faz |
|---|---|---|
| **G** | identidade institucional global do Ifes — "Ifes", "Instituto Federal do Espírito Santo", o brasão, o nome do produto | mantém, num lugar só |
| **U** | identidade específica da unidade — a sigla na marca, a assinatura das mensagens, o canal de atendimento | passa a vir do registro de Unidades, pela regra de contexto da §3 da spec |
| **T** | texto só explicativo — comentário, exemplo de ajuda, frase que fala da amostra de Editais | mantém |
| **DT** | dado de demonstração ou de teste | mantém |
| **H** | valor histórico ou de contrato, que não pode mudar | mantém, e a spec o protege |
| **F** | dependência funcional indevida de `cefor` | corrige |

Nenhuma ocorrência ficou na classe **F**: o comportamento só presume o Cefor pela **identidade** (U),
e nenhuma regra de negócio, autorização ou numeração depende da string `cefor`. A busca foi
`git grep -i cefor` e `git grep -E "Ifes|IFES|Espírito Santo"` em `backend/processo_seletivo` e
`backend/config`, fora das migrations, mais a leitura de cada uso de `PORTAL_ATENDIMENTO`.

## Os dez arquivos com "Cefor/Ifes"

| # | Onde | O que diz | Classe | Contexto que acha a unidade | Destino |
|---|---|---|---|---|---|
| 1 | `interface/templates/interface/base.html:11` | título de toda página da gestão, "— Cefor/Ifes" | U | a unidade ativa do ator | muda |
| 2 | `interface/templates/interface/base.html:72` | a marca da barra lateral | U | idem | muda |
| 3 | `interface/templates/interface/base.html:138` | a marca do topo, sem ator | U | a identificação da implantação | muda |
| 4 | `interface/templates/interface/base_de_acesso.html:6, 41, 70` | título, "Cefor · Ifes", rodapé da página de acesso | U, e G em "Instituto Federal do Espírito Santo" | a implantação: ainda não há ator | muda a sigla; o nome do Ifes fica |
| 5 | `portal/templates/portal/base.html:11, 21` | título e marca de toda página do portal | U | a implantação; na página pública da seleção, a unidade do ato | muda |
| 6 | `shared/templates/404.html:20, 25` | título e marca da página não encontrada | U | **só a implantação**: a 404 é também "existe e você não alcança", e dizer a unidade do objeto vazaria a existência dele | muda |
| 7 | `avisos/domain/mensagem.py:31` | assinatura do rodapé do aviso | U | a unidade do Edital; o texto é congelado no aviso confirmado (H para os já confirmados) | muda |
| 8 | `convocacao/application/comunicar.py:56` | assinatura da mensagem de convocação | U | a unidade do Edital | muda |
| 9 | `inscricoes/application/mensagem.py:63` | assinatura do comprovante por e-mail | U | a unidade **da Publicação** da versão aceita, a mesma do comprovante (FR-1115 da `060`) | muda |
| 10 | `identidade/application/mensagem.py:35, 36, 39, 60, 72, 75` | assunto, corpo e assinatura do código de acesso e do aviso de mudança de credencial | U | a implantação: a conta do candidato não é de unidade | muda |

A lista do pedido nomeia `publicacoes/infrastructure/pdf.py` e `processos/management/commands/seed_demo.py`
entre os dez. No `pdf.py`, "Cefor/Ifes" está só num comentário (`:1172`, sobre a caixa alta das
siglas); o cabeçalho, a sigla e o local do documento já vêm das colunas `unidade_*` da Publicação
desde a `060`. O `seed_demo` é **DT**. Os dois ficam como estão, e por isso a tabela acima tem dez
linhas com o `base.html` contado uma vez por ponto, e não por arquivo.

## As outras ocorrências

| Onde | O que é | Classe | Destino |
|---|---|---|---|
| `interface/templates/interface/lista.html:27`, `minhas_etapas.html:125`, `recusa.html:23`; `interface/erros.py:149` | "peça acesso a quem administra o sistema **no Cefor**" | U | muda: a unidade ativa |
| `interface/identidade.py:23`, `ESCOPO_PADRAO = "cefor"`; `interface/demonstracao.py:48, 91` | o seletor de demonstração identifica sempre no Cefor | DT | fica — o seletor continua igual (§5 do pedido) |
| `interface/identidade.py:25-26`, comentário do `PAPEIS` | "cada papel corresponderá a um grupo" do diretório | T, desatualizado | **corrige o texto** (item 7 do pedido) |
| `processos/management/commands/seed_demo.py:37-39, 338, 409, 645`; `tests/fixtures/autoridades.py`, `garantir_o_cefor`; `scripts/publicar_corpus_do_piloto.py:41, 85` | demonstração, fixtures e corpus do piloto | DT | fica |
| `publicacoes/models.py:68-79`, colunas `unidade_*` e `signatory_*`; `divulgacao/models.py:81` | a unidade e a autoridade congeladas no ato | H | fica — é o que os documentos publicados preservam |
| `editais/domain/secoes.py:174`, `REDACOES_PADRAO_RETIRADAS` | o preâmbulo retirado na `054`, com o nome do Cefor | H | fica: reconhece o texto que o acervo carrega |
| `editais/domain/perfis.py:312`; `editais/domain/secoes.py:206` | `NAMESPACE` de `uuid5` sobre `cefor.ifes.edu.br` | H | fica: mudar o namespace muda todo identificador já derivado |
| `shared/api/problems.py:47, 82` | `type` dos problemas, `https://processo-seletivo.cefor/errors/...` | H (contrato da API) | fica |
| `shared/api/operacional.py:56` | `"service": "Processo Seletivo e Editais — Cefor/IFES"` no endpoint operacional | T (identificação técnica) | fica; ver P-4 no `research.md` |
| `matriculas/domain/nomes.py:95`, `ABA = "Import_ModeloCefor"` | o nome da aba no modelo de importação do Registro Acadêmico | H (contrato externo) | fica; ver P-3 |
| `interface/templates/interface/convocacao.html:205, 541` | "por exemplo, site do Cefor" numa ajuda | T | fica |
| `interface/templatetags/interface_extras.py:394`; `editais/domain/validation.py:2979-3013` | "seções que todo Edital do Cefor tem" — fala da amostra de quinze Editais | T | fica; ver P-5 |
| `publicacoes/infrastructure/pdf.py:1089-1095, 1153` | as linhas do Ifes no cabeçalho, `SIGLA_DA_INSTITUICAO` | G | fica |
| `publicacoes/infrastructure/brasao.py` | o brasão da República | G | fica |
| `avisos/domain/modelos_iniciais.py:13`; `duvidas/domain/mensagens.py:43-176`; `interface/templates/interface/sem_autenticacao.html:13` | "Ifes" sem unidade | G | fica |
| `pyproject.toml:6`, `name = "processo-seletivo-cefor"` | nome do pacote | T | fica |
| comentários de `pdf.py`, `divulgacao/infrastructure/documento.py`, `shared/tempo.py`, `portal/templates/portal/selecao.html:30`, `comprovante.html:5`, `unidades/models.py:60` | contam a história da amostra | T | fica |

## O canal de atendimento

`PORTAL_ATENDIMENTO` (`config/settings/base.py:344`, exigido em `production.py:204-209`) é lido em
onze pontos. Separados pelo contexto:

| Onde | Para quê | Contexto | Destino |
|---|---|---|---|
| `avisos/application/previa.py:91`; `interface/avisos.py:110` | rodapé do aviso e o rodapé visível no editor | Edital | a unidade do Edital, e o global na falta |
| `convocacao/application/comunicar.py:321` | mensagem de convocação | Edital | idem |
| `portal/views.py:2295` | tela da convocação do candidato | Edital | idem |
| `duvidas/application/consultar.py:262` | canal "da implantação", depois do canal do Edital (decisão R-011 da `070`) | Edital | o canal do Edital, depois o da unidade, depois o global |
| `portal/identidade.py:65` | `_atendimento.html` nas telas de conta: CPF congelado e participação anterior | conta do candidato | global |
| `portal/views.py:1459, 1525` | aviso de mudança de credencial | conta do candidato | global |
| `identidade/application/mensagem.py:130` | idem, o padrão quando vazio | conta do candidato | global |

O canal **não** se confunde com o correio: `EMAIL_*` e `DEFAULT_FROM_EMAIL` são configuração técnica
de envio, uma só para a implantação, e esta feature não as toca.

## O que já resolve multiunidade, e se reaproveita

| Componente | Desde | O que dá |
|---|---|---|
| `Unidade` (`unidades/models.py`) e `unidades.json`, sincronizado com trilha por `sincronizar_unidades` | `060` | sigla, nome, cabeçalho, local, ativa — o cadastro institucional |
| colunas `unidade_*` da Publicação e da publicação de resultado | `060` | o valor histórico, congelado no ato |
| `contexto_do_ato.py`, `pdf.py` | `060` | o PDF lê a unidade do ato, e nunca o registro atual |
| `portal/views.py:_siglas_das_unidades` e `unidade_do_catalogo` | `072` (FR-1611) | a sigla do cartão vem do registro; o título da vitrine diz a unidade só quando o catálogo tem uma só |
| `portal/views.py:_unidade_da_versao` | `060` | o comprovante lê a unidade da Publicação |
| `interface/relatorio.py` | `099`, `100` | os relatórios leem a unidade do ator ou do Edital |
| `escopos_da_pessoa`, `trocar_unidade`, `Actor.institution_scope` | `106`, `107` | a unidade ativa na gestão; a troca não leva permissão de uma unidade a outra |
| a convenção `cefor` × `campus-a` dos testes da `106` e da `107` | `106` | o segundo campus fictício |

## Impacto no modelo de dados

Um atributo novo, e só um: o **canal de atendimento ao candidato da unidade**, opcional, em
`Unidade` e no `unidades.json`. Sigla, nome, cabeçalho e local já existem e bastam para a marca, a
assinatura e o documento. A coluna nova é texto com padrão vazio; a migration só a acrescenta, sem
dado, e o `unidades.json` do Cefor não muda — ausente, o canal da unidade é vazio e o global vale
como hoje. Nenhuma tabela append-only nova (o `M` do provisionamento continua 46).

## Escopo mínimo proposto

1. um resolvedor só, em `unidades/application`, que diz a identificação de uma unidade e a da
   implantação, e o canal de atendimento de uma unidade com a recaída no global;
2. as dez ocorrências de U e as quatro frases "no Cefor" passam a usá-lo;
3. o canal por unidade, opcional no registro, com o global como recaída e exigência de produção;
4. os testes com o Cefor e o `campus-a` da §6 do pedido;
5. o comentário do `PAPEIS`;
6. o documento separado das pendências da auditoria (`doc/`).

Fora: tela nova, configuração genérica, correio por unidade, cadastro de outro campus, mudança de
papel ou de autorização, mudança do PDF.

## Decisão arquitetural pendente

Uma, e ela não bloqueia esta feature: **quem é a marca das superfícies sem unidade de contexto
quando houver mais de uma unidade ativa** — o portal, a página de acesso, a 404, o código de acesso.
A feature implementa a regra que já existe no título da vitrine (FR-1611 da `072`): uma unidade
ativa, ela; mais de uma, só o Ifes. Com o Cefor sozinho, nada muda. A pergunta fica como P-1 no
`research.md`, para o usuário responder antes do segundo campus.
