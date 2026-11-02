# Comparação, tarefas e recomendação

> **Substituída na rodada 2.** A recomendação abaixo (A+D com conferência de E) deu lugar ao trilho editável com o texto do documento ao lado. Ver [sintese.md](sintese.md). As tarefas e o gabarito continuam valendo para o teste com operadores.

## Método e confiança

Avaliação heurística e walkthrough cognitivo pelo pesquisador, com evidências de navegação e código. Nenhum operador participou. As previsões abaixo indicam potencial de compreensão, não resultados de teste. As notas de confiança referem-se ao suporte das conclusões, não a uma escala quantitativa de desempenho.

- **Confiança alta:** significado da marca, propriedade dos pesos e marcos, vínculos de corte e comparação temporal; fontes e testes convergem.
- **Confiança moderada:** relações permanecem difíceis de reconhecer entre Etapas e Classificação; retirada de marca e jornada complexa dão evidência observável, mas a causa de confusão dos operadores não foi investigada diretamente.
- **Confiança moderada/baixa:** A+D será mais eficiente que E ou a interface atual. Os dois protótipos tornam relações mais visíveis, mas só tarefas com pessoas podem estabelecer aprendizagem, esforço e erros.

## Matriz comparativa

Mantidos os pesos orientativos. Em lugar de atribuir pontos e somá-los, a matriz usa **forte**, **parcial** e **fraco** como juízo comparativo de projeto. “Forte” significa que a representação expõe diretamente a informação necessária na tarefa; não significa validação empírica. Para viabilidade/manutenção, “forte” significa menor custo relativo e maior reaproveitamento.

| Critério e prioridade | Atual | A · Mapa | B · Decisões | C · Trajetória | D · Consequências | E · Caderno | Híbrida A+D e conferência E |
|---|---|---|---|---|---|---|---|
| Clareza de regras/consequências · 25% | Parcial: definição e prévia já ajudam; mudança anterior fica separada | Forte nas relações; parcial na lógica de critério | Forte na primeira decisão; parcial no conjunto | Forte para um caso; fraca generalização | Forte em causa/efeito local | Forte no compromisso e na revisão | Forte: vínculo, efeito e revisão se complementam |
| Prevenção/recuperação · 20% | Parcial: forma/peso e backend fortes, referências se distribuem | Forte se mantém referência inválida e ação de correção | Forte para escolhas cobertas; risco de esconder exceções | Parcial: caso pode não revelar falha estrutural | Forte com achados existentes e correção contextual | Forte na reconciliação antes/depois | Forte; exige uma fonte de validação só |
| Dependências visíveis · 15% | Parcial: jornada depende de abrir prévia | Forte com um Perfil em foco | Parcial: perguntas podem ocultar usos remotos | Parcial: trajetória selecionada não cobre consumidores | Parcial/forte se traz lista de afetados | Forte em alcance; parcial na topologia | Forte por projeção e índice de consumidores |
| Facilidade de configurar · 15% | Parcial: familiar, mas exige conceitos | Parcial: requer aprender relação etapa/marco | Forte para primeiro uso; fraca para manutenção se linear obrigatório | Fraca como editor principal | Forte pela continuidade com controles existentes | Parcial: boa para revisão; risco de frases longas | Parcial/forte se evitar múltiplos editores obrigatórios |
| Escala · 10% | Parcial: conjunto por Perfil já comprime | Parcial: cruzamentos e densidade pedem filtro/matriz | Fraca/parcial: muitas decisões sequenciais | Fraca para toda população; boa em detalhe | Parcial: vários efeitos podem virar prosa extensa | Parcial/forte por compromissos pesquisáveis | Parcial: depende de filtro e redução de informação |
| Viabilidade técnica · 10% | Forte: implementada | Parcial: projeção nova, sem motor novo | Parcial: mapear combinações/acervo | Fraca para simulação integral; forte como detalhe existente | Forte: maior reaproveitamento | Parcial: interpretação cobre exceções | Parcial: entrega incremental e contrato único são indispensáveis |
| Acessibilidade/manutenção · 5% | Forte em controles nativos; relações exigem leitura dispersa | Parcial: precisa equivalente textual e ordem de foco | Forte com perguntas e navegação direta | Parcial: tabela causal acessível; animação não é requisito | Forte com texto curto, vínculos e foco | Forte no texto; risco de complexidade linguística | Parcial/forte se tabelas/listas forem fonte da representação |

A recomendação prioriza os três primeiros critérios (60% orientativos), onde a lacuna observada é relacional. Isso favorece A+D sobre D isolada. E merece comparação com usuários porque pode ser melhor para primeira configuração e revisão, mesmo sem mapa. O custo e a necessidade de linguagem abrangente impedem recomendar ambos como editores completos no primeiro ciclo.

## Avaliação do esforço e da carga cognitiva

| Modelo | Informação simultânea | Decisões e navegações previstas | Memória / relações / consequências | Aprendizagem e escala | Custo relativo |
|---|---|---|---|---|---|
| Atual | Muitos atributos dentro do cartão; conjunto compacto por Perfil | Decisões normativas necessárias; deslocamento Etapas ↔ Classificação ↔ Revisão | Peso e marca precisam ser relacionados aos usos; prévia já explica resultado | Familiar a quem já opera; complexidade cresce com marcos | Existente |
| A | Etapas + relações de um Perfil + um inspetor | Seleção direta do objeto e consumidores; não elimina escolhas normativas | Menos lembrança de usos; risco de cruzamento visual em grande escala | Precisa ensinar dois tipos de seta, com legenda textual | Médio |
| B | Uma decisão e seu contexto por vez | Mais passos no primeiro percurso; manutenção deve permitir salto direto | Menor memória local, mas contexto global pode desaparecer | Fácil de começar; longo em editais extensos | Médio |
| C | Um caso e causas por etapa/critério | Abrir caso e acompanhar; não substitui compor a regra | Menor abstração; maior risco de generalizar um exemplo | Boa aprendizagem; ruim para dezenas de cenários simultâneos | Baixo como detalhe, alto como simulador integral |
| D | Campos pertinentes + interpretação curta | Percurso atual com menos idas a outras telas se houver atalho | Forte na consequência imediata; depende da lista de consumidores | Menor ruptura; prosa acumulada prejudica escala | Baixo/médio |
| E | Decisão declarada, origem e conferência | Escolher compromisso, responder, conferir alcance; acesso direto | Relação por frase e comparação antes/depois | Boa revisão verbal; exige vocabulário e detalhe normativo | Médio/alto |
| Híbrida | Mapa com foco + um contexto; laboratório em substituição | Acesso direto; conferência de alcance nas mudanças relevantes | Combina reconhecimento com prova concreta sob demanda | Escala pede filtro, busca e modo textual | Médio, repartido por ciclo |

Não se estimaram segundos, taxas de erro ou economia percentual. O número de escolhas normativas não deve cair eliminando decisões que o edital precisa declarar.

## Tarefas de comparação e gabarito

Aplicar os mesmos dados e tarefas às interfaces. Alternar a ordem das propostas entre participantes. Observar primeiro sem ensinar os conceitos; depois permitir ajuda. A maquete só permite as alternativas preparadas, portanto não pode medir velocidade de configuração completa do GPS.

| Tarefa | Pergunta ao participante | Resposta que demonstra compreensão |
|---|---|---|
| 1 · O que classifica? | “Que dados FINAL usa? Documental aumenta a nota?” | Objetiva, títulos e didática produzem parcelas com seus pesos; documental é porta e não soma nota |
| 2 · Para onde seguem? | “Quem vai para documental e o que falta para isso valer?” | Corte de POS-TIT, alvo 6 + 2 e empatados conforme política; precisa ser emitido; habilitação e progressão continuam valendo |
| 3 · Marca | “Retire a marca de títulos. Quem será eliminado?” | Ninguém por esse gesto; três marcos ficam com referência incompatível. Restaurar marca ou revisar enumeração explicitamente |
| 4 · Sorteio | “Se esperar até as 20h05, poderá sortear uma relação congelada hoje com fonte só de data?” | Não. 00h daquela data não é posterior ao congelamento. Retificar extração e suceder relação; com fonte horária genuína, comparar o horário real |
| 5 · Impacto anterior | “Mude o peso de títulos para 2. O que você sabe sem notas reais?” | POS-TIT, FINAL e RESERVA usam o peso; fórmulas mudam. Não sabe quantas pessoas mudam de posição; exemplo fictício é apenas conferência |
| 6 · Revisão e prontidão | “Falta peso. Está inválida ou incompleta? E com todos os campos preenchidos, pode executar?” | Incompleta nesse dado; circularidade é inválida. Estrutura coerente não prova publicação, resultados, faixa e permissões |

### Walkthrough por alternativa

| Tarefa | Atual | A | B | C | D | E | Híbrida |
|---|---|---|---|---|---|---|---|
| 1 | Ver entradas, forma da etapa e prévia | Entradas e inspetor | Pergunta de combinação | Exemplo mostra parcelas e porta | Interpretação local | Compromisso FINAL | Mapa + interpretação; exemplo opcional |
| 2 | Abrir regra de corte e ler destino | Relação tipada direta | Pergunta “quem segue?” | Trajetória parcial, se explicitada | Saída e condições | Frase de POS-TIT | Relação + condições de emissão |
| 3 | Ir à etapa; voltar e revisar | Usos e pendência no mesmo foco | Exige uma pergunta específica | Caso sozinho pode ocultar a estrutura | Lista de afetados e consequência | Reconciliação dos três compromissos | Mudança com alcance explícito |
| 4 | Aviso e diagnóstico já descrevem a regra | Mapa sozinho insuficiente | Perguntas precisam levar à fonte/tempo | Caso ajuda se mostra limite inferior | Comparação dos instantes | Compromisso temporal complementar | Vista temporal separada |
| 5 | Relembrar todos os marcos | Consumidores selecionáveis | Percurso pode ficar longo | Só efeito no caso | Antes/depois | Conferir todos os compromissos | Projeção + comparação sob demanda |
| 6 | Revisão e telas operacionais distintas | Mapa não prova prontidão | Respostas não provam atos | Simulação não prova execução | Estados em dois eixos | Conferência separa configuração/atos | Estado por operação e recorte |

“Walkthrough” aqui significa percorrer as tarefas e avaliar se a informação e a ação são encontráveis. Não representa fala ou comportamento observado de usuários.

## Recomendação

**Levar A+D a teste como experiência principal de manutenção**, com uma conferência curta de alcance inspirada em E. Levar E como contraproposta real para primeiro uso e revisão. A decisão de adoção só deve ocorrer depois de comparar compreensão e manutenção com operadores.

A composição recomendada resolve a visibilidade dos consumidores e a separação entre produzir ordem e alimentar etapa; permite que a marca tenha efeito legível; usa exemplos para conferir, não para descobrir toda a estrutura; e representa tempo com a granularidade real da fonte.

Preservar: nomes oficiais, dados e identificadores, controles nativos, composição por forma, método comum/override, conjunto de Perfis, rascunho local, achados de domínio, prévia com população estável, trajetória causal, casos-limite, recortes e limites de simulação, atos imutáveis e confirmações existentes.

Permanecem: complexidade normativa real, necessidade de conhecer o edital, integração entre responsáveis distintos, fontes externas imprevisíveis, recortes sobrepostos e acervo. Não se promete prever a classificação real sem entradas ou simular toda a cadeia. Um mapa não resolve esses limites.

Custo principal: projeção correta do conteúdo digitado e suas referências, explicação fiel de regras antigas, integração de foco/rascunho e revisão entre etapas. Risco principal: interpretação que pareça completa e omita condições. Reaproveitar funções e achados reduz divergência; testes de acervo e linguagem são necessários.

Ficam fora do primeiro ciclo: editor genérico de grafo, novo motor/DSL, LLM, importação de norma por texto livre, execução contínua da prévia, simulação multietapas integral, reescrita da classificação ou alteração das regras de sucessão.

## Autocrítica: as quatro perguntas finais

1. **Ver como as etapas se relacionam:** A oferece uma leitura melhor fundamentada das dependências; sua escala foi demonstrada apenas no cenário de quatro etapas, não em dezenas.
2. **Entender a marca sem tentativa e erro:** ambos explicitam permissão de uso e consumidores; ainda falta verificar se “Classificatória” permanece semanticamente ambígua para operadores.
3. **Reconhecer efeito em etapas posteriores:** cortes/destinos e alcance aparecem; o protótipo não calcula efeitos sobre inscrições reais nem todas as cadeias de atos.
4. **Revisar e explicar a outra pessoa:** E favorece explicação verbal; a síntese pode esconder detalhes e deve manter acesso à estrutura original. A simulação complementa essas leituras, mas a superioridade prática segue não comprovada.

A proposta é suficientemente concreta para revisão e pesquisa. Não é evidência para dispensar a etapa de teste com pessoas.
