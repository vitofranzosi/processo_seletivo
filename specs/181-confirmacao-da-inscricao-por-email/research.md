# Pesquisa: A confirmação da inscrição por e-mail

As decisões de produto estão na spec (D-001 a D-004). Aqui ficam o diagnóstico e as escolhas técnicas,
com o que foi lido no código em 18/11/2026, sobre a `main` em `31d93c47`.

## O diagnóstico: o que o GPS já fazia

| Pergunta do pedido | O que o código mostra |
|---|---|
| Como a inscrição é concluída | `portal/views.py` `revisao` (POST) chama `inscricoes/application/submissao.py` `enviar_inscricao`, que trava o par candidato–Edital e o Edital, revalida, grava o ato (`RASCUNHO` → `SUBMETIDA`), congela os fatos, grava a lista exigida, registra `SUBMETER` na trilha e fecha a reserva de idempotência. Depois, fora da transação, a view chama `_confirmar_por_email` e redireciona ao comprovante. |
| Estados | Dois: `RASCUNHO` e `SUBMETIDA` (`inscricoes/models.py`). O evento que conclui é a transição, uma vez; a inscrição enviada não muda depois (gatilho da `inscricoes/0007`). Não há cancelamento pelo candidato. A situação na área do candidato (`portal/situacao.py`) é derivada: "Inscrição enviada" logo após o envio; "Inscrição recebida", "aceita" etc. depois dos atos da `148`. |
| Já existe e-mail? | **Sim**, desde a `010` (FR-084, FR-084a, FR-084b): `inscricoes/application/mensagem.py`, modelos `inscricoes/templates/inscricoes/mensagem/comprovante.{txt,html}`, na moldura comum de `shared/correio.py` (`121`). Vale para todo Processo, Perfil e concorrência: só há um caminho até `SUBMETIDA`. Os cenários de treinamento da `134` criam enviadas direto no banco, sem mensagem. |
| Comprovante em PDF | **Sim**: `portal:comprovante` (página imprimível) e `portal:comprovante-pdf` (PDF/A desde a `178`, bytes determinísticos, com resumo SHA-256 na tela). Traz protocolo, código de verificação, Processo, Edital, Perfil, concorrência, nome, **CPF**, e-mail, **telefone**, instante, versão do Edital e cada documento com tamanho e SHA-256. Acesso só da titular, com sessão aberta por código enviado ao e-mail. |
| Componentes reutilizáveis | `shared/correio.py` (`compor`, `CABECALHOS`, moldura e estilos em linha); `correio/_botao.html`; `_dados_do_comprovante` (os fatos de página, PDF e mensagem num lugar só); o acesso com `destino` da `121` (FR-3876). |
| Envio assíncrono, registro, falha, retentativa | Só os avisos da `066`/`134`/`167` são assíncronos: tabelas append-only de aviso, destinatário, tentativa e resultado, despachadas por `despachar_avisos` a cada minuto, com trava global e tentativa indeterminada que nunca se repete. A convocação da `019` é síncrona e grava o resultado em `ComunicacaoEmitida`. **A confirmação da inscrição é síncrona e não registra nada**: a falha vai a `logger.exception` sem dizer de qual inscrição, e não há nova tentativa. |
| Pagamento, análise documental, outras condições | Não há taxa nem pagamento no GPS. A análise documental e os demais degraus vêm depois, por ato da comissão, e aparecem na área do candidato; nada fica "pendente" no instante do envio — o envio é recusado enquanto falta documento ou dado. |

### Os defeitos achados

1. **Duplicidade.** `enviar_inscricao` devolve a inscrição já enviada quando a mesma chave de
   idempotência chega de novo (duplo clique simultâneo, duas abas). A view não distingue o ato da
   repetição e chama `_confirmar_por_email` nas duas.
2. **Falha muda.** `enviar_comprovante` engole a exceção e registra só "Falha ao enviar a confirmação
   de inscrição.", sem a inscrição. E **não conta** o retorno de `send()`: um backend que devolve `0`
   sem erro passa por sucesso — a mesma armadilha que `convocacao/application/comunicar.py` já
   documentou e corrigiu.
3. **Vocabulário.** Assunto "Inscrição recebida — ‹protocolo›" e título "Recebemos a sua inscrição"; na
   área do candidato, "Inscrição recebida" é o degrau da relação publicada (`148`). A tela do
   comprovante diz "Inscrição realizada".
4. **Link.** O botão "Rever minha inscrição" leva à vitrine (`portal:vitrine`).
5. **Tela.** O comprovante não menciona a mensagem.

## R1 — A tentativa vive na trilha de auditoria

**Escolha**: cada tentativa é um `RegistroAuditoria` com `aggregate_type="Inscricao"`,
`operation="CONFIRMAR_POR_EMAIL"`, `detalhe={"tentativa": n, "resultado": "ENVIADA"|"NAO_ENVIADA"}`,
`reason` sem endereço. O ator é o candidato (`ator_do_candidato`), porque foi o gesto dele que disparou
o envio — o envio e a nova tentativa.

**Por quê**: é append-only, já é indexada por agregado e instante, e a `134` já grava nela o resultado
de cada envio do aviso de pendência (`avisos/application/despacho.py` `_auditar_o_envio`). Uma tabela
própria duplicaria a trilha para responder uma pergunta que ela já responde.

**Alternativas recusadas**: coluna na `Inscricao` (a enviada é imutável por gatilho, e "estado de
envio" é exatamente a coluna que a `066` recusou); tabela nova (D-002).

## R2 — Uma vez só: trava por inscrição, sem espera, e leitura da trilha antes de enviar

**Escolha**: `confirmar` abre uma transação, **tenta** a trava consultiva da inscrição
(`pg_try_advisory_xact_lock`, por `shared.concurrency.travar_consultivamente(esperar=False)`), lê as
tentativas, **não envia** se alguma foi `ENVIADA` ou se a última é de menos de um minuto, envia e grava
a tentativa. A trava é liberada no commit, depois de a tentativa estar gravada. Quem não consegue a
trava volta sem enviar: outra tentativa da mesma inscrição está em curso, e ela registra o resultado.

**Por quê**: serializa duas requisições da mesma inscrição sem tocar a linha dela (FR-8351). A
primeira redação esperava a trava; a revisão de código de 18/11 mostrou o custo — a conversa com o
servidor de correio acontece sob ela, até o `EMAIL_TIMEOUT`, e cliques repetidos ou várias abas
empilhavam requisições e workers atrás de um servidor fora do ar. O intervalo de um minuto
(`INTERVALO_ENTRE_TENTATIVAS`, FR-8363) limita o mesmo efeito para cliques em sequência. A técnica da
trava passou a morar em `shared.concurrency`, e `submissao._travar_o_par` a usa, com a mesma chave.

**Custo aceito**: a transação fica aberta durante a conversa com o servidor de correio, até o
`EMAIL_TIMEOUT` — uma por inscrição e por minuto, no máximo. Ela só segura a trava consultiva daquela
inscrição: nenhuma linha, nenhuma tabela.

**Contenção** (FR-8352): toda exceção de `confirmar` — a trava, a leitura, `montar_dados`, o commit —
vai ao registro técnico com o identificador da inscrição e devolve `None`. Antes, uma queda de banco
nesse caminho virava 500 com a inscrição já gravada.

**Caso pensado**: a trilha falha depois de a mensagem sair. A gravação vai num ponto de salvamento, e
a falha dela vai ao log; a mensagem já saiu, e a próxima tentativa — se a titular pedir — poderia
duplicar. É o único caminho de duplicidade restante, e exige a trilha falhar com o banco de pé.

## R3 — O remetente conta o retorno e diz de qual inscrição falhou

**Escolha**: `mensagem.enviar_comprovante` passa a devolver `True` só quando `send()` devolve um número
positivo, e aceita `inscricao_id` para o log (`"Falha ao enviar a confirmação da inscrição %s."`). O
endereço continua fora do log.

**Por quê**: FR-8360 e FR-8361, e a mesma correção já feita na convocação.

## R4 — O link leva ao comprovante, e a falta de sessão leva ao acesso

**Escolha**: `endereco` da mensagem passa a ser o endereço absoluto de `portal:comprovante` da
inscrição. A view `comprovante`, sem a chave de sessão do candidato, redireciona a
`portal:acesso?destino=<caminho>` **antes** de consultar a inscrição — exatamente o que a `121` fez na
convocação (FR-3876 daquela feature). A titularidade é conferida na volta, por `_inscricao_do_titular`.
O PDF continua como está: ele não é destino de link.

**Por quê**: o link não autentica (FR-084a da `010`), e a resposta sem sessão não depende do
identificador (FR-8357).

## R5 — A nova tentativa é um POST da titular, na tela do comprovante

**Escolha**: `POST /selecoes/inscricoes/<id>/comprovante/confirmacao` (`portal:comprovante-confirmacao`).
Exige sessão e titularidade (`_inscricao_do_titular`), e inscrição enviada; sem isso, a mesma resposta
de inscrição inexistente. Dentro do minuto depois de uma falha, não chama `confirmar`: guarda a frase
`ESPERE_PARA_TENTAR_DE_NOVO` na sessão, que o comprovante mostra no aviso de falha. Chama `confirmacao.confirmar` com os mesmos dados do primeiro envio e
redireciona ao comprovante (POST → redirect → GET). Se a última tentativa já foi aceita, `confirmar` não
envia nada, e a tela continua dizendo que foi enviada (FR-8351).

**Alternativas recusadas**: nova tentativa automática por comando ou timer (D-003); botão também na
lista "Minhas inscrições" (o comprovante é onde a pessoa vê o aviso, e um lugar basta).

## R6 — O texto da mensagem

**Escolha**: assunto "Sua inscrição foi enviada — Edital ‹número›/‹ano›"; título "Sua inscrição foi
enviada."; o quadro com protocolo e código; os dados (Perfil, concorrência, "Enviada em"); os
documentos; "O que acontece agora", com duas frases que valem em qualquer dia — a primeira redação
dizia "Por enquanto, você não precisa fazer nada", e a revisão de 18/11 a tirou, porque uma nova
tentativa semanas depois a diria a quem já tem passo pendente; o botão "Ver meu comprovante"; a nota de acesso por
código. A ressalva antiga ("O recebimento não implica deferimento…") sai da mensagem e fica no
comprovante (D-004): "Enviada não quer dizer aceita" diz o mesmo sem a palavra do deferimento.

**Por quê**: FR-8353 a FR-8356, UX-1020, UX-1021. O Edital vem de `_dados_do_comprovante`, o mesmo que
alimenta a página e o PDF.

## Recomendações, fora do escopo

- **Mostrar à equipe** o estado da confirmação no detalhe da inscrição, na gestão (a leitura é a mesma
  `confirmacao.tentativas`). Pede decisão de onde, e quem vê.
- **Os dois sentidos de "recebida"** (D-004): decidir se o comprovante como documento passa a dizer
  "enviada" numa versão futura do modelo de PDF, como a `178` fez com o comprovante PDF/A.
