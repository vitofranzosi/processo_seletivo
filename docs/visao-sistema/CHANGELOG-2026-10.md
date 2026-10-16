# Revisão de 15/10/2026 da Visão do Sistema

A documentação descrevia o sistema até a spec 068 (10/10). Desde então entraram na `main` quatro
specs implementadas e uma só especificada, e nenhuma delas aparecia no texto. Esta revisão descreve
como entregues as specs 069 a 072, contra a `main` em `db428b30`, cada uma com o que ainda espera
validação humana. A 073 é citada só como especificada. Também passa a dizer, no início e no estado do
produto, que o sistema não está em produção.

## Como foi conferido

- Cada spec foi lida e confrontada com o código da `main`, e não só com a própria spec. Onde as duas
  divergiam, vale o código. Quatro leituras paralelas, uma por spec, levantaram o que foi entregue, os
  rótulos exatos dos *templates* e as tarefas abertas. As afirmações centrais foram conferidas de novo
  antes de entrar no texto, entre elas:
  - os oito papéis de `PAPEIS` em `interface/identidade.py`;
  - as sete rotas novas em `interface/urls.py`, comparadas com `0edc0f8d`;
  - a guarda `_edital_do_piloto` em `interface/assistente.py`;
  - o comando `excluir_registros_do_piloto` e o prazo de 90 dias;
  - o catálogo `CATALOGO_DA_069`, a `APRESENTACAO` e `APRESENTACOES` em `editais/domain/secoes.py`;
  - o resumo em `publicacoes/infrastructure/apresentacao.py` e as frases da redação 2 em `pdf.py`;
  - os rótulos da vitrine, da página da seleção, do acesso e de `meus_dados.html`;
  - o `503` de `identificar` em `interface/views.py:628-629` e `sem_autenticacao.html`;
  - a ausência de código de LDAP em `backend/`, contra a resposta de 28/08 na spec 002 (T056
    aberta), e o §1 de `doc/implantacao-em-producao-ubuntu.md`.
- Os números de *Maturidade* foram recontados pelo método descrito na própria página. Rodado sobre
  `0edc0f8d`, a base da revisão de 10/10, o método reproduz todos os números publicados naquela
  data. O mesmo vale para a contagem de `Status: Draft`: 58 de 69 em `0edc0f8d`, 63 de 74 hoje.
- **Esta revisão não rodou a suíte, não percorreu o produto no navegador e não chamou o serviço de
  inferência.** A auditoria de consolidação de 15/10, que a encomendou, fez as duas primeiras coisas
  na mesma `main`: a suíte fechou em 11 297 passando e 11 pulados (`db428b30`, com o grupo
  `assistente`, 1312s), e é esse o número que a página traz; e o percurso pelo navegador está no
  relatório da auditoria. Nenhum teste lê `docs/`.
- Todas as âncoras internas têm destino, nenhum `id` se repete, e o HTML fecha as tags que abre.

## O que mudou na documentação

- **Edital em linguagem simples (069).** Entrou nos seguintes lugares:
  - a ficha da Publicação: a descrição administrativa fora do ato, o *“Resumo deste Edital”*, o
    *“Sumário”*, a redação 2 das frases, a fonte embutida, e título, idioma e marcadores no arquivo;
  - *As seções de conteúdo*: os títulos novos das mesmas 22 seções, e as seções reunidas sob as
    perguntas do candidato.

  Também foram corrigidas a lista do que o ato imprime (*“a descrição”* saiu) e duas citações aos
  nomes antigos das seções. A SC-517 entrou como pendente: as frases novas esperam a aprovação do
  responsável pelo produto antes do primeiro Edital real.
- **Fonte de consulta do Edital (070) e piloto do assistente (071).** Entrou a seção nova *O assistente
  de dúvidas do Edital*, no fim de *Processo, Edital e publicação* (âncora `#assistente-do-edital`),
  com o selo *Parcial*. Ela separa as três coisas:
  - a validação interna, sem modelo e sem gravação;
  - o piloto, com papel próprio, chave, conferência da resposta e registros que se excluem 90 dias
    depois do relatório final;
  - o protótipo da Fase C, sem link e sem spec.

  Ela diz também que nada disso é alcançável pelo candidato, e traz as dependências fora do
  repositório, os dois comandos e as tarefas abertas (T046 da 070; T058 a T060 e T065 da 071).
- **Papéis.** São oito: o *Participante do piloto do assistente* entrou na tabela, no glossário
  (*Papel*) e numa nota da matriz.
- **Jornada pública do portal (072).** Os passos 1, 3 e 12 da jornada e a tabela da página pública
  ganharam o que a 072 mudou:
  - o título e os filtros recolhidos da vitrine;
  - o cartão pelo Edital, com a oferta e o prazo de recurso;
  - a volta, o resumo *“O que esta seleção oferece”* e a frase do Requerimento;
  - o acesso que nomeia a vaga e volta a ela;
  - o texto de finalidade de nome e CPF.

  A SC-605 e a FR-1627 entraram como pendentes de validação humana. Ficou falsa, e foi corrigida, a
  lacuna que punha *“Unidade: CEFOR”* na vitrine: a vitrine usa a sigla, e a página da seleção
  ainda não. A rota `/selecoes/` passou a se chamar *Processos seletivos*.
- **O sistema não está em produção.** Agora é dito, sem dramatizar, em cinco lugares:
  - um aviso em *Estado atual do sistema*;
  - o veredito de *Maturidade*;
  - as linhas *Autenticação institucional* e *Implantação*;
  - a fragilidade de autenticação em *Segurança*;
  - a lacuna *Autenticação institucional real* e uma pergunta nova.

  Em todos vão os mesmos três fatos: o `503` sem o seletor de identidade, o LDAP respondido em 28/08 e
  nunca implementado, e a falta de política de retenção.
- **073.** Citada só na linha *Implantação* da maturidade, como especificada e sem implementação na
  `main`.
- **Estado do produto:**
  - 74 pastas de especificação, 94 migrations, 22 módulos (o novo é `duvidas`), 432 arquivos Python de
    aplicação, 166 templates, 849 arquivos de teste e 116 rotas da gestão; o portal segue com 33;
  - as 40 tabelas append-only e os 58 gatilhos não mudaram: os registros do piloto se excluem e não
    entram;
  - 63 das 74 specs dizem `Draft`;
  - *Domínio a domínio* ganhou a linha *Assistente de dúvidas do Edital* e atualizou *Inscrição* e
    *Documento como ato oficial*;
  - *Fechados desde 20/09* ganhou três linhas (ED-05, ED-08 e a sigla da vitrine);
  - entrou a subseção *Abertas desde 10/10*;
  - *Decisões pendentes* ganhou três linhas: as frases da 069, a validação da 072 e a revisão da 070;
  - *Divergências* ganhou a contagem nova de `Draft` e duas linhas sobre a 071: o cabeçalho
    desatualizado e a exclusão parcial.
- **Recursos disponíveis e perspectivas.** Entraram dois cartões, *Edital em linguagem simples* e
  *Assistente de dúvidas, só interno*. O cartão do assistente de nove passos passou a se chamar
  *Composição do Edital*, para não se confundir com o assistente de dúvidas. Entraram também a
  perspectiva *Participante do piloto do assistente* e um *Quero saber…*.
- **Catálogo e glossário.** O catálogo passou de 119 a 123 capacidades, e o glossário de 110 a 115
  termos:
  - Apresentação por perguntas;
  - Assistente de dúvidas;
  - Piloto do assistente;
  - Redação do documento;
  - Resumo do Edital.
- **Perguntas, rotas, dados pessoais e *Quem vê o quê*:**
  - três perguntas novas: produção, assistente e o PDF novo;
  - as sete rotas novas da gestão;
  - a linha das perguntas do piloto em *Dados pessoais*;
  - as trocas do piloto em *Existe só internamente*.

  De passagem, foi corrigida a contagem de rotas da evidência, que dizia 98 desde 30/09.
- **Âncoras.** Nenhuma foi removida. São novas `#assistente-do-edital` e as dos cinco termos do
  glossário.

## O que não foi verificado, e o que ficou de fora

- Nada foi exercitado no navegador nem no serviço de inferência. Ficaram sem reprodução:
  - o comportamento do piloto e do protótipo;
  - a conferência das respostas;
  - o modo simulado.
- Não se conferiu, além do que a 072 registra, a disposição em tela estreita. A 072 registra que, a
  320 px, o resumo da oferta não cabe.
- A 074 não está na `main` e não é mencionada. A implementação da 073 também não está, e não foi
  descrita.
- Achados que ficaram só registrados, sem virar texto próprio:
  - a 070 nunca produz o tipo *“Detalhe em anexo”*, só o aviso;
  - o painel do protótipo não mostra o aviso de serviço externo que a FR-1503 pede da tela do piloto;
  - a produção não exige a `tokenizers` com o piloto ligado (a página diz só que a imagem de
    contêiner não instala o grupo `assistente`).

# Revisão de 10/10/2026 da Visão do Sistema

A documentação descrevia o sistema até a spec 054 (30/09), e contradizia o que entrou depois, em
especial com a 059 e a 066. Esta revisão descreve como entregues as specs 055 a 068, contra a `main`
em `0edc0f8d`. A anterior está em [CHANGELOG-2026-09.md](CHANGELOG-2026-09.md).

## Como foi conferido

- Cada spec foi lida e confrontada com o código da `main`, e não só com a própria spec. Onde as duas
  divergiam, vale o código. Seis leituras paralelas, uma por grupo de specs, levantaram os trechos
  falsos ou incompletos com a evidência no código. As afirmações centrais foram conferidas de novo
  antes de entrar no texto, entre elas:
  - `_reingressou` em `classificacao/application/corte.py`;
  - os papéis e permissões em `interface/identidade.py`;
  - as rotas em `interface/urls.py`;
  - os códigos de `editais/domain/validation.py`;
  - os modelos iniciais e o rodapé do aviso;
  - os rótulos dos *templates* do portal e da gestão.
- Os números de *Maturidade* foram recontados pelo método descrito na própria página. O mesmo método
  rodado sobre `86bbf49`, a base da revisão de 30/09, reproduz os números publicados naquela data. A
  exceção são os arquivos de teste, que tinham sido contados em 29/09.
- **Não se rodou a suíte nem se percorreu o produto no navegador.** O total da suíte (10 408 passando,
  11 pulados) é o medido em 09/10 e registrado no `AGENTS.md`. Nenhum teste lê `docs/`.
- Todas as âncoras internas têm destino, e o HTML fecha as tags que abre.

## O que mudou na documentação

- **Convocação e Requerimento com porta no portal (059).** Ficaram falsas as lacunas que diziam que o
  candidato só chegava à própria convocação e ao Requerimento pedido nela pelo endereço. Elas estavam
  na jornada, na área do candidato, em *Quem vê o quê*, no catálogo, nas perguntas, na maturidade, nas
  lacunas e no tutorial. As caixas vermelhas do diagrama da jornada viraram caixas comuns.
- **Acompanhamento pela situação (063).** O passo 8 da jornada, *O que o candidato vê* em
  Resultados e o glossário citavam frases que o portal não escreve mais: *“Resultado divulgado”* e
  *“Você não foi classificado neste marco.”*. Agora descrevem a situação (rótulo, por quê, o que
  fazer), a *Classificação por lista* e o prazo de recurso de Resultado de Etapa no topo.
- **Resultados por Perfil, etapa e lista (062, PR 255, PR 262).** A lacuna *“o resultado não diz de
  qual lista é”* virou **Parcial**: o portal a diz em toda parte, e a gestão (o histórico e a prévia)
  ainda não. A frase da publicação vigente agora é *“Esta é a versão que vale.”*.
- **Unidades e autoridades (060).** Era falso o *catálogo fixo* de autoridades, com as três entradas
  só de cargo, e `publicacoes/domain/autoridades.py` não existe mais. Entraram:
  - a Unidade, com cabeçalho e local do ato;
  - as autoridades habilitadas com vigência;
  - a tela *Autoridades da unidade* e a permissão `autoridade:gerir`;
  - o quarto passo do `make preparar`.

  A divergência de cargo registrada na 054 deixou de ser de código.
- **Avisos aos candidatos (066).** Eram falsas as afirmações de que o sistema não manda e-mail de
  resultado e de que *“um quinto aviso exige rever a regra”*: a regra foi revista em 09/10. Entraram:
  - o aviso complementar, na tabela de e-mails e em Segurança;
  - o despacho;
  - a chave `AVISOS_AOS_CANDIDATOS`, desligada em produção até a LGPD;
  - a seção *Avisar os candidatos* em Resultados;
  - o *Não confunda* comunicação × aviso;
  - a permissão `aviso:enviar` do Publicador e do Gestor;
  - linhas na matriz, rotas e uma linha em *Operar em escala*.
- **Corte depois do recurso (061).** A obsolescência por *participante reingressou* foi qualificada:
  só o que a ordem lida ainda não cita. O corte emitido sobre a ordem sucessora nasce em dia, e o
  corte obsoleto bloqueia distribuir, concluir e consolidar.
- **O documento do Edital (064, 065, 067, 068).** O que entrou:
  - o que sai idêntico entre Perfis é impresso uma vez, o que corrige o *AX-11* em achados e lacunas;
  - o conflito de numeração impede o Edital e só avisa na Retificação;
  - a remissão sem destino gera aviso;
  - a frase de recurso nomeia o marco;
  - o marco por sorteio não pede nem imprime arredondamento;
  - o Perfil sem vaga imediata não imprime quadro nem reversão;
  - o aviso *“Prazos de recurso a conferir”*.

  A tabela de famílias da validação ganhou duas linhas. A linha *“Casas decimais e Arredondamento
  num marco de sorteio”* saiu de *Configuração sem consumidor*.
- **Polimento (055–058).** Três citações tinham *“(s)”* que a interface não escreve mais. A lacuna
  dos números *“espremidos”* da Ocupação ficou falsa. A ordem dos campos do Perfil na Retificação
  mudou. Corrigido também, de passagem, o *“7 seções textuais”* que a revisão de 30/09 deixou.
- **Produção.** A fragilidade *“não há caminho de produção”* passou a dizer que o caminho está
  escrito em `doc/implantacao-em-producao-ubuntu.md` (30/09) e não está no ar. A própria peça
  declara dois bloqueadores: a autenticação e a política de retenção.
- **Estado do produto:**
  - 69 pastas de especificação, 90 migrations, 40 tabelas append-only, 58 gatilhos (em 24
    migrations, sobre 47 tabelas), 21 módulos, 109 rotas da gestão e 33 do portal;
  - 58 das 69 specs dizem `Draft`;
  - *Fechados desde 20/09* ganhou onze linhas;
  - *Lacunas antigas* ganhou cinco resolvidas e duas parciais;
  - entrou a subseção *Encontradas desde 30/09*;
  - *Decisões pendentes* ganhou três linhas, e a DP-20 encolheu para *como o ato é assinado*.
- **Catálogo e glossário.** O catálogo passou de 102 a 119 capacidades, e o glossário de 101 a 110
  termos:
  - Atribuições do Perfil;
  - Aviso complementar;
  - Conflito de numeração;
  - Despacho;
  - Modelo de aviso;
  - Remissão interna;
  - Situação da inscrição;
  - Subseção comum aos Perfis;
  - Unidade.
- **Âncoras.** Nenhuma foi removida, e as novas são as dos nove termos do glossário.

## O que continua em aberto

Está registrado nas próprias páginas, sobretudo em *Lacunas e decisões em aberto*:

- a reabilitação de quem foi eliminado antes da última Etapa do marco não alcança o corte
  (achado de 07/10, com três saídas para decisão);
- a gestão não diz a lista no histórico de resultados nem na prévia;
- três grafias para o desfecho *Aceite* no portal;
- o reenvio da convocação sugere prazo novo;
- a convocação para heteroidentificação, entrevista e títulos não tem ato;
- a marca do Cefor fora do documento;
- os itens ED-* ainda abertos da auditoria do PDF;
- a regra da reserva no cadastro (RC-58);
- a validação de LGPD que liga os avisos em produção;
- a numeração automática dos parágrafos.
