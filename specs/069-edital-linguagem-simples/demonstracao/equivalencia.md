# Equivalência das regras — o PDF da `068` × o da `069`

**2026-10-12 · cenários A e B da auditoria de 08/10, e a variante de B.** Conferência **por enunciado**
(FR-1396, SC-517), no molde da amostra (`doc/analise-edital-linguagem-simples-2026-10-12/equivalencia.md`):
para cada regra do documento de antes, se o de agora mantém **condição, exceção, alcance e
consequência**. A cobertura de fatos é automática e está em
`backend/tests/unit/publicacoes/test_documento_da_auditoria_depois_da_069.py` (SC-516): toda data, hora,
número por extenso, percentual, código, fundamento, Anexo, localidade, documento, o e-mail e o hash de
antes estão no de agora, em A e em B.

Documentos comparados: `specs/068-…/demonstracao/A-publicado-068.pdf` × `A-publicado-069.pdf`;
`B-publicado-068.pdf` × `B-publicado-069.pdf`; e `B-variante-069.pdf`, que só muda os suplentes dos
tutores presenciais. Os snapshots são os congelados da auditoria, levados ao catálogo da `069` — o
título e a ordem das seções, e nada mais.

**Legenda.**
- **=** igual, só redação.
- **≈** reescrito, mesmo efeito: o texto muda e a regra não.
- **→** movido para outra seção, sem mudar o texto da regra.
- **+** frase nova, gerada do dado ou descrevendo regra do sistema; **exige aprovação**.
- **!** ponto a decidir. A feature não decide, e deixa à vista.

Origem: **G** gerado pelo sistema; **R** redação do Elaborador.

---

## Achados desta conferência

1. **A forma de convocação gerada não diz mais onde se publica (V4).** Antes: "A convocação dos
   classificados será feita por publicação no endereço eletrônico do certame." Agora: "… por
   publicação." É a redação do contrato (V4), e a razão é que o endereço do certame é texto do
   Elaborador — o domínio congelado e a rota legível estão fora desta feature —; em A, o "onde" continua
   dito duas vezes pelo texto dele, nas Disposições preliminares ("Todas as publicações deste processo
   seletivo serão feitas no endereço eletrônico do certame") e na convocação dos suplentes. **!** Num
   Edital cujo texto não diga onde publica, o documento passa a não dizer. Para aprovação do responsável
   pelo produto, junto das frases novas.
2. **A numeração digitada de B colide com as subseções da apresentação por perguntas.** O texto de B foi
   transcrito com a numeração do original ("2.1 Ser brasileiro…", "3.1 A inscrição…", "4.1 Os
   candidatos…", "11.1 A convocação…", "14.1 A inscrição…"). Na apresentação por perguntas, "2.1" é
   também a subseção "Requisitos gerais". A conferência da `065`, com a regra do prefixo apresentado
   (R-003), acusa cada uma como conflito comprovado, e **a publicação deste snapshot seria recusada**
   até o Elaborador corrigir a numeração — o mesmo tratamento que a `065` dá ao texto numerado de outro
   Edital. Não é perda de regra; é o que a demonstração mostra por partir de texto congelado.
3. **A remissão "descritos na seção Perfis de Vaga" (A, Requisitos gerais; A, seleção)** aponta para um
   título que o documento novo não tem. O aviso da FR-1400 aparece na Revisão, diz que a seção foi
   repartida e lista os destinos; o texto não é reescrito (FR-1395).
4. **Nenhuma condição foi acrescentada.** A continuação do corte saiu como "Depois, poderão ser chamados
   outros candidatos, além desses, seguindo a mesma ordem" (K9), sem "se sobrarem vagas" — a correção
   que a amostra registrou no achado 1 dela.

---

## Cenário A (pós-graduação, 4 polos, sorteio)

| # | Antes (`068`) | Agora (`069`) | Classe | Origem | Observação |
|---|---|---|---|---|---|
| A1 | Preâmbulo | idem | = | R | — |
| A2 | Descrição do Edital entre o título e o preâmbulo | retirada | — | G | sem regra (FR-1378, ED-25); fica no portal |
| A3 | — | Resumo: vagas, cadastro, inscrições, teto, seleção, datas, com o item de cada um | + | G | só dado; declara que não substitui as seções (FR-1370, D-005). **Aprovação** |
| A4 | Anúncio "MODALIDADE EAD" | "MODALIDADE EaD" | = | G | sigla preservada (FR-1377) |
| A5 | Disposições preliminares (Comissão, e-mail, publicações) | idem | = | R | — |
| A6 | Informações gerais (a distância, AVA, síncronos obrigatórios, 480 h, 18 meses) | idem | = | R | — |
| A7 | Público-alvo | 3.1, sob "Quem pode se inscrever?" | → | R | texto literal |
| A8 | Requisitos gerais ("descritos na seção Perfis de Vaga") | 3.2 | → **!** | R | texto literal; remissão textual com aviso (achado 3) |
| A9 | 5.5 Requisitos comuns aos Perfis (diploma reconhecido pelo MEC; computador com internet) | 3.3 Requisitos dos Perfis, a mesma lista, sem rótulo de grupo | → | G | alcance: todos os Perfis, e a seção diz "dos Perfis" |
| A10 | Tabela 1 (Perfil, localidade, vagas, cadastro, carga) + Tabela 2 (vagas por lista) | Tabela 1 — Vagas por Perfil e lista de concorrência (código, localidade, listas, total, linha de total) | ≈ | G | os mesmos números; 160 no total |
| A11 | Descrição de cada Perfil (5.1–5.4) | Tabela 2 — Características dos Perfis | → | G | texto literal |
| A12 | "Especialização…", 480 horas, cadastro "não há", repetidos por Perfil | "Em todos os Perfis: Especialização em Informática na Educação; carga horária de 480 horas; não há cadastro de reserva." | ≈ | G | dito uma vez, por identidade (FR-1374) |
| A13 | Tabela 3 — Modalidades (com a linha AC) | Tabela 3 — Reserva de vagas (sem AC) | ≈ | G | percentuais e fundamentos iguais; AC não é reserva |
| A14 | Reversão V1 ("Havendo ausência de candidatos aprovados na reserva de vagas…") | "Se não houver candidatos aprovados para as vagas reservadas de um código, essas vagas passam para a ampla concorrência do mesmo código." | ≈ | G | condição e alcance por código explícitos |
| A15 | Convocação "por publicação no endereço eletrônico do certame" | "por publicação", em "Como será a convocação?" | ≈ → **!** | G | achado 1 |
| A16 | "Marcos classificatórios: os descritos no item 5.6" por Perfil | — | — | G | a remissão some porque a regra está na seleção |
| A17 | "Os marcos abaixo se aplicam a cada um desses Perfis separadamente…" | "A classificação é feita separadamente em cada Perfil: cada Perfil tem a sua própria classificação e o seu próprio resultado." | ≈ | G | alcance preservado (FR-1347) |
| A18 | "Ordem: por sorteio"; "Habilitação: participam todas as inscrições submetidas" | "Participam do sorteio todas as inscrições enviadas." | ≈ | G | C2/C4 |
| A19 | Sorteio: método, algoritmo, fonte, ocorrência, quando, derivação, semente, se faltar | "Dados para conferir o sorteio" (8.2), em destaque: abertura com fonte, ocorrência e instante; método e algoritmo; qual concurso; semente; se faltar | ≈ → | G | os sete dados, inteiros (FR-1376, S1–S7) |
| A20 | Corte: "Progridem para Análise documental os primeiros desta ordem, até o número de vagas ofertadas no recorte, mais 15 (quinze) suplentes." | "Passam para a Etapa “Análise documental” os primeiros classificados de cada lista de concorrência, em número igual ao das vagas dessa lista, mais 15 (quinze) suplentes." | ≈ | G | "recorte" dito pelo que é (K3) |
| A21 | — | "Os suplentes são chamados, na ordem, para as vagas deste Edital que não forem preenchidas pelos primeiros classificados." | + | G | K7: só sem cadastro de reserva em nenhum Perfil (D-004). **Aprovação** |
| A22 | Continuação: "Poderá haver chamada, nesta ordem, além dos que este corte publicar." | "Depois, poderão ser chamados outros candidatos, além desses, seguindo a mesma ordem." | ≈ | G | achado 4 |
| A23 | Recurso: "Caberá recurso contra o resultado de “X”, no prazo de 2 (dois) dias corridos…" (no marco) | "Contra o resultado de “X”: no prazo de 2 (dois) dias corridos, contados da divulgação desse resultado." em "Como recorrer?" | ≈ → | G | R1; sem canal (FR-1363) |
| A24 | Da Inscrição (texto) | "Como se inscrever?" | = | R | — |
| A25 | — | "Período de inscrições: de 13/10/2026, às 09h, a 30/10/2026, às 23h59 (Cronograma, nº 1)." | + | G | V9: repete o Cronograma. **Aprovação** |
| A26 | "Cada candidato poderá ter apenas 1 inscrição enviada neste Edital." | "Cada candidato pode enviar apenas 1 (uma) inscrição neste Edital." | ≈ | G | V7 |
| A27 | — | "A inscrição inclui o Requerimento de Matrícula (item 11)." e "Além destes documentos, a inscrição inclui o Requerimento de Matrícula (item 11)." | + | G | V13: lembrete. **Aprovação** |
| A28 | Documentos exigidos (de todos; PPI; PcD) | idem, "Também, de quem concorre às vagas para…" | ≈ | G | D2–D4; instrução em minúscula (D5) |
| A29 | Verificação da autodeclaração (seção 8) | 8.4, sob a seleção | → | R | texto literal |
| A30 | Etapa: "Caráter: eliminatória; Resultado: Deferida ou Indeferida; Realização: …" | "Etapa eliminatória: o resultado é “Deferida” ou “Indeferida”. Será feita de … a …" | ≈ | G | E1–E3 |
| A31 | Critérios de classificação (texto) | principal de "Como será a seleção?" | → **!** | R | texto literal; "conforme o método publicado na seção Perfis de Vaga" (achado 3) |
| A32 | Cronograma: Início, Término | Quando: "de … a …" | ≈ | G | as mesmas datas e horas |
| A33 | Dos Recursos (texto) | depois da frase R1 | → | R | texto literal |
| A34 | Da Convocação (texto) | depois da frase V4 | → | R | texto literal |
| A35 | Matrícula; "O Requerimento de Matrícula será enviado no ato da inscrição. Ao enviá-lo, o candidato declarará:" | "O Requerimento de Matrícula é enviado no ato da inscrição. Ao enviá-lo, o candidato declara:", com a declaração em destaque | ≈ | R, G | V11 |
| A36 | Certificado, Anexos, Disposições finais | idem | = | R, G | — |
| A37 | "Verificação de integridade — este documento deriva integralmente…" | "Autenticidade — este documento corresponde integralmente à versão homologada…" | ≈ | G | F1; o hash é o mesmo |

## Cenário B (tutoria UAB, 18 Perfis, cadastro de reserva, pontuação)

| # | Antes (`068`) | Agora (`069`) | Classe | Origem | Observação |
|---|---|---|---|---|---|
| B1 | Descrição do Edital | retirada | — | G | FR-1378 |
| B2 | — | Resumo: "10 vagas imediatas, nos Perfis TD-ADM e TD-INFO-EDU; os demais formam cadastro de reserva"; cadastro "até 15 (quinze) classificados por Perfil"; seleção "pontuação em uma etapa classificatória, com uma etapa eliminatória" | + | G | nome longo das Etapas fora do resumo (FR-1371). **Aprovação** |
| B3 | Anúncio "CEFOR/IFES" | "Cefor/Ifes" | = | G | FR-1377 |
| B4 | Disposições preliminares 1.1–1.4 | idem | = | R | — |
| B5 | Requisitos gerais 2.1–2.4 | 2.1, sob "Quem pode se inscrever?" | → **!** | R | numeração digitada colide (achado 2) |
| B6 | Requisitos por Perfil (TD-ADM, TD-INFO-EDU) e 3.20 comuns aos TP | 2.2 Requisitos dos Perfis, por grupo: "Para o Perfil TD-ADM…", "Para o Perfil TD-INFO-EDU…", "Para os Perfis TP-01 a TP-16" | → | G | listas literais; faixa contígua (FR-1375) |
| B7 | Tabela 1 (18 Perfis; cadastro "limitado em 15"; carga) | "São 10 vagas imediatas, nos Perfis TD-ADM e TD-INFO-EDU." + Tabela 1 — Perfis (os dois TD) + Tabela 2 — Tutor presencial — Perfis TP-01 a TP-16 | ≈ | G | Perfis de mesmo nome em tabela própria, com o nome na legenda (SC-524) |
| B8 | Tabela 2 — vagas por lista (PTT com 0) | Tabela 3 — Vagas imediatas por lista de concorrência (PTT com 0, total) | = | G | — |
| B9 | Carga horária, remuneração e cadastro repetidos | "Em todos os Perfis: carga horária de 20 horas semanais; remuneração: bolsa mensal no valor de referência fixado pela CAPES para tutor; cadastro de reserva de até 15 (quinze) classificados por Perfil." | ≈ | G | a inicial do valor da remuneração em minúscula, dentro da frase |
| B10 | Tabela 3 — Modalidades (PTT "—") | Tabela 4 — Reserva de vagas (PTT "—") | ≈ | G | sem a linha AC; o "—" sem percentual fica |
| B11 | Reversão V2 ("Na hipótese do não preenchimento total…") | "As vagas reservadas de um código com vagas imediatas (TD-ADM e TD-INFO-EDU) que não forem preenchidas passam para a ampla concorrência do mesmo código." | ≈ | G | V3: alcance dito (só os Perfis com vagas) |
| B12 | Convocação individual (V5) | "A convocação será feita por mensagem individual à pessoa convocada.", em "Como será a convocação?" | ≈ → | G | — |
| B13 | Atribuições por Perfil + 3.19 comuns aos TP | 3.1 Atribuições, por grupo | → | G | texto literal, inclusive o item sem marcador de TD-INFO-EDU |
| B14 | "Dados exigidos na inscrição" por Perfil, com o tipo | "Na inscrição, informe também: o número de meses…; a data de nascimento." + "Esses dados são usados no desempate (item 7.1)." | ≈ + | G | V10: uma vez, igual em todos; a frase do uso é nova. **Aprovação** |
| B15 | 3.21 "Marcos classificatórios comuns…" + "aplicam-se separadamente" | 7.1 Classificação + CLASSIFICACAO_SEPARADA | ≈ → | G | alcance preservado |
| B16 | "Ordem: pela pontuação combinada das Etapas"; "Combinação: soma ponderada da Etapa … (peso 1)" | "A ordem de classificação segue a nota final." "A nota final é a pontuação obtida na Etapa “…”." | ≈ | G | C3, C8 (uma Etapa: sem peso, que não muda nada) |
| B17 | "Normalização: nenhuma" | — | ≈ | G | C9: "nenhuma" não é regra |
| B18 | Arredondamento | "A nota final é arredondada para 2 casas decimais; a partir da metade, arredonda-se para cima." | ≈ | G | C12 |
| B19 | Corte 10 + 5 suplentes; empate no corte; continuação | os três itens, juntos | ≈ | G | K1, K5, K9; sem K7 (há cadastro: D-004) |
| B20 | Critérios de desempate 1º–3º | idem, "data de nascimento mais antiga…", "maior número de meses…", "maior pontuação na Etapa “…”" | ≈ | G | T1, T2 (D-006); ausência preservada |
| B21 | Recurso no marco (R1) | "Como recorrer?", antes do texto | ≈ → | G | — |
| B22 | Da Inscrição 3.1–3.4 | "Como se inscrever?" | → **!** | R | achado 2 |
| B23 | Teto V7 | V7 | ≈ | G | — |
| B24 | — | Período de inscrições (V9) | + | G | **Aprovação** |
| B25 | Documentos exigidos; por Perfil (TP-01, TD-INFO-EDU); por lista (PPIQ, PcD, PTT) | idem, "Também, de quem concorre ao Perfil…" e "…às vagas para…" | ≈ | G | D2–D4; o comprovante de residência só do TP-01 é o dado (achado próprio em `doc/`) |
| B26 | Verificação 4.1–4.3; Atendimento PcD | 7.4 e 5.1 | → **!** | R | numeração digitada (achado 2) |
| B27 | Etapas (Caráter, Peso, Pontuação máxima, Avaliações, Realização) | frases E1–E3, como subseções 7.2 e 7.3 | ≈ → | G | a avaliação por inscrição continua dita |
| B28 | Critérios de classificação (texto) | principal de "Como será a seleção?" | → | R | — |
| B29 | Cronograma (18 Eventos) | "Quando" | ≈ | G | — |
| B30 | Recursos 8.1–8.3, Convocação 11.1–11.2, Prazo de validade, Anexos, Disposições finais | idem, nas seções novas | → | R, G | numeração digitada (achado 2) |
| B31 | Integridade | Autenticidade | ≈ | G | F1 |

## Variante de B (suplentes diferentes nos tutores presenciais)

| # | B | Variante | Classe | Observação |
|---|---|---|---|---|
| V1 | Regras de classificação iguais para os 18 Perfis | "Para todos os Perfis:" com a ordem, a combinação, o arredondamento e o desempate; depois "Para os Perfis TD-ADM e TD-INFO-EDU:" e "Para os Perfis TP-01 a TP-16:", cada um com a sua unidade do corte | ≈ | partilha parcial (R-009): o comum uma vez; a unidade do corte — corte, empate, continuação — inteira em cada grupo |
| V2 | 5 suplentes | 5 para os TD, 3 (três) para os TP | = | o dado da variante, nos dois grupos |

## Frases novas para aprovação (SC-517)

| Frase | Onde | Quando sai |
|---|---|---|
| K7 — "Os suplentes são chamados, na ordem, para as vagas deste Edital que não forem preenchidas pelos primeiros classificados." | seleção | só sem cadastro de reserva em nenhum Perfil (D-004) |
| Resumo — vagas, cadastro, inscrições, teto, seleção, datas | depois do preâmbulo | sempre que houver dado; cada linha só quando o dado a sustenta |
| V9 — "Período de inscrições: de … a … (Cronograma, nº N)." | "Como se inscrever?" | com o Evento de inscrições |
| V10 — "Esses dados são usados no desempate (item N)." | "Como se inscrever?" | quando algum critério usa o fato |
| V13 — "Além destes documentos, a inscrição inclui o Requerimento de Matrícula (item N)." | Documentos e Inscrição | Requerimento na inscrição |
| V4 — convocação "por publicação", sem o onde | "Como será a convocação?" | achado 1 |
| P1 de um Perfil — "Perfil P1: nome — descrição; carga horária de …; remuneração: …; cadastro …." | "Quantas vagas há, e onde?" | Edital de um Perfil só (revisão de código) |
| Resumo, seleção — "sorteio, com …" / "pontuação em …, com …", no lugar de "seguido de" | resumo | o dado não diz a ordem entre o sorteio e as Etapas (revisão de código) |

**Situação: aguardando a aprovação do responsável pelo produto.** Esta conferência não as aprova.
