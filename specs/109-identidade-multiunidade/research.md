# Research: Identidade institucional preparada para mais de uma unidade (109)

As decisões técnicas desta feature, com a alternativa descartada e o custo, e as perguntas que ficam
com o usuário. O inventário que as motivou está em [`inventario.md`](inventario.md).

## D-001 — Um resolvedor só, no `unidades`, sem memória entre requisições

`unidades/application/identificacao.py` responde três perguntas: a identificação de uma unidade, a
da implantação e o canal de atendimento de uma unidade, com a recaída no global. Telas, mensagens e
o assistente de dúvidas perguntam a ele, e só a ele.

**Uma leitura do registro por pedido, e não memória do processo.** O registro muda pelo comando de
sincronização, que roda **noutro processo**; uma memória no servidor envelheceria em silêncio até o
próximo reinício, e quem acabou de sincronizar veria a sigla antiga — a mesma armadilha do banco
reaproveitado que o `CLAUDE.md` já documenta. A tabela tem uma linha por unidade, e a leitura é pela
chave.

**Preguiçosa nas molduras.** A identificação entra no contexto dos templates como objeto preguiçoso,
como o nome do ator na `107`: o fragmento que o htmx troca não desenha moldura e não consulta nada.

*Descartado*: guardar a sigla na sessão ao identificar. O seletor dos testes reescreve o escopo da
sessão depois de identificar (`tests/interface/conftest.py::identificar`), e a sigla guardada ficaria
de outra unidade — exatamente o vazamento que a FR-3219 proíbe.

## D-002 — A implantação é a unidade ativa quando há uma só

A regra do título da vitrine (FR-1611 da `072`), estendida ao portal, à página de acesso, à 404 e às
mensagens da conta. Com o Cefor sozinho, ela reproduz o que está escrito hoje; com duas unidades, a
moldura diz "Ifes" e não escolhe. Não há atributo novo para dizer "qual unidade é a da implantação".

*Descartado*: um campo "unidade da implantação" no registro. Seria atributo sem uso enquanto houver
uma unidade, e com várias seria a escolha que a P-1 deixa ao usuário.

## D-003 — O canal da unidade é opcional, e o global continua sendo o da instituição

O canal entra no registro como sexto campo, **opcional**: a entrada que não o declara tem canal
vazio, e o `unidades.json` do Cefor não muda. O `PORTAL_ATENDIMENTO` deixa de ser "o" canal e passa
a ser o **canal institucional**: é a recaída das comunicações de Edital e a única fonte das da conta
do candidato. Produção continua a exigi-lo, porque a conta do candidato não tem unidade.

A validação é a mínima que a mensagem exige: texto, uma linha, até 255 caracteres. Que forma o canal
tem — e-mail, telefone, endereço — é política institucional, e a tela já decide como apresentá-lo
(`portal/_atendimento.html`). Ver P-2.

*Descartado*: migrar o canal do Cefor para o registro agora. O valor de produção está no `app.env`,
fora do repositório; copiá-lo para o arquivo versionado seria inventar o dado ou publicá-lo no diff.

*Descartado*: servidor, remetente ou credencial de correio por unidade. O pedido o proíbe, e a
separação fica nos nomes: canal é o que o candidato lê; envio é `EMAIL_*`, um só.

## D-004 — Documento e página de ato leem o ato; mensagem lê o registro no envio

- O PDF e o comprovante já liam as colunas `unidade_*` da Publicação (`060`). O comprovante por
  e-mail passa a ler as mesmas, pela função que o comprovante em papel já usa: os dois são o mesmo
  documento.
- A página pública de uma seleção lê a unidade da Publicação da versão vigente: é a página do ato.
- O aviso e a convocação leem o registro **no momento do envio**, pelo escopo do Edital. São
  comunicação de hoje, e não ato. O aviso congela o texto na confirmação (decisão de congelamento da
  `066`), e é esse congelamento que preserva o que já saiu.

## D-005 — A marca preserva o HTML de hoje

A marca do portal, do topo da gestão e da 404 é `Cefor<span>/Ifes</span>`. Com a sigla do registro,
o template escreve `{{ sigla }}<span>/Ifes</span>`, e sem unidade só `Ifes`. O HTML do Cefor sai
idêntico, e as folhas não mudam.

## D-006 — O domínio recebe a assinatura; não a procura

`avisos/domain/mensagem.py` é função pura (decisão de fronteira da `066`). Ele recebe a assinatura
pronta, como já recebe o canal. Quem a resolve é a aplicação, que sabe o Edital.

## D-007 — O PDF não muda, e a sigla do Ifes fica nos dois lugares que já a tinham

O compositor tem `SIGLA_DA_INSTITUICAO = "Ifes"` e as linhas do Ifes do cabeçalho. Importá-las no
resolvedor arrastaria o compositor para toda página; importar o resolvedor no compositor mexeria no
documento oficial sem necessidade. Ficam as duas constantes, e um teste confere que dizem o mesmo.

## D-008 — Os textos de amostra, de contrato e de demonstração ficam

O que o inventário classificou como T, H ou DT não muda: o `ESCOPO_PADRAO` do seletor, o
`seed_demo`, os `NAMESPACE` de `uuid5`, o `type` dos problemas da API, a aba do Registro Acadêmico e
as frases que falam da amostra de Editais do Cefor. Trocar qualquer um deles mudaria identificador,
contrato ou a demonstração que a homologação usa.

## As dependências do `unidades.json` que permanecem

A orientação de 31/10 mantém o arquivo e o comando como fonte oficial. O que continua dependendo
deles depois desta feature:

| Dependência | Onde | Por quê |
|---|---|---|
| A lista de campos, agora com o canal opcional | `unidades/application/sincronizacao.py`, `CAMPOS` e `validar` | o arquivo inteiro é validado antes de gravar, e só o comando grava |
| "Nenhuma unidade sai do arquivo" | `sincronizar`, `UNIDADE_RETIRADA` | a retirada é recusada; desativar é `"ativa": false` |
| A trilha com ator `implantacao` | `sincronizar`, `record_event` | o autor real é o do commit (M-09 da auditoria) |
| O passo do `make preparar` e do compose | `backend/Makefile`, `docker-compose.yml` | sem ele, a criação de Processo recusa com `unidade_nao_registrada` |
| O código imutável | `unidades/0002`, gatilho | o código é o escopo; vale para qualquer fonte |
| As molduras e mensagens desta feature | `identificacao.py` | leem o banco, e não o arquivo — **não** dependem do JSON |

**O que precisaria ser revisto para administrar as unidades pelo banco**, registrado sem decidir:

1. a decisão R-003 da `060` (arquivo, e não tela), e a de comando, e não data migration;
2. quem administra — o nível global da auditoria de 30/10, e o papel que o exerceria (catálogo da
   `106`), já que hoje ninguém tem permissão sobre unidade;
3. o que acontece com o arquivo: some, vira semente da primeira carga, ou passa a ser exportado;
4. a recusa da retirada e a trilha com ator `implantacao`, que precisariam de ator pessoa;
5. a revisão editorial do cabeçalho, que hoje é diff revisado;
6. o guardião `test_registro.py`/`test_sincronizacao.py`, que fixa o comportamento do comando.

Esta feature não toca nenhum dos seis: o canal entra pelo mesmo arquivo e pelo mesmo comando.

## Perguntas ao usuário

| # | Pergunta | Resposta provisória, implementada | Quando importa |
|---|---|---|---|
| **P-1** | Com mais de uma unidade ativa, o que o portal, a página de acesso, a 404 e o código de acesso dizem? | "Ifes" sozinho (D-002) | antes do segundo campus entrar no registro |
| **P-2** | Qual é a política de atendimento: o Cefor passa a declarar o canal no registro? Uma forma só (e-mail) ou várias? Quem atende a conta do candidato, que não é de unidade? | o Cefor fica no `PORTAL_ATENDIMENTO`; o registro aceita qualquer texto de uma linha | antes do segundo campus |
| **P-3** | A aba `Import_ModeloCefor` da exportação para o Registro Acadêmico vale para os outros campi? | fica como está (contrato externo) | quando outro campus exportar matrícula |
| **P-4** | O nome do serviço no endpoint operacional, "Processo Seletivo e Editais — Cefor/IFES", deve passar a ser do Ifes? | fica (identificação técnica, lida por monitoramento) | sem prazo |
| **P-5** | As frases que falam da amostra — "seções que todo Edital do Cefor tem" — devem ser generalizadas para outra unidade? | ficam: são fatos sobre a amostra | quando houver amostra do segundo campus |
| **P-6** | "No {sigla}" e "do {sigla}/Ifes" presumem sigla no masculino. Basta? | basta para Cefor e campi | se uma unidade tiver sigla no feminino |
| **P-7** | A área do candidato numa inscrição, o resultado e o sorteio devem trocar a moldura pela unidade do Edital, como a página da seleção? | ficam com a da implantação; o conteúdo já diz o Edital | antes do segundo campus |
