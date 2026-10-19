# Plano operacional DEC-14 e proposta de protocolo DEC-15.16

Data: 16/10/2026. **Proposta pendente de pactuação humana.** Não há participantes nomeados,
agenda aprovada ou ambiente persistente autorizado por este documento.

## Participantes e responsabilidades propostas

| Perfil | Responsabilidade proposta | Evidência esperada |
|---|---|---|
| Responsável pelo produto | Aprovar pauta, critérios, protocolo e destino dos achados | Registro prévio de aceite e decisões de escopo |
| Elaborador(es) do Cefor não envolvidos na implementação | Compor e retificar edital; interpretar validações | Conclusão/autonomia, dificuldades, mensagens compreendidas |
| Presidência, avaliador, julgador e comissão | Conferir classificação, recursos, sorteio e convocação conforme permissões | Rito explícito, universo correto, preservação de atos e dependentes |
| Candidatos simulados / pessoas externas ao desenvolvimento | Jornada pública, inscrição e acompanhamento com identidades fictícias | Tarefas sem orientação de implementação; entendimento do prazo e documentos |
| Usuário de tecnologia assistiva e avaliador de acessibilidade | Percurso por teclado/leitor de tela e instrumento de avaliação aprovado | Barreiras observadas por tarefa, sem presumir conformidade por automação |
| Operador de exportação / representante RA | Conferir prévia, download e limites de acesso | Compreensão do arquivo e lacunas; importação real não se presume autorizada |
| Observador/moderador | Aplicar roteiro e registrar sem induzir respostas | Fichas com tempos, intervenção e resultado separados |
| Equipe técnica | Preparar ambiente após autorização, observar falhas e preservar evidência | Versões, configuração sanitizada, resultados técnicos e achados |
| Cefor, encarregado e TI, conforme pauta | Validar decisões administrativas, coleta, controles e rito | Pareceres/aceites identificáveis e questões pendentes |

Uma mesma pessoa pode simular papéis em sessões distintas, respeitando segregação exigida pelo
sistema. Não presumir que isso prova desenho real de concessão institucional. Quantidade e nomes
serão pactuados; o percurso da 072 mantém seu critério existente de quatro de cinco pessoas, sem
redefini-lo aqui ou generalizá-lo para todas as jornadas.

## Ambiente e dados

Propor instância isolada, banco e mídia exclusivos, já preparados, sem credenciais/volumes de
desenvolvimento. Versão do código, PostgreSQL, URL e papéis sintéticos identificados na ficha.
Sem seed, criação de banco, migrations ou publicação persistente antes de autorização específica.
Se ambiente preexistente não existir, apresentar plano de preparação e aguardar decisão, sem
contornar a vedação a migrations desta fase.

Dados: Edital “HOMOLOGAÇÃO SINTÉTICA”, unidades/autoridades de teste, identidades fictícias e
documentos marcados “SEM VALOR ADMINISTRATIVO”. Não importar banco ou documento real; e-mails
somente em coletor local desabilitado para entrega externa, CPFs sintéticos de fixture existente
quando o validador exigir formato, nunca cadastro de pessoa. Sorteio com fonte sintética controlada,
sem consulta à Caixa ou inferência paga. Sem anexos que contenham assinaturas ou marcas pessoais.

Preservar estados do ensaio; não repetir publicação para “limpar” resultado. Reexecução usa novo
cenário identificado, sem apagar atos anteriores. Eventos de auditoria são parte da persistência
e exigem autorização mesmo em fluxo GET que parece apenas leitura.

## Roteiros e critérios de aceite propostos

Cada roteiro: instrução ao participante em linguagem de tarefa; estado inicial; papel; passos pelo
canal destinado ao ator; resultado esperado aprovado antes; resultado observado; evidências;
estado final. As propostas de aceite abaixo não substituem specs, pareceres ou pactuação DEC-14.

| Jornada | Execução proposta | Evidência / aceite proposto e dependências |
|---|---|---|
| H1 — elaboração e publicação | Elaborar edital sintético, revisar, homologar e publicar com papéis exigidos | Sem manipulação manual do banco; cabeçalho/autoridade corretos; validações compreensíveis. .11/.12 e conteúdo editorial dependem de Cefor |
| H2 — período e Retificação | Três cenários da .01; conferir designação e datas .05 | Distinguir publicar de receber; registrar achados/atos e inscrições anteriores/novas; efeitos administrativos não aprovados por sucesso técnico |
| H3 — documentação transversal | Mesmo código com nomes divergentes usado transversalmente e independente; conferir chave/nome/instruções | Mensagens e alcance coerentes; lista e arquivos históricos íntegros; .08/.10 e DEC-07 separada |
| H4 — candidato | Buscar seleção, compreender documentos, iniciar/enviar inscrição, acompanhar, acessar recurso/convocação conforme cenário | Sem ajuda de implementação; finalidade compreendida; não tomar bloqueio .13 como aprovado. Usar roteiros da 072 para critério específico existente |
| H5 — cálculo e atos dependentes | Retificar operação/normalização em cenário sintético autorizado e comparar ordens/cortes/recursos/convocações | Versões e atos anteriores íntegros, efeitos identificados e sucessor explícito. Ratificação .02/.03 não prova atendimento a todas as condições |
| H6 — sorteio e PDF | Conferir etapa, universo e método; distinguir relação congelada de método vigente | Comissão compara PDF e relação; nenhum requisito inventado; .09. Alcance .06 continua pendente; não converter espécie por iniciativa do ensaio |
| H7 — exportação/auditoria | Prévia vazia/nominal, erros, geração e resposta de download; tentar acesso sem permissão/escopo | Identificar exposição e eventos por operação; sem log de planilha; .14/.15. Recebimento/importação exigem prova própria |
| H8 — unidades e autoridade | Conferir catálogo e fluxo de aprovação/aplicação; seleção de autoridade | Sem pressupor competência por permissão; preservar PDF histórico; .11/.12/DEC-04 |
| H9 — acessibilidade transversal | Teclado, leitor de tela e formulários nas jornadas públicas e gestão selecionadas | Barreiras e conclusão por tarefa; avaliação oficial quando pactuada. Sem declarar conformidade legal por checklist |

Roteiros de base: [teste operacional assistido](../../roteiro-teste-operacional-assistido-28-2026.md),
[spec 072](../../../specs/072-jornada-publica-do-portal/spec.md) e seus artefatos de validação,
quickstarts das specs afetadas. Atualizar proposta de roteiro em documento de homologação,
sem reescrever specs nesta fase. Diferença entre versões do sistema deve constar na ficha.

## Protocolo proposto .16 — ainda não aprovado

Antes das sessões, produto, observadores e representantes pactuam instruções, limite inicial de
dez minutos, tratamento de pausas e momento de oferecer ajuda/parada. Dez minutos não é regra
definitiva nem critério automático de falha. Não alterar métricas retroativamente.

| Campo | Definição proposta |
|---|---|
| Conclusão autônoma | Objetivo concluído pelo canal previsto, sem intervenção que destrave tarefa; registrar orientação geral e adaptações de acesso separadamente |
| Conclusão assistida | Objetivo concluído após intervenção de conteúdo, navegação ou domínio; não contar como autônoma |
| Desistência | Participante decide interromper; registrar momento/motivo que desejar informar, sem pressão |
| Tarefa não concluída | Objetivo não atingido até limite pactuado ou interrupção por falha/segurança, sem rotular como desistência se a pessoa não desistiu |
| Tempo | Início, fim, tempo decorrido, pausas e motivo; tempo ativo calculado separadamente se pactuado |
| Intervenção | Momento relativo, tipo (domínio/navegação/técnica), motivo, iniciativa e conteúdo da ajuda |
| Dificuldades | Ponto, comportamento observado e fala sanitizada; hipótese causal separada do fato |

Fluxo proposto: observar sem indicar caminho; ao limite pactuado, perguntar se prefere seguir,
receber ajuda ou parar. Se houver ajuda, registrar antes de reclassificar. Não excluir silenciosamente
casos assistidos do relatório. Tratamento estatístico de tempo/comparação (inclusive excluir etapa
assistida de uma comparação) deve ser prévio e justificado, preservando registro bruto e dificuldades.
Não reduzir critério de autonomia da spec após observar resultados.

## Ficha e tratamento de achados

Ficha por sessão: ID sintético; data/versão; papel; jornada; cenário; início/fim/pausas; resultado
nas quatro classes; intervenções; dificuldades; esperado/observado; captura sanitizada/trilha;
achados; limite da evidência; aceite pelo responsável. Gravar áudio/vídeo de participantes somente
com definição prévia e autorização própria; não pressupor que autorização do ensaio autoriza gravação.

Achado: identificador local; descrição reproduzível; impacto em direito/ato/dado/jornada;
gravidade proposta; evidência; requisito/decisão relacionada; responsável; dependência; proposta de
destino. Separar defeito, dúvida de domínio e necessidade de decisão institucional. Não implementar
correção durante a medição para “salvar” tarefa; registrar mudança e nova rodada se autorizada.

Aceite do plano: participantes/responsáveis, protocolo, ambiente, gravações previstas e critérios
aprovados **antes** das sessões. Aceite da homologação: relatório por jornada, resultados completos,
aceites humanos e pendências encaminhadas, sem aprovação global por presença de testes verdes.
