# Contrato — Inscrição Simples e Documentos do Candidato

**Feature**: [spec.md](../spec.md) | **Modelo**: [data-model.md](../data-model.md)

Três superfícies têm contrato nesta feature: a **forma publicada** (que é contrato institucional e
entra no `openapi.yaml` da `001`), o **endereçamento por Retificação**, e as **superfícies HTML**
dos dois canais. As telas não têm esquema, mas têm garantias verificáveis, e é isso que este
documento fixa.

## 1. Forma publicada — acréscimos à versão canônica 4

O domínio não lê o contrato em execução: `editais/domain/validation.py` transcreve a forma e um
teste de contrato confere a transcrição contra `specs/001-processo-seletivo-editais/contracts/openapi.yaml`.
Os acréscimos abaixo entram nos dois lugares.

### 1.1 `EventoPublicado` — campo novo

| Campo | Tipo | Nulo | Regra |
|---|---|:--:|---|
| `isRegistrationPeriod` | booleano | não | Sempre presente. No máximo um item de `schedule` com valor verdadeiro |

### 1.2 `DocumentoExigidoPublicado` — objeto novo

| Campo | Tipo | Nulo | Regra |
|---|---|:--:|---|
| `id` | string, uuid | não | Identidade estável |
| `key` | string | não | Única no Edital |
| `name` | string | não | |
| `instructions` | string | não | `""` quando ausente, nunca `null` |
| `required` | booleano | não | |
| `order` | inteiro ≥ 0 | não | Única no Edital |
| `profileId` | string, uuid | **sim** | Aplicabilidade |
| `modalityId` | string, uuid | **sim** | Aplicabilidade |

A convenção de texto segue a que a `007` fixou no Perfil: string sempre presente, `""` quando
ausente. A nulabilidade dos dois identificadores é semântica — `null` significa "não restringe" —,
e é o que distingue as quatro combinações de aplicabilidade.

### 1.3 Raiz

| Campo | Tipo | Regra |
|---|---|---|
| `documentRequirements` | lista de `DocumentoExigidoPublicado` | Ordenada por `order`; pode ser vazia |

`schemaVersion` passa a `4`. Nenhum campo novo é campo de identidade: os três são retificáveis.

## 2. Endereçamento por Retificação

`/documentRequirements` entra em `COLECOES_COM_CHAVE`. Formas válidas, pela gramática existente e
sem alteração nela:

```text
/documentRequirements                                  # coleção inteira
/documentRequirements/id=<uuid>                        # um requisito
/documentRequirements/id=<uuid>/required               # um campo
/schedule/id=<uuid>/isRegistrationPeriod               # a designação do período
```

Recusas que continuam valendo: endereçar por posição, endereçar campo de identidade do conteúdo,
endereçar lista de controle interno.

## 3. Superfícies HTML — canal público

Rotas sob o prefixo público, sem identidade institucional em nenhuma delas.

| Superfície | Garantia verificável |
|---|---|
| Vitrine | Lista somente Editais publicamente consultáveis; nenhum dado administrativo; sem identificação |
| Detalhe da seleção | Deriva da versão consolidada vigente; oferece o documento oficial; um convite por Perfil |
| Situação das inscrições | Três estados com data, derivados do Evento marcado; ausência de marca é "não recebe inscrições" |
| Identificação | Chave de sessão própria; retorno ao ponto de origem; recusada em produção quando de demonstração |
| Sua inscrição | Só campos e requisitos aplicáveis; nada redigitado do que a identidade forneceu; `no-store` |
| Envio de arquivo | Uma requisição por requisito; recusa não afeta o que já é válido; progresso visível |
| Revisão | Resumo com retorno por bloco; obrigatório ausente impede o envio |
| Envio | Revalidação integral; idempotente; protocolo único |
| Comprovante | Protocolo, Edital, Perfil, modalidade, instante, nome, versão aceita e o resumo de cada anexo; código de verificação; publica o resumo do próprio PDF; `no-store` |
| Comprovante em PDF | Gerado no servidor; nome de arquivo derivado do protocolo; entregue como anexo; **determinístico** — a mesma inscrição devolve sempre os mesmos bytes; recusado a quem não é titular e a rascunho |
| Documento do titular | Mediado; `inline`; `no-store`; recusado a quem não é titular |

**Regra transversal**: nenhuma dessas superfícies consulta tabela de elaboração. A fonte é sempre a
versão consolidada vigente (`FR-011`).

**Sobre o comprovante em PDF** (`FR-063`, `FR-063a`, `FR-063b`). A primeira redação deste contrato
descrevia um comprovante "imprimível", porque a spec proibia gerar PDF. A decisão foi revista depois
da demonstração: impresso pelo navegador, o documento sai com o endereço da página no alto da folha,
com o nome de arquivo tirado do título da aba e com bytes diferentes a cada impressão — e nada disso
é verificável. Três garantias passam a valer:

| Garantia | Como se verifica |
|---|---|
| O anexo é o que foi entregue | Resumo SHA-256 de cada documento, impresso no comprovante e exibido na consulta administrativa |
| O papel é o que o sistema emitiu | Código de verificação (HMAC do servidor sobre o que o comprovante afirma), impresso e conferível contra a consulta administrativa |
| O arquivo é o que a página anuncia | Resumo SHA-256 do próprio PDF, publicado na página — só possível porque a composição é determinística e não lê o relógio |

O código de verificação **não é assinatura digital**: não há certificado nem ICP-Brasil, e trocar a
chave do servidor invalida os códigos já emitidos.

## 4. Superfícies HTML — canal institucional

| Superfície | Garantia verificável |
|---|---|
| `Inscrições` do Edital | Total e lista com protocolo, candidato, CPF na máscara canônica `***.456.789-**`, Perfil, modalidade, situação, recebidos/esperados e data; `no-store` |
| Detalhe da inscrição | Documentos agrupados **sob o requisito que atendem**; versão aceita visível; `no-store` |
| Documento | Mediado por permissão e escopo; `inline`; resumo recalculado e comparado; recusa em caso de divergência |

Nenhuma dessas telas apresenta deferimento, nota, parecer, classificação ou download em lote.

## 5. Contrato de entrega de arquivo

| Aspecto | Regra |
|---|---|
| Autorização | Titularidade (candidato) **ou** permissão e escopo (institucional). Nunca posse do identificador |
| Disposição | `inline` para exibir; `attachment` apenas na ação secundária de baixar |
| Cache | `no-store` |
| Corpo | Streaming; o conteúdo nunca é carregado inteiro em memória |
| Integridade | Na entrega institucional, resumo recalculado e comparado; divergência recusa e registra |

## 6. Configuração — o que produção passa a exigir

| Configuração | Guarda |
|---|---|
| Raiz privada de arquivos | Obrigatória, absoluta e fora da árvore estática; produção não sobe sem ela |
| Limite de tamanho por arquivo | Lido da configuração da aplicação, com 10 MB por padrão (`FR-046`). Nunca fixado em código, nunca por documento exigido |
| Provedor de identidade de demonstração | Produção não sobe com ele habilitado |

As duas seguem o formato da guarda já existente para o seletor de identidade institucional.

## 7. Recusas com significado

| Situação | O que o candidato lê |
|---|---|
| Arquivo que não é PDF | Que o arquivo é imagem (quando for) e que precisa convertê-lo em PDF |
| Arquivo acima do limite | O limite e o tamanho do que foi enviado |
| Documento obrigatório ausente | Quais requisitos faltam, nomeados |
| Fora do período | Que as inscrições estão encerradas, e que ter começado antes não dá direito de enviar |
| Edital retificado durante o preenchimento | Que o Edital mudou e é preciso revisar antes de confirmar |
| Mudança de modalidade que invalida arquivos | Quais arquivos serão descartados, antes de descartar |
