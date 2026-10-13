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
