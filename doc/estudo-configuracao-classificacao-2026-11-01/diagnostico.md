# Diagnóstico técnico e cognitivo

> **Revisto na rodada 2.** O ciclo "salvar, receber erro" foi raro na construção feita do zero. O problema dominante é a configuração que contraria o edital ser aceita sem aviso. Ver [diario-de-construcao.md](diario-de-construcao.md).

## Conclusão investigativa

O problema não é simplesmente excesso de combos. A unidade de edição atual alterna entre a **Etapa, compartilhada pelo Edital**, e o **marco, próprio do Perfil**. O operador precisa recompor mentalmente os usos da etapa, a produção da ordem, o corte e a participação posterior. A marca classificatória tem um nome curto para um efeito relacional que só fica claro na outra tela.

A hipótese de configuração de elementos isolados é sustentada pelos casos de retirada da marca e alteração do peso descritos abaixo. Contudo, a hipótese de que o sistema só explica depois de salvar é refutada em parte: há apresentação condicional, avisos de peso, pendências, visão dos perfis e uma prévia contextual com cálculo oficial. A experiência atual é mais avançada que a descrição inicial do problema.

A evidência permite recomendar um redesenho para avaliação, não afirmar que ele terá melhor desempenho com operadores. Não foram entrevistados os participantes do episódio relatado; o vínculo entre seu raciocínio e os problemas identificados continua sendo uma hipótese de pesquisa.

## O modelo real

A implementação investigada oferece duas formas de **conclusão da avaliação** (pontuada e decisória) e duas formas de **produção de ordem do marco** (pontuação e sorteio). Não são quatro métodos intercambiáveis do mesmo campo.

1. Uma inscrição pertence a um Perfil de Vaga; Etapas pertencem ao Edital e são compartilhadas entre seus Perfis.
2. A avaliação produz uma nota total ou uma decisão com sentido favorável/desfavorável. Os rótulos são os do edital. Não foi encontrado, nesse caminho de avaliação/classificação, um cadastro de rubricas ou componentes de nota que se agreguem automaticamente à nota da etapa. Critérios de desempate não são rubricas de correção.
3. A consolidação produz `ResultadoEtapa` com consequência, motivo e eventual pontuação. A V1 de consolidação não combina múltiplos avaliadores: mais de uma avaliação prevista gera impedimento por ausência de regra de combinação.
4. Um `MarcoClassificatorio` pertence ao Perfil e enumera Etapas. Por pontuação, combina suas notas, aplica critérios sucessivos e preserva empates residuais. Etapa decisória enumerada é porta, não parcela.
5. A regra de corte seleciona uma faixa da ordem, segundo alvo, suplentes, empate e continuação. Pode declarar explicitamente a etapa que alimenta, ou `NONE`.
6. Participar de uma etapa depende também das eliminações anteriores e, quando ativada a exigência, da habilitação na imediatamente anterior. O corte não substitui essas condições.
7. Ordenar, emitir corte, apurar ocupação, divulgar resultado e convocar são atos distintos. Publicar o edital não executa a classificação.
8. O sorteio tem relação publicada/congelada, método comprometido por versão e ocorrência observada. A ordem não é obtida pela combinação de notas.

Fontes principais: [etapas do Edital](../../backend/processo_seletivo/editais/models/etapas.py), [modelos de Perfil e marco](../../backend/processo_seletivo/editais/models/perfis.py), [regra do resultado](../../backend/processo_seletivo/resultados/domain/regra.py), [cálculo da ordem](../../backend/processo_seletivo/classificacao/application/calculo.py), [corte](../../backend/processo_seletivo/classificacao/domain/faixa.py). O índice de funções e testes está em [evidencias.md](evidencias.md).

## Mapa de conceitos

| Conceito e significado | Configuração atual | Dependências e efeito de alterar | Restrições relevantes | Explicação atual e dedução exigida |
|---|---|---|---|---|
| Etapa de Avaliação: momento do certame | Passo Etapas; nome, ordem e evento | Reordenar muda a anterioridade e a “última etapa” de cada marco; alterar alcança todos os perfis | Identidade/ordem únicas no Edital; evento deve existir | A tela diz que vale para todos os perfis; não lista ali todos os usos por marco |
| Forma pontuada | Opção “Com pontuação” | Produz total; mínima, máxima e caráter podem determinar eliminação | Pontuação e rótulos decisórios são incompatíveis; mínima ≤ máxima | Campos pertinentes aparecem; a regra de consequência local fica distante da composição |
| Forma decisória | “Com decisão, sem nota”, rótulos | Favorável/desfavorável produz habilitação/eliminação quando a regra permite consolidar | Sem notas; rótulos exigidos; não eliminatória tem consolidação impedida | Forma condicional ajuda; “Classificatória” ao lado pode sugerir que sempre há número |
| Caráter eliminatório | Checkbox, dependente da forma | Nota inferior à mínima elimina; igual habilita. Sem caráter, mínima sozinha não elimina | Pontuada eliminatória sem mínima: regra insuficiente; decisória não eliminatória: efeito não declarado | Falta uma representação da diferença entre nota, consequência e participação |
| **Marca classificatória** | Checkbox da etapa | Permite enumeração na composição do marco; mudar não atribui posição, não cria corte nem muda a consequência local | Marco que enumera etapa sem essa marca é impedido na conferência de publicação | O efeito aparece na lista de etapas de outra tela; a etapa não apresenta seus consumidores |
| Peso | Etapa, opcional até enumeração | Reutilizado em todos os marcos que consomem sua nota; altera combinações | Positivo; ausente não é 1; porta decisória não exige peso | Ao selecionar a etapa no marco, há aviso de peso ausente; não há análise conjunta dos usos |
| Avaliações por inscrição | Etapa | Ausência significa 1; declarar N não cria uma média entre avaliadores | Mais de 1 impede consolidação na V1 | O controle é configurável, mas executabilidade precisa ser distinguida da validade de estrutura |
| Marco classificatório | Passo Classificação, dentro de Perfil | Enumera etapas e produz uma ordem por recorte | Código único por Perfil; pela pontuação exige etapa; sorteio pode não enumerar nenhuma | A definição de etapa versus marco já existe e deve ser preservada |
| Combinação e arredondamento | Marco: soma/média, normalização, casas e modo | Lê pesos das etapas; arredonda uma vez ao fim; uma etapa nova deriva média quando não há declaração | Escala 0–4; modo explícito; média só de portas não tem divisor; acervo conserva operação declarada | Interface reduz perguntas em caso simples; a interpretação precisa honrar regra antiga, sem “corrigir” declaração |
| Critério de desempate | Linhas de critério no marco | Consome nota de etapa ou valor de fato declarado; ordem dos critérios é normativa | Alvo e comportamento na ausência explícitos; referências existentes | Tipo e alvo são controles separados com ajuda pedindo coerência; depende de reconhecer compatibilidade |
| Fato declarado | Perfil/inscrição | Inteiro ou data entra no desempate; não vira parcela automaticamente | Ausência não é zero | “Maior idade” não é um operador genérico encontrado: nascimento pode usar menor data; explicar conforme tipo real |
| Empate residual | Derivado da combinação e critérios | Compartilha posição, com saltos: 1,1,3 | Nenhum desempate oculto por nome/ID | A prévia explica causas e grupos; não precisa de outro algoritmo |
| Corte / faixa | Bloco do marco | Faixa inicial = alvo + suplentes; quantidades contam pessoas; empate pode ampliar ou impedir emissão | `STRICT` não escolhe arbitrariamente entre empatados; destino não pode ser entrada do próprio marco por nota | Rótulo “a faixa para no alvo” exige compreender que o ato pode não sair; a prévia já explica |
| Etapa governada | Corte: “Etapa que o corte alimenta” | Participação condicionada à faixa emitida, além da progressão | Uma etapa não pode ser governada por dois marcos no mesmo perfil; destino explícito, inclusive nenhuma | É o vínculo principal, mas aparece como uma opção entre campos do corte |
| Faixa seguinte | Política no corte | Permite continuidade além da faixa inicial segundo o domínio | Não é suplente inicial nem cadastro de reserva | Termos próximos exigem distinguir três conceitos e atos |
| Perfil e listas | Perfis, modalidades e quadro de vagas | Perfil separa competição; reserva se sobrepõe à ampla; alvo do quadro varia por recorte | Ampla precisa ser identificada; não duplica ocupação em reserva | A prévia já explica sobreposição e ocupação hipotética; não desenhar uma bifurcação de pessoas exclusivas |
| Método comum e próprio do sorteio | Edital ou override de marco | Próprio prevalece; mudar comum pode alcançar vários marcos | Método precisa existir e respeitar vocabulário/adaptador; conteúdo normativo | Atual tela mostra método resolvido; mudança exige tornar explícito quem herda e quem diverge |
| Habilitação antes do sorteio | Método: `qualifyingStageId` | Restringe universo à etapa declarada antes do compromisso | Não confundir com enumeração do marco ou etapa governada | Três vínculos com etapa têm semânticas diferentes; uma seta indiferenciada seria enganosa |
| Relação congelada | Presidência: publicar relação | Fixa candidatos, números, versão e hash do método; suceder é novo ato | Inscrições encerradas; universo não vazio; sucessão motivada | Há aviso anterior ao congelamento; falta sobretudo diminuir o raciocínio temporal exigido |
| Ocorrência da fonte | Observar na tela de sorteio | Material externo alimenta semente após normalização | Admissível, disponível, limite conhecido e estritamente posterior à relação; rede falhada não é indisponibilidade definitiva | Fonte e limite são exibidos; texto extenso pode ser complementado por comparação dos instantes |
| Prontidão | Distribuída por revisão, resultados, corte e sorteio | Mistura norma, atos vigentes, autorização, tempo e fonte | Não pode ser deduzida só da presença de campos | Não há um único “pronto” legítimo para todas as operações |
| Publicação / Retificação / sucessão | Atos próprios e responsáveis distintos | Publicação é imutável; nova norma e atos sucessores preservam anteriores | Nunca editar o publicado ou apagar históricos | A nova interface deve indicar estado e canal de correção antes de oferecer ações |

## Semântica precisa da marca

Não há, neste caminho, uma entidade chamada “marca classificatória” com um valor numérico. O correspondente real ao relato é o booleano `EtapaAvaliacao.classificatory`, apresentado como **Classificatória**.

- **Pontuada:** a marca permite que um marco enumere a etapa. A nota só entra se o marco a enumera; o peso usado vem da etapa.
- **Decisória:** se enumerada, atua como porta de habilitação e não soma valor. Peso não é cobrado de uma porta. Um marco formado só por portas pode ter pontuação nula e ordenar por critérios; uma divisão pela soma de pesos sem parcelas não é válida.
- **Sorteio:** a ordem nasce da relação e da semente, não da soma das notas. Enumerar etapas não transforma sorteio em pontuação. A habilitação prévia é vínculo próprio no método; o corte alimenta etapa por outro vínculo.
- **Progressão:** o resultado eliminatório afeta etapas seguintes mesmo que a etapa não seja classificatória. Retirar a marca não reabilita eliminados, não elimina habilitados e não decide o alvo do corte.
- **Critérios:** o seletor atual oferece etapas classificatórias como alvos de pontuação. A conferência geral verifica existência do alvo; não presumir que ela possui exatamente a mesma guarda da enumeração do marco. O domínio do desempate lê as pontuações recebidas, e é necessário conferir sua disponibilidade no contexto calculado.

A frase proposta é “**Classificatória — pode ser usada nos marcos**”, seguida de usos concretos e da diferença entre parcela e porta. Isso é uma hipótese de redação para teste, sem renomear o atributo normativo ou declarar que ele já determina classificação.

## Estrutura: ordem parcial de dependências sobre etapas ordenadas

As Etapas têm sequência por `order`. As dependências de classificação não formam simplesmente uma linha de etapas: uma etapa pode entrar em vários marcos, um marco combina várias etapas, cortes alimentam etapas declaradas, e o sorteio pode anteceder qualquer avaliação. A faixa seguinte é continuidade de um corte, não uma nova aresta livre. Há ainda portas e recortes sobrepostos.

O código verifica circularidade direta do destino com entradas do mesmo marco pontuado e duplicidade de governo no perfil. Isso não equivale a um editor de grafos arbitrários, nem demonstra um validador geral de todo ciclo indireto. A proposta deve projetar as relações existentes sem impor novas proibições ou permitir ramificações e condições que o backend não oferece. A posição visual do marco depois da última etapa enumerada é uma projeção de leitura, não um campo de ordem próprio do marco.

## Auditoria da experiência apresentada

Capturas efetivas do Chromium, não reconstruções dos templates. Os nomes dos candidatos vistos são os fictícios do `seed_demo`; o banco foi criado para este estudo.

| Evidência | Observação verificável | Consequência cognitiva |
|---|---|---|
| [01 — Etapas](capturas/atual/01-etapas-inicial.png) | Forma, nota, peso e caráter aparecem no cartão; não há consumidores da etapa ali | A pessoa conhece atributos locais, mas precisa lembrar os marcos dos dois perfis |
| [02 — conjunto](capturas/atual/02-classificacao-inicial.png) | Tabela resume forma, corte, critérios, recurso e situação por Perfil | Boa compressão por Perfil; entradas e destino do corte não aparecem como relações |
| [03 — marco aberto](capturas/atual/03-marco-aberto.png) | Etapas com pesos estão visíveis; corte e combinação são blocos distintos | As peças existem; recompor entrada, efeito e destino exige percorrer o cartão |
| [04 — prévia atual](capturas/atual/04-simulacao-existente.png) | Jornada explica empate que impediria corte e torna chegada na próxima etapa indeterminada | Refuta a ideia de simulador meramente decorativo ou posterior à gravação |
| [05/06 — peso ausente](capturas/atual/06-simulacao-incompleta.png) | Aviso antes de salvar o marco e recusa nomeada da prévia | Já há validação antecipada; falta o atalho de correção com alcance entre perfis |
| [07 — marca retirada](capturas/atual/07-marca-retirada.png) | Prova objetiva deixa a lista; a frase destaca títulos como única etapa disponível | A referência antiga perde visibilidade na edição; o operador pode interpretar a nova lista como declaração vigente |
| [08 — Revisão](capturas/atual/08-revisao-apos-marca-retirada.png) | Dois impedimentos apontam a etapa sem marca; o conjunto anterior dizia “sem pendência” | Conferência existe, mas o lugar que mostra usos e o lugar que acusa a inconsistência não coincidem |
| [10 — quarta etapa](capturas/atual/10-quarta-etapa-configurada.png) | Etapa criada pelo botão e configurada com nota, peso e caráter | Criação é alcançável sem shell; falta saber como ligá-la a um marco existente |
| [12/13 — cenário complexo](capturas/atual/13-previa-final-multietapas.png) | Três marcos no Perfil, quatro etapas compartilhadas e jornada parcial na prévia | A visão de conjunto por Perfil não explica sozinha a ordem de dependência dos três marcos |
| [15 — sorteio](capturas/atual/15-sorteio-aviso-atual.png) | Aviso antes de suceder uma relação já existe e dá a primeira data possível | Não é preciso reinventar a validação; representação temporal pode reduzir leitura e cálculo mental |
| [16/18 — compromisso e recusa](capturas/atual/18-recusa-de-execucao.png) | Relação sucessora congelada; ocorrência só com data; tentativa de sucessão do sorteio recusada | A mensagem já explica os três passos de recuperação. A mesma restrição merece ser reconhecida mais cedo visualmente |

### O ciclo de tentativa e erro: onde permanece e onde foi reduzido

O aviso de peso e a apresentação por forma previnem vários envios inválidos. A prévia obtém as regras digitadas antes da gravação e explica efeitos. Não é correto descrever todo o GPS como “só valida ao salvar”.

O ciclo ainda aparece quando a consequência depende de outro agregado: retirar a marca na Etapa muda opções no marco; editar corte afeta participação; mudar o método publicado não atualiza uma relação congelada. O operador precisa reconhecer que existem relações anteriores que continuam válidas como registros e que não somem quando uma opção deixa a lista.

Na reprodução da marca, houve restauração antes de continuar o estudo. **Não foi testado o salvamento da classificação com a referência fora da lista**; o achado confirmado é a invisibilidade na edição e a defasagem de indicação entre conjunto e Revisão. Perda definitiva ou publicação incorreta não foram demonstradas e não são afirmadas.

### Melhorias anteriores que já resolveram problemas reais

- `030`: pergunta sobre origem da ordem, revelação progressiva, combinação derivada para etapa única, método comum do sorteio e distinção etapa/marco.
- `037`: aviso de peso ausente no momento de enumerar a etapa.
- `051`: corte inicial derivado com origem reconhecível, sem escolher silenciosamente empate e continuação; padrão eliminatório apropriado para decisória nova; aplicação com prévia aos demais perfis.
- `052/053`: visão do conjunto por Perfil, edição focal, retorno aos dados digitados, rascunho local, erros com identidade e pendências.
- `078` e incrementos de apresentação: cartões mais legíveis, seleção das etapas por caixas com pesos, formas e ações contextualizadas.
- `094/095`: prévia sobre dados não salvos, população estável, casos-limite, trajetória do desempate, comparação, jornada parcial, listas reservadas e ocupação hipotética.
- `098`: sorteio fictício e resumo de rodadas, sem consultar a fonte real.
- `102`: previsão de inviabilidade desde publicação; aviso anterior ao congelamento; diagnóstico e sequência de recuperação, incluindo fuso institucional na recusa atual.

As restrições anteriores sobre ajuda fora do cartão tinham intenção de reduzir repetição. A recomendação de interpretação contextual precisa de nova especificação que revise conscientemente esse compromisso; não pode ser tratada como cumprimento literal de um requisito antigo que proibisse essa ajuda.

## Custo cognitivo e limites da evidência

| Dimensão | Juízo e evidência | O que precisa mudar |
|---|---|---|
| Visibilidade | Parcial: existe conjunto por perfil, não consumidores por etapa; 02 e 07 | Mostrar entradas e destino sem abrir vários blocos |
| Correspondência | “Etapa” e “marco” são corretos, mas distintos do modelo mental “quem segue?”; 03 | Começar pela decisão e revelar o nome oficial com contexto |
| Memorização | Peso, marca, forma e ordem vêm de outra tela; 01/05 | Usos e origem na mesma unidade de inspeção |
| Previsibilidade | Boa no simulador; menor ao alterar estrutura; 04/07 | Distinguir impacto estrutural de resultado dependente de dados |
| Feedback | Avisos e erros têm causa; a distribuição entre telas exige reconciliação; 06/08 | Referência estável e ação de correção contextual |
| Prevenção | Forte na forma e peso; referências cruzadas podem aparecer só na Revisão | Reusar achados contra o estado proposto antes da confirmação |
| Recuperação | Sorteio já descreve sequência correta; peso exige voltar à etapa | Atalhos com contexto e preservação do digitado |
| Complexidade acidental | Reconstituir uma relação a partir de campos separados | Relação como unidade de edição limitada ao domínio |
| Visão global | Conjunto por Perfil e jornada parcial são complementares | Mapa de dependências disponível antes de simular |
| Autonomia | Ainda incerta sem operadores; walkthrough exige explicar marco, corte e compromisso | Medir compreensão com tarefas, não adotar por aparência |

A quantidade de texto é um sintoma, mas removê-lo indiscriminadamente retiraria proteções importantes. O redesenho deve **externalizar as relações**, preservando detalhes e explicações sob demanda.

### Precisão sobre a porta e a ausência de resultado

“Porta” descreve a participação da etapa decisória no caminho completo; não é uma verificação de conclusão implementada dentro da soma. `combinar` apenas pula a parcela decisória. `universo_classificavel.preparar` lê a consequência eliminatória dos resultados recebidos; a seleção oficial de participantes aplica as regras de progressão de `prontidao`, inclusive a ativação condicional da habilitação anterior. Não atribuir à marca classificatória ou à função de combinação uma exigência universal nova de resultado prévio que elas, isoladamente, não implementam. Os exemplos dos protótipos declaram que a dupla já tem decisão documental favorável; não demonstram o caso de ausência desse resultado.
