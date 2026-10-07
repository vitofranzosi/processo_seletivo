# Contrato — o bloco de situação e os cartões do acompanhamento

A tela é `GET /selecoes/inscricoes/<id>/acompanhamento` (`portal:acompanhamento`), privada e atrás
da titularidade, como hoje. Este contrato fixa **o que** ela diz em cada situação; a redação exata
das frases é a das constantes de `portal/situacao.py` ([D-005](../research.md)).

## 1. Estrutura

```text
h1  Acompanhar
p   <nome do processo>
section.situacao  (aria-labelledby → h2)
  h2  Sua situação
  p.rotulo-da-situacao   <rótulo>          ← texto, não só cor (UX-155)
  h3  Por quê
  ul  <linhas do porquê>
  h3  O que fazer
  p   <ação>  [link]
  p   <prazo / aviso de prazo>
  p   <consequência>
  p   <canal>   p <cadastro reserva>
  p   <recurso: até dd/mm/aaaa às HHhMM>  [Recorrer de um resultado]
p.aviso           Edital atualizado após a inscrição        (quando houver, FR-079)
section           Convocação — dados e "Ver convocação"     (quando houver, D-008)
h2  Classificação por lista                                 (quando houver cartão)
  section.cartao-de-lista ×N
    h3  <lista> — <marco>
    p   <natureza> · publicado em dd/mm/aaaa
    p   <Nº lugar [— posição compartilhada] · pontuação X,XX>  |  Sem posição nesta lista + motivo
    p   Cabe recurso contra este resultado até …            (quando aberto)
    a   Ver o resultado completo  → publicação vigente
h2  Resultado das etapas … (como hoje)
h2  Seus recursos … (como hoje)
h2  Sua participação … (como hoje)
h2  Cronograma do processo … (como hoje)
a   Ver o que enviei
```

## 2. O que cada situação preenche

| Situação | Porquê | Ação | Prazo | Consequência | Canal / reserva | Recurso |
|---|---|---|---|---|---|---|
| Vaga aceita e demais desfechos | fundamento e data do registro; lista e chamada da convocação | Nada por enquanto. | — | — | — | se houver objeto |
| Convocado | espécie, lista, nº da chamada, data | Preencher o Requerimento de Matrícula / Requerimento enviado — conferir / Siga as instruções do Edital para esta convocação. | vencimento; ou "o prazo ainda não começou" (sem envio bem-sucedido); ou "o prazo terminou em …; o resultado da convocação ainda não foi registrado" (vencimento decorrido, sem desfecho) | "Se você não atender no prazo, a comissão poderá registrar o não atendimento desta convocação." — **só** com envio bem-sucedido, vencimento registrado e prazo não encerrado; nos demais casos, nenhuma | — | se houver objeto |
| Eliminado | etapa e motivo | Nada por enquanto. | — | — | — | se houver objeto |
| Aguardando chamada | cada lista com posição, natureza, etapa e data | Nada por enquanto. | — | "Novas chamadas, se houver, serão publicadas conforme o Edital." | se o Perfil declarar | se houver objeto |
| Aguardando resultado definitivo | cada lista, e "a classificação é preliminar e pode mudar" | Nada por enquanto. | — | — | — | se houver objeto |
| Não classificado | cada lista com o motivo | Nada por enquanto. | — | — | — | se houver objeto |
| Inscrição enviada | "Inscrição enviada em dd/mm/aaaa às HHhMM." | Nada por enquanto. O resultado será publicado conforme o Edital. | — | — | — | — |

## 3. Invariantes que os testes prendem

1. O bloco de situação é o primeiro `section` depois do subtítulo, e as três partes estão sempre
   presentes (SC-450).
2. A posição de cada cartão é a de `SituacaoDivulgada.posicao`, sem transformação (SC-451).
3. Nenhuma das palavras da UX-158 no HTML renderizado de nenhum cenário (SC-452).
4. Frase de consequência só das constantes (SC-453), e nenhuma afirmação de perda automática.
   Na varredura do requerimento (UX-058), só a cadeia exata "Indeferido na convocação" é retirada
   antes de procurar `deferid`; qualquer outra ocorrência reprova.
5. O número de consultas não depende de quantas listas e marcos a inscrição tem (SC-454).
6. Sem convocação, zero consulta ao requerimento (decisão 006 da `059`, `test_orcamento_de_consulta`).
7. Nenhum texto do corte nem da apuração (`FR-1169`, `FR-1171`): a função não os recebe.
