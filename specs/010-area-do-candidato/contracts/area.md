# Contrato — Área pessoal do candidato

**Canal**: HTML renderizado no servidor, sob o portal. **Ator**: o candidato autenticado.

Toda rota abaixo exige sessão de candidato. Sem ela, `302` para `/acesso`. Nenhuma delas concede
permissão institucional (`FR-003`, `SC-014`), e toda consulta a objeto verifica titularidade no
servidor (`FR-085`).

---

## `GET /inscricoes` — Minhas inscrições

A entrada padrão depois da autenticação.

| Situação | Resposta |
|---|---|
| Com inscrições | `200`, todas e somente as da identidade, mais recente primeiro (`FR-058`) |
| Sem inscrições | `200`, convite a consultar os processos seletivos, sem aparência de erro (`FR-061`) |

Cada item traz Edital, Perfil, situação, protocolo quando houver, e **uma** ação principal:
`Continuar inscrição` para rascunho, `Acompanhar` para enviada (`SC-018`).

---

## `GET /inscricoes/{id}/` — a inscrição

Rota **já existente**, da `009`. Passa a servir também a conferência do que foi submetido.

| Situação | Resposta |
|---|---|
| Inscrição da própria identidade, em rascunho | `200`, a jornada existente, retomada (`FR-059`) |
| Inscrição da própria identidade, enviada | `200`, oportunidade, situação, protocolo, instante, versão aceita, dados e documentos (`FR-067`) |
| Inscrição de outra identidade | `404` — a resposta não permite descobrir que ela existe (`FR-086`) |

Nada nesta rota edita inscrição enviada, substitui documento ou cancela (`FR-075`).

---

## `GET /inscricoes/{id}/documentos/{requisito}/arquivo` — o documento

Rota **já existente**. Reutiliza o armazenamento privado e a autorização da `009` (`FR-071`).

| Situação | Resposta |
|---|---|
| Documento da própria inscrição | `200`, exatamente o arquivo vigente naquela inscrição (`FR-069`) |
| Documento de outra identidade | `404` (`FR-086`) |

Visualizar ou baixar não altera a inscrição (`FR-070`).

---

## `GET /inscricoes/{id}/comprovante` e `/comprovante.pdf`

Rotas **já existentes**. Devolvem o comprovante produzido no envio, com as evidências de integridade
preservadas (`FR-072`, `FR-074`). Não existe segunda modalidade de comprovante.

---

## `GET /inscricoes/{id}/acompanhamento` — o acompanhamento

Dois blocos visualmente distintos (`FR-076`):

- **Sua participação** — fatos da própria inscrição, e apenas os que aconteceram (`FR-077`).
- **Cronograma do processo** — derivado da versão consolidada vigente.

Divergindo a versão vigente da versão aceita, a página avisa e dá acesso ao texto vigente, sem
alterar a versão aceita e sem reabrir nada (`FR-078`, `FR-079`).

---

## `GET /conta` — acesso à conta

Lista as credenciais verificadas, indica a principal, e oferece as ações abaixo.

## `POST /conta/emails` — adicionar credencial

| Situação | Resposta |
|---|---|
| Endereço aceitável | `302` para a confirmação por código, finalidade `adicionar_credencial` (`FR-016`, `FR-028`) |
| Endereço que já pertence a outra identidade | recusa que **não** revela a quem pertence (`FR-017`) |

CPF não é pedido em nenhum momento (`FR-016`).

**A mensagem do código é a da finalidade** (`FR-082a`): aqui ela diz que quem obtiver o código passa
a entrar numa conta **por este endereço** — o oposto do que a mensagem de login diz, e o que é
verdade neste caso.

**Confirmada a adição**, a credencial principal recebe aviso da mudança (`FR-018b`).

## `POST /conta/emails/{id}/principal` — escolher a principal

Passa a alimentar a Inscrição. Os rascunhos abertos acompanham; as enviadas não mudam (`FR-014`).

## `GET|POST /conta/emails/{id}/remover` — remover credencial

O `GET` **pergunta**, e o `POST` executa. A pergunta enuncia o que se perde, no mesmo formato da
confirmação de descarte de documento (`FR-018a`): o botão apagava no primeiro clique, e errar o alvo
custava uma via de acesso descoberta só na tentativa seguinte de entrar.

| Situação | Resposta |
|---|---|
| `GET`, credencial própria | `200` com a pergunta; nada é removido |
| `GET`, credencial única | `200` explicando que é por ela que a pessoa entra, sem oferecer o botão |
| `GET` ou `POST`, credencial de outra identidade | `404`, a mesma recusa da titularidade |
| Há outra credencial, e a removida não é a última | remove; nenhuma inscrição é alterada (`FR-019`) |
| É a última credencial | recusa (`FR-018`) |
| É a principal, havendo outras | outra é promovida, e é ela que recebe o aviso (`FR-018b`) |

## `GET|POST /meus-dados` — o núcleo mínimo, pedido uma vez

Esta é a rota que a implementação deu à correção de nome e CPF. Ela vive fora da jornada de
inscrição de propósito: a `009` não é reaberta, e o que mudou foi de onde vêm os dados que ela
consome, não a jornada que os usa.

| Situação | Resposta |
|---|---|
| Sem sessão | `302` para `/acesso` |
| `GET` | `200`, com o que a identidade já sabe; sem `no-store` seria dado pessoal no cache de um computador compartilhado |
| `POST` com nome | aceito a qualquer momento; rascunhos acompanham, enviadas não mudam (`FR-008`, `FR-014`) |
| `POST` com CPF, sem nenhuma inscrição enviada | aceito, validada a formação (`FR-006`) |
| `POST` com CPF, havendo inscrição enviada | ignorado — congelou, e corrigi-lo passou a ser ato institucional |
| Nome ou CPF malformado | `200`, com a recusa junto do campo e o que foi digitado preservado |

Quem chega aqui a caminho de uma vaga volta para ela ao terminar; quem chega pela conta volta para a
lista.

> **A rota `/conta/dados` prevista no desenho não existe**: a correção acontece em `/meus-dados`,
> acima, que é a mesma tela onde o núcleo é pedido pela primeira vez. Duas rotas para o mesmo
> formulário seriam duas telas a manter dizendo a mesma coisa.

---

## Auditoria destas rotas

Associação e remoção de credencial entram na trilha existente, com escopo institucional vazio, porque
o ato não pertence a Edital algum. Consequência declarada: **não aparecem** na consulta administrativa
de auditoria, que filtra por escopo (`FR-089`, D-012). Código inválido não gera evento de negócio;
tentativas excessivas, bloqueios e autenticação bem-sucedida são registrados como segurança técnica,
sem código, sem CPF completo e sem conteúdo de documento (`FR-088`).

---

## `POST /inscricoes/{id}/` — guardar ou avançar

A mesma rota da tela da inscrição, com um campo a mais decidindo para onde ir depois.

| Situação | Resposta |
|---|---|
| `acao=guardar` | grava e `302` de volta à própria tela, com a lista de documentos recalculada e uma confirmação (`FR-061a`) |
| Sem `acao` | grava e `302` para a revisão — o comportamento de sempre, e o que acontece sem JavaScript |
| A modalidade escolhida invalida documento já enviado | a confirmação de descarte vem antes, em qualquer dos dois casos, e leva `acao` adiante |

O campo de modalidade submete com `acao=guardar` ao mudar. Sem JavaScript ele não submete nada, e a
escolha é gravada ao clicar em "Revisar inscrição": os dois caminhos gravam, e só o momento difere.
