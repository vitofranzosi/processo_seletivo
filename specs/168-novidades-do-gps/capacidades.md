# Matriz das capacidades do GPS

> **Estudo, e não a página.** A vitrine que esta matriz fundamentou saiu das Novidades em 15/11
> (`D-014`): a página é do que mudou, e o tour do produto, se houver, mora num guia fora dela. A matriz
> e os textos dos dez cartões, no fim deste arquivo, ficam como matéria-prima desse guia. A seleção e a
> ordem foram julgamento editorial, sem dado de uso nem consulta a operador.

*Revisão editorial de 14/11/2026 (`D-012`, `D-013`), sobre a `main` em `416257b2` mais os PRs do
agendamento (#550, #554, #556), mergeados durante a revisão.* É a auditoria de produto que decide a
vitrine "Descubra o que o GPS já faz": o que o GPS permite fazer, para quem, o que substitui e se está
disponível. A disponibilidade foi conferida no código e nas configurações (`config/settings/`); a
implantação de cada ambiente fica fora do repositório (`D-001`).

**Disponível** quer dizer: no código da `main`, sem chave desligada por padrão. **Condicionada**: no
código, mas atrás de configuração — a nota declara a chave e some onde ela está desligada. **Fora**:
não é anunciada.

## O que entrou na vitrine

| # | Capacidade | O que permite | O que substitui ou resolve | Quem ganha | Situação | Evidência (specs) |
|---|---|---|---|---|---|---|
| 1 | Centro de Controle | Ver a fase do Edital, o que falta e de quem é a vez; ir ao lugar do ato e voltar | Caça por menus para descobrir o próximo passo | Presidência, quem conduz | Disponível | 127, 135, 136, 138, 139, 147 |
| 2 | Minhas atividades | Ver numa página o que é seu em todos os Editais | Abrir Edital por Edital | Toda a comissão | Disponível | 160 |
| 3 | Agenda das entrevistas | Configurar dias, janelas e bancas; montar com prévia; publicar com PDF; remarcar | Planilha de horários e aviso um a um | Quem conduz Etapa com horário; candidatos | Disponível (avisos por e-mail condicionados a `AVISOS_AOS_CANDIDATOS`) | 167 (entregas A, B e C) |
| 4 | Convocação com documentos | Convocar, receber documentos pela área do candidato, conferir com o PDF ao lado, dar prazo, registrar o resultado | E-mail com anexos, controle em planilha | Comissão; candidatos | Disponível (avisos condicionados) | 050, 115, 120, 140, 143, 149, 150, 152, 154, 156, 157, 159 |
| 5 | Da aprovação à matrícula | Requerimento de Matrícula no GPS, entrega ao setor que formaliza, planilha para o Registro Acadêmico | Redigitação dos dados e pacote de documentos por e-mail | Setor de matrícula; comissão | Disponível | 029, 031, 117, 153 |
| 6 | Edital guiado | Compor o Edital numa sequência, simular classificação e sorteio, gerar o PDF oficial em linguagem simples | Edital redigido à mão, conferido a olho | Quem elabora e homologa | Disponível | 030, 032, 043, 044, 051–054, 064–069, 094, 095, 098, 144 |
| 7 | Barema | Publicar critérios e pontuar item a item; o total sai calculado | Planilha paralela da ficha de títulos | Avaliadores; recursos | Disponível | 146 |
| 8 | Sorteio público | Conduzir o sorteio com a Loteria Federal, passo a passo, e publicar como foi feito | Sorteio fora do sistema, sem rastro público | Comissão; candidatos | Disponível | 021, 098, 102, 116, 122, 142, 145 |
| 9 | Verificação da autodeclaração | Etapa só para algumas Modalidades, pareceres da banca e regra de decisão publicada | Banca registrada fora do sistema | Banca; comissão | Disponível | 163, 164, 165 |
| 10 | Kit de divulgação | Textos para site, redes e mensagens, a partir do Edital publicado, num pacote | Redigitar datas e vagas para divulgar | Comunicação | Disponível (os textos); **condicionada** a peça visual (`KIT_DE_DIVULGACAO_TEMPLATES`, vazia por padrão) | 111, 119 |

## Fora da vitrine, e por quê

| Capacidade | Situação | Por que não é anunciada como entregue |
|---|---|---|
| Assistente de dúvidas para candidatos, na página pública | Só no desenvolvimento local | A produção recusa a página pública (`AMBIENTE_DE_PRODUCAO`, 170); há nota só do piloto interno, para quem tem a capacidade do piloto, e da habilitação pela interface, para quem a administra |
| Verificação da autodeclaração por vídeo | Só no desenvolvimento | `VERIFICACAO_POR_VIDEO` é recusada em produção (166); a habilitação pela interface (169) é só especificação |
| Peças visuais do kit | Condicionada | Nota própria com `requer_configuracao = "KIT_DE_DIVULGACAO_TEMPLATES"`; a capacidade promete só os textos |
| Avisos por e-mail aos candidatos | Condicionada | `AVISOS_AOS_CANDIDATOS` desligada em produção até a validação de LGPD; as notas declaram a chave |
| Gestão de acessos e cadastro de unidades | Disponível só no modo institucional | Notas para quem tem a capacidade; o seletor de demonstração não as alcança |
| Relatórios do Edital e consolidado, Agenda dos Editais, Visão Geral | Disponível | Ficam no histórico como notas transformadoras ou relevantes; a vitrine tem teto de dez e prioriza o trabalho do dia |

## A política que a vitrine seguia

Está no guia (`doc/curadoria-das-novidades.md`, "Os destaques"): no máximo dez capacidades, seis à
vista; entra a que cria capacidade nova ou elimina operação trabalhosa; quando passar de dez, sai a de
menor uso na rotina da comissão, e a decisão vai no PR. Destaque não é novidade recente: a capacidade
de setembro continua na vitrine enquanto for das mais importantes.

## Os textos dos cartões

Como estavam no arquivo das notas em 14/11, na ordem da vitrine. As notas citadas continuam no
histórico.

### Saiba em segundos o que falta em cada Edital, e de quem é a vez

`centro-de-controle` · notas: `centro-de-controle-do-edital`, `processo-aponta-o-que-esta-parado`, `pagina-do-processo`, `orientacao-aponta-o-passo-certo`, `lista-de-processos-com-abas-e-busca`, `encerrar-sabendo-o-que-esta-em-aberto`

A página do Edital mostra a fase, o que ainda precisa ser feito e quem faz cada coisa, com o que é seu
marcado. Um clique leva ao lugar certo, e depois você volta.

**Por onde começar:** Em Processos Seletivos, abra um Edital publicado.

*destino `interface:lista` · documentacao `centro-de-controle`*

### Comece o dia pela sua lista: o que é seu, em todos os Editais

`minhas-atividades` · notas: `minhas-atividades`

Avaliações, conferências e passos que dependem de você, reunidos numa página. Acabou abrir Edital por
Edital para descobrir o que falta.

**Por onde começar:** Na barra lateral, em Minhas atividades.

*destino `interface:minhas-etapas` · documentacao `minhas-atividades`*

### Organize as entrevistas sem montar planilhas

`agenda-de-entrevistas` · notas: `agenda-da-etapa`, `remarcar-a-agenda`

Defina os dias, os horários e as bancas; o GPS distribui os candidatos, publica a agenda e mostra a
cada pessoa o seu horário. Mudou algo? Remarque um por um, com registro.

**Por onde começar:** Na distribuição da Etapa que precisa de horário, no cartão Agenda.

1. Configure os dias, as janelas de horário e as bancas.
2. Monte a agenda e confira a prévia.
3. Publique: cada candidato vê o seu horário.

### Convoque, receba e confira documentos sem e-mail nem planilha

`convocacao-com-documentos` · notas: `documentos-na-convocacao-e-formalizacao`, `convocacao-como-fluxo`, `convocar-e-publicar-no-gps`, `correcao-da-convocacao`, `envio-de-varios-documentos`, `conferencia-com-o-documento-a-vista`, `convocacao-pelas-perguntas-de-quem-conduz`, `prevencao-nos-atos-irreversiveis`, `convocado-entende-a-convocacao`, `nao-se-aplica-com-fundamento`, `lista-no-gesto-de-titulares`, `convocacao-segue-o-canal`, `convocacao-e-conferencia-mais-claras`, `convocacao-depois-do-envio`, `vaga-reservada-sem-ocupante`, `vaga-acrescida`, `situacao-do-candidato`

O candidato envia os documentos pela área dele, e a comissão confere com o PDF ao lado e registra o
resultado. Prazos, histórico e avisos ficam num lugar só.

**Por onde começar:** Na página do Edital publicado, abra a convocação de cada lista.

1. Convoque os titulares da lista de uma vez.
2. Acompanhe o que cada pessoa enviou e o que falta.
3. Confira cada documento e registre o resultado.

*documentacao `convocacao-pelas-perguntas`*

### Da lista de aprovados à matrícula, sem redigitar dados

`da-aprovacao-a-matricula` · notas: `requerimento-de-matricula`, `exportacao-para-matricula`, `formalizacao-na-jornada-do-edital`

O candidato preenche o Requerimento de Matrícula no GPS, o setor que formaliza recebe os documentos de
quem ficou apto, e a planilha sai pronta para o Registro Acadêmico.

**Por onde começar:** Na página do Edital publicado, na fase de conclusão.

*documentacao `formalizacao`*

### Monte o Edital no GPS e receba o documento oficial pronto

`edital-guiado` · notas: `edital-em-linguagem-simples`, `simule-antes-de-publicar`, `revisao-acusa-o-que-nao-funcionaria`, `aplicar-aos-demais-perfis`, `vista-do-conjunto-em-perfis-e-classificacao`, `duplicar-perfil`, `o-que-se-repete-sai-uma-vez`, `texto-do-edital-conferido`, `autoridades-da-unidade`, `revisao-e-documento-dizem-a-classificacao`, `revisao-do-edital-reaproveitado`, `evento-oculto-no-pdf`, `normas-do-edital-em-pdf`, `cadastro-de-reserva-como-cr`, `documento-exigido-em-todos-os-perfis`, `regra-de-classificacao-mais-clara`, `tabelas-do-edital-em-pdf`, `edital-sem-masculino-generico`, `documentos-exigidos-mais-claros`

Você preenche vagas, datas e regras numa sequência guiada; o GPS confere o que travaria a seleção e
gera o PDF oficial em linguagem simples, já respondendo às perguntas do candidato.

**Por onde começar:** Em Processos Seletivos, clique em Novo Processo Seletivo.

1. Preencha as etapas da composição, na ordem.
2. Simule a classificação e o sorteio com candidatos fictícios.
3. Confira a Revisão e envie para homologação.

*destino `interface:lista` · documentacao `composicao-validacao`*

### Avalie títulos item a item, e o GPS soma a nota

`barema` · notas: `barema-da-etapa`

Publique os critérios da avaliação no Edital; quem avalia pontua cada critério na Mesa, e o total sai
calculado. Acaba a planilha paralela, e a nota fica fácil de conferir num recurso.

**Por onde começar:** Na composição do Edital, no cartão da Etapa pontuada, seção Barema.

*documentacao `barema-da-etapa`*

### Faça o sorteio público no GPS, com a Loteria Federal

`sorteio-publico` · notas: `jornada-do-sorteio`, `concurso-conferido-na-caixa`, `sorteio-viavel-desde-a-publicacao`, `mesmas-listas-em-toda-parte`, `sorteio-no-cartao-da-vaga`

O GPS guia o sorteio passo a passo — fixar quem participa, obter o número da Loteria Federal e sortear
— e publica quem participou e como foi feito, para qualquer pessoa conferir.

**Por onde começar:** Na página do Edital publicado, abra o sorteio.

*documentacao `jornada-do-sorteio`*

### A verificação da autodeclaração agora acontece dentro do GPS

`verificacao-da-autodeclaracao` · notas: `etapa-por-modalidade-e-deliberacao`

Organize a banca, registre o parecer de cada avaliador e deixe o GPS aplicar a regra de decisão
publicada no Edital — num lugar só, com o registro de cada passo.

**Por onde começar:** Na composição do Edital, no cartão da Etapa: a quem ela se aplica e como a comissão decide.

*documentacao `deliberacao`*

### Divulgue o Edital com textos prontos, tirados do que foi publicado

`kit-de-divulgacao` · notas: `kit-de-divulgacao`, `pecas-do-kit`

O GPS escreve os textos para o site, as redes e as mensagens a partir do Edital publicado, e entrega
tudo num pacote. Nada de redigitar datas e vagas.

**Por onde começar:** Na página do Edital publicado, em Kit de divulgação.

*documentacao `kit-de-divulgacao`*
