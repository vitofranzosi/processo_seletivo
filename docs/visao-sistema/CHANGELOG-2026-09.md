# Revisão de 29/09/2026 da Visão do Sistema

Reauditoria contra o código em `main` `3a53b23` (specs 001–053). A doc anterior era de 20/09 (specs até 038).

## O que mudou na documentação

- **Estrutura.** Continua sendo um arquivo só (`index.html`), agora com 26 páginas roteadas por JS e
  organizadas em quatro camadas: Entender, Aprender a operar, Consultar e Estado do produto. Todas as
  âncoras antigas continuam valendo. A busca cobre a documentação inteira e há tema claro/escuro.
- **Novas páginas:**
  - Comece por aqui;
  - Antes de começar ("não confunda");
  - Como as peças se encaixam;
  - Monte um processo seletivo (tutorial em 17 passos);
  - O que eu consigo configurar?;
  - Se eu mudar isso, o que acontece?;
  - Exemplos de configuração (9 receitas);
  - Acompanhar e operar em escala;
  - Perfis de Vaga, vagas e reservas;
  - Sorteio;
  - Catálogo de capacidades (100 itens, filtrável);
  - Glossário (101 termos, com exemplo e termos relacionados).
- **Novo selo:** "Implementado, não operacionalizado", para capacidade que tem código mas não fecha a jornada.
- **Conteúdo novo, das specs 039 a 053:**
  - visão institucional e Perfil (040–042);
  - duplicar Perfil (043);
  - recorte documental por código de Modalidade (044);
  - condução confiável, com 8 espécies de sinal (045);
  - executabilidade (046);
  - situação pública do Edital (047);
  - Retificação que acrescenta (048);
  - operar por marco (049);
  - convocação como fluxo (050);
  - padrões e aplicar a todos (051);
  - tabelas do conjunto em Perfis e Classificação (052/053).
- **Passaram de lacuna a implementado:**
  - acrescentar Modalidade por Retificação;
  - teto de inscrições publicado;
  - prazo recursal na página pública;
  - fase do Evento derivada;
  - sinal de recurso no painel;
  - frase de ausência relativa ao papel.
- **Corrigido (era falso ou mudou):**
  - "nenhuma capacidade inacessível" e "nenhum dado sem uso" (o cadastro de reserva e os campos internos da regra normativa não têm consumidor);
  - 10 espécies de sinal → 8;
  - 5 recusas de publicação → 11;
  - o reingresso pendente impede as duas naturezas de resultado;
  - o prazo de recurso conta da primeira publicação do ato;
  - Processo e Edital nascem juntos;
  - o período de inscrições é designado no passo Inscrição;
  - a validação tem dois níveis efetivos, não três;
  - a convocação não aparece dentro da inscrição do candidato.
- **Lacunas revistas uma a uma:** cada uma foi classificada como resolvida, parcial, ainda válida ou
  superada, e entraram lacunas novas. Destaques:
  - a convocação e o Requerimento pedido na convocação não têm link no portal;
  - aceitar antes do Requerimento fecha o Requerimento;
  - não há capacidade de "julgar o desempate", embora as recusas mandem fazê-lo;
  - o resultado publicado não diz de qual lista é;
  - o reaproveitamento não copia o teto nem o Requerimento;
  - a Retificação devolvida não tem tela de edição.

Estado de 29/09: a spec 054 (PR #233) estava aberta e não está descrita como entregue. Foi mergeada em 30/09, e está descrita pela atualização abaixo.

# Atualização de 30/09/2026: a spec 054

A spec 054, *O Edital do sistema como ato oficial* (PR #233), foi mergeada em 30/09, logo antes da
revisão acima. Esta atualização a descreve como entregue, contra a `main` em `86bbf49`. O resto da
documentação continua sendo o de 29/09.

## Como foi conferido

- Cada afirmação foi lida no código da `main`, e não só na spec:
  - `editais/domain/secoes.py`;
  - `publicacoes/domain/autoridades.py`;
  - `publicacoes/infrastructure/pdf.py`;
  - `publicacoes/application/retificacoes.py` e `publish_edital.py`;
  - `editais/domain/validation.py`;
  - `interface/forms.py`, `interface/revisao.py` e `interface/retificacao.py`.
- Os testes da 054 rodaram contra PostgreSQL: **152 passando** em 14 arquivos (catálogo, reuso, fecho
  e normas, data por extenso, Revisão, numeração na Retificação, avisos, consolidado datado, fecho
  publicado, topologia do acervo, etapa Conteúdo, autoridades, fixture de bytes do documento e
  reaproveitamento), mais os 4 de `conteudo.test.js`.
- Não se percorreu o produto no navegador. A numeração que acompanha o que se digita na etapa
  Conteúdo só foi exercida pelo teste JavaScript, que roda sobre um DOM simulado, e por isso está
  marcada *[a validar]*.

## O que mudou na documentação

- **O catálogo de seções.** Passou de "sete seções textuais de catálogo fixo" para 22 seções: 17
  textuais e 5 geradas (FR-980). As textuais nascem vazias, não há redação padrão, e a vazia não sai
  no documento. A numeração é uma só na tela e no documento. Mudou em três lugares: o tutorial
  (passo 10), a página de configuração e a seção *As seções de conteúdo*.
- **Aviso da Revisão.** O código `section_default_text` deu lugar a `section_universal_empty`: a
  Apresentação ou as Disposições Finais vão vazias.
- **Autoridade e fecho.** O catálogo de autoridades tem só o cargo. Nome e ato de nomeação são
  opcionais, e a Publicação passa a registrar o ato de nomeação. O documento publicado ganhou o
  fecho *"Vitória (ES), 29 de setembro de 2026."*. O exemplo do glossário foi corrigido.
- **Consolidado datado.** O documento da Retificação traz, abaixo do anúncio, *"Versão consolidada.
  Publicado em …; retificado em …."*. O item correspondente saiu dos limites da Retificação.
- **Declaração do Requerimento.** É publicada na seção Da Matrícula. As duas lacunas que diziam o
  contrário (passo Inscrição e página Matrícula) viraram notas.
- **Total de vagas.** A tabela de Perfis termina em *Total* quando há mais de um Perfil e alguma
  vaga imediata.
- **Retificação.** A topologia é conferida contra a do Edital publicado, e não contra o catálogo
  vigente. A Retificação pode dar texto a uma seção publicada vazia.
- **Reaproveitamento.** Copia só o texto que alguém escreveu, e não a redação padrão do acervo
  anterior.
- **Estado do produto.**
  - 55 pastas de especificação e 85 migrations.
  - `AX-3` passou de *Previsto* a *Parcial*.
  - Seções do documento: de *Ainda válidas* a *Parcialmente resolvidas*.
  - Entraram quatro linhas em *Fechados desde 20/09*.
  - A SC-001 da 008 aparece como emendada (FR-998).
  - A DP-20 aparece como executada, exceto a assinatura e o nome.
- **Catálogo de capacidades.** Ganhou duas linhas: o fecho do ato e o consolidado datado. São 102.
- **Lacunas.** Saíram as linhas "Documento consolidado da Retificação" e "Requerimento de
  Matrícula" de *O que a tela diz e não é o vigente*.
- **Âncoras.** Todas as 370 foram preservadas, e nenhuma é nova.

## O que continua em aberto

- **Registrado pela verificação da 054, e decisão do usuário:**
  - a seção textual continua sem tabela, subitem numerado ou negrito;
  - o subitem transcrito carrega o número do original, que deixa de casar com o da seção quando o
    Cronograma entra no corpo;
  - o cargo do catálogo ("Diretora-Geral…") diverge do cargo do 28/2026 ("Diretora…").
- **Com o Cefor:** como o ato é assinado e o nome de quem assina.

