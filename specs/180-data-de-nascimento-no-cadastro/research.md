# Pesquisa: A data de nascimento entra no cadastro do candidato

As decisões de produto estão na spec (D-001 a D-003). Aqui ficam as escolhas técnicas, cada uma com
o que foi lido no código em 17/11/2026, sobre a `main` em `3afb6702`.

## R1 — O núcleo é a regra única de "falta dado", e nenhuma rota nova é necessária

**Escolha**: acrescentar a data a `credenciais.falta_o_nucleo`.

**Por quê**: as duas portas que levam a "Seus dados" já perguntam a ela: a volta do código de acesso
a caminho de uma vaga (`portal/views.py`, depois de `abrir_sessao`) e `portal:inscrever`, antes de
abrir o rascunho. O cadastro antigo sem data cai nas mesmas portas, e a tela mostra nome e CPF já
preenchidos porque `meus_dados` sempre os carregou do registro (FR-8302, UX-1001).

**Alternativas recusadas**: uma tela própria de "complete seu cadastro" (duplicaria "Seus dados");
pedir no login (contraria a FR-005 da `010`, que só cobra dado a caminho de uma vaga).

## R2 — A data congela pela mesma regra do CPF

**Escolha**: `gravar_nucleo` só grava a data enquanto `cpf_congelado` for falso; a tela a mostra
somente leitura depois, com a mesma frase de atendimento do CPF (D-001).

**Por quê**: a regra já existe, é lida a cada requisição e tem frase pronta. Uma função
`data_congelada` seria sinônimo, e dois nomes para a mesma regra divergem com o tempo. O código
chama a mesma função, e o comentário diz que ela congela os dois.

**Caso pensado**: identidade com inscrição enviada antes da `180` e sem data. Com a regra literal,
ela nunca conseguiria informar a data, porque o CPF já congelou. **A regra é: congela a data que
existe.** Data vazia pode ser informada uma vez, mesmo com inscrição enviada; preenchida, congela.
Isso cumpre a FR-8302 para quem já se inscreveu antes e não abre correção livre.

## R3 — A inscrição recebe a data no ato do envio, e não no rascunho

**Escolha**: `Inscricao.data_nascimento` (anulável) é escrita na `compare_and_swap` de
`_gravar_o_ato`, lida do `CandidateIdentity` do titular dentro da mesma transação.

**Por quê**: "acompanha o rascunho, congela no envio" (a FR-014 da `010`) tem, para nome e CPF, a
cópia em `gravar_dados`. Para a data, copiar no rascunho criaria uma janela em que o cadastro
corrigido e o rascunho divergem até a pessoa gravar de novo. Ler no ato dá o mesmo efeito sem a
janela. E é a única escrita permitida pelo gatilho da `inscricoes/0007`, que só deixa passar a
linha cujo `OLD.status` é RASCUNHO.

**A recusa** (FR-8303) também mora no comando, antes de `_gravar_o_ato`: `DomainError`
`birth_date_required`, 422, com a frase "Falta informar sua data de nascimento em Seus dados." A
revisão do portal a antecipa: a linha "Data de nascimento" aparece com "Falta informar" e o link,
como já aparecem Nome e CPF "dos seus dados".

**Fonte da data no comando**: o contrato `IdentidadeDoCandidato` que a view passa, e que ganha o
campo. Mudou na implementação: a primeira versão desta pesquisa lia o `CandidateIdentity`, mas o
contrato é remontado do registro a cada requisição (`contrato_de`), e é dele que o comando já lê nome,
CPF e e-mail. Ler a data de outro lugar daria duas fontes para o mesmo ato, e obrigaria cada teste
que monta um contrato a gravar também uma linha de identidade.

## R4 — O campo é texto com máscara de data, e não o seletor nativo

**Escolha**: `<input type="text" inputmode="numeric" autocomplete="bday">`, que aceita `dd/mm/aaaa`
e também `aaaa-mm-dd`, a forma em que alguns navegadores preenchem `bday`. A leitura fica em
`inscricoes/domain/pessoais.py`, ao lado de `cpf_valido`.

**Por quê**: o seletor nativo de data abre no mês corrente no Android, e chegar a 1990 custa dezenas
de toques; é o que a UX-1000 recusa. O requerimento usa `type="date"` e não muda: lá a pessoa já
passou pela jornada, e mudar aquele campo é outra conversa.

**Recusas** (FR-8305, FR-8307), na ordem:
1. vazio → "Informe sua data de nascimento.";
2. fora do formato, ou ano com menos de quatro dígitos → "Informe a data como dia/mês/ano, com o ano
   completo — por exemplo, 07/03/1998.";
3. data inexistente → "Esta data não existe. Confira o dia e o mês.";
4. hoje ou depois → "A data de nascimento precisa ser anterior a hoje.";
5. mais de 120 anos → "Confira o ano: a data indica mais de 120 anos."

"Hoje" é a data local de Brasília (`timezone.localdate()`), e não UTC; a lembrança de 11/11 diz que
data em UTC falha à noite.

## R5 — A conferência é um POST que responde uma página privada

**Escolha**: `POST /gestao/inscricoes/<id>/conferir-identidade` com `motivo`. A regra fica em
`inscricoes/application/consulta.py` (`identidade_para_conferencia(actor, inscricao_id, motivo)`),
que reusa o escopo de `inscricao_para_consulta` (`CONSULTAR` e Edital no escopo), recusa motivo vazio
ou só com espaços e grava `CONFERIR_IDENTIDADE` com `reason=f"Conferência de identidade: {motivo}"`
(motivo cortado em 300 caracteres). Ela devolve CPF formatado e data. A view responde com
`marcar_como_privada`, e o template não tem link nem formulário que repita a revelação por GET.

**Por quê**: um GET ficaria no histórico do navegador e em registros de acesso com o identificador;
o POST com CSRF obriga o gesto. Reusar a permissão do detalhe é a D-002 ("quem já abre o detalhe").

**O que vai na trilha**: o motivo, e não CPF nem data (FR-8316). O motivo é texto livre da equipe, e
a tela diz "não escreva CPF nem data aqui".

**Negativas**: inscrição inexistente ou fora do escopo responde como o detalhe (404), e o ator sem
a permissão recebe o 403 do detalhe. Linha nova no inventário de negativas da `033`
(`test_gramatica_das_portas.py`). Motivo vazio volta o detalhe com a recusa, em 422, sem revelar
nada.

## R6 — O requerimento nasce com a data do cadastro

**Escolha**: em `requerimentos/application/preencher.abrir_rascunho`, quando o requerimento é
**criado** e `_copiar_para_a_frente` não trouxe data, preencher `data_de_nascimento` com a do
`CandidateIdentity` do titular (D-003).

**Por quê**: só na criação. Preencher a cada abertura apagaria a correção que a pessoa fez no
requerimento, contra a D-003 ("alterável ali, sem mudar o cadastro"). O que veio de um requerimento
anterior (`_copiar_para_a_frente`) vence, porque é declaração mais recente da própria pessoa naquele
documento.

## R7 — As fixtures ganham uma data padrão

**Escolha**: `tests/fixtures/candidato.registrar` grava `data_nascimento=date(2000, 1, 1)` nos
`defaults`, e as construções diretas de `CandidateIdentity` nas fixtures e no `seed_demo` também. Os
casos desta feature criam identidades **sem** data explicitamente.

**Por quê**: a regra nova faz toda identidade de teste "faltar o núcleo" e todo envio de teste ser
recusado. A causa é uma só, e se conserta na fixture (ver o risco no plano).

## R8 — A conferência aparece na trilha do Edital, e só ela

*Acrescentada na implementação da história 3, em 17/11.*

**O que foi lido**: `auditoria/selectors.trilha_do_edital` reúne o Edital, as Retificações e os atos
da condução (`_atos_da_conducao`). **Nenhum registro auditado sob a inscrição entra ali** — nem os
atos do candidato, nem `CONSULTAR_DOSSIE` da `115`. Gravada só como a R5 descreve, a conferência
ficaria no banco e em tela nenhuma, e o SC-2906 ("aparece na trilha com motivo") e o passo 5 do
roteiro não se cumpririam para quem audita.

**Escolha**: `trilha_do_edital` passa a consultar por um `Q` que soma, aos identificadores de sempre,
os registros com `aggregate_type="Inscricao"`, `operation="CONFERIR_IDENTIDADE"` e a inscrição entre
as do Edital (subconsulta). A frase do registro leva o **protocolo**, porque a tela mostra o tipo do
agregado e não o identificador: sem ele, "qual inscrição" (FR-8316) estaria no banco e não na tela.

**Alternativas recusadas**:
- pôr a inscrição entre os identificadores da trilha: traria tudo o que é auditado sob ela (os atos
  do candidato no rascunho, cada abertura do dossiê) e mudaria o que a tela mostra por uma razão que
  não é desta feature;
- auditar a conferência sob o Edital: a FR-8316 pede "qual inscrição", e o modelo de dados já diz
  que o agregado é a inscrição;
- acrescentar a `_atos_da_conducao`: o relatório do Edital (`interface/relatorio_trilha.py`) conta os
  atos dela como registro posterior ao desfecho, e uma conferência é leitura registrada, e não ato
  do certame.

**Custo**: nenhuma consulta a mais na página; a subconsulta vai no mesmo `SELECT`.

## R9 — O motivo é texto livre, e a tela pede que não se escreva CPF nem data nele

*Registrada na implementação da história 3.* A FR-8316 proíbe gravar CPF e data na trilha, e o
sistema não os grava. O motivo, porém, é digitado pela equipe, e nada impede alguém de escrever ali
o CPF que acabou de ler. A R5 decidiu pela dica na tela ("Não escreva CPF nem data aqui"), e a
implementação a seguiu sem acrescentar filtro: recusar motivo que contenha o CPF da inscrição seria
requisito novo, e fica como **ponto para decisão do usuário**, e não como escopo desta história.
