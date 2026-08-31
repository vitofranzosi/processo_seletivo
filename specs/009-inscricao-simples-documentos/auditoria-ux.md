# Auditoria de percurso — 009 Inscrição Simples e Documentos do Candidato

**Data:** 31/08/2026 · **Base:** branch `claude/spec-009-inscricao-documentos-7a1d00`
**Ambiente:** banco `ps_demo_009` recém-semeado, servidor em `localhost:8009`,
`ARQUIVOS_CANDIDATOS_RAIZ=/tmp/ps-arquivos`, viewport **375 × 812** (celular).

## Como este registro foi produzido, e o que ele não é

O percurso foi feito contra o servidor real: cada passo abaixo é uma requisição HTTP de verdade,
com sessão, CSRF, gravação em banco e escrita em disco. Duas ressalvas de método, ditas por
inteiro:

- O painel do navegador estava oculto durante parte da sessão, e nesse estado o clique por
  coordenada não chega ao elemento. Onde isso ocorreu, o acionamento foi disparado por
  `requestSubmit()` e a escolha de arquivo por `DataTransfer` — **o caminho de servidor é o mesmo**,
  o que foi simulado é apenas o gesto físico. Nada foi inserido diretamente no banco.
- As capturas de tela estão na conversa que gerou este documento. Aqui cada passo traz a
  **transcrição literal** do texto da tela, que é a evidência verificável e reexecutável.

## Resposta direta: o candidato envia arquivos?

**Sim.** Está implementado e foi exercitado de ponta a ponta neste percurso. O que existe hoje:

| Aspecto | Comportamento verificado |
|---|---|
| Onde | Na própria tela da inscrição, um bloco por documento exigido — sem tela separada |
| Formato | **Somente PDF**; qualquer outro é recusado |
| Tamanho | **10 MB** (`ARQUIVOS_CANDIDATOS_LIMITE_BYTES`, configurável) |
| Quantidade | **Um arquivo por requisito**; reenviar substitui |
| Quais requisitos | Calculados por Perfil e modalidade — quem não concorre à reserva não vê o documento da reserva |
| Onde fica | Armazenamento privado fora do diretório público; a URL do arquivo não existe |
| Quem abre | Só o titular da inscrição e a gestão com permissão — verificado a cada requisição |
| Depois do envio | Congelado: nem substituir nem remover |

Foi exercitada também a **recusa instrutiva de foto de celular** — o caso real mais frequente:

> Este arquivo é uma imagem (JPEG), e não um PDF — é o que o celular produz ao fotografar um
> documento. Converta a imagem em PDF e envie novamente.

## O percurso, passo a passo

**Passo 1 — Vitrine (`/selecoes/`).** Lista as seleções com inscrições abertas. Sem identificação,
sem login.

**Passo 2 — Seleção (`/selecoes/<edital>/`).** `Processo Seletivo Simplificado 2026 · PS-DEMO-2026 ·
Edital 01/2026 · Unidade: CEFOR`, tarja `Inscrições abertas até 20/09/2026 às 18h55`, botão
`Ler o Edital completo (PDF)` e os dois Perfis com vagas, localidade, concorrência e requisitos.
Tudo isso é público e visível antes de qualquer identificação.

**Passo 3 — Identificação (`/selecoes/identificar?destino=…`).** Acionar `Inscrever-se` leva à
identificação com o destino preservado. A tela declara-se demonstração:
`Ambiente de demonstração. A autenticação oficial ainda não foi integrada…`

**Passo 4 — Recusa de validação.** CPF inválido é recusado com o campo preenchido preservado.

**Passo 5 — Volta ao ponto de origem.** Concluída a identificação, o candidato **não** cai na home:
vai direto para a inscrição da vaga de onde saiu (302 → `/selecoes/inscricoes/<id>/`).

**Passo 6 — Sua inscrição.** Nome, CPF e e-mail já vêm preenchidos, com a explicação
`Estes dados vêm da sua identificação e não precisam ser digitados de novo.` O único campo próprio
é `Telefone (opcional)`. Concorrência oferece as modalidades do Perfil.

**Passo 7 — Documentos.** `0 de 3 documentos obrigatórios enviados.` — três blocos:
`Documento de identificação com foto`, `Diploma de graduação`, `Autodeclaração étnico-racial`
(este último só porque a modalidade escolhida foi a reserva).

**Passo 8 — Revisão prematura.** Pedir a revisão sem documentos é recusado, e a recusa **nomeia o
que falta**, um a um.

**Passo 9 — Foto de celular recusada.** JPEG enviado → recusa instrutiva citada acima. Nada do que
já estava enviado se perde.

**Passo 10 — Três PDFs enviados.** Cada envio marca o requisito com `✓`, mostra nome e horário do
arquivo, e oferece `Substituir o arquivo` e `Remover`. Contador chega a
`3 de 3 documentos obrigatórios enviados.`

**Passo 11 — Revisão.** Oportunidade, dados pessoais, os três documentos sob seus requisitos, as
duas declarações e o aviso `Depois de enviada, a inscrição não pode ser alterada.`

**Passo 12 — Envio sem declarações.** Recusado:
`As duas declarações são obrigatórias para enviar a inscrição.` Nada do que foi preenchido se perde.

**Passo 13 — Comprovante.** `✓ Inscrição realizada · Protocolo INS-2026-6N5SFREZ`, com processo,
edital, perfil, concorrência, candidato, CPF, instante do envio e os documentos apresentados.

**Passo 14 — De volta à seleção.** O card do Perfil passa a exibir
`✓ Inscrição enviada · Ver comprovante`.

**Passo 15 — Segunda vaga, sem redigitar nada.** Acionar o outro Perfil abre uma segunda inscrição
já identificada. Como o Técnico de Laboratório tem modalidade única, a tela mostra
`Ampla concorrência` como texto fixo com a explicação `É a única modalidade prevista para esta
vaga.`, e exige `0 de 1 documento obrigatório` — a aplicabilidade por Perfil e por modalidade
funcionando à vista.

**Passo 16 — Gestão.** Como `Ana Coordenadora — Gestor`: o Edital publicado oferece
`Inscrições recebidas (2)`; a lista traz protocolo, candidato, **CPF mascarado `***.456.789-**`**,
Perfil, concorrência, `3 de 3` e a data de envio; o detalhe traz os dados, a **versão do Edital
aceita** (`vigente desde 31/08/2026 18h55`) e cada arquivo **sob o requisito que atende**, com
`Visualizar` e `Baixar`.

## O que o percurso comprova

| Verificação | Evidência |
|---|---|
| Titularidade decide o acesso (FR-071) | Outra identidade autenticada recebe **404** na inscrição, no comprovante **e no arquivo** |
| Endereço não autoriza | Sessão anônima com o UUID correto: **404** |
| Entrega privada (FR-075) | `Content-Type: application/pdf`, `inline`, `Cache-Control: no-store, no-cache, must-revalidate, private` |
| Auditoria sem PII (FR-074/078) | Trilha `CRIAR → GRAVAR → ANEXAR ×3 → GRAVAR → SUBMETER`, autor `demo:25bf5596…` (HMAC); **zero** registros com CPF em claro |
| Versão congelada (FR-059a) | O detalhe administrativo mostra a versão aceita no ato, não a vigente |
| Guarda de produção (FR-024) | `PORTAL_IDENTIDADE_DEMO` recusa a subida em `config/settings/production.py:94` |
| Sem rolagem horizontal (SC-UX-004) | `documentElement.scrollWidth` = 375 = viewport, no fluxo do candidato |
| Nada redigitado (SC-UX-004/SC-004) | Segunda inscrição abre com nome, CPF e e-mail já preenchidos |

## Defeitos confirmados

> **Estado em 31/08/2026:** os cinco foram corrigidos e travados por teste. Cada um traz abaixo o
> que mudou e como a correção é verificada.

### D1 — O aviso "Enviando… não feche esta página" fica visível o tempo todo (alta)

`base.html:81` declara `.progresso{display:flex;…}`. Uma regra de classe vence o `[hidden]` do
navegador, e o `<p class="progresso" hidden>` de `_documentos.html:53` **nunca** se esconde. Medido:
`{hidden_no_html: true, display_computado: "flex", visivel: true}`.

O efeito é o oposto do pretendido por SC-UX-006: em vez de tranquilizar durante o envio, uma barra
vazia e um alarme permanente aparecem sob **cada** requisito, em repouso. Numa vaga com três
documentos são três avisos falsos de "não feche esta página" na primeira visita.

**Corrigido.** `.progresso[hidden]{display:none}` em `base.html:81`. Verificado no navegador:
`display` computado `none`, elemento sem caixa. Travado por
`test_o_aviso_de_nao_fechar_a_pagina_fica_escondido_em_repouso`.

### D2 — A ação principal aparece antes do trabalho que ela conclui (alta)

Em `inscricao.html` o botão `Revisar inscrição` está na linha **77** e o bloco de documentos na
linha **84**. O candidato lê, nesta ordem: seus dados → concorrência → **botão verde grande** →
"Documentos necessários · 0 de 3". Quem obedece à hierarquia visual aciona o botão antes de enviar
qualquer arquivo e é recusado — foi exatamente o que aconteceu no passo 8.

A causa é técnica: o bloco de documentos usa formulários próprios e não pode ficar dentro do
`<form>` dos dados — aninhar formulários é proibido em HTML.

**Corrigido** com o atributo `form=` do HTML5: o formulário dos dados ganhou
`id="dados-da-inscricao"` e o botão passou a ser renderizado **depois** do bloco de documentos,
associado a ele por `form="dados-da-inscricao"`. Travado por
`test_a_acao_principal_vem_depois_dos_documentos`.

### D3 — Quantos documentos faltam está abaixo da dobra (alta — viola SC-UX-003)

SC-UX-003 exige que a tela informe, **sem rolagem adicional**, para qual Edital e Perfil a inscrição
é *e quantos documentos faltam*. Medido em 375 × 812, no Perfil mais simples (um documento):
contador a **969 px** do topo, dobra em **812 px** — 157 px fora da vista. No Perfil com três
documentos e escolha de modalidade a distância é maior.

**Corrigido.** Um resumo de estado (`_resumo_documentos.html`) passou a aparecer logo abaixo do
cabeçalho: *"Faltam 2 de 3 documentos obrigatórios · Ver quais"*, ou a confirmação quando todos
chegaram. Medido depois: **203 px** do topo, contra os 969 px de antes.

Ele vive fora do `#documentos` e por isso não seria alcançado pela troca do htmx; volta junto com
o bloco por `hx-swap-oob`. Sem `role=status`, para não anunciar duas vezes a quem usa leitor de
tela. Travado por `test_quantos_documentos_faltam_aparece_junto_ao_cabecalho` e
`test_o_resumo_do_cabecalho_acompanha_o_envio`.

### D4 — A tabela de inscrições estoura o layout em tela estreita (média)

Na consulta administrativa em 375 px: tabela com **903 px** dentro de um container de **375 px**,
`overflow-x: visible` — a página inteira rola na horizontal (`body.scrollWidth` 927). Não viola
SC-UX-004, que fala do fluxo do candidato, mas quebra a leitura para quem confere inscrições pelo
celular.

**Corrigido.** Contêiner `.tabela-rolavel{overflow-x:auto}` em volta da tabela: ela rola dentro
de si mesma e a página não rola mais na horizontal (`documentElement.scrollWidth` = 375 = viewport).
Travado por `test_a_tabela_larga_rola_dentro_de_si_mesma`. As demais tabelas da interface
administrativa não foram tocadas — a medição foi feita nesta.

### D5 — Rascunhos entram na conta de "Inscrições recebidas" (média)

`acoes.py:86` conta `Inscricao.objects.filter(edital=edital)` sem filtrar situação. O painel anuncia
`Inscrições recebidas (2)` quando **uma** foi enviada e a outra é um rascunho vazio, aberto e
abandonado segundos antes. A lista repete o número no título (`Inscrições — 2`).

Isso tem dois custos. O gestor não sabe quantas inscrições realmente recebeu — numa seleção real,
centenas de rascunhos abandonados inflam o número. E os dados pessoais de quem **não** entregou
nada à administração ficam visíveis para ela, o que é difícil de sustentar pela finalidade
declarada em FR-076.

FR-067 pede a coluna `situação`, o que justifica **mostrar** rascunhos; FR-066 pede "o total
recebido", o que não os inclui. A spec é ambígua aqui e a implementação escolheu um lado sem dizer.

**Corrigido.** O rótulo da ação e o título da lista passaram a contar apenas as submetidas, e os
rascunhos foram para uma seção própria — *"Em preenchimento — N"*, com a explicação de que não são
inscrições recebidas e podem nunca ser enviados. Travado por
`test_rascunho_nao_conta_como_inscricao_recebida` e
`test_a_acao_do_edital_conta_apenas_as_inscricoes_enviadas`.

**O que a correção não decide:** os dados pessoais de quem abriu rascunho e não entregou nada
continuam visíveis para a gestão, agora sob rótulo honesto. Ocultá-los é decisão de produto, não
de implementação, e depende da política de retenção que L11 registra.

## Lacunas e oportunidades, por prioridade

> **Estado em 31/08/2026:** as três de maior impacto — L1, L2 e L4 — foram corrigidas e travadas
> por teste. As demais seguem abertas.

**L1 — O comprovante não era levável (alta). Corrigido.** A tela final oferecia apenas `Voltar à
seleção`: nenhum `Imprimir / salvar em PDF`, nenhuma frase dizendo como reencontrar o protocolo.
Quem fechava a aba ficava com a sensação de ter perdido o comprovante.

A página já era imprimível — `@media print` na base tira cabeçalho e ações. O que faltava era o
caminho: num celular, "imprimir ou salvar em PDF" está atrás do menu do navegador, e quem acabou de
se inscrever não vai procurá-lo. Agora há o botão, a orientação de guardar o protocolo e a frase
que diz como voltar (`identifique-se com o mesmo CPF`). O botão nasce `hidden` e só aparece quando
o script carrega: sem JavaScript não fica botão morto na tela. Travado por
`test_o_comprovante_pode_ser_impresso_e_reencontrado`.

**O que continua faltando:** a cópia por e-mail, que depende de serviço de envio ainda inexistente
no projeto.

**L2 — A recusa não era anunciada a quem não vê (alta). Corrigido.** A recusa das declarações
aparecia no topo, mas o elemento não recebia foco — medido:
`{focado: false, aria_live: null, activeElement: "BODY"}`. `role=alert` anuncia o que **muda** numa
página já carregada, não o que já veio no HTML da resposta; para leitor de tela o envio
simplesmente não acontecia e nada era dito.

Agora o resumo recebe o foco por script, lista **apenas** a declaração que falta com link para ela,
e a caixa faltante ganha `aria-invalid`. Verificado no navegador:
`{foco_no_alerta: true, ciencia_invalida: "true", veracidade_invalida: null,
links: ["#ciencia → Declaração de ciência do Edital"]}`.

No caminho apareceu um segundo defeito, do mesmo ponto: **a recusa apagava a declaração já
marcada** — quem marcava uma das duas reencontrava as duas em branco, contra SC-UX-007. As duas
correções estão travadas por `test_a_recusa_das_declaracoes_recebe_o_foco_e_aponta_o_que_falta` e
`test_a_recusa_nao_apaga_a_declaracao_ja_marcada`.

**L3 — Nenhum indicador de etapa (média).** O candidato nunca sabe em que ponto está nem quanto
falta. Identificação → dados → documentos → revisão → comprovante são cinco momentos sem nome. Um
indicador de três passos reduz abandono num público que se inscreve uma vez na vida.

**L4 — O CTA dominante da página era o PDF (média). Corrigido.** Na tela da seleção, `Ler o Edital
completo (PDF)` usava o mesmo verde sólido (`rgb(21,128,61)`) dos botões de inscrição e era o
**único** botão preenchido na primeira dobra — o de inscrever-se está a 795 px. Quem chegava pelo
celular via como ação principal "baixar um PDF de cem páginas".

Agora é ação secundária de verdade: contorno verde sobre fundo branco (`rgb(255,255,255)` com borda
e texto em `rgb(20,108,55)`), e o único elemento preenchido da página passa a ser a inscrição.
Travado por `test_ler_o_edital_nao_disputa_a_decisao_com_inscrever_se`.

**O que continua faltando:** a chamada de inscrição ainda começa fora da dobra em 375 px. Trazê-la
para cima exigiria decidir o que fazer quando o Edital tem vários Perfis — é decisão de produto, não
de estilo.

**L5 — A recusa de imagem não diz como converter (média).** A mensagem é boa: nomeia o formato,
explica a causa e diz o que fazer. Falta o **como** para quem não sabe — em iPhone, `Compartilhar →
Imprimir → Salvar em PDF`; em Android, o próprio app de Arquivos ou a câmera do Google Drive. Duas
linhas atrás de um `<details>` resolvem, e este é o erro mais comum de candidato.

**L6 — Requisito já enviado ocupa a tela como se não estivesse (média).** Depois do envio, o bloco
continua exibindo o formulário de substituição aberto: ~850 px por requisito, ~2 500 px de rolagem
com três documentos completos. **Correção:** colapsar para arquivo + ações discretas.

**L7 — Documentos exigidos são invisíveis antes de se identificar (média).** A tela pública lista
requisitos de titulação, mas não diz quais **arquivos** serão pedidos. Quem quer saber o que
preparar precisa se identificar primeiro. Uma linha por Perfil — "serão pedidos: identidade,
diploma" — reduz a inscrição interrompida na metade.

**L8 — Cartão da vaga clicável só no botão (baixa).** Nome do Perfil e cartão inteiro não são
alvo; em celular isso custa toques.

**L9 — `novalidate` desliga a validação nativa (baixa).** A decisão é defensável — uma única
gramática de erro, no servidor —, mas custa o retorno imediato de campo. Vale reavaliar para os
campos triviais (e-mail, obrigatórios), mantendo o servidor como autoridade.

**L10 — Acesso administrativo a documento não é auditado (média, decisão de produto).** FR-077 audita
os atos do candidato e dispensa a consulta pública; sobre a **consulta administrativa** a spec é
silenciosa, e não há registro. Hoje não é possível responder quem abriu o documento de quem. Para
dado sensível de candidato — inclusive autodeclaração étnico-racial — isso costuma ser exigido em
auditoria. Não é defeito da implementação: é requisito ausente.

**L11 — Retenção e descarte continuam sendo precondição não implementada (média).** A própria spec
declara (FR-076, linha 80) que a política de retenção fica fora desta feature. O percurso mostra o
custo concreto: rascunhos com CPF e e-mail já se acumulam a partir do primeiro dia. Antes da
implantação real, alguém precisa decidir prazo e rotina.

**L12 — Uma pessoa pode declarar-se outra (conhecido, declarado).** O provedor de demonstração
aceita qualquer CPF sem prova de titularidade. Está corretamente rotulado na tela, e
`config/settings/production.py` recusa a subida com ele ligado. Registrado aqui só para que a
integração com o provedor real permaneça visível como bloqueio de implantação, não como melhoria.

## O que não foi verificado neste percurso

- Envio de arquivo grande em rede lenta (o progresso real de `htmx:xhr:progress`), simulado apenas
  nos testes automatizados.
- Retificação do Edital publicada com rascunho aberto — o aviso de nova versão e o reconhecimento.
- Navegação completa por teclado e leitor de tela de ponta a ponta; foram medidos pontos isolados
  (L2), não a jornada inteira.
- Encerramento do período com rascunho em aberto.
