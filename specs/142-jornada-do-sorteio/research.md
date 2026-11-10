# Research: A tela do sorteio como a jornada de quem o conduz (142)

As decisões de produto estão na spec (`D-001` a `D-007`). Aqui ficam as questões técnicas.

## T-001 — De onde vem a situação de cada passo

- **Decisão**: das células do andamento (`andamento.do_edital(..., perfis=[perfil])`), pelos pontos
  `RELACAO`, `SEMENTE`, `SORTEIO` e `RESULTADO` do marco.
- **Por quê**: é a fonte que o Centro lê. As funções `situacao_*` são puras, mas os fatos delas não
  estão todos no contexto da tela (a célula da ordem do indicador da condução, a habilitação da Etapa,
  o fim do período): montá-los aqui seria a segunda leitura.
- **Alternativa descartada**: chamar `situacao_da_relacao` etc. com os fatos da tela — diverge na
  primeira célula que a `127` mudar.

## T-002 — O custo

- **Medido** no C06, depois de dois sorteios: ver `verificacao.md`. O "Próximo nesta lista" lia a
  derivação depois de cada ato; passa a receber a mesma leitura da view.

## T-003 — A ordem gravada

- **Decisão**: `sorteio.ato.posicoes`, ordenadas por posição, com `inscricao` em `select_related`, e o
  número público lido das participantes da relação do sorteio (`relacao.participantes`), por inscrição.
- **Por quê**: é o ato constituído — o mesmo que a página pública de verificação reproduz. Não é
  prévia: só existe depois do ato.

## T-004 — A âncora da execução

- **Decisão**: `sorteio-<lista|ampla>`, ao lado de `recorte-<lista|ampla>`; a seção é
  `titulo-execucao`. A mesma função alimenta a derivação e o filtro do template, como a `139` fez com
  a do recorte.

## T-005 — A situação do passo da semente para quem tem várias listas

- A célula da semente é a mesma em todas as listas (`Ponto.celulas`); o passo 2 lê a primeira, uma
  vez, e não a repete por lista (FR-4906).
