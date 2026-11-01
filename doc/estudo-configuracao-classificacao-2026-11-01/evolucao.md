# Evolução incremental proposta

Este é um plano de produto/técnico para discussão, não uma spec aprovada, backlog automaticamente priorizado ou autorização de implementação. Nenhuma regra do domínio deve ser alterada para acomodar uma maquete.

## Ciclos e critérios de aceite propostos

| Ciclo | Capacidade observável | Reaproveitamento / dependência | Esforço e riscos | Critérios para avaliar conclusão |
|---|---|---|---|---|
| 0 · Comparar compreensão | Operadores completam as seis tarefas nas interfaces de referência e nas propostas | Estudo e protótipos presentes; preparar casos equivalentes na atual | Baixo/médio; poucos participantes não autorizam generalização estatística | Registrar respostas, causas dos erros e estratégias; não escolher só por preferência estética; incluir primeira configuração e manutenção |
| 1 · Prevenir desencontro de referências | Quem altera uma etapa reconhece seus marcos consumidores e referências incompatíveis antes de confirmar | Índice transitório de usos; achados existentes; preservação do rascunho | Baixo/médio; risco de ocultar ou descartar referência filtrada | Retirar marca mantém o uso inválido visível; nomeia marcos/perfis; restaurar ou corrigir mantém identidades; backend continua recusando a publicação inconsistente |
| 1 · Representar a precedência do sorteio | Operador explica por que esperar a noite não resolve e qual ato falta | `viabilidade`, diagnóstico da relação, instante efetivo da fonte, fuso comum | Baixo; risco de substituir limite real por horário digitado | Mostrar congelamento, limite inferior e comparação; distinguir previsão/observado; mesmo dia com fonte horária posterior não é recusado genericamente; manter avisos e permissões atuais |
| 2 · Redesenho principal A+D | Configurar relação de entradas, ordenação e destino no mesmo contexto, com revisão de alcance | Parser e commands atuais; projeção de leitura; evidência do ciclo 0 | Médio; foco, rascunho, acervo e escala | Criar e revisar cenário complexo sem shell; três marcos, porta, nota e corte legíveis; não perguntar decisão dedutível sem exibir origem; nenhum vínculo livre não suportado |
| 2 · Conferência curta de E | Revisor identifica resultado/origem/alcance da alteração | Mesma projeção do mapa e versão base; princípio de inferência explícita | Médio; paráfrase incompleta pode parecer norma | Revisão antes/depois lista objetos e perfis afetados; sem cópias silenciosas; norma publicada e fonte estruturada continuam únicas |
| 3 · Exemplos junto da decisão | Abrir a prévia existente no contexto da regra e comparar com entradas fixas | Serviços 094/095/098; população estável, limites e trajetória já existentes | Médio; recomputação excessiva e falsa impressão de simulação completa | Solicitação explícita; rótulo fictício persistente; calculado/contexto/indeterminado distintos; fonte externa nunca chamada na composição; nenhuma escrita normativa pela prévia |
| Posterior, só se demanda comprovada | Explorar casos escolhidos, comparação avançada ou busca/matriz para grande escala | Pesquisa com editais extensos; orçamento de custo e abrangência | Médio/alto; testes combinatórios e aprendizagem | Definir problema de usuário e escopo antes de ampliar; recusar custos sem ganho observável |

## Arquitetura mínima que sustenta a experiência

Não é necessária migração de configuração. `EtapaAvaliacao`, `MarcoClassificatorio`, regras de corte, critérios, fatos e métodos continuam sendo fontes. A necessidade nova é **ler suas relações no conteúdo proposto**, inclusive referências temporariamente inválidas. Isso justifica um DTO/projeção transitória e uma camada determinística de apresentação, não uma entidade persistente de “regra visual”.

1. Parser da interface lê o digitado sem gravar, como a prévia já faz. Conteúdo e base têm identificadores/revisão estáveis.
2. Funções existentes respondem forma, operação efetiva, origem do método, etapa governada e achados. Diagnóstico de execução usa seletores do ato adequado, no canal autorizado.
3. Índices de consumidores por etapa, marco, fato e método permitem impacto estrutural. A ordem das etapas acrescenta relações de progressão; isso não autoriza concluir impactos pessoais.
4. HTML renderizado pelo servidor apresenta relações, frases e correções; HTMX já disponível pode transportar propostas e preservar foco. Uma biblioteca de grafos não se justifica no primeiro ciclo.
5. Confirmar usa os mesmos commands, controle de revisão, transação, auditoria e autorizações. Publicado leva ao rito de Retificação; resultados/ordens/cortes usam sucessão quando cabível.

Essa projeção deve ter cobertura de interpretação e equivalência, especialmente para: etapa única antiga com soma/peso diferente de 1; porta enumerada; marco só com portas; critério sem valor; corte estrito com empate; destino `NONE` versus não declarado; método próprio versus comum; retirada de etapa/referência; dois Perfis; ampla/reserva; fonte sem horário; obsolescência e concorrência.

O diagnóstico de prontidão não precisa virar um serviço universal que replique todos os módulos. Pode adaptar respostas existentes a um vocabulário comum de apresentação, mantendo cada decisão no seu domínio. Nomear sempre operação, recorte, instante e versão conferidos. Leituras de prontidão podem envelhecer; a execução revalida tudo.

## Segurança, dados e compatibilidade

- Nenhuma prévia usa candidatos reais por padrão. Candidatos fictícios têm origem visível; compartilhar cenários não divulga dados pessoais.
- Projeção e diagnóstico respeitam o mesmo escopo do ator. Identificador na URL ou no grafo não concede acesso. Não oferecer ação que o papel não pode executar; explicar responsável quando pertinente.
- Ausência de permissão no backend, triggers append-only e histórico não são flexibilizados. A interface não apaga configurações ou atos para “consertar” um vínculo.
- A apresentação de acervo usa as mesmas funções de leitura histórica; não normaliza publicações antigas para defaults novos. Testar ambos os caminhos: rascunho e norma já publicada.
- CSS/JS externos e CSP do projeto preservados. Não se introduz script inline no template.
- A aplicação em vários Perfis continua com prévia do alcance e autoria. Não copiar silenciosamente peso/forma para cada marco.

## Acessibilidade e operação

Adotar as diretrizes já praticadas no projeto, com controles HTML nativos e complementação apropriada. Não afirmar conformidade completa por uma inspeção automática.

- Mapa baseado em lista/tabela, com botões por objeto. Tab alcança etapas/marcos; Enter/Espaço selecionam. O vínculo é lido como entrada, marco, corte e destino; setas decorativas são ocultas da tecnologia assistiva.
- Caminho textual equivalente e filtragem por Perfil. Sem dependência de arrasto ou mouse, sem adicionar `role=application` ou grid incompleto.
- Foco retorna ao objeto acionador quando o detalhe fecha; na remoção de um controle, vai para título/correção equivalente. Resultado assíncrono é anunciado por região viva sem repetição constante.
- Causa, alcance e ação vinculados aos campos; não só cor ou ícone. Itens incompletos não recebem erro enquanto a pessoa está começando a responder.
- Em tela estreita, relação e inspetor se empilham; o contexto selecionado precisa continuar identificável. Uma barra de ações não pode cobrir campo ou mensagem com zoom.
- Validar com teclado completo, leitor de tela, zoom/refluxo e contrastes no protótipo implementado. A maquete atual verifica parcialmente foco, teclado e largura móvel; não substitui avaliação assistiva humana.

## Pesquisa que deve preceder adoção

Recrutar operadores que conheçam editais, misturando quem já usa GPS e quem chega sem seu modelo interno. Por exemplo, uma primeira rodada qualitativa com 5–8 pessoas pode revelar problemas recorrentes; não é um tamanho para validar percentuais de ganho. Usar tarefas e gabaritos de [avaliacao.md](avaliacao.md), alternar ordem e observar sem ensinar.

Registrar se identificam a porta, os consumidores e o destino do corte; se distinguem incompleta de inválida e pronta de apenas configurada; se explicam a diferença entre data da fonte e horário do edital. Se não conseguem explicar essas relações depois do uso, a proposta precisa ser revista, mesmo que seja visualmente preferida.

Após a escolha do usuário e a revisão do estudo, criar a spec SDD do incremento escolhido. Achados laterais continuam registros separados; este plano não atribui automaticamente prioridade a uma implementação seguinte.
