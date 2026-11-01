# Validação antecipada, explicação e análise de impacto

## Estados que a interface deve distinguir

Dois eixos independentes evitam um semáforo enganoso.

| Eixo da configuração | Significado e apresentação |
|---|---|
| Não respondida | Campo ainda intocado; pergunta neutra, sem alerta prematuro |
| Incompleta | Resposta iniciada sem todas as partes; dizer “falta declarar…” após sair da decisão ou pedir revisão |
| Inválida | Valores declarados contradizem uma regra, por exemplo destino circular; explicar relação e correção |
| Coerente no escopo conferido | Validações daquele objeto e suas dependências passaram; não significa publicação ou execução autorizadas |

| Eixo da operação | Significado e apresentação |
|---|---|
| Ainda não avaliável | Faltam dados ou atos necessários para verificar; não mostrar “pronto” |
| Aguarda ato | Resultado, publicação, faixa vigente ou autoridade ainda necessários |
| Aguarda tempo/fonte | Depende do instante de referência ou da ocorrência externa; mostrar o que se compara |
| Impedida | Há contradição ou condição recusada pelo domínio; indicar ato e causa |
| Pronta neste instante para esta operação | Identificar operação, perfil, marco, recorte, versão e momento conferidos; o backend revalida dentro da transação |

Não exigir uma simulação como condição nova para publicar. “Exemplo consultado” é informação da experiência, não norma. Nenhum `OK` de tela vence a validação transacional, a autorização ou os privilégios do banco.

## Inventário de validações relevantes

Escopo: famílias de validações da composição, classificação e rito do sorteio, não todas as regras do monólito. Uma família agrupa suas variações de identidade/campo. **“Antecipar” não significa mudar a fase em que o backend hoje recusa.** Campos ainda não graváveis podem existir no preenchimento local; isso não autoriza salvar uma estrutura que `replace_draft` recusa.

Legenda de fases: **R** = gravação do rascunho conforme as guardas existentes; **P** = conferência/submissão/publicação, com particularidades de Retificação; **E** = execução do ato. O diagnóstico pode ser exibido antes delas, sempre conservando a guarda original.

| Categoria / validação | Quando e dados necessários | Antes de salvar? / explicação e ação | Fase que deve continuar protegida |
|---|---|---|---|
| Obrigatoriedade: nome da etapa, identificação do marco | Ao concluir a decisão; campos do objeto | Sim; apontar nome/código em falta; preencher sem resetar a tela | R para invariantes; manter exigências de formulário e P |
| Identidades e ordens únicas de etapas | Coleção proposta completa | Sim; “duas etapas têm a mesma ordem”; reordenar explicitamente | R e constraints |
| Códigos de marco únicos por Perfil | Marcos do Perfil | Sim; nomear os dois; escolher código distinto | R e banco |
| Referência de evento existe no mesmo Edital | Etapas + cronograma propostos | Sim; mostrar evento removido com nome e referência preservada; religar ou declarar sem vínculo | R/P; ausência legítima de vínculo é aviso, não erro novo |
| Faixa numérica de etapa | Peso, mínima, máxima, quantidade de avaliações | Sim após saída; peso/max > 0, mínima ≥ 0, mínima ≤ máxima, avaliações ≥ 1 | R/P e constraints |
| Aplicabilidade da forma | Forma, notas e rótulos | Sim; mostrar só campos aplicáveis; avisar quais declarações serão retiradas ao mudar forma | R conforme normalização; P para forma publicada |
| Decisória precisa de rótulos | Forma + textos do edital | Sim; “o candidato verá qual resultado?”; preencher favorável/desfavorável | P; R segue guardas vigentes |
| Pontuada eliminatória sem mínima | Etapa proposta | Sim; “não há regra para decidir eliminação”; declarar mínima ou revisar caráter conforme edital | E (`impedimento_da_regra`); antecipar sem inventar nova proibição de publicação |
| Decisória não eliminatória | Forma + caráter | Sim; “efeito desfavorável não declarado para consolidação”; rever norma, não inventar consequência | E; manter regime atual de avisos/conferência |
| Mais de uma avaliação por inscrição | Quantidade prevista | Sim; “a V1 não combina N avaliações”; revisar edital ou reconhecer limite operacional | E; não apresentar média de banca como suportada |
| Marco por pontuação precisa de etapa | Forma da ordem + entradas | Sim; selecionar etapa classificatória existente; sorteio permite nenhuma | R/P; preenchimento local pode permanecer incompleto |
| Etapa enumerada existente e classificatória | Conteúdo inteiro, inclusive referências antes válidas | Sim; “POS-TIT ainda usa títulos, cuja marca foi retirada”; restaurar ou ajustar usos explicitamente | P; preservar referência inválida na edição, sem apagá-la automaticamente |
| Etapa pontuada enumerada precisa de peso | Entradas do marco + atributos da etapa | Sim; aviso já existe; oferecer edição da etapa com retorno ao marco | P e cálculo defensivo |
| Operação, normalização e arredondamento suficientes | Entradas, pesos, operação, escala 0–4, modo | Sim; explicar soma versus média; respeitar declaração antiga, mesmo com etapa única | P e `RegraIncompleta` no cálculo |
| Divisor inexistente/zero | Operação e parcelas pontuadas | Sim; média só com portas não possui soma de pesos útil; escolher regra que a norma suporte | P/cálculo; porta sem peso não é “peso ausente” |
| Critério tem ordem, alvo e política de ausência | Critérios do marco e domínio dos alvos | Sim; filtrar alvos pelo tipo, preservar seleção inválida e explicar; completar política | R/P |
| Etapa/fato do critério existe | Conteúdo proposto + fatos do Perfil | Sim; referência retirada fica visível; substituir explicitamente | P; tipo/compatibilidade seguem validações existentes |
| Corte possui alvo, suplentes e declarações obrigatórias | Regra de corte; distinção ausência/0/NONE | Sim; perguntas neutras até decisão concluída; não presumir empate/continuação | R/P conforme família; corte parcial mantém guardas atuais |
| Alvo derivado possui linha do quadro | Corte + quadro do Perfil/recorte | Sim; “o alvo tem esta origem”; criar/corrigir quadro, não converter ausência em zero | P/E |
| Corte governa etapa existente ou nenhuma | Regra + etapas | Sim; perguntar “onde serão analisadas estas pessoas?”; escolher etapa ou `NONE` | P |
| Circularidade direta | Entradas e destino do mesmo marco por nota | Sim; “o corte decide quem fornece o próprio resultado”; escolher outro destino ou revisar as entradas segundo o edital | P; exceção do sorteio preservada |
| Dois marcos governam mesma etapa no Perfil | Todos os cortes daquele Perfil | Sim; nomear ambos; rever uma declaração; não unir faixas ou escolher precedência | P |
| Inscrições ainda em curso | Cronograma vigente + instante comum | Sim, antes de congelar; mostrar encerramento e relógio de referência | E; bloquear congelamento e sucessão |
| Relação vazia / sucessão sem motivo | Inscrições submetidas, habilitação prévia, relação vigente e texto | Sim por leitura; “não há universo neste recorte” ou “declare por que sucede” | E transacional; motivo obrigatório |
| Método de sorteio suficiente e fonte conhecida | Override/comum resolvidos, adaptador e vocabulário | Sim; exibir origem do método e campos faltantes; corrigir na norma apropriada | R/P/E; produção recusa fonte de demonstração |
| Fonte só com data inviável desde a publicação | Granularidade, ocorrência e fim das inscrições | Sim; 00h institucional da extração ≤ fim das inscrições; escolher dia posterior disponível | P bloqueia original; Retificação adverte, não fecha a saída |
| Congelar agora torna sorteio inviável | `max(agora,fim)` + limite previsto | Sim; aviso concreto já existe; retificar antes do compromisso | E mantém congelamento possível com aviso, conforme decisão vigente |
| Relação presa a método/versão anterior | Relação + método comprometido + vigente | Sim; “retificar não atualizou esta relação”; suceder após retificar | E e confirmação do compromisso |
| Ocorrência disponível/admissível e com limite posterior | Relação vigente + observação registrada + cadeia de substituição | Parcial: precedência prevista antes; efetiva somente após resposta da fonte; mostrar valores comparados | E; `<=` recusa; referência, fonte, limite e estado conferidos |
| Fonte ainda não publicou / falha de rede | Horário declarado, relógio e resposta externa | Estado externo; “aguarde horário” ou “tente observar de novo”; rede falhada não autoriza avançar ocorrência | E; falha de acesso não grava indisponibilidade |
| Empate residual atravessa faixa estrita | Dados efetivos + ordenação + política do corte | Não é determinável só pela configuração; exemplo pode demonstrar risco; julgar desempate ou retificar conforme norma | E; não selecionar um empatado arbitrariamente |
| Dados/atos obsoletos ou resultados incompatíveis | Versões, resultados e atos citados, corte vigente | Estrutura: antes; efeitos sobre pessoas: só com consultas autorizadas; indicar sucessão necessária | E; preservar atos antigos |
| Estado do Edital/Processo e permissão/escopo | Ator, estado vigente, operação, versão/revisão | Leitura antecipada orienta, mas pode envelhecer; levar à Retificação/ato apropriado ou negar acesso | R/P/E dentro da transação; negar por padrão |
| Mudança concorrente | Revisão esperada + revisão atual e proposta | Só ao cotejar com servidor; “a base mudou”; reler e comparar, sem perder digitado | R/P/E; não sobrescrever silenciosamente |

## Explicação determinística

Recomenda-se uma **projeção de leitura**, não outro modelo normativo. Ela é necessária porque a interface hoje precisa cruzar etapas, marcos, cortes e perfis para explicar uma mudança. Pode ser um conjunto de DTOs transitórios no Python, com identificadores, nomes, origem, consumidores e achados já produzidos pelo domínio. Não requer tabela, DSL, motor de regras ou formato JSON persistente novo.

Fluxo proposto:

```text
estado digitado + base identificada
    → parser existente, sem persistir
    → validações/funções de domínio já existentes
    → projeção de vínculos + achados + interpretação
    → fragmento HTML acessível
```

O formato de transporte continua sendo detalhe do plano técnico posterior. Nenhum texto produzido vira uma segunda fonte normativa. A interpretação consulta funções como `combinacao_efetiva`, `declara_sorteio`, `metodo_que_governa`, `faixa.etapa_governada` e `limite_previsto`; não deve reescrever seus predicados em JavaScript. Referência inválida é apresentada como inválida, com nome anterior quando disponível e identidade, não ocultada por uma lista filtrada.

| Caso | Texto possível e cuidado |
|---|---|
| Nota + não eliminatória | “Títulos produz nota e não elimina por pontuação. POS-TIT e FINAL usam essa nota com o peso declarado na etapa.” |
| Mínima + eliminatória | “Nota inferior a 6 elimina; nota exatamente 6 habilita nesta etapa. Isso não substitui o corte para a próxima.” |
| Porta decisória | “Documental decide Deferido/Indeferido. FINAL a enumera como porta; não soma nota nem exige peso.” |
| Marca sem consumidor | “A etapa pode entrar em marcos; nenhum marco deste Perfil a enumera atualmente.” Evitar afirmar que a nota já participa da ordem |
| Marca retirada com consumidor | “FINAL continua apontando a etapa, mas a marca foi retirada. A configuração publicada seria recusada.” |
| Média | “Combina as notas das etapas A, B e D com pesos 2,1,3; divide pela soma dos pesos; arredonda ao fim.” Se não há divisor, explicar falta |
| Soma antiga de etapa única | “Esta declaração multiplica a nota pelo peso 2.” Não usar frase genérica “a nota é a da etapa” |
| Critérios sucessivos | “Se as notas combinadas empatarem, comparar maior nota em didática. Persistindo empate, aplicar o próximo critério declarado.” |
| Valor ausente | “Último neste critério” é diferente de “critério não se aplica ao grupo se qualquer integrante não tiver o valor”. O docstring histórico menciona par; a função atual é por grupo |
| Corte | “Seleciona alvo 6 e 2 suplentes na mesma emissão. Se um empate cruzar a fronteira, todos progridem nesta declaração.” No estrito: emissão pode ser impedida |
| Destino | “Essa faixa, depois de emitida, restringe a entrada em documental; resultados e eliminações anteriores continuam valendo.” |
| Reserva | “Autodeclarados também concorrem pela ampla. A ocupação evita contar na reserva quem ocupa pela ampla.” Não desenhar conjuntos exclusivos |
| Sorteio | “A ordem usa a relação comprometida e a ocorrência admissível. Não depende da soma das notas das etapas enumeradas.” |

Testar textos por configuração e exemplos adversos, incluindo acervo, ausência, zero legítimo, porta, normalização, fonte apenas com data e Retificação. Ser determinístico não basta se a frase omitir condição importante.

## Impacto: o que se pode saber

| Alteração | Determinável sem dados pessoais | Depende de dados/atos e não pode ser prometido |
|---|---|---|
| Retirar marca | Marcos que enumeram a etapa, perfis, referências agora inválidas | Quantas pessoas perderiam posição; jamais excluir referências automaticamente |
| Mudar peso | Marcos que usam a etapa, fórmula antes/depois, necessidade de reavaliar exemplo | Nova ordem real, novos ocupantes e extensão do corte |
| Trocar forma da etapa | Campos que deixam de se aplicar, portas/parcelas afetadas, exigências de consolidação | Validade dos resultados já produzidos, sem usar comparadores existentes |
| Mudar ordem | Etapas anteriores antes/depois, última enumerada de marcos, projeção de jornada | Efeito final da progressão em inscrições específicas |
| Mudar destino/alvo/empate | Etapas governadas e dependências de participação, dimensão do alvo por recorte quando quadro disponível | Quantos efetivamente avançam, empates na fronteira, desistências |
| Mudar método comum | Marcos que herdam versus método próprio; relações comprometidas que não mudam por herança | Se a fonte estará disponível ou qual ordem produzirá |

Análise estrutural pode percorrer referências explícitas e a ordem das etapas, com índices montados uma vez por conteúdo. Não é preciso um banco de grafos. Consultas sobre atos oficiais devem usar comparadores já existentes de reprodução/obsolescência, após autorização, em vez de inferir que “toda mudança invalida tudo”. Rascunho não tem os mesmos efeitos de Retificação sobre um certame em execução.

## Simulador: evolução proporcional

A prévia atual já possui população estável, comparação do estado anterior, casos-limite e trajetória de desempate. Pontuação, universo classificável, corte e ocupação são funções reaproveitadas. A prévia de sorteio usa a mesma função de ordem e semente fictícia, sem fonte real. Há limites deliberados: até **4 etapas com nota**, **6 modalidades reservadas** e **600 candidatos fictícios**; o resumo de sorteio executa **1.000 rodadas** sob demanda.

A jornada põe os outros marcos em contexto/indeterminação. Ela não calcula uma cadeia inteira com passagem real entre etapas: dar notas fictícias na final não prova que aquelas pessoas atravessaram os cortes anteriores. A ocupação é uma rodada hipotética, sem histórico de chamadas, aceitações e desistências. O estudo preserva esses limites.

Primeiro ciclo: abrir a prévia existente a partir da relação inspecionada, mantendo origem e rótulo fictício; comparar apenas quando o operador pedir. Interpretação estrutural pode ser atualizada ao terminar uma decisão. Não disparar resumo de 1.000 sorteios a cada tecla.

Posteriormente: se usuários precisarem, oferecer conjuntos de exemplos escolhidos e comparação de configuração com população fixa. Um simulador multietapas integral exigiria tratar progressão, recursos, obsolescência, cortes e atos hipotéticos; custo alto e benefício ainda não demonstrado. Fica fora da recomendação inicial.

### Cuidado com anulação e cadeia de relações

Além das condições da tabela, anular um sorteio exige relação nova do mesmo recorte, sucessora **direta** da relação do ato anulado, ocorrência nova e motivo. Uma filha direta que já foi sucedida não é executável. O ensaio de duas sucessões revelou opção oferecida que o backend recusa; ver [evidencias.md](evidencias.md). Um futuro diagnóstico de prontidão precisa conferir essas condições juntas. Não basta “relação nova existe”. Nenhuma mudança dessa regra é recomendada como parte do redesenho sem decisão de domínio.
