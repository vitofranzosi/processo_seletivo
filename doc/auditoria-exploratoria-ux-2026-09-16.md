# Reauditoria exploratória de UX — Sistema de Processos Seletivos

**Data:** 2026-09-16 · **Fuso:** -03 (America/Sao_Paulo) · **Commit:** `5f37eec`

---

## 1. Protocolo e baseline

| Item | Valor |
|---|---|
| Commit auditado | `5f37eecf63178b17153df4542cf619b868683d82` (`5f37eec`) |
| Branch | `claude/reauditoria-processos-seletivos-de81a1` |
| Working tree no início | **limpo** |
| Execução | nativa, `manage.py runserver` na porta **8040** |
| Banco | PostgreSQL local, banco **exclusivo** `ps_reaudit_20260916`, criado para esta auditoria |
| Preparação | `make preparar` → **31 de 31** tabelas append-only protegidas; `migrate --check` sem pendências |
| Navegador | Browser pane do Claude Desktop (Chromium) |
| Viewports | desktop (1024×768) e **375×812** no portal |
| Identidade | `INTERFACE_SELETOR_IDENTIDADE=true`, `PORTAL_IDENTIDADE_DEMO=true` |
| Artefatos | `doc/diario-reauditoria-2026-09-16.md` (893 linhas) e este relatório |

**Identidades usadas** (todas fictícias): `ana.gestora` (Gestor), `bruno.elaborador` (Elaborador),
`carla.homologadora` (Homologador), `diego.publicador` (Publicador), `elis.julgadora` (Julgador),
`paula.presidente` (presidência da comissão), `rafael.avaliador`, `sofia.avaliadora`.

**Dados** — tudo criado **pela interface**, nada de `seed_demo`, nenhum dado pessoal real:
Processo `PS 01/2026`, Editais `01/2026` (percorrido inteiro) e `02/2026` (criado no reteste);
4 inscrições (`maria.candidata`, `joao.candidato`, `ana.candidata`, `carlos.candidato`), CPFs de
teste notórios; 1 Retificação publicada; 4 avaliações; 2 atos de classificação; 2 divulgações;
1 recurso julgado; 1 apuração de ocupação.

### Limitações metodológicas

1. **O auditor não é um novato real.** Li `AGENTS.md` e a seção de ambiente do `README.md` antes de
   começar. Onde isso me deu vantagem, está marcado no texto.
2. **Personas simuladas.** Não houve usuários reais. Previsões sobre comportamento humano aparecem
   como `[HIPÓTESE DE PESQUISA]`, nunca como fato.
3. **Upload de arquivo.** A automação do painel não expõe seletor de arquivo; os PDFs fictícios
   foram construídos no próprio formulário da página e **submetidos pelo botão real**. Nenhuma outra
   etapa foi contornada.
4. **Screenshots.** As capturas foram feitas no painel e não podem ser persistidas como arquivo por
   esta ferramenta. As evidências ficaram preservadas como **transcrições literais de tela** no
   diário, que são reproduzíveis e mais verificáveis que imagens.
5. **Relógio intocado.** Não alterei data do sistema nem do banco, o que deixou a Fase J bloqueada
   por uma regra legítima (prazo recursal aberto).
6. **Alteração de working tree:** apenas uma entrada acrescentada a `.claude/launch.json`, sem tocar
   nas existentes.

---

## 2. Resumo executivo

> **Quão perto o sistema está de permitir que um operador compreenda e execute um Processo Seletivo
> completo sem treinamento intensivo?**

**Muito perto na elaboração, na avaliação e na publicação — e ainda não chega ao fim.**

Consegui, sem consultar documentação para descobrir onde clicar, **criar um Processo do zero,
compor um Edital de nove etapas, submetê-lo, homologá-lo, publicá-lo, receber quatro inscrições pelo
portal, retificar o Edital publicado, constituir comissão, distribuir, avaliar, consolidar,
classificar, divulgar resultado preliminar, receber e julgar um recurso, ver a classificação ser
sucedida e republicar** — tudo pelo canal do ator. Esse é um arco muito maior do que a maioria dos
sistemas desta classe entrega.

O que impede a nota alta não é falta de funcionalidade: é que **as últimas etapas do arco não fecham
pela interface**, e que o produto **explica muito bem quase tudo, menos o que ele exige de você
antes de você precisar**.

Três frases resumem o estado:

- **O sistema ensina o domínio melhor do que ensina a si mesmo.** "O Resultado nasce do cálculo que
  o Edital publica", "o parecer é obrigatório porque é ele que responde a um recurso", "um resultado
  definitivo não é sucedido por um preliminar" — o produto é um excelente professor de Direito
  Administrativo aplicado. Mas "consolidar", "marco", "recorte", "geração", "faixa" chegam sem
  apresentação.
- **Os bloqueios estão certos e a maior parte deles agora chega na hora certa** — a maior evolução
  desde 13/09. Restam três que chegam tarde e um que não chega: um **404 mudo**.
- **A cauda do processo é onde se trava.** Convocação e suplência **não são executáveis** para um
  Edital simples, e quem tem a permissão de publicar resultado **não tem caminho até a ação**.

### Notas (0–10)

| Dimensão | Nota | Justificativa resumida | Confiança |
|---|---|---|---|
| Clareza conceitual | **7** | Definições excelentes no ponto de decisão (Processo×Edital, Perfil, forma da Etapa, consolidação). Mas 5 conceitos centrais sem apresentação: consolidar, marco, recorte, geração, faixa | Alta |
| Encontrabilidade | **7** | E0 na maior parte; mesa do avaliador e caixa do julgador são exemplares. Falham: publicar resultado (sem caminho), corte (link condicional), período de inscrições (E2) | Alta |
| Previsibilidade | **5** | "O que este ato provoca" é modelo para os **atos**. Mas a **composição** deixa publicar Editais inexecutáveis (sem marco, sem método de sorteio, com reserva sem apuração) e a conta chega depois da publicação | Alta |
| Fluxo ponta a ponta | **4** | Da concepção ao resultado funciona; **convocação e suplência não fecham**, a **reserva de vagas não apura** e o **sorteio não chega a executar** | Alta |
| Generalização entre famílias | **7** | O esqueleto (Edital → Perfil → vagas → Etapas → marco → resultado) cobriu **três famílias da amostra real** sem violência. Cede nas bordas, e sempre no mesmo lugar: turma/polo/código viram Perfil; **barema** e **cascata de grupos** não têm representação — ambas pendências já registradas pelo projeto | Alta |
| Organização do trabalho | **7** | Comissão, alocação e distribuição são dos melhores artefatos vistos — mas **ignoram o Perfil**: num Edital de 7 polos não há como entregar a cada comissão local o que é dela (`ACH-60`) | Alta |
| Experiência do candidato | **8** | Descoberta, inscrição, comprovante, versão aceita e acompanhamento muito bons; falta o **parecer** | Alta |
| Avaliação | **9** | Mesa de trabalho real: fila, rastreio de leitura, regra à vista, avanço automático, recuperação nomeada | Alta |
| Resultado e publicação | **8** | Cálculo × ato × divulgação separados; obsolescência detectada; diff posição a posição | Alta |
| Recuperação de erros | **7** | Prévias que pegam erro real, revogação, sucessão com motivo. Cai no 404 mudo e no beco da convocação | Média-alta |
| Visão global | **5** | "O que fazer agora" some quando o Processo fica vivo; oito contadores concorrentes na distribuição | Alta |

Não faço média: **9 na avaliação e 5 no fluxo ponta a ponta convivem**, e é exatamente essa a forma
do produto hoje.

---

## 3. Cobertura

| Cenário | Origem dos dados | Personas | Variáveis cobertas | Execução | Cobertura ausente |
|---|---|---|---|---|---|
| **1 — Seleção simples** | criado do zero pela interface | A, B, C, D, E, F | 1 Perfil, 3 vagas, 1 Etapa pontuada eliminatória+classificatória, sem modalidades, 1 marco, recurso admitido, 4 inscrições | **EXECUTADO** até resultado preliminar sucessor; **Fase J BLOQUEADA** (prazo recursal aberto); **Fase K BLOQUEADA** (ACH-46) | resultado definitivo; convocação; suplência |
| **2 — Análise e classificação** | mesmo Edital | C, D | comissão de 3, alocação, distribuição automática e manual, 2 avaliadores, consolidação em lote, classificação, sucessão por recurso | **PARCIALMENTE EXECUTADO** | **divergência entre avaliações** (exigiria `avaliações por inscrição ≥ 2`) |
| **3 — Sorteio** | Editais **03/2026** e **04/2026**, criados do zero pela interface | A, B, C, F | marco que ordena por sorteio, método completo (algoritmo, fonte, ocorrência, derivação, normalização, substituição), sorteio sem Etapa | **PARCIALMENTE EXECUTADO / BLOQUEADO** | congelamento do universo, semente, execução, ordem sorteada, manifesto, verificação pública, suplência |
| **4 — Modalidades e reservas** | Edital **02/2026**, criado do zero pela interface | A, B, C, D, E, F | 3 modalidades (AC/PcD/PPP) com percentual e fundamento legal, quadro 7/1/2, documentos por modalidade, inscrição por modalidade, corte pelo quadro, ocupação por recorte | **EXECUTADO** até a ocupação; **BLOQUEADO** na apuração dos recortes reservados | convocação pela reserva, suplência |
| **5 — Curso ou formação** | Edital **78/2026**, criado do zero pela interface, espelhando os Editais reais 57 e 78/2026 | A, B, C, E | duas **turmas** como Perfis, cotas AC/PcD/PPI por turma, reversão declarada, dois marcos de **sorteio**, congelamento da relação | **EXECUTADO** até o congelamento do universo | execução do sorteio (ACH-55) |
| **6a — Orientador de TFC** | Edital **14/2026** da amostra, montado pela interface | A, B, C | três **grupos em cascata**, duas Etapas com peso, **barema**, alvo fixo de 10 por código | **PARCIALMENTE EXECUTADO** | inscrições e execução (os pontos decisivos ficaram determinados na composição) |
| **6b — Pós-graduação, 7 polos** | Edital **28/2026** da amostra, montado e **publicado** pela interface | A, B, C, F | **7 polos × 3 modalidades** (21 recortes, 280 vagas), reversão por polo, 7 marcos de sorteio, escala | **EXECUTADO** até a publicação | inscrições, sorteio, heteroidentificação (não representável) |
| Reteste de regressão | Editais 01 e 02/2026 | A, B, C, D, F | Top 10 de 13/09 | **EXECUTADO** (8 de 10 pelo navegador) | reaproveitamento de Edital |

**Os seis cenários foram cobertos**, em três sessões no mesmo commit e no mesmo banco. Nenhum foi
contornado por fora da interface.

**Onde cada um parou, e por quê:** 1 e 4 na **convocação** (ACH-46, ACH-47); 3 e 5 na **execução do
sorteio** (ACH-55 — a declaração do método não é computável); 6 foi **parcialmente executado**, com
os dois pontos decisivos verificados na interface e a montagem completa dispensada por não acrescentar
evidência. As famílias dos cenários 5 e 6 foram escolhidas **a partir da amostra real** de 101 PDFs
de Editais, como o protocolo exige.

---

## 4. Jornada real observada — Cenário 1

**Concepção** 🟢 → **configuração** 🟡 → **publicação** 🟢 → **inscrição** 🟢 → **comissão** 🟢 →
**avaliação** 🟢 → **consolidação** 🟢 → **classificação** 🟢 → **resultado preliminar** 🟢 →
**recursos** 🟡 → **resultado final** ⛔ → **convocação** ⛔ → **Retificação** 🟢

Detalhe por trecho:

| Trecho | Estado | Por quê |
|---|---|---|
| Achar a gestão | 🟡 | nenhum caminho da raiz pública para `/gestao/` (ACH-01) |
| Criar Processo + Edital | 🟢 | a tela ensina o conceito no momento da decisão |
| Compor Perfil | 🟡 | 3 decisões de fases posteriores cobradas aqui (ACH-05) |
| Cronograma | 🟡 | etapa fica PENDENTE por período **em curso** (ACH-08) |
| Etapas de avaliação | 🟢 | consequência da forma declarada antes da escolha |
| Classificação (marco) | 🔴 | 28 controles; conceito sem apresentação; peso "(opcional)" que impede (ACH-10, ACH-16) |
| Inscrição / Anexos / Conteúdo | 🟢 | composição × derivação separadas, com link à origem |
| Revisão → Publicação | 🟢 | "O que este ato provoca"; segregação anunciada antes |
| Portal: descobrir e inscrever | 🟢 | filtros, prazo, comprovante com versão aceita |
| Comissão e alocação | 🟢 | dependência anunciada antes; conferência antes de gravar |
| Distribuição | 🟢 | bloqueio exemplar + proposta com antes/depois |
| Mesa do avaliador | 🟢 | melhor artefato do produto |
| Consolidação | 🟢 | coluna **POR QUÊ** com a regra e os números |
| Classificação e divulgação | 🟡 | ótimas, mas o publicador não chega até elas (ACH-40) |
| Recurso: interpor e julgar | 🟡 | porta de entrada resolvida; julgador sem a prova (ACH-43) |
| Superação do resultado | 🟢 | obsolescência detectada + diff posição a posição |
| Resultado definitivo | ⛔ | prazo recursal aberto — **bloqueio legítimo** |
| Convocação / suplência | ⛔ | **inalcançável** sem regra de corte (ACH-46) |
| Retificação | 🟢 | diff humano, histórico preservado, candidato avisado |

---

## 5. Regressão em relação à auditoria de 2026-09-13

| # | Achado anterior | Estado atual | Evidência do reteste | Efeito colateral / observação | Confiança |
|---|---|---|---|---|---|
| 1 | Edital publica vagas que o sistema não usa — S4 | **RESOLVIDO** | Preenchi só "Vagas imediatas: 3". A Revisão mostrou "3 vaga(s) imediata(s) · **o quadro reparte 3**" e "Quadro: Ampla concorrência — 3". A Ocupação apurou `Publicadas 3 · Efetivas 3`. A ajuda declara a regra nova: "Enquanto o Perfil não declara lista reservada, a quantidade da ampla concorrência é a de 'Vagas imediatas'" | A linha do quadro passou a ser **derivada**, exatamente a direção proposta. Sobra ruído menor: a coluna MODALIDADE exibe "Não declarada" onde não há modalidade | Alta |
| 2 | Reaproveitar publica cronograma vencido — S3 | **PARCIALMENTE RESOLVIDO**; reaproveitamento **NÃO RETESTADO** | A validação de data passada **agora existe**: a etapa 3 fica `PENDENTE` com "Esta etapa fica pendente enquanto o Cronograma carregar Evento cuja data já passou — 1 dele agora. Corrigir as datas abaixo é o que a conclui" | O mecanismo pedido foi criado. Mas **calibragem errada**: dispara para período **em curso** (ACH-08), e o portal mostra o mesmo evento como "ACONTECENDO AGORA" | Alta (mecanismo) / — (reaproveitamento) |
| 3 | Microcópia invisível — S3 sistêmico | **PARCIALMENTE RESOLVIDO** | DOM da etapa 2: as dicas **continuam `.oculto`** (0–1px), incluindo "Sem esta declaração o sistema recusa convocar". Porém as mesmas frases agora compõem o disclosure visível "Como preencher estes campos" | A prosa deixou de ser inacessível, mas **desgrudou do campo**. Li o bloco na Fase 1 sem perceber que explicava campos que ainda não existiam na tela (ACH-04) | Alta |
| 4 | Processo não recebe segundo Edital — S3 | **RESOLVIDO** | Botão **"Novo Edital neste Processo"** na tela do Processo → `/processos/<id>/editais/criar`. Criei o Edital 02/2026 pela interface | — | Alta |
| 5 | Julgador sem porta nem contexto — S3 | **PARCIALMENTE RESOLVIDO** | **Porta criada**: a coluna "O QUE POSSO FAZER" passa a exibir "Recursos recebidos (1)" com contador. **Contexto ainda ausente**, mas agora **declarado**: "Julgar não as concede" | O que era omissão virou limitação explícita e fundamentada (FR-105). Continua sendo decisão sem a prova (ACH-43) | Alta |
| 6 | 30 decisões na Classificação — S3 | **PARCIALMENTE RESOLVIDO** | Contei **28 controles**. Sorteio e corte agora são `details` colapsados com resumo do estado ("este marco não sorteia", "este marco não corta") | Progressive disclosure aplicado ao sorteio/corte. **Não aplicado** a combinação/normalização (obrigatórias com 1 Etapa) nem a casas decimais/arredondamento (ainda sem padrão) | Alta |
| 7 | Retificação em JSON Pointer e UTC — S3 | **PARCIALMENTE RESOLVIDO** | **UTC eliminado**: tudo em horário local ("30/09/2026 23:59"). A **prévia** ficou impecável (valor antigo riscado, novo destacado). Mas a tela do **ato** ainda exibe `/schedule/id=f15da77c-…/endAt` e `REPLACE` | O renderizador humano existe e **é usado no público** ("ALTERADO — Evento do cronograma…"), só não na tela interna do ato (ACH-31) | Alta |
| 8 | "Impedimento" com dois sentidos — S3 | **RESOLVIDO** (nomenclatura) / **PERSISTENTE** (contadores) | Não existe mais contador "com impedimento". A prontidão diz "ainda não há avaliação concluída para esta inscrição" → "pronta para consolidar"; "Impedimentos" é botão separado | O rename foi feito. Os contadores sobrepostos **permanecem** e aumentaram: contei **oito** (ACH-27) | Alta |
| 9 | Atos operacionais em um clique — S2/S3 | **RESOLVIDO** | "Confira antes de consolidar" e "Confira antes de emitir" são telas próprias. E o marco **agora avisa**: "A divulgação pública ficou para trás. O que está público é resultado preliminar, de 15:22, e corresponde a uma ordem anterior" | O estado que faltava foi acrescentado, com a frase quase idêntica à proposta | Alta |
| 10 | Bloqueios corretos que chegam tarde — S2 | **RESOLVIDO em 2 de 3** | **Distribuir**: bloqueio agora aparece na tela e **diz o que fazer** ("Antecipar o término publicado é ato de Retificação; encerrar o Edital é outro ato"). **Definitivo**: a prévia recusa **antes** de confirmar, com data. **Segregação**: a tela de Homologar avisa antes | Sobra a 3ª ocorrência: a tela do Edital **antes** de homologar ainda não menciona a consequência (ACH-19) | Alta |

**Regressões:** nenhuma identificada. Não encontrei comportamento pior que o de 13/09.

**Complexidade nova introduzida:** a tela de Retificação passou a expor **todos** os campos de todas
as entidades, inclusive o bloco inteiro de sorteio num Edital que não sorteia, com identificadores de
máquina visíveis como opções (`DIGITOS_EM_SEQUENCIA`, `OCORRENCIA_SEGUINTE_DA_MESMA_FONTE`) — ACH-32.

**Problema deslocado:** a correção do achado 3 tirou a explicação da invisibilidade e a colocou num
bloco distante do campo. Resolveu a acessibilidade; moveu o custo para a correlação mental (ACH-04).

---

## 5-bis. Cenários 3 e 4 — sorteio, modalidades e reservas

> Executados numa segunda sessão, mesmo commit `5f37eec`, mesmo banco. Três Editais novos criados do
> zero pela interface: **02/2026** (modalidades), **03/2026** e **04/2026** (sorteio).

### 5-bis.1 — Cenário 4: modalidades e reservas — **EXECUTADO**

**Montagem.** Perfil `PROF-MAT`, **10 vagas**, três modalidades — `AC` Ampla Concorrência, `PCD`
Pessoas com Deficiência (5%, Lei 13.146/2015 art. 34), `PPP` Pessoas Negras (pretas e pardas) (20%,
Lei 12.990/2014 art. 1º) —, quadro **7/1/2**, três documentos (um geral, um só de PcD, um só de PPP),
regra de corte `FROM_VACANCY_TABLE`. Quatro inscrições em três modalidades, avaliadas, consolidadas,
classificadas.

**O que está muito bem resolvido — e responde ao achado nº 1 da auditoria anterior.** Os AVISOS que
faltavam existem, com quase a redação proposta:
> *"O Perfil 'PROF-MAT' publica 10 vaga(s) imediata(s) e reparte 10 no quadro. Sem linha no quadro:
> … — **a ocupação e a convocação não terão quantidade a apurar nesse(s) recorte(s)**."*

Outros pontos fortes verificados: a **armadilha das duas grafias** de ampla concorrência é
administrada (a linha duplicada some sozinha ao declarar qual modalidade é a AC); o quadro é
**conferido aritmeticamente** (`IMPEDE … soma 13 e o Perfil declara 10 — excesso de 3`) e **contra o
percentual normativo**, sem impor (*"o percentual publicado (20%) sobre 10 vagas daria 2. A
quantidade declarada é a que vale"*); a modalidade **governa os documentos** e isso é dito antes da
escolha; trocar de modalidade com documento enviado abre uma tela própria — **"Mudar de modalidade
descarta documentos"** — nomeando o arquivo. O Edital publicado traz o quadro e as modalidades
corretamente, e agrupa os documentos por modalidade.

### ACH-47 — o sistema aceita, publica e não consegue executar a reserva de vagas — **S4 / P0**

Com o quadro 7/1/2 publicado e as inscrições classificadas:
1. A **classificação** produziu **uma ordem única**, com a modalidade apenas como coluna. A tela
   **ignora `?lista=`** (testado).
2. O **corte** do recorte reservado responde: *"Este recorte não tem ordem emitida: não há o que
   cortar."* E a tela de corte **não oferece navegação** entre recortes.
3. A **ocupação** lista os três recortes e oferece **"Apurar a ocupação deste recorte"** em cada um —
   mas nos reservados falha: *"Este recorte não tem ordem vigente: não há ocupação a apurar."*

**Causa [CÓDIGO]** — `classificacao/application/emissao.py:58-63`: *"Um ato computado é **sempre** o
de ampla concorrência — **só o sorteio emite por lista**"*, com `lista_id=None`. É decisão de escopo
deliberada (a 021 tratou cotas no sorteio; a 015 não).

**Por que é S4 mesmo sendo deliberado:** a interface deixa declarar as modalidades, **valida a soma**,
**publica a reserva com fundamento legal**, **recebe e identifica** inscrições por modalidade — e só
no fim oferece três botões idênticos, dois dos quais **sempre falham**, com uma mensagem que nomeia o
sintoma e não a causa. Um Edital pontuado com reserva **publica cotas que o sistema não tem como
apurar nem convocar**, e nada avisa enquanto ainda era possível corrigir.

**Direção.** Ou a classificação passa a emitir por lista quando o Perfil declara reserva, ou a
composição **impede** declarar reserva em marco pontuado, dizendo por quê. O que não pode continuar é
publicar a reserva e descobrir depois.

### 5-bis.2 — Cenário 3: sorteio — **PARCIALMENTE EXECUTADO / BLOQUEADO**

**Executado:** composição do método completo, publicação, roteamento por tipo de marco, leitura da
tela de sorteio, recusa por fonte indisponível.
**Não executado:** congelamento do universo, semente, execução, ordem sorteada, manifesto, verificação
pública, suplência — por **falta de população** (o prazo que declarei venceu antes de eu inscrever) e
por **indisponibilidade da fonte externa**, que o sistema corretamente se recusa a substituir.

**A tela de execução do sorteio é um dos melhores artefatos do produto.** Exibe o **método declarado
no Edital** por extenso — algoritmo, fonte, ocorrência, derivação, normalização, "Se a ocorrência
faltar" — com um **hash SHA-256 do método**; separa norma de execução (*"Alterá-lo é uma Retificação,
e não uma decisão desta tela"*); declara a ordem correta em sete palavras (*"o universo é
comprometido antes de a semente existir"*); e, quando a fonte falha, **recusa por princípio**:
> *"Prosseguir exige Retificação que declare outro método: **o sistema não escolhe fonte por conta
> própria, e continuar tentando seria escolher**."*

### ACH-48 — a validação proíbe exatamente o sorteio que a ajuda descreve — **S3 / P1**

Salvar um marco de sorteio num Edital **sem Etapas** é recusado: *"Um marco classificatório deve
enumerar ao menos uma Etapa: sem Etapa não há pontuação a combinar, e a ordem não sai."*
Mas a ajuda **da mesma tela** diz: *"o sorteio costuma vir antes da análise documental: quando é o
caso, **não há Etapa que habilite a participar**"*, e o campo de elegibilidade oferece **"Nenhuma —
entram todas as inscrições submetidas"**. Para compor um sorteio puro é preciso **inventar uma Etapa
fictícia** — foi o que fiz, e está declarado.

### ACH-49 — publiquei um Edital sem marco algum, e nada avisou — **S4 / P0**

O salvamento do marco do Edital 03/2026 falhou (ACH-48); **eu não percebi**, porque os campos
continuavam preenchidos ("O que você digitou foi preservado abaixo") e o passo seguinte seguia
acessível. A Revisão não acusou nada (`IMPEDE: []`). Submeti, homologuei e **publiquei**.
Verificado: `classificationMilestones = []` no snapshot canônico.

**O Edital 03/2026 está publicado, imutável, anuncia-se "Sorteio público" e não contém regra
classificatória alguma.** Ninguém pode ser classificado por ele; corrigir exige Retificação.
A tela de composição **afirma** a regra em prosa — *"Um Perfil sem marco não classifica"* — e a
validação de publicabilidade **não a aplica**: há `IMPEDE` para "ao menos um Perfil" e "ao menos um
Evento", e nenhum para Perfil sem marco.

### ACH-50 — o Edital publica o método errado e omite a regra do sorteio — **S4 / P0**

Com o marco salvo (Edital 04/2026), o documento publicado imprime:
```
SORT-X  Sorteio Público
Combinação:      soma ponderada da Etapa Confirmação de inscrição (peso 1)
Normalização:    nenhuma
Arredondamento:  sem casas decimais, truncamento
```
Duas falhas somadas: **omite integralmente a regra do sorteio** (varri o PDF: sem algoritmo, sem
`Loteria Federal`, sem semente, sem normalização nem substituição) e **afirma um método falso** — diz
que a ordem sai de soma ponderada de uma Etapa, quando sairá de sorteio.

Contradiz a ajuda da própria tela (*"o método é **conteúdo publicado do Edital**"*). O método é
tratado como norma internamente e **não chega ao documento que o candidato lê** — sem ele, a
verificação pública do sorteio não tem base normativa.

### ACH-51 — a fonte da semente é texto livre, e só dois nomes exatos funcionam — **S3 / P1**

`sorteios/infrastructure/fontes/__init__.py` reconhece exatamente `"Loteria Federal"` e
`"Fonte de demonstração"`. Na **composição** o campo é **texto livre**, sem lista nem validação; na
**Retificação** é um **select** com essas duas opções. A lista fechada existe e é conhecida — só não
é oferecida onde o valor é criado. Qualquer variação produz um Edital **publicado e imutável** cuja
fonte não executa, e a descoberta acontece **no dia do sorteio**. Funcionou comigo por acaso.

---

## 5-ter. Cenários 5 e 6 — curso/formação, grupos em cascata e polos

> Terceira sessão. Famílias escolhidas **a partir da amostra real** (101 PDFs em `~/Downloads`),
> como o protocolo exige para o cenário 6.

### 5-ter.1 — Cenário 5: curso/formação — **EXECUTADO**

Espelhei os Editais reais **57/2026** (dois cursos de aperfeiçoamento, 80 vagas cada, AC 56/PcD 4/
PPI 20, sorteio eletrônico) e **78/2026** (Libras A1, duas turmas de 21 e 40 vagas). Montei o Edital
`78/2026` com duas turmas, cotas por turma, reversão declarada e dois marcos de sorteio; publiquei;
inscrevi dois candidatos; **congelei a relação** do sorteio.

**A resposta à pergunta central do cenário é positiva, com uma ressalva.** O termo
**"Perfil de Vaga" é do domínio** — o Edital 78 real o usa literalmente na coluna do quadro de
distribuição. A ressalva é que, no Edital real, o *perfil* é o **público** ("Público externo"),
idêntico nas duas linhas, e o que distingue as ofertas é a **turma** (horário):

```
Código de vaga | Perfil da Vaga   | Quantidade | Dias e horários das aulas
Turma 1        | Público externo  | 21         | Segundas e quintas, 09h às 11h
Turma 2        | Público externo  | 40         | Segundas e quintas, 13h às 15h
```

**`ACH-52` (S2)** — Para representar isso, criam-se **dois Perfis cujo perfil é o mesmo**, e o
horário vai para a **Descrição**. O Perfil oferece `carga horária`, `remuneração` e `atribuições` —
vocabulário de **vaga de trabalho** — e **não tem** turma, horário, polo nem modalidade de ensino.
Não impede nada; é artificialidade de modelagem.

**`ACH-53` (S2)** — A página pública do Edital de Libras tem como título **"Seleção de Tutores a
Distância"**: o nome do **Processo** ao qual o anexei. A tela de criação incentiva reunir Editais num
Processo, e o Cefor publica unificados anuais — quando o Processo reúne objetos diferentes, o portal
rotula todos pelo nome do Processo.

**O que a família revelou de bom.** A opção de reversão **"A quantidade que ficou sem preencher"**
corresponde **literalmente** à cláusula 4.3 do Edital 57. Os quadros aceitaram o arredondamento real
das cotas (5% de 21 → 1). E, sobretudo:

**`PP-113` — o sorteio resolve cotas, e é aí que a família real vive.** A tela do sorteio apresentou
**quatro recortes** com universo e congelamento próprios (`Todos os inscritos` 2 · `AC` 1 · `PcD` 1 ·
`PPI` 0). Isso **confirma pela interface** o que o código dizia no **ACH-47**: ordem por lista existe
no **sorteio**, não na classificação pontuada — e a família dominante do Cefor é **sorteio + cotas**.
Isso **reduz a frequência provável do ACH-47**, sem reduzir sua gravidade quando ocorre.

**`PP-114` — congelamento do universo, completo e conforme o Edital real.** *"Relação congelada em
16/09/2026 18:14 por paula.presidente, com 2 participantes. Resumo `c738902…` Ver no canal público"*,
com o **número de cada participante** — exatamente o que o Edital exige. Suceder a relação exige
motivo escrito: *"A relação publicada é o compromisso do universo."*

**`ACH-54` (S2)** — A tela de sorteio continua oferecendo "Publicar e congelar a relação" para o
recorte da **modalidade AC declarada**, que **não tem vagas** (elas passaram à linha geral). A
colisão de *nomes* já foi tratada; falta dizer **quantas vagas** cada recorte tem.

### `ACH-55` (S3) — o método do sorteio pede prosa e precisa de dado

Preenchi `Ocorrência que fixará a semente` e `Como a ocorrência decorre da data programada` em
**prosa** — como um Edital se escreve, e como os rótulos pedem — e usei a **"Fonte de demonstração"**.
A tela respondeu:

> *"A ocorrência declarada e todas as substitutas previstas pela regra publicada estão indisponíveis.
> Prosseguir exige Retificação que declare outro método…"*

**Não foi a fonte que falhou** [CÓDIGO]: `FonteDeTeste` devolve material para qualquer referência
exceto a string `"indisponivel"`. O que falhou foi a **derivação da referência**
(`previa.py:96-108`): sem ela, a tela não oferece "Observar a ocorrência" e cai na mensagem acima.

Três problemas somados: os campos são texto livre mas precisam ser **dado computável**; **nada valida
na composição** (o Edital foi submetido, homologado e publicado sem uma palavra); e a mensagem
**atribui a falha à fonte externa** e prescreve **Retificação**, sem dizer o que corrigir. Mesma
família do **ACH-51**.

### 5-ter.2 — Cenário 6: Orientador de TFC (Edital 14/2026) — **PARCIALMENTE EXECUTADO**

> **Correção registrada.** Minha primeira escolha para este cenário foi o Edital **IFNMG 1122/2026**
> (chamada de experiências exitosas para a Reditec). **Estava errada**, e o usuário apontou: é de
> **outra instituição** e não é processo seletivo de pessoas nem de alunos. O arquivo estava na pasta
> de trabalho, mas **não integra a amostra do projeto**. Os achados que dependiam dele —
> *ajuste regional* e *inscrito não-pessoa* — foram **descartados**. O cenário foi refeito com um
> Edital da amostra, e o achado que sobreviveu está revalidado abaixo.

**A amostra real** está catalogada em `doc/avaliacao-de-capacidade-editais-2026-09-12.md`: onze
Editais do Cefor/Ifes (58, 59, 69, 77, 78, 158, 57, 28, 173, 14, 76), com o 46/2026 explicitamente
"fora do alvo por decisão". Como o cenário 1 cobriu seleção de pessoal pontuada e o 5 cobriu curso
FIC com sorteio e cotas, restavam **28/2026** (pós-graduação, 7 polos × 3 modalidades) e
**14/2026** (Orientador de TFC). Escolhi o **14/2026**: o 28 repete o mecanismo do cenário 5
variando a estrutura de oferta, enquanto o 14 é **computado**, com **barema**, **duas etapas** e
**grupos em cascata** — nada disso tocado antes. O próprio documento do projeto o chamava de
"a medida da distância".

**Estrutura real:** três **grupos** escolhidos pelo candidato na inscrição (1: concursados do campus
ofertante; 2: concursados de outros campi; 3: externos), com *"três listas de inscritos, uma para
cada grupo"*; **cascata** — convocam-se prioritariamente os do Grupo 1 **até 10 por código**, e
*"caso o número de classificados deste grupo seja menor que 10 … serão convocados … Grupo 2 e …
Grupo 3"*; **duas etapas** (Prova de Títulos e Entrevista); **barema** nos Anexos IV e V, com
*"limite máximo de pontos"* por item; e **autopontuação** do candidato.

**Montei no sistema:** Perfil `TFC-GESTAO-EPT` com 10 vagas, os três grupos como Modalidades, e as
duas Etapas com peso 1.

### `ACH-59` (S3) — grupo de prioridade não é modalidade, e o sistema empurra para a resposta errada

Modelar grupo como modalidade é o mapeamento natural — o candidato **opta** por um, como opta por uma
cota. O sistema então cobra a repartição das vagas:

> *"…declara 3 Modalidade(s) e não declara qual delas é a da ampla concorrência…"*
> *"…publica 10 vaga(s) imediata(s) e reparte 10 no quadro. Sem linha no quadro: Grupo 1…, Grupo 2…,
> Grupo 3 — **a ocupação e a convocação não terão quantidade a apurar nesse(s) recorte(s)**."*

Mas o Edital **não reparte**. As três saídas são todas falsas:

| Saída | O que o Edital passaria a afirmar |
|---|---|
| Repartir (ex. 10/0/0) | que os Grupos 2 e 3 **não têm vaga** |
| Deixar as linhas vazias | ocupação e convocação **sem quantidade a apurar** |
| Declarar G1 como ampla concorrência | que G2 e G3 são **reservas com quantidade própria** |

**Honestidade sobre a novidade:** esta é **pendência já conhecida** — a tabela do projeto lista, para
o 14/2026, exatamente *"cascata Grupo 1→2→3 (016/019)"*. O que acrescento é **como ela se manifesta
na composição**: o operador não recebe um "não dá", recebe **dois avisos que o empurram a declarar
uma repartição que o Edital não tem**.

### `ACH-56` revalidado (S2) — o barema não é representável

Verificado na interface, agora num Edital da amostra: a Etapa expõe onze campos — `name`,
`scheduleEventId`, `forma`, `minimumScore`, `maximumScore`, `rotuloFavoravel`, `rotuloDesfavoravel`,
`weight`, `evaluationsPerRegistration`, `eliminatory`, `classificatory` — e **nenhum** de critério,
item ou limite por item. A Mesa oferece **um** campo de nota.

O barema dos Anexos IV e V só cabe como **anexo PDF**: o avaliador lança **a soma**, e o sistema não
guarda nem confere a composição; a **autopontuação** não tem onde ser declarada. Também aqui o
projeto já registra as pendências: **"barema (D-4)"** e **"autopontuação (P-7)"**.

### O que o 14/2026 mostrou que o modelo faz bem

**Duas Etapas com peso**, combinadas por soma ponderada no marco, representam sem violência o
"Prova de Títulos + Entrevista". O **alvo fixo de 10** é coberto pela regra de corte `FIXED`. E o
**código de inscrição** mapeia para Perfil — o mesmo padrão de turma (ACH-52) e de eixo.

### 5-ter.3 — Cenário 6 (b): Edital 28/2026, pós-graduação com 7 polos — **EXECUTADO**

A segunda família do cenário 6, executada a pedido. Acrescenta o que nenhum outro cenário tocou:
**polo** e **escala**. Estrutura real: **280 vagas em 7 polos**, cada um com **AC 28 / PcD 2 /
PPI 10 = 40**, reversão **por polo**, seleção por **sorteio**, e verificação da autodeclaração pela
**CLVA do campus**, com recurso para a **CPVA institucional**.

Montei e **publiquei** o Edital inteiro: 7 Perfis (polos) × 3 modalidades = **21 modalidades e 21
linhas de quadro**, 7 marcos de sorteio, 1 Etapa, 1 documento — **sem um único IMPEDE**.

### `ACH-60` (S3) — a organização do trabalho não conhece o Perfil

Verificável em duas telas:
- **Alocação por Etapa**: a matriz tem uma coluna **por Etapa**, nunca por Perfil. Com 7 polos e uma
  Etapa, quem for alocado recebe inscrições **dos sete polos**.
- **Distribuir**: os filtros são **Cobertura** e **Avaliador**. **Não há filtro por Perfil nem por
  modalidade**, e a tabela não traz coluna de Perfil.

Consequência: a presidência distribuiria **280 inscrições sem saber, na tela, de qual polo cada uma
é** — e sem poder separar o que cabe à comissão local de cada campus. **E a CLVA não tem
representação**: a Comissão é **única por Processo**, e a **CPVA** — instância recursal institucional,
distinta da comissão do certame — também não tem lugar. *(Pendência já registrada pelo projeto como
"heteroidentificação (L-2 + spec própria)".)*

### `ACH-61` (S2) — a escala da composição, medida

| Tela | Medida |
|---|---|
| Etapa 2 (Perfis), 7 polos × 3 modalidades | **18.943 px**, **399 controles**, **14 avisos** simultâneos |
| Etapa 5 (Classificação), 7 marcos de sorteio | 6.238 px, 237 controles |
| Método do sorteio | **98 campos** para declarar **7 vezes a mesma regra** |

No Edital real o método do sorteio é **um só** para os sete polos. No sistema ele mora no **marco**,
que é por Perfil — então é declarado sete vezes. Além do custo, cria risco de integridade: sete
declarações independentes da mesma regra, e qualquer divergência de digitação produz métodos
diferentes no mesmo Edital.

### O que escala bem

**`PP-115`** — os 21 recortes foram declarados, validados e publicados sem impedimento; os 14 avisos
iniciais desapareceram à medida que declarei ampla concorrência e quantidades.
**`PP-116`** — o **portal escala bem**: as 7 ofertas cabem em 2.728 px, cada uma com polo,
localidade, concorrências e vagas. A página pública é o oposto da tela de composição.
**`PP-117`** — recusa por estado, ao tentar publicar sem homologar: *"Este ato não cabe na situação
atual. Ele só é admitido a partir de Homologado… **Nada foi alterado.**"*

### Terceira e quarta ocorrências de padrões já registrados

- **`ACH-53`** — a página pública do 28/2026 também se chama **"Seleção de Tutores a Distância"**,
  nome do Processo. Terceira ocorrência (01, 78, 28).
- **A repartição não chega ao candidato** — cada oferta exibe "40 vagas imediatas" e a lista de
  concorrências, **sem as quantidades**. O candidato PcD de Iúna não sabe que há 2 vagas para ele.
  Quarta ocorrência.
- **O total do Edital não é somado**: as 280 vagas só aparecem porque eu as escrevi na descrição.

### As duas famílias do cenário 6, lado a lado

| | **14/2026** Orientador de TFC | **28/2026** 7 polos |
|---|---|---|
| Mecanismo | computado, duas Etapas com peso | sorteio por recorte |
| Não representa | **barema** (`ACH-56`), **cascata de grupos** (`ACH-59`) | **comissão local por polo** (`ACH-60`), heteroidentificação |
| Representa bem | duas Etapas com peso; alvo `FIXED`; código → Perfil | 21 recortes; reversão por polo; sorteio por lista; portal |
| Custo escondido | — | **escala da composição** (`ACH-61`) |

**As duas caem no mesmo ponto do arco:** a **organização do trabalho e a execução**, não a
elaboração. Nenhuma falha em publicar; ambas falham em **conduzir**.

### Achados descartados por virem do Edital errado

`ACH-57` (ajuste regional) e `ACH-58` (inscrito não-pessoa) **não valem**: descreviam o Edital do
IFNMG. No contexto do Cefor, o inscrito **é** pessoa física e o modelo está adequado.
Permanece válida a observação factual que sustentou a correção do `ACH-12`: um *fato exigido do
candidato* aceita apenas **`Data`** e **`Número inteiro`**.

### Correção retroativa — `ACH-12` estava impreciso

Registrei na primeira sessão que não havia desempate por **maior idade**. Verificado agora: o fato
declarado aceita o tipo **`Data`**, então `data-de-nascimento` + critério "Menor valor de um fato
declarado" resolve o desempate etário **diretamente**. O mecanismo existe e é adequado; permanece só
a ressalva de que o valor é **autodeclarado**. **ACH-12 rebaixado a observação.**

---

## 6. Top 10 fricções atuais

> **Revisto após os cenários 3 e 4.** Três achados novos entraram no topo (ACH-47, ACH-49, ACH-50) e
> deslocaram para baixo itens da primeira sessão. O padrão que os une está na seção 11 (E-7).

### 0. Três formas de publicar um Edital que o sistema não consegue executar — `ACH-49` · `ACH-50` · `ACH-47` — **S4 / P0**

Os três achados mais graves desta auditoria são variações de um mesmo defeito estrutural: **a
validação de publicabilidade não verifica se o Edital é executável**, e o ato imutável sai assim.

| # | O que foi publicado | O que o sistema não consegue fazer | Avisou? |
|---|---|---|---|
| `ACH-49` | Edital "Sorteio público" **sem marco algum** (`classificationMilestones = []`) | classificar qualquer pessoa | **não** — `IMPEDE: []` |
| `ACH-50` | Edital de sorteio cujo documento diz *"soma ponderada da Etapa … (peso 1)"* e **omite algoritmo, fonte da semente e regras** | publicar o método real; permitir verificação pública | **não** |
| `ACH-47` | Edital com **reserva de vagas** (7/1/2, com fundamento legal) em marco pontuado | apurar ocupação e convocar pelos recortes reservados | **não** |

Em todos, a tela de composição **afirma a regra em prosa** — "Um Perfil sem marco não classifica";
"o método é conteúdo publicado do Edital" — e a validação **não a aplica**. O operador descobre
depois da publicação, quando a correção já custa Retificação.

**Direção comum.** A "Validação do conteúdo" precisa de uma classe nova de verificação: **o Edital é
executável?** — Perfil tem marco; marco de sorteio publica método; reserva declarada tem via de
apuração. Não é polish: hoje o `IMPEDE` cobre "ao menos um Perfil" e "ao menos um Evento", e nada do
que faz o certame funcionar. **Confiança: alta.**

---


### 1. Convocação e suplência são inalcançáveis num Edital que não declara corte — `ACH-46` — **S3 / P0**

**Evidência [UI].** Ocupação apurada (`Publicadas 3 · Ocupadas 0 · A ocupar 3`). Cliquei em "Pedir a
faixa seguinte com este déficit" e recebi:
> *"Não foi possível apurar: Não há geração vigente neste recorte: emita o corte antes de continuá-lo."*

Varri todos os links de `main` na tela do Edital: **não existe rota de corte, faixa ou convocação**
acessível.

**Causa confirmada [CÓDIGO].** `interface/templates/interface/detalhe.html:146` renderiza o link da
tela de corte **apenas `{% if marco.cutRule %}`**. Meu marco declarou "este marco não corta".
`convocacao/application/convocar.py:8`: *"Ela lê a faixa que o corte vigente…"*. Cadeia: sem
`cutRule` → sem tela de corte → sem geração → sem faixa → **sem convocação**.

**Agravante [UI].** A ajuda da etapa 5 declara outra consequência para a ausência de corte — *"sem
ele, o marco não corta e a Etapa seguinte recebe todos os habilitados"* — e **silencia a que
importa**: sem regra de corte **não há convocação**. A decisão é tomada na etapa 5; o efeito aparece
semanas depois, num Edital já publicado.

**Afetados.** Toda seleção simples sem fase seguinte — o caso mais comum. Persona C descobre no dia
de convocar. **Recuperação:** só Retificando o Edital para declarar um corte artificial.

**Direção.** Duas coisas, nenhuma é tooltip: (a) a tela de ocupação **não deve oferecer** um botão
impossível — deve dizer, como o produto faz em toda parte, "Este marco não declara regra de corte:
a convocação exige uma faixa, e a faixa exige o corte"; (b) a etapa 5 deve declarar a consequência
real no momento da escolha. **Confiança: alta.**

---

### 2. Quem pode publicar o resultado não tem caminho até a ação — `ACH-40` — **S3 / P0**

**Evidência [UI].** Como `diego.publicador` (Publicador puro): a tela do Edital **não exibe o bloco
"Classificação"**, e a URL do ato de classificação devolve **404**. O único caminho que o sistema
indica — *"A divulgação é ato do próprio ato emitido, e sai de lá — em Consultar ato e proveniência"*
— leva a uma tela que ele não pode abrir.

**Correção do meu próprio diagnóstico [CÓDIGO].** Eu havia concluído que divulgar exigia vínculo de
comissão. **Estava errado.** `interface/views.py:5594` (`_edital_para_publicar`) exige **apenas**
`resultado:publicar`. Reteste decisivo: abri `/marcos/<id>/atos/<id>/publicar` diretamente como
`diego.publicador` → **a tela abre normalmente**. O 404 vinha de outra view, `ato_de_ordenacao`
(linha 5545), que usa `_edital_para_classificar`.

**O achado real, portanto:** a permissão existe, a tela funciona, **e a navegação não liga as duas**.
Na configuração de papéis segregada que o próprio produto propõe, o resultado só é publicado por
quem também pertence à comissão — ou por quem souber montar a URL.

**Direção.** A tela do Edital deve listar os marcos e seus atos para quem tem `resultado:publicar`,
com a ação de divulgar; e o texto do marco deve parar de mandar o operador a uma tela que o ator
talvez não alcance. **Confiança: alta.**

---

### 3. O julgador decide sem poder ver a prova — `ACH-43` — **S3 / P0**

**Evidência [UI].** A tela do recurso declara: *"Para abrir o resultado atacado, a avaliação que o
produziu e os documentos da inscrição é preciso presidir este Processo, ter a permissão de auditoria
ou a de consultar inscrições. **Julgar não as concede.**"* A razão do recurso era *"o currículo
comprova, na página 2, contrato de tutoria de 8 meses"* — verificável **apenas** no documento. Fixei
88 pontos com base num resumo de uma linha (`ELIMINADA · 30,0000`).

**É regra, não bug [CÓDIGO/SPEC].** `specs/018/spec.md` **FR-102** garante ao julgador a
fundamentação e a motivação — não os documentos; **FR-105**: respostas "MUST NOT ampliar o acesso a
documentos do candidato". É proteção de dados escrita como requisito. **Retiro** minha leitura
inicial de falha de autorização e reclassifico de S4 para S3.

**O que permanece.** O produto protege o documento restringindo o julgador e **não oferece nenhum
ato de instrução do recurso**: não há como a presidência juntar, para aquele julgador e aquele
recurso, o extrato da avaliação e a peça contestada. Sobra o dilema: acumular papéis (desfazendo a
proteção que a FR-105 quer) ou decidir sem ver.

**Direção.** Um **ato de instrução** com escopo estreito — a presidência anexa ao recurso o parecer e
o documento citado, registrado na auditoria, visível só naquele recurso. Preserva a FR-105 (não
amplia acesso genérico) e devolve o contraditório. **Confiança: alta.**

---

### 4. O parecer não chega a quem mais precisa dele — `ACH-42` — **S3 / P1**

**Evidência [UI].** Verifiquei `/acompanhamento` e `/inscricoes/<id>/` do candidato eliminado: a
única ocorrência de "parecer" no HTML é o **verbo**, dentro de um comentário de CSS. O candidato lê
"Eliminada · pontuação 30" e "30,0000 < 40,0000". Não lê *"o currículo não comprova os 6 meses"*.

**Tensão com a própria spec [CÓDIGO/SPEC].** `specs/012/spec.md:369` justifica exigir o parecer
assim: *"o desfavorável é justamente o caso em que **o candidato mais precisará da fundamentação
para recorrer**, e é contra o parecer que o recurso responderá."* A razão declarada para exigir o
parecer é servir ao candidato — e ele não o recebe.

**Direção.** Exibir o parecer ao titular quando o resultado da Etapa lhe for desfavorável e houver
prazo recursal — que é exatamente o recorte que a spec descreve. **Confiança: alta.**

---

### 5. Duas datas-limite contraditórias para o mesmo recurso — `ACH-41` — **S3 / P1**

**Evidência [UI].** Na **mesma tela** de acompanhamento, o candidato lê:
> "Cabe recurso contra este resultado até **18/09/2026** às 23h59." *(janela do marco)*
> Cronograma: "Prazo para interposição de recursos … **06/10/2026 – 07/10/2026"** *(Evento)*

São duas fontes normativas do mesmo prazo, e **o sistema nunca as confronta**: nem na composição,
nem na "Validação do conteúdo", nem na publicação do resultado. Quem confiar no Cronograma publicado
perde o prazo real por 18 dias.

**Honestidade.** A configuração incoerente foi minha, ao antecipar a divulgação sem mexer no
Cronograma. **O achado não é o meu erro** — é que produzir essa contradição é trivial, e nada a
sinaliza em nenhum dos cinco pontos onde poderia. Ecoa o achado já conhecido do projeto de que
checklist e testes de citação ficam verdes com regras incompatíveis.

**Direção.** Uma validação que confronte janela recursal declarada × Evento de recurso do Cronograma,
e um AVISO na publicação do resultado quando as duas divergirem. **Confiança: alta.**

---

### 6. O bloqueio que não diz o que fazer, em três lugares — `ACH-02` · `ACH-30` · `ACH-38` — **S2 / P1**

O produto tem um padrão **excelente** para isso, na tela do Edital:
> *"Você não poderá publicar este Edital… **Peça a alguém com a permissão de publicar que conclua o
> ato.**"*

E **não o aplica** em três lugares onde o ator trava:
1. **Gestor que acabou de criar o Edital** — a validação lista "IMPEDE: Ao menos um Perfil é
   obrigatório", e não há controle para criar Perfil nem indicação de que falta papel.
2. **Gestor diante de Edital publicado** — "Correções ocorrem por Retificação", sem a ação e sem
   dizer quem pode.
3. **Presidência mandada divulgar** — segue a instrução e encontra "Você não tem ação disponível
   sobre este ato", sem o "peça a alguém".

**Direção.** Generalizar a frase que já existe. É a mudança de maior retorno por linha alterada.
**Confiança: alta.**

---

### 7. A única negativa que não se explica é um 404 — `ACH-35` — **S2 / P1**

**Evidência [UI].** Como `diego.publicador`, a URL de distribuição devolveu **404** — e a própria
página de debug mostra que a URL **casou** com o padrão. Com `paula.presidente`, abre. É autorização
por desenho, como o projeto documenta.

**O problema é a inconsistência:** em todo o resto o sistema diz "Nenhum ato disponível para seus
papéis nesta situação" ou explica e indica o próximo passo. Aqui, silêncio. Em produção será um 404
genérico — ainda sem explicação.

**Direção.** Onde a negativa é de **vínculo** (não de escopo institucional), responder com a mesma
gramática das outras telas. O 404 opaco deve ficar reservado ao que o ator não deve sequer saber que
existe. **Confiança: alta.**

---

### 8. As telas de ato são as menos legíveis do produto — `ACH-39` · `ACH-31` · `ACH-45` — **S2 / P1**

**Evidência [UI].** "Ato de classificação": título `Ato c818be37-…`; Proveniência com o UUID de
Processo, Edital, Perfil, Marco e Versão; e a tabela **"Resultados que entraram na ordem"** com
**quatro colunas inteiras de UUID** — nenhuma coluna legível, nenhum nome de participante.
Desempate como `MAIOR_PONTUACAO_NA_ETAPA · e8e3ebd5-…`. Na Retificação:
`/schedule/id=f15da77c-…/endAt` e `REPLACE`. No recurso: `INTERPOSTO POR:
cand:19421183ce52413fa51515cf3ffba8d1` — com o nome logo abaixo.

**O contraste é o achado.** O **público** lê o mesmo fato como **`ALTERADO` — Evento do cronograma
"Período de inscrições…" — Término**. O renderizador humano existe e está em produção. Ele
simplesmente não foi aplicado às telas internas — que são as que ficam registradas para o operador.

**Direção.** Reaproveitar o renderizador público nas telas de ato, mantendo o identificador ao lado
(auditabilidade sem opacidade). **Confiança: alta.**

---

### 9. Um período de inscrições em curso é tratado como data vencida — `ACH-08` — **S2 / P2**

**Evidência [UI].** Evento "Inscrições", 16/09 00:00 → 30/09 23:59. A gestão acusa:
> "O Evento … começou em 16/09/2026 às 00:00, **que já passou**."

e mantém a etapa 3 `PENDENTE`. O **portal**, com o mesmo dado, exibe "Inscrições abertas desde
16/09/2026… Faltam 14 dias" e **"ACONTECENDO AGORA"**.

Consequência: um Edital perfeitamente legítimo — inscrições abrindo no dia da publicação — **nunca
consegue ter a etapa 3 concluída**, e duas superfícies do mesmo sistema discordam sobre o mesmo fato.

**Direção.** A regra deve olhar o **fim** do período, não o início: vencido é o Evento cujo término
já passou. **Confiança: alta.**

---

### 10. O marco classificatório: 28 controles e um rótulo que mente — `ACH-10` · `ACH-16` — **S2 / P2**

**Evidência [UI].** Para **1 Perfil, 1 Etapa, 3 vagas**, o marco pede 28 controles, entre eles duas
decisões matematicamente vazias com uma única Etapa (`Como as pontuações se combinam`,
`Normalização`) e duas obrigatórias sem padrão (`Casas decimais`, `Arredondamento`).

E o rótulo que mente: na etapa 4 o campo se chama **`Peso (opcional)`** e diz "Vazio: a Etapa não
pondera". Ao enumerar a Etapa num marco — decisão tomada **depois**, na etapa 5 — ele vira
impeditivo, e a contradição só aparece na **etapa 9**:
> "O marco enumera uma Etapa sem peso declarado. Quem enumera declara o peso."

**Direção.** Combinação e normalização só aparecem com **duas ou mais** Etapas enumeradas; casas
decimais ganham padrão 2 e arredondamento "meio para cima"; e o peso deixa de ser "(opcional)" —
passa a ser pedido no momento em que a Etapa é enumerada pelo marco. **Confiança: alta.**

---

## 7. Glossário observado

Coluna 3 = o que **inferi pela UI antes** de consultar qualquer fonte. Não corrigi retroativamente.

| Conceito | Como a UI apresenta | Interpretação inicial (só pela UI) | Significado confirmado | Problema |
|---|---|---|---|---|
| Processo Seletivo | "o Processo reúne Editais que podem ter cronogramas próprios" | contêiner de Editais | idem | — (D0) |
| Edital | "nenhum Edital existe sem ele" | o ato normativo | idem | — (D0) |
| Perfil de Vaga | "uma oportunidade do Edital, com requisitos, vagas e modalidades próprios" | o cargo/vaga a que se concorre | idem | — (D0) |
| Etapa | "as fases pelas quais os candidatos passam… valem para todos os Perfis" | fase de avaliação | idem | — (D0) |
| **Marco classificatório** | "onde a ordem entre participantes é produzida. Um Perfil sem marco não classifica" | "algo que ordena; não sei por que é separado da Etapa" | regra de ordenação **por Perfil** | **D2/D3** — nome inventado; e a assimetria Etapa→Edital × marco→Perfil nunca é explicada (ACH-09) |
| **Consolidar** | só o botão, e a tela de confirmação | "fechar as avaliações?" | transformar avaliações em **Resultado de Etapa** | **D3** — conceito central sem apresentação no ponto de uso (ACH-36) |
| **Recorte** | "Apurar a ocupação deste recorte" | "a linha do quadro?" | a lista de concorrência apurada | **D3** — não definido |
| **Geração / Faixa** | "Não há geração vigente neste recorte" | **não entendi** | conjunto de convocáveis produzido pelo corte | **D3** — nunca apresentados antes de aparecerem num erro (ACH-46) |
| Quadro de vagas | "o quadro reparte 3" | repartição por modalidade | idem, derivado quando não há reserva | — (resolvido desde 13/09) |
| Cadastro reserva | 3 opções nomeadas | idem | idem | — (D1) |
| Modalidade | "Qual delas é a ampla concorrência" | cota / lista de concorrência | idem | D1, com armadilha conhecida |
| Alocação × Distribuição | "Alocação por Etapa" + botão "Distribuir" | quem trabalha × quem recebe o quê | idem | — bem resolvido |
| Impedimento | botão próprio "Impedimentos" | conflito de interesse | idem | — (resolvido desde 13/09) |
| Publicação × Retificação | "Correções ocorrem por Retificação" | ato imutável + emenda | idem | — (D1, muito bem ensinado) |
| Versão vigente | "a vigência é da versão consolidada, que não tem documento próprio" | "difícil, mas entendi" | idem | **D1/D2** — preciso e denso (ACH-20) |
| Preliminar × Definitivo | "um resultado definitivo não é sucedido por um preliminar" | idem | idem | — (D1) |
| Superação / sucessão | "MOTIVO DA SUPERAÇÃO" + diff | resultado substituído com rastro | idem | — excelente |

---

## 8. Mapa de encontrabilidade

Só primeiro contato. Não reclassifiquei nada que ficou fácil depois de aprendido.

| Intenção | "Eu procuraria em…" | Local real | Esforço | 1º contato? |
|---|---|---|---|---|
| Criar um Processo Seletivo | página inicial do sistema | `/gestao/` (a raiz pública **não leva lá**) | **E4** | sim (ACH-01) |
| Criar o Processo, já em `/gestao/` | tela inicial | botão "Novo Processo Seletivo" | **E0** | sim |
| Cadastrar vagas | dentro do Edital | etapa 2 do assistente | **E0** | sim |
| Definir as fases da seleção | dentro do Edital | etapa 4 | **E0** | sim |
| Definir como se classifica | junto das Etapas | etapa 5, **por Perfil** | **E1** | sim |
| Definir o período de inscrição | no Cronograma (etapa 3) | **etapa 6** — e o aviso diz "marcado", mandando ao Cronograma | **E2** | sim (ACH-13) |
| Criar outro Edital no Processo | tela do Processo | "Novo Edital neste Processo" | **E0** | sim (resolvido) |
| Adicionar avaliador | tela do Processo | aba "Comissão" | **E0** | sim |
| Distribuir inscrições | junto da comissão | "Alocação por Etapa" → "Distribuir" | **E0** | sim |
| Saber quantas inscrições chegaram | tela do Edital | "Inscrições recebidas (4)" | **E0** | sim |
| Encontrar meu trabalho (avaliador) | não sabia | **login já cai em "Minhas Etapas"** | **E0** | sim |
| Julgar um recurso | não sabia | "Recursos recebidos (1)" na coluna de ações | **E0/E1** | sim (resolvido) |
| Corrigir uma publicação | tela do Edital | "Retificar" (só com papel de elaborar) | **E1** | sim |
| Publicar o resultado | tela do marco | **nenhum caminho** para o Publicador puro | **E4** | sim (ACH-40) |
| Convocar / chamar suplente | Ocupação | **não encontrável** (link condicionado a `cutRule`) | **E4** | sim (ACH-46) |
| Preparar o sorteio | — | **não testado** | — | — |

**Prioritários (E2–E4):** período de inscrições, publicar resultado, convocar, achar a gestão.

---

## 9. Pontos de imprevisibilidade

Configurações cujo efeito só ficou evidente muito depois:

1. **`Peso (opcional)`** (etapa 4) → vira impeditivo ao enumerar a Etapa num marco (etapa 5), e a
   contradição aparece na etapa 9.
2. **Término das inscrições** (etapa 3) → governa **quando a avaliação pode começar**. Descoberto na
   distribuição, com o Edital já publicado; corrigir custou uma **Retificação**.
3. **Regra de corte ausente** (etapa 5) → **impede a convocação**. A ajuda declara só o efeito sobre
   a Etapa seguinte. Descoberto na Fase K — o mais caro dos três.
4. **Atribuições × Requisitos** (etapa 2) → microcópias diferentes produzem parágrafo corrido × lista
   no documento. Descoberto **no PDF já publicado**; corrigir exige Retificação.
5. **Numeração das seções** → a tela de composição numera 1–12; o documento publica 1–10, com as
   compostas fora e Anexos omitido quando vazio. "A seção 8" significa coisas diferentes conforme a
   tela — e é a Retificação que endereça seções.
6. **Forma de convocação "Não declarado"** → o aviso está correto ("o sistema recusa convocar"), mas
   **nunca cheguei a vê-lo morder**: o fluxo trava antes, no corte.

---

## 10. Complexidade desnecessária

| Decisão | Poderia | Evidência |
|---|---|---|
| `Como as pontuações se combinam` / `Normalização` | **aparecer só com ≥ 2 Etapas** enumeradas | com 1 Etapa, soma e média ponderadas são idênticas |
| `Casas decimais` / `Arredondamento` | **ganhar padrão** (2, meio para cima) | obrigatórias e sem default numa seleção trivial |
| `Qual delas é a ampla concorrência` / `Reversão de vaga reservada` | **aparecer só após a 1ª Modalidade** | expostas com zero modalidades declaradas |
| `Como a convocação é comunicada` | **ser pedida na convocação**, não na composição do Perfil | decisão de fase muito posterior cobrada no cadastro |
| Coluna `MODALIDADE` na classificação | **sumir** quando não há modalidade | exibe "Não declarada" em todas as linhas |
| Oito contadores na distribuição | **colapsar em dois eixos**: cobertura e conclusão | `4 todas`, `4 sem nenhum avaliador`, `4 sem avaliador suficiente`, `4 com avaliação pendente` |
| Bloco de sorteio na Retificação | **não ser renderizado** para marco que não sorteia | expõe `DIGITOS_EM_SEQUENCIA`, `OCORRENCIA_SEGUINTE_DA_MESMA_FONTE` |
| `Chave` do documento exigido | **ser derivada do nome**, editável só quando preciso | obriga a inventar identificador técnico e entender versionamento |

---

## 11. Problemas estruturais

**E-1 · A cauda do processo não fecha.** Convocação e suplência dependem de uma cadeia
(corte → geração → faixa) cujo primeiro elo é **opcional na composição** e **invisível na navegação**
quando não declarado. Não é polish: é o desenho que faz um Edital simples ser inconvocável.

**E-7 · A validação não pergunta se o Edital é executável.** `IMPEDE` cobre a existência de Perfil e
de Evento — e nada do que faz o certame funcionar: Perfil sem marco (ACH-49), marco de sorteio sem
método publicado (ACH-50), reserva de vagas sem via de apuração (ACH-47), marco sem regra de corte
sem convocação (ACH-46). Em todos, a prosa da tela **afirma** a regra e a validação **não a aplica**.
É a causa única dos quatro achados S3–S4 desta auditoria, e a intervenção de maior retorno.

**E-2 · Autorização e navegação discordam.** O produto tem dois eixos — papel institucional e vínculo
de comissão — e isso é correto. Mas a navegação é montada por um e as permissões pelo outro: o
Publicador **pode** publicar e **não chega** lá; a presidência é mandada a uma tela que não pode
abrir; a negativa por vínculo cai num 404 mudo. O eixo duplo só é explicado no seletor de
identidade, que **não existe em produção**.

**E-3 · Duas gramáticas para o mesmo fato.** O mesmo dado é renderizado de forma humana no público
(`ALTERADO — Evento do cronograma…`) e de forma técnica na gestão (`/schedule/id=…/endAt`,
`REPLACE`, quatro colunas de UUID). O tradutor existe; falta aplicá-lo onde o operador decide.

**E-4 · Fontes normativas que ninguém confronta.** Janela recursal (marco) × Evento de recurso
(Cronograma); término de inscrições (Cronograma) × designação (etapa 6); numeração de seção (tela) ×
numeração (documento). O sistema é rigoroso **dentro** de cada fonte e cego **entre** elas.

**E-5 · A explicação desgrudou do campo.** A correção da microcópia invisível criou um bloco
coletivo, distante e anterior aos campos que explica — que aparece inclusive com zero cartões na
tela.

**E-6 · A visão global some quando o Processo fica vivo.** "O que fazer agora" conduz a elaboração
com excelência e, publicado o Edital, reduz-se a **Encerrar** e **Cancelar** — justo quando há 4
inscrições, comissão a compor e avaliação a organizar.

---

## 12. Quick wins

1. Generalizar **"Peça a alguém com a permissão de…"** aos três bloqueios que hoje calam (ACH-02, 30, 38).
2. A regra de "Evento vencido" passar a olhar o **término**, não o início (ACH-08).
3. Padrões para `Casas decimais` (2) e `Arredondamento` (meio para cima) (ACH-10).
4. Não renderizar o bloco de sorteio na Retificação de marco que não sorteia (ACH-32).
5. Omitir a coluna `MODALIDADE` quando o Perfil não declara modalidades.
6. Formatar pontuação com as casas declaradas em toda parte — hoje `92,00` no público e `92,0000` na
   gestão e **no motivo exibido ao candidato** (ACH-17).
7. Trocar o rótulo do link do marco: de "Consultar ato e proveniência" para algo que anuncie a ação
   que mora lá (ACH-37).
8. A etapa 7 (Anexos) deixar de ficar `PENDENTE` quando a própria tela diz que vazio "é legítimo"
   (ACH-15).
9. Na tela do ato, acrescentar **uma coluna legível** (nome do participante) à tabela de resultados
   que entraram na ordem — sem remover os identificadores (ACH-39).
10. Descrever o objeto do recurso em terceira pessoa nas telas administrativas — hoje "**o meu**
    resultado da Análise Curricular" aparece para o julgador (ACH-44).

---

## 13. Melhorias estruturais

### 13.1 Tornar a convocação alcançável — e a decisão que a governa, visível
**Raiz:** E-1. **Evidências:** ACH-46.
**Mudança:** (a) a tela de ocupação nunca oferece "faixa seguinte" onde não pode haver faixa,
e explica a cadeia; (b) a etapa 5 declara, ao lado de "Regra de corte", que **sem ela não há
convocação**; (c) o link do corte deixa de ser condicionado ao `cutRule` e passa a levar a uma tela
que explica por que está vazio.
**Fluxos afetados:** composição, ocupação, convocação. **Risco:** baixo — nenhuma regra muda.
**Por que não é só explicação:** hoje o operador é levado a um botão que não pode funcionar.

### 13.2 Um ato de instrução do recurso
**Raiz:** E-2 + FR-105. **Evidências:** ACH-43, ACH-42.
**Mudança:** a presidência anexa ao recurso, para aquele julgador, o parecer da Etapa atacada e o
documento citado; o acesso é registrado na auditoria e **limitado àquele recurso**. Em paralelo, o
parecer desfavorável passa a ser visível ao **titular** enquanto houver prazo recursal.
**Risco:** exige cuidado com dados pessoais — por isso o escopo é por recurso, não por papel.
**Por que é melhor que ampliar o papel:** ampliar `recurso:julgar` violaria a FR-105; o ato de
instrução preserva a regra e devolve o contraditório.

### 13.3 Navegação derivada da permissão, não do vínculo
**Raiz:** E-2. **Evidências:** ACH-40, ACH-35, ACH-38.
**Mudança:** a tela do Edital lista marcos e atos para quem tem `resultado:publicar`, com a ação de
divulgar; negativas por **vínculo** respondem com a gramática das outras telas, reservando o 404 ao
que é de outro escopo institucional.
**Impacto:** desbloqueia a divulgação na configuração segregada que o produto recomenda.

### 13.4 Um renderizador normativo único
**Raiz:** E-3. **Evidências:** ACH-31, ACH-39, ACH-45.
**Mudança:** o renderizador que já serve o público passa a servir as telas de ato, homologação e
publicação, com o identificador **ao lado** do nome legível.
**Por que não é polish:** são as telas onde alguém assina.

### 13.5 Validação entre fontes normativas
**Raiz:** E-4. **Evidências:** ACH-41, ACH-13, ACH-18.
**Mudança:** a "Validação do conteúdo" ganha verificações **cruzadas** — janela recursal × Evento de
recurso; término de inscrições × designação; e a numeração exibida na composição passa a ser a do
documento.
**Impacto:** ataca a classe inteira de contradições silenciosas, não um caso.

### 13.7 Uma validação de executabilidade, antes de publicar
**Raiz:** E-7. **Evidências:** ACH-49, ACH-50, ACH-47, ACH-46.
**Mudança:** acrescentar à "Validação do conteúdo" uma família de verificações que pergunta se o
Edital **funciona**, e não apenas se está preenchido: (a) `IMPEDE` para Perfil sem marco
classificatório; (b) `IMPEDE` para marco de sorteio cujo método não será publicado, e inclusão do
método na seção de marcos do documento; (c) `IMPEDE` (ou bloqueio na composição) para reserva de
vagas declarada em marco que não emite ordem por lista; (d) `AVISO` para marco sem regra de corte,
dizendo que a convocação dependerá dela.
**Fluxos afetados:** composição, revisão, publicação. **Risco:** baixo — nenhuma regra de domínio
muda; o que muda é *quando* o operador descobre.
**Por que é melhor que explicar:** hoje a prosa já explica tudo isso, e o Edital sai errado mesmo
assim. O que falta não é texto — é a verificação.

### 13.6 Um painel de condução para o Processo vivo
**Raiz:** E-6. **Evidências:** ACH-25.
**Mudança:** publicado o Edital, "O que fazer agora" continua respondendo — inscrições recebidas,
comissão pendente, Etapas sem alocação, avaliações em aberto, atos obsoletos, publicação defasada.
O sistema **já calcula** todos esses estados; eles só não estão reunidos.
**Não é "fazer um dashboard":** é não desligar o guia que já existe.

---

## 14. O que **não** fazer

- **Não** adicionar tooltip explicando "geração" e "faixa": o problema é oferecer uma ação impossível,
  não a falta de glossário.
- **Não** conceder acesso a documentos ao papel `recurso:julgar` para resolver o ACH-43: violaria a
  FR-105. O caminho é o ato de instrução com escopo por recurso.
- **Não** desfazer a decisão de manter ajuda fora dos cartões (ACH-04): ela foi tomada
  deliberadamente. Aproximar a explicação **dentro** dessa regra é o caminho.
- **Não** transformar o 404 de vínculo em 404 "mais bonito": ele precisa virar uma **recusa nomeada**,
  não um erro mais educado.
- **Não** remover os UUIDs das telas de ato: eles são a auditabilidade. Falta o nome **ao lado**.
- **Não** resolver o ACH-41 obrigando o Cronograma a ter Evento de recurso: o remédio é confrontar as
  duas fontes, não criar uma terceira obrigação.
- **Não** tratar o cenário 1 como prova de que o produto suporta sorteio, modalidades, cursos ou
  outras famílias — **nada disso foi testado**.

---

## 15. Padrões que devem ser preservados

Registro os que mais me impressionaram, com a frase literal quando ela é o padrão:

1. **Ensinar o conceito no momento da decisão** — "Um Processo Seletivo nasce com o primeiro Edital…
   nenhum Edital existe sem ele."
2. **Declarar a consequência antes da escolha** — "A pontuada publica nota e não publica rótulos; a
   decisória publica os rótulos."
3. **"O que este ato provoca"** como página própria dos atos normativos, com quem recebe o trabalho
   depois.
4. **Bloqueio anunciado antes da tentativa, com as saídas nomeadas** — "Antecipar o término publicado
   é ato de Retificação; encerrar o Edital é outro ato, mais amplo e irreversível."
5. **Bloqueio que diz o que fazer** — "Peça a alguém com a permissão de publicar que conclua o ato."
6. **A coluna "O QUE POSSO FAZER"**, que muda com o papel do ator.
7. **A coluna "POR QUÊ"** na consolidação — a regra e os números: "30,0000 < 40,0000".
8. **Prévia que não grava e diz que não grava** — "Nada foi registrado por abrir esta tela";
   "Abrir esta tela não apura nada".
9. **Conferência antes de gravar, com antes/delta/depois** — `TEM HOJE | RECEBE | FICA COM`. Ela
   pegou, na minha execução, uma alteração normativa indevida que eu não tinha percebido.
10. **A mesa do avaliador** — fila, rastreio real de leitura ("2 de 2 abertos por você"), regra à
    vista, avanço automático para a próxima pendente, e a recuperação nomeada ("a reabertura é ato da
    presidência, com motivo registrado").
11. **O parecer explicado pela finalidade futura** — "É o que responderá a um eventual recurso."
12. **Detecção de obsolescência com diff posição a posição**, e o aviso de que **a divulgação ficou
    para trás**.
13. **Link permanente que não mente** — "Este resultado foi sucedido… não é mais o que vale."
14. **A versão aceita pelo candidato** — "Sua inscrição continua valendo sob a versão que você
    aceitou."
15. **Privacidade por desenho** — CPF mascarado na mesa do avaliador; a lista pública nomeia apenas
    quem recebeu posição; "Se este endereço puder ser utilizado, enviaremos um código".
16. **Dizer que o vazio é legítimo** — "É legítimo: nem todo Edital fornece formulário próprio."
17. **Nomear o que não se pode corrigir** — "O que não se corrige por Retificação nesta seção."

---

## 16. Backlog priorizado

| Prioridade | ID | Achado | Tipo | Sev. | Esforço | Impacto | Recomendação |
|---|---|---|---|---|---|---|---|
| **P0** | ACH-49 | Publica Edital sem marco algum, sem IMPEDE | validação | **S4** | P | Alto | 13.7 |
| **P0** | ACH-50 | Edital de sorteio publica método errado e omite a regra | documento normativo | **S4** | M | Alto | 13.7 |
| **P0** | ACH-47 | Reserva de vagas publicada sem via de apuração/convocação | estrutural | **S4** | G | Alto | 5-bis.1 |
| **P1** | ACH-48 | Marco de sorteio exige Etapa, contra a própria ajuda | regra × ajuda | S3 | P | Médio | 5-bis.2 |
| **P1** | ACH-51 | Fonte da semente em texto livre; só 2 nomes exatos | encontrabilidade | S3 | P | Médio | 5-bis.2 |
| **P1** | ACH-55 | Método do sorteio em prosa não é computável; sorteio inexecutável e mensagem culpa a fonte | validação | S3 | M | Alto | 13.7 |
| **P2** | ACH-59 | Grupo de prioridade em cascata não é modalidade; avisos empurram a repartir o que o Edital não reparte | modelo | S3 | G | Médio | 5-ter.2 |
| **P1** | ACH-60 | Organização do trabalho não conhece Perfil: alocação por Etapa, distribuição sem filtro por polo/modalidade | AI | S3 | M | Alto | 5-ter.3 |
| **P2** | ACH-61 | Escala da composição: 19 mil px e 399 controles com 7 polos; método do sorteio declarado 7× | densidade | S2 | M | Médio | 5-ter.3 |
| **P2** | ACH-56 | Sem critérios de avaliação com pontuação própria | modelo | S2 | M | Médio | 5-ter.2 |
| **P2** | ACH-52 | Perfil é de vaga de trabalho; turma/polo não existem | modelo | S2 | M | Médio | 5-ter.1 |
| **P2** | ACH-53 | Portal rotula o Edital com o título do Processo | AI | S2 | P | Médio | 5-ter.1 |
| **P2** | ACH-54 | Sorteio oferece congelar recorte sem vagas | densidade | S2 | P | Médio | 5-ter.1 |
| **P0** | ACH-46 | Convocação inalcançável sem regra de corte | estrutural | S3 | M | Alto | 13.1 |
| **P0** | ACH-40 | Publicador sem caminho até publicar resultado | navegação | S3 | P | Alto | 13.3 |
| **P0** | ACH-43 | Julgador decide sem a prova | modelo de fluxo | S3 | M | Alto | 13.2 |
| **P1** | ACH-42 | Parecer não chega ao candidato | direito do candidato | S3 | P | Alto | 13.2 |
| **P1** | ACH-41 | Duas datas-limite de recurso contraditórias | validação cruzada | S3 | M | Alto | 13.5 |
| **P1** | ACH-02/30/38 | Bloqueio sem "peça a alguém" (3 telas) | microcópia | S2 | P | Alto | 12.1 |
| **P1** | ACH-35 | Negativa por vínculo vira 404 mudo | consistência | S2 | P | Médio | 13.3 |
| **P1** | ACH-39/31/45 | UUID e vocabulário de máquina nas telas de ato | consistência | S2 | M | Médio | 13.4 |
| **P1** | ACH-16 | `Peso (opcional)` que impede | nomenclatura | S2 | P | Médio | 6.10 |
| **P2** | ACH-08 | Período em curso lido como vencido | regra de validação | S2 | P | Médio | 12.2 |
| **P2** | ACH-26 | Término das inscrições governa a avaliação, e não se diz | previsibilidade | S2 | P | Médio | 13.5 |
| **P2** | ACH-10/05 | Marco com 28 controles; decisões prematuras no Perfil | densidade | S2 | M | Médio | 6.10 / 10 |
| **P2** | ACH-36 | "Consolidar" sem definição no ponto de uso | conceito | S2 | P | Médio | frase na tela de distribuição |
| **P2** | ACH-13/34 | Período de inscrições editado em dois lugares | arquitetura da informação | S2 | M | Médio | 13.5 |
| **P2** | ACH-18/33 | Numeração de seção diverge tela × documento | endereçamento | S2 | P | Médio | 13.5 |
| **P2** | ACH-25 | Visão global some com o Processo vivo | AI | S2 | M | Médio | 13.6 |
| **P2** | ACH-01 | Sem caminho da raiz pública para a gestão | encontrabilidade | S2 | P | Médio | rodapé discreto |
| **P2** | ACH-27 | Oito contadores concorrentes | densidade | S1/S2 | P | Médio | 10 |
| **P2** | ACH-04 | Explicação distante do campo | AI | S1/S2 | M | Médio | 13.5 / §14 |
| **P3** | ACH-28/29 | Avisos obsoletos após a publicação | estado | S1/S2 | P | Baixo | limpar por estado |
| **P3** | ACH-17 | `40.0000` / `92,0000` — precisão interna vazando | formatação | S1 | P | Baixo | 12.6 |
| **P3** | ACH-03/15 | Estados `PRONTA PARA REVISAR` / `PENDENTE` confusos | estado | S1 | P | Baixo | 12.8 |
| **P3** | ACH-21/23 | Atribuições × Requisitos; declaração sem link ao Edital | microcópia | S1 | P | Baixo | prévia + link |
| **P3** | ACH-22/37/44/11/32/24 | Retomada da inscrição; rótulo do link; 1ª pessoa; resumo defasado; ruído na Retificação; validade do comprovante | diversos | S0/S1 | P | Baixo | 12 |
| **P3** | ACH-06 | `name` de campo em inglês | consistência interna | S0 | P | Baixo | — |
| — | ACH-12 | ~~Sem desempate por maior idade~~ — **retificado**: o fato tipo `Data` resolve | — | — | — | — | **descartado** (ver 5-ter) |

---

## 17. Limitações e pontos não testados

**Não executado:** a **execução do sorteio** propriamente dita — semente, ordem sorteada, manifesto,
verificação pública e suplência (bloqueada pelo ACH-55; o **congelamento** foi executado em 5-ter.1),
**convocação pela reserva** (ACH-47),
divergência entre avaliações, reaproveitamento de Edital ("Partir de um Edital anterior"),
impedimentos de avaliador, remoção de membro com trabalho feito, encerramento e cancelamento de
Processo/Edital, supervisão, auditoria, API, anexos, `seed_demo`.

**Bloqueado:** resultado definitivo (prazo recursal aberto — regra legítima; não alterei o relógio);
convocação e suplência (ACH-46).

**Apenas inferido:** o comportamento com volume (testei 4 inscrições); acessibilidade além do básico
observado (`aria-label` nas células de alocação, foco gerenciado na avaliação, ordem de leitura) —
**não afirmo conformidade WCAG**; desempenho — não medi nada e **não deduzo escalabilidade do
código**.

**Montagem dispensada, com razão declarada:** o Edital do cenário 6 (14/2026) foi montado até a
composição — Perfil, grupos e as duas Etapas — e não foi publicado nem recebeu inscrições: os dois
pontos decisivos (**barema** e **cascata de grupos**) ficaram determinados ali, e levá-lo adiante não
acrescentaria evidência.

**Erro de escolha corrigido:** a primeira versão deste cenário usou o Edital **IFNMG 1122/2026**, que
**não pertence à amostra do projeto** nem ao contexto (outra instituição, chamada de trabalhos para
um evento). O usuário apontou; refiz o cenário com o 14/2026 e **descartei** os dois achados que
dependiam do Edital errado (`ACH-57`, `ACH-58`). A lição metodológica fica registrada: eu havia
tratado "PDF na pasta de trabalho" como "amostra do projeto", sem verificar o catálogo — que existe,
em `doc/avaliacao-de-capacidade-editais-2026-09-12.md`.

**Exige validação com usuários reais:** que a numeração divergente de seções (ACH-18) cause erro em
Retificação; que a página longa de Retificação induza digitação no campo errado (meu caso foi erro de
automação, e está declarado); que "marco classificatório" seja de fato o termo que trava o novato;
que o bloco "Como preencher" seja lido antes dos campos.

**Correções que fiz ao meu próprio diagnóstico**, registradas por honestidade: (a) ACH-40 **não** é
"publicar exige comissão" — é falta de navegação; (b) ACH-43 **não** é bug de autorização — é regra
deliberada (FR-105), e o que falta é o ato de instrução; (c) a alteração indevida flagrada na
Retificação foi **erro da minha automação**, não do produto — o produto, aliás, a pegou.

**Três falsos positivos descartados na segunda sessão**, todos com a mesma origem — preencher
formulários por script contorna as affordances visuais do produto: (d) "o PDF omite os rótulos das
modalidades" — era o **meu regex**, que parava no parêntese escapado; o escape do produto está
correto; (e) "a mensagem de erro do marco está vazia" — o motivo está numa `<ol>` que meu extrator
não leu; a mensagem é boa; (f) "o campo de instante não tem exemplo de formato" — **tem placeholder**
(`2026-11-20T20:00:00-03:00`), que eu sobrescrevi via automação. Registro-os porque a diferença entre
um S4 real e um artefato de ferramenta é exatamente o que uma auditoria precisa acertar.

---

## 18. Fechamento

### 1. O que uma pessoa consegue compreender hoje **apenas usando o sistema**

A **natureza normativa do que está fazendo**: que Edital publicado é imutável e se corrige por
Retificação; que publicar é ato irreversível com autoridade signatária; que há segregação de funções
e por quê; que resultado preliminar e definitivo são coisas diferentes; que um ato pode ser sucedido
sem ser apagado. A **elaboração inteira** de um Edital, guiada por nove etapas com estado. A
**inscrição**, do lado do candidato, incluindo a que versão do Edital ele aderiu. E o **trabalho de
avaliar** — a mesa do avaliador é autoexplicativa a ponto de dispensar treinamento.

### 2. Onde é preciso conhecer previamente como o produto foi pensado

- **O duplo eixo de autorização** (papel institucional × vínculo de comissão). Só é explicado no
  seletor de identidade, que **não existe em produção**.
- **A cadeia corte → geração → faixa → convocação**, que não aparece em lugar nenhum antes de virar
  um erro.
- **A separação entre "vagas do Perfil" e "linha do quadro"** — hoje derivada, mas ainda presente
  como dois campos no modelo.
- **Que a numeração das seções na composição não é a do documento.**
- **Que o término das inscrições governa quando a avaliação pode começar.**

### 3-bis. O quanto o modelo generaliza

Percorri **três famílias da amostra real do projeto**: seleção de pessoal com análise pontuada
(cenário 1, família do 173/2025), curso FIC com turmas, cotas e sorteio (cenário 5, família do
57/58/59/77/78/158) e seleção com grupos em cascata e barema (cenário 6, Edital 14/2026). O cenário 4
acrescentou reserva de vagas a um cargo pontuado.

O núcleo `Edital → Perfil → vagas → Etapas → marco → resultado → publicação` **é sólido e o
vocabulário é do domínio**: "Perfil de Vaga" está escrito nos Editais reais do Cefor. Todas as
famílias couberam nele, e o que varia de uma para outra — turma, polo, código de inscrição — mapeia
consistentemente para **Perfil**.

Onde o modelo cede são três bordas, **as duas primeiras já registradas como pendência pelo projeto**:
- **Barema** — critérios com pontuação e limite por item não existem; a Etapa tem uma nota só
  (`ACH-56`, pendência "barema (D-4)" e "autopontuação (P-7)").
- **Cascata de grupos** — prioridade de convocação sem reserva de quantidade não tem representação,
  e a composição empurra o operador a repartir vagas que o Edital não reparte
  (`ACH-59`, pendência "cascata Grupo 1→2→3 (016/019)").

- **A organização do trabalho ignora o Perfil** — a alocação é por Etapa e a distribuição não filtra
  por polo nem por modalidade, de modo que um Edital de 7 polos com comissões locais por campus não
  tem como entregar a cada uma o que é dela (`ACH-60`). Esta é a borda que mais dói na condução.

E uma borda de vocabulário: o Perfil carrega `carga horária`, `remuneração` e `atribuições` —
desenho de vaga de trabalho —, de modo que um curso o reinterpreta e põe o horário da turma na
descrição (`ACH-52`).

**O padrão que atravessa as quatro famílias:** o sistema **elabora e publica** bem qualquer uma
delas; onde ele cede é sempre depois — na **condução** do certame.

### 3. Onde a dificuldade pertence legitimamente ao domínio (D1)

Imutabilidade e Retificação; segregação de funções; a distinção entre não declarar e negar recurso;
preliminar × definitivo; a impossibilidade de fechar resultado definitivo com prazo aberto; a
diferença entre a versão consolidada vigente e os documentos de cada ato; modalidades e reservas.
**Nada disso deve ser simplificado** — e o sistema já ensina quase tudo isso bem.

### 4. O que faria o sistema ensinar seu próprio modelo durante o uso

Generalizar quatro padrões que **ele já tem**: (a) declarar a consequência **no ponto da decisão**
(como faz na forma da Etapa) — aplicando-a ao corte, ao peso e ao término das inscrições;
(b) explicar toda negativa e **dizer o que fazer** (como faz na homologação) — aplicando ao 404 e às
três telas que calam; (c) o renderizador normativo humano (como faz no público) nas telas de ato;
(d) manter "O que fazer agora" vivo **depois** da publicação.

### 5. Onde um servidor novo provavelmente travaria amanhã

1. **Na etapa 5**, diante de 28 controles e da palavra "marco" — o primeiro ponto de hesitação real.
2. **Na etapa 9**, ao descobrir que um campo "(opcional)" impede submeter.
3. **Na distribuição**, ao descobrir que precisa Retificar o Edital para começar a avaliar.
4. **Ao publicar o resultado**, se for o publicador institucional: ele **não tem caminho**.
5. **Na convocação** — e aqui ele não trava, ele **para**: não há caminho nenhum, e a mensagem manda
   fazer algo que a interface não oferece.

E há um lugar onde ele **não trava e deveria**: se o Edital for de sorteio ou tiver reserva de vagas,
ele conseguirá publicar — sem aviso algum — um ato imutável que o sistema depois não executa
(ACH-49, ACH-50, ACH-47). Travar ali seria o melhor serviço que o produto poderia lhe prestar.

---

> ## As cinco mudanças que mais aproximariam o produto de não precisar de manual
>
> 1. **Validar se o Edital é executável antes de publicá-lo.** Hoje é possível publicar — ato
>    imutável — um Edital sem marco classificatório, um sorteio que não publica seu método, e uma
>    reserva de vagas que o sistema não consegue apurar. A prosa da tela já explica todas essas
>    regras; falta a verificação que as aplica. É a mudança de maior retorno do produto inteiro.
> 2. **Fechar a cauda do processo.** Tornar a convocação alcançável e declarar, na etapa 5, que sem
>    regra de corte não há convocação. Hoje o arco termina antes do fim.
> 3. **Ligar a navegação à permissão.** Quem pode publicar o resultado precisa **ver** o caminho; e
>    toda negativa por vínculo precisa ser uma recusa nomeada, nunca um 404 mudo.
> 4. **Dar ao julgador o que ele julga** — por um ato de instrução com escopo por recurso, que
>    respeite a FR-105 — e **dar ao candidato o parecer** que a própria spec diz existir para ele.
> 5. **Declarar a consequência no ponto da decisão**, sempre — peso, término das inscrições, regra de
>    corte. O produto já faz isso admiravelmente na forma da Etapa e na tela de Comissão; falta
>    aplicar onde a conta chega mais tarde.
> — e confrontar as fontes normativas entre si (janela recursal × Cronograma, término × designação,
>    numeração × documento): o sistema é rigoroso dentro de cada fonte e cego entre elas.
