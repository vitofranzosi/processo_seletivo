# Auditoria de consolidação — o que falta para o sistema servir a um certame real

**Data:** 15/10/2026
**Base:** a `main` em `db428b30` (merge do #282, 14/10), na worktree `auditoria-consolidacao-sistema-1b65b5`,
sincronizada com `origin/main`. O PR #283 (implementação da `073`) estava aberto e não entra na base.
**Ambiente:** macOS, PostgreSQL local, Python 3.13 com `uv`, grupos `dev` e `assistente` instalados.

**Entregáveis:**

| | Documento | O que é |
|---|---|---|
| A | este relatório | síntese, método, panorama, lacunas, riscos e recomendação |
| B | [matriz de pendências](auditoria-de-consolidacao-2026-10-15/matriz-pendencias.md) | 172 itens canônicos com evidência, estado, prioridade e próxima ação |
| C | [rastreabilidade histórica](auditoria-de-consolidacao-2026-10-15/rastreabilidade-historica.md) | demanda → decisão → spec → implementação → testes → estado; o que se recuperou das sessões |
| D | [roadmap consolidado](auditoria-de-consolidacao-2026-10-15/roadmap-consolidado.md) | proposta em ondas, com dependências e conflitos a aprovar |
| E | manuais e documentação | as alterações estão listadas no [inventário documental](auditoria-de-consolidacao-2026-10-15/inventario-documental.md), §0 |
| F | [decisões pendentes](auditoria-de-consolidacao-2026-10-15/decisoes-pendentes.md) | 16 decisões que só uma pessoa pode tomar |

> **A pergunta.** O que ainda precisamos desenvolver, corrigir, consolidar ou documentar para que o
> Sistema de Processos Seletivos seja uma solução funcionalmente completa, consistente, confiável e
> adequada à operação institucional?

---

## 1. Resumo executivo

**O sistema é amplo, tecnicamente sólido e nunca foi usado por quem vai usá-lo.** Ele cobre o ciclo
inteiro de um certame:

- elaboração assistida do Edital, revisão, homologação, publicação imutável e Retificação com
  vigência;
- PDF oficial em linguagem simples;
- portal com vitrine, inscrição sem senha e documentos;
- comissão, Mesa de avaliação, consolidação e classificação por recorte;
- sorteio público auditável, corte, recursos e ocupação de vagas;
- convocação com suplência, Requerimento de Matrícula e exportação para o Registro Acadêmico;
- avisos aos candidatos por e-mail.

A suíte contra PostgreSQL fecha em **11 297 testes passando, 11 pulados deliberados e nenhuma falha**.
A jornada do candidato e as principais telas da gestão funcionaram de ponta a ponta no navegador
nesta auditoria. Mas:

1. **Ele não pode entrar em produção.** A gestão não tem autenticação institucional: o usuário
   escolheu LDAP em 28/08, e nada foi implementado. Sem o seletor de demonstração, `/gestao/`
   responde 503. Também não existe a política de retenção que o próprio usuário pôs como
   precondição, em 01/09, para receber dado real. São seis os **P0 para a implantação**, e todos
   começam por uma conversa com a TI, o encarregado de dados, o Cefor ou o setor de correio.
2. **Nada está validado com pessoas.** Nenhum dos 172 itens da matriz chega a "implementado e
   validado". O teste operacional assistido com o setor (DP-18) nunca foi feito, e o percurso com
   cinco candidatos da `072` está pendente. Ninguém de fora compôs um Edital, avaliou uma inscrição,
   realizou um sorteio ou ouviu o portal num leitor de tela.
3. **O desenvolvimento recente correu à frente da operação.** As últimas cinco specs (`070` a `074`)
   foram dedicadas ao assistente de dúvidas, que é piloto interno e protótipo. Enquanto isso,
   pendências de jornada básica seguem abertas:
   - o link "Edital completo" pode levar a um PDF sem a Retificação em vigor;
   - o texto do reenvio da convocação sugere prazo novo;
   - um recurso deferido antes do marco não alcança o corte.

   O manual de operação, planejado em 25 sessões, não teve nenhuma sessão de produção desde 08/09.
4. **Há trabalho em risco de perda.** A spec `074` e seu código existem só numa worktree local, sem
   commit. Uma chave de API exposta numa captura de tela em 14/10 não tem revogação confirmada.

**Maturidade: pré-piloto.** O produto está funcionalmente completo para um certame do tipo que ele
modela, e verificado tecnicamente, mas não está implantável e não foi validado com usuários.

**A recomendação** (detalhe na §12 e no roadmap) tem três frentes:

- **Decidir quando será o primeiro certame real** (DEC-01) e disparar já os pedidos institucionais,
  que têm prazo de semanas.
- **Fazer uma semana de validação com pessoas** (DEC-14), que não depende de produção.
- **Como próxima etapa de desenvolvimento, um lote de correções diretas e a spec curta do Edital
  vigente.** Nada de funcionalidade nova até a validação dizer onde as pessoas travam.

## 2. Escopo e metodologia

A auditoria seguiu as cinco fases pedidas.

1. **Inventário.** A estrutura do repositório (24 apps, 94 migrations, 116 rotas da gestão e 33 do
   portal, 74 pastas de spec), a documentação, o histórico do Git e do GitHub, e os registros de
   sessões acessíveis.
2. **Investigação retrospectiva.** Dezesseis investigações paralelas:
   - dez lotes de sessões anteriores;
   - specs 001–037 e 038–073 contra tarefas e código;
   - achados e auditorias em `doc/`;
   - varredura do código e da configuração;
   - GitHub;
   - inventário documental.

   Em seguida, cinco consolidações por área deduplicaram as cerca de 800 pendências brutas e as
   **conferiram contra a `main`**. Uma pendência "aberta" numa sessão antiga só entrou na matriz
   depois de verificada no código atual; as resolvidas ficaram num anexo da matriz, com a evidência
   da resolução.
3. **Validação funcional.** A suíte completa contra PostgreSQL. Um banco novo com `seed_demo`. Um
   percurso pelo navegador como candidata, Gestor/Publicador/Auditor e avaliadora, com um aviso
   confirmado e despachado. A largura medida em dez telas a 375 px.
4. **Documentação.** A Visão do Sistema revista até a `072`; a arquitetura do manual na Revisão 6; o
   README, o `AGENTS.md`, o `.env.example`, um runbook, um roteiro e um quickstart corrigidos onde
   contradiziam o código.
5. **Consolidação.** Matriz, rastreabilidade, roadmap e decisões.

Classificação de estado: os nove estados pedidos. "Validado" exige uso real ou validação humana
registrada. Teste automatizado verde, quando a spec pedia validação com pessoas, conta como "sem
validação suficiente".

## 3. Fontes efetivamente investigadas

| Fonte | Alcance | Como |
|---|---|---|
| Código | `backend/` inteiro: apps, rotas, settings, comandos, templates, testes | leitura e varredura; marcadores de provisório (zero `TODO`/`FIXME`; dois adaptadores provisórios de identidade) |
| Specs | as 74 pastas (`001`–`073`, `012-013`), mais a `074` local, só leitura | tarefas: 2793 de 2883 marcadas (001–037) e 1289 de 1323 (038–073); as abertas foram reconferidas no código |
| `doc/` | 44 achados, decisões, 14 auditorias e registros datados, manual | estado declarado × estado verificado |
| Git e GitHub | 282 PRs (279 mergeados, 2 fechados, 1 aberto), 1 issue, branches remotas, CI | corpos de PR varridos por frases de pendência; nenhum comentário de revisão existe (0 reviews) |
| **Sessões anteriores** | **185 transcrições do agente, de 28/08 a 15/10** (1,1 GB, todo o período do projeto), mais 111 respostas literais do usuário a perguntas estruturadas | digesto por sessão: pedidos do usuário, fala final de cada turno, recaps, follow-ups propostos; ≈ 735 decisões e ≈ 812 pendências brutas |
| Memória persistente do agente | 121 notas em `~/.claude/projects/…/memory/` | como contexto, conferido antes de usar |
| Sistema em execução | banco `ps_aud1015`, servidor de desenvolvimento, painel do navegador | §9 |
| Suíte | `make test-pg` completo | 11 297 passando, 11 pulados, 0 falhas, 1312 s |

## 4. Limitações da auditoria

- **Nenhum ator institucional foi ouvido.** TI, encarregado, Cefor, correio, Registro Acadêmico e o
  setor de seleção estão nesta auditoria só pelo que as sessões registraram deles. Tudo o que depende
  deles está na matriz como BLOQUEADO ou nas decisões pendentes.
- **Não há ambiente de produção.** Nada foi verificado em VM, nginx, systemd, SMTP real nem Ollama na
  L4. O 503 da gestão em produção foi verificado no código e no teste `tests/interface/test_lista.py:159`.
- **Sessões.** Os digestos levam a última fala de cada turno, e não o raciocínio intermediário. Há
  falas truncadas, duas transcrições vazias (das 187, 185 tinham conteúdo), sessões só operacionais e trechos repetidos por retomada de contexto.
  As respostas a perguntas de formulário foram recuperadas à parte (111). Mensagens que o usuário
  colou de um conselheiro externo foram tratadas como posição dele, com a marca "colado". Relatórios
  publicados como artifacts do claude.ai em sessões antigas não estão no repositório e não foram
  lidos.
- **Percurso pelo navegador.**
  - Ficaram de fora: a composição de um Edital do zero, uma Retificação, um sorteio, o corte, a
    convocação e o recurso pelo candidato. Esses estados existiam no `seed_demo` e foram lidos, mas
    não exercidos.
  - Os PDFs de teste foram anexados por `DataTransfer` no próprio formulário: é o mesmo POST de um
    upload, mas não o clique no seletor de arquivos.
  - Não houve leitor de tela nem celular real.
- **A `074` e os vídeos** foram lidos só por `git status` nas worktrees deles.
- **Libras e Ifes Ads** foram classificados quanto à maturidade, e não avaliados no mérito.

## 5. Panorama atual do sistema

| Dimensão | Estado |
|---|---|
| Ciclo do certame | Coberto do Edital à exportação para matrícula, em 19 fases (a arquitetura do manual as descreve na §B.2) |
| Integridade | Publicação imutável; 40 tabelas append-only com gatilho e privilégio ausente; trilha de auditoria append-only; segregação elaborar × homologar × publicar no código |
| Papéis | 8: Elaborador, Homologador, Publicador, Gestor, Julgador de recursos, Auditor, Exportador de matrículas, Participante do piloto do assistente. Presidência e avaliação vêm do vínculo com a comissão |
| Identidade | Candidato: código de 6 dígitos por e-mail, pronto para produção. Gestão: só o seletor de demonstração, que produção recusa |
| Integrações | SMTP (real), Loteria Federal/Caixa (real, sem contrato nem verificação periódica), base de CEP (local), LLM (opcional, piloto), Registro Acadêmico (arquivo, nunca importado) |
| Operação | Guia de implantação extenso, ensaiado em parte em 29/09; nada de systemd, servidor de aplicação nem backup versionado; `/health` e `/readiness` existem |
| Qualidade | 11 297 testes; CI verde, só contra PostgreSQL; sem proteção de branch e sem revisão de PR |
| Documentação | Visão do Sistema atualizada até a `072`; manual só planejado; guia de implantação atual, com a revisão do #283 pendente |
| Implantação | **Nenhuma.** O sistema existe só na máquina do responsável (premissa reafirmada pelo usuário em 14/10) |

## 6. Funcionalidades consolidadas

Implementadas, cobertas por teste e, onde está marcado, **exercidas no navegador em 15/10**.
Nenhuma está "validada" no sentido da auditoria, porque nenhuma passou por usuário real.

- **Portal público:**
  - vitrine com busca, filtros e situação de cada seleção ✔;
  - página da seleção com oferta, cronograma, documentos e Retificações ✔;
  - resultado público, relação e verificação do sorteio, com manifesto.
- **Candidato:**
  - acesso por código ✔ e "Seus dados" com finalidade declarada ✔;
  - inscrição com modalidade ✔ e envio de documento ✔;
  - Requerimento de Matrícula ✔;
  - revisão e envio ✔, comprovante com código de verificação ✔ e e-mail de confirmação ✔;
  - Minhas inscrições ✔ e acompanhamento pela situação ✔;
  - convocação e Requerimento pedido na convocação (`059`) e recurso.
- **Elaboração:** assistente de composição em nove passos, Perfis e quadro de vagas, Etapas e
  marcos, desempate, reaproveitamento de Edital, Revisão com impeditivos e advertências, PDF oficial
  em linguagem simples (`069`).
- **Aprovação e publicação:** submeter, homologar, publicar e retificar, com segregação de pessoas;
  autoridades da unidade (`060`).
- **Condução:**
  - inscrições recebidas, com CPF mascarado ✔ e documento auditado ✔;
  - comissão e alocação, distribuição e Mesa com painel de documento ✔;
  - consolidação, classificação e corte, sorteio e ocupação;
  - convocação com suplência, recursos com impedimento do julgador e exportação `.xlsx` para
    matrícula.
- **Supervisão:** Supervisão do Processo ✔, Visão Geral ✔, condução por marco.
- **Comunicação:**
  - avisos aos candidatos com prévia, destinatários tirados do ato e rodapé que diz que o aviso
    não substitui a publicação ✔;
  - despacho por comando, com o resultado por pessoa ✔;
  - modelos de aviso da unidade ✔.

A Visão do Sistema mantém o catálogo completo: 123 capacidades, cada uma com a sua evidência.

## 7. Lacunas identificadas

172 itens canônicos (de 217 registros, depois de fundir 45 repetidos entre áreas):

| Estado | Itens |
|---|---|
| IMPLEMENTADO E VALIDADO | 0 |
| IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | 20 |
| PARCIALMENTE IMPLEMENTADO | 25 |
| ESPECIFICADO E NÃO IMPLEMENTADO | 8 |
| IDENTIFICADO E NÃO ESPECIFICADO | 84 |
| BLOQUEADO | 10 |
| ADIADO FORMALMENTE | 20 |
| DESCARTADO OU SUBSTITUÍDO | 1 |
| NÃO CONFIRMADO | 4 |

| Prioridade | Itens | "para a implantação" |
|---|---|---|
| P0 | 6 | 6 |
| P1 | 30 | 8 |
| P2 | 77 | 1 |
| P3 | 59 | 0 |

**O padrão das lacunas** (o detalhe de cada uma está na matriz):

- **O que falta implementar** é pouco, e quase todo pequeno: autenticação, retenção, sessão,
  empacotamento de produção, exportação de inscritos e resultados, e meia dúzia de correções de
  jornada.
- **O que falta especificar** é o grosso da contagem (84): famílias normativas fora do alvo (DP-10),
  alcance da Etapa por Perfil, nome social e a Retificação de documento exigido. Quase tudo isso
  depende de decisão, e não de código.
- **O que falta validar** atravessa tudo: 20 itens implementados esperam pessoas.
- **O que falta documentar:** o manual de operação, o procedimento de atendimento ao candidato, a
  concessão de papéis, a resposta a incidente com dado pessoal e a contingência do certame.

## 8. Problemas de integração

- **Identidade da gestão × tudo** (GO-01). A segregação de funções, a trilha de autoria e o
  impedimento do julgador estão no código, mas operam sobre uma identidade declarada no seletor.
  Até haver autenticação, nenhuma dessas garantias protege contra quem se declara outro.
- **Portal × documento oficial** (ED-06, com CA-08 e AS-05). A página da seleção chama de "Edital
  completo" o PDF da publicação de origem da versão vigente, que pode não conter uma Retificação em
  vigor. No percurso de 15/10, a mesma página listava duas "Retificação 15/10/2026", uma delas
  "vigente desde 30/10" (PV-05).
- **Recurso × corte** (AV-04). A reabilitação antes do marco torna a ordem obsoleta, mas não o corte.
- **Requerimento × dados exigidos pelo Edital** (PV-01). A mesma data de nascimento é pedida duas
  vezes, sem conferência entre as duas fontes.
- **Sistema × Registro Acadêmico** (AV-09). O arquivo de matrículas nunca foi importado no destino, e
  o `seed_demo` grava `PPP` onde o destino espera `PPI`.
- **Sistema × Caixa** (AS-24). A fonte do sorteio é real, mas não tem contrato, nem E2E periódico,
  nem uma cadeia de substituição efetiva.
- **Configuração × produção** (CA-05). `AVISOS_AOS_CANDIDATOS` não tem trava de inicialização:
  basta uma variável para ligar os avisos sem a validação de LGPD.

## 9. Problemas nas jornadas

O que o percurso de 15/10 encontrou, somado ao que a matriz registra.

- **Candidato:**
  - inscrever-se exige, depois de "Seus dados", voltar à vaga e clicar de novo em "Inscrever-se";
  - a data de nascimento é pedida duas vezes (PV-01);
  - o comprovante fala em SHA-256 e em comandos de terminal (PV-02);
  - o "Protocolo" fica vazio no Requerimento antes do envio (PV-05);
  - o texto do reenvio da convocação sugere prazo novo (CA-23);
  - o nome social não existe (CA-19);
  - não há ajuda nem aviso de privacidade (CA-04).
- **Equipe de seleção:**
  - a Revisão de um Edital retificado mostra a norma do dia da publicação (ED-07);
  - gravar a etapa Perfis apaga a descrição da Modalidade (ED-18);
  - a Retificação não alcança documento exigido (ED-08).
- **Comissão:**
  - numa equipe de 2 ou 3 pessoas, um recurso pode ficar sem julgador elegível, e não há aviso
    antecipado (AV-03);
  - a reavaliação determinada por recurso tem caminho, mas a tela não orienta (AV-14).
- **Avaliador:** a Mesa abre o documento em painel lateral e em aba própria; zoom e rotação são os do
  leitor de PDF do navegador (AV-41), e falta medir com avaliador real.
- **Responsividade:** oito das dez telas medidas cabem em 375 px. A verificação pública do sorteio
  (673 px) e o detalhe do Edital na gestão (440 px) transbordam (PV-03, PV-04).

## 10. Riscos técnicos e operacionais

| Risco | Gravidade | Item |
|---|---|---|
| Perda da `074` (spec, código e testes sem commit numa worktree) | Alta e imediata | GO-46 |
| Chave do OpenRouter exposta, com revogação não confirmada | Alta e imediata (custo) | GO-09 |
| Vídeos (~21 GB) sem cópia nem versionamento | Média | GO-47 |
| SMTP como único fator de acesso; falha do código silenciosa | Alta na implantação | GO-25 |
| Sorteio do piloto dependente de API sem contrato e sem E2E periódico | Alta no dia do sorteio | AS-24 |
| Guia de implantação nunca ensaiado em VM; backup só como receita | Alta na implantação | GO-24, GO-23 |
| Sessão de duas semanas e "Sair" sem `flush` | Média | GO-03 |
| Repositório sem proteção de branch e sem revisão de PR | Média | GO-32 |
| Trabalho em PR conflitante (#283) e documentação que depende dele | Baixa | GO-26 |
| Modo SQLite da suíte vermelho, documentado e sem conserto | Baixa | GO-34 |

## 11. Pendências históricas recuperadas

A [rastreabilidade histórica](auditoria-de-consolidacao-2026-10-15/rastreabilidade-historica.md), §3,
lista o que as sessões guardavam e o planejamento não. As de maior peso:

- **LDAP** (28/08). A resposta literal do usuário foi registrada como tarefa da `002` (T056) e nunca
  virou trabalho.
- **Nome social em spec própria** (16/09). Decidido, nunca aberto.
- **Retenção como precondição de dado real** (01/09). Está no README, mas sem dono nem prazo.
- **Retificação de documento exigido** (03/09), chamada de P0 pelo usuário. Metade foi feita.
- **Decisões tomadas pelo agente sem pergunta.** A FR-372 (Requerimento obrigatório para enviar),
  `registration_period_cancelled`, reclassificações da `026` e a leitura estreita da decisão 001 da
  `044` (ED-47).
- **Posições do usuário de 16/09 sobre o modelo Oferta**, que não foram registradas em `doc/` (ED-31).
- **Follow-ups propostos pelo agente em fim de sessão e nunca iniciados.** Entre eles: o E2E periódico
  da Caixa, a varredura de microcópia e a auditoria de UX do Requerimento e da exportação.
- **Compromissos de sessões recentes.** O commit da `074`, a entrada do `launch.json` não desfeita
  numa worktree e a trilha do filme de lançamento nunca ouvida.

## 12. Recomendações

1. **Decidir a janela do primeiro certame real (DEC-01)** e, com ela, disparar o pacote institucional
   para TI, encarregado, Cefor e correio (DEC-02 a DEC-05). Sem data, deixar os pedidos redigidos em
   `doc/`.
2. **Fazer agora o que só o usuário pode fazer:** revogar a chave exposta, autorizar o commit da
   `074`, copiar os vídeos e decidir sobre o #283.
3. **Semana de validação com pessoas (DEC-14)**, com o `seed_demo`: elaboração e condução (DP-18),
   jornada do candidato com cinco pessoas, leitor de tela, sorteio com a comissão, revisão das
   respostas da `070` e aprovação das frases da `069`.
4. **Próximo ciclo de desenvolvimento:**
   - o lote de correções diretas: ED-07, ED-18, ED-13 (#117), PV-03, PV-04 e PV-05 (a);
   - as specs curtas que dependem de uma decisão: o Edital vigente (DEC-06), o texto da convocação,
     o recurso antes do marco (DEC-08) e a sessão;
   - nenhuma funcionalidade nova até a validação dizer onde as pessoas travam.
5. **Pausar o assistente** até haver critério de aceite do piloto (DP-3) e acesso à L4. O que existe
   fica como está: validação interna (`070`), piloto (`071`), protótipo e demonstração local (`074`).
6. **Manual:** adiar a produção até o piloto e escrevê-lo com quem opera, partindo da Visão do Sistema
   (DEC-13).

## 13. Conclusão

O projeto chegou ao ponto em que o próximo ganho não está no código. As garantias que a Constituição
pede estão implementadas e testadas, e o ciclo do certame está coberto: imutabilidade, segregação,
trilha e negação por padrão. O que separa o sistema de um certame real são decisões institucionais
com prazo longo, uma identidade de gestão de verdade e a primeira vez que pessoas de fora o usarem.
Este documento, a matriz e as decisões pendentes foram escritos para que essa passagem comece de uma
lista conferida, e não da memória de 185 sessões.

---

## Síntese executiva — as dez respostas

1. **Qual é o estado de maturidade?** Pré-piloto. O produto está completo para o tipo de certame que
   modela e é tecnicamente sólido (11 297 testes, percurso de ponta a ponta no navegador). Não é
   implantável: faltam autenticação da gestão, política de retenção, ambiente, correio e assinatura
   do ato. E não foi validado com nenhum usuário real.
2. **O que está efetivamente concluído?** O ciclo do Edital à matrícula, com integridade normativa no
   banco; o portal e a jornada do candidato até o acompanhamento; a condução pela gestão; os avisos.
   Ver §6. "Concluído" aqui quer dizer implementado e verificado, e não validado com pessoas.
3. **Que demandas antigas ficaram esquecidas?**
   - LDAP (28/08);
   - nome social (16/09);
   - retenção (01/09);
   - Retificação de documento exigido (03/09);
   - teste operacional com o setor (DP-18);
   - posições sobre o modelo Oferta (16/09);
   - decisões que o agente tomou sem perguntar (ED-47).
4. **O que está só parcialmente pronto?** 25 itens. Os principais:
   - a Retificação de documento exigido;
   - o reaproveitamento de Edital;
   - o PDF oficial (resíduos de composição e acessibilidade);
   - a trilha de auditoria (atos do candidato fora dela);
   - a base de CEP (sem job);
   - a detecção do canal de dúvidas;
   - a multiunidade (modelada, uma unidade só exercitável).
5. **Que problemas prejudicam as jornadas completas?**
   - o "Edital completo" sem a Retificação em vigor;
   - o recurso deferido que não alcança o corte;
   - o texto da convocação que sugere prazo novo;
   - a Revisão que mostra norma revogada;
   - a descrição da Modalidade apagada ao gravar;
   - dados pedidos duas vezes;
   - um julgador possivelmente inexistente numa equipe de 2 ou 3 pessoas.
6. **Que trabalho manual o sistema ainda deixa?**
   - barema e heteroidentificação (fora do sistema por decisão);
   - redigir o Edital no Word e transcrever (E10 = B);
   - exportar inscritos e resultados (não há planilha);
   - lançar notas (não há importação);
   - convocar o cadastro de reserva;
   - registrar a matrícula efetivada;
   - cadastrar membros por texto colado;
   - cadastrar Unidade pelo arquivo;
   - corrigir CPF e recuperar acesso (sem ferramenta);
   - avisar Retificação e prazos por outro canal;
   - segunda instância recursal e prazos em dias úteis.
7. **As dez pendências de maior impacto:**

   | # | Item | Prior. | O quê |
   |---|---|---|---|
   | 1 | GO-01 | P0 (impl.) | autenticação institucional |
   | 2 | GO-19 | P0 (impl.) | retenção e descarte |
   | 3 | GO-31 | P1 | validação com o setor (DP-18), com CA-01, CA-15, CA-14 e AV-07 |
   | 4 | GO-25 | P0 (impl.) | correio como único acesso |
   | 5 | ED-04 | P0 (impl.) | autoridade e assinatura do ato |
   | 6 | ED-06 | P1 | o "Edital completo" depois de Retificação |
   | 7 | GO-20 | P1 | pacote LGPD, incluindo a cota ao lado do nome (CA-06) |
   | 8 | AV-04 | P1 | recurso antes do marco não alcança o corte |
   | 9 | CA-23 | P1 | reenvio da convocação sugere prazo novo |
   | 10 | ED-10 | P1 | famílias normativas fora do alvo (barema, heteroidentificação) |

   Fora da lista por serem ações de um minuto, mas urgentes: GO-46 (`074` sem commit) e GO-09 (chave
   exposta).
8. **O que precisa de decisão antes de implementar?** As 16 decisões de
   [decisões pendentes](auditoria-de-consolidacao-2026-10-15/decisoes-pendentes.md). A que ordena
   todas é a DEC-01: quando, e com qual Edital.
9. **Que documentos e manuais foram atualizados?**
   - **Criados:** este relatório, a matriz, a rastreabilidade, o roadmap, as decisões, o inventário e
     as capturas.
   - **Atualizados:**
     - a Visão do Sistema (revisão de 15/10, até a `072`);
     - a arquitetura do manual (Revisão 6);
     - o README;
     - o `AGENTS.md`;
     - o `.env.example`;
     - o runbook de CEP;
     - o roteiro do teste operacional;
     - o quickstart da `066`.
   - **Marcadas como superadas em parte:** a consolidação de 26/09 e suas decisões pendentes.
   - **Deliberadamente não tocado:** o guia de implantação, que o #283 reescreve.

   Detalhe no inventário, §0.
10. **Qual deve ser a próxima etapa de desenvolvimento?** O lote de correções diretas mais a spec
    curta do Edital vigente, enquanto o pacote institucional e a semana de validação correm fora do
    código. Funcionalidade nova, inclusive a abertura do assistente, espera o que a validação mostrar.
