# Contrato — a operação de reaproveitamento

A feature **não expõe API nova**. O contrato aqui é o do serviço de aplicação e o da afordância na
interface administrativa, que é o canal de quem elabora.

## Serviço de aplicação

```text
reaproveitar_edital(
    actor,                 # precisa de `edital:elaborar`
    edital_id,             # o DESTINO, que já existe e está vazio
    origem_id,             # o Edital publicado ou encerrado de onde se parte
    expected_revision,     # revisão do destino, para o compare-and-swap
    idempotency_key,
    correlation_id,
) -> Edital                # o destino, já com o conteúdo
```

**Uma transação, nesta ordem** — a sequência do `§7.1` da spec, detalhada:

```text
1. autorizar; carregar destino e origem — 404 para o que o ator não alcança
2. reservar a chave; se a reserva já tem resultado, devolver o destino e ENCERRAR
3. só agora recusar as precondições mutáveis: rascunho não vazio, destino fora de
   elaboração, Processo que não aceita mudança
4. versao = effective_version(edital_id=origem_id); conteudo = elevar(versao.content)
5. montar o mapa de identidades (T-005)
6. criar ArtefatoAnexo + AnexoEdital do destino, na ordem da origem
7. remapear o payload; converter os três instantes (T-002); filtrar as seções textuais (T-006);
   zerar o status dos Eventos
8. replace_draft(destino, ...) — validações e compare-and-swap
9. registrar a origem na trilha — a **versão** de onde o conteúdo saiu
```

Falha em qualquer passo desfaz todos: não existe destino pela metade (`FR-017`).

**O passo 2 antes do 3 é requisito, não estilo** (`FR-017a`). Depois da primeira cópia o rascunho
não está mais vazio — conferir a precondição antes da chave faria toda repetição responder
`draft_not_empty`, e a operação deixaria de ser idempotente no único caso que importa. É a ordem que
`add_edital` já pratica, com a mesma justificativa escrita no comentário dele. Autorização e escopo
ficam **antes** da reserva: repetição conhecida não é passe para quem não alcança o objeto.

## Recusas

| Código | Quando | Situação |
|---|---|---|
| recusa de permissão | ator sem `edital:elaborar` | a do resto da gestão |
| `not_found` | destino ou origem fora do escopo; origem inexistente; origem não publicada nem encerrada | `404`, indistinguível — inelegível responde como inexistente |
| `draft_not_empty` | o destino já tem Perfil, Evento, Etapa, Documento, Seção ou Anexo — **e a chave não é de uma repetição conhecida** | nomeia o que já existe; nada é apagado |
| `no_effective_version` | a origem não tem conteúdo vigente | não deveria ocorrer para origem elegível; é a rede de segurança do seletor |
| as de `replace_draft` | o conteúdo copiado não passa nas validações da composição | a recusa nomeia o que impediu (`FR-019`) |
| conflito de revisão | outra gravação alterou o destino nesse meio-tempo | `compare_and_swap`, como em toda a elaboração |

A repetição com a mesma chave devolve o mesmo destino, sem executar segunda cópia (`FR-017`).

## Evento de auditoria

Um por operação, além do `ALTERAR_RASCUNHO` que `replace_draft` grava (`T-004`).

```text
operation        operação própria desta feature
aggregate_type   Edital
aggregate_id     identificador do DESTINO
actor_subject    quem elaborou
occurred_at      o instante
reason           o IDENTIFICADOR da VERSÃO CONSOLIDADA de origem — nunca prosa (FR-015a).
                 O Edital de origem deriva dela por `edital_id`; guardar a versão preserva
                 "independência e versão", que é o que a Constituição pede de conteúdo
                 reutilizável incorporado
new_state        EM_ELABORACAO
new_revision     a revisão resultante
correlation_id   o da requisição
```

O aviso permanente (`FR-014`) é montado a partir deste registro: resolve a **versão** pelo
identificador, chega ao Edital por `edital_id`, e renderiza o Edital por número e ano mais a versão
pelo par `(publicação que a produziu, vigência)` — único por construção, e o que impede duas versões
da mesma fronteira de se anunciarem iguais (`FR-014a`). **Nunca
interpreta o texto do registro** — é o que faz o aviso sobreviver a renomeações e o que impede que a
origem se perca. E porque é a versão que está guardada, uma Retificação posterior na origem não apaga
*de qual configuração se partiu*.

## Afordância na interface

| Onde | O quê | Condição |
|---|---|---|
| primeira etapa da composição | cartão *"partir de um Edital anterior"* | destino em elaboração **e** rascunho vazio |
| tela de escolha | lista de origens elegíveis, com número, ano, título e Processo, localizável por esses atributos | escopo do ator; publicados e encerrados |
| tela de escolha | mensagem própria quando não há origem elegível | nunca lista vazia sem explicação |
| composição, todas as etapas | aviso permanente com a origem e o pedido de atualização, em `compor_base.html` — que todas as etapas estendem, e **não** em `base.html` | enquanto o destino estiver em elaboração |

O formulário de escolha leva `chave_idempotencia`, como as telas de criação (`T-009`).

**E a regra que separa exibir de enviar** — a que custou dois defeitos antes de ser escrita. A tela
confere, **para exibir**, tudo o que decide se vale a pena oferecer: situação do Edital e rascunho
vazio. Para **enviar**, confere apenas o que a operação não altera — permissão e escopo, que são
autorização — e deixa situação, Processo e rascunho **inteiramente** para o serviço, depois da
reserva da chave.

```text
GET   permissão · escopo · situação · rascunho vazio
POST  permissão · escopo                              → o resto é do serviço (FR-017a)
```

A razão é a de `FR-017a`, e vale para **todas** as precondições que a operação altera, não só para o
rascunho: copiado o Edital e submetido para revisão, reenviar a mesma requisição encontraria situação
diferente — e responderia 404 onde a reserva já tem resposta pronta.
