# Contrato — o canal do candidato

**Feature**: 018 · **Canal**: `portal/`, HTML, atrás de titularidade · **Spec**: [spec.md](../spec.md)

Tudo aqui é servido pelo portal e protegido por `exigir_titularidade`, que compara
`inscricao.identity_subject` com o `subject` da sessão e recusa com **404** — nunca 403, porque dizer
"existe, mas não é seu" já entrega que existe. Nenhuma rota nova de API: o candidato não tem API.

---

## 1. Resultado da Etapa no acompanhamento

**Onde**: acréscimo a `portal:acompanhamento`, sem rota nova.

**O fato autorizador** (FR-014): existe `PublicacaoResultado` vigente de um marco do Perfil da
Inscrição, e esse marco enumera a Etapa N na versão que o ato dela cita.

**O que aparece, por Etapa autorizada:**

| campo | origem |
|---|---|
| nome da Etapa | rótulo da versão que o ato cita |
| consequência | `ResultadoEtapa.consequencia`, em texto institucional |
| motivo | `ResultadoEtapa.motivo`, como escrito |
| pontuação | quando a forma a tiver |
| correção | quando o vigente for sucessor: que corrigiu o anterior, por qual decisão e quando |

**O que nunca aparece**: Resultado de outro candidato, lista de Resultados, Avaliação, parecer,
nome de avaliador, identificador técnico, enum canônico.

**Recusas e vazios**

| situação | resposta |
|---|---|
| nenhuma publicação vigente de marco do Perfil | o bloco não existe |
| marco publicado que não enumera a Etapa | aquela Etapa não aparece |
| titular não é o da sessão | 404 uniforme |

**Consultas**: três, constantes entre 1 e N marcos (T-009). A norma vem da versão que o **ato** cita
— nunca da vigente —, por `conteudos_das_versoes`, uma linha por versão distinta.

---

## 2. Interpor recurso

**Rota**: `POST portal:recorrer` (`inscricoes/<uuid>/recorrer`), com `GET` para o formulário.

**Entrada**

| campo | obrigatório | observação |
|---|---|---|
| objeto atacado | sim | identidade da publicação **ou** do Resultado da Etapa, e exatamente uma |
| assinatura do objeto lido | sim | o que a tela apresentou; é o que a FR-009 revalida |
| fundamentação | sim | texto; vazio recusa |
| chave de idempotência | sim | reserva antes de gravar |

**Saída, em sucesso**: o recurso, com protocolo, instante, objeto atacado nomeado em linguagem
institucional e — havendo janela computável — os instantes de abertura e encerramento.

**Recusas**

| código | HTTP | quando | o que a mensagem diz |
|---|---|---|---|
| `not_found` | 404 | não é titular; objeto inexistente; objeto que não lhe diz respeito | recurso não encontrado |
| `appeal_reason_required` | 422 | fundamentação vazia | recurso sem fundamento não é peça |
| `appeal_target_superseded` | 409 | o objeto lido foi superado antes da confirmação | nomeia o objeto vigente e oferece o caminho |
| `appeal_window_closed` | 422 | janela declarada e encerrada | cita a norma, a abertura e o encerramento |
| `appeal_not_provided` | 422 | o marco declara que **não** admite recurso (FR-113) | encaminha à comissão do certame |
| `appeal_already_filed` | 409 | já há recurso deste titular contra este objeto | nomeia o protocolo da primeira peça |
| `appeal_not_visible` | 404 | o Resultado da Etapa não é visível ao titular (o fato de D-003 não ocorreu) | recurso não encontrado |

**Dois códigos, e não um, para o que parece a mesma recusa.** `appeal_window_closed` diz que o
prazo passou; `appeal_not_provided` diz que o recurso não é previsto naquele marco. Um código só
obrigaria o cliente a ler a mensagem para distinguir "chegue mais cedo" de "não é por aqui" — e são
duas orientações opostas para quem as recebe (FR-113).

**Idempotência**: repetir a mesma chave devolve o desfecho da primeira e não cria segunda peça
(FR-010). A reserva cobre o **pedido inteiro** — a fundamentação e a identidade do objeto atacado:
sem o objeto, a mesma chave usada contra outro alvo devolveria a primeira peça em silêncio, e quem
recorreu de duas coisas sairia com o protocolo de uma só. Chave igual com conteúdo diferente é
conflito (FR-098).

**A ação não é oferecida** quando a interposição não é possível — janela fechada, objeto já
recorrido, objeto não visível. A recusa existe para quem chega por outro caminho, e não como
comportamento normal da tela (FR-013).

---

## 3. Acompanhar e ler a decisão

**Rota**: `GET portal:recurso` (`recursos/<uuid>`), e um resumo dentro do acompanhamento.

**O que o titular vê, em linguagem institucional:**

```text
protocolo · instante · objeto atacado · a própria fundamentação
   ↓
admissibilidade   →  admitido | não admitido, com o motivo escrito
   ↓
decisão           →  a espécie, em texto; a motivação; quem decidiu; quando
   ↓
efeito            →  o que mudou, quando houve mudança
```

**A espécie em texto, e nunca o enum:**

| espécie | como o candidato lê |
|---|---|
| `INDEFERIDO` | "Recurso indeferido" |
| `CORRECAO_FIXADA` | "Recurso deferido — o resultado foi corrigido" |
| `REAVALIACAO_DETERMINADA` | "Recurso deferido — a etapa será reavaliada" |
| `PROVIDENCIA_A_JUSANTE` | "Recurso deferido — a instituição praticará o ato corretivo" |

**O que o titular não vê**: a trilha técnica, o identificador do ato viciado, a proveniência do
cálculo, o nome de quem avaliou. A FR-092 é para a administração e a auditoria; a FR-093 é o que
chega ao candidato.

**Não há notificação.** O candidato descobre consultando, e é por isso que a decisão precisa ser
legível ali (FR-109).

---

## 4. O protocolo

`REC-2026-XXXXXXXX`, mesmo alfabeto do protocolo da Inscrição — sem `0`/`O` e sem `1`/`I`/`L`,
porque ele é ditado ao telefone. Único, opaco, sem sequência.

**O protocolo não é credencial.** Conhecê-lo não dá acesso a nada: a rota exige a sessão do titular,
como todo o resto do portal (FR-104).
