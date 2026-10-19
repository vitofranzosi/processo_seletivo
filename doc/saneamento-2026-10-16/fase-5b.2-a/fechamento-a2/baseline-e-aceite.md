# Baseline sintética — critérios objetivos e cobertura

Revisão documental de `f4-sintetico-v1`. Nenhuma geração/carga foi executada e nenhum hash de
dataset foi inventado. Fonte: [baseline vigente](../../fase-5b.1/baseline.json),
[receitas](../../fase-5b.1/cenarios.json), Fase 5A e plano F4; fonte técnica:
`backend/processo_seletivo/processos/management/commands/seed_demo.py`.

## Critérios de aceite antes de autorizar carga

| Critério | Evidência objetiva requerida | Reprovação / situação atual |
|---|---|---|
| Determinismo de entrada | Manifesto com commit, imagens/digests/plataforma, lock, versão de schema, parâmetros, fuso, T0 e fonte sintética de sorteio; nenhuma aleatoriedade sem seed declarada | Parâmetro implícito, relógio não controlado ou versão ausente bloqueia; T0 ainda requer decisão |
| Ausência de origem real | Catálogo campo a campo de valor/regra geradora e arquivo fictício; atores/candidatos inventados, e-mails `.test`, sem import/dump/consulta a cadastro real; todo documento marcado sintético | Nome de pessoa real, dado copiado, endereço externo ou origem sem prova bloqueia. CPF de fixture não prova inexistência de titular e não deve ser pesquisado |
| Unidades/autoridades | Manifesto identifica exatamente o catálogo e as autoridades que serão usados | Seed sincroniza `ler_unidades()` e usa Cefor institucional; não chamar esse catálogo de fictício. Para exigência integralmente sintética, preparar unidade/autoridades fictícias via mecanismo existente em plano aprovado; não presumir exceção para catálogo real |
| Integridade referencial | 100% dos IDs referenciados resolvidos no mesmo manifesto, sem órfãos, vínculos/escopos de permissão corretos, datas/versões/fundamentos identificados | Um órfão, referência externa, chave reutilizada ou versão incoerente reprova. Consultas de conferência futuras devem ser somente leitura |
| Conteúdo temporal | Decisão registrada entre T0 absoluto fixo e janelas relativas à sessão; todas as janelas abertas/encerradas/canceladas esperadas demonstráveis na data aprovada | F4 propõe T0 da execução; baseline fixa 16/10/2026 e app usa relógio real. Essa diferença ainda não está resolvida; não monkeypatchar retrospectivamente para obter resultado |
| Reprodutibilidade semântica | Duas instalações novas autorizadas, mesmas entradas; igualdade de representação canônica por alias estável, relações, estados, datas normativas, cálculos e universo do sorteio | Não exigir UUID/bytes idênticos sem garantia. Registrar também hashes brutos; somente diferenças técnicas explicitamente listadas podem ser normalizadas |
| Canonicalização | Lista de campos/ordenação e mapa bijetivo alias→UUID revisados antes do ensaio; rejeitar campo desconhecido | Não omitir datas normativas, fundamento, ator ou relação para fazer comparação passar. Timestamps de execução/UUIDs só via lista aprovada e preservação do original |
| Quantidade e limites | Manifesto por entidade e cenário, previsão de máximo e medição futura antes/depois; orçamento total até 20 Editais/100 inscrições/5000 eventos, ainda sujeito à aprovação | Total desconhecido ou maior que teto bloqueia antes da carga; não truncar para caber. Hoje não há orçamento demonstrado/enforcement |
| Cobertura | Cada variante abaixo possui alias de cenário, objetos/atores, pré-condições e operação posterior separados | Seed não materializa automaticamente as 14 receitas; um cenário sem precondição bloqueia sua demonstração, não deve ser preenchido como observado |
| Separação de carga/demonstração | Manifesto de atos inevitáveis da preparação separado da lista de atos a observar; estado inicial por subcaso | O seed já publica, classifica, sorteia e convoca para preparar estados; esses atos não são a demonstração nem seu resultado |
| Recuperação | Hashes/manifesto inicial e procedimento de nova instalação/namespace com autorização própria | Não restaurar sobre atos existentes, limpar tabelas, reexecutar seed ou apagar reserva; falha parcial é preservada |

Estado: **não aprovada para carga**. Os critérios acima são proposta técnica de aceite, não
ratificação administrativa nem prova de que o gerador os satisfaz.

## Inspeção do seed e limites concretos

`_semear` (linha 672 em diante na base inspecionada) chama `_unidade_e_autoridades` antes de
verificar Processo existente. Há transações por partes, não uma única transação global.
Os caminhos numéricos criam primeiro, segundo, terceiro e quarto Editais; o último fica em
elaboração e pertence ao Processo do ano seguinte. Não assumir um único Processo ou um único ato.
As contagens finais de inscrições/eventos não foram medidas.

O seed mistura comandos de domínio com escrita ORM de preparação, por exemplo anexos em
`_anexar_formularios` e inscrições em `_sortear`/`_divulgar_resultado`. Não descrevê-lo como
execução exclusivamente pelas interfaces de usuário. Isso é preparação técnica, não homologação
de jornada. Nenhum código funcional foi alterado para adaptá-lo à baseline.

## Cobertura das 14 receitas e variantes

| Receita | Pré-condição obrigatória a preparar | Demonstração posterior, com gate separado | Cobertura atual |
|---|---|---|---|
| P01-A | Edital completo homologado não publicado, único Evento cancelado | Primeira publicação recusada pelo impeditivo específico | Variante não garantida pelo seed |
| P01-B | Outro Edital publicado, inscrições rascunho/enviada e janela aberta | Retificação cancela Evento; comparar aceitas e novo envio | Seed tem publicação/retificação, mas não prova essa variante |
| P01-C | Estado cancelado e segundo Evento válido, aliases distintos | Redesignação/vigência/calendário e tentativa de envio | Complemento necessário |
| P06-A | Snapshot sintético anterior ao degrau 10, método ausente | Elevação em memória; persistência só se aprovada separadamente | Fixture em memória planejada, não carga automática |
| P06-B | Sorteio previsto; dois estados: sem relação e com relação congelada | Retificar método e comparar hash da relação | Seed faz sorteio; isso não substitui estados anteriores requeridos |
| P06-C | Classificação por pontos sem ordem e, em outro estado, com ordem | Tentar mudança pelas operações existentes; registrar recusa | Seed tem classificação, não ambos os negativos comprovados |
| P07-A | Mesma identidade, fundamento explicitamente fictício errado | Corrigir foundation/version/effectiveFrom; preservar vínculos | Complemento necessário |
| P07-B | Duas identidades fictícias e mapa de referências | Recusar troca de id; sucessão legítima não implementada | Apenas recusa pode ser demonstrada; mérito permanece pendente |
| P15-A | Ator autorizado, entrada sem população escolhida | GET, metadados/trilha | Baseline deve fornecer estado e ator exatos |
| P15-B | População com lacunas agregadas sem nominal | GET e eventos antes/depois | Variante específica não garantida |
| P15-C | Declaração sensível fictícia incompatível com destino | Prévia nominal e evento sem conteúdo sensível copiado | Complemento específico necessário |
| P15-D | População incompleta/modalidade desconhecida | Recusa, mensagem e trilha | Variante negativa não garantida |
| P15-E | Prévia válida/requerimentos enviados e duas assinaturas: válida/obsoleta | POST, geração e recebimento local distinguidos | Seed prepara requerimento de um caso; não cobre todas as tentativas |
| P15-F | Sem permissão e outro escopo, mesmos objetos sintéticos | GET/POST negados e ausência de arquivo | Atores/permissões explícitos ainda precisam de manifesto |

Não há prova de cobertura completa das dez famílias ou das 43 condições só porque o seed é
navegável. A aceitação futura precisa registrar casos não executados e respectivas razões,
incluindo dependências institucionais. Homologação humana e ratificação não resultam da carga.
