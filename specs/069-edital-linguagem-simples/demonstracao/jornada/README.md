# Jornada pelo navegador — 069 (T066, quickstart §10)

12/10/2026. Cada passo pelo canal do ator, no navegador embutido, com identidades de demonstração.

## Servidores e banco

| Ordem | Código | Porta | O que fez |
|---|---|---|---|
| 1 | `main` (`a79ce463`, por `git archive`, `manage.py` de dentro) | — (sem servidor) | criou e migrou `ps_069_jornada` e rodou o `seed_demo` (`--codigo PS-MAIN-2026 --numero 61 --dias-atras 10`), que publica Editais e emite e divulga atos de ordenação pelos mesmos comandos da API, com atores distintos |
| 2 | esta branch | — | migrou o mesmo banco (`editais/0023`, `publicacoes/0011`) |
| 3 | esta branch | **8069** | o runserver da jornada, com settings de scratchpad (`SESSION_COOKIE_NAME` e `CSRF_COOKIE_NAME` próprios, pela linha de comando), porque havia outros dois runservers em `localhost` (8033 e 8070, de outras sessões). O `.claude/launch.json` não foi editado |

**Duas diferenças do roteiro, ditas aqui.** (1) O ato de ordenação da redação 1 foi preparado pelo
`seed_demo` da `main`, e não clicando na interface com o runserver da `main`: o comando percorre os mesmos
comandos de aplicação com atores distintos, e montar inscrições, avaliações e consolidação pela tela
custaria horas sem provar mais. (2) Para que esse ato tivesse a frase de desempate — onde a redação 1 e a 2
diferem —, a cópia da `main` no scratchpad recebeu um critério de desempate no marco da demonstração
(`MAIOR_PONTUACAO_NA_ETAPA`); o repositório não foi tocado.

## Passos

| Passo | Ator e canal | O que se viu | Evidência |
|---|---|---|---|
| 1 | Elaboradora (`ana.elaboradora`), assistente de composição | o Edital 36/2027 (reaproveitado pelo seed, com o Cronograma vencido) teve as datas atualizadas na etapa Cronograma e o texto escrito na etapa Conteúdo, inclusive "descritos na seção Perfis de Vaga" em Requisitos gerais e "o método publicado na seção Perfis de Vaga" na seleção. A etapa mostra a numeração apresentada — "2. Quem pode se inscrever?" antes de "2.1 Público-alvo", "7.2 a 7.4 Etapas de avaliação" — e os dois avisos de remissão no topo | `01-conteudo-aviso-e-numeracao.jpg` |
| 2 | Elaboradora, prévia | a prévia (`previa-edital-36-2027.pdf`, lida pela resposta do link da tela): 4 páginas, fonte embutida, resumo, sumário, idioma, título e a marca de prévia | `02-previa.jpg` |
| 3 | Elaboradora, Revisão | os dois avisos, não impeditivos: o trecho, "foi repartida neste documento" e os três destinos com o item de cada um; "Ir para Conteúdo". As frases da Revisão são as do documento ("A ordem de classificação segue a nota final.", "Contra o resultado deste marco: …", "Passam para a Etapa “Análise documental” …") | `03-revisao-aviso-de-remissao.jpg` |
| 4 | Elaboradora submete; Homologador (`bruno.homologador`) homologa; Publicadora (`carla.publicadora`) publica, pela interface | três pessoas, três atos; os avisos repetidos na confirmação da submissão e da publicação, sem impedir | `04-publicado.jpg` |
| 5 | Candidato, portal público | "Ler o Edital completo (PDF)" responde `Content-Disposition: inline; filename="edital-36-2027.pdf"`; o arquivo tem título ("Edital nº 36/2027 — …"), autor, `pt-BR`, 17 marcadores em dois níveis, 10 links do sumário e o `mailto:` do texto, e continua sem marcação. A resposta foi lida pelo navegador; o clique abriria o diálogo de download do painel, que pede confirmação, e o arquivo guardado aqui veio da mesma URL pública | `05-portal.jpg`, `edital-36-2027.pdf` |
| 6a | Presidência (`paulo.presidente`), página do ato de ordenação publicado antes | o ato do Edital 11/2026, publicado pela `main` (redação 1): "maior pontuação na Etapa Prova objetiva — valor 8,5" — a frase que o ato publicou, sem as aspas da redação 2 (FR-1397) | `06-ato-de-ordenacao-redacao-1.jpg` |
| 6b | Presidência, proposta de ordenação do mesmo marco | a proposta lê a redação vigente: "maior pontuação na Etapa “Prova objetiva”". O contorno laranja na captura foi posto pelo roteiro de captura, para achar o trecho | `07-proposta-redacao-2.jpg` |

## O que a jornada mostrou e virou correção

Na etapa Conteúdo, com Público-alvo e Requisitos gerais vazios, a pergunta "Quem pode se inscrever?" —
que sai pelos requisitos dos Perfis — não aparecia antes deles, e a tela parecia começar no item 2. O título
da pergunta passou a vir antes do primeiro membro sempre que a seção sai (`forms._grupos_sem_principal`).

E a seção principal vazia de uma pergunta que sai pelo conteúdo gerado — "Como se inscrever?", que sai
pelo período e pelo teto — aparecia como "vazia — não sai no documento", o que era falso: a legenda passou
a dizer o número dela, como a etapa já fazia com a seção de norma acrescentada
(`forms._principais_que_saem_sem_texto`; `test_a_pergunta_que_sai_pelo_gerado_nao_se_diz_vazia`).
