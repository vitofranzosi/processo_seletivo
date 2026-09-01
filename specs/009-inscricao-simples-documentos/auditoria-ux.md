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

### D6 — CPF e telefone aceitavam qualquer coisa (alta)

Encontrado por quem usou o sistema, não por este percurso — e é a prova de que uma auditoria feita
por quem escreveu o código tem ponto cego. Três campos passavam lixo:

- **CPF**: só a contagem de dígitos era conferida, e `11111111111` entrava. O CPF decide de quem é
  a inscrição e alimenta o `subject` da auditoria: digitado errado, produz uma identidade que
  ninguém reencontra — a pessoa volta, digita certo, e sua inscrição "sumiu".
- **Telefone**: `28934` era gravado como telefone. Pior, o campo **truncava** entradas longas em
  vez de recusá-las, gravando meio número como se fosse válido. Um número errado custa a vaga: a
  comissão liga, não encontra ninguém e conclui que a pessoa desistiu.
- **Nome**: o rótulo pede o nome completo, e `Joao` passava. O nome vai no comprovante e é por ele
  que a comissão confere o documento apresentado.

Nenhum dos três tinha máscara, o que também não dizia o formato esperado.

**Corrigido.** Os dígitos verificadores do CPF passaram a ser conferidos no domínio
(`inscricoes/domain/pessoais.cpf_valido`), com sequências de dígito repetido recusadas à parte —
elas passam no cálculo e nunca foram atribuídas a ninguém. O telefone exige DDD e dez ou onze
dígitos, ou fica em branco. O nome exige sobrenome. **Os três guardam uma forma só**: o CPF vira
`123.456.789-09` e o telefone `(27) 99999-0000`, venham como vierem — sem isso a mesma pessoa
aparece de dois jeitos nas telas de quem confere.

As máscaras são escritas enquanto a pessoa digita, e o cálculo do CPF é espelhado no cliente com a
mesma mensagem do servidor. Apagar continua funcionando: a máscara é recalculada a partir dos
dígitos, e o cursor nunca fica preso atrás de um parêntese. Sem JavaScript nada se perde — quem
decide é o servidor.

Verificado no navegador: `11111111111` → *"Este CPF não existe. Confira os números digitados."*;
`28934` → recusa com o valor preservado no campo (`(28) 934`) e foco no aviso. Travado por
`test_cpf_inventado_e_recusado_na_identificacao`, `test_primeiro_nome_sozinho_e_recusado`,
`test_telefone_que_nao_e_telefone_e_recusado_em_vez_de_estourar` e mais dez casos de unidade em
`tests/unit/inscricoes/test_pessoais.py`.

**O que isto não é:** prova de titularidade. Um CPF válido continua podendo ser de outra pessoa —
é o que L12 registra, e o que só o provedor de identidade real resolve.

### D7 — O comprovante não parecia um documento, e a sessão não tinha saída (alta)

Os dois vieram de quem usou o sistema, com o PDF impresso na mão.

**O comprovante impresso.** Saía sem qualquer identificação do órgão — o cabeçalho verde da tela é
escondido na impressão, e nada tomava o lugar dele —, com o indicador de etapas impresso junto
(*"Etapa 3 de 3"*, que faz o documento parecer a captura de uma tela pela metade), sem dizer o que
atesta, sem dizer sob qual versão do Edital a inscrição foi feita e sem dizer como conferi-lo. Um
comprovante é lido por quem **não** estava na tela: pode ser apresentado numa banca, anexado a um
recurso, guardado por um ano.

**Corrigido.** No papel aparece um timbre com o Instituto e o Cefor, e some tudo que é navegação.
O protocolo ganhou bloco próprio em monoespaçada. Entraram a versão do Edital aceita, o horário de
recebimento de **cada** documento, e o parágrafo que diz o que o documento prova — e o que não
prova:

> Este comprovante atesta que a inscrição acima foi **recebida** pelo sistema na data e hora
> indicadas, com os documentos listados. O recebimento não implica deferimento: a conferência dos
> documentos e a análise dos requisitos são feitas pela comissão, nos prazos do Edital.

A segunda frase evita o mal-entendido mais caro da jornada — ninguém deve chegar à divulgação do
resultado achando que o comprovante garantia algo sobre o mérito. Fecha com onde conferir o
comprovante. Travado por `test_o_comprovante_se_identifica_como_documento` e
`test_o_papel_nao_leva_navegacao_nem_botao`.

**A sessão sem saída.** O portal nunca ofereceu `Sair`. A rota existia desde a entrega 3 e **nenhum
template a expunha** — quem se identificasse ficava identificado até o cookie expirar. Num
computador compartilhado — laboratório, biblioteca, lan house — a pessoa seguinte começava a
inscrição dela com o CPF de quem estava antes, e a inscrição ia para a identidade errada.

**Corrigido.** O cabeçalho do portal passou a mostrar quem está identificado e a oferecer `Sair`,
por um processador de contexto próprio do candidato — nunca o `ator` da interface administrativa,
que é outro eixo (FR-020, FR-021). Travado por `test_quem_se_identificou_encontra_a_saida` e
`test_quem_nao_se_identificou_nao_ve_saida_nenhuma`.

**Uma correção de teste veio junto:** o `Sair` traz um token CSRF ao cabeçalho, e o teste que
compara byte a byte a recusa de inscrição alheia com a de inscrição inexistente passou a comparar
ruído aleatório. O token é normalizado antes da comparação — a propriedade que importa (não existir
oráculo de existência) continua sendo verificada.

### D8 — A tela da inscrição não tinha desenho (alta)

O julgamento veio de quem olhou a tela pronta: *"está amadora"*. Estava, e o diagnóstico é
específico — não era falta de enfeite, era falta de estrutura.

**O que havia.** Texto corrido do começo ao fim: títulos soltos, pares de rótulo e valor sem
contenção nenhuma, e o campo de arquivo do navegador no meio — *"Procurar… Nenhum arquivo
selecionado"*, com a tipografia do sistema operacional, ao lado de um botão com a tipografia da
página. Nada agrupava nada. Somava-se a isso:

- **duas contagens dizendo a mesma coisa** com palavras diferentes — *"Falta 1 de 1 documento
  obrigatório"* no topo e *"0 de 1 documento obrigatório enviado"* oito centímetros abaixo;
- o campo de telefone com **32 rem de largura** para caber onze dígitos;
- o CPF exibido **sem máscara** (`11111111111`);
- o botão principal encostado no último cartão, sem dizer o que falta para acioná-lo.

**O que mudou.**

Cada seção virou **painel** — fundo, borda, título com linha de base própria. Não é decoração: é o
que permite ler um formulário longo por varredura, que é como se lê no celular.

Os dados da identidade ganharam **rótulo pequeno acima do valor**, em vez de pares lado a lado: o
olho encontra o valor sem atravessar o rótulo, e em 375 px nada precisa de duas colunas.

A contagem de dentro do bloco virou **barra de progresso**. O resumo do cabeçalho continua dizendo
em palavras quantos faltam; a barra diz o mesmo de relance, e o número segue no texto para quem usa
leitor de tela. Uma frase, não duas.

**O campo de arquivo deixou de aparecer cru.** O `input` continua existindo e continua sendo o que
envia — sai de vista mantendo foco e rótulo, e o `label` assume a aparência de botão
(*"Escolher arquivo PDF"*), com o nome do arquivo escolhido ao lado. Verificado no navegador:
`{input_focavel_por_teclado: true, tabindex_efetivo: 0, nome_mostrado: "diploma-2024.pdf"}`.

**`Enviar` nasce secundário e ganha peso quando há o que enviar.** Antes, dois botões verdes
sólidos disputavam a mesma tela; agora o contorno vira sólido no momento em que o arquivo é
escolhido (SC-UX-008).

O telefone ganhou largura proporcional ao que se escreve nele, o CPF passou a ser formatado também
na exibição, e o botão principal ganhou a linha que diz o que falta: *"Você poderá enviar a
inscrição depois de anexar o documento que falta."*

Travado por `test_o_campo_de_arquivo_do_navegador_nao_aparece_cru` e
`test_o_progresso_dos_documentos_e_barra_e_nao_segunda_frase`; a ausência de rolagem horizontal em
375 px e a ordem entre documentos e ação principal seguem cobertas pelos testes de D2 e SC-UX-004.

### D9 — O comprovante listava arquivos sem permitir verificá-los (alta)

O comprovante já se identificava como documento (D7), mas ainda não servia à pergunta que importa
quando alguém precisa confiar nele: **este arquivo é o que foi entregue?** Listar
`documento2.pdf` identifica tanto quanto um nome de arquivo identifica — quase nada. Dois arquivos
com o mesmo nome são indistinguíveis no papel, e é exatamente aí que uma contestação começa.

Além disso o documento passou a ocupar **duas páginas**, e o que caía na segunda folha era
justamente o parágrafo que diz o que ele atesta — a parte que dá valor à primeira.

**Corrigido: cada arquivo passou a ser verificável.**

O resumo SHA-256 já era calculado no envio e guardado com o documento; o que faltava era estar à
vista. Agora cada arquivo aparece com **nome, tamanho, horário de recebimento e o resumo inteiro**
— 64 caracteres, sem prefixo abreviado, porque um prefixo não serve para conferir. Junto vai o
comando que faz a conferência: `shasum -a 256 arquivo.pdf` no macOS e Linux,
`certutil -hashfile arquivo.pdf SHA256` no Windows.

Isso fecha os dois lados da confiança:

- **o candidato** demonstra, meses depois, que o arquivo que tem em mãos é o que entregou;
- **quem confere** afirma que o arquivo que abriu é o que foi recebido — por fora, sem depender do
  sistema. O mesmo resumo passou a aparecer também no detalhe administrativo, ao lado de
  `Visualizar` e `Baixar`.

O sistema já recusava servir arquivo divergente (FR-053a); o que não existia era o meio de **outra
pessoa** chegar à mesma conclusão sozinha. Verificação que só o próprio sistema pode fazer não é
verificação — é uma afirmação sobre si mesmo.

**Corrigido: cabe em uma página.** O papel passou a ser tratado como o meio que é — corpo em
10,5 pt, entrelinha menor, margem de página declarada, dados em **duas colunas**, documentos em
lista densa, e `break-inside: avoid` para que nenhum arquivo seja partido entre folhas. Medido com
três documentos e três resumos: **663 px de conteúdo contra 1032 px** de área útil de uma A4 —
cabe com folga.

**Corrigido: o documento diz de quando é.** Entrou a linha `Comprovante emitido em …`, que não
depende do rodapé do navegador.

**O que não pude corrigir, e por quê.** O cabeçalho com o endereço da página e o rodapé com a data
são do **navegador**, não desta página: nenhuma regra de CSS os remove, nem `@page`. É decisão de
quem imprime. O que dava para fazer, foi feito — o documento carrega o próprio timbre e a própria
data, para não depender deles, e a tela ganhou a linha que diz onde desligá-los (*na janela de
impressão, desmarque Cabeçalhos e rodapés*).

Travado por `test_o_comprovante_permite_verificar_cada_arquivo`,
`test_o_comprovante_cabe_em_uma_pagina` e `test_quem_confere_ve_tamanho_e_resumo_de_cada_arquivo`.

### D10 — A vitrine não dizia se havia vaga para quem estava lendo (média)

Comparada com o que o Cefor publica hoje no site institucional, a vitrine dizia menos do que a
página que ela substitui. O cartão trazia o nome do processo, o código, a unidade e a data-limite —
e mais nada. Para descobrir **se havia vaga para si**, a pessoa tinha de abrir a seleção. Quem
procura emprego faz isso uma vez, não dez.

Faltavam quatro coisas, e a referência real tem todas: o **título do Edital** (que é onde o cargo
aparece), **quais vagas** e **quantas**, o **período inteiro** — só o fim era exibido, e "até
20/09" não diz se já começou — e alguma noção de **urgência**.

**Corrigido.** O cartão passou a trazer:

- o título do Edital abaixo do nome do processo — *"Edital 01/2026 — Professor Substituto e
  Técnico-Administrativo"*;
- a linha `VAGAS`, com os Perfis e o total: *"Professor de Informática · Técnico de Laboratório —
  3 vagas imediatas, com cadastro reserva"*;
- o período completo, com início **e** fim;
- o prazo restante em destaque — *"Faltam 19 dias."* —, que vira aviso âmbar nos últimos dois dias
  e *"Último dia"* no fim. Uma data sozinha e um contador são a mesma informação e produzem
  decisões diferentes;
- um convite visível, *"Ver vagas e inscrever-se"*, que **parece** botão e não é: o alvo continua
  sendo o link do título estendido a todo o cartão, porque um segundo elemento clicável daria dois
  destinos ao teclado para uma decisão só.

As seleções passaram a ser **agrupadas por situação**, abertas primeiro, e ordenadas pela que fecha
antes: a ordem da página é a da urgência de quem lê, e não a de criação de quem publicou. O prazo
restante entrou também na página da seleção, que é onde a decisão de começar agora ou depois
acontece.

**O que não foi feito, e por quê.** A referência agrupa por público (alunos, bolsistas,
substitutos, tutores) e lista todos os anexos do Edital com formato e tamanho. O primeiro depende
de uma classificação que o Edital ainda não declara — inventá-la aqui seria decidir taxonomia
institucional numa tela. O segundo depende da 008, que trata dos anexos: hoje há um PDF só, e ele
já está na página da seleção.

Travado por `test_o_cartao_diz_para_qual_vaga_e_quantas` e
`test_as_abertas_vem_primeiro_e_em_secao_propria`.

### D11 — Faltava provar que o **papel** é o que o sistema emitiu (alta)

D9 deu ao comprovante o resumo de cada anexo, que responde *"este arquivo é o que foi entregue?"*.
Ficou de fora a outra metade, e é a que uma comissão precisa primeiro: *"este papel é o que o
sistema emitiu?"*. Um comprovante é um HTML impresso — qualquer pessoa abre as ferramentas do
navegador, troca o nome, o protocolo ou a lista de documentos, e imprime.

Junto com isso, dois incômodos concretos de quem imprimiu:

- o arquivo salvo chamava-se `Comprovante de inscrição — Cefor_Ifes.pdf`, indistinguível do
  comprovante de qualquer outra seleção;
- o cabeçalho do navegador, com `localhost:8009/...`, continuava impresso.

**Corrigido: código de verificação.** Um HMAC-SHA256 sobre o que o comprovante afirma — protocolo,
titular, instante do envio, Edital, Perfil, modalidade e o resumo de cada documento —, exibido ao
lado do protocolo em dezesseis dígitos hexadecimais: `0A49-4F81-A48D-5DEF`. O **mesmo** código
aparece na consulta administrativa: quem recebe o papel abre a inscrição no sistema e compara dois
números, em vez de conferir linha por linha.

HMAC, e não um resumo simples, porque um SHA-256 do texto qualquer pessoa recalcula — e então
qualquer pessoa forja: altera o comprovante e recalcula o número. O HMAC depende de uma chave que
só o servidor tem.

Dezesseis dígitos e não sessenta e quatro porque este número é **transcrito por pessoas**: alguém
lê no papel e compara na tela. Sessenta e quatro caracteres nessa situação produzem erro de
leitura, não segurança — e o que se defende é a alteração de um comprovante por quem o apresenta,
não um ataque de colisão.

**O que ele não é**, e está dito no código: não é assinatura digital com valor jurídico próprio —
não há certificado, não há ICP-Brasil, e trocar a `SECRET_KEY` invalida os códigos emitidos. É
verificação interna.

**Corrigido: o nome do arquivo é o protocolo.** O `<title>` passou a ser
`Comprovante INS-2026-6N5SFREZ`, e é dele que o navegador tira o nome do PDF salvo — e o texto do
cabeçalho impresso.

**O cabeçalho do navegador continua lá, e a razão é definitiva.** Ele é desenhado pelo navegador
fora da página; nenhuma regra de CSS o alcança, nem `@page`. Só quem imprime pode desligá-lo. O que
dava para fazer, foi feito: o documento carrega timbre, data de emissão e agora protocolo no
próprio cabeçalho impresso, e a tela ganhou instruções **por navegador** — Firefox
(*Mais configurações → Imprimir cabeçalhos e rodapés*), Chrome, Edge e Safari.

**A alternativa que resolveria de vez, e que é decisão de produto.** Gerar o PDF no servidor
elimina o cabeçalho, fixa o nome do arquivo e produz bytes idênticos a cada emissão — o que
permitiria publicar também o resumo do próprio PDF. O projeto **já tem** o gerador
(`publicacoes/infrastructure/pdf.py`, escrito à mão e sem dependências novas), então o custo é de
composição, não de infraestrutura. O que impede é a spec: **FR-063 proíbe** gerar PDF de
comprovante. A restrição foi decidida quando o comprovante era entendido como tela; depois de D7,
D9 e D11 ele é um documento, e vale reabrir a decisão — mas não sozinho, e não por dentro de uma
correção de UX.

Travado por `test_o_comprovante_se_identifica_pelo_protocolo_no_titulo`,
`test_o_comprovante_traz_o_codigo_que_prova_que_e_ele`,
`test_quem_confere_ve_o_mesmo_codigo_do_comprovante` e
`test_o_codigo_de_verificacao_muda_quando_o_comprovante_muda`.

### D12 — O comprovante passou a ser gerado pelo servidor (decisão de produto revista)

D11 terminou dizendo que o cabeçalho do navegador não tinha solução dentro da página, e que a
solução real — gerar o PDF no servidor — esbarrava em **FR-063**, que a proibia. A decisão foi
reaberta e revista em 31/08/2026.

**Por que a proibição fazia sentido, e por que deixou de fazer.** Ela foi escrita quando o
comprovante era entendido como a última tela de um fluxo — e para uma tela, gerar arquivo é
excesso. Ele não é uma tela. É a única prova que o candidato leva e o papel que a comissão recebe:
apresentado numa banca, anexado a um recurso, guardado por um ano. É documento do candidato **e**
do Ifes.

Impresso pelo navegador, ele saía com `localhost:8009/...` no alto da folha, com o nome de arquivo
tirado do título da aba, e com bytes diferentes a cada impressão — o que impedia publicar o resumo
do próprio documento.

**O que foi feito.**

`render_documento` foi **extraída** de `render_edital_pdf`: os dois documentos são diferentes em
tudo o que dizem e idênticos em como viram arquivo, e o que estava embutido num deles era, na
verdade, a infraestrutura dos dois. O gerador do Edital continua produzindo bytes idênticos — a
fixture que o guarda passa sem alteração.

O comprovante em PDF traz brasão e timbre do Ministério, o protocolo e o código de verificação num
quadro, os dados da inscrição, cada documento com tamanho, horário e resumo, e o atestado. Rodapé
com protocolo e código em **todas** as páginas. Uma página no caso de referência — três documentos
e três resumos de 64 caracteres.

**Determinismo, e o que ele compra.** Nada na composição lê o relógio: a data que o documento
carrega é a do envio, que é fato passado. Por isso o mesmo comprovante gera sempre os mesmos bytes,
e por isso a página pode publicar o **resumo do próprio arquivo**. Verificado de ponta a ponta —
resumo publicado na página e `shasum` do arquivo baixado por outro cliente:

```
288de0b75dfff354430a7ba6004649f3726267923635e32ca20cf2ca1aa93252
```

O nome do arquivo é `Comprovante INS-2026-6N5SFREZ.pdf`, entregue como `attachment`: quem clicou
veio buscar um arquivo para guardar, e abrir no visualizador o devolveria à tela de onde saiu.

**Uma ação só, e o link estava sem estilo.** A primeira versão desta tela oferecia duas — baixar o
arquivo e imprimir a página —, e o link de baixar aparecia como **texto simples** no meio do
parágrafo enquanto o botão de imprimir tinha contorno: o CSS dizia `button.principal`, e o seletor
por elemento não alcança um `<a>`. O resultado é o pior arranjo possível — a ação errada era a que
parecia botão.

Corrigido nos dois níveis. O seletor virou `.principal`, e o botão de imprimir **saiu**: com o PDF
disponível, ele dividia a decisão sendo pior em tudo o que importa aqui — a impressão sai com o
endereço que o navegador escreve na folha, com o nome de arquivo tirado do título da aba, e com
bytes diferentes a cada vez. Junto saíram o script que o acionava e as instruções de como desligar
o cabeçalho do navegador, que só existiam por causa dele. A página continua imprimível por quem
apertar Ctrl+P; o que saiu foi o convite.

**A spec foi alterada, e não contornada.** FR-063 passou a exigir o PDF gerado; FR-063a fixa o
determinismo e a publicação do resumo; FR-063b descreve o código de verificação e declara o que ele
**não** é. SC-012 acompanhou, e SC-012a passou a exigir que um comprovante alterado seja
reconhecível.

Travado por `test_o_comprovante_em_pdf_e_um_arquivo_com_nome_proprio`,
`test_o_mesmo_comprovante_gera_sempre_o_mesmo_arquivo`,
`test_o_pdf_do_comprovante_diz_o_que_o_papel_precisa_dizer`,
`test_o_pdf_de_outro_candidato_nao_e_entregue`, `test_rascunho_nao_tem_comprovante_em_pdf` e
`test_o_pdf_cabe_em_uma_pagina_no_caso_de_referencia`.

## Lacunas e oportunidades, por prioridade

> **Estado em 31/08/2026:** L1 a L10 foram corrigidas e travadas por teste. L11 e L12 continuam
> abertas, e a razão é a mesma nas duas: não são trabalho de implementação — são, respectivamente,
> uma decisão de política institucional e uma integração externa. Corrigi-las aqui seria simular
> que estão resolvidas.

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

**L3 — Nenhum indicador de etapa (média). Corrigido.** Identificação, dados, documentos, revisão e
comprovante eram cinco momentos sem nome, e ninguém sabia se estava no começo ou no fim.

Agora três etapas no topo — *Seus dados e documentos · Revisão · Comprovante* — com a atual marcada
por `aria-current="step"` e o texto "Etapa N de 3", que diz o mesmo a quem não distingue as cores.
Três e não cinco: a identificação já passou quando a lista aparece, e os documentos acontecem
**dentro** da primeira etapa — anunciá-los à parte prometeria uma tela que não existe. Travado por
`test_as_tres_etapas_dizem_onde_a_pessoa_esta`.

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

**L5 — A recusa de imagem não dizia como converter (média). Corrigido.** A mensagem nomeava o
formato, explicava a causa e dizia o que fazer — mas não o **como**, e "converta em PDF" não ajuda
quem nunca converteu. É o erro mais comum de candidato.

Agora, e **só** nessa recusa, um `Como transformar uma foto em PDF` recolhido traz o caminho no
iPhone, no Android e o de juntar vários documentos num arquivo só. Noutras recusas não aparece, o
que evita transformar a instrução em ruído. Travado por `test_a_recusa_de_imagem_ensina_a_converter`
e `test_a_recusa_de_formato_nao_ensina_a_converter`.

**L6 — Requisito já enviado ocupava a tela como se não estivesse (média). Corrigido.** Depois do
envio o formulário de substituição continuava aberto: ~850 px por requisito, ~2.500 px de rolagem
com três documentos completos.

Agora o formulário some para dentro de um `Substituir ou remover` recolhido — medido depois:
**225 px** por requisito atendido. Substituir é exceção; o estado normal é "está enviado". Quando a
substituição é recusada o bloco volta aberto, senão a pessoa leria o motivo sem encontrar onde
tentar de novo. Travado por `test_o_requisito_enviado_recolhe_o_formulario_de_substituicao`.

**L7 — Documentos exigidos eram invisíveis antes da identificação (média). Corrigido.** A tela
pública listava requisitos de titulação e nada sobre arquivos: descobrir que precisaria do diploma
digitalizado custava identificar-se e abrir uma inscrição. Quem lê no ônibus, sem os arquivos à
mão, desiste no meio.

Cada Perfil ganhou um `Documentos que serão pedidos` recolhido, com o que vale para todo mundo e o
que cada modalidade acrescenta — *"Se concorrer em Pessoas pretas, pardas e indígenas, também:
Autodeclaração étnico-racial"* —, mais formato e limite. Sai da mesma função de aplicabilidade que
decide o que a inscrição pede: três leituras da mesma regra, e não três interpretações. Travado por
`test_os_documentos_exigidos_aparecem_antes_da_identificacao`.

No caminho apareceu um defeito pequeno e real: **o limite "10 MB" estava escrito à mão em dois
templates** enquanto `ARQUIVOS_CANDIDATOS_LIMITE_BYTES` é configurável. Mudar o limite deixaria a
tela mentindo para o candidato. Agora é uma tag que lê a configuração
(`test_o_limite_exibido_e_o_limite_aplicado`).

**L8 — Cartão da vitrine clicável só no título (baixa). Corrigido.** Num celular, mirar duas
palavras de título é o tipo de precisão que faz errar. O cartão inteiro virou alvo — medido: de
**8.304 px²** para **86.725 px²**, dez vezes mais. O link continua sendo **um só**: o pseudo-elemento
estende a área dele, então teclado e leitor de tela seguem vendo exatamente um destino, e o cartão
ganhou `:focus-within` para que o foco continue visível.

**L9 — `novalidate` desligava a validação nativa (baixa). Corrigido.** A decisão original era
defensável — uma gramática de erro só, no servidor —, mas custava o retorno imediato de campo.

O `novalidate` saiu do HTML e passou para o script: **sem** JavaScript o navegador volta a exigir os
obrigatórios e o formato do e-mail sozinho, que é mais do que havia antes; **com** JavaScript o
script assume, usando a mesma Constraint Validation API que a interface administrativa já usa
(`interface/validacao.js`) e repetindo **a mensagem do servidor**, palavra por palavra. Verificado
no navegador ao digitar um CPF curto: `{aria_invalid: "true", mensagem: "Informe um CPF com 11
dígitos.", valido: false}` — a mesma frase que `_recusas_da_identificacao` devolveria. A gramática
de erro continua sendo uma só; o que mudou é quando ela chega.

**L10 — Acesso administrativo a documento não era auditado (média). Corrigido.** FR-077 audita os
atos do candidato e dispensa a consulta pública; sobre a **consulta administrativa** a spec era
silenciosa, e o silêncio deixava o sistema sem resposta para a pergunta que uma auditoria de dados
pessoais faz primeiro. Documento de candidato inclui autodeclaração étnico-racial: é dado sensível,
e acesso a dado sensível deixa rastro.

Cada entrega de arquivo passou a registrar `CONSULTAR_DOCUMENTO`, com ator, inscrição, requisito e
instante — e **sem** o nome do arquivo, que é do candidato (FR-074). Verificado no banco após uma
consulta real: `Ana Coordenadora | inscricao=afc6f2cc | requisito 0000…00d1`. Travado por
`test_abrir_documento_de_candidato_deixa_rastro`.

**Isto é acréscimo ao que a spec pedia**, e não cumprimento dela: FR-077 não exige este registro.
Vale registrá-lo na próxima revisão da spec para que não pareça acidente.

**L11 — Retenção e descarte (média). Não corrigida, e de propósito.** A spec não é omissa aqui: ela
**proíbe** (FR-076) que esta feature implemente rotina automática de expurgo, e declara a política
de retenção como precondição de implantação. Escrever um expurgo agora seria decidir por conta
própria quanto tempo o CPF de um candidato fica guardado — decisão institucional, não técnica, e
que uma vez em código passa a parecer resolvida.

O percurso mostra o custo concreto de deixá-la em aberto: rascunhos com CPF e e-mail se acumulam a
partir do primeiro dia, e a correção de D5 os tornou mais visíveis, não menos numerosos. **O que
falta é a decisão**: por quanto tempo, sob que responsável, com que rotina. Depois dela, o código é
pequeno.

**L12 — Uma pessoa pode declarar-se outra. Não corrigível aqui.** O provedor de demonstração aceita
qualquer CPF sem prova de titularidade. Não há o que consertar no código: o que falta é o provedor
real (gov.br ou equivalente institucional), que é integração externa e depende de credenciamento.

O que o sistema já faz é o que lhe cabe: a tela declara-se demonstração sem eufemismo, e
`config/settings/production.py:94` **recusa a subida** com o provedor de demonstração ligado — a
barreira existe e é executável. FR-026 garante que trocar o provedor não altera a semântica da
Inscrição. Continua sendo bloqueio de implantação, e não melhoria de experiência.

## O que não foi verificado neste percurso

- Envio de arquivo grande em rede lenta (o progresso real de `htmx:xhr:progress`), simulado apenas
  nos testes automatizados.
- Retificação do Edital publicada com rascunho aberto — o aviso de nova versão e o reconhecimento.
- Navegação completa por teclado e leitor de tela de ponta a ponta; foram medidos pontos isolados
  (L2), não a jornada inteira.
- Encerramento do período com rascunho em aberto.
