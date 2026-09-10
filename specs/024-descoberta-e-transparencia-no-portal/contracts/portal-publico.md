# Contrato — Portal público: vitrine e seleção

A feature altera **duas rotas de leitura anônima** do portal do candidato. Não cria rota, não cria
API, não cria formulário que grave. Este contrato descreve o que cada rota aceita, o que devolve, e
o que ela nunca faz.

---

## 1. As rotas

| | Vitrine | Seleção |
|---|---|---|
| Método | `GET` | `GET` |
| Endereço | a raiz do portal | a seleção, por identificador de Edital |
| Identificação | **nunca exigida** (`FR-150`) | **nunca exigida** (`FR-150`) |
| Efeito colateral | **nenhum** — sem escrita, sem auditoria, sem registro de navegação (`FR-151`, `SC-047`) | idem |
| Idempotência | total, salvo passagem do tempo e novo ato publicado | idem |

**Por que não geram auditoria.** A trilha registra ato sensível praticado por alguém identificado.
Aqui não há ator e não há ato: registrar produziria trilha de leitura anônima, que é vigilância de
candidato — recusada pela `D-008` sob o Princípio III.

---

## 2. Vitrine — o que aceita

| Parâmetro | Valores aceitos | Ausente ou irreconhecível |
|---|---|---|
| `busca` | texto livre | sem busca |
| `unidade` | escopo institucional presente no catálogo publicado | todas as unidades |
| `situacao` | `aberta` \| `futura` \| `encerrada` \| `sem-prazo` | todas as situações |
| `perfil` | denominação de Perfil presente no catálogo publicado | todos os Perfis |
| `ordem` | `prazo` \| `recentes` | `prazo` |

**Regra única de recusa:** não há. Valor irreconhecível é lido como ausência do filtro
(`FR-142`, T-004). A rota não devolve 4xx por consulta malformada, e não escreve mensagem de erro.

**Combinação:** filtros e busca se somam — `E` entre eles, nunca `OU` (`FR-139`).

**Fora do catálogo:** seleção cancelada não entra em resultado algum (`FR-152`).

---

## 3. Vitrine — o que devolve

| Elemento | Condição | Requisito |
|---|---|---|
| Grupos pelas quatro situações, sem fundir futuras com encerradas | **sem** consulta ativa | `FR-146` |
| Lista única ordenada, sem cabeçalho de grupo | **com** consulta ativa | `FR-146a` |
| Situação de cada seleção como marca explícita | sempre | `FR-145` |
| Data-limite exata **e** prazo restante | seleção aberta | `FR-147` |
| Nenhuma frase de prazo | seleção sem período designado | `FR-149` |
| Caminho visível para consultar a seleção | seleção sem inscrição aberta | `FR-148` |
| Contagem de resultados | sempre que há consulta | `FR-141` |
| Caminho para limpar a consulta | sempre que há consulta | `FR-141` |
| O que foi procurado, e a volta ao catálogo | consulta sem resultado | `FR-142` |
| A consulta inteira refletida no endereço | sempre que há consulta | `FR-143` |
| A mesma informação na mesma posição em todos os cartões | sempre | `UX-016` |

**Onde a ordem se aplica** (`FR-140a`): dentro de cada grupo quando há agrupamento; sobre a lista
inteira quando há consulta.

**Qual é a ordem:** a de urgência de quem lê — o que fecha antes, primeiro — salvo `ordem=recentes`,
que ordena pelo início de vigência **do conteúdo exibido** (`FR-140`, `T-006`). Não pelo instante do
ato que o produziu: uma Retificação publicada hoje e vigente na semana que vem não muda a posição
hoje, porque o cartão ainda mostra o conteúdo anterior.

**A contagem é uma só** (`FR-141`): o total encontrado, e não um número por grupo.

---

## 4. Seleção — o que aceita

| Parâmetro | Uso |
|---|---|
| identificador do Edital | no caminho, como hoje |
| os cinco parâmetros da §2 | **apenas** para montar o caminho de volta à vitrine (`FR-144`) |

Nenhum outro parâmetro atravessa para o link de volta. Um valor que não seja consulta reconhecida da
vitrine é descartado — repassar texto arbitrário para dentro de um endereço é como se abre
redirecionamento (T-007).

---

## 5. Seleção — o que devolve

### 5.1 Cronograma

| Elemento | Condição | Requisito |
|---|---|---|
| Eventos na ordem publicada, com o período declarado | há cronograma publicado | `FR-125` |
| Situação de cada Evento: concluído, em curso, por vir | idem | `FR-126` |
| Local do Evento | o Edital o declarou | `FR-127` |
| **Nada** — nem seção, nem frase de ausência | não há cronograma publicado | `FR-128`, `D-009` |

**Invariante:** a situação descreve o Evento. Nenhuma frase desta seção fala da pessoa que lê
(`FR-126`).

### 5.2 Histórico normativo

| Elemento | Condição | Requisito |
|---|---|---|
| Cada ato publicado, com a data de publicação | há mais de um ato | `FR-129` |
| Justificativa publicada | o ato é Retificação | `FR-130` |
| O que foi alterado, em linguagem do domínio | o ato é Retificação | `FR-130`, `D-005` |
| Documento daquele ato, alcançável | sempre que o ato existe | `FR-132` |
| O conteúdo exibido é o consolidado vigente | sempre | `FR-131` |
| Identificação de que o conteúdo exibido é o vigente | há mais de um ato | `FR-131a` |
| **Nada** — nem seção, nem frase de negação | ato único | `FR-133`, `D-009` |

**O que nunca aparece:** endereçamento estrutural do conteúdo (`target_path`), resumo criptográfico,
identificador de versão consolidada. Nenhum deles é vocabulário do domínio (`D-005`, Princípio I).

**O que entra como ato:** somente Retificação **publicada**. Em elaboração, em revisão, homologada e
cancelada não são atos publicados.

### 5.3 A vaga

| Elemento | Condição | Requisito |
|---|---|---|
| Atribuições, carga horária, remuneração | declarados no conteúdo publicado | `FR-134` |
| Linha omitida, sem rótulo e sem "não informado" | campo não declarado | `FR-135`, `D-009` |
| Oferta como leitura principal | zero vagas imediatas com reserva declarada | `FR-136`, `D-007` |
| Convite de inscrição, com os três estados de hoje | inalterado | — |
| Aviso de que inscrever-se exige identificação | antes de o convite ser acionado | `FR-137` |

---

## 6. O que as duas rotas nunca fazem

1. Exigir identificação (`FR-150`).
2. Gravar qualquer coisa — tabela, sessão, trilha, contador (`FR-151`).
3. Anunciar seleção cancelada (`FR-152`).
4. Afirmar ausência que o Edital não declarou (`D-009`).
5. Exibir conteúdo que não seja o vigente como se fosse (`FR-131`, `D-006`).
6. Depender de execução de script para mostrar o que o servidor já sabe (`UX-017`).

---

## 7. Compatibilidade

Endereço em uso hoje continua válido: a vitrine sem parâmetro nenhum devolve o catálogo inteiro, e a
página da seleção sem parâmetro de consulta devolve a volta para a vitrine sem filtro.

Nenhum endereço existente muda de forma. Nenhum contrato de API pública é tocado — o
`public-history`, o `public-document` e o `public-anexo` continuam como estão, e a feature não
altera nenhum deles.
