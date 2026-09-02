# Fase 1 — Como demonstrar e validar

**Feature**: 012 — Mesa de Avaliação | **Data**: 2026-09-01

A condição de merge de cada entrega é o **percurso navegado**, não a contagem de testes (princípio
VI da Constituição). Como na 011, metade do que esta feature promete só se demonstra **pela
recusa** — e aqui há uma recusa nova, que é a mais importante de todas: a que impede que retirar uma
atribuição vire um modo de escolher quais notas contam.

São três janelas, porque são três papéis distintos no percurso — quem preside, quem avalia e quem
não deveria alcançar nada — e eles não compartilham sessão.

---

## Pré-requisitos

**PostgreSQL local precisa de `LC_ALL`, e a role padrão da máquina não existe no cluster** —
sobrescreva `DB_USER`.

**`TEST_DB_ENGINE=postgresql` é obrigatório**, e nesta feature o custo de esquecer é maior que na
011. Sem ela a suíte cai para SQLite **sem avisar**, e três coisas deixam de ser verificadas: o
índice único parcial que garante uma conclusão por pessoa, inscrição e Etapa (FR-074); a trigger
append-only da conclusão preservada (FR-094); e o bloqueio do Processo herdado de
`comando_de_comissao`, que é inócuo em SQLite.

**Um banco de teste por worktree**, senão duas suítes em paralelo se destroem:

```bash
cd backend && TEST_DB_ENGINE=postgresql LC_ALL=en_US.UTF-8 DB_USER="$(whoami)" DB_NAME=ps012 uv run pytest -q
```

**A interface administrativa exige o seletor de identidade ligado**; sem a variável, `/gestao/`
devolve 503. Ele continua recusado em produção — e nesta feature isso deixa de ser detalhe de
ambiente e vira o gate de FR-058: é aqui que dado pessoal de candidato real passaria a ser aberto a
membro de comissão.

```bash
cd backend && INTERFACE_SELETOR_IDENTIDADE=true DB_USER="$(whoami)" uv run python manage.py runserver 8012
```

**Dados**: um Edital publicado com Etapa declarando duas avaliações e pontuação máxima, comissão com
presidente e três membros alocados, e ao menos seis inscrições submetidas.

---

## Entrega 1 — O incremento normativo

**O que se vê**: quem elabora declara, na Etapa, quantas avaliações cada inscrição recebe e qual a
pontuação máxima; o Edital publicado carrega as duas, e o PDF as imprime.

1. Elaborar uma Etapa com `2` avaliações e máxima `100`. Publicar.
2. Abrir o documento materializado: as duas linhas aparecem junto de nota mínima e caráter.
3. Abrir um Edital publicado **antes** do incremento: a Etapa não tem as duas, e a tela diz "uma
   avaliação" e "limite não declarado" — e não em branco (FR-009, FR-066).
4. **A demonstração que a spec mandou fazer**: retificar esse Edital antigo. A Retificação é
   composta, homologada e publicada normalmente; a Versão Consolidada nova nasce na versão vigente;
   e a Publicação original continua com o mesmo `content_hash` de antes (FR-098, T-001).

**Prova por teste**: `test_forma_publicada.py` conferindo a transcrição contra o `openapi.yaml`; um
teste de integração retificando conteúdo de versão anterior; um teste que afirma que nenhuma linha
de `Publicacao` ou `VersaoConsolidada` foi atualizada durante o percurso.

---

## Entrega 2 — Distribuir

**O que se vê**: a presidência distribui quatrocentas inscrições em poucas submissões, e a tela diz
o que falta.

1. Abrir a distribuição da Etapa: carga por pessoa, inscrições sem avaliador suficiente, total.
2. Selecionar duzentas inscrições e um avaliador. **Uma** submissão.
3. Repetir para o segundo avaliador. A contagem de déficit cai à medida que o previsto é atingido.
4. Tentar atribuir uma terceira pessoa a uma inscrição que já tem duas: **recusado**, nomeando o
   número que o Edital publicou (FR-065).
5. Reenviar o mesmo lote — F5, duplo clique, timeout: nada é criado e nenhum evento novo é gravado
   (FR-084).
6. Distribuir um conjunto em que três linhas estão impedidas: o lote conclui, e o resultado diz
   "197 atribuídas, 3 recusadas", com o motivo de cada uma (FR-085, FR-097).

---

## Entrega 3 — A Mesa, e as recusas que a definem

**O que se vê**: cada avaliador vê o que lhe cabe, e só.

1. Entrar como avaliador com atribuições: a Mesa lista as inscrições, com contagem e filtro de
   pendentes e concluídas.
2. Entrar como quem está **alocado à Etapa e não recebeu nada**: a Mesa abre e está **vazia**, com
   texto que explica; não é 404 (FR-023).
3. Esse mesmo ator abre a URL de uma inscrição atribuída a outro: **404** (FR-045).
4. Trocar o UUID da inscrição na URL de quem tem atribuição, para uma que não é dele: **404**.
5. **Remover a alocação** desse avaliador na Etapa. Recarregar: a Mesa some. Devolver a alocação: as
   mesmas atribuições voltam (FR-046, EC-003).
6. Conferir no banco que a remoção e a devolução **não escreveram em Atribuição nenhuma** (FR-069).

---

## Entrega 4 — A inscrição e o documento

1. Abrir uma inscrição atribuída: identificação mínima e a lista de documentos, cada um sob o
   Documento Exigido que atende.
2. Abrir um documento: abre inline, conferido antes do primeiro byte.
3. Conferir a trilha: há um `CONSULTAR_DOCUMENTO` com ator, inscrição e requisito (FR-027).
4. Corromper um arquivo no armazenamento e abri-lo: recusa registrada, e não aviso silencioso
   (FR-029, EC-008).
5. Procurar, na tela e no HTML, qualquer caminho para baixar tudo: não existe (FR-028).

---

## Entrega 5 — Avaliar

1. Gravar pontuação e parecer sem concluir. Sair e voltar: o rascunho está lá (FR-031).
2. Pontuação acima da máxima publicada: recusada, nomeando o limite (FR-033).
3. Pontuação **abaixo da mínima** numa Etapa eliminatória: aceita, e o parecer passa a ser
   obrigatório (FR-033, FR-034).
4. Concluir. A tela deixa de aceitar alteração pelo avaliador (FR-035).
5. Abrir a mesma avaliação em duas abas, gravar nas duas: a segunda é recusada por revisão obsoleta
   (FR-081, EC-016).
6. Publicar uma Retificação que muda a máxima enquanto um rascunho está aberto. Concluir: o aviso
   aparece **antes**, o avaliador reconhece, e a versão gravada é a mesma contra a qual a validação
   correu (FR-073, FR-096, EC-014).
7. Concluir fora do período previsto da Etapa: aviso perceptível, conclusão aceita, instante real
   gravado (FR-077, FR-095).
8. Conferir que nada na tela diz média, situação, apto ou inapto (FR-037, SC-013).

---

## Entrega 6 — Impedimento, reabertura e a recusa central

**Esta é a demonstração que fecha a feature.** Sem ela, a 012 entrega um mecanismo de seleção de
notas com aparência de organização do trabalho.

1. Registrar impedimento sobre um par que tem Atribuição **ativa e sem conclusão**: a confirmação
   diz quantas serão inativadas; o acesso do avaliador some na hora (FR-041).
2. Registrar impedimento sobre quem **já concluiu**: a conclusão permanece, e aparece na
   organização do trabalho marcada como inelegível, com o ato, o autor e o motivo (FR-079, FR-093,
   EC-012).
3. Conferir que a vaga foi liberada: a inscrição volta a aparecer como carente, e uma substituta
   pode ser distribuída (FR-090, EC-020).
4. Conferir que a avaliação invalidada continua **consultável** pela presidência e pela auditoria —
   conteúdo, instante, versão e o ato que a tirou do conjunto (FR-091). A consulta é a página de
   **conclusões preservadas**, e não a trilha: a trilha guarda que o ato aconteceu e nunca a
   pontuação nem o parecer (FR-054).
   Nas duas páginas — a trilha e as conclusões — conferir a porta: **maria**, que preside sem papel
   de auditoria, entra; uma identidade com **só** o papel Auditor entra; **joao**, que avalia nesta
   Etapa, recebe 404.
5. Entre a confirmação do impedimento e o clique em "Registrar mesmo assim", concluir a avaliação
   numa segunda janela. O ato é **recusado**, dizendo que o alcance mudou, e a confirmação é
   refeita sobre o que existe agora (FR-041, FR-106).
6. **Tentar retirar, pela via comum de redistribuição, a Atribuição de quem já concluiu**: recusado,
   nomeando os atos que teriam esse efeito e o que cada um exige (FR-092, EC-018).
7. Reabrir uma avaliação concluída, com motivo. O avaliador volta a poder gravar.
8. Concluir de novo, e então perguntar o que ele havia concluído antes da reabertura: a resposta
   existe, com pontuação, parecer, versão e instante (FR-094, SC-028).
9. Tentar concluir numa aba que ficou aberta desde antes da reabertura: recusada, dizendo que a
   avaliação foi reaberta (FR-082).

---

## Escala, medida e não afirmada

| medida | limite |
|---|---|
| Mesa com 500 atribuições | 3 consultas, nenhuma por linha (FR-024, SC-015) |
| distribuir 1000 inscrições | contagem de submissões na casa das dezenas, nunca das centenas (FR-047, SC-014) |
| retirar pessoa de uma Etapa com 500 atribuições | 1 escrita (FR-069) |
| organização do trabalho de um Edital com 1000 inscrições | contagens por agregação, não por laço |

Os quatro vão para `tests/performance/`, contando consultas — como a 011 fez com a leitura da
comissão.

---

## O que **não** é demonstrável nesta feature, e por quê

- **Resultado, média, quórum e situação**: são da 013, e a ausência deles é critério de aceite
  (SC-013).
- **Distribuição automática**: FR-017.
- **Retirada de inscrição**: não existe estado de retirada no sistema (D-006 da spec, EC-006).
- **Identidade institucional confiável**: continua sendo o gate herdado da 011, e esta é a feature
  em que ele deixa de ser teórico (FR-058).

---

## Gates de implantação, conferidos e registrados

Não são demonstrações: são condições que precisam estar **respondidas por escrito** antes de a 012
subir com dado real, e a conferência final registra o estado de cada uma.

| gate | origem | o que registrar |
|---|---|---|
| identidade institucional confiável | 011, FR-058 | se o mecanismo de produção existe, ou a pendência declarada |
| retenção e descarte do acervo | FR-057 | qual é o prazo, quem descarta e por qual ato — a 012 torna a pergunta urgente e não a responde |

**FR-057 não tem tarefa de implementação de propósito**: resolvê-lo é decisão institucional sobre
dado pessoal, não código desta feature. O que a 012 deve entregar é a pergunta registrada e visível,
e não uma resposta inventada pela engenharia.

### Estado em 2026-09-02, ao fim da implementação

| gate | estado | o que falta |
|---|---|---|
| identidade institucional confiável (FR-058) | **pendente, e é bloqueante para produção** | O seletor de identidade continua sendo o mecanismo disponível, e com ele **qualquer pessoa se declara presidente ou avaliador**. Até a 011 isso expunha organização do trabalho; a partir da 012 exporia documento e dado pessoal de candidato. `INTERFACE_SELETOR_IDENTIDADE` continua recusado em produção, e é essa recusa que segura a feature. |
| retenção e descarte do acervo (FR-057) | **não respondido** | Não há prazo declarado, ato de descarte nem responsável. A 012 não o resolve e o torna mais urgente: ela é a primeira feature em que membro de comissão lê documento comprobatório em volume, e documento de candidato inclui autodeclaração étnico-racial. A resposta é institucional. |

Nenhum dos dois é defeito de código, e nenhum dos dois se resolve escrevendo mais código. Ficam
registrados aqui porque um gate que só existe na cabeça de quem implementou não é um gate.

---

## Execução registrada — 2026-09-02

O percurso das seis entregas foi executado contra o servidor de demonstração, com dados semeados
por `seed_demo` e uma comissão de quatro pessoas — Maria preside, João e Ana avaliam, Bruno fica
alocado sem receber nada. **34 verificações, nenhuma divergência.**

Três observações do percurso, todas sobre o **roteiro** e não sobre o sistema:

1. **O Edital semeado não declara as duas propriedades**, e por isso ele exercita justamente a
   leitura da ausência: a tela diz "1 avaliação por inscrição" e "o Edital não declara pontuação
   máxima", que é o que FR-009 e FR-066 mandam. Para exercitar a dupla avaliação é preciso um
   Edital que a declare.
2. **A versão a reconhecer na conclusão vem do formulário, e não da última materializada.** O seed
   cria uma Retificação com vigência futura, então a versão mais recente **não** é a vigente — e
   uma tentativa de concluir declarando aquela é corretamente recusada com "o Edital foi retificado
   enquanto você avaliava". Quem percorre o roteiro deve usar o que a página oferece, como uma
   pessoa faria.
3. **O protocolo é único no sistema inteiro**, então semear um segundo Edital de demonstração exige
   protocolos com prefixo próprio.


---

## Segunda execução registrada — 2026-09-02, depois da revisão

A revisão de `origin/main...f5bcaba` encontrou cinco defeitos funcionais que a primeira execução
não alcançou, e as correções mudaram três telas: a porta da trilha, o registro da abertura de
documento e a nova página de conclusões preservadas. **A execução acima é anterior a elas**, e por
isso os pontos afetados foram percorridos de novo, pelo mesmo canal e contra o mesmo banco de
desenvolvimento: **22 verificações, nenhuma divergência.**

Duas observações novas, e as duas são sobre o roteiro:

4. **O `seed_demo` não envia documento nenhum.** A Entrega 4 não é percorrível sobre os dados
   semeados sem antes anexar um — e a 009 recusa anexar a inscrição **já enviada**, de propósito.
   A inscrição precisa nascer com o documento e ser promovida depois, que é o percurso do candidato.
5. **Anexar exige `ARQUIVOS_CANDIDATOS_RAIZ`** apontando para um diretório absoluto fora da árvore
   do código. Sem ela o sistema recusa receber documento, o que é o comportamento correto — e é a
   segunda variável de ambiente que o roteiro precisa declarar, ao lado do seletor de identidade.
