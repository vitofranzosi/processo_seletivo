# Contrato: os casos de uso do registro e a semente

## `unidades/application/registro.py`

Todas recebem o `ator` da sessão e um `now`, e levantam `DomainError` com o código abaixo. Nenhuma
grava antes de todas as conferências passarem; o ato e o evento são uma transação.

| Função | Grava | Recusas, na ordem em que se conferem |
|---|---|---|
| `conferir_registro(ator, *, campos)` | nada | `forbidden` (sem `unidade:administrar`; as permissões do ator são as do escopo ativo, e só o institucional a tem, por `require_authorization_base`); as de validação (`codigo_invalido`, `codigo_reservado`, `campo_obrigatorio`, `cabecalho_invalido`, `atendimento_invalido`); `codigo_ja_registrado` |
| `registrar(ator, *, campos, motivo, now)` | a Unidade ativa, os três modelos iniciais de aviso com a pessoa como autora, `REGISTRAR_UNIDADE` | as de `conferir_registro`; `motivo_obrigatorio` |
| `conferir_alteracao(ator, *, codigo, campos)` | nada; devolve o antes, o depois e a `versao` | `forbidden`; `unidade_nao_registrada` (404 na tela); as de validação; `nada_mudou` |
| `alterar(ator, *, codigo, campos, versao, motivo, now)` | os campos e `alterada_em`, `ALTERAR_UNIDADE` | as de `conferir_alteracao`; `motivo_obrigatorio`; `unidade_alterada` |
| `desativar(ator, *, codigo, versao, motivo, now)` | `ativa=False`, `alterada_em`, `ALTERAR_UNIDADE` (`ATIVA`→`DESATIVADA`) | `forbidden`; `unidade_nao_registrada`; `motivo_obrigatorio`; `unidade_ja_desativada`; `unidade_alterada` |
| `reativar(ator, *, codigo, versao, motivo, now)` | `ativa=True`, `alterada_em`, `ALTERAR_UNIDADE` (`DESATIVADA`→`ATIVA`) | idem, com `unidade_ja_ativa` |
| `consequencias(ator, *, codigo, ato)` | nada; devolve, para `desativar` ou `reativar`, os Processos não encerrados, como fica a identificação das telas sem unidade, e a `versao` | `forbidden`; `unidade_nao_registrada` |
| `listar(ator)` | nada; as unidades, por sigla | `forbidden` |
| `ficha(ator, *, codigo)` | nada; a unidade, a `versao` e os eventos dela (agregado `Unidade`, `id`), do mais recente ao mais antigo | `forbidden`; `unidade_nao_registrada` |

`campos` é um dicionário com `sigla`, `nome`, `cabecalho` (lista), `local`, `atendimento` e, só no
registro, `codigo`. Chave a mais é ignorada — inclusive `codigo` na alteração (EC-9).

O evento é gravado no escopo da unidade, com o `subject` e as permissões do ator (D-008). A
permissão e o escopo institucional são conferidos como recusa por base (403), e não por
`require_permission(..., institution_scope=...)`, que responderia 404 (D-006). O código repetido
por cadastro concorrente vira `codigo_ja_registrado` por um bloco atômico aninhado em volta do
`INSERT` (EC-2).

## `manage.py semear_unidades`

| Situação | Grava | Saída | Saída do processo |
|---|---|---|---|
| tabela vazia, arquivo válido | as unidades do arquivo, com `REGISTRAR_UNIDADE` de `implantacao`; modelos iniciais | `Unidades: N semeadas.` | 0 |
| tabela vazia, arquivo malformado | nada | `unidade_malformada: …` no erro | 1 |
| tabela com unidades | nada de unidade; modelos iniciais que faltem | `Unidades: registro com N unidades; a semente não se aplica.` | 0 |
| sempre, depois da linha acima | — | `Modelos de aviso: N criados.` | — |

`--arquivo CAMINHO`: outro arquivo, para conferência; nunca em produção (como hoje).

`--exportar`: imprime o registro no formato do arquivo, ordenado por código, e não grava nada. Todo
campo obrigatório vai, inclusive `ativa`; `atendimento` só quando preenchido, porque a validação da
`109` recusa o canal declarado vazio (D-016). Para
a reversão ([migracao.md](../migracao.md)); nenhum roteiro de implantação o chama.

**`manage.py sincronizar_unidades`** é o apelido (D-003): aceita as mesmas opções, faz o mesmo, sai
com o mesmo código e imprime o mesmo no *stdout*; no *stderr*, uma linha a mais:
`sincronizar_unidades é o nome anterior de semear_unidades; atualize o roteiro que o chamou.`

## Os comandos de implantação dos papéis institucionais (D-002)

`conceder_administracao_institucional`, `retirar_administracao_institucional` e
`substituir_administracao_institucional` ganham `--papel`:

| Valor | Papel | Permissões |
|---|---|---|
| `administrador-institucional` (padrão) | Administrador institucional de acessos | `acesso:administrar` |
| `administrador-de-unidades` | Administrador do registro de unidades | `unidade:administrar` |

Outro valor: recusa do `argparse`, antes de qualquer gravação. As demais opções e recusas não mudam,
e valem por papel — `--adicional` para a segunda pessoa com o mesmo papel, `--sem-administracao`
para retirar a última. A saída nomeia o papel. Sem `--papel`, a saída e o efeito são os de hoje.

Pela aplicação (tela da `107` ou chamada direta a `conceder`), qualquer papel institucional recebe
`PAPEL_SO_POR_IMPLANTACAO` (403), sem gravar (FR-3339).

## O provedor de homologação (D-018) — só no código de teste

| Parte | Contrato |
|---|---|
| `tests.homologacao.provedor.ProvedorDeHomologacao` | subclasse de `tests.fixtures.provedor_simulado.ProvedorSimulado`; `nome = "homologacao"`; herda `apenas_para_testes = True` e `concluir` |
| `iniciar(request, *, retorno, estado)` | a página do provedor: uma entrada por pessoa com `IdentidadeExterna(provedor="homologacao")`, com o nome e os papéis vigentes; cada entrada leva a uma ação do próprio provedor que chama `provedor_simulado.emitir(...)` e redireciona a `retorno?state=<estado>&bilhete=<bilhete>`. Sem estilo nem *script* embutidos |
| `concluir(request, *, estado)` | o do simulado: o bilhete sai do provedor e vira a `IdentidadeAutenticada`, uma vez só; senão `None` |

Com as settings de produção, `GESTAO_PROVEDOR_INSTITUCIONAL` apontando para ele faz o serviço recusar
subir (FR-3026 da `106`).

## Gatilhos de `processos`

Uma tentativa de mudar `institution_scope` de Processo Seletivo ou de Edital levanta erro do banco
(`the institution scope of a processo is immutable`, `… of an edital is immutable`), e a transação
inteira volta. A aplicação não captura: nenhum caminho dela tenta.
