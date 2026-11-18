# Estudo — identidade do candidato, CPF coincidente, histórico fragmentado e vantagem em sorteio

**Data:** 2026-11-17 · **Conferido contra:** `main` em `3afb6702`

**Natureza:** análise. Não decide produto, não especifica e não autoriza implementação. As decisões
estão reunidas no §14 e são do usuário.

**Entrada:** o contexto `contexto-identidade-cpf-coincidente-2026-11-17.md`, com as catorze entregas
pedidas. Cada premissa dele foi conferida no código, na `010`, na Constituição e em dez Editais da
amostra; o que a conferência mudou está no §1.

| Entrega pedida | Onde está |
|---|---|
| 1. Análise sob produto, domínio, segurança, LGPD e operação | §2 |
| 2. Como outros sistemas equilibram | §3 |
| 3. Comparação das alternativas | §4 |
| 4. Recomendação principal e contingência | §5 |
| 5. Modelo de identidade | §6 |
| 6. Momento da prova forte ou da decisão | §7 |
| 7. Workflow do CPF coincidente | §8 |
| 8. Efeitos sobre sorteio, avaliação, classificação, recursos e convocação | §9 |
| 9. Consolidação do histórico | §10 |
| 10. Inscrições e identidades existentes | §11 |
| 11. Ameaças e abuso | §12 |
| 12. Decisões do usuário | §13 (as 19 questões) e §14 |
| 13. Incrementos | §15 |
| 14. Cenários de aceitação | §16 |

## 0. Resumo

1. **O CPF declarado serve de sinal, e não de chave.** Ele basta para *abrir* uma análise e não
   basta para *decidir* nada sozinho. Com isso, a proteção contra "primeiro a enviar vence" fica de
   pé, e o CPF não precisa virar único.
2. **Declarar CPF falso não dá vantagem em sorteio, desde que o deferimento confira o CPF contra o
   documento.** A inscrição de CPF inventado que for sorteada cai na análise documental, e a ordem
   dos demais continua uniforme. A única forma de vantagem que sobrevive ao deferimento é a mesma
   pessoa com o mesmo CPF em duas contas — exatamente o que a coincidência detecta (§2.3). Por isso
   o gate institucional resolve o problema **sem** provedor forte.
3. **Recomendação principal: C + D, lidos como E.** Coincidência relevante vira pendência do recorte
   e impede congelar a relação de habilitados enquanto não houver ato motivado; a pessoa une as
   próprias contas provando o controle das duas; e "pessoa" passa a ser o conjunto de contas unidas
   por ato append-only, sem tocar em nenhuma Inscrição. O gov.br entra como segunda forma de
   entrar e como saída rápida da pendência, e não como porta única.
   **O Cefor já inscreve por gov.br** nos Editais 57, 28 e 35/2026 (§3.3): para esses, o GPS só por
   e-mail dá menos garantia do que o processo que ele substitui, e a integração deixa de ser
   hipótese distante.
4. **A fusão por reescrita não é uma opção, é uma impossibilidade.** A Inscrição enviada é imutável
   por gatilho de banco, e a `010` proíbe reescrever o titular (FR-042) e fundir identidades
   (FR-056). A consolidação só pode ser uma camada de associação — e exige emendar a `010`.
5. **Há um segundo furo, que o contexto não cita:** o teto de inscrições por candidato no Edital
   (`maxInscricoesPorCandidato`, a cláusula "apenas um dos cursos" do 58/2026) também é contado por
   conta, e a marca de coincidência é por Perfil — a segunda conta fura o teto sem deixar marca.
6. **Descoberta depois do sorteio não pede sorteio novo.** Retirar um participante de uma ordem
   sorteada mantém uniforme a ordem dos outros; refazer prejudicaria quem nada fez. O que não pode é
   a pessoa escolher a melhor das duas posições: a regra de qual inscrição segue precisa estar
   escrita **antes** e não depender do resultado.
7. **Parte das duplicidades é honesta, e o sistema as provoca:** a inscrição enviada não se corrige
   nem se substitui, e a única saída de quem errou é outra conta. Fechar essa porta é um incremento
   próprio (§15, I5).

## 1. O que a conferência mudou no contexto

O contexto descreve o modelo com fidelidade. Sete pontos mudam a análise:

| # | O que o contexto diz ou deixa em aberto | O que o repositório diz | Consequência |
|---|---|---|---|
| 1 | "Pode ser mais adequado criar uma associação […] do que substituir os `identity_subject`" | A Inscrição enviada é imutável na aplicação e por gatilho (`inscricao_enviada_imutavel`, [inscricoes/models.py](../backend/processo_seletivo/inscricoes/models.py)); a `010` proíbe reescrever o identificador (FR-042) | A associação é o único caminho, e não o preferível |
| 2 | "Nada une automaticamente X e Y" | Mais forte: a `010` diz que *"o sistema NÃO PODE fundir identidades"* (FR-056) e que a única movimentação de credencial é a retomada a partir de identidade **sem inscrição alguma** (FR-053; `retomar`, em [associacao.py](../backend/processo_seletivo/identidade/application/associacao.py)) | As alternativas D e E pedem **emenda** da `010`, e não só acréscimo |
| 3 | O dano é o sorteio | O teto por candidato no Edital conta por `identity_subject` (`outras_enviadas_no_edital`, em [submissao.py](../backend/processo_seletivo/inscricoes/application/submissao.py)) | Segunda conta fura também o teto; e, como a marca é por Perfil, **sem marca** |
| 4 | "A gestão vê a marca de CPF coincidente" | A marca é calculada na leitura da listagem (`_cpfs_coincidentes`, em [consulta.py](../backend/processo_seletivo/inscricoes/application/consulta.py)) e existe só naquela tabela. Não há registro, evento, aviso nem item em "Minhas atividades" | Quem não abrir a lista de inscrições não fica sabendo |
| 5 | "Habilitação" antes do sorteio | Nos Editais de sorteio lidos não há Etapa de habilitação: entram todas as enviadas (`elegiveis`, em [projecao.py](../backend/processo_seletivo/sorteios/domain/projecao.py)), e a análise documental vem **depois** do sorteio (58/2026, item 6.3) | Não existe avaliação anterior onde pendurar a decisão; ela precisa de ato próprio |
| 6 | "Um e-mail pode ser compartilhado entre familiares?" | Uma conta carrega **um** nome e **um** CPF, e o CPF congela na primeira inscrição enviada (`cpf_congelado`, em [credenciais.py](../backend/processo_seletivo/identidade/application/credenciais.py)) | Hoje uma conta já é uma pessoa: o responsável não inscreve dois filhos pelo mesmo endereço |
| 7 | — | Não existe corrigir, substituir, cancelar nem desistir de inscrição enviada (`010`, FR-075; `012`) | Quem errou a modalidade ou um documento só "corrige" abrindo outra conta |
| 8 | "Dependência de um provedor institucional ainda inexistente" | Os Editais 57, 28 e 35/2026 do Cefor já mandam o candidato ao gov.br para se inscrever (§3.3) | O provedor existe no processo atual de parte dos Editais; o que não existe é a integração do GPS |

E um achado na norma: os Editais de sorteio dizem **"cada candidato receberá um número para o
sorteio"** (57/2026, item 8.4; 58/2026, item 6.4; 59/2026). A unidade da norma é o candidato; a do
sistema é a inscrição. A divergência do sistema em relação ao Edital existe hoje, com ou sem fraude.

## 2. Análise do problema

### 2.1 Três perguntas, três provas

O modelo atual responde bem a uma pergunta e empresta a resposta às outras duas.

| Pergunta | Prova necessária | Situação hoje |
|---|---|---|
| Quem pode entrar nesta conta? | Controle de uma credencial | Resolvido: código por e-mail |
| De quem é este histórico? | Controle das **duas** contas, ou decisão institucional | Não existe: histórico é da conta |
| Esta pessoa já participa deste recorte? | Identidade civil provada, **ou** decisão institucional sobre um indício | Não existe: a unicidade é da conta |

Tornar o CPF único tentaria responder a terceira com a prova da primeira. Um provedor forte
responde as três de uma vez, mas ao preço da entrada. O caminho do meio é dar a cada pergunta a
prova que ela pede, no momento em que ela importa.

### 2.2 Produto

- **O que a entrada simples comprou continua valendo.** Ninguém cria senha, ninguém informa CPF para
  olhar um Edital, e nenhum caminho termina em beco. Nada na recomendação mexe nisso.
- **A fragmentação é silenciosa.** A pessoa que entra pelo e-mail novo vê uma área vazia e conclui
  que o histórico se perdeu. A tela não tem como dizer "você tem outra conta" sem virar oráculo
  (§12), mas pode sempre oferecer **"tenho outra conta"**.
- **O sistema provoca duplicidade honesta** (linha 7 do §1). A regra "vale a última enviada", que o
  próprio Cefor escreve no 14/2026 (item 7.8), é a tradução normativa desse comportamento: quem
  manda de novo quer que a nova valha.
- **Uma conta é uma pessoa** (linha 6). Representação — responsável que inscreve menor, procurador —
  não está modelada, e não deve entrar por acidente nesta mudança.

### 2.3 Domínio: por que CPF falso não rende

O sorteio produz uma ordem uniforme dos números. Considere quem tenta duas chances:

- **Mesmo CPF, duas contas.** As duas inscrições sobrevivem à análise documental. É a vantagem real,
  e é o que a coincidência por CPF enxerga.
- **CPF diferente na segunda conta** (inventado, com dígitos válidos). Não há coincidência. Mas os
  Editais exigem o documento de CPF de todos os candidatos (58/2026, item 5.4 b), e o deferimento
  vem depois do sorteio. Se a inscrição falsa for sorteada, é indeferida e a vaga passa ao seguinte;
  se a verdadeira for sorteada, a pessoa tem a chance que teria com uma inscrição só. **O ganho é
  zero** — e os demais não perdem nada, porque retirar elementos de uma permutação uniforme deixa
  uniforme a ordem relativa dos que ficam.
- **CPF e documentos de outra pessoa.** É outra pessoa concorrendo (o "laranja"). A vaga seria dela,
  e a matrícula é pessoal. Não é problema de identidade de conta.

Disso saem duas conclusões de projeto. A detecção por CPF declarado é **completa para a vantagem que
importa**; e ela depende de uma condição que precisa ser dita em requisito: **a análise documental e
a formalização conferem o CPF declarado contra o documento**. Sem essa conferência, o segundo caso
volta a render.

Em Edital classificatório o dano é outro: duas inscrições são duas tentativas de avaliação
("melhor de duas"), com documentos ou modalidades diferentes, e podem ocupar duas posições.

### 2.4 Segurança

- **CPF é dado conhecido de terceiros.** No Brasil, deve ser tratado como público para fins de
  ameaça. Qualquer efeito automático preso a ele — bloquear, unir, preferir, suspender — é uma
  alavanca na mão de quem conhece o número alheio. Isso vale para "primeiro a enviar vence" e vale
  igualmente para **"último a enviar vence" automático** (a alternativa F sem ato humano).
- **Unir contas é a operação mais perigosa do desenho.** Quem a completa passa a ler documentos
  comprobatórios de outra conta. Ela só pode nascer de prova de controle das duas pontas ou de ato
  institucional com contraditório.
- **Toda resposta que varia conforme o CPF é um oráculo.** A `010` já trata isso com cuidado
  (FR-017, FR-052c, FR-087), e a mudança precisa herdar o cuidado.

### 2.5 LGPD

- **Base legal.** Tratamento pelo poder público para execução de competência legal e de política
  pública (arts. 7º, II e III, e 23). Prevenir participação dupla é finalidade compatível com a da
  coleta: o CPF foi pedido para identificar o candidato no certame.
- **Necessidade.** A recomendação não coleta dado novo. Usa a igualdade do CPF já declarado, dentro
  do mesmo Edital, e os documentos que a inscrição já anexou. Comparar entre Editais diferentes
  amplia a finalidade e não é necessário — coincidência entre Editais é legítima.
- **Decisão humana.** O ato que retira uma inscrição do recorte é de autoridade, motivado e
  contestável; não há decisão unicamente automatizada (art. 20).
- **Minimização na comunicação.** O aviso a uma conta nunca traz dado da outra — nem endereço
  mascarado.
- **Retenção.** Os atos de vínculo e de decisão são registro do certame, e seguem a mesma política
  das inscrições. Essa política é a precondição PC-003 da `010`, que **continua aberta**: a questão
  19 do contexto já era gate de produção antes deste estudo.

### 2.6 Operação

- **A janela existe no calendário.** O 58/2026 publica a lista de habilitados dois dias antes do
  sorteio (item 6.4). Entre o fim das inscrições e esse ato é que a pendência se resolve.
- **A carga tem de ser proporcional ao caso real**, que é raro (o achado de 30/09 já dizia que a
  marca é exceção). O caso honesto se resolve sozinho quando a pessoa une as contas; o que sobra
  para a comissão é o resíduo.
- **A pendência precisa aparecer quando nasce**, e não no dia de congelar: em "Minhas atividades"
  (`160`) e na prévia do sorteio (`098`, `102`), desde o envio da segunda inscrição.

## 3. Como outros sistemas equilibram

Pesquisa de 17/11/2026. **Aberto** quer dizer que a fonte foi lida; **índice** quer dizer que só o
resumo do buscador foi visto, porque a página não abriu. O que ficou sem confirmação está dito.

### 3.1 Dois padrões, e nenhum é o nosso

| Padrão | Quem | Entrada | Unicidade | Duplicidade | Recuperação |
|---|---|---|---|---|---|
| **Provedor forte obrigatório** | Sisu, Prouni, Fies, Enem | gov.br | Uma conta por CPF, por construção | Vale a última alteração confirmada no prazo (Sisu); uma inscrição por CPF (Enem) | Entregue inteira ao gov.br |
| **Conta própria com CPF como chave** | Ifes (técnicos), IFSC, IFB, IFRN, Ufes, bancas | CPF + senha; o e-mail só ativa e recupera | CPF único no cadastro | "Vale a última inscrição" (Ifes, IFSC, FGV) ou bloqueio da segunda (IFB, CAp UFPE) | Por e-mail; perdido o e-mail, atendimento com envio de documento (Cebraspe) |

**Não foi encontrado nenhum sistema que identifique o candidato só por e-mail com CPF apenas
declarado.** Em todos, a unicidade é do CPF. O modelo da `010` é mais leve na entrada do que
qualquer par — e é o único em que a duplicidade é possível por construção.

### 3.2 O que cada grupo ensina

- **Seleções do MEC e do Inep.** O Sisu 2026 exige gov.br e classifica pela última alteração
  confirmada pelo candidato (Edital MEC nº 29/2025, itens 1.3 e 1.9 —
  [aberto](https://www.ufmg.br/sisu/wp-content/uploads/2026/01/1-Edital-SiSU-MEC-2026.pdf)). O
  Prouni diz que manter e recuperar a conta cabe só ao candidato (Edital SESu nº 51/2026, item 7.3 —
  [aberto](https://www.unisinos.br/graduacao/images/2026/prouni/Edital_n_51_2026_SESu_PROUNI.pdf)).
  O Enem aceita uma inscrição por CPF
  ([FAQ do Inep, aberto](https://www.gov.br/inep/pt-br/acesso-a-informacao/perguntas-frequentes/exame-nacional-do-ensino-medio-enem)).
- **O próprio Ifes.** No processo de cursos técnicos, o sistema recebe uma inscrição por pessoa e
  vale a última finalizada; para mudar de curso ou modalidade, cancela-se e faz-se outra (PS 32/2025,
  seção 3 —
  [aberto](https://ifes.edu.br/images/stories/-publicacoes/processos-seletivos/alunos/2025/2025-32-conc-subs/edital-32-2025-cursos-tecnicos-concomitantes-e-subsequentes.pdf)).
  As [perguntas frequentes do Ifes](https://ifes.edu.br/perguntas-frequentes?catid=5) (aberto, ciclo
  de 2021) dizem o mesmo e acrescentam que o CPF não muda depois da inscrição.
- **Outros Institutos com sorteio.** O IFSC considera válida apenas a última inscrição (Edital
  03/2026-2, item 4.4 —
  [aberto](https://www.ifsc.edu.br/documents/d/ingresso/edital-03_2026_2_tecnico_conc_sub_sorteio-ok)).
  O IFB declara que o sorteio e as demais etapas são feitos **pelo CPF**, e bloqueia a segunda
  inscrição (Edital 23/2023, item 5.2.1.1 — aberto). O IFRN proíbe o mesmo e-mail para candidatos
  distintos (Edital 11/2025-PROEN, item 3.2 —
  [aberto](https://processoseletivo.ifrn.edu.br/edital/arquivos/254)).
- **Bancas.** No Cebraspe, quem perdeu o e-mail informa CPF e endereço novo e envia imagem do
  documento de identidade e do CPF; depois da análise, o acesso vai para o endereço novo. Inscrição
  excedente é cancelada
  ([perguntas frequentes, aberto](https://www.cebraspe.org.br/perguntas-frequentes/)). Na FGV vale a
  realizada por último (índice).
- **Sorteios de vagas.** O Colégio de Aplicação da UFPE admite uma inscrição por CPF no grupo de
  concorrência (aberto). Na Escola de Aplicação da USP, um número de sorteio foi cancelado por
  duplicidade, com registro em ata, e os demais seguiram (índice). **Não apareceu nenhum caso de
  sorteio refeito por duplicidade descoberta depois**: cancela-se a inscrição ou o número, mantém-se
  a ordem dos outros e chama-se o seguinte — o que o §9.1 propõe.

### 3.3 O Cefor já inscreve por gov.br

É o achado que mais pesa. Os Editais do próprio Cefor mandam o candidato ao gov.br para se
inscrever: 57/2026 (item 5.2.1), 28/2026 e 35/2026 (item 5.1.2), conferidos nos PDFs da amostra; e o
142/2025, conferido na pesquisa. O 58/2026 e o 59/2026 (FIC) não o mencionam, e o 76/2026 usa o
SIGAA.

Duas consequências:

- **Parte do público do GPS já tem conta gov.br**, porque o processo atual a exige. Para esses
  Editais, o argumento da fricção contra o provedor forte é fraco.
- **Trocar esse processo pela entrada só por e-mail reduz a garantia que a instituição tem hoje**:
  onde o gov.br entregava um CPF por conta, o GPS passa a aceitar CPF declarado. O risco que este
  estudo trata não existia, para esses Editais, no processo que o GPS substitui.

### 3.4 O que o gov.br entrega, e o que não entrega

- **Entrega o CPF como identificador** (`sub`), o nome, o e-mail verificado e o nível da conta, por
  OpenID Connect
  ([roteiro técnico, aberto](https://acesso.gov.br/roteiro-tecnico/iniciarintegracao.html)). Bronze
  é cadastro validado na Receita ou no INSS; prata e ouro pedem biometria, banco ou certificado
  ([níveis, aberto](https://www.gov.br/governodigital/pt-br/identidade/conta-gov-br/niveis-da-conta-govbr)).
  Para a **unicidade**, qualquer nível basta: há uma conta por CPF.
- **Autarquia federal pode integrar.** O pedido é de um gestor público, a credencial é por sistema,
  e o roteiro fala em três dias para homologação e três para produção, com domínio oficial
  ([aberto](https://acesso.gov.br/roteiro-tecnico/solicitacaocredencialprocesso.html)). **O custo
  para o órgão não foi confirmado** em nenhuma página oficial.
- **Não cobre todos.** Sem CPF não há conta
  ([aberto](https://acesso.gov.br/faq/_perguntasdafaq/cadastrosemcpf.html)); o atendimento de menor
  passa pelo responsável legal. Que o adolescente tenda a ficar no bronze é inferência, e não fonte.
- **Há um caminho intermediário:** a API de CPF do Conecta devolve nome, nascimento e situação
  cadastral a órgão federal
  ([aberto](https://www.gov.br/conecta/catalogo/apis/cadastro-base-do-cidadao-cbc-cpf)). Ela não
  prova que quem digita é o titular, mas acusa no envio o CPF que não confere com o nome — erro de
  digitação e número inventado. A adesão pede Plano de Transformação Digital e SISP; a gratuidade não
  foi confirmada.

### 3.5 Boas práticas de união e recuperação

- **Não vincular contas porque um atributo coincide.** A recomendação da OWASP é explícita para
  e-mail e atributos de perfil
  ([Authentication Cheat Sheet, aberto](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)).
  CPF declarado é atributo de perfil.
- **Mesma resposta para conta existente e inexistente; código de uso único; nada muda antes do
  código válido; sempre um caminho de recuperação com prova de identidade**
  ([Forgot Password Cheat Sheet, aberto](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)).
- **Sem autenticação por conhecimento; perda de fator pede prova de identidade no nível do
  cadastro; notificar toda alteração de credencial** (OWASP ASVS 5.0, V6.4.2, V6.4.4 e V6.3.7 —
  aberto).
- **Toda recuperação notifica o titular** (NIST SP 800-63B-4, recuperação de conta —
  [aberto](https://pages.nist.gov/800-63-4/sp800-63b/events/); a numeração da seção não foi
  conferida).
- **Conta plantada antes da vítima** (*pre-hijacking*): de 75 serviços populares, ao menos 35 eram
  vulneráveis
  ([USENIX Security 2022, aberto](https://www.usenix.org/conference/usenixsecurity22/presentation/sudhodanan)).
  A causa é usar um identificador alegado sem verificar a posse — o que a união por CPF faria.

### 3.6 Base normativa

- **LGPD**, arts. 6º, III (necessidade), 7º, II e III, e 23
  ([aberto](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)); o guia da
  ANPD para o poder público lê o art. 7º junto com o 23 (versão 1.0, aberta; a 2.0 não foi lida).
- **Lei 14.129/2021**, art. 28: o CPF é número suficiente para identificar o cidadão em serviço
  público — e entra no cadastro quando a instituição tem documento comprobatório ou acesso à base da
  Receita (§2º) ([aberto](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14129.htm)).
  O parágrafo descreve a condição do §2.3: o CPF vale quando conferido contra o documento.
- **Lei 14.534/2023**, art. 1º: CPF como número único
  ([aberto](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14534.htm)).
- **Não foi encontrada** orientação da ANPD sobre o CPF como chave de deduplicação. O que há é
  necessidade na coleta e cuidado na divulgação (CPF mascarado em listas).

## 4. Comparação das alternativas

| Alternativa | O que resolve | Riscos principais | Complexidade | Veredito |
|---|---|---|---|---|
| **A.** Identidade forte desde o início | Os três problemas, para quem tem o provedor. É o padrão do MEC e o do próprio Cefor em três Editais (§3) | Desfaz a entrada simples; depende de credenciamento do GPS; não cobre quem não tem CPF, e o menor depende do responsável; a migração das contas atuais continua necessária | Média na técnica (OpenID Connect), incerta no prazo institucional | Não como porta única. Como **exigência por Edital**, é decisão a considerar (§14, P-8) |
| **B.** E-mail primeiro, prova forte antes de produzir direito | Vantagem e, com vínculo automático, histórico | Mesma dependência de A; etapa obrigatória a mais para todos por causa de um caso raro; prazo e tratamento de falha | Média a alta | Aproveitar **em parte**: a prova forte como segunda entrada e como *saída da pendência*, e não como etapa de todos (§7) |
| **C.** Aceitar e criar gate institucional | Vantagem; resolução motivada | Carga operacional; atraso se ninguém decidir; vetor de obstrução em massa (§12) | Média | **Sim**, é o núcleo |
| **D.** Consolidação voluntária | Histórico; resolve sozinha o caso honesto de C | Tomada de conta por união; precisa de desfazimento | Média | **Sim**, junto de C |
| **E.** Separar conta de pessoa | Dá nome ao que falta | Como mudança estrutural (nova coluna na Inscrição, migração), esbarra na imutabilidade da linha enviada | Alta se literal; baixa se a pessoa for **derivada** dos vínculos de D | **Sim, como leitura**: a pessoa é o conjunto de contas unidas (§6) |
| **F.** Deduplicar só no sorteio | Vantagem no sorteio | Automática, vira "último a enviar vence"; esconde o problema das outras etapas; não diz qual inscrição vale | Baixa | **Não** como automática. A regra de F é reaproveitada dentro de C, aplicada por ato |

## 5. Recomendação

### 5.1 Principal

Manter a entrada como está e acrescentar três peças, nesta ordem de valor:

1. **Gate (C).** Coincidência relevante é pendência do **recorte**, e não suspensão da pessoa.
   Congelar a relação de habilitados — e publicar o primeiro resultado, no Edital sem sorteio — é
   recusado enquanto houver coincidência sem ato. O ato é append-only, motivado, de autoridade, e
   diz: *mesma pessoa, segue a inscrição N* ou *pessoas distintas*.
2. **Regra objetiva no Edital.** "Uma inscrição por pessoa em cada Perfil; havendo mais de uma,
   segue a última enviada dentro do prazo." O sistema propõe pela regra; a autoridade confirma.
3. **União de contas (D), com a pessoa derivada (E).** Quem está numa conta prova o controle de uma
   credencial da outra, e um ato append-only as declara da mesma pessoa. A partir dele: histórico
   único, unicidade e teto contados por pessoa. Unir contas com coincidência aberta **é** a
   declaração de mesma pessoa, e resolve a pendência pela regra.

Depois: recuperação institucional para quem perdeu o e-mail antigo e substituição da própria
inscrição dentro do prazo.

**Em paralelo, e não depois:** iniciar o credenciamento do GPS no gov.br. Ele não substitui nenhuma
das três peças — o legado, quem entra por e-mail e quem não tem conta continuam existindo —, mas
esvazia a fila da comissão e é o que o Cefor já pratica. O prazo é institucional, e por isso começa
cedo.

### 5.2 Contingência

Se a instituição não aceitar um gate que **bloqueia** o congelamento (medo de atrasar o certame):
manter a detecção, o aviso e o ato de decisão, mas **não impeditivos** — com advertência na
confirmação do congelamento e ciência registrada de quem congela, no padrão da `152` — e resolver
depois do sorteio pela mesma regra pré-fixada, retirando da ordem a inscrição que não segue.

É matematicamente justa (§2.3, §9.1) e operacionalmente mínima. O custo é de legitimidade: a relação
publicada mostra número, nome e protocolo, e o mesmo nome aparece duas vezes num ato público. Por
isso é contingência, e não recomendação.

O que **não** serve de contingência: CPF único no envio, união automática por CPF e deduplicação
automática. As três transformam o CPF declarado em efeito sem ato.

## 6. Modelo de identidade recomendado

Nenhum conceito existente muda de significado. Ganha-se um ato e uma leitura.

| Conceito | No código | Papel | Muda? |
|---|---|---|---|
| **Credencial** | `CandidateEmail` | Prova de acesso. Um endereço, uma conta | Não. No futuro, um segundo tipo: o identificador do provedor forte |
| **Conta** | `CandidateIdentity` (`subject`) | Onde a sessão entra. Carrega nome e CPF declarados | Não muda de forma |
| **Inscrição** | `Inscricao.identity_subject` | Pertence à conta que a enviou — é a **autoria**, e fica para sempre | Não é tocada |
| **Vínculo** | novo, append-only | Ato que declara duas contas da mesma pessoa. Tem fundamento, ator, instante e motivo; desfaz-se por ato sucessor, nunca por exclusão | Novo |
| **Pessoa** | derivada | O conjunto de contas ligadas por vínculos vigentes. Conta sem vínculo é pessoa de uma conta só, sem linha nenhuma a criar | Nova leitura |

**Fundamentos do vínculo**, do mais fraco ao mais forte — e o ato registra qual foi:

1. `CONTROLE_DAS_CREDENCIAIS` — a pessoa provou, na mesma operação, uma credencial de cada conta.
2. `DECISAO_INSTITUCIONAL` — recuperação sem acesso ao e-mail antigo, com evidência e contraditório.
3. `PROVEDOR_FORTE` — as duas contas apresentaram o mesmo CPF verificado.

**O que passa a ler a pessoa, e não a conta:**

- titularidade (`e_titular`, em [titularidade.py](../backend/processo_seletivo/inscricoes/domain/titularidade.py)): a inscrição é de uma das contas da pessoa;
- "Minhas inscrições": todas as contas da pessoa, com a indicação de por qual conta cada uma foi enviada;
- abertura de rascunho e envio: uma inscrição por **pessoa**, Edital e Perfil, e o teto por pessoa —
  na aplicação, sob a mesma trava que o teto já usa. A restrição de banco continua por conta;
- avisos: saem para o endereço principal da pessoa.

**O que continua lendo só a conta:** a autoria gravada em cada inscrição, recurso e requerimento, e a
trilha. Nada do que foi praticado muda de autor.

**Duas regras que o modelo precisa dizer:**

- **CPF divergente não se une por autoatendimento.** Duas contas com CPFs declarados diferentes só
  se unem por decisão institucional: unir por controle de e-mail faria uma pessoa com dois CPFs.
- **Unir não apaga a coincidência; decide-a.** Se as duas contas têm inscrição enviada no mesmo
  Perfil, a tela diz antes qual seguirá pela regra do Edital, e a pessoa confirma sabendo.

Se a leitura da pessoa será materializada (uma referência na conta, mantida pelo ato) ou calculada a
cada requisição é decisão de plano. Os conjuntos têm duas ou três contas; a fonte da verdade são os
atos.

## 7. O momento da prova forte e da decisão

| Momento | O que se exige | Por quê |
|---|---|---|
| Entrar, consultar, abrir rascunho | Código por e-mail | É o que a entrada simples comprou |
| Enviar inscrição | Nome e CPF declarados, com dígitos válidos | A coincidência **nasce** aqui, como pendência; ninguém é recusado (FR-064 fica) |
| Do envio até congelar a relação | **Decisão institucional** sobre cada coincidência relevante do recorte | Último instante antes do efeito irreversível; os documentos já estão anexados |
| Publicar resultado que habilita ou ordena (sem sorteio) | A mesma decisão | Evita "melhor de duas" |
| Análise documental e formalização | CPF declarado conferido contra o documento | É a condição do §2.3 |
| Convocar | Nenhuma coincidência sem ato entre os alcançados | Última linha de defesa, para o legado |

**A prova forte não é etapa obrigatória de ninguém, por padrão.** Quando houver provedor, ela é
oferecida em três lugares: como outra forma de entrar ("Entrar com gov.br", ao lado do código por
e-mail); como atalho para unir contas; e como saída imediata da pendência — a conta que prova o CPF
pelo provedor é a do titular, e a comissão recebe o caso praticamente decidido. Quem não tem
coincidência nunca precisa dela.

Para a unicidade basta qualquer nível da conta gov.br, porque há uma conta por CPF. Exigir nível
prata só faria sentido para abrir documentos de outra conta na união.

Se um Edital pode **exigir** a entrada pelo provedor — como os Editais 57, 28 e 35/2026 fazem hoje
no processo atual — é decisão institucional (§14, P-8), e não consequência deste desenho.

## 8. Workflow do CPF coincidente

### 8.1 O que é coincidência relevante

Entre inscrições **enviadas**, de **contas não unidas**, no **mesmo Edital**, com o mesmo CPF:

- **R1 — mesmo Perfil.** Duas chances no mesmo recorte. É o que a marca vê hoje.
- **R2 — Perfis diferentes, somando mais que o teto do Edital.** Fura a cláusula "apenas um dos
  cursos". Hoje não tem marca.

Não é relevante: mesmo CPF em Editais diferentes; em Perfis diferentes dentro do teto; rascunho. E
homonímia não entra: o gatilho é o CPF, nunca o nome.

### 8.2 Passos

1. **Nasce no envio.** A segunda inscrição é aceita. O envio grava o fato na trilha e a pendência
   aparece para a gestão do Processo. Para o candidato, a tela de envio é **a mesma** com ou sem
   coincidência (§12).
2. **Aviso às duas contas**, pelos endereços verificados, com o mesmo texto e sem dado da outra:
   há outra inscrição com o mesmo CPF neste Perfil; se as duas são suas, una as contas; se não,
   nada a fazer agora — a comissão analisará pelos documentos.
3. **Resolução pela própria pessoa.** Unidas as contas, a pendência ganha a proposta "mesma pessoa,
   segue a inscrição N", pela regra do Edital.
4. **Análise pela comissão**, para o que restar. Ela vê, lado a lado: os dados declarados, os
   documentos anexados (em especial o de CPF), os instantes de envio, e indícios auxiliares que o
   sistema já tem — mesmo telefone, mesmo arquivo anexado (resumo idêntico).
5. **Ato de decisão**, append-only, com motivo, autoridade e trilha:

   | Desfecho | Quando | Efeito |
   |---|---|---|
   | **Mesma pessoa** | Contas unidas, ou evidência documental | Segue a inscrição da regra; as demais ficam **sem efeito** no recorte, sem ser apagadas |
   | **Pessoas distintas — erro de CPF** | O documento de uma delas mostra outro número | As duas seguem; o CPF errado é corrigido por ato (§13, questão 10) |
   | **Pessoas distintas — uso indevido** | Uma das inscrições não tem como provar o CPF | A indevida fica sem efeito, com fundamento; o titular segue e é informado de que o número dele foi usado |

6. **Comunicação** do ato às contas envolvidas, com o motivo e o caminho de contestação.
7. **Contestação.** Antes do congelamento, o ato é sucedido por outro. Depois, a correção sucede a
   relação, pelo mecanismo que já existe (motivo obrigatório, cadeia única).
8. **Gate.** O congelamento do recorte e os atos do §7 recusam enquanto houver coincidência relevante
   sem ato vigente, e a recusa nomeia quantas e onde resolver.

### 8.3 Os estados pedidos na questão 7

A coincidência cria **pendência do recorte** e **impedimento de publicar** aquele recorte. Não cria
suspensão de habilitação: enquanto não há ato, as duas inscrições estão íntegras, e é o ato de
publicar que espera. Suspender por coincidência entregaria a terceiros o poder de suspender o
titular. A situação é derivada dos atos, sem coluna de estado.

## 9. Efeitos sobre as etapas

### 9.1 Sorteio

- **Antes de congelar:** a inscrição sem efeito não entra na projeção (`elegiveis`). A frase do
  critério publicado passa a dizê-lo, como já diz da Etapa de habilitação — quem ficou de fora
  precisa encontrar no texto público a razão.
- **Relação congelada, sorteio ainda não realizado:** relação sucessora, com motivo. A numeração
  muda, e isso é aceitável porque ainda não há semente.
- **Sorteio realizado:** **não se refaz.** A inscrição que não segue é retirada da ordem por ato, e
  os seguintes sobem. A ordem relativa de todos os outros continua uniforme; um sorteio novo tiraria
  a posição de quem foi bem sorteado e nada fez. A inscrição que segue é a da **regra pré-fixada**,
  qualquer que seja a posição dela — nunca a melhor colocada. Se a comissão apurar má-fé, a
  eliminação das duas é decisão dela, pelo Edital (76/2026, item 5.3.1, III e IV), com contraditório.

### 9.2 Avaliação

A inscrição sem efeito sai da distribuição e da Mesa. Se já foi avaliada, o resultado dela permanece
como registro e deixa de produzir efeito. Todo leitor do universo de inscrições precisa declarar o
que faz com "sem efeito", no padrão do guardião dos leitores da consequência (`164`).

### 9.3 Classificação

Gate antes da publicação. A inscrição sem efeito não entra no universo classificável, e a
classificação já publicada se corrige por sucessão, como hoje.

### 9.4 Publicação das inscrições (`148`)

A relação de recebidas mostra o que foi recebido, inclusive as duas. O preliminar e a homologação são
o lugar natural de a inscrição sem efeito aparecer como não homologada, com recurso pelo prazo que o
ato já tem. A `148` é opcional (FR-5401) — onde for usada, a decisão ganha contraditório público sem
mecanismo novo.

### 9.5 Recursos

Recursos interpostos por qualquer conta da pessoa passam a ser vistos pela pessoa. A autoria não
muda. O recurso contra o ato de decisão é questão aberta (§14, P-7).

### 9.6 Convocação, formalização e matrícula

Última defesa: convocar recusa alcançar duas inscrições do mesmo CPF sem ato. A formalização confere
o CPF contra o documento. A exportação de matrícula leva o CPF da inscrição — duas linhas com o mesmo
número chegariam ao sistema acadêmico, que é onde hoje o problema seria descoberto.

## 10. Consolidar o histórico sem perder autoria

1. **Entrada.** "Tenho outra conta", sempre visível na área; e a recusa atual de "adicionar e-mail"
   quando o endereço é de outra conta (`pertence_a_outra`) deixa de ser beco e passa a oferecer a
   união.
2. **Prova.** A pessoa informa o endereço da outra conta; sai um código com finalidade própria
   (`CONSOLIDAR`, como `RETOMAR` já é — FR-028). A resposta é a mesma, exista ou não a conta.
3. **Confirmação informada.** Antes do ato, a tela mostra o que vai acontecer — inclusive a
   coincidência que a união decide (§6).
4. **Ato.** Append-only: as duas contas, a credencial provada de cada lado, instante, fundamento.
   Nenhuma inscrição, documento, recurso ou evento de trilha é alterado.
5. **Aviso a todas as credenciais** das duas contas, com o caminho para contestar.
6. **Desfazer.** Por ato sucessor — da própria pessoa em prazo curto, ou institucional. Desfeito, as
   leituras voltam a ser por conta; o que foi praticado no intervalo fica com a autoria que tem.
7. **Sem e-mail antigo.** Pedido de recuperação pela conta nova, com os protocolos das inscrições
   antigas e documento de identificação; decisão de autoridade, com motivo; aviso ao endereço antigo
   e prazo de espera antes do efeito; fundamento `DECISAO_INSTITUCIONAL`. Nunca por perguntas sobre
   dados pessoais: quem conhece o CPF costuma conhecer o resto.

## 11. O que já existe

- **Nenhuma união automática**, nem na implantação. Contas existentes com o mesmo CPF continuam
  separadas até a pessoa uni-las ou a instituição decidir.
- **Levantamento somente leitura**, antes de especificar: coincidências R1 e R2 por Edital, e em que
  ponto do certame cada Edital está. Ele dimensiona tudo o mais.
- **Editais com inscrições abertas ou encerradas, sem relação congelada:** entram no gate. As
  coincidências existentes viram pendência no dia da implantação.
- **Relação congelada ou sorteio realizado:** tratamento do §9.1, caso a caso, por ato.
- **Editais publicados sem a cláusula da regra:** a regra objetiva só vale se o Edital a disser.
  Para os vigentes, ou Retificação, ou decisão da comissão caso a caso com base em "cada candidato
  receberá um número". É decisão institucional (§14, P-2).
- **Os conjuntos não reconciliados da implantação da `010`** (FR-044, FR-047) — CPF com mais de um
  identificador herdado, "inalcançáveis até tratamento operacional" — são exatamente o que a
  recuperação institucional vem resolver.
- **A marca atual** continua, e passa a ser o atalho para a pendência.

## 12. Ameaças e abuso

| # | Ameaça | Como se dá | Resposta do desenho |
|---|---|---|---|
| 1 | Duas chances | Mesma pessoa, mesmo CPF, duas contas | Gate + regra pré-fixada |
| 2 | Duas chances com CPF inventado | Segunda conta com outro número | Não rende (§2.3), desde que o deferimento confira o CPF |
| 3 | Furar o teto do Edital | Segunda conta em outro Perfil | Coincidência R2; teto por pessoa depois da união |
| 4 | Bloquear o titular | Inscrever-se antes com o CPF dele | Já resolvido: CPF não é único, e continua não sendo |
| 5 | Derrubar o titular | Inscrever-se **depois** com o CPF dele, contando com "vale a última" | A regra só se aplica a *mesma pessoa*, e quem declara isso é a união de contas ou a comissão — nunca a igualdade do CPF |
| 6 | Obstruir o certame | Muitas inscrições coincidentes para travar o congelamento | Cada uma custa e-mail verificado e envio completo; limites por origem (FR-030); decisão em lote para as que não têm documento de CPF; o impedimento é por recorte |
| 7 | Tomar a conta pela união | Controlar um e-mail da vítima e unir à própria conta | Prova das **duas** pontas na mesma operação; aviso a todas as credenciais; desfazimento; CPF divergente não se une sozinho |
| 8 | Conta plantada | Criar conta com o CPF da vítima antes dela, esperando união por CPF | Não existe união por CPF |
| 9 | Oráculo de participação | Enviar com o CPF de alguém para saber se ele está inscrito | Tela de envio idêntica com e sem coincidência; o aviso só vai a endereços verificados. O atacante com conta própria recebe o aviso — resíduo aceito, porque a relação de inscritos é pública |
| 10 | Oráculo de conta | "Tenho outra conta" com endereço alheio | Resposta única; código só chega a quem controla a caixa |
| 11 | E-mail reciclado | O provedor reatribui o endereço antigo e o novo dono entra na conta | Risco que já existe; a união aumenta o que há atrás de cada credencial. Mitigar com remoção de credencial (existe) e aviso de acesso |
| 12 | Recuperação fraudulenta | Pedir a conta de terceiro alegando perda do e-mail | Evidência documental, aviso ao endereço antigo, prazo de espera, ato motivado |
| 13 | Melhor de duas | Duas inscrições, escolher depois a melhor posição ou nota | Regra independente do resultado; a pessoa não escolhe depois do efeito |
| 14 | Abuso interno | Decidir coincidência a favor de conhecido | Capacidade própria, negada por padrão; motivo obrigatório; trilha; impedimento |

## 13. As dezenove questões de domínio

A coluna da direita diz quem responde: **evidência** quando os Editais ou o código já respondem, e
**decisão** quando é institucional.

| # | Questão | Resposta proposta | Base |
|---|---|---|---|
| 1 | Uma inscrição por Perfil, Edital ou Processo? | Por **Perfil**, sempre; por **Edital**, quando ele declara teto; por Processo, não | Evidência: "cada candidato receberá um número" (57, 58, 59/2026); "apenas um dos cursos" (58/2026, 4.2); "somente 1 inscrição por candidato" (14/2026, 7.8). Confirmar — P-1 |
| 2 | O limite atravessa Editais do mesmo Processo? | Não, por padrão | Nenhum Edital lido o faz; o teto é campo do Edital. Decisão — P-1 |
| 3 | Perfis diferentes são sempre legítimos? | Não: só dentro do teto do Edital | Constituição ("salvo restrição expressa do Edital") e 58/2026, 4.2 |
| 4 | O que caracteriza a mesma pessoa? | Contas unidas por ato; ou decisão motivada sobre evidência; no futuro, CPF verificado. Nunca a igualdade do CPF declarado, sozinha | §2.1 |
| 5 | Quem declara institucionalmente? | A comissão do Processo, por quem tenha capacidade própria para o ato | Decisão — P-3 |
| 6 | Quais evidências? | Documentos já anexados, controle de credenciais, instantes de envio, indícios auxiliares; contato pelo endereço verificado | §8.2 |
| 7 | Alerta, pendência, suspensão, impedimento? | Pendência do recorte + impedimento de publicar. Sem suspensão | §8.3 |
| 8 | Qual inscrição prevalece? | A última enviada dentro do prazo | Precedente: 14/2026, 7.8. Decisão — P-2 |
| 9 | A escolha é de quem? | Regra objetiva do Edital. A escolha do candidato é o ato de enviar por último, antes do congelamento; depois, nunca | §9.1 |
| 10 | Corrigir CPF antes ou depois do envio? | Antes, livre (já é assim). Depois, por ato institucional com base no documento, que não reescreve a inscrição | `010`, FR-008. Decisão — P-5 |
| 11 | O candidato pode contestar? | Sim | Decisão sobre o meio — P-7 |
| 12 | Inscrição com CPF de terceiro? | Sem efeito, por ato com fundamento; titular informado; encaminhamentos conforme o Edital | Decisão — P-6 |
| 13 | Descoberta depois do sorteio? | Retirada da ordem por ato, sem sorteio novo, pela regra pré-fixada | §9.1 |
| 14 | Consolidar sem alterar atos? | Vínculo append-only e pessoa derivada | §6, §10 |
| 15 | Perdeu o e-mail antigo? | Recuperação institucional | §10, passo 7 |
| 16 | Haverá provedor forte? | Já há, no processo atual: três Editais do Cefor inscrevem por gov.br. Falta o credenciamento do GPS, que autarquia federal pode pedir; o custo não foi confirmado (§3.3, §3.4) | Evidência + decisão — P-8 |
| 17 | Estrangeiros, menores, sem CPF, representação? | O envio exige CPF de onze dígitos; os Editais citam estrangeiro permanente, menor com responsável e procuração na matrícula. Representação não está modelada | Evidência + decisão — P-9 |
| 18 | E-mail compartilhado entre familiares? | Hoje já não funciona (§1, linha 6). Manter "uma conta, uma pessoa" | Decisão — P-9 |
| 19 | Retenção de identidades e credenciais? | Sem resposta no repositório; é a PC-003 da `010` | Decisão institucional pendente |

## 14. Decisões do usuário antes de especificar

| # | Decisão | Recomendação | O que muda se for outra |
|---|---|---|---|
| P-1 | Alcance da unicidade: Perfil sempre, Edital pelo teto, nada entre Editais | Como proposto | Atravessar Editais exige comparar CPF fora do certame, e a LGPD pesa mais |
| P-2 | Regra de qual inscrição segue, e como vale para Editais já publicados | "Última enviada", escrita no Edital; vigentes por decisão caso a caso | "Primeira enviada" penaliza quem reenviou para corrigir; escolha livre do candidato só é segura antes do congelamento |
| P-3 | Quem decide a coincidência | Capacidade nova, atribuída à presidência da comissão | Usar `resultado:publicar` evita capacidade nova, mas mistura publicar com decidir |
| P-4 | Gate impeditivo ou advertência | Impeditivo no congelamento | Advertência é a contingência do §5.2 |
| P-5 | Correção de CPF por ato institucional | Sim, com base no documento anexado | Sem ela, erro de digitação termina em indeferimento |
| P-6 | Tratamento do uso indevido de CPF | Sem efeito + aviso ao titular; sanção é do Edital | — |
| P-7 | Meio da contestação | Sucessão do ato antes do congelamento; onde houver `148`, o recurso dela | Tornar o ato objeto recorrível próprio é um incremento a mais |
| P-8 | gov.br: pedir o credenciamento do GPS? Em que papel? Um Edital pode exigi-lo? | Pedir já. Entrada opcional e saída da pendência (§7). Exigência por Edital: só depois de saber quem ficaria de fora | Obrigatório para todos é a alternativa A; sem integração, a carga inteira fica com a comissão |
| P-8a | Os Editais que hoje exigem gov.br migram para o GPS antes ou depois da integração? | Depois, ou com o gate (I1) já no ar | Migrar antes troca CPF verificado por declarado nesses Editais |
| P-9 | Uma conta, uma pessoa; representação fora do escopo | Manter | Representação é feature própria, com modelo próprio |
| P-10 | Emendar a `010` (FR-053, FR-056, FR-060, FR-062, FR-066) | Sim, por emenda datada, como a `010` já foi emendada | Sem emenda, D e E contradizem requisito escrito |
| P-11 | Substituir a própria inscrição dentro do prazo | Sim, como incremento próprio | Sem ele, a duplicidade honesta continua sendo produzida |
| P-12 | Conferência do CPF contra o documento como item explícito da análise | Sim | É a condição de que o §2.3 depende |

## 15. Incrementos

Cada um é entregável sozinho e deixa o sistema melhor do que encontrou. A ordem é a do risco.

| # | Incremento | Entrega | Depende de |
|---|---|---|---|
| I0 | **Levantamento e norma** (sem código de produto) | Relatório somente leitura das coincidências R1 e R2; cláusula-padrão para os próximos Editais; respostas a P-1 a P-4 | — |
| I1 | **Pendência e gate** | Coincidência R1 e R2 como fato registrado; item em "Minhas atividades" e na prévia do sorteio; ato de decisão append-only; inscrição sem efeito lida pela projeção do sorteio e pela classificação; recusa do congelamento | P-1 a P-4 |
| I2 | **Comunicação e contestação** | Avisos às contas (`066`); situação no portal; sucessão do ato; tratamento pós-congelamento e pós-sorteio | I1, P-7 |
| I3 | **União de contas** | Finalidade `CONSOLIDAR`; ato de vínculo; pessoa derivada; "Minhas inscrições", titularidade, unicidade e teto por pessoa; desfazimento; emenda da `010` | P-10 |
| I4 | **Recuperação institucional** | Pedido, evidência, decisão, prazo de espera; resolve os conjuntos da FR-044 | I3 |
| I5 | **Substituir a inscrição no prazo** | Reenvio pela mesma conta, com a anterior sem efeito pela regra | P-11; independe de I3 |
| I6 | **gov.br** | Segundo tipo de credencial ("Entrar com gov.br"); união automática de contas com o mesmo CPF verificado; saída da pendência | P-8; credenciamento externo, pedido desde o I0 |

I1 sozinho fecha a vantagem. I3 sozinho fecha o histórico. I5 seca a fonte honesta. Os três são
independentes entre si; I2 e I4 completam o contraditório. O I6 está no fim pela dependência
externa, e não pela importância: o pedido de credenciamento sai junto do I0, e o incremento entra
quando a credencial chegar. A união automática do I6 usa o ato de vínculo do I3.

## 16. Cenários de aceitação indispensáveis

**Entrada e envio (o que não pode regredir)**

1. Endereço novo, sem participação anterior: entra sem informar CPF e recebe área utilizável.
2. Segunda inscrição com CPF já declarado por outra conta no mesmo Perfil: é **aceita**, com a mesma
   tela e o mesmo comprovante de qualquer envio.
3. Ninguém é recusado, em caminho nenhum, por CPF que outra conta declarou.

**Pendência e gate**

4. Enviada a segunda inscrição coincidente, a pendência aparece para a gestão sem que ninguém abra a
   lista de inscrições.
5. Mesmo CPF em Perfis diferentes, acima do teto do Edital: há pendência. Dentro do teto: não há.
6. Mesmo CPF em Editais diferentes: não há pendência.
7. Congelar a relação de um recorte com coincidência sem ato: recusado, e a recusa diz quantas são e
   onde decidir. O recorte vizinho, sem coincidência, congela.
8. Ato "mesma pessoa": a relação congelada traz um participante, o da regra, e o critério publicado
   diz que inscrições sem efeito não entram.
9. Ato "pessoas distintas": as duas participam, cada uma com o seu número.
10. O ato de decisão não se altera nem se exclui; a mudança é outro ato, com motivo.
11. Quem não tem a capacidade não decide; fora do escopo do Processo, a resposta é a de recurso
    inexistente.

**Depois do efeito**

12. Coincidência decidida depois do congelamento e antes do sorteio: relação sucessora, com motivo.
13. Coincidência decidida depois do sorteio: a ordem dos demais não muda entre si; segue a inscrição
    da regra, ainda que a outra esteja mais bem colocada; nenhum sorteio novo.
14. Convocação que alcançaria duas inscrições do mesmo CPF sem ato: recusada.

**União de contas**

15. Quem controla as duas contas as une e passa a ver, por qualquer credencial, todas as inscrições,
    cada uma com a conta que a enviou.
16. Depois da união, nenhuma Inscrição, documento, recurso ou evento de trilha anterior mudou — nem
    o titular gravado.
17. Tentar unir informando endereço que não é de conta alguma: mesma resposta do caminho feliz.
18. Código pedido para entrar ou para adicionar e-mail não serve para unir.
19. Unir contas que têm inscrição enviada no mesmo Perfil: a tela diz antes qual seguirá; confirmada,
    a pendência recebe a proposta pela regra.
20. Depois da união, abrir segunda inscrição no mesmo Perfil pela outra conta é recusado, e o teto do
    Edital conta as duas contas.
21. Contas com CPFs declarados diferentes não se unem por autoatendimento.
22. Todas as credenciais das duas contas são avisadas da união, e ela pode ser desfeita por ato.
23. Conhecer o CPF de alguém, e nada mais, não dá acesso a inscrição, documento ou conta dele por
    caminho nenhum.

**Recuperação**

24. Quem perdeu o e-mail antigo pede a recuperação pela conta nova; o endereço antigo é avisado; o
    efeito só vem depois do prazo de espera e do ato motivado.
25. Pedido de recuperação contestado pelo endereço antigo dentro do prazo não produz efeito.

**Abuso**

26. Terceiro envia por último com o CPF do titular: a inscrição do titular **não** perde efeito sem
    ato de autoridade.
27. O contador de tentativas de qualquer prova incide sobre quem tenta, e nunca sobre a conta alvo.
