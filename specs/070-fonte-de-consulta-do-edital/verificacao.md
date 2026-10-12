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
| 6 | `P-08` do Técnico de Laboratório | "Depende da leitura do Edital", com o Evento "Resultado final e abertura do prazo recursal" inteiro. A explicação não diz que não cabe recurso e encaminha ao atendimento institucional |
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
| passando | **10575** (eram 10408 na medição de 09/10); **10600** depois da revisão de código (§5) |
| pulados | **11**, os mesmos onze nas duas; os testes da `070` não pulam nada |
| falhas e erros | nenhum nas duas |
| tempo | 1256s; 1213s depois da revisão |

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
   - os rótulos da Etapa decisória;
   - as regras de convocação da modalidade.

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

