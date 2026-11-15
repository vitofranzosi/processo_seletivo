# Registro das revisões de 14/11/2026

*Três pareceres, trazidos pelo usuário depois da entrega do estudo. O primeiro apontou seis
correções, o segundo três, e todas foram conferidas contra os arquivos e todas procedem; o terceiro
foi favorável ao merge e à P0, e pediu cuidados para o piloto. Este documento registra o que cada
um dizia, o que foi conferido e o que mudou. Nas duas primeiras rodadas nada no produto foi
alterado, e os protótipos, as capturas e as medições continuam os da primeira versão; a P0, que
veio depois da terceira, está em [08-p0.md](08-p0.md).*

## Primeira rodada

### O parecer, em resumo

Aprova a direção visual **para um piloto**, e pede que o plano seja revisto antes de implementar. O
estudo sustenta a necessidade de consolidar componentes e composições; ainda não demonstra que todas
as regras propostas melhoram a operação.

### Os seis pontos

| # | O que o parecer apontou | O que foi conferido | Veredito |
|---|---|---|---|
| 1 | "A causa é uma só" é categórico demais; um componente também pode ser bem definido só por CSS | o estudo mostra correlação (71 aberturas, uma peça compartilhada), e não uma causa única | procede |
| 2 | A ocupação da metade direita não deve virar meta de qualidade | [`medicoes/largura.js`](medicoes/largura.js) conta intervalos verticais com conteúdo além do meio; descreve distribuição, e não desperdício. O plano exigia "acima de 45%" | procede |
| 3 | Os ganhos dos protótipos não vêm de comparação equivalente | os protótipos resumem conteúdo, têm outra quantidade de registros e estimam altura; o próprio relatório dizia isso, sem tirar a consequência | procede |
| 4 | As afirmações de acessibilidade vão além da triagem feita | [`medicoes/metricas.js`](medicoes/metricas.js) aceita `title` ou a presença de atributo ARIA como rótulo, e aproxima o fundo no contraste | procede |
| 5 | O piloto se contradiz em três lugares | P1.4 mudava `.acao` em cerca de 40 telas com o aceite exigindo nada fora do piloto; P1.6 estava fora do piloto e o aceite cobrava os guardiões; a Ocupação estava descrita como "sem tocar em ato", e o template tem cinco formulários de operação | procede, nas três |
| 6 | Algumas convenções nascem rígidas antes da validação | um botão cheio por tela, quatro pontos de quebra, seis tamanhos e um aviso por tom estavam escritos como regra; no protótipo de Compor a 375 px, pendências e ajuda aparecem depois de "Avançar" | procede |

### O que mudou em cada documento

| Documento | Mudança |
|---|---|
| [README.md](README.md) | o diagnóstico passa a falar em falta de contratos compartilhados e de mecanismos de adoção, sem causa única; a largura é descrita como distribuição; os protótipos mostram viabilidade, e não ganho; a acessibilidade é triagem; o piloto e as decisões apontam para a versão revista |
| [02-evidencias.md](02-evidencias.md) | nova seção de limites do instrumento (rótulo, contraste, alvo, o que não foi medido); a causa de S1 vira "causa provável"; S2 diz o que a medida não prova; o §5 troca "o que os números dizem de bom" por "o que o instrumento não acusou" |
| [03-design-system.md](03-design-system.md) | nova seção 0, que separa a direção experimental das hipóteses; "componente no template" vira "componente com contrato"; tipografia, pontos de quebra e guardiões marcados como decisão posterior ao piloto; as regras de uso viram convenções de partida; o trilho no celular entra como ponto aberto |
| [04-prototipos.md](04-prototipos.md) | nova seção sobre o que as comparações provam e o que não provam, com a diferença de cada protótipo para o estado real; as tabelas passam a dizer "indicativa"; a estimativa de altura da Lista saiu; o defeito de ordem no celular está registrado |
| [05-roadmap.md](05-roadmap.md) | o piloto foi reescrito: estilo delimitado por folha de grupo e classe de escopo, sem mudança global de `.acao`; nenhum guardião novo no aceite; a Ocupação com os atos e os estados que pratica; a primeira comparação equivalente; acessibilidade conferida à mão; legibilidade e localização da ação no lugar da meta de largura; as decisões divididas em duas levas |

### O que a revisão recomenda aprovar, e o que adia

| Aprovar agora, como direção experimental | Decidir depois do piloto, com a equipe |
|---|---|
| os neutros da tela de entrada | a redução tipográfica |
| a hierarquia: cabeçalho de página e composições | o recolhimento e o deslocamento de explicações |
| os componentes: botão, indicador, aviso, cartão | os limites rígidos e os guardiões novos |
| o piloto de três telas, com o estilo delimitado | a mudança global de `.acao` e dos tokens antigos |

**É recomendação do parecer, incorporada ao plano. A decisão continua sendo do usuário.**

## Segunda rodada

Um segundo parecer conferiu a revisão, considerou o estudo uma boa base para especificar o piloto e
apontou três ajustes, todos no plano. Os três procedem.

| # | O que o parecer apontou | O que mudou no [roadmap](05-roadmap.md) |
|---|---|---|
| 1 | A P0 dentro do piloto contradiz "nada fora do piloto muda": ela altera a Visão Geral e avisos de outras telas | a P0 virou entrega própria, anterior ao piloto; ao fim dela o instrumento roda de novo, e o resultado é a referência contra a qual o piloto se compara |
| 2 | Exigir o texto do `main` idêntico, como sequência, reprova a mudança legítima de posição | o aceite passa a conferir textos, quantidades, associações e ações, como conjunto; a ordem ganhou critério próprio, com as sequências que não se invertem (fundamento, consequência, confirmação) declaradas na spec |
| 3 | A variante tipográfica estava com escopo ambíguo: o piloto a excluía, e a entrega a previa | virou experimento opcional, separado do aceite e fora da `main`; sem ele, a redução tipográfica fica inteira para depois |

O parecer também corrigiu uma frase deste registro: a comparação equivalente pode ser feita em
protótipo, e fazê-la no produto é escolha do plano. Corrigido abaixo.

**Sobre as duas decisões**, o parecer é favorável à direção experimental e a manter a Ocupação no
piloto, e sugere levantar quanto dos estados dela as fixtures existentes já cobrem antes de pensar
em trocá-la por custo. Não considera necessário refazer protótipos nem o rastreio. A decisão
continua sendo do usuário.

**Próximo passo, segundo o parecer:** a especificação do piloto e o plano técnico, conforme a
Constituição. A aprovação da migração completa continua dependendo dos resultados.

## Terceira rodada

Um terceiro parecer, também de 14/11, conferiu o estudo depois das duas rodadas. **É favorável ao
merge do estudo e ao início da P0.** Não pediu correção nos documentos; pediu cuidados para o
piloto, e confirmou a sequência que o usuário aprovou.

### A sequência aprovada

1. **A P0, as correções críticas**, como entrega própria e anterior ao piloto.
2. **Uma nova referência medida depois da P0**: o instrumento roda de novo, no mesmo banco de
   cenários, e o resultado é a base contra a qual o piloto se compara.
3. **A spec do piloto pelo Spec Kit**, com a confirmação de ato, a Ocupação de vagas e a Lista de
   Processos.
4. **A validação com a equipe**, que executa as mesmas tarefas na versão antiga e na nova.

### O que o parecer pede ao piloto

| # | Pedido | Onde ele vale |
|---|---|---|
| 1 | Manter a fonte, os tamanhos, os textos completos e as ações existentes | já é o que o [roadmap](05-roadmap.md) diz em *O que entra, e como fica delimitado* e em *A primeira comparação*; o parecer o reforça como condição |
| 2 | Deixar para depois a redução tipográfica, o recolhimento de explicações, a coluna "Fase e próximo passo" e as mudanças globais de CSS | os quatro já estavam fora do piloto: a Lista de Processos entra sem a coluna nova, e a coluna continua sendo a decisão 9 do [roadmap](05-roadmap.md). O parecer os confirma como adiados, e não só como fora do escopo |
| 3 | A spec do piloto deve dizer **explicitamente** se as duas telas de conferência da Ocupação (`ocupacao_acrescimo.html` e `ocupacao_nao_preenchida.html`) entram | a spec do piloto; o roadmap deixava a decisão para ela sem exigir que fosse escrita |
| 4 | As confirmações de ato devem ser avaliadas **pelo entendimento das consequências e pela prevenção de erro**, e não só pela composição | a spec do piloto, nos critérios de aceite e na validação com a equipe (passo 4): o que conta é se quem confirma sabe o que vai acontecer e se evita o ato errado |

Os pedidos 3 e 4 são para a spec do piloto, que não é desta entrega. Ficam registrados aqui para
que ela os encontre.

### O que a P0 entregou

A P0 está no PR que acompanha esta rodada, com o que mudou, as medições antes e depois e a nova
referência em [08-p0.md](08-p0.md).

## O que continua aberto

- **A comparação equivalente não foi feita.** Os protótipos são os da primeira versão. Ela pode ser
  feita em protótipo; este plano escolhe fazê-la no produto, como primeiro passo do piloto, porque
  ali os estados, as permissões e os textos são os reais.
- **A posição do trilho no celular.** O defeito do protótipo de Compor está registrado, e não
  corrigido: a correção depende de decidir a ordem por conteúdo, tela a tela.
- **A acessibilidade.** Continua sendo triagem até a conferência manual do piloto.
- **O custo de fotografar os estados da Ocupação.** O levantamento das fixtures foi feito depois
  da segunda rodada ([07-fixtures-da-ocupacao.md](07-fixtures-da-ocupacao.md)): a suíte desenha 51
  dos 63 ramos visíveis da tela, e montar cenário deixou de ser o custo. Falta o caminho para
  levar esses estados a imagem e a um banco que a equipe abra. O levantamento também corrigiu o
  plano: a tela tem sete formulários, e não cinco. Manter a Ocupação ou trocá-la continua sendo
  escolha do usuário.
- **O rastreio não foi refeito** nas duas primeiras revisões: as medidas dos documentos 01 a 05 são
  as de 14/11, sobre `37ed0ad0`. Ele foi refeito ao fim da P0, num banco montado do zero, e o
  resultado é a referência do piloto ([08-p0.md](08-p0.md)).
- **As duas decisões do piloto que o terceiro parecer pediu escritas**: se as telas de conferência
  da Ocupação entram, e como as confirmações serão avaliadas. São da spec do piloto.
