# Auditoria de UI/UX e consolidação do design system do GPS

**Data:** 14/11/2026 · **Base:** `main` em `37ed0ad0` · **Natureza:** investigação, diagnóstico e
proposta. **Nada no produto foi alterado**, e nada deve ser antes da decisão sobre a direção visual.

> **Revisto em 14/11/2026**, em duas rodadas, depois de um parecer que apontou seis correções e de
> outro que apontou mais três. O que mudou, e por
> quê, está em [06-revisao.md](06-revisao.md). Em resumo: o diagnóstico ficou menos categórico, a
> medida de largura deixou de ser meta, os ganhos dos protótipos passaram a ser indicativos, as
> afirmações de acessibilidade se limitam à triagem feita, e o piloto foi reescrito.
>
> **Depois da terceira rodada veio a P0** ([08-p0.md](08-p0.md)): as correções críticas no produto, e
> a nova referência medida sobre elas, contra a qual o piloto se compara. As medidas dos documentos
> 01 a 05 continuam as de 14/11 sobre `37ed0ad0`.

| Entregável | Arquivo |
|---|---|
| A. Inventário de interfaces | [01-inventario.md](01-inventario.md) |
| B. Relatório executivo | este documento |
| C. Relatório de evidências | [02-evidencias.md](02-evidencias.md) |
| D. Proposta de design system | [03-design-system.md](03-design-system.md) |
| E. Protótipos comparativos | [04-prototipos.md](04-prototipos.md) e [`prototipos/`](prototipos/index.html) |
| F. Plano de convergência | [05-roadmap.md](05-roadmap.md) |
| Registro da revisão | [06-revisao.md](06-revisao.md) |
| Estados da Ocupação que a suíte já monta | [07-fixtures-da-ocupacao.md](07-fixtures-da-ocupacao.md) |
| P0, correções críticas, e a referência do piloto | [08-p0.md](08-p0.md) e [`referencia-p0/`](referencia-p0/) |
| Capturas | [`capturas/`](capturas/), 94 imagens |
| Medições e scripts | [`medicoes/`](medicoes/), com o resultado por tela em [`telas.csv`](medicoes/telas.csv) |

## Resposta curta

**A percepção do pedido se confirma, com uma correção importante.** A fundação do GPS parece sólida:
tokens num lugar só, moldura única, 94% das cores por token, e nenhum transbordo a 375 px nem campo
sem rótulo que o instrumento tenha detectado nos estados inspecionados. O que as medidas mostram é
um problema de **composição e de escala**:

- cada tela monta o próprio cabeçalho, e por isso há **71 aberturas diferentes em 89 telas**;
- não existe regra de largura por tipo de conteúdo: na tela mediana, **a metade direita não tem
  conteúdo em 73% da altura** a 1440 px, e em 86% a 1920 px. O número descreve distribuição, e não
  prova desperdício;
- a mesma peça foi redesenhada a cada tela: **63 regras de caixa, 28 de aviso, sete desenhos de
  indicador, quatro alturas para o mesmo botão**, onze tamanhos de fonte em uso corrente.

O que essas evidências têm em comum: **faltam contratos compartilhados de composição, de variantes
e de uso, e mecanismos que levem as telas a adotá-los.** A única peça que as 89 telas compartilham
é a trilha de navegação. Cada funcionalidade nova resolveu a própria tela, com o guardião exigindo
regra para toda classe citada, e o resultado são 576 classes usadas por um template só. O estudo
não demonstra uma causa única, e parcial de template é um meio de firmar o contrato, e não o
remédio inteiro: um componente também pode ser bem definido só por CSS.

**A proposta é consolidar, e não redesenhar.** Seis mudanças de fundação e uma convergência por
família de tela. Os [protótipos](04-prototipos.md) mostram que quatro arquétipos diferentes saem de
uma única folha de cerca de 260 linhas, sem estilo próprio de tela. Eles mostram que a direção é
viável; **ainda não mostram que ela opera melhor**, porque a comparação com as telas de hoje não é
equivalente.

**Sequência recomendada:** primeiro as correções críticas, como entrega própria; depois uma nova
medição de referência; depois o piloto em três telas, a confirmação de ato do Edital, a Ocupação de
vagas e a Lista de Processos Seletivos, com o estilo novo delimitado a elas e com textos,
quantidades, associações e ações preservados ([detalhe](05-roadmap.md#o-piloto)). Os neutros, a
hierarquia e os componentes entram como direção experimental. A redução tipográfica, o recolhimento
de explicações e os limites rígidos ficam para decidir depois do piloto, com a equipe.

## O que foi feito

| Fase do pedido | Como foi feita |
|---|---|
| Reconhecimento | leitura das 55 folhas, dos 266 templates e das 255 rotas; inventário gerado do resolvedor de URLs |
| Auditoria das interfaces reais | Chromium dirigido por script: 647 visitas, **131 variações de tela**, nove identidades, cinco larguras |
| Melhores referências internas | escolhidas pelas medidas e pela leitura das capturas (abaixo) |
| Diagnóstico transversal | 11 problemas sistêmicos e 12 específicos, cada um com evidência, causa, alcance, severidade e esforço |
| Proposta de design system | fundamentos, 16 componentes, 11 arquétipos, governança com contratos e guardiões candidatos |
| Demonstração | quatro protótipos HTML navegáveis e uma folha de componentes, medidos com o mesmo instrumento |
| Plano de convergência | P0 a P3, piloto com critérios de aceite, sete decisões para o usuário |

Para montar os estados, a auditoria usou um banco próprio (`ps_auditoria_visual`), com o `seed_demo`
e os 17 cenários de treinamento. Nenhum banco existente foi tocado.

## As melhores referências internas

Não são as mais recentes: são as que melhor resolvem um problema que as outras telas ainda têm.

| Referência | Por que funciona | O que vira padrão |
|---|---|---|
| **Moldura da gestão** (barra lateral, trilha, cabeçalho de contexto) | igual em 88 das 89 telas; recolhe; vira gaveta no celular; a seção atual é sempre visível | fica como está |
| **Centro de Controle do Edital** ([captura](capturas/g-centro-do-edital.jpg)) | diz onde o Edital está, de quem é a próxima ação e por quê; é a tela que melhor usa a largura (46% a 1440 px) | a composição "principal e trilho" e o "o que fazer agora" |
| **Minhas atividades** ([folha 1](capturas/folha-1-centro-processo-atividades.jpg)) | lista o trabalho sem caixa nenhuma: verbo, Edital, etapa | a lista de itens, no lugar do cartão por item |
| **Entrada da gestão** ([captura](capturas/g-entrada.jpg)) | o melhor acabamento do produto: neutros, raio, sombra e hierarquia | os tokens dela, que hoje só ela usa |
| **Corte e progressão** ([captura](capturas/g-corte.jpg)) | indicadores, tabela e o ato irreversível numa ordem que se lê de cima para baixo | o arquétipo "operação com etapas" |
| **Confirmação de ato irreversível** ([captura](capturas/g-ato-encerrar.jpg)) | separa o que impede, o que continua e o que não se desfaz | o conteúdo; a composição passa a ser centrada |
| **Convocação do candidato** ([captura](capturas/p-convocacao.jpg)) | o prazo vem antes de tudo, e a tela diz o que falta | a ordem do conteúdo da jornada do candidato |
| **Página da seleção, no portal** ([captura](capturas/p-selecao.jpg)) | vagas, cronograma e a ação de inscrever sem precisar de explicação | o arquétipo "portal público" |
| **Tabela comum** | cabeçalho em caixa alta de 12 px, número à direita com algarismo tabular | fica; ganha moldura e cartão únicos |
| **`tokens.css` e as duas larguras** | a decisão de separar medida de leitura e medida de página está certa e documentada | ganha as medidas que faltam |

**Referências externas, só de conceito.** A lista com painel de contexto ao lado (Linear, GitHub),
a página de entidade com atos no cabeçalho (Stripe), o formulário em medida fixa com ajuda lateral
(GOV.UK), a jornada em coluna centrada com uma ação por tela (GOV.UK, gov.br). Nenhuma é para copiar:
servem de prova de que a composição proposta é convenção conhecida, e não invenção.

## As doze perguntas do pedido

**1. Quais telas existem, e quais foram inspecionadas?**
135 rotas rendem tela (de 255 no resolvedor; as outras são API, fragmentos e gestos por POST). **84
foram abertas e medidas no navegador**, 7 têm captura das jornadas da suíte (acessos e unidades), e
**44 não foram vistas**: as conferências que só nascem de um POST, a administração institucional
além do que a suíte captura, e os estados que os cenários não produzem. A lista está no
[inventário](01-inventario.md), rota a rota. Boa parte das não vistas usa um template que foi visto
por outra rota.

**2. Quais têm a melhor qualidade visual?**
A entrada da gestão, o Centro de Controle, a Página do Processo, Minhas atividades, e, no portal, a
página da seleção e a convocação do candidato. Ver a tabela acima.

**3. Quais padrões devem ser preservados?**
A moldura, os tokens de cor, a tabela comum, as duas medidas de largura, o foco visível, a
confirmação de ato em página própria, a moldura rolável no celular, e os guardiões.

**4. Quais são as inconsistências mais recorrentes?**
A abertura da página (71 formas), o conteúdo encostado à esquerda (90 de 92 telas), o indicador (7
desenhos), o botão pequeno (4 alturas), o aviso (28 regras) e a escala de fonte (11 tamanhos).

**5. Quais problemas têm origem compartilhada?**
Quase todos: S1 a S11 no [relatório de evidências](02-evidencias.md#2-problemas-sistêmicos). O que
eles têm em comum é a falta de contratos compartilhados (composição, variantes, uso) e de escalas
em token.

**6. O que se corrige globalmente, e o que pede solução local?**
Global: tokens, cabeçalho, composições, botão, indicador, aviso, guardiões. Local: os 12 problemas
específicos, entre eles a Visão Geral (contraste e transbordo), a Lista de Processos, a Convocação,
o Retificar de 11.631 px e a troca de moldura da Alocação.

**7. Como organizar o uso da largura?**
Por tipo de conteúdo, e não por tela: tabela e matriz na página inteira (96rem); formulário em 46rem;
prosa em 68ch; contexto num trilho de 21rem ao lado; página de um gesto só em 44rem, centrada. Acima
de 96rem nada estica. A regra vale de 1280 px para cima e não toma monitor ultralargo como
referência: a 1280 px o trilho já cabe, e abaixo disso ele desce. São hipóteses de composição, a
confirmar no piloto por legibilidade e por localização da ação, e não por ocupação da largura.

**8. Quais componentes precisam ser padronizados?**
Dezesseis, na [proposta](03-design-system.md#4-componentes). Os cinco de maior efeito: cabeçalho de
página, botão, indicador, aviso e cartão.

**9. Que direção visual representa o GPS como SaaS moderno?**
A que ele já tem na tela de entrada, levada para dentro: neutros levemente esverdeados, raio de 10 e
6 px, sombra discreta, hierarquia clara no cabeçalho e o contexto ao lado do trabalho. O verde
institucional e a moldura ficam. Está nos [protótipos](prototipos/index.html). O texto de interface
em 14 px e o limite de um botão cheio por tela aparecem neles como hipótese, e não como parte da
direção a aprovar agora.

**10. Qual é o menor conjunto de mudanças com o maior avanço?**
Seis: tokens de escala, cabeçalho de página, três composições, `.acao` com altura única, indicador e
aviso como componentes, e contratos de componente com os guardiões que o piloto justificar
([tabela](05-roadmap.md#o-menor-conjunto-com-o-maior-avanço)). É a hipótese de maior alcance; o
piloto testa quatro delas em três telas antes de qualquer uma valer para o produto inteiro.

**11. Como demonstrar o avanço antes de alterar dezenas de telas?**
Com os protótipos, que já existem, e com o piloto: três telas, uma delas um template que serve seis
rotas. O primeiro passo do piloto é a comparação que os protótipos não fazem: o mesmo estado, com os
mesmos registros, textos, permissões e ações, antes e depois.

**12. Como impedir que a fragmentação volte?**
Com contratos escritos para cada componente, guardiões que protegem os contratos que importam e
admitem exceção justificada, e o instrumento de medida no repositório, que acusa a tela que ganhou
uma assinatura nova. Contar propriedade de CSS não garante consistência: os guardiões fecham a porta
de entrada, e a consistência se confere pelo que foi renderizado e pela revisão de tela nova. Quais
guardiões nascem é decisão para depois do piloto.

## Limites do que este estudo afirma

- **Cobertura.** 84 de 135 rotas no navegador. As 44 não vistas estão nomeadas; nenhuma conclusão
  sistêmica depende delas.
- **Experiência operacional.** As leituras de uso (§4 das evidências) são de quem percorreu as telas
  com dados fictícios. Não houve teste com a equipe de seleção nem com candidatos.
- **Acessibilidade.** O que há é triagem automática: contraste com fundo aproximado, presença de
  rótulo, tamanho de alvo, títulos e refluxo a 375 px. "Nenhum detectado" quer dizer nenhum problema
  adicional acusado pelo instrumento nos estados inspecionados, e não conformidade. Teclado, foco,
  zoom, 320 px, estados de erro e leitor de tela não foram exercitados, e entram no piloto.
- **Largura.** A ocupação da metade direita é diagnóstico auxiliar. Não é meta, e nenhum critério de
  aceite depende dela.
- **Protótipos.** Cobrem um estado de cada tela, resumem conteúdo, usam quantidades diferentes de
  registros e encurtam textos decididos em spec. A redução de altura não pode ser atribuída só ao
  design. São proposta de composição, e não de redação nem prova de ganho.
- **Estimativas.** Esforço e risco são relativos, feitos sem escrever código do produto.
- **Relação com os estudos anteriores.** A série de polish de setembro (`055` a `058`) resolveu
  medidas pontuais, tela a tela, e várias continuam valendo. Este estudo olha o que ela não podia
  ver de dentro de uma tela: a repetição entre telas.

## Para reproduzir

O servidor da auditoria é a entrada `auditoria-visual` do `.claude/launch.json` (porta 8165, banco
`ps_auditoria_visual`). Os comandos estão no [fim do documento de protótipos](04-prototipos.md#como-reproduzir).
Os scripts em `medicoes/` não gravam nada no banco: fazem um POST, o da entrada pela identidade de
demonstração, e o resto é leitura.

## O que se pede agora

Uma decisão sobre a **direção experimental** e sobre o **piloto revisto**. As decisões estão no
[fim do plano](05-roadmap.md#decisões-que-ficam-com-o-usuário), separadas entre as que cabem agora
e as que esperam o piloto. Enquanto isso, nada no produto muda.
