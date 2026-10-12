# Verificação — 070 · A fonte de consulta do Edital vigente

*12/10/2026, na worktree `audit-edital-assistant-a8f915`, sobre a `main` em `a79ce463`.*

## 1. Pelo canal do ator (`SC-538`, princípio VI)

**Ambiente.** O roteiro B de [quickstart.md](quickstart.md):

- banco próprio `ps_070_demo`, preparado com `make preparar` e povoado com `make seed`;
- servidor `duvidas-070` do `.claude/launch.json`, porta 8070, com o seletor de identidade;
- identidade `gabriel.gestor`, papel Gestor, escopo `cefor`, pela tela de identificação.

**Edital:** 01/2026 do `seed_demo`. Ele tem a publicação original e duas Retificações; a segunda tem
vigência futura de 15 dias. Nada foi feito por banco ou shell, só pela tela.

| Passo | O que se fez | O que se viu |
|---|---|---|
| 1 | Página do Edital → "Ver as respostas do assistente de dúvidas (validação interna)" | A tela abre com o aviso de validação interna, o instante de referência, os pontos para revisão e as onze perguntas que se aplicam. A `P-09` não aparece: o 01/2026 não tem sorteio |
| 2 | Pontos para revisão | "Há Retificação publicada com vigência a partir de 27/10/2026, às 14h36." Nenhum canal divergente: o 01/2026 não tem seções, e o canal é o institucional |
| 3 | `P-01` no presente | "As inscrições estão abertas até 01/11/2026, às 14h36." O aviso diz que a Retificação já publicada prorroga para 11/11/2026 a partir de 27/10/2026. A descrição literal traz "isenção de taxa até o 5º dia". O início leva à **publicação original** |
| 4 | `P-01` em 28/10/2026, com a versão da resposta anterior | O aviso "Este Edital mudou desde a resposta anterior" vem **antes** da versão. A resposta diz 11/11/2026; o término leva ao documento **da Retificação** vigente desde 27/10/2026, e o início continua na original |
| 5 | `P-03` do Professor de Informática | "3 vagas imediatas: 2 de ampla concorrência, 1 na modalidade PPP." O total e a ampla concorrência levam à primeira Retificação; a linha PPP, à original. Cadastro de reserva limitado a 6 |
| 6 | `P-08` do Técnico de Laboratório | "Depende da leitura do Edital", com o Evento "Resultado final e abertura do prazo recursal" inteiro. A explicação não diz que não cabe recurso e encaminha ao atendimento institucional. *Depois da validação de 12/10 (§6): sem canal configurado na demonstração, diz que nem o Edital nem a implantação informam um canal* |
| 7 | Os links dos cartões | Os dois documentos de ato e o cronograma da página pública respondem 200, os documentos como `application/pdf`. Nenhum link se chama "Edital completo" |
| 8 | 375 px de largura | `scrollWidth` = `clientWidth` = 375, sem elemento além da borda. Captura feita na sessão |
| 9 | 1280 × 900 | Resposta da `P-08` legível, com os três rótulos de natureza em palavras. Captura feita na sessão |

Os logs do servidor não registraram erro durante o roteiro.

**Achado na própria verificação, e corrigido.** No passo 3, o início das inscrições levava, de
início, ao documento da **primeira Retificação**, e não ao da original. A causa: a versão
materializada por uma Retificação guarda em `applied_publications` só as Retificações, e não a
publicação original. Lida sem ela, a regra "sem registro de proveniência, vale a original" caía na
primeira Retificação.

- **Correção:** `duvidas/application/consultar.py` passa a incluir sempre a original, na mesma
  consulta.
- **Regressão:** `tests/integration/duvidas/test_documento_de_origem_incompleto.py::test_valor_que_nunca_mudou_leva_a_publicacao_original`.
- **Por que os testes não pegaram antes:** os testes unitários usavam o ajudante do corpus, que
  incluía a original por construção.

## 2. Tempo de resposta (`SC-537`)

Medição feita em 12/10/2026, com um teste temporário, apagado depois de rodar.

- **Edital:** o 92/2026, o maior do corpus, com 18 Perfis, publicado pelo fluxo real
  (`publicar_do_corpus`).
- **Amostra:** 20 consultas a cada pergunta oferecida, 220 no total.
- **Ambiente:** PostgreSQL local, Apple M5 Pro, 24 GB.

| Medida | Valor |
|---|---|
| p50 | 4,1 ms |
| **p95** | **5,9 ms** (meta: 2 s) |
| máximo | 39,6 ms |
| pior pergunta, no p95 | `P-11`, 6,2 ms |

O número de consultas ao banco por resposta é preso por teste (`R-019`). São 5 sem versão futura e
6 com ela, mais uma para a versão anterior informada e outra para o desfecho.

## 2a. A suíte (T049) e a conferência antes de integrar (T051)

`make lint check test-pg DB_NAME=ps_070`, em 12/10/2026, sem edição durante a execução:

| Medida | Valor |
|---|---|
| `ruff check` e `ruff format --check` | limpos, 1427 arquivos |
| `manage.py check` e `makemigrations --check` | sem problema, nenhuma migration |
| passando | **10575** (eram 10408 na medição de 09/10); **10600** depois da revisão de código (§5); **10606** depois da validação (§6); **10608** depois da decisão 011 |
| pulados | **11**, os mesmos onze nas quatro; os testes da `070` não pulam nada |
| falhas e erros | nenhum nas quatro |
| tempo | 1256s; 1213s; 1244s; 1128s |

O `makemigrations --check` avisa que o banco `ps_070` não existe — é o banco de desenvolvimento,
que esta worktree não criou; a suíte usa o de teste. Não é do diff.

Conferência antes de integrar, no mesmo dia:

- nenhum PR aberto; a `main` continua em `a79ce463`;
- teto nas worktrees: a `069` chega a 1400 nos requisitos funcionais, 524 nos critérios de
  sucesso e 193 nos de experiência — abaixo do início da faixa da `070` (1410, 530 e 200). Nada a
  renumerar. Os identificadores da `069` vão por extenso porque não existem nesta branch, e o
  guardião de citações os recusaria;
- a `069` não foi integrada; a revisão de vocabulário da *Compatibilidade com a 069* fica para
  quando uma das duas entrar depois da outra;
- nenhum arquivo alterado nas duas worktrees ao mesmo tempo, `test_gramatica_das_portas.py`
  inclusive. Não houve linha nova no inventário da `033`.

## 3. A revisão com o setor de seleção (T046) — pendente, do usuário

A revisão é do setor, e não do agente. O que levar a ela:

1. **A tabela de pertinência** (`D-007`): para cada pergunta, as seções que tratam do assunto e as
   que acompanham. Errar para menos omitiria ressalva.
2. **As listas de termos do canal** (`R-011`):
   - termos de dúvida: `duvida`, `esclarec`, `atendimento`, `contato`, "informações sobre este
     edital";
   - termos de exclusividade: `exclusivamente`, `somente`, `unicamente`, `apenas`.

   A conferir contra a redação dos Editais reais do Cefor.
3. **As formas da explicação** (contracts/resposta.md §4) e os rótulos de valores
   (`duvidas/domain/rotulos.py`): linguagem simples, sem jargão da gestão.
4. **A detecção do canal** (`duvidas/domain/canal.py`). A revisão de código de 12/10 mostrou casos
   em que a heurística erra, todos dependentes das listas do item 2:
   - "atendimento" casa também o "atendimento especial" da pessoa com deficiência: com o canal de
     dúvidas no mesmo Edital, a resposta sai "Fontes divergentes";
   - e-mail e telefone do mesmo setor, no mesmo parágrafo, contam como dois canais;
   - `https://ifes.edu.br` e `www.ifes.edu.br` não se reconhecem como o mesmo;
   - o telefone não reconhece `3357.7500`, `3357 7500` nem `0800 723 1234`, e reconhece qualquer
     número solto de oito dígitos num parágrafo que fale de dúvida;
   - "Dúvidas:" numa linha e o endereço na seguinte não se juntam.

   Ajustar as listas e a regra é emenda de `R-011`, e não correção silenciosa.
5. **O catálogo.** O guardião de cobertura mostrou campos publicados que nenhuma pergunta mostra
   (`duvidas/domain/cobertura.py`, `SEM_PERGUNTA`):
   - as atribuições do Perfil;
   - a descrição do Edital;
   - as regras de convocação da modalidade.

   Os rótulos da Etapa decisória, que estavam nesta lista, passaram à `P-07` na validação (§6).

   Decidir se entram numa pergunta, nova ou existente.

**Mudança em `D-007` ou em requisito é emenda da spec, e não ajuste silencioso.**

## 4. Emendas e correções feitas durante a implementação

| O quê | Onde | Por quê |
|---|---|---|
| US3, cenário 1, dividido em 1 e 1a | spec.md | O `TEC-LAB` do 01/2026 tem um Evento que fala de recurso; a resposta certa é "Depende da leitura" (`R-014`) |
| Orçamento de consultas: de seis para no máximo oito | research.md `R-019`; plan.md; tasks.md | A medição mostrou 5 a 6, mais as duas condicionais; a consulta aos documentos não era necessária |
| Recusa fora do escopo pelo `not_found` do domínio | contracts/tela.md; tasks.md T013 | O padrão das telas dos avisos. Não houve linha nova no inventário da `033` |
| Descrição, carga horária e remuneração na `P-03` | respostas.py; contracts/resposta.md | O guardião de cobertura mostrou que nenhuma pergunta as mostrava |
| A publicação original sempre entre os atos | consultar.py | Achado no passo 3 acima |

## 5. Revisão de código (12/10/2026)

Três revisões independentes, por área: a consulta (`consultar.py`, `origem.py`, `revisao.py`,
`canal.py`, `anexos.py`), as respostas (`respostas.py`) e o catálogo, os testes e os documentos.
Cada defeito confirmado foi reproduzido antes de corrigido e ganhou um caso que o prende, quase todos
em `tests/unit/duvidas/test_casos_da_revisao.py`.

| Defeito | Correção |
|---|---|
| Consulta a instante passado mostrava como "futura já publicada" a Retificação publicada depois dele | `materialized_at <= instante` nas futuras (`R-003`) |
| Valor de Perfil ou Modalidade acrescentado por Retificação levava ao documento da publicação original, que não o contém | `origem.acrescimos`: o primeiro ato cujo documento contém a entidade (`R-004`) |
| Desfecho sem data valia em qualquer instante | Só no presente, como `R-006` decide |
| O valor futuro saía cru ("UNLIMITED", identidades, "sim/não"), deslocava itens de lista e não via acréscimos — "não altera o que esta resposta cita" com um Evento novo | O mesmo construtor sobre o conteúdo futuro, cartão a cartão (`R-003`); uma linha por versão futura |
| A Retificação futura podia ser nomeada com a data da publicação original | O ato da mudança vem dos atos que a versão futura acrescenta |
| Na `P-05`, o aviso `REDACAO_ALCANCA_MAIS` nunca saía: o veredito divergente é um "não se aplica" e era pulado | O documento divergente tem cartão e aviso |
| A `P-05` dizia "o Edital exige" com documentos facultativos | "pede", e a obrigatoriedade fica no cartão |
| A `P-02` dizia "Em andamento" com o Edital cancelado, e "já passaram" para Eventos cancelados | O desfecho prevalece, como na `P-01`; "Nenhuma data deste cronograma está por vir" |
| Vagas imediatas ausentes viravam "não tem vagas"; caráter de Etapa ausente virava "não" | "não declara" e "não declarado" (`FR-1416`, `FR-1422`) |
| A `P-09` de um Perfil sem sorteio, num Edital em que outro sorteia, dizia "não classifica por sorteio" | A oferta por Perfil da `FR-1417` é conferida no `resolver` |
| A `P-07` de Perfil sem marco era "Respondida" sem cartão | As Etapas do Edital, ditas como não ligadas a marco do Perfil |
| A versão anterior mais nova que a atual dava o aviso de mudança sem ato nenhum | `MudancaDeVersao` nos dois sentidos |
| `?em=9999-12-31T23:59` derrubava a tela com 500 | O instante que transborda em UTC é recusado como os outros |
| Data inexistente levantava `ValueError`; instante sem zona usava a da máquina | Dito como está escrito; sem zona, a do Edital |
| Ordem nula de critério ou Etapa levantava `TypeError` | `order or 0` |
| A citação de anexo casava "anexo civil" e o anexo de outra norma, e não via "Anexos III e IV" nem "Anexo 04" | Romano válido, exclusão de "do Decreto…", plural e número normalizado |

**Testes que não podiam falhar**, reescritos:

- o orçamento de consultas aceitava folga de até duas; agora prende os números exatos e mede as
  condicionais;
- a localização "sem número impresso" olhava só os três primeiros caracteres;
- o teste do desfecho do Processo testava o do Edital — o do Processo sozinho não se alcança pelo
  fluxo real, e o caso passou para a camada de conteúdo;
- a `FR-1428` citava um teste que não conferia a reserva nem a reversão.

**Ficou registrado, e não corrigido:** a heurística do canal (item 4 da seção 3), que é das listas
de `R-011`.

## 6. Validação de correção e referências (12/10/2026)

Feita pelo agente, a pedido do usuário, no Edital 01/2026 do banco de demonstração: cada valor das
respostas conferido contra o PDF do ato a que o cartão leva (os três atos, por `pdftotext`), em todas
as perguntas e nos dois Perfis. **Não substitui a T046**: a linguagem para o candidato, a pertinência
e as decisões de regra continuam com o setor.

**Correto.** Todos os valores e textos conferem com o documento. Cada valor leva ao ato que o fixou:
as vagas do DOC-INFO à 1ª Retificação (2 → 3, ampla 1 → 2), a vaga PPP e a reserva à original. Em
28/10, o término leva à 2ª Retificação, cujo documento contém o 11/11 e as vagas da 1ª. O anexo: a
autodeclaração do 01/2026 leva ao Anexo I pelo vínculo; a `P-07` do 92/2026 avisa o Anexo IV, que a
consulta não lê (pela camada de conteúdo, porque o 92/2026 não está no banco de demonstração).

| Observação | Tipo | O que se fez |
|---|---|---|
| Sem canal nenhum, as respostas mandavam "procurar o atendimento institucional", que a `P-11` dizia não existir | Erro factual (`FR-1441`) | "Nem o Edital nem a implantação informam um canal para dúvidas." |
| O Evento era nomeado pelo tipo ("Prova objetiva"), que o cronograma do PDF não imprime | Redação | Pela descrição, como o documento |
| A Etapa decisória dizia "favorável ou desfavorável"; o Edital diz "Deferido ou Indeferido" | Redação | Os rótulos do Edital, em cartão de texto |
| Na `P-02`, a descrição do Evento terminada em ponto dava "“…dia.”." | Redação | Sem o ponto final dentro da frase |
| `P-12`: "as Retificações publicadas em X" para uma só, contando o próprio ato | Redação | Singular e plural, e "esta" à parte |
| "retificada em 12/10/2026 e em 12/10/2026" | Redação | Data e hora na linha da versão |
| Perfil só de reserva: "não tem vagas imediatas" lia-se como "não há seleção" | Redação | "…: a seleção forma cadastro de reserva." |
| A `P-07` do 92/2026 é "Respondida" com os critérios de pontuação no Anexo IV, que a consulta não lê | **Regra** | Decidido pelo usuário: "Respondida" exige cobertura do enunciado; a resposta passa a "Depende da leitura", nomeia o que remete ao anexo e o anexo (`D-011`) |

## 7. Conferência documental para a T046 (12/10/2026)

Feita pelo agente, a pedido do usuário, com os Editais reais do Cefor disponíveis localmente
(57, 58, 59, 77 e 78/2026; 14, 28, 35, 69, 76, 89 e 90/2026; 140, 146 e 173/2025 — quinze com texto
extraível; o 62 e o 73/2026 são imagem). **A revisão institucional não está concluída**: a T046
continua aberta até a manifestação do setor. O que segue separa o verificado do que só o setor
decide.

### 7.1 Canal de dúvidas e restrições expressas

**Verificado** — a detecção da `070` (`canal.py`) rodada sobre o texto de cada Edital, com um
parágrafo por item numerado, e comparada à leitura da cláusula:

| Forma da cláusula | Editais | O que a `070` faz |
|---|---|---|
| "Quaisquer **dúvidas** … deverão ser esclarecidas **exclusivamente** pelo e-mail X **ou** pelo whatsapp Y" | 28, 35, 57, 76 | Acha a cláusula. Conta e-mail e whatsapp como dois canais: "Fontes divergentes", embora a cláusula ofereça os dois |
| "**Contatos** e informações adicionais … serão obtidas, **exclusivamente**, pelo e-mail X" | 14, 89, 90, 140, 146, 173 | Acha a cláusula |
| "**Informações** a respeito das inscrições e seleção serão fornecidas **exclusivamente** por e-mail, no endereço X" | 58, 59, 77, 78 | **Não acha.** Toma no lugar o e-mail da coordenação do curso, de um parágrafo sobre certificado ou acesso ao ambiente — **canal errado** |
| Sem cláusula de canal no texto | 69 | Cai no institucional, como deve |

Além disso, em **9** dos 14 Editais com canal a resposta seria "Fontes divergentes" por parágrafos
que não são canal de dúvidas: a heteroidentificação por videoconferência, o Napne, a secretaria
acadêmica, os endereços da Receita e do Flash Player, o telefone de um setor.

**"Exclusivamente" aparece na cláusula de canal de 12 dos 15 Editais.** O ponto para revisão da
`FR-1442` sairia em quase todo Edital: a questão da `DA-02` não é exceção, é a regra no Cefor.

**Depende do setor** — emenda de `R-011`, com estas evidências:

1. acrescentar "informações a respeito" (ou "informações sobre as inscrições") aos termos de
   dúvida, para as cláusulas dos FIC (58, 59, 77, 78);
2. contatos **do mesmo parágrafo** são um canal só ("e-mail ou whatsapp"); a divergência fica entre
   parágrafos;
3. endereço eletrônico não é canal de dúvidas, salvo na cláusula que o diz;
4. restringir a busca às seções em que o Edital põe a cláusula (disposições gerais ou finais), em vez
   de todas;
5. decidir, antes da abertura pública, como o assistente trata o "exclusivamente" de quase todos os
   Editais (`DA-02`).

### 7.2 Seções e fontes por pergunta (`D-007`)

**Verificado no código.** O guardião de cobertura (`SC-533`) e a tabela de pertinência sobre os
três Editais do corpus, que estão na estrutura de seções do sistema.

**Verificado nos Editais reais, por amostra.** Os assuntos ficam fora do capítulo "natural":

- o 89/2026 trata a inscrição em mais de um Perfil no capítulo das inscrições (3.11: "será
  considerada válida apenas a última inscrição") — coberto pela `P-06`, que trata `inscricao`;
- o 57/2026 declara "não cabendo recurso" no capítulo das inscrições (5.4 e 5.10), e não no de
  recursos. A `P-08` trata só `recursos`: ela não mostraria essa negativa declarada.

**Não verificável documentalmente.** Os Editais reais não estão na estrutura de seções do sistema
(chaves `inscricao`, `recursos`…); como um Edital real se distribui por elas depende de como o setor
o compõe. **Depende do setor:** se a `P-08` deve acompanhar também `inscricao` (caso do 57/2026), e
a conferência da tabela com Editais compostos no sistema.

### 7.3 Linguagem das respostas

**Verificado.** Termos que as respostas usam e que nenhum dos quinze Editais usa: "vagas
imediatas", "lista de concorrência", "soma ponderada", "decisória", "pontuada" e "mensagem
individual". Alguns vêm do documento que o próprio sistema compõe ("soma ponderada" está no PDF da
`068`), outros só da tela. Os rótulos de valores estão em `duvidas/domain/rotulos.py`, e as formas
da explicação em contracts/resposta.md §4.

**Depende do setor:** se a resposta fala a língua dos Editais do Cefor ou a do documento que o
sistema compõe, e a revisão de cada forma da explicação para quem se candidata.

