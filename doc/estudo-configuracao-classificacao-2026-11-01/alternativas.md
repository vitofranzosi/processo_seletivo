# Cinco modelos de interação e referências

## Referências investigadas e limites de transferência

Consulta em 01/11/2026, a fontes primárias. A tradução para o GPS abaixo é inferência de design; não evidência de que uma dessas ferramentas resolveria a tarefa do operador.

| Referência | Problema de representação que resolve | O que aproveitar no GPS | Custo que não se deve importar |
|---|---|---|---|
| [Node-RED: conexões entre nós](https://nodered.org/docs/user-guide/editor/workspace/wires) | Mostra como saídas alimentam entradas, com seleção de vínculos | Destacar consumidores da etapa selecionada e diferenciar uso de resultado de governo por corte | Portas e arrasto livre sugerem conexões arbitrárias; habilidade motora e depuração de um grafo virariam tarefa administrativa |
| [Camunda: tabelas de decisão e política de acerto](https://docs.camunda.io/docs/components/modeler/dmn/decision-table-hit-policy/) | Torna explícito como condições combinadas produzem saídas e como tratar múltiplas correspondências | Tabela curta de “quando / efeito”, especialmente mínima, decisão documental e empate no corte | DSL e políticas DMN não existem no GPS; uma tabela livre criaria outro motor normativo |
| [n8n: dados preparados e fixados](https://docs.n8n.io/build/work-with-data/pin-and-mock-data/) | Permite explorar lógica com entradas repetíveis em desenvolvimento | Preservar população fictícia ao comparar regras; destacar origem e natureza dos dados | Dados reais ou execução externa não são necessários na composição; não confundir fixação de exemplo com congelamento jurídico da relação |
| [Bret Victor: níveis de abstração](https://worrydream.com/LadderOfAbstraction/) | Relaciona uma regra abstrata a exemplos concretos e diferentes escalas de observação | Ir da etapa ao marco e à trajetória de um candidato fictício; retornar sem perder a decisão em edição | Uma visualização contínua de todos os candidatos pode sobrecarregar; o protótipo não prova eficiência de um laboratório permanente |
| [W3C: padrão de grid](https://www.w3.org/WAI/ARIA/apg/patterns/grid/) e [teclado](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/) | Define navegação consistente para interfaces compostas | Preferir inicialmente lista, tabela e botões nativos; foco previsível e alternativa textual | Declarar `role=grid` impõe um contrato de teclado que uma tabela de links não implementa automaticamente |

Não se propõe copiar um editor de automação. O GPS configura normas de um certame com atos imutáveis, não mensagens que percorrem nós reexecutáveis livremente.

## A — Mapa assistido de relações

**Modelo:** o operador seleciona a etapa e vê seus consumidores, ou seleciona um marco e vê entradas, produção da ordem e destino do corte. A conexão é a unidade visível; a edição é contextual e limitada aos vínculos que o domínio suporta.

A representação separa etapas compartilhadas de marcos por Perfil. Em vez de cada etapa virar um nó universal de workflow, linhas de relação leem “objetiva + títulos → POS-TIT ⇢ documental”. A primeira seta usa resultados; a segunda indica participação condicionada à faixa emitida. Textos equivalentes continuam disponíveis.

**Vantagens:** revela reutilização e alcance; ajuda a perceber circularidade; aproxima dados, regra e efeito; permite examinar o conjunto antes de simular.

**Limitações:** etapas são ordenadas, mas as relações podem cruzar; todos os perfis simultâneos produziriam densidade. A maquete recorta um Perfil e mantém a indicação de usos em outros; um edital com dezenas de marcos precisará busca, agrupamento e modo textual. Não promete layout universal legível.

**Melhor aplicação:** manutenção de editais com várias etapas e marcos; diagnóstico de mudança anterior. **Risco:** custo de manter a projeção correta e tentação de evoluir para editor de grafo genérico.

[Protótipo A com consequências de D](prototipos/mapa.html). Não há arrasto de conexões; todas as ações possuem botões/listas e sequência de Tab. A visão móvel empilha relações.

## B — Configuração orientada por decisões

**Modelo:** começa com perguntas do edital, como “o que compara?”, “quem será analisado na próxima etapa?”, “o que o empate determina?”. A resposta escolhe um bloco de configuração existente; o resumo traduz a decisão para marco/corte/etapa.

**Vantagens:** reduz exposição inicial a termos desconhecidos; perguntas podem impedir uma seleção sem significado; permite que o operador explique a norma antes de ver atributos técnicos.

**Limitações:** um wizard obrigatório para toda alteração aumenta passos e oculta o conjunto. Todas as decisões continuam precisando existir. O operador experiente deve entrar diretamente na decisão desejada, com o conjunto à vista. Não escolher respostas normativas por conveniência.

**Melhor aplicação:** primeiro edital e casos simples. **Risco:** manter dois editores independentes ou excluir combinações do acervo. Deve haver uma representação única de conteúdo, com dois caminhos de interação se ambos forem necessários.

O [caderno](prototipos/caderno.html) demonstra perguntas com acesso direto, sem obrigar percurso sequencial. Não é uma terceira implementação completa.

## C — Trajetória dos candidatos

**Modelo:** seguir um candidato hipotético, lendo entradas, consequência da avaliação, posição, corte e situação posterior. Agrupar estados por causa, não só por cor.

**Vantagens:** diferencia “eliminado”, “sem nota”, “fora da faixa” e “aguardando anterior”; dá concretude à porta decisória e ao peso. O operador pode explicar a outro o que aconteceria com uma pessoa.

**Limitações:** uma trajetória não prova a regra geral; omitir uma lista ou um empate pode transmitir segurança indevida. O simulador atual não executa todo o fluxo com passagem real entre marcos. A proposta teria que declarar fronteiras entre calculado, hipótese e indeterminado, como a jornada atual já faz.

**Melhor aplicação:** aprendizagem, conferência de casos-limite e diagnóstico de resultados. **Risco:** alto se virar editor principal ou simulação integral; moderado como detalhe da prévia existente.

A trajetória aparece no laboratório dos dois protótipos, com dupla e resultados preparados. Não é cálculo de um processo completo nem uma terceira maquete.

## D — Configuração com interpretação e consequências simultâneas

**Modelo:** preservar edição reconhecível, mas projetar “usa / produz / alimenta / afeta / falta” no mesmo contexto. Reutiliza a resposta do servidor ao finalizar uma decisão. Exemplo é aberto por solicitação, não recalculado a cada tecla.

**Vantagens:** caminho técnico mais curto; adaptação pequena para operadores atuais; melhora a recuperabilidade e a previsibilidade sem ensinar um editor gráfico novo.

**Limitações:** um painel com prosa para todo campo vira outra parede de avisos. Precisa de estrutura curta, nomes concretos, origem e ações. Com a tela atual já lado a lado com a prévia, um terceiro painel seria insustentável: interpretação ocupa o inspetor; laboratório substitui temporariamente esse contexto.

**Melhor aplicação:** melhoria imediata e edição pontual de regras. **Risco:** duplicação das regras se a explicação for gerada por JavaScript independente.

Foi incorporado ao [Mapa](prototipos/mapa.html), não apresentado como solução isolada universal.

## E — Caderno de compromissos e conferências (ideia independente)

**Origem no código:** um campo como peso é compartilhado, enquanto o efeito está em vários marcos e os atos são imutáveis. O operador precisa tomar responsabilidade por uma decisão que alcança vários objetos. O princípio constitucional de tornar explícito resultado, origem e alcance aponta para uma **unidade de confirmação por compromisso do edital**.

**Modelo:** o operador constrói enunciados limitados, como “usar objetiva e títulos para selecionar 6 + 2 para documental”. Cada compromisso mostra **o que a norma declara**, **quais objetos a realizam** e **como conferir uma consequência**. Alterar uma etapa abre uma reconciliação antes/depois dos compromissos afetados. A linguagem é estruturada: não se digita uma regra livre.

A conferência é central, ao contrário do mapa centrado em topologia. O acesso pode começar por uma intenção (“quem segue?”), por uma cláusula ou por uma mudança. Confirmar exige saber o alcance; não equivale a publicar nem cria um novo ato jurídico. Não há importação automática de cláusulas ou LLM.

**Vantagens:** aproxima a redação do edital da configuração, expõe derivações e aplicação em vários perfis; melhora revisão e prestação de contas; é naturalmente textual e acessível.

**Limitações:** frases compostas podem ocultar detalhes; não se deve substituir o documento normativo gerado por paráfrases. Depende de bom vocabulário de templates para soma, portas, acervo e exceções. Não resolve sozinho a exploração espacial dos consumidores.

**Melhor aplicação:** elaboração, revisão por outra pessoa e mudanças com vários consumidores. **Risco:** médio/alto de uma tradução que pareça juridicamente equivalente sem explicitar condições; mitigar com detalhes estruturados, origem e casos adversos.

[Protótipo E](prototipos/caderno.html): perguntas, frases selecionáveis, comparação antes/depois e conferência de compromissos. Sua diferença de A é a ordem do raciocínio e a unidade de revisão, não a decoração dos controles.

## Representação apropriada para cada problema

| Problema | Representação indicada | Uso limitado ou inadequado |
|---|---|---|
| Reutilização de etapas e destino do corte | Relações tipadas, matriz de usos, filtro por Perfil | Linha do tempo única esconde múltiplas entradas |
| Efeito local de nota/decisão | Tabela de decisão curta, linguagem concreta | Grafo genérico aumenta complexidade sem adicionar informação |
| Fonte posterior ao compromisso | Comparação de instantes com linha temporal | Ordem visual das etapas não prova precedência da ocorrência |
| Mudança normativa | Antes/depois com alcance e origem | Seta animada não informa quais declarações mudam |
| Ordenação, empate e corte de candidatos fictícios | Tabela de classificação e trajetória causal | Árvore de decisão pode explodir em combinações de critérios |
| Escala entre muitos perfis | Tabela resumida + abertura por Perfil; matriz sob demanda | Todos os grafos simultâneos ou sanfona de dezenas de cartões |
| Operação pronta | Lista de condições por operação, recorte, versão e instante | Um único selo verde por processo |

A recomendação híbrida usa A para reconhecer relações, D para editar com consequências e uma conferência curta de E. B e C ficam como caminhos de aprendizagem. Sorteio tem uma vista temporal própria; não se incorpora uma engine de workflows.
