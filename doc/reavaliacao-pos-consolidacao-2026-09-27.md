# Reavaliação depois do ciclo da consolidação — completude, carga cognitiva e esforço operacional

**Data:** 27/09/2026
**Contra:** a `main` em `8dd4f942`, que já traz a `044` implementada, a `045`, a `046`, a `047`, a `048`
e as correções de 26/09 (#183, #185, #194)
**Linha de base:** a [auditoria de consolidação](auditoria-de-consolidacao-2026-09-26.md), para as
lacunas, e o [estudo de esforço de 21/09](estudo-esforco-de-cadastro-2026-09-21.md), para o esforço de
composição — o único lugar em que o esforço foi **medido**
**Método:** leitura de código, templates, specs e testes, e a estrutura de três Editais reais
extraída dos PDFs. **Nada foi executado**: nem servidor, nem suíte, nem percurso pela interface.
**Anexos:** as quatro frentes de investigação e a estrutura dos Editais, em
[`reavaliacao-pos-consolidacao-2026-09-27/`](reavaliacao-pos-consolidacao-2026-09-27/), com
`caminho:linha` para cada afirmação.

> **A pergunta.** Quanto o sistema evoluiu, na prática, desde a auditoria consolidada — em completude
> funcional, facilidade de operação e redução do esforço necessário para executar um processo seletivo
> real?
>
> **As duas lentes.** O sistema deve absorver a complexidade do domínio para que o operador não precise
> carregá-la. E crescer o Edital não deveria multiplicar proporcionalmente o trabalho manual.

**Sobre os números.** Só dois números de esforço deste documento são medidos: os do estudo de 21/09 e
as 101 interações que a `043` contou na etapa Perfis do 140/2025. Os demais são **estimativas por custo
unitário**, com a conta escrita nos anexos A e B. Servem para ordem de grandeza e para dizer o que cresce
com o quê — não para comparar decimais.

---

## A. Resumo executivo

**O sistema evoluiu muito em confiabilidade e pouco em esforço.** O ciclo teve seis entregas, e elas
se dividem em dois tipos:
- **Quatro fecharam coisas que o sistema afirmava ou publicava errado.** A `045` corrigiu o painel que
  dizia "nada a fazer". A `046` impede publicar o que não executa. A `047` corrigiu a página pública que
  calava o prazo. A `044` fez o documento exigido dizer o que o portal cobra.
- **A `048` deu conserto ao Edital publicado.**
- **Só uma mudou a escala do trabalho humano**: a `043`, duplicar Perfil, que chegou pouco antes da
  auditoria. A `044` completa a `043` do lado dos documentos.

**Os ganhos relevantes, em ordem de efeito:**
1. **Honestidade do sistema.** As superfícies que conduzem — o painel, a validação, a página pública e o
   documento — deixaram de afirmar o que não sabem. Isso reduz o risco de erro institucional, mas quase
   não reduz o trabalho.
2. **A etapa Perfis deixou de ser o gargalo da composição.** Cada Perfil irmão custa ~4 interações,
   contra ~33. No 140/2025 a etapa foi de ~530 para 101 interações medidas; no 28/2026, de ~215 para
   ~55 estimadas.
3. **O documento por modalidade ficou fiel e barato.** O documento de "todo PcD" é declarado uma vez, e
   não uma vez por Perfil: 112 → 7 linhas no 140/2025, por construção. Ainda não foi medido na tela.

**O que foi só incremental.** O Edital pequeno (78/2026) custa hoje o mesmo que em 21/09, ~150
interações: Cronograma, Documentos e Classificação respondem por dois terços, e nenhuma entrega os tocou.
Do lado da operação, nada mudou de escala. A Mesa, os atos por recorte e a convocação por pessoa são os
mesmos de antes do ciclo.

**Os maiores gargalos hoje:**

| # | Gargalo | O que acontece |
|---|---|---|
| 1 | **Não há caminho de produção** | Nenhuma natureza de Edital roda em produção: não há login institucional na gestão nem artefato de implantação (§C) |
| 2 | **A convocação** | A tela não tem porta de entrada. Cada titular é convocado à mão, com três formulários por pessoa, e todo desfecho obriga a reapurar antes da chamada seguinte |
| 3 | **A escala por recorte** | Ordem, corte, apuração e publicação são um ato por recorte: 64 recortes no 140/2025, e 64 documentos onde o Edital real divulga um |
| 4 | **A armadilha da ampla concorrência** | A tela sugere não declarar a Modalidade da ampla. Sem ela, a inscrição transforma todo candidato em cotista ou deixa o não cotista sem opção |
| 5 | **A Classificação multiplica por Perfil** | No fluxo que o assistente sugere, o duplicar não leva marcos, e o custo que a `043` tirou dos Perfis reaparece na etapa Classificação |
| 6 | **Famílias que ficam fora** | Cadastro de reserva sem vagas imediatas não convoca, e o barema e a verificação da autodeclaração acontecem fora do sistema |

---

## B. Matriz Auditoria → SPEC → resultado atual

Só as questões com efeito operacional.

| Problema identificado | SPEC(s) | O que mudou no código e no produto | Impacto operacional | Situação atual | Lacuna residual |
|---|---|---|---|---|---|
| O painel afirmava ausência que não media; o recurso novo era invisível; o `status` do Evento nunca derivava (C1–C6, RC-78…82) | `045`; #194 (RC-115) | Frase de ausência relativa ao alcance; admissibilidade no sinal; fase do Evento derivada das datas; `UX-002` retirado; `UX-001` virou aviso de composição | Com papéis separados, o painel deixa de mentir e o ruído permanente some | Fechado no código; falta o percurso com identidades segregadas | O sinal de ordem obsoleta (`UX-004`) abre o recorte errado; recorte sem ato e apuração obsoleta não sinalizam (anexo B §17) |
| Publicar o que não executa (RC-29, RC-30, RC-32, RC-72) | `046`; #194 (RC-113, RC-114) | Impede Perfil sem marco ou sem corte e Etapa sem Resultado quando o fluxo o exige; a fonte de demonstração saiu de produção; o Edital publicado não roda mais o juízo de publicação | Menos Edital publicado sem saída | Fechado, e a primeira versão teve dois defeitos corrigidos no mesmo dia | O piso por Perfil subiu: 4 escolhas sem padrão a mais por marco, e uma linha de impedimento por Perfil na Revisão. A forma de convocação "não declarado" publica sem achado e só falha na hora de comunicar (anexo D, P1.3) |
| Documento exigido por modalidade infiel e caro; a Mesa recalculava a lista (RC-52, RC-53, AX-10/14/17) | `044` | Recorte pelo código da Modalidade em todos os Perfis; lista exigida gravada no envio e lida pela Mesa, pela consulta e pelo portal | Documentos O(D) em vez de O(P×D); a leitura das inscrições antigas não muda de repente | Fechado, mas os números de redução não foram medidos na tela | O código da Modalidade virou identidade do Edital e não se retifica; o seletor mostra P×M pares; condição sobre o candidato segue sem forma (decisão D2) |
| Edital publicado sem conserto — Modalidade, janela, corte, reversão, critério (RC-37, RC-38) | `048` | A Retificação acrescenta os cinco objetos que o contrato já permitia | O Edital deixa de exigir cancelar e republicar | Fechado para frente: quem já se inscreveu não muda de Modalidade | Tudo **item a item**, e a spec proíbe o lote (FR-802): esquecer a ampla na origem e copiar para 16 Perfis custa ~160 interações para retificar |
| Esforço de composição por Perfil (estudo E1/E3; RC-07) | `043` | Duplicar Perfil | Perfis: −75% no médio, −79% no grande | Parcial | As cópias só levam marcos se a origem já os tiver (§E); cópias independentes, sem "aplicar a todos"; Revisão e Retificação continuam O(P) |
| Página pública calava o prazo recursal e o desfecho (RC-48, RC-116, RC-117) | `047` | O prazo recursal público sai da mesma função da interposição; o desfecho do Edital e o histórico dos resultados aparecem | O candidato vê o prazo sem entrar na área dele | Fechado | Quatro perguntas de domínio registradas e sem decisão (RC-118…121); o título da página ainda é o do Processo, e as concorrências não mostram quantidade (RC-47) |
| `ValorDeFato` com uma camada; "O que mudou" sem o recorte (RC-101, RC-39) | #183, #185 | Gatilho e guarda de modelo; o recorte do documento no resumo público | Integridade e transparência | Fechado | O "O que mudou" ainda cala 45 dos 84 campos retificáveis (RC-111) |
| Cadastro de reserva sem vaga imediata (RC-58) | nenhuma | — | — | **Aberto** | Convocar exige vaga faltante; `reserveType`, `reserveLimit` e `callRules` são publicados e não executados |
| Autenticação e implantação (C7, RC-92, RC-124) | nenhuma | — | — | **Aberto** | Nada roda em produção |
| Trabalho por Perfil e polo (RC-61) | nenhuma | — | — | Aberto | A distribuição automática ignora o Perfil, e a tabela não tem coluna de Perfil |
| Barema e verificação da autodeclaração (RC-64, RC-65) | nenhuma — decisão de alvo pendente (DP-10) | — | — | Aberto | A banca soma o barema fora e digita o total; a verificação acontece fora |
| Reuso com estado de revisão (RC-43) | nenhuma | — | — | Aberto | O reuso copia a prosa inteira, sem marcar o que falta revisar; o custo do reuso nunca foi medido |

---

## C. Completude ponta a ponta

**Antes de qualquer diferença de domínio: nada roda em produção.** A gestão só identifica pelo seletor de
demonstração, e a produção recusa subir com ele (`config/settings/production.py:87-91`). A classe de
autenticação institucional que a produção exige não existe no repositório. `wsgi.py` e `asgi.py` caem em
`development` quando falta a variável, e a única imagem é de desenvolvimento (RC-124). O correio é o
único fator de acesso do candidato. **A tabela abaixo vale para um piloto assistido fora de produção.**

| Natureza (Editais da amostra) | Classificação | Onde a continuidade se rompe |
|---|---|---|
| **Curso FIC por sorteio, vagas remanescentes** (78, 59, 77) | completo com dependências externas | O sorteio só aceita Loteria Federal, e o Edital como o Cefor escreve hoje não é esse método (D-G3). As listas "resultado da análise documental" e "homologação das matrículas" não são atos do sistema. A matrícula sai em arquivo com código de curso, turno e polo vazios, e a importação no destino nunca foi feita |
| **Pós EaD multipolo com cotas e verificação da autodeclaração** (28, 149, 35) | parcialmente suportado | Não existe verificação da autodeclaração nem recurso à comissão própria; a Etapa vale para o Edital inteiro; a Modalidade não muda depois do envio, e "sai da PPI e fica na AC" só entra por desfecho de convocação com fundamento digitado |
| **Cadastro de reserva UAB com títulos** (140, 173) | **impossível sem trabalho externo** | Com 0 vagas, convocar é recusado por falta de vaga (`ocupacao/domain/apuracao.py:265-287`; `convocacao/application/convocar.py:249-297`). O barema fica fora, e faltam submodalidades, ordem intercalada entre listas e validade de dois anos |
| **Orientadores com títulos, entrevista e cascata de grupos** (14) | parcialmente suportado | Títulos, entrevista, média e desempate funcionam; a cascata 1→2→3 não existe |
| **Unificado de aperfeiçoamento** (57) | parcialmente suportado | A mesma ruptura da pós multipolo |
| **Técnico subsequente com cadastro de reserva, inscrição pelo SIGAA** (76) | **impossível sem trabalho externo** | A inscrição acontece fora, e não há como trazê-la (P-8; decisão sem carga retroativa); o cadastro de reserva sem número cai no RC-58 |
| **Chamada pública com reserva sobre poucas vagas e entrega presencial** (69) | completo com dependências externas | Conferência presencial e procuração ficam fora; o sistema registra o desfecho |

**Onde o sistema ainda depende de algo externo, em qualquer natureza:**
- **Planilha ou cálculo fora:** o barema, somado fora e digitado como total; prazos em dias úteis,
  digitados.
- **Ferramenta externa:** a transmissão do sorteio; a publicação nos sítios do Ifes e do Cefor (a
  convocação "por publicação" pede que se digite onde ela foi publicada); a importação no Registro
  Acadêmico.
- **Execução administrativa fora:** a verificação da autodeclaração; a vinculação UAB/CAPES; os fatos
  pós-matrícula (AVA, primeira semana), que voltam como atestado, por pessoa.
- **Conhecimento tácito:** para o candidato ver e recorrer do resultado documental, a Etapa documental
  precisa estar enumerada no marco publicado (`recursos/application/interpor.py:302-318`). Isso não está
  dito na composição.

**Funcionalidades que existem, mas não formam fluxo:**
1. **A convocação não tem porta.** Nenhuma tela da gestão leva a ela: nem a página do Edital, nem os
   destinos do marco, nem a ocupação. Só se chega digitando o endereço com o identificador do recorte, e
   é assim desde a `019` (`bcc8b9f1`). **Nenhuma auditoria anterior registrou isso.**
2. **O sinal de ordem obsoleta (`UX-004`) abre o recorte errado:** encaminha sem `?lista=`, e a tela abre
   a ampla (`interface/supervisao.py:986`).
3. **A primeira passada por marco × recorte é de memória.** Recorte sem ato não é sinal, e a página do
   Edital lista marcos, não recortes.
4. **Toda mudança de fato envelhece a apuração**, e convocar com apuração obsoleta é recusado. O painel
   não sinaliza apuração obsoleta; o operador descobre na recusa.
5. **Recortes do sorteio ≠ recortes da ocupação** (RC-73).
6. **A exportação "resultado" leva todo classificado** — num sorteio, todo inscrito —, e a opção se
   identifica só pela data. A exportação certa ("convocados") exige convocar cada titular.
7. **Encerrar não confere a cauda:** convocação em aberto, recurso pendente e apuração obsoleta não
   impedem nem avisam. E encerrar o Processo não fecha as inscrições dos Editais dele (RC-118).
8. **`reserveType`, `reserveLimit` e `callRules` são publicados e nunca executados.**

---

## D. Carga cognitiva e conhecimento de domínio

**A resposta curta.** Quem conhece o Edital compõe sozinho um Edital de ampla concorrência pura. **Não
compõe corretamente** um Edital com cotas, sorteio ou convocação sem saber quatro coisas do modelo que
a tela não diz no momento da decisão.

### D.1 Onde o sistema passou a orientar

- **Ausência honesta e prévia antes do ato irreversível** em todas as superfícies de condução: o
  painel, a publicação, a distribuição e a exportação.
- **A fase do Evento** (`045`) e **a situação pública do Edital** (`047`) são derivadas, e o operador
  não precisa mantê-las.
- **O `como-preencher` de cada etapa, a forma da ordem que abre o marco** (só se pergunta sobre sorteio
  quando há sorteio) e **a combinação que só aparece com duas ou mais Etapas.**
- **O marco nasce com código e denominação vindos do Perfil**, com arredondamento padrão; o período de
  inscrições é marcado num Evento, e não digitado; a linha geral do quadro é derivada.
- **As recusas nomeiam a saída e, quando cabe, a capacidade a pedir** (`037`, `045`).
- **A `046` antecipa para a Revisão** o que antes só aparecia na consolidação ou na convocação.

### D.2 Onde o operador ainda precisa "pensar como o banco de dados"

1. **A ampla concorrência tem três formas.** São a linha geral, a Modalidade "AC" declarada e o
   ponteiro que diz qual delas é a ampla. A tela sugere não declarar: *"Nenhuma — a ampla concorrência é
   só a linha geral"* (`_perfil.html:195`). Mas a inscrição só oferece as Modalidades declaradas
   (`inscricoes/application/rascunho.py:278-315`):
   - com **uma** cota declarada, todo inscrito vira cotista daquela cota;
   - com **duas ou mais**, quem não é cotista não tem o que escolher.

   A validação só avisa, e fala do quadro, não da inscrição. **É a causa do RC-37**, que a `048`
   conserta depois, pela Retificação, uma Modalidade por Perfil.
2. **Para convocar, é preciso declarar um corte**, mesmo quando nada é cortado: um corte que "não
   governa Etapa alguma", com alvo, empate e continuação. Desde a `046`, isso é impeditivo por Perfil.
3. **A forma de convocação "não declarado" publica sem achado** (`validation.py:1011-1013`), e a
   comunicação é recusada depois, mandando retificar.
4. **A Etapa decisória nasce não eliminatória**, e a consolidação sempre recusa essa combinação.
   "Nota mínima (opcional)" é obrigatória quando a Etapa é pontuada e eliminatória.
5. **O marco de sorteio faz perguntas sem efeito.** "Empate na última posição" é obrigatório numa ordem
   que não empata. O instante da ocorrência é digitado no formato RFC 3339, com fuso. A normalização e a
   substituição pedem a regra e também a prosa dela.
6. **Uns 15 campos não se corrigem depois de publicados, e nada avisa na composição.** Entre eles estão
   o código da Modalidade — que desde a `044` é a chave do recorte entre Perfis — e o **Tipo do Evento**,
   texto livre que nada lê (`mutabilidade.py:423-427`; `inscricoes/domain/periodo.py:7`).
7. **A operação é por recorte, e ninguém diz quais recortes faltam** (§E).
8. **Ordem e vocabulário.** O Anexo é cadastrado na etapa 7, mas vinculado ao documento na etapa 6. O
   selo "Classificação concluída" acende com um marco em qualquer Perfil, e a publicação exige marco e
   corte em todos. "Marco" também nomeia Evento do Cronograma na Supervisão, e "Geração" também nomeia o
   arquivo exportado.

### D.3 O que poderia virar inferência, contexto ou default

Em ordem: das decisões que o operador não tem como acertar sozinho para as de menor peso.

| Hoje o operador decide | Poderia ser | Por quê |
|---|---|---|
| Se declara a ampla como Modalidade | **Ampla implícita** na inscrição sempre que o Perfil tiver linha geral com vagas; ou impedimento que diga a consequência na inscrição | É a decisão com pior consequência e menos pista na tela |
| A forma de convocação, por Perfil | **Declarada uma vez no Edital** e herdada pelos Perfis, cobrada na publicação quando há corte | O Edital a declara uma vez |
| "Eliminatória" na Etapa decisória | **Pré-marcada**; "Avaliações por inscrição > 1" escondido; "classificatória" derivada de o marco enumerar a Etapa | A combinação padrão hoje é a que nunca consolida |
| O corte do marco final ou único | **Default de contexto**: alvo "o que o quadro publicar", sem Etapa governada, 0 suplentes; empate oculto no sorteio | Hoje o operador declara um corte para dizer que não corta |
| O instante e a prosa do sorteio | **Instante tirado do Evento** do Cronograma; prosa gerada da regra escolhida | Já está declarado em outro lugar |
| Os critérios de desempate como tipos | **A língua do Edital** ("maior idade" cria o fato da data de nascimento), com fatos filtrados pelo Perfil | O seletor oferece P×F fatos, e a publicação recusa os de outro Perfil |
| O quadro de vagas | **Sugerido pelo percentual** (o piso e o teto já são calculados em `validation.py:2934-2960`) | Hoje o operador faz a conta e o sistema confere |
| Quais campos são definitivos | **Marcados na composição** | Hoje só a tela de Retificação os lista |

---

## E. Esforço operacional — o mapa dos loops humanos

P = Perfis ou polos; M = Modalidades por Perfil; R = recortes (≈ P × (M+1)); C = inscritos;
Cv = convocados; E = Eventos; D = documentos; N = Perfis afetados por uma correção.

### E.1 Composição

| Operação | Unidade de repetição | Escala hoje | Lote ou reuso? | Impacto em Edital grande |
|---|---|---|---|---|
| Criação, Identificação, método comum do sorteio, 7 seções, atos de publicação | — | O(1) | — | nenhum |
| Perfis irmãos | Perfil | O(P) × ~4 | **duplicar (`043`)** | baixo |
| Divergências entre irmãos (4 blocos de requisito no 140/2025) | Perfil divergente | O(P_div × campos) | nenhum "aplicar a todos" | médio |
| **Marco + critérios de desempate** | **Perfil** | **O(P × (12 + 5C)) seguindo a ordem do assistente**; O(1) se o operador compuser o marco antes de duplicar | duplicar, **só se a origem já tiver marco** (`views.py:2092-2097`), e ele nasce na etapa 5 | **o maior loop restante: ~400 interações no 140/2025; ~1.650 num Edital de 66 Perfis** |
| Eventos do Cronograma (e datas no reuso) | Evento | O(E), ~5 cada | nenhum | médio, não depende de P |
| Documentos exigidos | documento | O(D) no recorte transversal; O(P×D) no exato | **recorte transversal (`044`)** | baixo, se usado |
| Documento sob condição do candidato | — | sem forma | — | infidelidade |
| Leitura da Revisão | Perfil, marco | O(P), O(P×M): sete famílias por Perfil | agrupamento só de Evento e Etapa | alto: o impedimento se perde entre dezenas de linhas |
| Retificar dado comum (atribuições, percentual, critério, denominação) | Perfil | **O(N)** | nenhum; a `048` também é item a item (FR-802) | alto: ~160 interações para acrescentar a ampla a 16 Perfis |
| Restaurar o rascunho local | Perfil × Modalidade | a perda cresce com P×M (RC-08) | — | risco |

### E.2 Operação

| Operação | Unidade de repetição | Escala hoje | Lote ou reuso? | Impacto em Edital grande |
|---|---|---|---|---|
| Comissão e alocação | membro, membro × Etapa | O(1) | **lote**: colar a lista; matriz | nenhum |
| Distribuição | Etapa | O(E) | **rodízio automático** | nenhum, **exceto** banca por curso ou polo: O(C) manual, sem coluna de Perfil |
| Mesa (análise e pontuação) | inscrição × Etapa × documento | O(C·E·D) | unitário, e irredutível: é decisão sobre uma pessoa | o maior custo absoluto; com o barema fora, 10–20 min por inscrição |
| Consolidação | página de 25 | O(C/25) | lote **paginado** | 24 rodadas com 600 inscrições |
| Sorteio | recorte | O(R): publicar relação e sortear, por recorte | a tela lista os recortes juntos, com um botão por recorte | médio |
| Ordem, corte, apuração, publicação (preliminar e definitiva) | **recorte** | **O(R) × 4–5 atos por rodada** | nenhum | **alto: 64 recortes e 64 documentos no 140/2025**, contra um "Resultado preliminar" do Edital real |
| Recursos | peça | O(Rc), mais reemissão e republicação do recorte alcançado | unitário, e coerente | médio |
| **Convocação** | **pessoa — titular inclusive** | **O(Cv) × 3 formulários**: convocar, comunicar, desfecho — mais uma reapuração a cada rodada | nenhum; espécie, vencimento e fundamento digitados a cada chamada | **alto: 280 vagas → 460 a 1.270 formulários no 28/2026** |
| Exportação para matrícula | marco | O(M) | — | baixo, mas só é fiel com todos convocados |
| Retificação durante a operação | Perfil | O(N) | nenhum | alto |

**Onde o unitário é coerente, e onde não é.** O sistema é unitário onde a decisão é sobre uma pessoa
(Mesa, recurso, desfecho), e isso é coerente com "decisão tem autor". Há três casos em que o unitário
não protege decisão nenhuma:
- **A consolidação em páginas de 25:** a confirmação já declara o alcance, e paginar só multiplica
  cliques.
- **Um ato por recorte**, quando a decisão é do marco: a mesma pessoa confirma R vezes o mesmo gesto, em
  R telas.
- **Convocar o titular:** o código diz que isso "é formalizar o que o número já diz"
  (`convocar.py:252-257`). A faixa e a fila já decidiram quem é.

**Resposta à pergunta central.** Dobrar o Edital:
- **já não dobra a etapa Perfis;**
- **dobra a Classificação no fluxo que a tela sugere, a Revisão e toda Retificação de conteúdo comum;**
- **na operação, dobra os atos por recorte e, com as vagas, a convocação;**
- **não mexe no Cronograma, nos documentos e nos anexos**, que crescem com o tamanho do certame e não
  com o número de polos — mas nenhuma entrega os barateou.

---

## F. Comparação por cenários

### F.1 Composição

| | 78/2026 — pequeno | 28/2026 — médio | 140/2025 — grande |
|---|---|---|---|
| Estrutura | 2 turmas, sem Modalidade, 11 Eventos, sorteio, 7 documentos | 7 polos idênticos, 3 Modalidades, 18 Eventos, sorteio + verificação, 12 documentos | 16 códigos, 4 Modalidades, 13 Eventos, prova de títulos, cadastro de reserva, ~16 linhas de documento, 3 fatos de desempate |
| **21/09** | ~150 (medido) | ~390–480 (estimado) | ~825 (medido, com reuso e documentos infiéis); ~530 só na etapa Perfis |
| **Hoje, seguindo o assistente** | ~150–170 | ~250–310 | ~690 |
| **Hoje, compondo o marco antes de duplicar** | ~140 | ~200–250 | ~320 |
| O que domina hoje | Cronograma, documentos, Classificação — ~105 de ~155 | **Cronograma (~80)** | **Classificação (~400)**, se seguir a ordem |
| O que ainda cresce | nada relevante | Eventos, documentos | marcos e critérios por Perfil, Revisão, Retificação |

**Leitura.**
- **No pequeno, nada mudou.**
- **No médio,** a queda (−20% a −45%) vem toda da etapa Perfis e do recorte transversal.
- **No grande,** o total só cai à metade se o operador descobrir sozinho que deve compor o marco antes
  de duplicar. A tela não sugere isso, e o texto de ajuda do duplicar promete levar os marcos.

### F.2 Operação

As faixas de inscritos são supostas, porque nenhum dos três Editais estima demanda.

| | 78/2026 (C ≈ 50–100) | 28/2026 (C ≈ 300–800) | 140/2025 (C ≈ 200–500) |
|---|---|---|---|
| Atos no sistema | ~150–420 | ~900–2.200 | ~550–1.700 |
| Mesa | 50–100 conclusões | 250–550 | 200–500, com o barema somado fora |
| Recortes | 2 | 21 | **64** |
| Convocação | 75–250 formulários | **460–1.270** | **não executável** (RC-58) |
| O que domina | Mesa ≈ convocação | Mesa ≈ convocação; navegação por 21 recortes | Mesa com barema fora, de longe; depois os 64 recortes |
| Fora do sistema | transmissão do sorteio, homologação da matrícula, importação no destino | verificação da autodeclaração (70–175 entrevistas), idem | barema, verificação, toda a cauda de dois anos do cadastro de reserva |

---

## G. Lacunas atuais

Só as que continuam fazendo sentido diante do sistema de hoje.

| # | Problema real | Quem é afetado | Frequência | Como escala | Impede fluxo? | Mais conhecimento? | Mais esforço? |
|---|---|---|---|---|---|---|---|
| G1 | **Sem caminho de produção**: login institucional da gestão, artefato de implantação, correio institucional | todos | todo Processo | — | **sim, todos** | — | — |
| G2 | **A convocação sem porta, por pessoa e com reapuração** | gestão | todo Edital que convoca | O(3·Cv) + rodadas | na prática, sim: a tela só abre pelo endereço | sim | **alto** |
| G3 | **A ampla concorrência como ausência**, e a inscrição que força cotista | candidato e gestão | todo Edital com cota | a correção custa O(P) retificações | produz inscrições erradas, e não tem desfazer | **sim, o maior** | alto na correção |
| G4 | **A operação por recorte**, sem sinal dos recortes pendentes, e com um documento por recorte | presidência, publicador | todo Edital com cotas ou vários Perfis | O(P×M) × 4–5 atos | não; é frágil | sim | **alto** |
| G5 | **Marcos e critérios por Perfil**, com o duplicar dependente da ordem; Revisão e Retificação O(P) | elaboração | Editais multipolo (4 de 5 da amostra) | O(P) | não | sim (a ordem é tácita) | **alto** |
| G6 | **Cadastro de reserva sem vagas imediatas** | famílias UAB e técnico | frequente no Cefor | — | **sim, a cauda inteira** | — | — |
| G7 | **O "O que mudou" cala 45 dos 84 campos** (RC-111) | candidato | toda Retificação desses campos | — | não; é transparência (FR-130) | — | — |
| G8 | **Barema e verificação da autodeclaração** fora do sistema | banca, comissão | famílias de títulos e de cota racial | O(C × itens) fora | parcial | — | alto, fora |
| G9 | **Consolidação em páginas de 25; distribuição sem Perfil** | presidência | Editais grandes; bancas por curso | O(C/25); O(C) | não | — | médio |
| G10 | **Restaurar o rascunho local perde coleções** (RC-08, a validar) | elaboração | quando usado | P×M | não; é perda silenciosa | — | médio |

---

## Complexidade transferida e over-engineering

Não parto da premissa de que as specs foram boas decisões. Mas também não chamo de over-engineering o
que se justifica: o congelamento do sorteio, a separação entre julgar e ver a prova, a imutabilidade e as
derivações da `045` e da `047`.

1. **Validar na publicação em vez de impedir na origem (`046`).** O contrato decide, na publicação, se
   a Etapa pode ser publicada conforme quem consome o Resultado: quatro consumidores, a decisória como
   "porta". A primeira versão errou num caso no mesmo dia (RC-114). É sinal de que a validação por
   inferência de uso se acumula mais rápido do que se entende. A saída mais simples seria **nascer
   certo**: defaults na Etapa e no marco (§D.3) reduzem o que a publicação precisa adivinhar.
2. **O recorte transversal é o catálogo da `039` por convenção de digitação (`044`).** Para não mover a
   Modalidade para o Edital, o código digitado virou identidade entre Perfis, com impeditivo de
   denominação idêntica. Resolve os documentos, mas o operador passa a precisar saber que o código é
   chave e não se retifica — e a tela não diz isso na composição.
3. **Conserto depois em vez de prevenção antes (`048`).** A Retificação aditiva é necessária, mas o caso
   típico que ela conserta — a ampla esquecida na origem e copiada para 16 Perfis — é produzido pela
   própria composição (G3) e custa ~160 interações. Prevenir custa uma decisão de modelo.
4. **O duplicar produz N cópias independentes (`043`).** Economiza a digitação e transfere o custo para
   a manutenção: a Revisão, a Retificação e o PDF continuam O(P), e o risco de divergência entre cópias
   aumenta.
5. **Estrutura sem consumidor.** `calculation`, `rounding`, `distribution` e `callRules` da regra
   normativa são gravados, publicados e não retificáveis, sem tela nem leitor. `reserveLimit` é
   publicado e não tem efeito. É complexidade que o operador vê, ou que o documento afirma, sem nenhuma
   consequência. **Ou se executa, ou se para de pedir e de publicar.**
6. **Flexibilidade maior que a dos Editais.** Forma de convocação, reversão, desempate e método são
   declarados por Perfil ou por marco, quando o Edital real os declara uma vez. Os achados externos
   registram que "a cláusula do corte é idêntica, palavra por palavra" em toda a família de sorteio.
7. **A superfície de validação cresceu:** cerca de 95 construtores de achado em `validation.py`. Não é
   defeito em si, mas é o lugar onde cada nova regra aumenta o que a Revisão mostra por Perfil.

---

## Priorização — máxima alavancagem, não máxima cobertura

Cada item segue o formato **problema → evidência → intervenção mínima → ganho**. Nada aqui é spec
numerada.

> **Depois da avaliação desta priorização, em 27/09, a ordem mudou.** A ampla saiu da fila de specs e
> virou correção; operar por marco foi partido em duas, e a metade que não mexe no ato público veio antes
> da convocação; e entrou um teste operacional antes de qualquer spec estrutural. A ordem adotada, o
> critério e as decisões que ela abriu estão em
> [decisões pendentes, "Depois da reavaliação"](decisoes-pendentes-da-consolidacao.md#depois-da-reavaliação-de-2709).
> O texto abaixo fica como estava, salvo a correção marcada no item 4.

### 1. Declarar uma vez no Edital o que o Edital declara uma vez, e materializar por Perfil

- **Problema.** Marco, critérios de desempate, forma de convocação, reversão e janela recursal são
  declarados por Perfil. O duplicar só ajuda se a ordem for invertida, e toda correção de conteúdo comum
  custa O(N).
- **Evidência.** Classificação ~400 no 140/2025 e ~1.650 num Edital de 66 Perfis (§E.1); a Retificação
  ~160 para a ampla nos 16 Perfis; a Revisão com sete famílias por Perfil.
- **Intervenção mínima.** "Aplicar a todos os Perfis" — a TF-1 que a `043` registrou — na etapa
  Classificação e na Retificação, **e** valores padrão no nível do Edital para o que não é cota. Uma ação
  humana gera N materializações, e cada Alteração continua registrada.
- **Compatibilidade.** Não contradiz a decisão de 25/09, porque as Modalidades e as quantidades de cota
  continuam por Perfil. O que se move é a declaração dos padrões do certame, que a própria decisão de
  25/09 deixou em aberto (E2).
- **Ganho.** A Classificação, a Retificação de dado comum e boa parte da Revisão passam de O(P) para
  O(1). É o que fecha a proporcionalidade que a `043` só abriu.

### 2. A convocação como fluxo, e não como formulário por pessoa

- **Problema.** A tela não tem porta; o titular é convocado à mão, com três formulários por pessoa; cada
  desfecho obriga a reapurar.
- **Evidência.** Anexo B, §9 e §17; `convocar.py:252-257`; 460 a 1.270 formulários no 28/2026.
- **Intervenção mínima.**
  - **Correção direta, sem spec:** o link da ocupação e da página do Edital para a convocação.
  - **Com spec:**
    - convocar os titulares da faixa num ato só, que é formalização e não decisão;
    - espécie e vencimento derivados do Edital;
    - a apuração seguinte emitida junto com o desfecho que a envelhece, ou derivada.
- **Ganho.** A convocação passa de O(3·Cv) para O(desfechos), e o fluxo deixa de depender de digitar o
  endereço.

### 3. Operar por marco, e não por recorte

- **Problema.** Ordem, corte, apuração e publicação são um ato e um documento por recorte, e ninguém diz
  quais recortes faltam.
- **Evidência.** `divulgacao/models.py:52-56` ("três atos raiz num marco exigem três publicações"); 64
  recortes no 140/2025; `supervisao.py:842-846`.
- **Intervenção mínima.**
  - Emitir e publicar todos os recortes de um marco num ato, gerando um documento por marco. A tela do
    sorteio já lista os recortes juntos.
  - Um indicador "recortes deste marco: ordenados, cortados, apurados, publicados".
  - **Correções diretas, sem spec:** o `?lista=` do `UX-004` e a consolidação sem paginação.
- **Ganho.** A operação passa de O(P×M) para O(marcos), com um documento público como o Edital real.

### 4. A ampla concorrência como padrão, e não como ausência

- **Problema.** A tela sugere não declarar a ampla, e a inscrição força o candidato para uma cota.
- **Evidência.** `_perfil.html:195`; `rascunho.py:278-315`; é a origem do RC-37 e do custo de ~160
  retificações da `048`.
- **Intervenção mínima.** A inscrição oferece a ampla sempre que o Perfil tiver linha geral com vagas —
  um recorte nulo escolhível. **Ou**, se isso contrariar alguma decisão, a publicação impede com a
  consequência dita na inscrição.
- **Decisão necessária** — *corrigido em 27/09*. A primeira redação dizia que a correção dependia de
  decisão por tocar a FR-039 e a FR-040 da `009`. Não depende: a FR-039 já permite apresentar a ausência
  de reserva como ampla concorrência sem entidade gravada, e a `048` registra o defeito como achado A-1
  (*"Assumir sem perguntar é o achado A-1, e não desta feature"*). O que resta decidir é a condição em
  que a ampla é oferecida (`DP-14`).
- **Ganho.** Elimina a armadilha de maior consequência e a decisão que o operador não tem como acertar,
  e torna a `048` exceção, e não rotina.

### 5. O caminho de produção

- **Problema.** Nada roda em produção.
- **Evidência.** §C; RC-92; RC-124.
- **Intervenção mínima.**
  - **Correção direta:** `wsgi` e `asgi` caindo na produção, que recusa subir mal configurada.
  - **Decisão institucional:** quem empacota e serve, e qual é o provedor de identidade.
  - **Spec:** o adaptador de autenticação da gestão, com a origem dos papéis, e o SMTP institucional
    com a resiliência do código de acesso.
- **Ganho.** É a condição para qualquer ganho acima valer num processo real.

### Correções diretas, sem spec

Restauram requisito escrito ou fecham uma porta que falta:
- o link da convocação;
- o `?lista=` do `UX-004`;
- a consolidação sem paginação;
- o dicionário do "O que mudou" completo, com um teste guardião contra o contrato de mutabilidade
  (RC-111, FR-130 da `024`);
- o padrão de `wsgi`/`asgi`;
- o texto de ajuda do duplicar dizer que os marcos só vêm se já estiverem gravados;
- marcar na composição os campos que não se retificam.

### O que seria over-engineering agora

- **Barema genérico, verificação da autodeclaração completa, cascata e submodalidades** antes de a
  família entrar no alvo (DP-10). A Constituição, no §V, pede nada de estrutura antes de haver Edital que
  a consuma.
- **Notificações internas** antes da identidade real.
- **Novos painéis ou métricas** antes de operar por marco.
- **Estado de revisão do reuso campo a campo.**
- **Modelos de Edital por família** — a "origem controlada" que a Constituição admite — **antes** dos
  padrões no nível do Edital. Um modelo que materializa por Perfil apenas congela a repetição de hoje.
  Depois do item 1, ele fica barato e útil.

---

## Respostas às questões obrigatórias

1. **O sistema está significativamente mais fácil de operar?**
   - **Mais confiável, sim, significativamente:** as superfícies que conduzem deixaram de afirmar o que
     não sabem, e a publicação barra o que não executa.
   - **Mais fácil, só na composição de Editais multipolo,** e só na etapa Perfis. O Edital pequeno e a
     operação pós-publicação custam o mesmo que antes do ciclo.

2. **Quanto ainda depende de conhecimento do modelo interno?** Pouco para a ampla concorrência pura, e
   muito para cotas, sorteio e convocação. Há quatro decisões que a tela não explica no momento certo
   (§D.2, itens 1–4), uns 15 campos definitivos sem aviso, e uma regra de ordem tácita: compor o marco
   antes de duplicar.

3. **Um Edital maior ainda cresce linear ou pior?**
   - **Linear em P:** Classificação (no fluxo sugerido), Revisão e Retificação de dado comum.
   - **Linear em P×M:** os atos e documentos por recorte.
   - **Linear em vagas, com fator 3:** a convocação.
   - **Linear em C:** a Mesa, e aí é irredutível.
   - **Nada pior que O(P×M)** foi encontrado.

4. **Quais loops foram eliminados?** A criação de Perfis irmãos (`043`), os documentos por Perfil para
   condição de modalidade (`044`), a manutenção manual do estado do Evento (`045`) e a repetição do
   método do sorteio, este desde a `030`.

5. **Quais loops importantes permanecem?** Marco e critérios por Perfil; Retificação por Perfil;
   Revisão por Perfil; ordem, corte, apuração e publicação por recorte; convocação por pessoa com
   reapuração; consolidação em páginas de 25; distribuição manual quando a banca é por curso; e Eventos
   do Cronograma sem lote.

6. **Quais naturezas são executáveis de ponta a ponta?** Nenhuma em produção. Fora dela, num piloto
   assistido:
   - **completas com dependências externas:** curso FIC por sorteio e chamada com entrega presencial;
   - **parciais:** pós multipolo com cotas e verificação, unificado de aperfeiçoamento e títulos com
     cascata;
   - **impossíveis sem trabalho externo:** cadastro de reserva sem vagas e inscrição feita fora.

7. **Onde ainda recorremos a ferramentas ou procedimentos externos?**
   - barema;
   - verificação da autodeclaração;
   - cadastro de reserva;
   - prazos em dias úteis;
   - publicação nos sítios do Ifes e do Cefor;
   - transmissão do sorteio;
   - importação no Registro Acadêmico;
   - vinculação UAB;
   - fatos pós-matrícula;
   - atendimento ao candidato.

8. **Quais lacunas antigas já não faz sentido atacar?**
   - **Resolvidas pelo ciclo:** a visão global como "outro painel", a validação que atacaria a classe
     inteira do E-4, a Retificação sem porta de acréscimo, a derivação do `status` do Evento e o
     documento por modalidade.
   - **Continuam não valendo o custo agora:** as famílias fora do alvo (DP-10), notificações internas e
     a métrica de condução.
   - **Contraditas:** o catálogo de Modalidades da `039`.

9. **As últimas specs simplificaram o produto?** Simplificaram o que o sistema **afirma**, e aumentaram o
   que o operador precisa **entender**. Três padrões merecem ser reconsiderados:
   - validar na publicação em vez de nascer certo;
   - consertar depois em vez de prevenir, com a `048` item a item, sem lote, e a FR-802 vedando
     mecanismo novo de acréscimo;
   - estrutura publicada sem consumidor (`callRules`, `reserveLimit`).

   Não é over-engineering generalizado. É o custo acumulado de resolver cada achado no ponto em que ele
   apareceu, em vez de na origem.

10. **Se fizéssemos só mais 3 a 5 intervenções?**
    - Declarar uma vez no Edital e materializar por Perfil (item 1).
    - A convocação como fluxo (item 2).
    - Operar por marco (item 3).
    - A ampla como padrão (item 4).
    - O caminho de produção (item 5), que é condição e não ganho.

    Os três primeiros são os que mudam a escala do trabalho humano; o quarto é o que mais reduz o
    conhecimento exigido.
