# Contrato — Acesso do candidato

**Canal**: HTML renderizado no servidor, sob o portal. **Ator**: o candidato, no navegador.

Nenhuma destas rotas aceita ou devolve CPF em endereço de página (`FR-009`), e nenhuma delas revela
se um endereço existe (`FR-020`).

---

## `GET /acesso` — informar o endereço

Formulário com um campo de e-mail.

| Situação | Resposta |
|---|---|
| Sempre | `200`, o formulário |
| Já autenticado | `302` para a área pessoal |

---

## `POST /acesso` — solicitar o código

| Situação | Resposta |
|---|---|
| Endereço com forma aceitável | `302` para `/acesso/codigo`, sempre — exista ou não identidade (`FR-020`) |
| Endereço malformado | `200`, o formulário com a recusa, sem consumir limite |
| Limite por endereço ou por origem esgotado | `302` para `/acesso/codigo`, com a **mesma** mensagem e a **mesma** janela de espera que o caminho feliz (`FR-021`) |
| Falha no envio | `302` para `/acesso/codigo`, mensagem idêntica; a falha é registrada no servidor (`FR-083`) |

**Efeitos**: cria um `DesafioDeAcesso` de finalidade `entrar` e invalida os anteriores ainda
utilizáveis daquele endereço (`FR-026`).

**Nunca**: nos **três** casos que poderiam revelar a existência do endereço — existe, não existe,
limite esgotado — e também na falha de envio, a resposta, o código de estado, o texto e a janela de
reenvio são idênticos.

O endereço malformado é caso distinto e responde `200` com a recusa do formulário. Ele não revela
nada: a recusa fala da forma do que foi digitado, e é anterior a qualquer consulta.

---

## `GET /acesso/codigo` — informar o código

Formulário com **um** campo de texto, que aceita colagem integral e digitação natural (`UX-005`). O
endereço informado permanece visível e não é perdido em erro (`UX-007`).

---

## `POST /acesso/codigo` — validar

| Situação | Resposta |
|---|---|
| Código correto, endereço já verificado | `302` para `/inscricoes`; sessão rotacionada (`FR-035`) |
| Código correto, endereço sem correspondência anterior | cria identidade sem pedir CPF e `302` para `/inscricoes` (`FR-049`) |
| Código correto, endereço com correspondência anterior | `302` para `/acesso/reconciliar` (`FR-050`) |
| Código errado, expirado, já usado, ou acima de cinco tentativas | `200`, com recusa que **não** distingue os quatro casos (`FR-031`) |

**Efeitos**: o consumo do código é atômico — duas requisições simultâneas com o mesmo código
produzem exatamente um consumo (`FR-025`, `SC-003`).

---

## `GET /acesso/reconciliar` — o convite

Aparece somente depois de um código válido cujo endereço consta de inscrições anteriores. Oferece
**Confirmar agora** e **Continuar sem isso** (`FR-050`).

O texto não revela nome, CPF, protocolo nem quantidade de inscrições da identidade anterior
(`UX-008`).

---

## `POST /acesso/reconciliar` — confirmar ou recusar

| Situação | Resposta |
|---|---|
| CPF confere com exatamente uma identidade correspondente | associa o endereço a ela e `302` para `/inscricoes` (`FR-050`, `FR-051`) |
| CPF não confere | `200`, com recusa que não diz de quem é o quê; conta tentativa no desafio (`FR-052a`) |
| Quinta tentativa errada | cria identidade própria e `302` para `/inscricoes` — **nunca** beco sem saída (`FR-052`, P-009) |
| **Continuar sem isso** | cria identidade própria e `302` para `/inscricoes` (`FR-052`) |
| Dez minutos após o consumo do código | o convite expira; a pessoa segue com identidade própria (`FR-052b`) |

**Efeitos**: a decisão ocorre **antes** de o vínculo entre endereço e identidade existir. Em nenhum
desfecho o visitante fica sem sessão.

**Onde as tentativas são contadas**: no desafio que provou o endereço, que permanece o portador da
reconciliação pendente depois de consumido (`FR-052a`, D-016). Não na sessão, que uma aba nova
zeraria; e nunca na identidade alvo, o que permitiria a um terceiro esgotar as tentativas e impedir o
titular legítimo de reconciliar (`FR-052c`). Tentar de novo exige novo código, sob o limite da
`FR-030`.

---

## `POST /acesso/reconciliar/retomar` — a retomada

Disponível de dentro da área, e **somente enquanto a identidade atual não tiver nenhuma inscrição,
nem rascunho** (`FR-053`).

Passa por um desafio novo ao endereço que carrega a correspondência: é uma regra só de contagem nos
dois caminhos (D-016), e o ato que move credenciais e descarta uma identidade merece ser reprovado no
instante em que acontece.

| Situação | Resposta |
|---|---|
| Identidade vazia e CPF confere | move **todas** as credenciais para a identidade anterior, descarta a vazia, `302` para `/inscricoes` (`FR-054`) |
| Identidade já tem qualquer inscrição | `404` — a ação deixou de ser oferecida |
| CPF não confere | `200`, com recusa; conta tentativa |

**Efeitos**: verificar, mover e descartar acontecem em uma operação só, sob bloqueio de linha tomado
também pela abertura de rascunho (`FR-055`, D-010). Não existe desfecho parcial (`SC-016`).

---

## `POST /sair`

Encerra a sessão do candidato, e apenas a dele (`FR-038`).

---

## O que foi removido

`GET|POST /identificar` — a identificação por declaração da `009` — deixa de existir (`FR-048`,
D-011). A variável de ambiente que a habilitava permanece definida e a recusa de inicialização em
produção permanece ativa, como armadilha: se o caminho voltar, produção não sobe.
