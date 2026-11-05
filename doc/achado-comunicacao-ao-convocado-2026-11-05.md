# Achado — o convocado só sabe dos documentos se entrar no portal

Verificado em 05/11/2026 sobre a `main` em `7a4f7aec`, percorrendo a jornada do candidato num banco
de demonstração (`ps_demo_conv_kit`, Edital 72/2026, montado pelas fixtures da `117` e da `118`): a
mensagem de convocação, a entrada por código, o acompanhamento, a convocação e o envio de um
documento. Nenhum código foi alterado.

> **Não vira escopo por estar escrito aqui.** As duas lacunas já têm nome nas specs — X3 da `118` e
> QI-7 da `115` — e as duas esperam decisão do usuário. Este registro junta o que se vê do lado do
> candidato, para que a decisão se tome olhando a jornada inteira, e não cada spec.

> **Desfecho (05/11).** As duas perguntas da tabela "O que decidir" foram respondidas no
> [estudo da experiência da convocação](estudo-experiencia-da-convocacao-2026-11-05/README.md),
> que partiu deste registro, e entraram na spec
> [`121`](../specs/121-experiencia-da-convocacao/spec.md):
> - a **X3** entra no incremento 1, pela D-4 do estudo: a mensagem diz quando a chamada pede
>   documentos, e a da sucessora diz que corrige a anterior;
> - a **QI-7** fica fora dele, pela D-5: o aviso de pendência espera decisão institucional e de
>   privacidade própria.
>
> O texto abaixo é o de quando o achado foi registrado, e não foi atualizado.

## Resumo

Desde a `115`, a convocação pode pedir documentos, e o portal da `118` diz bem o que falta. Mas o
**canal que chega à pessoa** — o e-mail — continua o mesmo de antes da `115`:

1. **A mensagem de convocação não diz que há documentos a enviar.** Ela manda "acessar a sua área e
   seguir as instruções", com o prazo. Quem lê não sabe que precisa juntar certidão, histórico e
   comprovante antes de o prazo vencer, nem quantos são.
2. **Depois da mensagem, nada mais chega por e-mail.** Pendência registrada, documento conferido,
   prazo perto do fim: a pessoa só descobre entrando no portal. Uma pendência registrada no quarto
   dia de um prazo de cinco é, para quem não voltou ao portal, um prazo perdido.

## O que a pessoa recebe hoje

O corpo é o de `convocacao/application/comunicar.py` (`CORPO`, linhas 48–59):

```text
Você foi convocada(o) no Edital 72/2026.

Prazo para atender: até 10/11/2026 às 09:40, contado do envio desta mensagem.

O que fazer: acesse a sua área e siga as instruções da convocação em
http://‹endereço›/selecoes/inscricoes/

Em caso de dúvida, fale com ‹canal da unidade›.
```

É o mínimo da FR-290 da `019` (o que fazer, o prazo, o canal, sem dado da inscrição), e o link não
autentica (P-001 da `010`): a entrada é por e-mail e código de seis dígitos. Nada disso é defeito, e
nada disso precisa mudar. O que falta é **uma frase**: a FR-290 foi escrita quando "o que fazer" era
comparecer ou responder, e não enviar documentos pelo portal.

A `118` já viu isso e o deixou de fora de propósito (`specs/118-jornada-consolidada-do-convocado/spec.md`,
linha 1014 e item X3 da linha 1225): *"a frase 'esta convocação pede documentos' fica para decisão
própria"*, junto com a variante da mensagem da sucessora — a correção da `120` reenvia a mesma
mensagem com o prazo novo, e ela não diz que corrige a anterior (`convocacao/application/fluxo.py`,
`_FRASE_DA_COMUNICACAO`).

## O que a pessoa não recebe

A FR-084 da `010` limita o e-mail, além do código de acesso, a **quatro** situações nominais: a
confirmação do envio da inscrição, o aviso de endereço que passou a alcançar a conta, a convocação e
o aviso complementar da `066`. Acrescentar uma quinta exige revisar a regra, e o guardião
`tests/test_situacoes_de_mensagem.py` reprova sem a revisão. O aviso da `066` não serve aqui: ele é
vinculado a ato oficial publicado, e a conferência de um documento não é ato publicado. Por isso:

- a **pendência** registrada pela comissão (com o motivo que o portal mostra) não gera aviso — é a
  QI-7 da `115` (`specs/115-documentos-na-convocacao/spec.md`, linha 1294) e o MAT-13 da auditoria de
  matrícula (`doc/auditoria-matricula-e-dossie-documental-2026-11-03.md`, linha 534);
- a **conferência** e o **desfecho** também não. Para o desfecho isso é coerente com o resto do
  sistema — resultado se publica, não se avisa —, mas para a pendência a ausência tem custo direto:
  ela pede uma ação dentro de um prazo que já está correndo.

No portal, o que a pessoa vê ao voltar está certo: o cartão sobe para o topo como *"Precisa de
correção"*, com o motivo, e o acompanhamento diz *"Você ainda precisa corrigir 1 documento…"*. O
problema é só que ninguém a chama de volta.

## Verificado e descartado

O atendimento apareceu como *"o atendimento institucional"* na convocação do portal e como *"a
comissão do certame"* na mensagem. É artefato da demonstração: a unidade semeada não tem canal, e o
`development` não declara `PORTAL_ATENDIMENTO`. Em produção, `config/settings/production.py`
(linhas 204–210) recusa subir sem ele, e `Identificacao.canal` (`unidades/application/identificacao.py`,
linha 62) recai no canal da instituição quando a unidade não declara o seu.

## O que decidir

| | Pergunta | Onde mexeria | Custo aproximado |
|---|---|---|---|
| **X3** | A mensagem de convocação diz quando a chamada pede documentos? E a da sucessora diz que corrige a anterior? | revisão da FR-290 da `019`; `CORPO` em `comunicar.py`, com a lista da chamada já gravada no ato de convocar | pequeno: o dado existe na hora do envio, e a mensagem continua uma só |
| **QI-7** | A pendência registrada gera aviso por e-mail? | revisão da FR-084 da `010` (quinta situação) e do guardião; o envio síncrono (A-04 da auditoria) pesa se for por conferência | médio: regra nova de mensagem, com o mesmo cuidado de dado mínimo da FR-290 |

As duas são independentes: a X3 melhora a primeira mensagem sem criar situação nova; a QI-7 cria. Se
só uma couber agora, a X3 é a mais barata e já evita o caso de quem descobre os documentos tarde.

## Como reproduzir

No banco de demonstração, entre no portal com `formalizacao10@exemplo.test` (Bruna, nada enviado) e
`formalizacao11@exemplo.test` (Diego, histórico pendente); o código sai no terminal do `runserver`.
O corpo da mensagem de convocação está no mesmo terminal, no momento em que a comissão comunica.
