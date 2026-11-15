# Matriz das capacidades do GPS

*Revisão editorial de 14/11/2026 (`D-012`, `D-013`), sobre a `main` em `416257b2` mais os PRs do
agendamento (#550, #554, #556), mergeados durante a revisão.* É a auditoria de produto que decide a
vitrine "Descubra o que o GPS já faz": o que o GPS permite fazer, para quem, o que substitui e se está
disponível. A disponibilidade foi conferida no código e nas configurações (`config/settings/`); a
implantação de cada ambiente fica fora do repositório (`D-001`).

**Disponível** quer dizer: no código da `main`, sem chave desligada por padrão. **Condicionada**: no
código, mas atrás de configuração — a nota declara a chave e some onde ela está desligada. **Fora**:
não é anunciada.

## Na vitrine

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

## A política da vitrine

Está no guia (`doc/curadoria-das-novidades.md`, "Os destaques"): no máximo dez capacidades, seis à
vista; entra a que cria capacidade nova ou elimina operação trabalhosa; quando passar de dez, sai a de
menor uso na rotina da comissão, e a decisão vai no PR. Destaque não é novidade recente: a capacidade
de setembro continua na vitrine enquanto for das mais importantes.
