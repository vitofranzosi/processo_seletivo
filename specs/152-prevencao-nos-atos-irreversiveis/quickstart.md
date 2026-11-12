# Quickstart: verificar a 152 pela interface

A verificação refaz os passos do estudo da jornada final de 11/11/2026, onde os achados foram
vistos. O "antes" são as capturas do estudo, em `doc/estudo-jornada-final-2026-11-11/img/`.

## Pré-requisitos

- Banco migrado e provisionado (`make preparar`; ver o CLAUDE.md).
- Runserver com `INTERFACE_SELETOR_IDENTIDADE=true`, e o correio local (console ou mailpit) para os
  códigos e as mensagens.
- Cenários de treinamento C09 e C11 carregados:

```bash
CENARIOS_DE_TREINAMENTO=true uv run python manage.py carregar_cenarios_de_treinamento --banco processo_seletivo --cenario C09 --cenario C11
```

## 1. O atalho do indeferimento (achado 04)

Para o vocabulário de "apresentado", ver o [data-model](data-model.md).

1. **C11, como presidência, abra a convocação do recorte e o cartão de Alice** (nada enviado, prazo
   em curso). O atalho "Indeferir pelas pendências de documento" **não** aparece (SC-1900). O
   passo continua "Aguardando o candidato enviar 2 documentos".
2. **No desfecho geral de Alice, escolha "Indeferimento" e registre sem a marca de ciência.** A
   tela recusa com a frase da ciência, devolve o fundamento digitado, e nenhum desfecho é gravado
   (SC-1901). Marque e registre: o desfecho é gravado, e a trilha mostra a ciência com o vencimento
   (FR-5806).
3. **Faça Bernardo enviar os dois documentos pelo portal; na página dos documentos, marque um
   conforme e outro pendente com motivo.** O atalho aparece no cartão dele, e o fundamento cita só
   o pendente e o motivo (FR-5800, FR-5801). Com o prazo em curso, o atalho pede a ciência
   (FR-5803).
4. **Num terceiro convocado, com o vencimento decorrido e nada enviado**, o atalho não aparece. O
   passo diz que nada foi apresentado no prazo e aponta "Não atendimento à convocação" (FR-5809,
   SC-1910).
   - Para chegar lá: chame alguém da fila com vencimento de poucos minutos (a data e a hora são
     livres) e espere decorrer, sem enviar nada pelo portal.

## 2. A chamada individual e o corte (achado 08)

1. **C09, depois da desistência de Cecília, abra "Chamar uma pessoa da fila", escolha Davi e clique
   em "Conferir antes de convocar".** Na conferência:
   - aparecem Davi, "para vaga que vagou", o fundamento, o e-mail e o prazo;
   - nenhuma convocação nasceu e o correio não recebeu nada (SC-1902);
   - ao confirmar, nasce uma convocação e sai uma mensagem;
   - um segundo envio do mesmo formulário não produz outra (SC-1903).
2. **Escolha Estela no lugar de Davi, sem a marca de precedência.** A conferência recusa sem botão.
   Com a marca, ela diz que Estela passa à frente de Davi (FR-5812).
3. **Num recorte sem corte emitido, clique em "Conferir antes de emitir".** A página "Confira antes
   de emitir o corte" mostra a faixa e quem fica fora, e nenhum corte é gravado. Ao confirmar, o
   corte é emitido (SC-1904).
4. **Com corte vigente, peça a faixa seguinte com quantidade 2.** A conferência mostra as duas
   posições e as pessoas alcançadas. Uma quantidade além do resto da ordem não é recusada: a
   conferência mostra a quantidade pedida ao lado de quantas pessoas a faixa alcança — só quem
   resta, às vezes ninguém —, antes do botão (FR-5829).

## 3. O seletor do desfecho e o atestado (achado 12)

1. **C09, abra o desfecho de Alice** (tudo conforme, prazo em curso, sem atestado).
   - O seletor oferece Aceite, Indeferimento, Desistência expressa e Reclassificação.
   - A nota "Ainda não cabem nesta chamada" nomeia o não atendimento (com a data do vencimento) e o
     cancelamento por inércia (com a exigência do atestado).
   - "Regularização" não aparece em lugar nenhum (SC-1905).
2. **Numa chamada para regularizar**, "Atestar fato externo" não aparece, e Aceite e inércia também
   não (FR-5840, FR-5837).

## Suíte

```bash
cd backend && make lint check test-pg
```

Os arquivos novos estão no plano (seção 7). Os casos de domínio dos desfechos cabíveis rodam sem
banco. Os da conferência e da ciência são transacionais onde a trava importa.
