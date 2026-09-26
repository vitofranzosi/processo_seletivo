# Contrato — a lista exigida da inscrição

**Feature**: `044-recorte-transversal-documental` · **Data**: 2026-09-25

> **O que é público aqui:** a tabela e as garantias dela, que outras features vão ler, e o que a
> Mesa, a consulta administrativa e o portal mostram a partir dela. Nenhum endpoint novo, nenhuma
> permissão nova.

---

## 1. A gravação

- **Quando:** no ato do envio, em `enviar_inscricao`, na mesma transação que põe a inscrição em
  `SUBMETIDA` e grava os fatos declarados.
- **O quê:** uma linha por Documento Exigido da versão que o envio registra como aceita, com
  situação, recorte e divergência (`data-model.md`, §2).
- **Garantias no banco:** as linhas não se alteram nem se apagam (privilégio + gatilho). Toda linha
  inserida pertence a uma inscrição `SUBMETIDA`, da versão aceita por ela, no instante do envio.
- **Idempotência:** o reenvio com a mesma chave não chega à gravação. A unicidade
  `(inscricao, requisito_id)` é a segunda barreira.
- **Auditoria:** nenhum evento próprio. O evento `SUBMETER`, que já existe, cobre o ato (`FR-729`).

---

## 2. A leitura

`lista_exigida(inscricao, conteudo) → ListaExigida(itens, reconstruida)`

| A inscrição | O que devolve |
|---|---|
| enviada, com linhas | as linhas, na ordem dos documentos na versão aceita; `reconstruida=False` |
| enviada antes da feature, sem linhas | `aplicabilidade` sobre a versão aceita; `reconstruida=True` |
| em rascunho | não é chamada: o rascunho continua lendo a versão vigente |

**Nenhum leitor de inscrição enviada recalcula o recorte fora desta função.** Os leitores: a Mesa, a
consulta administrativa (lista e detalhe) e a inscrição enviada no portal (a página e o comprovante).

**Autorização:** a de cada tela, sem mudança (`FR-728`). A lista não tem rota própria.

---

## 3. A Mesa — os três estados (`FR-718`, `UX-081`, `UX-082`, `UX-083`)

```text
Documentos pedidos
  Documento de identidade        obrigatório   pedido de todos os candidatos
                                               Abrir · 1,2 MB           aberto
  Laudo médico                   obrigatório   pedido de quem concorre em Pessoas com Deficiência,
                                               em todos os Perfis
                                               Abrir · 800 KB
  Autodeclaração de deficiência  facultativo   pedido de todos os candidatos
                                               não apresentado

Não se aplicam a esta inscrição
  Autodeclaração étnico-racial   Não se aplica: pedido de quem concorre ao Perfil C1 em PPIQ
```

- Os pedidos vêm primeiro. Os que não se aplicam vêm depois, sob um título próprio, e se distinguem
  pelo título e pelo texto, sem depender de cor.
- O facultativo traz a marca *facultativo*. Hoje ele não traz marca nenhuma.
- A instrução do documento, que o PR #167 leva à Mesa, continua abaixo do nome.

**Lista reconstruída**, acima da lista, uma vez:

> Esta inscrição foi enviada antes de o sistema gravar a lista de documentos pedidos. A lista abaixo
> foi reconstruída a partir da versão do Edital que ela aceitou.

**Divergência do publicado** (`FR-727`), no item:

```text
  Laudo médico   Não se aplica: pedido de quem concorre ao Perfil C1 em Pessoas com Deficiência
                 — o Edital publicado o exigia de todo candidato em Pessoas com Deficiência.
                 O portal não o pediu a esta inscrição.
```

---

## 4. A consulta administrativa (`FR-719`)

- **Lista "Inscrições recebidas":** a coluna "Documentos" continua *"{recebidos} de {esperados}"*,
  com `esperados` = itens `OBRIGATORIO` da lista, e `recebidos` = os que têm `DocumentoSubmetido`. O
  número de consultas da página continua independente do número de inscrições.
- **Detalhe:** os mesmos três estados e a mesma razão da Mesa. O aviso de lista reconstruída também.
- **Seção "em preenchimento":** inalterada. Rascunho não tem lista.

---

## 5. O portal (`FR-720`)

- A página da inscrição enviada e o comprovante tiram as linhas da lista. Continuam mostrando só os
  documentos **enviados**, como hoje.
- O código de verificação não muda: ele é calculado sobre os arquivos, e não sobre a lista.
