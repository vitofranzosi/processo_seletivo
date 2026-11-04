# Achado — a lista de documentos da convocação é clara, e o caminho até ela não é

Encontrado em 04/11/2026, relendo pelos olhos do candidato as telas da `115` já mergeada (#369):
as capturas a 375 px de `specs/115-documentos-na-convocacao/capturas/` e os templates do portal.

> **Não vira escopo por estar escrito aqui.** O que se registra são quatro lacunas de clareza em
> volta da lista de documentos, o que cada uma custa e o que corrigir exigiria. Priorizar e decidir
> são do usuário. Nada foi testado com candidato real — a leitura é de quem fez a feature, e
> validação com pessoas diria mais do que ela.

## O que funciona

A lista em si (`portal/templates/portal/_documentos_da_convocacao.html`) cumpre o desenho: um
cartão por documento, a instrução do Edital, a situação em palavras ("Falta enviar", "Recebido…,
aguardando conferência", "Pendente: Falta a página 2. Envie outro arquivo até…"), um botão de
escolher e um de enviar, o reenvio já aberto na pendência, e o cartão verde com ✓ quando conferido.
Cabe a 375 px sem rolagem lateral (capturas `candidato-lista-a-375px.jpg` e
`candidato-pendencia-a-375px.jpg`).

As lacunas estão **fora** do cartão.

## 1. Ninguém avisa o candidato — o maior risco

- O aviso por e-mail da `066` nasce desligado: `AVISOS_AOS_CANDIDATOS` é `false` por padrão em
  `config/settings/base.py:257` e só vem ligado em `development` e `test`. Em produção fica assim até
  a validação de LGPD.
- O aviso de **pendência** nem existe: é a QI-7 da `115`, que revisaria a FR-084 da `010`, e ficou
  em aberto.

**O que custa.** O prazo é um só por chamada (D-019 da `115`): documentos e Requerimento fecham
juntos no vencimento. A comissão que marca pendência no 4º dia de cinco depende de a pessoa voltar
ao portal por conta própria para ver. Se não voltar, o prazo passa com o documento pendente, e a
comissão desfecha por um motivo que a pessoa nunca leu.

**O que corrigir exigiria.** Decisão institucional (LGPD) para ligar a `066` em produção, e uma
spec para a QI-7. Não é texto de tela.

## 2. A tela "Sua situação" não fala de documentos

`portal/situacao.py`, `_acao_da_convocacao` (linha 339): a ação principal é uma de três —
"Preencher o Requerimento de Matrícula.", "Seu Requerimento de Matrícula foi enviado." ou
`SIGA_AS_INSTRUCOES` ("Siga as instruções do Edital para esta convocação.", linha 88) com o link
"Ver convocação". Nenhuma das três diz que há documento a enviar, nem que há pendência.

**O que custa.** Quando o Edital pede o Requerimento **e** documentos na convocação, o botão
principal leva ao Requerimento, e os documentos não aparecem em lugar nenhum do acompanhamento. A
pessoa preenche o Requerimento, lê "Seu Requerimento de Matrícula foi enviado." e tem motivo para
achar que terminou.

**O que corrigir exigiria.** Ler o estado documental da chamada no acompanhamento (a leitura já
existe, `leitura_da_chamada`) e escrever a ação a partir dele: "Envie 2 de 4 documentos",
"1 documento pendente: envie outro arquivo". Mexe na redação das FR-1175 a FR-1177 da `063`, e por
isso pede spec — ou emenda à `115` — e não correção solta.

## 3. Na tela da convocação, a lista fica escondida

`portal/templates/portal/convocacao.html`:

- Antes da lista vêm "Espécie: Para vaga inicial" (linha 38) e "Fundamento: No interesse da
  Administração, item 8.2 do Edital…" (linha 45) — vocabulário do ato, e não do candidato.
- Depois vem "O que fazer: Siga as instruções do Edital para esta convocação dentro do prazo
  acima…" (linhas 57–58), que não aponta para a lista que está logo abaixo (linha 62).
- No celular, a lista começa na metade da segunda tela (`candidato-lista-a-375px.jpg`). Não há
  resumo do tipo "faltam 2 de 4".

**O que custa.** Quem chega pelo link "Ver convocação" lê primeiro o que não entende e depois uma
instrução genérica. A lista é achada por quem rola, não por quem lê.

**O que corrigir exigiria.** Ordem e texto: o "O que fazer" dizer "Envie os documentos abaixo"
quando há documento pedido, e um resumo no topo do bloco. Não muda regra nenhuma. Espécie e
Fundamento continuam — são o ato que a pessoa tem direito de ler —, só não precisam vir primeiro.

## 4. Palavras que confundem

- **"Conforme"** é vocabulário de quem confere. O termo é deliberado — FR-3589 da `115`: conforme
  ao exigido pelo Edital, nunca autêntico —, e "Aprovado" foi evitado por soar como garantia da vaga
  (FR-292c da `019`). Uma alternativa a avaliar é "Conferido: está de acordo com o Edital".
- **"Atendido pelo documento enviado na inscrição em DD/MM"** não diz que não é preciso enviar de
  novo. O PDF do Edital diz — *"Quem enviou X na inscrição não precisa enviá-lo de novo"* (spec da
  `115`, segundo cenário de aceitação da User Story 7) —, e o portal, não.
- **Com o prazo vencido, dois avisos dizem quase o mesmo**: "O prazo informado nesta convocação já
  passou. Isso não decide nada sozinho: fale com o atendimento se você atendeu e não consta."
  (`convocacao.html:51`) e, dentro do bloco, "O prazo terminou em …, às …. A comissão vai decidir."
  (`frase_do_prazo_decorrido`). "Não decide nada sozinho" é difícil de entender
  (`candidata-prazo-vencido-a-375px.jpg`).

**O que corrigir exigiria.** Texto, com a ressalva da FR-3589 e da FR-292c: qualquer redação nova
tem de continuar sem prometer autenticidade nem vaga.

## Custo de cada um

| | Natureza | Precisa de |
|---|---|---|
| 1 | aviso que não existe ou está desligado | decisão de LGPD; spec da QI-7 |
| 2 | acompanhamento sem o estado documental | spec ou emenda (redação da `063`) |
| 3 | ordem e texto da tela da convocação | correção pequena, sem regra nova |
| 4 | redação | correção pequena, dentro da FR-3589 e da FR-292c |

O 2 e o 3 são os mais baratos e os que mais ajudam quem já está no portal. O 1 é o que mais pesa
para quem não está.
