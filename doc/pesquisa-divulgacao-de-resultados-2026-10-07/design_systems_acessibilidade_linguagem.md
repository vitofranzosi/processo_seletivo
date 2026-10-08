# Design systems públicos, acessibilidade e linguagem simples aplicados à divulgação de resultados

Escopo: três telas — (1) página pública do Edital com os resultados divulgados; (2) página de um resultado divulgado (lista classificatória, possivelmente por lista de cota, com histórico de versões substituídas); (3) página autenticada "acompanhe sua inscrição", com a situação da pessoa e os próximos passos.

Nota de método sobre o gov.br DS: as páginas `gov.br/ds/components/...` são renderizadas no navegador (SPA) e não puderam ser lidas por fetch. O texto das diretrizes foi lido na fonte, no GitLab do próprio projeto (`gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core`, arquivos `components/<nome>/<nome>.md`, última atividade em 2026-01-12), cujos links internos apontam para `/ds/fundamentos-visuais/...`, a mesma árvore do site. O repositório fica sob o grupo "experimentos", então trate-o como a fonte das diretrizes publicadas, sem garantia de que esteja byte a byte igual à versão no ar.

---

## 1. GOV.UK Design System e Service Manual: padrões aplicáveis às três telas

### Takeaway
O GOV.UK oferece peças diretas para as três telas: **Table** (lista classificatória), **Summary list** (metadados do resultado e dados da inscrição), **Tag** (situação, sempre com texto e sem interação), **Notification banner** (aviso que não depende da tarefa da página, no máximo um por página), **Panel** (só em página de confirmação) e o padrão **Confirmation pages**, que exige um "o que acontece a seguir e quando". Para versões substituídas, o modelo de **change notes** do GOV.UK diz exatamente quando registrar uma mudança e como redigi-la.

### Cited Findings
**Table**
- Use tabelas "to let users compare information in rows and columns", e nunca para layout ("use the grid system"). — [GOV.UK Design System – Table](https://design-system.service.gov.uk/components/table/)
- A caption funciona como título e ajuda a encontrar e entender a tabela. Use `scope="col"` e `scope="row"` para separar cabeçalho de coluna e de linha. — [Table](https://design-system.service.gov.uk/components/table/)
- Números alinhados à direita: "When comparing columns of numbers, align the numbers to the right" (classes `govuk-table__header--numeric` / `govuk-table__cell--numeric`). — [Table](https://design-system.service.gov.uk/components/table/)
- Muitos dados: "try to organise it into multiple tables or multiple pages". Para tabela grande inevitável, use `govuk-table--small-text-until-tablet`. O componente não traz orientação sobre rolagem horizontal ou linhas empilhadas no celular. — [Table](https://design-system.service.gov.uk/components/table/)

**Summary list**
- Serve para pares chave–valor, como respostas ao fim de um formulário ou metadados ("Last updated: 22 June 2018"). "Do not use it for tabular data or a simple list of information or tasks". — [Summary list](https://design-system.service.gov.uk/components/summary-list/)
- Links de ação por linha precisam de texto visualmente oculto, para o leitor de tela ouvir "Change name" e não só "Change". **Summary cards** agrupam listas de itens semelhantes e permitem ação no cartão inteiro (ex.: "Withdraw"). — [Summary list](https://design-system.service.gov.uk/components/summary-list/)
- Pense bem antes de remover as bordas entre linhas: elas ajudam sobretudo quem amplia a página. — [Summary list](https://design-system.service.gov.uk/components/summary-list/)

**Tag (situação)**
- A Tag mostra o estado de algo que pode ter mais de um. Comece com poucos estados: "the more you add, the harder it is for users to remember them". — [Tag](https://design-system.service.gov.uk/components/tag/)
- Use só adjetivos, sem verbos: um verbo "might make a user think that clicking on them will do something". A Tag nunca é interativa. — [Tag](https://design-system.service.gov.uk/components/tag/)
- "Do not use colour alone to convey information", e mantenha as cores consistentes entre telas (WCAG 2.2). São nove cores. — [Tag](https://design-system.service.gov.uk/components/tag/)
- No **Task list**, "Completed" aparece em texto preto simples e "Incomplete" em tag azul. Os estados são escritos em sentence case, e o estado se liga ao nome da tarefa por `aria-describedby`. — [Task list](https://design-system.service.gov.uk/components/task-list/)

**Confirmation pages / Panel**
- A página de confirmação traz o número de referência, "details of what happens next and when", o contato do serviço, links para os próximos passos, link de feedback e um jeito de guardar o registro (ex.: PDF). — [Confirmation pages](https://design-system.service.gov.uk/patterns/confirmation-pages/)
- Links e botões dentro do painel verde não serão acessíveis. Deixe a página reabrível, porque há quem a use como recibo. Se não der, ofereça outro caminho, como acompanhar a solicitação ou falar com o suporte. — [Confirmation pages](https://design-system.service.gov.uk/patterns/confirmation-pages/)
- O Panel serve só para páginas de confirmação e de interrupção: "Never use the Panel component to highlight any other information". O texto deve ser curto. — [Panel](https://design-system.service.gov.uk/components/panel/)

**Notification banner / Inset text / Warning text**
- O Notification banner serve para informação que não se liga à tarefa imediata da página: problema no serviço, aviso específico da pessoa, resultado de uma ação anterior, prazo se aproximando. Deve ser usado "sparingly". Evite mais de um por página e nunca o coloque junto de um Error summary. — [Notification banner](https://design-system.service.gov.uk/components/notification-banner/)
- O banner neutro (azul) usa `role="region"` e o de sucesso (verde) usa `role="alert"`. Use títulos como "Success" para não depender da cor. — [Notification banner](https://design-system.service.gov.uk/components/notification-banner/)
- Se a informação diz respeito à própria tarefa da página, ponha no corpo, com Inset text ou Warning text. O Inset text deve ser usado "very sparingly" e não serve para o que é crítico, porque "some users do not notice" ele em páginas complexas. O Warning text é para conteúdo muito importante, como informação legal. — [Inset text](https://design-system.service.gov.uk/components/inset-text/); [Notification banner](https://design-system.service.gov.uk/components/notification-banner/)

**Step by step navigation**
- É um padrão exclusivo do GOV.UK, mantido pelo GDS, e não serve para serviços transacionais: nesses, use o padrão "Complete multiple tasks". Os passos ficam "in the order users need to complete them", com conectores "and"/"or". — [Step by step navigation](https://design-system.service.gov.uk/patterns/step-by-step-navigation/)

**Histórico e "Last updated": change notes**
- Mudança **menor** (erro de digitação, layout, link quebrado) é silenciosa e não muda a data de atualização. Mudança **maior** atualiza a data pública, entra no histórico do documento, dispara e-mail aos assinantes e vai para o topo das listas de "latest". — [Inside GOV.UK – when should you add change notes](https://insidegovuk.blog.gov.uk/2013/09/09/when-should-you-add-change-notes); [Content Publisher ADR 0016](https://docs.publishing.service.gov.uk/repos/content-publisher/adr/0016-publishing-times-and-change-history.html)
- Escreva nota de mudança quando acrescentar informação que muda o que a pessoa deve fazer, retirar orientação desatualizada ou alterar taxas e prazos. A nota precisa ser "very clear about what has changed and where", vir em frases completas, ser específica e começar pelo mais importante. "Do not say the page has been updated without saying what has changed" — "Guidance updated" é o exemplo ruim. — [GOV.UK – Change notes](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/change-notes/)

### Inferences
- **Tela 1 (Edital):** a lista de resultados divulgados cabe numa Table, com caption e data, ou numa lista com links descritivos. Os metadados do Edital (número, situação, última atualização) cabem num Summary list. Aviso de "resultado retificado" ou "prazo de recurso aberto até…" vai num Notification banner neutro, no máximo um por página.
- **Tela 2 (resultado):** use uma Table por lista de cota, cada uma com caption própria ("Ampla concorrência — 40 vagas"), em vez de uma tabela única com a cota como coluna. Isso segue o "organise it into multiple tables". As versões substituídas seguem o modelo de change notes: cada versão diz o que mudou e onde, e o aviso de substituição não pode se limitar a "Resultado atualizado".
- **Tela 3 (acompanhamento):** dados da inscrição em Summary list ou Summary card. A situação vai numa Tag com texto, sem verbo e sem link. Os "próximos passos e quando" seguem a regra da Confirmation page. O Panel não serve aqui: ele é só para confirmação ou interrupção.

### Gaps
- O componente Table do GOV.UK não orienta sobre tabela responsiva (rolagem × linhas empilhadas). Ver a seção 4.
- Não encontrei no GOV.UK um padrão para lista classificatória, linha de corte, lista de espera ou desempate.
- A página de change notes não trata documentos que são substituídos (versão A → versão B) como objetos distintos. O modelo dela é o de um documento só, com histórico.

---

## 2. GOV.UK: HTML em vez de PDF

### Takeaway
O GOV.UK publica em HTML por padrão: PDF é ruim no celular, não se adapta a quem muda cor ou tamanho de fonte, desatualiza fora do site e não deixa medir o uso. O eMAG brasileiro diz o mesmo — documentos "preferencialmente em HTML".

### Cited Findings
- Post de Neil Williams, então Head of GOV.UK, em 16/07/2018: o PDF dificulta a quem precisa mudar cores e tamanho de texto; "PDFs are not designed to be flexible in their layout" e exigem zoom e rolagem nos dois eixos; quem baixa o PDF continua a consultá-lo offline sem saber que ele mudou; não se mede o uso offline; fora do site, a pessoa não navega para o conteúdo relacionado; atualizar significa publicar várias versões, com "more opportunities for error". — [GDS blog – Why GOV.UK content should be published in HTML and not PDF](https://gds.blog.gov.uk/2018/07/16/why-gov-uk-content-should-be-published-in-html-and-not-pdf/)
- eMAG 3.1, recomendação 3.8: "Os documentos devem ser disponibilizados preferencialmente em HTML". Se houver PDF, ofereça alternativa em HTML ou ODF. — [eMAG 3.1](https://emag.governoeletronico.gov.br/)
- A Confirmation page do GOV.UK admite PDF como forma de guardar o registro da transação, ou seja, como cópia e não como canal principal. — [Confirmation pages](https://design-system.service.gov.uk/patterns/confirmation-pages/)

### Inferences
- A página de resultado (tela 2) deve ser HTML com a tabela de verdade. O PDF, se existir e for o ato oficial, entra como anexo descrito: formato e tamanho no texto do link. O argumento "o PDF desatualiza offline" pesa ainda mais quando há retificação, porque quem baixou a versão A não fica sabendo da B.

### Gaps
- A página atual do GOV.UK sobre anexos acessíveis (`guidance.publishing.service.gov.uk/.../prepare-attachments/`) não foi lida: o redirecionamento não foi seguido. As exigências legais britânicas de 2018 para PDF não foram verificadas aqui.

---

## 3. gov.br Design System / Padrão Digital de Governo

### Takeaway
O gov.br DS tem equivalentes diretos: **Message** (estados informativo, sucesso, alerta e erro; tipos padrão e contextual), **Table** (com regra própria de responsividade: rolagem horizontal no grid de 4 colunas), **Tag** (tipo status, com label adjetivo ou substantivo e sem verbo), **Step** (progresso numa jornada) e **Breadcrumb**, além de princípios de escrita alinhados à lei de linguagem simples. Há uma divergência a anotar: o DS admite **Tag de status sem label, só cor**, o que conflita com o WCAG 1.4.1 e com o próprio guia de escrita do DS.

### Cited Findings
**Aplicabilidade e base normativa**
- Segundo o Governo Digital, o Padrão Digital de Governo vale para "Sistemas com serviços para cidadão(ã), Portais com serviços para cidadão(ã), Painéis com acesso para cidadão(ã), Aplicativos móveis". São "padrões de interface que devem ser seguidos". Referências: Decreto 9.756/2019 (portal único gov.br), ABNT NBR 17225 (web) e ABNT NBR 17060 (móvel). — [Governo Digital – Padrão de Governo Digital (Design System)](https://www.gov.br/governodigital/pt-br/estrategias-e-governanca-digital/sisp/guia-do-gestor/guia-orientativo-de-padroes-e-fluxos-das-tecnologias-de-transformacao-digital/padrao-de-governo-digital-design-system)
- Um resumo de busca atribui a obrigatoriedade à Portaria MCOM 540/2020 e menciona a revisão da Portaria SGD/ME 39/2019. **Não verificado na fonte primária.** — [busca; documentos do Governo Digital, ex.: Nota Informativa 23755](https://www.gov.br/governodigital/pt-br/acessibilidade-e-usuario/acessibilidade-digital/padroes-web-em-governo-eletronico/Nota_Informativa_23755.pdf)

**Message (Mensagem)**
- Use para "transmitir qualquer informação ao usuário em decorrência de interações com o sistema, ou em decorrência de eventos previamente programados". Há quatro estados: Informativo (o padrão, neutro), Sucesso ("finalização de tarefa/passo ou conclusão bem sucedida"), Alerta ("advertência… evitar erros") e Erro. Cada estado tem um ícone próprio. — [gov.br DS – Message (fonte GitLab)](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/message/message.md); página pública: [gov.br/ds – Message](https://www.gov.br/ds/components/message?tab=designer)
- **Tipo Padrão** é o feedback global, da tela ou seção. **Tipo Contextual** é o feedback ligado a um componente, como a validação de campo. A mensagem global fica "entre o cabeçalho e o componente breadcrumb". A mensagem direcionada fica "próximo ao elemento ao qual a mensagem se refere". — [Message](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/message/message.md)
- O texto deve ser "curto, claro e objetivo". Evite várias Mensagens do Tipo Padrão na mesma tela: use contextuais. Se o conteúdo é muito importante, não convém oferecer o botão Fechar. — [Message](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/message/message.md)

**Table (Tabela)**
- O header é obrigatório. O nome da coluna é conciso, de preferência menor que os dados. A barra de título é opcional e tem uma linha só. — [gov.br DS – Table](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/table/table.md)
- **Responsividade:** nos grids de 12 e 8 colunas, quebra de linha nas células (o comportamento padrão do HTML). No grid de 4 colunas (celular), "é recomendável utilizar o recurso de rolagem", isto é, rolagem horizontal da tabela inteira, com barra de título e paginação fixas. "Sempre que possível, opte pela utilização dos recursos de busca e paginação" em telas pequenas. — [Table](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/table/table.md)
- Truncamento com reticências e tooltip é permitido. Para tabela extensa e sem interação, recomenda-se o hover na linha para guiar a leitura. — [Table](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/table/table.md)
- "Sempre que possível opte pela utilização de tabelas simples, pois, múltiplos níveis de cabeçalhos… podem confundir usuários que se utilizam de leitores de tela". Remete ao "Tables with irregular headers" do W3C. Evite colunas com células vazias. — [Table](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/table/table.md)
- Ordenação: um parâmetro por vez (sem ordenação, crescente ou decrescente), com ícone visível na coluna ordenada. Busca: filtra as linhas e destaca o termo. — [Table](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/table/table.md)

**Tag**
- Há cinco tipos: interação, texto, status, contagem e ícone. A Tag de texto "nunca é interativa". O label "deve ser um adjetivo ou substantivo, *não use verbos*". Use o mínimo de palavras, de preferência uma, e uma cor por tag. — [gov.br DS – Tag](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/tag/tag.md)
- A **Tag de status** "é flexível podendo ser utilizado com label ou apenas a superfície circular. Neste caso, a informação é transmitida unicamente por meio de cores". Sem label, o DS recomenda tooltip "para evitar ambiguidade". — [Tag](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/tag/tag.md). **Conflita com** o guia de escrita do próprio DS ("Qualquer classificação importante feita por meio de cores deve possuir também uma identificação textual" — [Princípios de UX Writing](https://gitlab.com/govbr-ds/govbr-ds-writing/-/blob/main/principios-writing/principios-writing.md)), com o GOV.UK ("Do not use colour alone" — [Tag](https://design-system.service.gov.uk/components/tag/)) e com o [WCAG 1.4.1 Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html).
- "Não exagere… se tudo em uma página for considerado importante, nada atrairá atenção exclusiva". Não misture tags interativas e estáticas. — [Tag](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/tag/tag.md)

**Step**
- Use para "sinalizar ao usuário uma ideia de progressão durante uma jornada: etapas concluídas, não concluídas e etapas em andamento" e o tamanho do fluxo. Não use quando as etapas não tiverem relação entre si; nesse caso, Menus ou Tabs. O indicador numérico é o mais comum. Com ícone, "recomenda-se fortemente a utilização de rótulos". — [gov.br DS – Step](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/step/step.md)

**Princípios de escrita (UX Writing) do gov.br DS**
- "Comece com o objetivo da ação". Exemplo recomendado: "Consulte seu extrato acessando as opções do perfil". — [Princípios de UX Writing](https://gitlab.com/govbr-ds/govbr-ds-writing/-/blob/main/principios-writing/principios-writing.md)
- Prefira numerais a números por extenso ("Você tem 4 novas mensagens"). Rótulos objetivos ("Aceitar", não "Ok"). Na primeira vez, nome por extenso e sigla entre parênteses. Voz ativa. Escreva para uma pessoa, no singular. Evite jargão e, se for inevitável, explique logo em seguida. Parágrafos de no máximo 4 linhas. — [Princípios de UX Writing](https://gitlab.com/govbr-ds/govbr-ds-writing/-/blob/main/principios-writing/principios-writing.md)
- Links descritivos: "O texto deve fazer sentido mesmo quando isolado do contexto da página". Evite "clique aqui", "leia mais", "saiba mais". — [Princípios de UX Writing](https://gitlab.com/govbr-ds/govbr-ds-writing/-/blob/main/principios-writing/principios-writing.md)

### Inferences
- Para a situação na tela 3, adote a Tag de status **com label**: a variante só de cor não atende ao WCAG 1.4.1.
- A regra do gov.br DS para tabela no celular é a rolagem horizontal. Ela é compatível com a exceção de tabelas do WCAG 1.4.10, desde que a rolagem fique contida na tabela (ver seção 4).
- A Message global, entre o cabeçalho e o breadcrumb, é o equivalente gov.br ao Notification banner do GOV.UK. Ambos pedem uma mensagem por página.
- O Step serve para mostrar as fases do certame na tela 3 (inscrição → homologação → resultado → recurso → convocação), sem ser navegação.

### Gaps
- A página pública do gov.br DS não pôde ser lida (SPA). Não verifiquei se o repositório "experimentos/govbr-ds-design-diretrizes-core" difere da versão publicada nem o que mudou no DS 4.0 (MGI/Serpro, 2024).
- Não li as diretrizes do Breadcrumb e do Collapse/Accordion; os arquivos existem no mesmo repositório.
- A norma que torna o DS obrigatório (Portaria MCOM 540/2020?) não foi confirmada na fonte primária.
- Não encontrei no gov.br DS orientação específica sobre comunicar status de processo ao cidadão, além dos componentes acima.

---

## 4. Acessibilidade: LBI, eMAG, NBR 17225 e WCAG 2.2

### Takeaway
A obrigação legal (LBI, art. 63) remete às "melhores práticas e diretrizes… adotadas internacionalmente". Na prática, o alvo é o WCAG 2.2 AA, que a ABNT NBR 17225:2025 adota como "conformidade regular". O eMAG 3.1 (2014) continua sendo a referência governamental para tabelas, links e HTML em vez de PDF. Para lista classificatória, o que pesa é: caption e cabeçalhos com `scope`; tabela que rola dentro de um contêiner focável sem quebrar a página a 320 px; status anunciado sem mover o foco; links com propósito claro.

### Cited Findings
- **LBI (Lei 13.146/2015), art. 63, caput:** "É obrigatória a acessibilidade nos sítios da internet mantidos por empresas com sede ou representação comercial no País ou por órgãos de governo, para uso da pessoa com deficiência, garantindo-lhe acesso às informações disponíveis, conforme as melhores práticas e diretrizes de acessibilidade adotadas internacionalmente." §1º: "Os sítios devem conter símbolo de acessibilidade em destaque." — [Câmara – Lei 13.146/2015, publicação original](https://www2.camara.leg.br/legin/fed/lei/2015/lei-13146-6-julho-2015-781174-publicacaooriginal-147468-pl.html)
- **eMAG 3.1 (abril de 2014):** 3.9 — "O título da tabela deve ser definido pelo elemento CAPTION" (e `summary` em tabela extensa). 3.10 — TH para cabeçalho, TD para dado, THEAD/TBODY/TFOOT, e associação por `id`/`headers` ou `scope`. 3.5 — "links que remetem ao mesmo destino devem ter a mesma descrição", sem "clique aqui". 3.8 — documentos "preferencialmente em HTML". 3.3 — título da página descritivo, no formato "[assunto] – [nome do sítio]". 3.4 — breadcrumb. 3.1/3.2 — idioma. — [eMAG 3.1](https://emag.governoeletronico.gov.br/)
- **ABNT NBR 17225:2025**, publicada em 11/03/2025: primeira norma brasileira de acessibilidade web, baseada no WCAG 2.2, com 146 requisitos ou recomendações. A conformidade regular equivale ao WCAG 2.2 A + AA. Foi coordenada por Ceweb/NIC.br, com 178 especialistas. — [Teletime, 11/03/2025](https://teletime.com.br/11/03/2025/abnt-lanca-norma-para-aprimorar-a-acessibilidade-de-sites/); [Mobile Time](https://www.mobiletime.com.br/noticias/11/03/2025/abnt-acessibilidade/). A página do Governo Digital também a cita como referência do Padrão Digital ([Governo Digital](https://www.gov.br/governodigital/pt-br/estrategias-e-governanca-digital/sisp/guia-do-gestor/guia-orientativo-de-padroes-e-fluxos-das-tecnologias-de-transformacao-digital/padrao-de-governo-digital-design-system)).
- **WCAG 1.4.10 Reflow (AA):** o conteúdo deve ser apresentável em 320 CSS px de largura sem rolagem em duas dimensões. Tabelas de dados são exceção, porque têm relação bidimensional entre cabeçalhos e células. A exceção não cobre o entorno: "a heading or paragraph that introduce the table, or a search field and pagination component" precisam refluir. A boa prática é pôr o conteúdo bidimensional "in its own scrollable area". — [W3C – Understanding Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)
- **WCAG 4.1.3 Status Messages (AA):** mensagem de status é "a change in content that is not a change of context" que informa resultado de ação, espera, progresso ou erros. Deve ser exposta por role ou propriedade (`role="status"`, `alert`, `log`) para que a tecnologia assistiva a anuncie "without receiving focus". Os exemplos incluem contagem de resultados de busca ("18 results returned") e envio bem-sucedido. Mudanças que movem o foco não entram no critério. — [W3C – Understanding Status Messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)
- **Critérios citados por referência** (textos normativos do W3C, não relidos nesta sessão): 1.3.1 Info and Relationships (A; estrutura de tabela programaticamente determinada) — [W3C](https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html); 1.4.1 Use of Color (A) — [W3C](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html); 2.4.4 Link Purpose (In Context) (A) — [W3C](https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-in-context.html); 2.4.9 Link Purpose (Link Only) (AAA) — [W3C](https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-link-only.html); 2.5.3 Label in Name (A; o nome acessível contém o texto visível do rótulo) — [W3C](https://www.w3.org/WAI/WCAG22/Understanding/label-in-name.html).
- **Tabela responsiva acessível (Adrian Roselli, 2017, com atualizações posteriores):** envolva a tabela em `<div role="region" aria-labelledby="<id da caption>" tabindex="0">`, para que o teclado consiga rolar e o leitor de tela anuncie a região, preservando a semântica nativa. A alternativa de "cartões empilhados" (`display:block` em `table/tr/td` + `data-label`) faz o navegador deixar de tratar o elemento como tabela, e exige devolver `role="table"/"row"/"cell"` por ARIA. — [Adrian Roselli – A Responsive Accessible Table](https://adrianroselli.com/2017/11/a-responsive-accessible-table.html). (O fetch indicou uma atualização recente da página, sobre a dispensa de role explícito em elemento focável genérico; a data exata não foi confirmada.)

### Inferences
- **Tela 2:** uma `<table>` por lista de cota, cada uma com `<caption>` ("Ampla concorrência — classificação"). A coluna de classificação é numérica e alinhada à direita. O nome da pessoa vai em `<th scope="row">`. Envolva a tabela no contêiner `role="region"` + `tabindex="0"` + `aria-labelledby` da caption. Isso concilia a rolagem horizontal do gov.br DS com o 1.4.10, e o título, o texto introdutório e os links ao redor refluem a 320 px.
- **Linha de corte e lista de espera:** transmitir "dentro das vagas / cadastro reserva" só por cor, borda ou linha visual fere o 1.4.1 e o 1.3.1. As alternativas são uma coluna de situação com texto, `<tbody>` separados com cabeçalho de grupo (`<th scope="rowgroup">`/`colgroup`) ou tabelas separadas com caption própria. Isso respeita a recomendação do gov.br DS de evitar cabeçalhos em vários níveis.
- **Tela 3:** a situação é texto visível e não só Tag colorida. Avisos que aparecem sem recarregar a página (ex.: "documento enviado") usam `role="status"`. Links como "Ver resultado" repetidos em cada linha precisam de contexto programático (2.4.4) ou de texto completo ("Ver resultado preliminar da lista de Ampla concorrência"). Se houver `aria-label`, ele deve conter o texto visível (2.5.3).
- PDF anexo: o eMAG 3.8 pede HTML preferencial e alternativa acessível. Se o PDF é o ato legal, a página HTML deve trazer o mesmo conteúdo, e não só o link.

### Gaps
- O texto integral da NBR 17225 é pago (ABNT) e não foi consultado. Não sei quais dos 146 requisitos tratam de tabelas ou PDF.
- Não confirmei se há norma recente que substitua o eMAG 3.1 no Executivo Federal. A página do Governo Digital cita a NBR 17225, sem dizer que o eMAG foi revogado.
- A página de acessibilidade em PDF (PDF/UA) do Governo Digital ou do GOV.UK não foi lida.

---

## 5. Linguagem simples: Lei 15.263/2025, gov.br e GOV.UK

### Takeaway
A **Lei nº 15.263, de 14 de novembro de 2025** (DOU de 17/11/2025, vigente desde a publicação) institui a Política Nacional de Linguagem Simples para toda a administração pública direta e indireta, de todos os Poderes e entes, e lista no art. 5º 18 técnicas obrigatórias. Entre elas: informação mais importante primeiro, frases curtas em ordem direta, termo técnico explicado, nome completo antes da sigla, listas e tabelas, e teste com o público. Isso converge com o GOV.UK (plain English, front-loading, datas e números) e com o guia de escrita do gov.br DS.

### Cited Findings
- **Lei 15.263/2025: âmbito.** "órgãos e entidades da administração pública direta e indireta" de todos os Poderes da União, dos Estados, do DF e dos Municípios. Vigência na data da publicação (art. 9º). Art. 7º vetado. — [Câmara – Lei 15.263/2025, publicação original](https://www2.camara.leg.br/legin/fed/lei/2025/lei-15263-14-novembro-2025-798293-publicacaooriginal-177011-pl.html); [Planalto](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15263.htm) (não carregou nesta sessão)
- **Objetivos (art. 2º):** garantir linguagem simples na comunicação com o cidadão; possibilitar que o cidadão "encontre, entenda e use" a informação; reduzir intermediários, custo e tempo de atendimento; transparência ativa; participação e controle social; compreensão pela população com deficiência. — [Câmara](https://www2.camara.leg.br/legin/fed/lei/2025/lei-15263-14-novembro-2025-798293-publicacaooriginal-177011-pl.html); [resumo em busca](https://www.lex.com.br/lei-no-15-263-de-14-de-novembro-de-2025/)
- **Técnicas (art. 5º, incisos I–XVIII):** I ordem direta; II frases curtas; III uma ideia por parágrafo; IV palavras comuns; V sinônimo ou explicação para termo técnico; VI evitar estrangeirismo de pouco uso; VII evitar termo pejorativo; VIII "redigir o nome completo antes das siglas"; IX listas, tabelas e gráficos para organizar; X "informações mais importantes apareçam primeiramente"; XI norma gramatical e ortográfica; XII voz ativa; XIII evitar intercalação; XIV evitar substantivo no lugar de verbo; XV eliminar redundância; XVI evitar imprecisão; XVII linguagem acessível à pessoa com deficiência (Lei 13.146/2015); XVIII "testar com o público-alvo se a mensagem está compreensível". — [Câmara – Lei 15.263/2025](https://www2.camara.leg.br/legin/fed/lei/2025/lei-15263-14-novembro-2025-798293-publicacaooriginal-177011-pl.html)
- Cabe a cada Poder e ente definir diretrizes complementares e a operacionalização. — [resumo em busca, Lex](https://www.lex.com.br/lei-no-15-263-de-14-de-novembro-de-2025/)
- **GOV.UK style guide:** "All content on GOV.UK should be written in plain English". Datas sem ordinal e com o mês por extenso ("2 June"). Intervalos com "to", não hífen. Números em algarismos, inclusive de 2 a 9. Link "front-load(ed)… active and specific", com "select" em vez de "click". Abreviação explicada na primeira ocorrência. Evitar "eg"/"ie", que o leitor de tela lê mal. — [GOV.UK A to Z style guide](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/)
- **gov.br DS:** escrever o objetivo antes da ação, usar numerais, voz ativa, singular, sigla depois do nome por extenso, explicar jargão, parágrafos de até 4 linhas, links que fazem sentido isolados. — [Princípios de UX Writing](https://gitlab.com/govbr-ds/govbr-ds-writing/-/blob/main/principios-writing/principios-writing.md)

### Inferences
- A lei transforma em obrigação para o Ifes (autarquia federal) práticas que antes eram só recomendação de estilo. O inciso X (o mais importante primeiro) e o XVIII (testar com o público) pesam mais na tela 3. Ali a primeira coisa visível deve ser a situação da pessoa e o que ela precisa fazer, com prazo. O número do Edital e o histórico vêm depois.
- Termos do domínio como "homologação", "classificação preliminar", "cadastro reserva", "ampla concorrência" e "retificação" caem no inciso V: explique-os junto do termo, por exemplo com uma frase sob a tag de situação ou um Details/Collapse.
- O inciso VIII exige escrever o nome por extenso antes de siglas como "PcD", "PPI", "AC" e "Cefor" na primeira ocorrência de cada página.

### Gaps
- Não encontrei regulamentação federal complementar da Lei 15.263/2025 (decreto ou portaria do Executivo) até a data desta pesquisa. Não verifiquei se há sanção ou prazo de adequação.
- Não consultei a página "linguagem simples" do gov.br (ex.: guia do Governo Federal ou do Laboratório de Inovação). O guia de escrita do DS cobre parte disso.

---

## 6. Rankings, linha de corte, lista de espera e desempate em tabela acessível; tabela responsiva no celular

### Takeaway
Nenhum dos dois design systems tem um padrão específico para lista classificatória. A orientação aplicável é a combinação: tabelas simples, uma por grupo (GOV.UK, gov.br DS); cabeçalhos com `scope` e caption (eMAG, WCAG 1.3.1); nenhuma situação expressa só por cor (WCAG 1.4.1); rolagem contida num contêiner focável no celular, em vez de cartões empilhados que destroem a semântica (gov.br DS, WCAG 1.4.10, Roselli).

### Cited Findings
- GOV.UK: "organise it into multiple tables or multiple pages"; números alinhados à direita. — [Table](https://design-system.service.gov.uk/components/table/)
- gov.br DS: tabela simples de preferência, porque cabeçalho em vários níveis confunde o leitor de tela; sem células vazias; rolagem horizontal no grid de 4 colunas; busca e paginação em telas pequenas. — [Table](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/table/table.md)
- WCAG 1.4.10: tabela de dados é exceção ao reflow, mas o entorno deve refluir, e a boa prática é uma área de rolagem própria. — [W3C – Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)
- Roselli: contêiner `role="region"` + `tabindex="0"` + `aria-labelledby` preserva a semântica. Os cartões empilhados via `display:block` exigem restaurar os roles por ARIA. — [Adrian Roselli](https://adrianroselli.com/2017/11/a-responsive-accessible-table.html)
- gov.br DS (Table): paginação e busca são componentes previstos. WCAG 4.1.3: a contagem de resultados após filtrar ("18 results returned") é mensagem de status. — [Table](https://gitlab.com/govbr-ds/experimentos/govbr-ds-design-diretrizes-core/-/blob/main/components/table/table.md); [W3C – Status Messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)

### Inferences
- **Linha de corte:** prefira "situação" como coluna de texto ("Classificado dentro das vagas", "Cadastro reserva", "Eliminado") ou dois `<tbody>` com linha de cabeçalho de grupo. Não use uma borda grossa ou um fundo verde e cinza como único sinal.
- **Desempate:** se a ordem depende de critério de desempate, mostre-o numa coluna ou nota ligada à tabela (caption ou parágrafo introdutório) e não só no PDF. O inciso IX da Lei 15.263 manda organizar com tabelas, e o X manda pôr o mais importante primeiro.
- **Filtro "encontre seu nome":** se existir, anuncie a contagem filtrada com `role="status"`. Paginação e busca precisam refluir a 320 px, mesmo com a tabela rolando.
- **Celular:** para uma lista com 3 a 4 colunas curtas (posição, nome, nota, situação), a quebra de linha nas células já resolve. Para mais colunas, use a rolagem contida acessível. Cartões empilhados só com os roles ARIA restaurados.

### Gaps
- Não encontrei guia oficial (GOV.UK, gov.br, W3C) sobre como apresentar ranking, linha de corte ou lista de espera. As recomendações acima são inferência a partir de regras gerais.
- Não encontrei pesquisa com usuários comparando rolagem horizontal e cartões empilhados para listas classificatórias.
- Proteção de dados (LGPD) ao publicar nome e CPF em listas está fora deste escopo e não foi pesquisada aqui.
