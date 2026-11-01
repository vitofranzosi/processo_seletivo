# Jornadas reconstruídas com dados de desenvolvimento

Ambiente nativo Django/PostgreSQL, papel de runtime próprio e Chromium a 1440 × 1000. Preparação normativa exclusivamente por semente e comandos oficiais em banco novo. Interações citadas como executadas foram feitas pelo navegador; preparação de estado não é apresentada como capacidade de UI nova.

**Contagem de decisões:** os números abaixo contam tópicos de domínio agrupados para a tarefa descrita, não cliques, controles, tempo ou desempenho medido. A quantidade varia com a norma. Navegações e pedidos HTTP não foram instrumentados; não se inventou uma métrica quantitativa de usabilidade.

## A — Sorteio, compromisso e fonte posterior

**Intenção:** comprometer um universo, observar a ocorrência declarada e constituir uma ordem auditável. **Conhecimento prévio:** método publicado, inscrições encerradas, eventual habilitação, recorte correto, fonte e granularidade; saber que congelamento e sorteio são atos distintos.

**6 tópicos de decisão:** método comum/próprio; universo/recorte e habilitação; ocorrência e instante normativos; normalização/substituição; momento/motivo de compromisso; confirmação do ato. Os detalhes do método não desaparecem por serem agrupados.

**Executado:** a semente publicou e sorteou o caso simples com fonte de demonstração que informa horário. Para investigar a recusa, um comando de Retificação no banco exclusivo alterou o método para a fonte fictícia que só informa data. Como presidência no navegador: ler aviso → justificar e publicar relação sucessora → observar 9001 → pedir anulação com sucessor → receber recusa explicada. A interface manteve o sorteio anterior e a relação nova. Capturas [15](capturas/atual/15-sorteio-aviso-atual.png), [16](capturas/atual/16-relacao-sucessora-inviavel.png), [17](capturas/atual/17-ocorrencia-observada-inviavel.png), [18](capturas/atual/18-recusa-de-execucao.png).

No ramo contrastante, preparado em um segundo Processo sintético independente, uma Retificação manteve a fonte de demonstração **com horário** e declarou a referência 9003. Pelo navegador foram publicados nova relação, observação posterior e sorteio sucessor. Isso demonstra que mesmo dia não é uma proibição genérica. Essa troca de fonte é ensaio sintético, não recomendação para contornar a Loteria Federal em produção. Capturas 19–21.

**Relação oculta:** o edital pode anunciar um horário, mas o adaptador só tem data; o dado efetivo é 00h. Outra relação importante é o método da versão comprometida, que não muda com a Retificação seguinte.

**Erro e feedback:** aviso antes do compromisso e diagnóstico posterior já existem. A mensagem após a tentativa diz: “A relação foi congelada em 01/11/2026 20:27… [a extração] só pode ser datada a partir de 01/11/2026 00:00”. A rota redireciona, mas o ato não é constituído; não interpretar HTTP 302 como execução bem-sucedida.

**Prevenção/recuperação:** publicação original inviável é impedida; no congelamento, a política atual avisa e permite o compromisso. A recuperação de caso real com fonte só de data é retificar a extração para dia posterior disponível, suceder a relação, observar a ocorrência admissível e constituir. Esperar até a noite ou só suceder a relação não resolve.

**Como confirmar:** verificar fonte, referência, limite observado, instante da relação, versão/hash do método e ato/manifesto constituído. Mais útil durante a decisão: comparação dos instantes e lista das condições ainda pendentes, com responsáveis distintos. [Protótipo temporal](prototipos/mapa.html?vista=tempo).

## B — Classificação por nota e peso ausente

**Intenção:** combinar objetiva e títulos conforme os pesos do edital. **Prévio:** quais etapas pontuam, escala, pesos e regra de empate/corte.

**5 tópicos:** etapas de entrada; pesos na origem; operação/normalização; arredondamento; desempate e corte. Critérios de desempate são diferentes das notas totais lançadas por avaliadores.

**Executado:** abrir DOC-INFO, inspecionar entradas e simular; retirar peso de objetiva no passo Etapas e salvar; voltar à Classificação, ler aviso e pedir prévia; restaurar peso e salvar. [03–06](capturas/atual/06-simulacao-incompleta.png).

**Oculto:** peso mora em outra etapa de composição e pode afetar vários marcos/perfis. **Erro:** ausência não é peso 1; soma e média não são equivalentes se os pesos não somam 1. **Feedback:** aviso de peso no cartão já previne erro; a prévia diz “Etapa enumerada pelo marco sem peso declarado”. Ela usa dados do marco ainda não salvos.

**Recuperação:** voltar à etapa, declarar peso, retornar ao marco. O sistema não tem que escolher por quem conhece o edital. **Confirmação:** fórmula interpretada e prévia com população estável/casos-limite, além da conferência normativa. Informação mais útil: “estas etapas, estes pesos, esta fórmula e estes consumidores”, com atalho de ida e volta.

## C — Múltiplas etapas e dois cortes que alimentam avaliação

**Intenção:** objetiva seleciona para títulos; objetiva+títulos selecionam para documental; a final combina notas de objetiva, títulos e didática e exige documental.

**7 tópicos:** ordem/forma das etapas; entrada de PRE; alvo/destino de PRE; entrada/operação de POS-TIT; alvo/destino de POS-TIT; entrada/porta/critério de FINAL; alvo final por recorte. O número representa agrupamentos, não um limite de campos.

**Executado:** acrescentar quarta etapa pela UI, marcar documental como classificatória e conservar seu caráter decisório; editar primeiro marco como POS-TIT; acrescentar PRE e FINAL; salvar e reabrir, verificando persistência; simular e revisar. A captura 12 mostra três marcos e 13 mostra a jornada da prévia. Dados de identidade em [cenario-configurado.json](cenario-configurado.json).

**Oculto:** o marco não é uma etapa; a mesma nota entra em vários lugares; porta não tem peso; ordenação visual/código do marco não governa participação. **Erro possível:** POS-TIT alimentar títulos, de onde tira sua própria nota, ou dois marcos governarem documental. Isso é configuração inválida; não é mera falta de preenchimento.

**Feedback e recuperação:** backend confere circularidade e duplicidade de governo. A tabela atual resume os três marcos, mas suas entradas e destinos não formam um percurso explícito. A correção é editar a relação declarada, sem deduzir o destino pela posição na tela.

**Como confirmar:** ler entradas/destinos da configuração completa e explorar um marco de cada vez. A prévia calcula o selecionado; outros são contexto/indeterminados. A confirmação de “todo candidato passa corretamente por toda a cadeia” **não foi demonstrada pela simulação** e não deve ser prometida. Informação mais útil: mapa tipado com descrição textual e fronteiras do que foi calculado.

## D — Alterar a marca de uma etapa anterior

**Intenção:** revisar se objetiva deve participar da classificação sem perder a visão das regras existentes. **Prévio:** etapa compartilhada e marcos que a enumeram.

**4 tópicos:** qual propriedade mudar; todos os consumidores afetados; manter/restaurar marca ou rever enumerações; verificar consequência antes da confirmação.

**Executado:** após restaurar o peso no cenário inicial, retirar `Classificatória` de objetiva e salvar Etapas. A tela Classificação deixou apenas títulos na seleção e mostrou a frase da única etapa disponível. A tabela por Perfil dizia “sem pendência”; a Revisão acusou os dois marcos. A marca foi restaurada. [07](capturas/atual/07-marca-retirada.png), [08](capturas/atual/08-revisao-apos-marca-retirada.png).

**Oculto:** uma opção removida da lista não apaga sua referência normativa anterior. **Erro possível:** acreditar que os marcos já passaram a usar só títulos. **Feedback:** a revisão protege publicação, mas a edição não apresenta a referência agora inválida. **Recuperação:** restaurar marca ou ajustar cada marco de forma explícita e conferir os dois perfis. Não foi ensaiado salvar a Classificação inválida; não se afirma perda de dados.

**Como confirmar:** comparar consumidores antes/depois; não basta observar que o checkbox mudou. Mais útil: lista de marcos afetados no momento da proposta e referências inválidas ainda selecionáveis para correção.

Nos protótipos, o mesmo problema usa **títulos**, para mostrar três consumidores em dois perfis no cenário complexo. É um caso equivalente por referência, não transcrição literal do ensaio com objetiva.

## E — Ampla, reserva e alvo por recorte

**Intenção:** compreender por que autodeclarado também aparece na ampla e por que a mesma regra pode ter cortes diferentes entre listas.

**4 tópicos:** Perfil; modalidade/identificação da ampla; origem do alvo no quadro ou fixo; ocupação/reversão declarada. **Prévio:** reserva não é conjunto exclusivo e corte não é ocupação.

**Executado:** prévia do DOC-INFO com ampla e PPP e leitura de jornada/ocupação no navegador; a população fixa trouxe empate na ampla e explicação de que a ocupação de reservas depende de quem ocupa pela ampla. O modelo de cálculo e os testes de equivalência por recorte foram inspecionados/executados. Não foram criadas inscrições reais ou nova política de cotas.

**Erro possível:** somar os totais das listas como pessoas distintas ou aplicar a quantidade da ampla a toda reservada. **Feedback:** a prévia atual já explica a sobreposição e as hipóteses de uma rodada sem chamadas anteriores. **Recuperação:** conferir o quadro e o tipo de alvo, selecionar recorte e caso-limite apropriado, sem alterar a população para obter resultado desejado.

**Como confirmar:** ler origem do alvo e distinguir ordem, corte e ocupação. Mais útil durante a decisão: resumo por recorte sob demanda e exemplo de autodeclarado dentro da ampla. Não colocar todos os candidatos de todas as listas no mapa de configuração.

## Conhecimento interno exigido nos pontos críticos

O operador não deveria precisar saber que o peso está em uma tabela de Etapas, que a enumeração ocorre em JSON publicado, que um marco é posicionado pela última etapa, ou que uma referência omitida por um seletor pode continuar persistida. Precisa entender os conceitos administrativos equivalentes: **quais resultados a ordem usa**, **quem o corte manda analisar**, **quais decisões são compartilhadas** e **qual compromisso de fonte a relação preservou**.
