# Complemento — Documentos e conferência na convocação, para além da matrícula — 03/11/2026

*Complemento crítico à [auditoria de matrícula e dossiê documental](auditoria-matricula-e-dossie-documental-2026-11-03.md),
pedido pelo usuário em 03/11/2026, sobre a mesma `main` (`6137f1c4`). A pergunta é se a recomendação
da auditoria tinha viés de escopo: o GPS conduz seleção de alunos, mas também de bolsistas,
professores formadores, colaboradores e servidores. Nada foi implementado. Este documento traz só o
que muda; o que não é citado aqui continua valendo como está na auditoria. As marcas são as mesmas:
[F] código, [S] spec ou doc, [N] norma, [E] Edital, [I] inferência, [H] hipótese.*

> **A §10 registra a decisão de produto de 03/11/2026 sobre a fronteira do GPS**: não é GED nem
> acervo; a seleção confere e decide; o setor competente formaliza e custodia. Ela prevalece sobre
> o que divergir dela neste documento e na auditoria.

**Editais acrescentados à evidência** (em `~/Downloads`, pela convenção do projeto):

- bolsistas e colaboradores: 89/2026 e 90/2026 (mediadores e tutores UAB), 140/2025 (tutores
  presenciais), 146/2025 (assistente pedagógico) e 14/2026 (orientador de TFC), além do 173/2025 e
  do 73/2026 da auditoria;
- servidores, da Reitoria: 04/2026 (licença para capacitação) e 05/2026 (afastamento);
- alunos: 72/2026 (vagas remanescentes de Multimeios), composto no próprio GPS.

---

## Resumo

**O ajuste procede, e a evidência é mais forte do que o pedido supunha.** A necessidade de exigir,
receber e conferir documento **depois da inscrição** aparece em todas as famílias de Edital lidas
que terminam em vínculo:

- **[E] 89/2026, 11.1–11.2.** O certificado do curso de formação, se não veio na inscrição, *"é
  obrigatório apresentá-lo quando convocados"*, e quem não o apresenta *"será desclassificado"*.
  É o caso mais limpo: o **mesmo** documento serve ao desempate na inscrição (6.2.5, c) e ao
  requisito de vinculação na convocação.
- **[E] 89 e 90/2026, 2.2.** A idade mínima de 18 anos é verificada *"na data da vinculação"*, e
  não na inscrição.
- **[E] 140/2025 (10.3) e 173/2025 (9.3).** *"No ato da vinculação apenas serão vinculados os
  candidatos que, quando convocados, cumpram os requisitos necessários à sua função."*
- **[E] 14/2026 (12.3), 89/2026 (13.3), 90/2026 (12.3), 140/2025 (13.3) e 146/2025 (20.4).** A
  *Ficha de Cadastramento/Termo de Compromisso do Bolsista* é *"disponibilizada no momento
  oportuno"*, preenchida, assinada e entregue depois da convocação.
- **[E] 69/2026 (6.1) e 72/2026 (item 8).** Os documentos de matrícula são entregues
  presencialmente na convocação. O 72 foi composto no GPS, e mesmo assim manda o candidato ao
  balcão: é a mesma lacuna, num Edital do próprio sistema.

**Há também um contraexemplo, e ele delimita a capacidade.** Nos Editais de servidores, a
formalização acontece inteira fora da seleção:

- [E] 05/2026, 1.4: a aprovação *"não garante o afastamento automático"*; depois vem a *"abertura de
  processo para análise dos demais requisitos"*;
- [E] 04/2026, 4.2.3: *"os demais documentos comprobatórios serão extraídos pela Coordenadoria de
  Gestão de Pessoas"*;
- a desistência é por documento no SIPAC (04/2026, 5.5.1).

Ali, o GPS não deve receber nada depois da classificação. A capacidade é **opcional por documento**,
e não fase obrigatória de todo Edital.

**A recomendação técnica não muda; muda o que ela nomeia.** A auditoria já recomendava completar a
convocação, que é neutra quanto à natureza do vínculo:

- [F] o portal da `059` *"não diz matrícula nem contratação"* (`portal/situacao.py:57-60, 343`);
- [F] o desfecho *Aceite* aparece como *"Vaga aceita"* (`portal/situacao.py:62`).

O viés estava no que vinha **em volta**: a secretaria como ator, *"Documentos para a matrícula"* como
seção, `matricula:conferir` como capacidade e a QI-1 perguntando pela secretaria. Corrigido isso, a
primeira spec deve ser **"Documentos e conferência na convocação"**. A matrícula é o primeiro caso
demonstrável, e o 146/2025 (bolsista com vaga imediata) é o segundo.

**Três achados novos mudam o desenho:**

1. **Num mesmo Edital, quem confere varia.** No Cefor, a matrícula é dirigida à *Coordenadora de
   Registros Acadêmicos* [E 77, Anexo II]; a vinculação do bolsista é da *Coordenação da UAB*
   [E 14, 14.2; 146, 22.2] ou do *Coordenador do Curso* [E 140, 13.3]. Um papel único por unidade
   faria o registro acadêmico ver documento de bolsista, e o inverso. **A competência precisa de
   designação por Processo, e não só de papel na unidade** (§4).
2. **O multiunidade já aparece nos Editais de bolsista, e não só no 46.** O 89 e o 90/2026 são do
   Cefor, e os Perfis pertencem a cursos de *"Campus ofertante: Campus de Alegre"*, com polos em
   quatro municípios (Anexo III). A primeira spec precisa registrar **a unidade em que cada ato foi
   praticado**, para não ser reestruturada depois (§6).
3. **Dos sete desfechos, seis servem a vínculos não acadêmicos. O sétimo tem rótulo acadêmico e é
   oferecido a todo Edital.** É *"Cancelamento de matrícula por inércia"*
   (`convocacao/models.py:250`; `portal/situacao.py:67`). O desligamento do bolsista depois da
   vinculação é da Coordenação UAB, fora da seleção [E 14, 14.2], e não é esse desfecho (§5).

---

## 1. A capacidade pode ser comum? Evidência por família

| Família | Edital | O que se exige depois da convocação | Quem recebe ou confere | Se faltar | Onde se formaliza |
|---|---|---|---|---|---|
| Alunos, técnico | 69, 72/2026 | documentos de matrícula (Anexo I), presencialmente | Cefor, na entrega | reclassificação para o fim da lista (69, 6.3) | SIGAA |
| Alunos, FIC e pós | 77, 57, 28/2026 | hoje nada: tudo vai na inscrição (a causa da auditoria) | Registro Acadêmico (Anexo II) | indeferimento | SIGAA (77, 8.1 a) |
| Alunos, técnico multicampi | 46/2026 | requerimento ao campus (item 10); escolaridade *"no ato do requerimento de matrícula"* | campus | — | campus / SIGAA |
| Bolsista UAB, mediador e tutor | 89, 90/2026 | certificado do curso de formação (89, 11.1); idade na vinculação (2.2); Ficha/Termo (13.3, 12.3) | Coordenação UAB / coordenação do curso | desclassificação (89, 11.2) | cadastro CAPES (Lei 11.273/2006, citada em 12.2) |
| Bolsista UAB, tutor presencial | 140/2025 | requisitos da função *"no ato da vinculação"* (10.3); Ficha/Termo assinados *"no local determinado pelo Coordenador do Curso"* (13.3) | coordenador do curso | não vinculação | CAPES |
| Bolsista, assistente pedagógico | 146/2025 | Ficha/Termo (20.4); pagamento por depósito em conta, conforme a CAPES (19.5) | Coordenação UAB | — | CAPES |
| Bolsista Fapes | 173/2025 | requisitos da bolsa (11.2); o cadastro é aprovado pela Fapes (11.3) | Coordenação; **Fapes** decide o cadastro | *"não obtenção da bolsa e desclassificação"* (11.2) | Fapes |
| Professor formador e orientador | 14/2026 | *"comprovar os demais requisitos"* da Lei 11.273 (12.2); Ficha/Termo (12.3), entregue no Cefor | Coordenação UAB | — | CAPES |
| Servidores | 04, 05/2026 | **nada no certame**: um processo à parte no SIPAC; a CGP extrai os documentos | CGP, chefia | — | SIPAC |

**Conclusão [I].** Três padrões se repetem fora da matrícula, e os três são o que a capacidade da
auditoria faz:

- um documento exigido **na convocação**;
- uma conferência por quem tem competência;
- uma consequência registrada quando falta.

O que **não** se repete é o que vem depois. Matrícula no SIGAA, cadastro na CAPES ou na Fapes e
processo no SIPAC são outros sistemas, outros setores e outros prazos de guarda. A fronteira certa é
exatamente a da auditoria: o GPS vai **até o desfecho da convocação e o encaminhamento**, e para ali.

**O que não está demonstrado, e por isso não entra:**

- coleta de dados bancários pelo GPS: o 146 (19.5) diz só que a CAPES deposita, e o dado vai na
  Ficha da agência;
- formulário estruturado de bolsista, equivalente ao Requerimento de Matrícula: a Ficha é modelo
  **da agência**, a ser preenchido e assinado, e cabe como Documento Exigido com modelo anexo
  (`DocumentoExigido.anexo`, `editais/models/documentos.py:52-58`);
- etapas pós-vínculo: avaliação por disciplina (173, 11.3) e desligamento (14, 14.2).

## 2. Recomendação orientada à matrícula × capacidade transversal à convocação

| Aspecto | Como estava (auditoria, §F.1) | Capacidade transversal (recomendada) | Custo da diferença |
|---|---|---|---|
| Nome e escopo da spec | "Documentos de matrícula na convocação" | **"Documentos e conferência na convocação"** | zero |
| Momento do Documento Exigido | `INSCRICAO` / `CONVOCACAO` | igual | zero: já era neutro |
| Seção do PDF | "Documentos para a matrícula" | **"Documentos exigidos na convocação"**; o Edital diz na instrução para que serve | zero |
| Quem confere | papel de secretaria na unidade (`matricula:conferir`) | **designação por Processo** de quem confere, com capacidade neutra (§4) | pequeno: uma designação a mais |
| Quem decide | desfecho existente (presidência) | igual, com a capacidade de desfechar **separável** da de conferir (§4) | pequeno |
| Desfechos | os sete atuais | os sete atuais; o rótulo da inércia é registrado como achado (§5) | zero na spec |
| Requerimento de Matrícula | dados `AT_CALL` | **igual, e continua acadêmico**: não se cria "requerimento genérico" | zero |
| Formulário do bolsista | — | **Documento Exigido com modelo anexo**, assinado e devolvido | zero: o modelo já existe |
| Aproveitamento de documento da inscrição | por referência | igual; o 89/2026 é o caso que o demonstra fora da matrícula | zero |
| Dossiê e destinação | "dossiê da matrícula", com a TTD acadêmica | **dossiê operacional da convocação**; a destinação depende da natureza e não é desta spec (§6) | zero na spec; evita refazer depois |
| Unidade | Edital de unidade única | igual no piloto, mas o ato registra a unidade de atuação, e a autorização passa por um predicado só (§7) | pequeno |
| Primeiro cenário demonstrável | matrícula no Cefor | matrícula no Cefor (tipo 72/2026), e **também** um bolsista de vaga imediata (tipo 146/2025) | um cenário de teste a mais |

**A capacidade transversal custa quase o mesmo e evita duas reestruturações**: a renomeação de uma
capacidade de autorização já concedida, e o remodelo da designação quando o primeiro Edital de
bolsista usar o recurso. A matrícula, construída primeiro com nomes de matrícula, deixaria as duas
como dívida.

**Onde a transversal pode virar o que não se quer.** É preciso recusar:

- uma taxonomia de "natureza do vínculo" que governe estados;
- etapas configuráveis depois da convocação;
- um formulário configurável para substituir a Ficha da agência.

Os três estão fora porque nenhuma regra demonstrada os consome. A Constituição, V, exige necessidade
demonstrável. Pelo padrão do projeto, entidade nasce quando a regra que a consome nasce.

## 3. Particularidades sem motor de workflow

As particularidades vivem em **quatro lugares que já existem**, e nenhum é novo estado.

| O que varia por Edital | Onde fica | Exemplo |
|---|---|---|
| **Quais** documentos, para quem e **quando** | Documento Exigido: recorte, obrigatoriedade, instrução, modelo anexo e, agora, momento | certidão (aluno); Ficha/Termo (bolsista); certificado de formação (mediador, na inscrição **ou** na convocação) |
| **Que dados** estruturados | Requerimento de Matrícula (`029`), só onde o Edital o declara | alunos; nenhum outro caso demonstrado |
| **Que consequência** tem a falta | desfecho existente, com fundamento | indeferimento (*"desclassificado"*, 89, 11.2), não atendimento, reclassificação (69, 6.3) |
| **Onde se formaliza** depois | fora do GPS: exportação, encaminhamento | SIGAA; CAPES/Fapes; SIPAC |

**O caso do 89/2026 testa o desenho.** O certificado é facultativo na inscrição, onde vale como
desempate, e obrigatório na convocação para quem não o enviou. No desenho, isso fica assim:

- **dois Documentos Exigidos com momentos distintos**, ou **um com dois momentos**;
- **aproveitamento por referência**: o documento enviado na inscrição atende a exigência da
  convocação sem reenvio.

A escolha entre "dois registros" e "um com dois momentos" é decisão de plano. **[I] Recomenda-se
"dois registros com vínculo de aproveitamento"**, porque cada um tem obrigatoriedade e consequência
próprias, e porque a lista exigida da inscrição (`ItemDaListaExigida`, `inscricoes/models.py:201`)
já está congelada e não deve ganhar semântica de convocação.

## 4. Quem confere e quem decide, sem presumir secretaria

**Fato [F].** O desfecho é registrado por quem pode gerir a comissão do Processo: a permissão
sistêmica `comissao:gerir` ou a presidência da comissão (`comissoes/domain/autorizacao.py:65-81`,
chamada por `convocacao/application/desfechar.py:69`). A comissão tem duas funções, `PRESIDENTE` e
`MEMBRO`, e é **por Processo** (`comissoes/models.py:31-45`). Não há conferente.

**Fato [E].** No mesmo Cefor, o responsável muda com a natureza do Edital: Registro Acadêmico
(alunos), Coordenação UAB ou coordenador do curso (bolsistas). Na Reitoria, a CGP (servidores, que
nem usariam a capacidade).

**Três formas de dar a competência:**

| Opção | Como | A favor | Contra |
|---|---|---|---|
| 1. Papel na unidade | `Vinculo(pessoa, unidade, "conferente")`, como os papéis atuais | trivial; já é como o SSO vai alimentar | **reprovada pela evidência**: no Cefor, o Registro Acadêmico veria os documentos dos bolsistas, e a Coordenação UAB, os dos alunos |
| 2. Nova função na comissão | `MembroComissao.funcao = CONFERENTE` | reusa designação por Processo, troca, impedimento e trilha | chama de comissão de seleção quem não é; a identidade do membro ainda é texto livre, pendente do SSO ([S] `doc/ativacao-do-sso-institucional.md`, §4) |
| **3. Papel na unidade + designação por Processo** | o papel diz que a pessoa *pode* conferir; a designação, *em quais Processos* (e, opcionalmente, *em quais Perfis*) | segrega por Edital; reusa o `Vinculo` do SSO; a designação por Perfil é a mesma peça que o multiunidade vai usar (§7) | duas peças |

**Recomendação [I]: a opção 3.** A designação pode seguir o molde da comissão: append-only, com
motivo, quem designou e revogação. O que se recomenda separar desde já:

- **conferir** (juízo por documento) e **desfechar** (decisão sobre a convocação) como capacidades
  distintas;
- o desfecho continua com a base atual por padrão, e a spec admite que a designação conceda também
  o desfecho, **se** a QI-1 assim decidir.

Separar agora custa pouco. Juntar e separar depois exige migrar autorizações concedidas.

**A pergunta institucional reformulada** substitui a QI-1 da auditoria:

> **QI-1′ — Em cada tipo de Edital, quem confere os documentos exigidos depois da convocação, e
> quem decide sobre o atendimento das exigências: a mesma pessoa ou setor, ou outra?** E a quem
> se encaminha o selecionado para a formalização (registro acadêmico, coordenação do programa de
> bolsas, gestão de pessoas)?

## 5. Os desfechos atuais servem a vínculos não acadêmicos?

| Desfecho (rótulo no portal) | Matrícula | Bolsista / colaborador | Compatível? |
|---|---|---|---|
| Aceite ("Vaga aceita") | aceite registrado ≠ matrícula efetivada | aceite registrado ≠ bolsa concedida: a Fapes aprova o cadastro depois (173, 11.3) | **sim**, com o mesmo cuidado de vocabulário (MAT-15) |
| Indeferimento ("Indeferido na convocação") | documentação não atende | *"desclassificado"* por falta de certificado (89, 11.2); *"não serão vinculados"* (140, 10.3; 173, 9.3) | **sim**; o Edital diz "desclassificação", o sistema diz "indeferimento", e a diferença de termo é só registro |
| Desistência expressa | sim | sim (04/2026, 5.5, num caso análogo) | **sim** |
| Não atendimento | sim | sim (o convocado que não entrega) | **sim** |
| Reclassificação | sim (69, 6.3; 72, item 8) | não demonstrado | **sim**: opcional, e o Edital que não a prevê não a usa |
| Regularização / convocação para regularizar | 77, 8.2–8.3 | não demonstrado | **sim**, e menos necessária com a complementação |
| **Inércia ("Matrícula cancelada por inércia")** | 77, 9.2 (não acessar o AVA) | **não se aplica**: o desligamento do bolsista é pós-vínculo e da Coordenação UAB (14, 14.2; 146, 22.2), fora do GPS | **incompatível no rótulo**; oferecida a qualquer Edital (`convocacao/domain/nomes.py:73-97` não distingue natureza) |

**O fato externo depois do aceite já é representável.** A Fapes pode recusar o cadastro depois que
o GPS registrou o aceite (173, 11.2). A sucessão de desfechos é genérica: qualquer espécie sucede a
vigente, com motivo obrigatório (`convocacao/application/desfechar.py:126-134`). Um indeferimento
que sucede o aceite, com fundamento *"cadastro de bolsista não aprovado pela Fapes"*, exclui da
ocupação e reabre a vaga. **Não há desfecho novo a criar.**

**Incompatibilidades que não são desta spec, já registradas na `097`** ([S]
`specs/097-convocar-do-cadastro-de-reserva/spec.md:379-386`): os Editais de bolsista de cadastro de
reserva (89, 90, 140, 173) dependem de três coisas que o GPS não tem:

- a sequência de convocação entre modalidades como dado;
- o retorno à ampla concorrência na falta da modalidade;
- a validade de 2 anos.

O desligamento depois da vinculação é *"pergunta dela"*. **Consequência para esta spec:** a
capacidade documental pode ser especificada para qualquer Edital, mas o primeiro bolsista
demonstrável é o de **vaga imediata** (146/2025). Os de cadastro de reserva esperam a spec da `097`.

## 6. Dossiê operacional × documentos a encaminhar

**A separação que a auditoria pedia fica mais nítida com as outras famílias.**

- **Dossiê operacional da convocação** é a prova do ato do certame. Ele contém:
  - a lista exigida congelada na convocação;
  - os documentos apresentados, com versões e hash;
  - as referências aos documentos da inscrição que foram aproveitados;
  - cada conferência, com autor, unidade, instante e motivo;
  - o desfecho e a trilha.

  Ele responde *"por que esta pessoa foi aceita ou indeferida"*, e é o que um recurso, um controle
  ou um pedido do titular consulta. **Pertence ao processo seletivo**, qualquer que seja o vínculo.
- **Documentos a encaminhar** são o subconjunto que o setor de formalização precisa: os arquivos da
  convocação com desfecho que **inclui** (aceite ou regularização). O destino muda com a natureza:

  | Natureza | Destino |
  |---|---|
  | Aluno | Registro Acadêmico / SIGAA. [N] Na TTD das IFES, o assentamento do aluno tem 100 anos (456.43) |
  | Bolsista | Coordenação UAB e cadastro da agência. [H] A classe arquivística não foi verificada: a Portaria AN 92/2011 trata de atividades-fim; a de atividades-meio não foi lida |
  | Servidor | não se aplica: o processo nasce no SIPAC |

**O que permite política de retenção por finalidade sem dois armazenamentos [I]:** o **registro da
conferência** e o **arquivo** têm ciclos distintos.

- O registro (quem conferiu, quando, o quê, contra qual hash) é ato do certame e fica no GPS sob a
  guarda do processo seletivo.
- O arquivo é encaminhado e, depois, pode ter destinação própria por natureza, com listagem aprovada
  ([N] Lei 8.159, art. 9º).
- O hash no registro continua provando o que foi conferido mesmo depois de o arquivo sair.

**O que a primeira spec precisa fazer, e o que não precisa:**

| Precisa | Não precisa |
|---|---|
| guardar os documentos da convocação **ligados à convocação**, separados dos da inscrição | política de retenção ou destinação |
| gravar, por documento, requisito, hash, instante e versão | taxonomia de natureza do vínculo |
| gravar a conferência como ato próprio, distinto do arquivo | encaminhamento automatizado, pacote de exportação |
| dizer, na spec, que o GPS guarda e **não elimina** nada nesta fase | eliminação |

Por isso **a QI-4 deixa de bloquear a primeira spec.** Sem eliminação, o padrão é o da
Constituição, e a pergunta de destinação pode amadurecer em paralelo. **Continua bloqueando o uso
em produção** com dado real, porque *guardar indefinidamente* também é decisão.

## 7. Multiunidade sem reestruturação posterior

**Evidência [E].** As formas de multiunidade que aparecem nos Editais lidos são estas:

- Edital do Cefor com Perfis de cursos de **outro campus** e polos (89 e 90/2026, *"Campus
  ofertante: Campus de Alegre"*);
- Edital da Reitoria com cursos de vários campi (46/2026);
- Edital da Reitoria para servidores de várias unidades (04/2026, que nem usaria a capacidade).

**Fato [F].** Hoje, um ator tem um escopo por vez, e o escopo alheio responde 404
(`seguranca/application/authorization.py:117-146`). O Perfil não tem unidade ofertante
(`editais/models/perfis.py:26`).

**O que a primeira spec deve prever, sem construir o multicampi:**

1. **Cada ato registra a unidade em que foi praticado**, ao lado do ator: apresentação, conferência,
   desfecho e designação. É o que torna a trilha correta quando o conferente for de outra unidade
   que não a do Edital. Inferir a unidade depois, pelo Edital, daria a resposta errada exatamente
   nos casos que importam.
2. **A autorização da conferência passa por um predicado só**: *pode conferir esta convocação*.
   - Hoje: designado no Processo, no escopo do Edital.
   - Depois: designado no Processo **ou no Perfil**, com a unidade ofertante do Perfil.

   Muda a regra, não o dado.
3. **A designação admite restrição por Perfil desde o início.** É a mesma peça que, no 90/2026,
   designaria a coordenação do curso de Alegre só para os Perfis de Alegre.
4. **Nenhuma coluna, índice ou unicidade presume** que a unidade do conferente é a do Edital.

**O que fica para decisão própria, antes da spec do multicampi.** A designação de uma pessoa de
outra unidade num Processo exige mudar a doutrina *"escopo alheio = 404"* para *"escopo alheio = 404,
salvo designação"*. É decisão arquitetural com efeito sobre a `033` e a `109`, e é o que a auditoria
já chamava de MAT-09. **Não é desta spec**, mas a spec não pode fechá-la (itens 1 a 4).

---

## 8. Ajustes ao diagnóstico da auditoria

| Onde, na auditoria | Como estava | Como fica |
|---|---|---|
| Resumo, item 3 | "um ator de secretaria com competência por unidade" | "um responsável pela conferência, designado por Processo, com capacidade neutra" |
| Resumo, MVP; §F.1 | documentos **de matrícula** na convocação | **documentos e conferência na convocação**; a matrícula e o bolsista de vaga imediata como cenários |
| §B.4 | diagrama com "Exportação / SIGAA" como saída única | a saída é **encaminhamento ao setor de formalização**: SIGAA, coordenação do programa ou outro |
| §D.1, eixo finalidade | `MATRICULAR` | `FORMALIZAR O VÍNCULO` (matrícula, vinculação de bolsista e outros). Continua valendo que o **momento** precisa virar campo e a finalidade não, na primeira spec |
| §D.2, matriz | só documentos de aluno | acrescentam-se: **Ficha de Cadastramento/Termo de Compromisso** (modelo da agência, na convocação; 14, 89, 90, 140, 146); **certificado de formação** (inscrição ou convocação, com aproveitamento; 89, 11.1); **comprovação de idade na vinculação** (89 e 90, 2.2); **anuência da chefia** (na inscrição; 173, Anexo IX, e 14, Anexo VI) |
| MAT-03 | competência da secretaria | **competência por natureza do Edital, num mesmo Processo e numa mesma unidade**: a designação por Processo é necessária (§4) |
| MAT-04 | TTD acadêmica | a destinação depende da natureza; a classe dos documentos de bolsista não foi verificada [H]; **não bloqueia a primeira spec**, bloqueia o uso em produção (§6) |
| MAT-09 | multicampi como caso do 46 | **reforçado**: 89 e 90/2026 já têm Perfis de outro campus; a primeira spec deve registrar a unidade de atuação (§7) |
| §J | "dossiê documental" | **dossiê operacional da convocação**, distinto dos documentos a encaminhar (§6) |
| §L, secretaria | "fila da secretaria" | **fila de conferência**: a mesma tela para qualquer responsável designado |
| QI-1 | "quem confere e quem decide a matrícula?" | **QI-1′** (§4) |
| QI-2 | "em quais tipos de curso a documentação de matrícula pode passar para a convocação?" | **QI-2′ — em quais tipos de Edital** (cursos, bolsas, colaboradores) os documentos só necessários à formalização podem ser pedidos na convocação? |

**Achados novos:**

| ID | Descrição | Evidência | Sev. | Recomendação | Dep. |
|---|---|---|---|---|---|
| **MAT-18** | O desfecho *inércia* tem rótulo de matrícula e é oferecido a qualquer Edital | [F] `convocacao/models.py:250`; `portal/situacao.py:67`; `convocacao/domain/nomes.py:73-97` | Baixa | Registrar; decidir o rótulo neutro ou a restrição por Edital fora da primeira spec | A |
| **MAT-19** | Quem confere varia por natureza do Edital dentro da mesma unidade | [E] 77 (Anexo II); 14 (14.2); 140 (13.3); 146 (22.2) | **Alta** para o desenho | Designação por Processo (e Perfil), e não papel único na unidade (§4) | A + T |
| **MAT-20** | O GPS compõe Editais que mandam o candidato ao balcão para entregar documentos (72/2026, item 8) | [E] 72/2026 | Média | É o caso de uso imediato da primeira spec | — |

**Conclusões da auditoria que continuam válidas sem mudança:**

- não criar estados paralelos aos desfechos;
- o desfecho é a decisão única sobre a convocação;
- um catálogo de documentos e um armazenamento;
- aproveitamento por referência;
- nada automático (perda de vaga, nova chamada, eliminação);
- o GPS não é arquivo permanente;
- minimização como benefício principal;
- os riscos normativos (consentimento nulo, Lei 13.726, TTD);
- o pré-requisito da trilha do dossiê (A-07);
- a reavaliação da varredura de PDF (MAT-08).

---

## 9. Recomendação para a primeira spec

**Título:** *Documentos e conferência na convocação.*

**Problema:** o GPS só recebe documento na inscrição. Por isso, os Editais pedem a todos os inscritos
o que só os convocados precisam apresentar, ou mandam o convocado ao balcão (69, 72).

**Escopo:**

1. **Momento no Documento Exigido**, inscrição ou convocação, declarado na elaboração, publicado,
   classificado no contrato de mutabilidade (`026`), com seção própria e neutra no PDF.
2. **Lista exigida da convocação**, congelada na convocação.
3. **Apresentação no portal**, na tela da convocação, enquanto a chamada estiver em aberto:
   - versões append-only, com `PROTECT`;
   - o mesmo armazenamento, a mesma validação e o mesmo hash;
   - **aproveitamento por referência** de documento da inscrição;
   - modelo anexo para formulário a preencher e assinar.
4. **Conferência por documento**: conforme, pendente com motivo ou não se aplica com motivo. É
   append-only, com autor, **unidade de atuação** e instante.
5. **Complementação** do pendente até o vencimento da chamada, sem prazo novo.
6. **Guarda no desfecho existente**: aceite só com os obrigatórios conformes; indeferimento com
   fundamento pré-redigido a partir das pendências.
7. **Designação por Processo** (com restrição opcional por Perfil) de quem confere. A capacidade de
   conferir é distinta da de desfechar, e a autorização passa por um predicado só.
8. **Fila de conferência** por vencimento e estado, sem deferimento em lote.
9. **Trilha** da apresentação, da conferência, da consulta ao documento e da consulta ao dossiê
   (A-07).

**Cenários demonstráveis** (Constituição, VI):

- **(a)** Edital de alunos do Cefor com vagas imediatas e documentos na convocação, no molde do
  72/2026;
- **(b)** Edital de bolsista com vaga imediata e Ficha/Termo na convocação, no molde do 146/2025;
- **(c)** aproveitamento de documento da inscrição, no molde do certificado do 89/2026, num Edital
  de vagas imediatas.

**Fora:**

- recurso contra o desfecho;
- multicampi (designação de outra unidade);
- aviso de pendência por e-mail;
- encaminhamento e exportação do dossiê;
- retenção e destinação;
- Editais de bolsista de cadastro de reserva (dependem da spec da `097`);
- taxonomia de natureza do vínculo;
- formulário estruturado para outros vínculos;
- integração com SIGAA, CAPES ou Fapes.

**Decisões antes da spec:**

- **QI-1′** (quem confere e quem decide, por tipo de Edital);
- **QI-2′** (em quais tipos de Edital o documento vai para a convocação);
- **revisão da `FR-402`** da `029`: o catálogo continua um só e muda o momento; é governança de
  spec, não código.

**Decisões antes do uso em produção, mas não da spec:**

- QI-3 (quais documentos são exigíveis);
- QI-4 (guarda e destinação);
- MAT-08 (varredura de PDF).

**Porte: M**, como na auditoria. A generalização acrescenta a designação e um cenário de teste, e
não muda a ordem de grandeza.

---

## 10. Decisão de produto de 03/11/2026: a fronteira do GPS

*Registrada a pedido do usuário, depois de duas rodadas de avaliação sobre um "dossiê digital
institucional" e a consulta longitudinal pelo GPS. Esta seção **prevalece** sobre o que divergir
dela neste complemento e na auditoria. As decisões são do usuário; os ajustes são da avaliação que
ele aceitou.*

### 10.1 O que foi decidido

| # | Decisão | Classificação |
|---|---|---|
| 1 | **O GPS não é GED nem acervo permanente** de alunos, bolsistas ou outros vínculos | **DECIDIDO PELO USUÁRIO** |
| 2 | **A seleção confere os documentos e decide** sobre a convocação (deferimento, indeferimento e demais desfechos). A consulta por outro setor não lhe dá competência decisória | **DECIDIDO PELO USUÁRIO**; responde à parte "quem confere e quem decide" da QI-1′ |
| 3 | **O setor competente formaliza e custodia**: secretaria acadêmica, coordenação de bolsas ou outro. Ele recebe do GPS os documentos necessários à formalização e providencia a guarda no ambiente institucional apropriado | **DECIDIDO PELO USUÁRIO** |
| 4 | **O GPS conserva os registros e documentos do processo seletivo pelos prazos legalmente aplicáveis ao certame**, e não pelos do vínculo | **DECIDIDO PELO USUÁRIO** |
| 5 | Consulta longitudinal permanente e guarda prolongada no GPS **não serão desenvolvidas** | **DECIDIDO PELO USUÁRIO** |
| 6 | A meta é **evitar coleta excessiva, download desnecessário e circulação descontrolada**, e não eliminar todo download | **DECIDIDO PELO USUÁRIO** |
| 7 | Fora do escopo: GED, novo repositório documental e integração obrigatória com sistemas externos | **DECIDIDO PELO USUÁRIO** |

Três responsabilidades, cada uma com um dono:

```
Seleção (no GPS)       recebe na inscrição ou na convocação · confere · decide · registra o desfecho
GPS                    disponibiliza ao setor competente · registra a entrega · conserva o do certame
Setor competente       formaliza (matrícula, vinculação, contrato) · custodia no próprio acervo
```

### 10.2 O que deixa de valer

| Onde | Como estava | Agora |
|---|---|---|
| Auditoria, Resumo 5 e §J | o GPS como "ambiente operacional de custódia" até a destinação, e "dossiê documental" | o GPS conserva **só o que é do certame**, pelo prazo do certame. O dossiê do aluno ou do bolsista é do setor competente |
| Auditoria, §F.3 | integração com SIGAA, CAPES e SIPAC como integrações futuras | fora do escopo; a entrega ao setor é por exportação controlada (§10.4), e o setor escolhe o próprio acervo |
| Complemento, §4 (opção 3) e §9 (item 7) | designação por Processo de **quem confere** | **quem confere é a comissão do Processo**, que já tem designação, troca e impedimento ([F] `comissoes/models.py:31-45`). A designação por Processo, com Perfil opcional, passa para **quem recebe a entrega** (§10.4) |
| Complemento, §6 | encaminhamento como etapa futura sem spec | entrega controlada como **segunda spec provável e pequena** (§10.4) |
| Complemento, §9 (item 6) e Resumo | "aceite" como marca de quem segue para a formalização | **"apto para formalização"** (§10.3) |
| A avaliação da rodada 2, que não foi gravada em documento | spec 2 de consulta longitudinal; spec 3 condicional de guarda prolongada ou de encaminhamento a SIGAA/SIPAC | descartadas |

**Continua valendo:**

- completar a convocação, sem estados paralelos;
- o desfecho como decisão única;
- um catálogo de documentos e um armazenamento;
- aproveitamento por referência;
- nada automático;
- a unidade de atuação gravada em cada ato e a autorização por um predicado só (§7);
- os riscos normativos da auditoria;
- os pré-requisitos A-07 e MAT-08.

### 10.3 Aceite não é vínculo, e aceite ainda não é "encaminhado"

Três estados distintos, cada um com uma fonte só:

| Termo | Fonte | Quem afirma |
|---|---|---|
| **Apto para formalização** | desfecho vigente que **inclui** na ocupação: aceite ou regularização ([F] `DESFECHOS_QUE_INCLUEM`, `convocacao/domain/nomes.py`) | o GPS, pelo ato da seleção |
| **Encaminhado ao setor X em DD/MM, por Y** | **registro da entrega** (§10.4). Sem ele, o GPS não sabe se alguém recebeu | o GPS, pelo ato de quem entregou ou recebeu |
| **Matrícula efetivada, bolsa concedida, contrato celebrado** | o sistema ou setor do vínculo: SIGAA, CAPES/Fapes ou outro | **nunca o GPS** |

O código já respeita a terceira linha:

- [F] a `029` veda "matrícula efetivada" nas telas (`requerimentos/application/selectors.py:45-49`);
- [F] o portal diz que, depois do aceite, *"nenhum ato… confirma matrícula ou contratação"*
  (`portal/situacao.py:57-60`).

A primeira spec deve usar **"apto para formalização"** onde a auditoria dizia aceite como passagem.
**"Encaminhado"** só pode aparecer quando houver registro de entrega.

### 10.4 Entrega documental controlada: o que existe e o que falta

| Necessidade | Existe? | Evidência |
|---|---|---|
| Ver o documento no navegador, sem cache e com hash reconferido | **sim** | [F] `interface/views.py:5766-5838` |
| Baixar um documento por vez, com registro | **sim** | [F] evento `CONSULTAR_DOCUMENTO` (`interface/views.py:5810`) |
| Pacote por convocado ou por chamada | **não, e proibido** | [S] `FR-069` da `009`: *"NÃO DEVE existir download em lote, exportação, planilha nem painel"* (`specs/009-inscricao-simples-documentos/spec.md:598-600`); [F] o mesmo motivo em `interface/views.py:5773-5775` |
| O setor competente como quem recebe | **não**: quem lê é o Gestor, com `inscricao:consultar` na unidade inteira | [F] `interface/identidade.py:56-68`; `inscricoes/application/consulta.py:40-53` |
| Registro de "entregue a quem, quando" | **não** | — |
| Molde de exportação controlada | **sim**: a `031` tem prévia com o alcance, confirmação, papel próprio não concedido por padrão, registro append-only e **arquivo não guardado** | [F] `matriculas/models.py:1-17`; `matriculas/application/exportar.py:187-302`; `interface/identidade.py:113-127` |

**Conclusão.** Não é preciso infraestrutura nova (armazenamento, serviço, repositório), mas os
mecanismos atuais não bastam. Eles cobrem a consulta e o download individual, não a entrega. Para
uma chamada pequena, o download individual registrado basta. Para uma chamada de dezenas de pessoas
com vários documentos cada, a falta do pacote empurra a equipe de volta à pasta de rede.

**Lacuna registrada para uma segunda spec, que não está aberta.** *Entrega documental controlada*,
no molde da `031`:

- pacote com manifesto: requisito, hash, convocação, Edital e Perfil;
- população = aptos para formalização, com o alcance mostrado antes da confirmação;
- capacidade própria do setor que recebe, com designação por Processo e Perfil opcional;
- registro append-only da entrega, que é a fonte do termo "encaminhado";
- arquivo gerado e descartado, sem guarda no GPS.

**Pré-condição de governança:** revisar a `FR-069` da `009`, como a `FR-402` da `029`. A proibição
nasceu para a tela de inscrições recebidas, e a entrega ao setor competente seria exceção
deliberada, não descuido. **Momento:** depois de a Spec 1 provar o fluxo; o tamanho real das chamadas
dirá se ela é necessária.

### 10.5 Restrição por Processo, Perfil e unidade

| Quem | Na Spec 1 | Na entrega (2ª spec) | Limite conhecido |
|---|---|---|---|
| Seleção, que confere e decide | membros da comissão do Processo; o desfecho, pela base atual (`comissoes/domain/autorizacao.py:65-81`) | — | a comissão é por Processo, não por Perfil |
| Setor competente, que recebe | — | papel na unidade + designação por Processo, com Perfil opcional | Perfil sem unidade ofertante ([F] `editais/models/perfis.py:26`) |
| Setor de outra unidade (89 e 90/2026, Perfis do Campus de Alegre) | — | **não no piloto**: o Cefor exporta e encaminha pelo canal institucional que já usa | exige mudar *"escopo alheio = 404"*, decisão arquitetural própria (MAT-09, §7) |

**Pendência de minimização, sem escopo:** o Gestor continua lendo, com `inscricao:consultar`, o
dossiê de qualquer inscrito da unidade, sem prazo e depois do encerramento ([F]
`inscricoes/application/consulta.py:40-53`). Isso não é deste incremento. Mas, com a decisão 1, o
acesso amplo e indefinido deixa de ter justificativa de "acervo", e cabe decidir se ele continua.

### 10.6 Riscos que a decisão desloca, sem eliminar

- **A pasta de rede pode só mudar de dono.** Se o ambiente apropriado do setor for, na prática, a
  pasta compartilhada, o GPS terá feito a sua parte: a população cai de todos os inscritos para os
  aptos, e a entrega fica registrada. O risco continua no setor. É **dependência institucional**, e
  nenhuma spec do GPS deve ser lida como solução do acervo do setor.
- **"Não ser acervo" exige, um dia, descartar.** Conservar pelo prazo do certame significa:
  - para a inscrição de quem não se matriculou: *até a homologação + 1 ano*, e então eliminação com
    listagem aprovada ([N] TTD 456.112; Lei 8.159, art. 9º);
  - para o documento de renda das cotas: no mínimo 5 anos ([N] PN MEC 18/2012, art. 8º, §1º, IV);
  - para resultados e recursos: guarda permanente ([N] 456.115, 456.116).

  Sem um mecanismo de destinação, o GPS guarda tudo para sempre e **vira acervo por inércia**,
  contrariando a decisão 1. Não é escopo agora; é a pendência que a QI-4 passa a carregar.

### 10.7 Próximo passo

1. **Spec 1 — Documentos e conferência na convocação**, em sessão própria (uma spec por sessão),
   com:
   - os nove itens da §9, com o item 7 restrito à comissão;
   - o vocabulário da §10.3;
   - os três cenários: alunos tipo 72/2026, bolsista tipo 146/2025 e aproveitamento tipo 89/2026.
   - **Ainda antes dela:** a QI-2′ (em quais tipos de Edital o documento passa para a convocação) e
     a revisão da `FR-402`.
2. **Entrega documental controlada**: lacuna registrada (§10.4), não aberta; depende da revisão da
   `FR-069`.
3. **Destinação dos documentos do certame**: pendência institucional (QI-4), sem spec.
