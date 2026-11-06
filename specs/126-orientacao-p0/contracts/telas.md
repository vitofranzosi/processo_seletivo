# Contrato das telas (126)

O que cada tela diz e oferece, verificável por teste. Os textos passam pela varredura de vocabulário.

## A1 — Sucessão recolhida (FR-4010 a FR-4013, UX-223)

| Tela | Rótulo do bloco | Aberto quando |
|---|---|---|
| Corte | "Suceder este corte (exige motivo)" | `corte_obsoleto` |
| Ordem | "Suceder esta ordem (exige motivo)" | `obsoleto` (e recalculável), ou há decisão de recurso a citar |
| Ocupação | "Suceder esta apuração (exige motivo)" | estado do recorte `OBSOLETE` |
| Sorteio | "Suceder esta relação (exige motivo)" | relação com diagnóstico (nunca sortearia) |

- O bloco é `<details class="sucessao">`, com o formulário de hoje dentro (motivo obrigatório).
- O botão de dentro mantém rótulo e desenho (o guardião `test_nenhum_botao_muda_de_rotulo_desenho_ou_lugar`
  os prende): o que tira o peso dele é estar recolhido.
- A primeira emissão (sem ato vigente) continua fora de qualquer bloco.

## A1 — Mensagens de sucesso (FR-4014 a FR-4018)

| Ato | Frase |
|---|---|
| Corte | "Corte emitido para <recorte>: N progride(m), até a Xª posição." + ", sucedendo a geração anterior" quando sucede. "O ato é imutável, e quem ficou fora continua legível nele." |
| Faixa seguinte | "Faixa seguinte emitida para <recorte>: N progride(m) nela, até a Xª posição." |
| Ordem | "Ordem emitida para <recorte>: N com posição, M sem posição. O ato é imutável e já pode ser consultado." |
| Apuração | "Apuração emitida para <recorte>: E vaga(s) efetiva(s), O ocupada(s), F a ocupar. O ato é imutável; corrigir é emitir uma sucessora com motivo." |
| Relação | "Relação publicada e congelada — <recorte>, com N participante(s)." + o resumo (o prefixo de antes fica: outras telas e testes o leem) |

Sem navegação de recortes (Perfil com um só), "para <recorte>" é omitido.

## A2 — Lista sem inscrito (FR-4019 a FR-4026, UX-224)

- Condução, célula: texto "Não se aplica", nota "nenhuma inscrição nesta lista", `data-estado="nao_se_aplica"`, sem link.
- Condução, todos sem inscrito: "**Nada a conduzir neste marco.** Nenhuma inscrição enviada declarou as listas dele." Sem seção de gestos; a legenda de totais diz "Nenhuma operação se aplica a este marco."
- Conferência do gesto: situação `fora`, razão "Nenhuma inscrição nesta lista: não há relação, ordem nem apuração a praticar nela."
- Convocação: "**Não se aplica.** Nenhuma inscrição enviada declarou esta lista: não há ocupação a apurar nem quem convocar neste recorte." Sem "Ir para a apuração de ocupação", sem o gesto de titulares, sem a seção da fila.
- Convocação sem corte, fila vazia: "Não há mais quem chamar na ordem deste recorte." Sem link para a faixa seguinte.
- Ocupação: "**Não se aplica.** Nenhuma inscrição enviada declarou esta lista: não há ordem a emitir nem ocupação a apurar neste recorte."

## A4 — Convocação no relatório e no Encerrar (FR-4027 a FR-4030, UX-225)

- Pendência nova: "N convocação sem comunicação enviada" / "N convocações sem comunicação enviada", sem data.
- No resumo de vagas do relatório: "N sem comunicação enviada".
- Consolidado: rótulos "convocação sem comunicação enviada" / "convocações sem comunicação enviada"; coluna "Sem comunicação enviada" na tabela do PDF.

## A5 — Aviso de congelamento (FR-4031 a FR-4034, UX-226)

- Topo dos recortes: o aviso da `102`, sem a frase "Vale também para publicar relação nova…", só se `inscricoes_correndo` ou `inclui_congelamento`.
- Dentro de "Suceder esta relação", quando o aviso existe e a relação não tem diagnóstico: "**A relação nova seria congelada hoje, e o sorteio dela seria recusado.** A extração do Edital (<referência> de <fonte>) é de dd/mm/aaaa, e o sorteio só aceita extração de dia posterior ao congelamento. Antes de suceder, retifique o Edital (ou peça a quem elabora as Retificações), trocando a extração por uma a partir de dd/mm/aaaa."

## A6 — Confirmação da ordem (FR-4035 a FR-4039, UX-227)

- Seção "Inscrições sem resultado nas Etapas deste marco", quando `sem_resultado > 0`:
  - com `nenhuma_com_resultado`: "**Nenhuma inscrição deste recorte tem resultado nas Etapas que o marco enumera.** Emitida agora, a ordem grava todas sem posição."
  - senão: "**N das M inscrições consideradas estão sem resultado numa Etapa que o marco enumera**, e ficam sem posição por isso."
  - lista: "<Etapa>: K sem resultado" por Etapa.
  - consequência: "Quando os resultados forem consolidados, esta ordem ficará obsoleta, e sucedê-la exigirá motivo."
- "Participantes sem posição": por grupo, "K — <motivo> (protocolos)".
- O botão "Emitir a ordem" continua.
