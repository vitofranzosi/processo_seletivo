# Equivalência das regras — o PDF de hoje × a proposta do lote 1

**2026-10-12 · cenários A e B da auditoria de 08/10.** Conferência **por enunciado**, e não por fato: para
cada regra do documento de hoje, se a proposta mantém **condição, exceção, alcance e consequência**.
A cobertura de fatos (datas, números, documentos, códigos, fundamentos, anexos, hash) é automática e
está no §9.2 do relatório: 27 de 27 em A e 85 de 85 em B. Ela não prova equivalência de regra, e esta
página existe por isso.

Documentos comparados: `atual-A.pdf` × `proposta-A.pdf`; `atual-B.pdf` (o da 068) × `proposta-B.pdf`.

**Legenda.**
- **=** igual, só redação.
- **≈** reescrito, mesmo efeito: o texto muda e a regra não.
- **→** movido para outra seção, sem mudar o texto da regra.
- **+** frase nova, gerada do dado ou descrevendo regra do sistema; **exige revisão**.
- **!** ponto a decidir. A proposta não decide, e deixa à vista.

Origem: **G** gerado pelo sistema; **R** redação do Elaborador.

---

## Achados desta conferência

1. **A primeira redação acrescentava uma condição, e foi corrigida.** A continuação do corte saiu como
   "Se ainda sobrarem vagas, poderão ser chamados outros candidatos". A norma publicada não tem essa
   condição: diz *"Poderá haver chamada, nesta ordem, além dos que este corte publicar"*. O sistema só
   chama para vaga não preenchida (019, 050), mas isso é comportamento de convocação, e não texto do
   marco. A proposta voltou a *"Depois, poderão ser chamados outros candidatos, além desses, seguindo a
   mesma ordem"*. É exatamente o tipo de erro que a contagem de fatos não pega.
2. **Uma frase explicativa só vale sem cadastro de reserva.** "Os suplentes são chamados, na ordem,
   para as vagas deste Edital que não forem preenchidas pelos primeiros classificados" descreve a regra
   do sistema e torna compreensível, em A, "não há cadastro de reserva" ao lado de "mais 15 suplentes".
   Em B ela seria errada: lá há cadastro de reserva de até 15, e o corte leva 10 + 5. Como as duas
   coisas se relacionam é a pendência DP-05 / RC-58, que o documento não pode explicar. A proposta só
   imprime a frase quando nenhum Perfil tem cadastro.
3. **"Havendo mais inscritos que vagas" não contradiz "participam todas as inscrições"** — a primeira
   diz *quando* há sorteio, a segunda *quem* participa. A primeira versão do relatório as chamava de
   contraditórias, e isso estava errado. O que existe é **divergência entre o texto do Elaborador e o
   comportamento do sistema**: um marco por sorteio sempre sorteia (`classificacao/application/emissao.py:231`;
   021, casos-limite: "A ordem de um é legítima"). Com menos inscritos que vagas, todos passam do
   mesmo jeito, mas a norma escrita promete algo que o sistema não faz. O Edital 78/2026 real tem essa
   condição, e ela nunca foi modelada. **!** A proposta mantém o texto do Elaborador.

---

## Cenário A (pós-graduação, 4 polos, sorteio)

| # | Hoje | Proposta | Classe | Origem | Observação |
|---|---|---|---|---|---|
| A1 | Preâmbulo | idem | = | R | — |
| A2 | Descrição do Edital entre o título e o preâmbulo | retirada; o resumo cumpre o papel | — | G | sem regra (ED-25). Fica no portal |
| A3 | — | Resumo: vagas, cadastro, inscrições, teto, seleção, datas, com o item de cada uma | + | G | só dado estruturado; declara que não substitui as seções. **Revisão jurídica do estatuto de um resumo dentro do ato** |
| A4 | "conduzido por Comissão de Seleção designada pela Diretora-Geral do Cefor" | idem, com "uma" | = | R | — |
| A5 | "dúvidas [...] esclarecidas exclusivamente pelo e-mail [...] das 8h às 17h" | "somente pelo e-mail" | ≈ | R | exclusividade preservada |
| A6 | "publicações [...] no endereço eletrônico do certame" | "em https://exemplo…/91-2026" | ≈ **!** | R | endereço de exemplo; depende da fonte do §3.4 |
| A7 | Curso integralmente a distância, AVA, encontros síncronos **obrigatórios** para avaliações finais e TFC | idem; "síncronos (ao vivo)" | ≈ | R | "ao vivo" explica, não restringe; obrigatoriedade e alcance mantidos |
| A8 | 480 h, 18 meses | idem | = | R | — |
| A9 | Público-alvo: "Portadores de diploma de curso superior de graduação em qualquer área" | "Pode se inscrever quem tem diploma…" | ≈ | R | — |
| A10 | Requisitos gerais: "atender aos requisitos do polo pretendido, descritos na seção Perfis de Vaga" | "é preciso atender a todos os requisitos abaixo", seguido da lista | ≈ → | R, G | a lista sai na mesma seção (era 5.5). "Todos" é o que "os requisitos" já significava |
| A11 | Requisitos (5.5): diploma de graduação reconhecido pelo MEC; acesso a computador com internet | idem, mesma lista | → | G | alcance: hoje "comuns aos Perfis INF-…"; proposta: a mesma lista, que é a de todos os Perfis — a seção diz isso |
| A12 | Tabela 1 (Perfis: localidade, vagas, cadastro, carga) + Tabela 2 (vagas por lista) | uma matriz Código × Localidade × AC × PPI × PcD × Total, com linha de total | ≈ | G | os mesmos números, por Perfil e lista; total 160 = 112 + 40 + 8 |
| A13 | Nome do Perfil e descrição, repetidos em 5.1–5.4 | "Em todos os Perfis: [nome] — [descrição]; carga horária…; não há cadastro de reserva" | ≈ | G, R | a descrição foi reescrita pelo Elaborador **sem o nome do polo**, que já é a localidade; idênticas, saem uma vez (identidade da 064/068) |
| A14 | Tabela 3 (modalidades: AC sem percentual; PPI 25%; PcD 5%; Resolução CS nº 10/2017) | tabela de reserva só com PPI e PcD | ≈ | G | a linha "AC — —" não afirmava nada |
| A15 | Reversão `ON_EXHAUSTION`: "Havendo ausência de candidatos aprovados na reserva de vagas, o quantitativo será destinado à respectiva ampla concorrência" | "Se não houver candidatos aprovados para as vagas reservadas de um código, essas vagas passam para a ampla concorrência do mesmo código" | ≈ | G | "respectiva" = do mesmo Perfil; "código" é o identificador impresso do Perfil (sem campo novo, §7.4) |
| A16 | Convocação "por publicação no endereço eletrônico do certame" (no Perfil) | "A convocação dos classificados será feita por publicação" (seção de convocação) | ≈ → **!** | G | sem o endereço: a publicação de convocação pode ser externa (050). O Elaborador diz onde, no item 1 |
| A17 | Inscrição "exclusivamente pela internet, no endereço eletrônico do certame, no período previsto no Cronograma" | "somente pela internet, em [endereço]" + "Período de inscrições: de 13/10/2026, às 09h, a 30/10/2026, às 23h59 (Cronograma, nº 1)" | ≈ + | R, G | o período passa a ser gerado do Evento marcado: a Retificação que prorrogar muda a frase sozinha |
| A18 | "indicará o polo e a lista de concorrência" | "Escolha o polo e a lista de concorrência" | ≈ | R | — |
| A19 | "concorrem também às vagas de ampla concorrência do mesmo polo" | idem | = | R | — |
| A20 | Teto: "apenas 1 inscrição enviada neste Edital" | "pode enviar apenas 1 (uma) inscrição neste Edital" | ≈ | G | conta só a enviada, como hoje |
| A21 | Documentos (5 de todos; 1 PPI; 1 PcD), "(facultativo)", instruções | idem, na mesma ordem e com as mesmas instruções | = | G | rótulo do grupo em frase ("Também, de quem concorre às vagas para…") |
| A22 | Requerimento enviado na inscrição, só na seção 14 | também lembrado em "Documentos" e em "Como se inscrever?" | → + | G | ED-18 |
| A23 | Verificação da autodeclaração: sorteados para PPI pretos e pardos; webconferência; data a divulgar; indeferida → só ampla | idem | ≈ | R | alcance (sorteados, pretos e pardos) e consequência preservados |
| A24 | Etapa Análise documental: eliminatória; Deferida/Indeferida; período | "Etapa eliminatória: o resultado é 'Deferida' ou 'Indeferida'. Será feita de… a…" | ≈ | G | — |
| A25 | Critérios: "Havendo mais inscritos que vagas, a ordem [...] por sorteio, conforme o método publicado na seção Perfis de Vaga" | idem, remetendo ao item 8.2 | = **!** | R | ver achado 3 |
| A26 | "Após o sorteio, serão analisados os documentos dos sorteados até o número de vagas do polo e da lista, mais os suplentes previstos" | idem | = | R | repete regra gerada (A29); o guia orienta a não repetir |
| A27 | "Os marcos [...] aplicam-se a cada um desses Perfis separadamente [...] própria classificação e [...] próprio resultado" | "A classificação é feita separadamente em cada Perfil: cada Perfil tem a sua própria classificação e o seu próprio resultado" | ≈ | G | alcance por Perfil preservado |
| A28 | "Habilitação: participam todas as inscrições submetidas" | "Participam do sorteio todas as inscrições enviadas" | ≈ | G | "enviada" = submetida, a palavra do teto |
| A29 | Corte: "Progridem para Análise documental os primeiros desta ordem, até o número de vagas ofertadas no recorte, mais 15 (quinze) suplentes" | "Passam para a Etapa 'Análise documental' os primeiros classificados de cada lista de concorrência, em número igual ao das vagas dessa lista no código, mais 15 (quinze) suplentes" | ≈ | G | "recorte" = Perfil × lista (`faixa.py`); alcance preservado |
| A30 | — | "Os suplentes são chamados, na ordem, para as vagas deste Edital que não forem preenchidas pelos primeiros classificados" | + | G | regra do sistema (019/050), sem cadastro; achado 2. **Revisão** |
| A31 | Continuação: "Poderá haver chamada, nesta ordem, além dos que este corte publicar" | "Depois, poderão ser chamados outros candidatos, além desses, seguindo a mesma ordem" | ≈ | G | achado 1: a condição acrescentada foi retirada |
| A32 | Método do sorteio: comum; algoritmo; fonte; concurso 6010; 14/11/2026, 19h; derivação; semente; substituição | caixa "Dados para conferir o sorteio", com frase de abertura e os mesmos seis dados | ≈ | G | nenhum dado de auditoria retirado (FR-465 da 032); "Semente" mantida com explicação |
| A33 | Recurso do marco: "contra o resultado de 'Classificação por sorteio eletrônico', no prazo de 2 (dois) dias corridos, contados da divulgação desse resultado" | idem, na seção "Como recorrer?" | → | G | sem canal gerado: em B o texto do Elaborador indica outro canal, e gerar "pelo sistema de inscrição" criaria conflito |
| A34 | "recurso contra o resultado preliminar da análise documental, no prazo previsto no Cronograma, exclusivamente pelo sistema de inscrição" | "Contra o resultado preliminar da análise documental: no prazo do Cronograma (nº 7), somente pelo sistema de inscrição" | ≈ | R | a remissão ao Evento 7 é do Elaborador; o sistema não sabe que o Evento 7 é esse recurso (tipo livre) |
| A35 | "Não serão aceitos recursos enviados por e-mail ou fora do prazo" | idem | = | R | o alcance (todos os recursos ou só o da análise?) continua o do texto de hoje; não foi decidido |
| A36 | Convocação de suplentes por desistência, na ordem do sorteio, por publicação | idem, com o endereço | ≈ **!** | R | ver A16 |
| A37 | Matrícula a partir da documentação da inscrição, sem comparecimento | idem | = | R | — |
| A38 | Requerimento no ato da inscrição; declaração transcrita | idem, declaração em caixa | = | G | texto da declaração idêntico |
| A39 | "Fará jus ao certificado de especialista o aluno aprovado em todos os componentes curriculares e no TFC" | "Terá direito ao certificado…" | ≈ | R | — |
| A40 | Anexos I–III | idem | = | G | — |
| A41 | "casos omissos serão resolvidos pela Comissão [...], ouvida a Diretoria de Ensino" | idem, com "situações que este Edital não prevê" | ≈ | R | — |
| A42 | Fecho, autoridade, ato de nomeação, integridade | idem; "Autenticidade — corresponde integralmente" | ≈ | G | L17 |
| A43 | Cronograma (10 eventos, início/término/local) | mesmas linhas; "Quando" em "de … a …" | ≈ | G | datas e horas idênticas; agora na seção 5 |

---

## Cenário B (tutores UAB, 18 Perfis, pontuação)

| # | Hoje | Proposta | Classe | Origem | Observação |
|---|---|---|---|---|---|
| B1 | Preâmbulo | idem | = | R | — |
| B2 | 1.1 Regido pelo Edital, executado pela Comissão designada por portaria | idem, sem o "1.1" | = | R | a numeração digitada sai; a do documento é calculada (065) |
| B3 | 1.2 "destina-se à formação de cadastro de reserva, e a convocação [...] conforme a necessidade dos cursos, durante o prazo de validade" | "A seleção forma cadastro de reserva. Os classificados serão convocados conforme a necessidade dos cursos, durante o prazo de validade deste Edital" | ≈ | R | — |
| B4 | 1.3 sem vínculo empregatício | idem | = | R | — |
| B5 | 1.4 "É vedado o acúmulo de bolsas…" | "É proibido acumular bolsas…" | ≈ | R | — |
| B6 | 2.1–2.4 requisitos gerais | lista "Para se inscrever, é preciso:" com os quatro | ≈ | R | ordem, condições ("se do sexo masculino", "no período de atuação") e remissão mantidas |
| B7 | Requisitos do TD-ADM, do TD-INFO-EDU e comuns aos TP-01…TP-16 (3.20) | três grupos, em "Quem pode se inscrever?" | → | G | os mesmos três grupos, pela identidade da lista |
| B8 | Tabela 1 (18 Perfis × nome, localidade, vagas, cadastro, carga) | Tabela 1 (TD-ADM, TD-INFO-EDU com nome) + Tabela 2 ("Tutor presencial — Perfis TP-01 a TP-16", sem repetir o nome) + "Em todos os Perfis: carga…; remuneração…; cadastro de reserva de até 15" | ≈ | G | os mesmos valores. "TP-01 a TP-16" só porque os códigos são contíguos e sem lacuna (regra determinística) |
| B9 | — | "São 10 vagas imediatas, nos Perfis TD-ADM e TD-INFO-EDU. Os demais formam cadastro de reserva" | + | G | derivado de `immediateVacancies` e `reserveType`. "Os demais formam cadastro" não diz como a reserva se aplica a eles (RC-58), e não deve dizer |
| B10 | Tabela 2 (vagas por lista: TD-ADM 3/2/1/0; TD-INFO-EDU 2/1/1/0) | Tabela 3, mais a coluna Total | ≈ | G | — |
| B11 | Tabela 3 (modalidades: AC; PPIQ 30%; PcD 5%; PTT sem percentual; fundamentos) | Tabela 4, sem a linha AC | ≈ | G | PTT continua com "—" no percentual e o fundamento inteiro |
| B12 | Reversão `ON_BALANCE`: "Na hipótese do não preenchimento total das vagas reservadas, o quantitativo não preenchido será destinado à respectiva ampla concorrência" | "As vagas reservadas de um código com vagas imediatas (TD-ADM e TD-INFO-EDU) que não forem preenchidas passam para a ampla concorrência do mesmo código" | ≈ | G | a espécie é diferente da de A, e a frase também: aqui conta o que **não foi preenchido**, lá a **ausência de aprovados**. O alcance "com vagas imediatas" explicita o que a 067 já fazia ao não imprimir reversão nos Perfis sem vaga |
| B13 | Convocação "por mensagem individual à pessoa convocada" (no Perfil) | idem, na seção de convocação | → | G | — |
| B14 | Atribuições do TD-ADM, do TD-INFO-EDU (a última linha sem marcador) e comuns aos TP (3.19) | três grupos em "3.1 Atribuições", todas as linhas como itens | ≈ | G | a linha do TD-INFO-EDU sem "●" vira item: **!** confirmar que é atribuição, e não nota — o dado não distingue |
| B15 | Dados exigidos na inscrição (meses de experiência, número inteiro; data de nascimento, data), em cada Perfil | uma vez, em "Como se inscrever?": "informe também: o número de meses…; a data de nascimento", + "Esses dados são usados no desempate" | ≈ + | G | iguais nos 18; o tipo do dado sai (L13); "usados no desempate" é derivado de quais fatos os critérios usam |
| B16 | 3.1–3.4 inscrição | reescritos; a recusa por mais de 30 páginas "sem possibilidade de recurso" ganhou "Atenção:" | ≈ | R | vedação e consequência mantidas |
| B17 | Teto | idem | ≈ | G | — |
| B18 | Atendimento à PcD (seção 7 de hoje) | subseção de "Como se inscrever?" | → | R | o pedido é feito no formulário de inscrição |
| B19 | Documentos: 6 de todos, TD-INFO-EDU (mestrado), TP-01 (residência), PPIQ, PcD, PTT | idem, mesma ordem e instruções | = | G | o comprovante de residência continua só para TP-01, como o dado diz (quirk do cenário) |
| B20 | 4.1–4.3 heteroidentificação | reescritos | ≈ | R | alcance (pretos ou pardos), critério (só fenótipo) e consequência (sai da reservada, fica na ampla) mantidos |
| B21 | Critérios (texto livre): nota final = pontuação da prova de títulos, depois dos recursos, decrescente, por código; um só código por candidato | idem | ≈ | R | — |
| B22 | "Ordem: pela pontuação combinada das Etapas"; "Combinação: soma ponderada da Etapa Prova de títulos [...] (peso 1)"; "Normalização: nenhuma" | "A nota final é a pontuação obtida na Etapa 'Prova de títulos…'" | ≈ | G | com uma Etapa de peso 1 e sem normalização, a conta é a mesma (L6). Com duas Etapas, a frase volta a dizer soma ponderada |
| B23 | "Arredondamento: 2 casas decimais, meio para cima" | "A nota final é arredondada para 2 casas decimais; a partir da metade, arredonda-se para cima" | ≈ | G | L7 |
| B24 | Corte FIXED: "os 10 (dez) primeiros desta ordem, mais 5 (cinco) suplentes" para a Análise documental | "Passam para a Etapa 'Análise documental…' os 10 (dez) primeiros classificados, mais 5 (cinco) suplentes" | ≈ | G | — |
| B25 | Empate no corte `ADMITS_SURPLUS`: "progridem todos os empatados, ainda que excedam essa quantidade" | "passam todos os empatados, mesmo que ultrapassem esse número" | ≈ | G | — |
| B26 | Continuação | "Depois, poderão ser chamados outros candidatos, além desses, seguindo a mesma ordem" | ≈ | G | achado 1 |
| B27 | — (frase dos suplentes) | **não impressa** | — | G | achado 2: há cadastro de reserva |
| B28 | Desempate 1º "menor valor declarado em Data de nascimento; sem o valor, fica por último" | "maior idade (data de nascimento mais antiga, informada na inscrição); quem não a informar fica em último lugar neste critério" | ≈ | G | menor data = mais velho; ausência com o mesmo efeito (L4) |
| B29 | 2º "maior valor declarado em Meses de experiência…; sem o valor, fica por último" | "maior número de meses de experiência…, informado na inscrição; quem não o informar fica em último lugar" | ≈ | G | L5 |
| B30 | 3º "maior pontuação na Etapa Prova de títulos…; sem o valor, o critério não se aplica" | idem, "para quem não a tiver, o critério não se aplica" | ≈ | G | **!** para a comissão: o 3º critério repete a nota final, e só desempata se houver diferença que o arredondamento escondeu — é regra do cenário, mantida |
| B31 | Marco "aplica-se a cada Perfil separadamente" (3.21) | "A classificação é feita separadamente em cada Perfil" | ≈ | G | — |
| B32 | Recurso do marco: 3 dias corridos, contados da divulgação do resultado da "Classificação final pela prova de títulos" | idem, em "Como recorrer?" | → | G | — |
| B33 | 8.1 recursos "exclusivamente por meio do formulário eletrônico [...] observados os prazos do Cronograma"; 8.2 sem documentos; 8.3 sem Correios, e-mail ou outra forma | reescritos | ≈ | R | **!** o canal do Elaborador (formulário) e o do sistema (portal, 018) podem ser o mesmo ou não — por isso a frase gerada não diz canal |
| B34 | Etapa Prova de títulos: classificatória; peso 1; máx. 100; 1 avaliação; período | "Etapa classificatória, com pontuação máxima de 100 e peso 1. Cada inscrição recebe 1 (uma) avaliação. Será feita de… a…" | ≈ | G | — |
| B35 | Etapa Análise documental: eliminatória; Habilitado/Não habilitado; período | idem | ≈ | G | — |
| B36 | Cronograma (18 eventos) | mesmas linhas; "Quando" em "de … a …"; seção 4 | ≈ | G | datas, horas e locais idênticos |
| B37 | 11.1 convocação por mensagem ao e-mail da inscrição; 2 dias úteis contados do envio | "A mensagem será enviada ao endereço eletrônico informado na inscrição. O convocado terá 2 (dois) dias úteis, contados do envio, para manifestar interesse" | ≈ | R | sem repetir a frase gerada (B13) |
| B38 | 11.2 sem manifestação → desistente, substituído pelo próximo do mesmo código | idem | ≈ | R | — |
| B39 | Validade de 2 anos, da publicação do resultado final, prorrogável uma vez | idem | ≈ | R | — |
| B40 | Anexos I–VI | idem | = | G | — |
| B41 | 14.1–14.3 | reescritos | ≈ | R | — |
| B42 | Fecho; autoridade só pelo cargo; integridade | idem | = | G | ED-10 continua aberto |
| B43 | Título com "CEFOR/IFES" em caixa alta | "Cefor/Ifes" preservado | ≈ | G | ED-24 |
| B44 | Descrição do Edital | retirada; resumo | — | G | ED-25 |

---

## O que esta conferência não cobre

- **Leitura por quem não conhece o sistema.** A coluna "≈" foi decidida por quem conhece o domínio.
  O teste com candidatos (§8 do relatório) e a revisão da comissão são a verificação que falta.
- **Equivalência jurídica** das frases novas (A3, A30, B9) e do resumo dentro do ato.
- **Generalização.** São dois cenários. O compositor da amostra não tem nada escrito para eles, mas
  Editais com dois marcos no mesmo Perfil, sorteio com método próprio, Perfis com regras diferentes
  entre si ou Retificação não foram compostos.
