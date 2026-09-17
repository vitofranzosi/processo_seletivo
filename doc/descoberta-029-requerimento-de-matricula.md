# Descoberta — Requerimento de Matrícula (`029`)

**Data**: 16/09/2026 · **Status**: investigação concluída, anterior à spec
**Evidências**: `ANEXO_II-REQUERIMENTO_DE_MATRICULA_Edital77.2026.pdf`,
`Import_LIBB_58_78-2026.xlsx` (com os **comentários de célula** do Registro Acadêmico), os Editais
reais 46, 57, 58, 69, 77 e 78 de 2026, e o código deste repositório em `5f37eec`.

> **A frase que governa a investigação:** *quais informações adicionais precisam ser obtidas de quem
> conquistou ou poderá ocupar uma vaga para transformar a candidatura em dados aptos à matrícula,
> sem pedir de novo o que o sistema já sabe?*

> **A separação que a investigação precisa preservar:** seleção e matrícula não são o mesmo momento
> administrativo. Um dado de matrícula **não vira** dado de seleção por hoje ser pedido na
> inscrição.

---

## 0. Proveniência das evidências, e o que não é reproduzido aqui

**Os artefatos não entram no repositório**, pela convenção que este projeto já pratica com a amostra
de Editais: eles ficam fora da árvore, e o que o repositório guarda é a leitura deles. O que faltava
era o endereçamento — sem ele a matriz não é reconferível. Ficam registrados o nome, o resumo
criptográfico e **onde**, dentro de cada artefato, cada afirmação foi lida.

| Artefato | `sha256` |
|---|---|
| `ANEXO_II-REQUERIMENTO_DE_MATRICULA_Edital77.2026.pdf` | `cabc2feb7acf5da58ee8fbd52e41ce20e1bd8bc7ce64031fb1fe0756edcafc6b` |
| `Import_LIBB_58_78-2026.xlsx` | `b4605d51273f39e26b81bf71684c7b50d0ad3f477d60ef2c2c3d1b024dc79027` |
| `EDITAL Nº 77_2026 … retificado em 26.08.2026.pdf` | `4e95a6fbbf6c77e6e84803a9f72a2b9e01235718f0a8ca33ea396b4b129f9a18` |
| `EDITAL UNIFICADO N-58-2026 … RETIFICADO EM 06-07-2026.pdf` | `099f32a6c2a91c41117108461e23d8bf68e9dbff19724f907db743ac8daa1c7f` |
| `Edital-69-2026-Chamada-Publica … Multimeios-Didaticos.pdf` | `04da0739d3cdb18d9200308ec521d70a2533c1bc504f4e1113e4030e568cd02f` |
| `edital-46-2026-cursos-tecnicos-integrados-retificado-em-20-08-2026.pdf` | `283b431e95654d8a6b611a399dc0df3d69b9b5ed05609dca070eaa8541258840` |

**Onde cada coisa foi lida.** Os campos do Requerimento saem da página 1 do Anexo II — folha única.
Os nomes de coluna da planilha saem da linha `1` da aba `Import_ModeloCefor`; **as instruções do
Registro Acadêmico citadas entre aspas são comentários de célula**, em `A1`, `C1`, `D1`, `F1`, `G1`,
`H1`, `I1`, `K1`, `L1`, `S1`, `T1`, `AE1` e `AH1`; a única linha de dados reais é a `2`. As cláusulas
dos Editais estão citadas com o item normativo em cada ocorrência (77/2026 5.4.g; 58/2026 5.4.h;
69/2026 item i; 46/2026 item 27 do cronograma e §2.1).

**A linha 2 da planilha é de uma pessoa real, e por isso ela não é reproduzida.** Nome, CPF, RG,
endereço, CEP, telefone, e-mail, título eleitoral e filiação daquela candidata **não** aparecem neste
documento nem na spec: o que aparece é a **forma** do dado e a divergência estrutural encontrada. Um
achado sobre qualidade de dado não precisa do dado para ser verdadeiro, e reproduzi-lo espalharia
dado pessoal por um repositório que não é o lugar dele — o que a Constituição veda em Princípio III e
o que esta própria feature existe para tratar com cuidado.

---

## 1. Entregável 1 — Diagnóstico do estado atual

### 1.1 O que o sistema sabe sobre a pessoa

| Onde | O que guarda | Muda? |
|---|---|---|
| `identidade.CandidateIdentity` | `subject`, `nome`, `cpf_normalizado` | nome sempre; **CPF congela** na primeira inscrição enviada (`cpf_congelado`) |
| `identidade.CandidateEmail` | e-mail canônico **com controle provado**, principal | acrescenta e troca a principal |
| `inscricoes.Inscricao` | `nome`, `cpf`, `email`, `telefone`, `profile_id`, `modality_id`, `protocolo` | rascunho muda; **enviada não muda mais** (`save` recusa) |
| `inscricoes.ValorDeFato` | fatos declarados do Perfil — **só `DATE` ou `INTEGER`** | append-only, congelado na submissão |
| `inscricoes.DocumentoSubmetido` | um arquivo por Documento Exigido, com hash | não muda depois de enviada |

**O que o sistema não sabe, e é preciso dizer sem rodeio:** não existe data de nascimento, sexo,
cor/raça, estado civil, filiação, naturalidade, nacionalidade, RG, órgão emissor nem **endereço**
— em lugar nenhum. A varredura por `cep|endereco|logradouro|IBGE` no backend inteiro só encontra
`endereço` no sentido de *URL*. Não há modelo de endereço para reaproveitar, nem município, nem
código IBGE.

**A identidade é fina de propósito.** Ela existe para autenticar e para possuir inscrições
(`identidade/models.py`: *"o candidato não é ator institucional, e é a Inscrição que ele possui"*).
Engordá-la com dados de matrícula contraria o desenho dela.

### 1.2 O que o sistema sabe sobre a oferta

`PerfilVaga` tem `code`, `name`, `description`, `locality`, `immediate_vacancies`, `reserve_type`,
`duties`, `workload`, `compensation`. `ModalidadeConcorrencia` tem `code` e `name`.

**Não existem curso, turno e polo como entidades, e não existe código institucional nenhum.** O
`seed_demo` guarda `"Polo Serra"` em `locality` e *"Curso técnico subsequente, na modalidade a
distância"* em `description` — texto livre. O Edital 46/2026 publica, no quadro de vagas,
*Curso · Turno · Código · Duração* (`Agropecuária · Integral · 1887 · 3 anos`), e o sistema não tem
onde pôr as três primeiras colunas.

### 1.3 O que o sistema sabe sobre o desfecho

A `019` está entregue, e é o achado mais importante do diagnóstico: **o ciclo de vida da matrícula
já existe em domínio**, do lado de fora desta feature.

- `Convocacao` — espécies `VAGA_INICIAL`, `SUPLENCIA`, `PARA_REGULARIZAR`; com proveniência de três
  atos, vencimento informado, e vigência derivada de *"ninguém me sucedeu"*.
- `DesfechoDaConvocacao` — sete espécies, e três delas são vocabulário de matrícula:
  `INDEFERIMENTO`, `REGULARIZACAO` e `INERCIA` (*"cancelamento de matrícula por inércia"*).
- `ComunicacaoEmitida` — o que o sistema **enviou**, nunca o que chegou.
- `portal/views.py::convocacao` — a tela do candidato, que já distingue *"não há convocação"* de
  *"você não foi chamado"*.

**Consequência direta:** *em análise*, *deferido*, *indeferido* e *regularizado* **não** são estados
a criar nesta feature. Eles já existem, com atores, fundamento e auditoria, como desfechos da
convocação. Criá-los de novo seria uma segunda fonte de verdade sobre a mesma vaga.

### 1.4 O que o sistema faz hoje com o Requerimento

Nada estruturado — e por uma razão que está escrita no Edital. No 77/2026, item 5.4:

> *"g) **Requerimento de Matrícula – Anexo II (devidamente preenchido)**, incluindo a marcação do
> termo de veracidade ao final do anexo (…). O preenchimento incompleto e/ou incorreto das
> informações solicitadas implicará no indeferimento do candidato, não cabendo recurso."*

Ou seja: **o Requerimento é hoje um `DocumentoExigido` como qualquer outro** — PDF baixado,
preenchido à mão, assinado, digitalizado e anexado, ao lado da identidade e do diploma. O sistema o
recebe como arquivo opaco, e o Registro Acadêmico o transcreve para a planilha à mão. É exatamente o
fluxo que esta feature existe para substituir.

### 1.5 Capacidades reutilizáveis, e a que **não** se deve reutilizar

| Reutilizar | Por quê |
|---|---|
| Titularidade da Inscrição (`exigir_titularidade`) | já é a fronteira de acesso do candidato, e é indistinguível de 404 |
| Padrão *rascunho → enviado, e enviado não muda* | `Inscricao.save` e `DocumentoSubmetido._recusar_se_enviada` |
| `versao_aceita` + `declaracoes_aceitas_em` | a Inscrição já registra aceite sob versão consolidada |
| `revision` + `compare_and_swap` | controle otimista do projeto |
| `AtoAdministrativo` / `RegistroAuditoria` | auditoria append-only já existente |
| A tela de conferência (`_conferencia`) | mostrar o que o sistema recebeu, sem redigitar |
| A convocação da `019` | é o gatilho, e ela já sabe chamar suplente |
| O contrato de mutabilidade (`026`) | todo campo novo do conteúdo publicado precisa de classificação |

| **Não** reutilizar | Por quê |
|---|---|
| `ValorDeFato` / `declaredFacts` | são os fatos que **a classificação** consome — tipos `DATE` e `INTEGER`, congelados na submissão, append-only. Data de nascimento caberia no tipo e não cabe no propósito: seria dado de matrícula entrando pela porta da seleção, que é a confusão que esta feature existe para desfazer |
| `DocumentoExigido` para os **dados** | é requisito de arquivo; transformar campo em documento é o retrocesso que estamos desfazendo |
| `SituacaoDivulgada` | é projeção de ato publicado, e não estado de pessoa |

### 1.6 Riscos de duplicação identificados

1. **Estados de análise** — já são os desfechos da `019` (§1.3).
2. **E-mail** — a identidade já tem credencial com controle provado; um campo de e-mail no
   requerimento criaria um segundo endereço sem prova.
3. **Telefone** — a `Inscricao` já tem um, **congelado na submissão**; e o Registro Acadêmico quer
   `CELULAR` no momento da matrícula, que pode ser meses depois.
4. **Cor/raça** — a modalidade PPI já é autodeclaração com comprovação; `COR` da planilha é censo.
   **Não são o mesmo dado**, e colapsá-los faria a cota decidir o censo ou o contrário.
5. **Necessidades especiais** — idem: a modalidade PcD é cota com comprovação e análise;
   `NECESSIDADES_ESPECIAIS` da planilha é informação de acolhimento pedagógico.

---

## 2. Entregável 2 — Matriz completa de dados

Legenda de origem: `IDENT` identidade · `INSC` inscrição · `REQ` requerimento · `EDITAL`
Processo/Edital · `OFERTA` perfil/vaga · `RESULT` resultado/classificação · `CONFIG` configuração
institucional · `DERIV` derivado · `—` inexistente.

### 2.1 Campos do Requerimento em papel

| Informação | Identidade | Inscrição | Requerimento (PDF) | Planilha RA | Origem recomendada | Usuário informa? | Observação |
|---|:--:|:--:|:--:|:--:|---|:--:|---|
| Nome | ✅ | ✅ | ✅ | `NOME` | `IDENT` | já informou | só visualiza |
| Filiação (mãe) | ❌ | ❌ | ✅ (junto) | `NOME_MAE` | `REQ` | **informa** | o PDF diz *"filho(a) de ___ e ___"*, sem dizer qual é qual |
| Filiação (pai) | ❌ | ❌ | ✅ (junto) | `NOME_PAI` | `REQ` | **informa** | ausência é legítima e precisa ser representável |
| Cor/raça | ❌ | ❌ | ✅ | `COR` | `REQ` | **informa** | censo, **não** é a modalidade PPI |
| Sexo | ❌ | ❌ | ✅ | `SEXO` (F/M) | `REQ` | **informa** | PDF é campo livre; planilha é lista de dois |
| Data de nascimento | ❌ | ❌ | ✅ | `DATA_NASCIMENTO` | `REQ` | **informa** | não existe em lugar nenhum hoje |
| Local de nascimento | ❌ | ❌ | ✅ (município + estado) | `CIDADE_NATAL` | `REQ` | **informa** | planilha só leva o município; a UF se perde |
| Endereço completo | ❌ | ❌ | ✅ (linha corrida) | 7 colunas | `REQ` estruturado | **informa/confirma** | CEP → município/UF/IBGE por enriquecimento |
| RG / órgão / expedição | ❌ | ❌ | ✅ | `RG`,`EMISSOR`,`IDENTIDADE_DATA` | `REQ` | **informa** | ver achado C-4 |
| CPF | ✅ | ✅ | ✅ | `CPF` | `IDENT` | já informou | planilha quer sem pontuação |
| Telefone celular | ❌ | ✅ (um) | ✅ | `CELULAR` | `REQ` (pré-preenchido da `INSC`) | **confirma** | o da inscrição congela na submissão |
| Telefone residencial | ❌ | ❌ | ✅ | ❌ | — | **não coletar** | sem destino e sem cláusula que o consuma |
| E-mail | ✅ (credencial) | ✅ | ✅ | `EMAIL` | `IDENT` | já provou | ver questão aberta Q-3 |
| Com quem reside / outros | ❌ | ❌ | ✅ | ❌ | — | **não coletar** | finalidade não demonstrada |
| Nº de pessoas que residem | ❌ | ❌ | ✅ | ❌ | — | **não coletar** | só teria uso junto da renda per capita, que Q-6 deixa em aberto |
| Nº de filhos | ❌ | ❌ | ✅ | ❌ | — | **não coletar** | finalidade não demonstrada |
| Estado civil | ❌ | ❌ | ✅ | `ESTADO_CIVIL` | `REQ` | **informa** | planilha exige a forma flexionada |
| Renda familiar (em SM) | ❌ | ❌ | ✅ | `RENDA_PER_CAPITA_PNP` | `REQ` — faixa do total | **informa** | destino significa per capita; divergência mantida e nomeada (C-1) |
| Aluno trabalhador | ❌ | ❌ | ✅ | ❌ | — | **não coletar** | finalidade não demonstrada |
| Profissão | ❌ | ❌ | ✅ | ❌ | — | **não coletar** | finalidade não demonstrada |
| Tipo sanguíneo | ❌ | ❌ | ✅ | ❌ | — | **não coletar** | dado de saúde, sem consumidor identificado |
| Necessidades educacionais especiais | ❌ | ❌ | ✅ | `NECESSIDADES_ESPECIAIS` | `REQ` | **informa** | acolhimento; **não** é a cota PcD |
| Curso em que requer matrícula | ❌ | ✅ (Perfil) | ✅ | `COD_CURSO` | `OFERTA`/`DERIV` | **não** | a pessoa se inscreveu para um Perfil |
| Declaração de veracidade | ❌ | ✅ (outra) | ✅ | ❌ | `REQ` | **aceita** | texto normativo do Edital |
| Data e assinatura | ❌ | ❌ | ✅ | ❌ | `DERIV` | **não** | data é o instante do envio |
| Foto | ❌ | ❌ | ✅ | ❌ | — | **questão aberta** | sem consumidor identificado |

### 2.2 Colunas da planilha do Registro Acadêmico

Os comentários entre aspas são **do próprio arquivo**, escritos pelo Registro Acadêmico.

| Campo de saída | Origem | Informado pelo candidato? | Já existe? | Observação |
|---|---|:--:|:--:|---|
| `INSC` | `INSC` — protocolo | não | ✅ `Inscricao.protocolo` | *"informação repassada pela seleção"*; formato divergente (`INS-AAAA-XXXXXXXX` × inteiro de seis dígitos) |
| `NOME` | `IDENT` | sim, originalmente | ✅ | não redigitar |
| `CLASSIF_CURSO_FINAL` | `RESULT` | não | ✅ `PosicaoNaOrdem` | *"numeração cardinal a partir de 1, em sequência"* — é a **ordem das linhas**, não a classificação |
| `COD_CURSO` | `CONFIG`/`OFERTA` | não | ❌ | *"cada curso tem seu número específico. Informação constante no Sistema Acadêmico"* — **lacuna** |
| `COD_TURNO` | `OFERTA` | não | ❌ | `V` no exemplo — **lacuna** |
| `COD_FORMA_INGRESSO` | `OFERTA` (modalidade) | não | ⚠️ parcial | *"conforme modalidade de vaga: AC, PPI, PCD; para pós-graduação PGAC, PGCD, PGPPI"* — exige correspondência |
| `CPF` | `IDENT` | sim, originalmente | ✅ | *"sem ponto e traço"* |
| `SEXO` | `REQ` | sim | ❌ | *"F ou M"* |
| `ESTADO_CIVIL` | `REQ` (+`DERIV`) | sim | ❌ | *"Solteiro…/Solteira…"* — a flexão é derivável de estado civil + sexo |
| `EMAIL` | `IDENT` | já provou | ✅ | |
| `DATA_NASCIMENTO` | `REQ` | sim | ❌ | *"dd/mm/aaaa"* |
| `COR` | `REQ` | sim | ❌ | *"Branca, Preta, Parda, Amarela, Não declarada"* — **falta Indígena** (achado C-2) |
| `NOME_MAE` | `REQ` | sim | ❌ | |
| `NOME_PAI` | `REQ` | sim | ❌ | ausência precisa ser representável |
| `CIDADE_NATAL` | `REQ` | sim | ❌ | a UF do PDF não tem coluna |
| `COD_NACIONALIDADE` | `REQ` + `CONFIG` | sim | ❌ | `BR` no exemplo; **o Requerimento não pergunta nacionalidade** — lacuna |
| `RG` | `REQ` | sim | ❌ | na única linha real da amostra, `RG` = o CPF (achado C-4) |
| `EMISSOR` | `REQ` | sim | ❌ | sigla do órgão, sem forma declarada |
| `IDENTIDADE_DATA` | `REQ` | sim | ❌ | `dd/mm/aaaa` |
| `TITULO_ELE` | **sem fonte** | ? | ❌ | *"xxxx xxxx xxxx"* — não está no Requerimento (achado L-1) |
| `ZONA_ELE` | **sem fonte** | ? | ❌ | idem |
| `SECAO_ELE` | **sem fonte** | ? | ❌ | idem |
| `CEP` | `REQ` | sim | ❌ | formato `NNNNN-NNN` |
| `ENDEREÇO` | `REQ` | sim | ❌ | logradouro |
| `NÚMERO` | `REQ` | sim | ❌ | |
| `COMPLEMENTO` | `REQ` | sim | ❌ | lote e quadra, na amostra |
| `BAIRRO` | `REQ` | sim/`DERIV` | ❌ | derivável do CEP, corrigível |
| `CIDADE` | `DERIV` do CEP | confirma | ❌ | |
| `ESTADO` | `DERIV` do CEP | confirma | ❌ | |
| `CELULAR` | `REQ` | sim | ⚠️ parcial | a `Inscricao` tem um telefone congelado |
| `RENDA_PER_CAPITA_PNP` | **contradição** | ? | ❌ | achado C-1 |
| `NECESSIDADES_ESPECIAIS` | `REQ` | sim | ❌ | `NENHUMA` no exemplo |
| `NOME_POLO` | `OFERTA` | não | ⚠️ `locality` é texto livre | `CEFOR` |
| `COD_POLO` | `CONFIG` | não | ❌ | *"cada polo tem um código"* — **lacuna** |

### 2.3 As três listas que a comparação produz

**Na planilha e não no Requerimento** — `INSC`, `CLASSIF_CURSO_FINAL`, `COD_CURSO`, `COD_TURNO`,
`COD_FORMA_INGRESSO`, `COD_NACIONALIDADE`, `TITULO_ELE`, `ZONA_ELE`, `SECAO_ELE`, `NOME_POLO`,
`COD_POLO`, `RENDA_PER_CAPITA_PNP`.

**No Requerimento e não na planilha** — telefone residencial, com quem reside, nº de pessoas que
residem, nº de filhos, renda familiar em salários mínimos, aluno trabalhador, profissão, tipo
sanguíneo, foto, UF de nascimento, assinatura.

**Já disponível na inscrição ou na identidade** — nome, CPF, e-mail, telefone (congelado), Perfil
(curso), modalidade, protocolo.

---

## 3. Entregável 3 — Achados

### Duplicidade

- **D-a** Nome, CPF e e-mail seriam redigitados; os três já existem, e o e-mail com controle
  **provado**.
- **D-b** Curso: o candidato se inscreveu para um Perfil. *"Venho requerer matrícula no curso ___"*
  é o Perfil da inscrição, e perguntar de novo permite divergir do que ele disputou.
- **D-c** Telefone: a inscrição já tem um. Reaproveitar como **pré-preenchimento** (não como fonte)
  é o desenho certo, porque o da inscrição congelou.
- **D-d** Declaração: a inscrição já registra aceite sob versão consolidada. O mecanismo existe; o
  que falta é a declaração **do requerimento**, que tem texto próprio.

### Lacuna

- **L-1** `TITULO_ELE`, `ZONA_ELE`, `SECAO_ELE` não têm fonte declarada. O Requerimento não os
  pergunta; o Edital 77 exige *comprovante de votação ou certidão de quitação eleitoral* (5.4.c), e
  a hipótese mais provável é que o Registro Acadêmico os **transcreva do documento**. Nenhuma
  evidência confirma. **Questão aberta.**
- **L-2** `COD_CURSO`, `COD_TURNO`, `COD_POLO` e `COD_NACIONALIDADE` são códigos do Sistema
  Acadêmico. O domínio não tem onde guardá-los.
- **L-3** Data de nascimento não existe no sistema — e é exigida pela planilha e por qualquer
  matrícula.
- **L-4** `NOME_POLO` existe como texto livre em `PerfilVaga.locality`, sem código.
- **L-5** `CLASSIF_CURSO_FINAL` é ambíguo: o comentário pede numeração sequencial das linhas, o nome
  diz classificação final no curso. São coisas diferentes quando a planilha traz duas modalidades.

### Contradição

- **C-1 — Renda, três conceitos.** O Requerimento pede *"renda familiar (soma dos rendimentos dos
  membros da família que residem na mesma casa), **em número de salários mínimos**"* — total do
  domicílio. A planilha pede `RENDA_PER_CAPITA_PNP` em faixas (`0,5<RFP<=1`) — **per capita**. E o
  comentário da coluna diz que *"a seleção encaminha no formato 'de R$ 2.431,00 até R$ 4.052,00 por
  pessoa'"* — per capita **em reais**. As três não se convertem entre si sem duas informações que
  ninguém declarou: o número de membros da família (que não é *"pessoas que residem com o
  estudante"*) e o salário mínimo do ano de referência. *(A aritmética fecha com SM = R$ 1.621,00:
  0,5 SM = R$ 810,50 e 2,5 SM = R$ 4.052,50 — os mesmos valores do comentário. Isso **explica** a
  conversão, e não a autoriza: nenhum artefato a declara como regra.)*
  Agrava: o Edital 58/2026 — de onde vem a planilha da amostra — **não menciona renda em lugar
  nenhum**, e a coluna veio preenchida.

  > **Confirmado e decidido em 16/09/2026.** O formulário em uso pergunta *"Renda Familiar"* nas
  > **sete faixas de salário mínimo** que são, na origem, as faixas per capita da Plataforma Nilo
  > Peçanha — e quem opera confirmou que o rótulo significa **a soma da família**, não o valor por
  > pessoa. Logo o processo atual escreve um total numa coluna que significa per capita, e a
  > distância não é pequena: uma família de quatro pessoas com 2 salários mínimos de renda total é
  > registrada três faixas acima do que deveria.
  >
  > A decisão de governança foi **manter a pergunta como está**: a feature coleta a faixa do total
  > (`FR-412`), e a divergência é registrada no contrato de saída em vez de corrigida aqui. Não há
  > conversão a inventar — dividir uma faixa por um número não produz uma faixa.
- **C-2 — Cor/raça sem Indígena.** A lista do Registro Acadêmico é *Branca, Preta, Parda, Amarela,
  Não declarada*. O IBGE tem cinco categorias, e a quinta é **Indígena** — a mesma que o Edital
  46/2026 usa ao reservar vagas para *"pretos, pardos ou indígenas (PPI)"*. Uma pessoa indígena não
  tem como ser registrada no destino.
- **C-3 — `INSC` de formatos diferentes.** O protocolo deste sistema tem a forma
  `INS-<ano>-<oito caracteres>`; a amostra traz um inteiro de seis dígitos, do sistema de inscrição
  anterior.
- **C-4 — `RG` preenchido com o CPF.** Na única linha real da planilha, `RG` e `CPF` são o mesmo
  número, dígito a dígito — conferido na célula `Q2` contra a `G2`. O valor **não** é reproduzido
  aqui (§0). É defeito do processo manual atual, e é o argumento mais curto a favor de coletar RG
  como campo estruturado.
- **C-5 — Sexo.** Campo livre no PDF, lista de dois no destino. Sexo e identidade de gênero não são
  o mesmo dado, e nome social não aparece em artefato nenhum.
- **C-6 — Necessidades especiais × PcD.** A planilha tem `NENHUMA` como valor; a cota PcD é ato com
  comprovação. Tratar como um só faria a ausência de necessidade contradizer a cota deferida.

### Derivável — nunca perguntar ao candidato

`INSC`, `CLASSIF_CURSO_FINAL`, `COD_CURSO`, `COD_TURNO`, `COD_FORMA_INGRESSO`, `NOME_POLO`,
`COD_POLO`, a data do requerimento, o curso requerido, a flexão de `ESTADO_CIVIL`, e — do CEP —
`CIDADE`, `ESTADO`, código IBGE e, se um dia existirem, latitude e longitude.

### Questionável — finalidade institucional não demonstrada

São **oito**, e a lista é exatamente a da `FR-382` da spec: foto, tipo sanguíneo, número de filhos,
profissão, condição de aluno trabalhador, com quem reside, número de pessoas do domicílio e telefone
residencial. Nenhum deles tem coluna na planilha nem cláusula em Edital que os consuma. **Não
preservar burocracia por ela existir.** *(A renda saiu desta lista em 16/09/2026: ela tem coluna, é
coletada em faixa, e o que continua em aberto é o que a coluna significa — ver C-1.)*

### Oportunidade — fora desta feature

Endereço estruturado com código IBGE abre análise territorial futura; o requerimento anterior da
mesma pessoa pode pré-preencher o próximo; o Requerimento estruturado torna possível **retirar** o
PDF assinado da lista de Documentos Exigidos — decisão institucional, não técnica (Q-2).

---

## 4. Entregável 4 — Decisões de domínio

| # | Conclusão | Classificação |
|---|---|---|
| 1 | A matrícula já tem vocabulário na `019` (indeferimento, regularização, inércia); esta feature não o recria | **DECIDIDO PELA EVIDÊNCIA** — está no código |
| 2 | O Requerimento é hoje um Documento Exigido em PDF (77/2026, 5.4.g) | **DECIDIDO PELA EVIDÊNCIA** |
| 3 | O momento da coleta varia entre Editais reais: 77 e 58 na inscrição; 69 *"no ato da matrícula presencial"*; 46 *"conforme cronograma do campus"*, após a homologação | **DECIDIDO PELA EVIDÊNCIA** |
| 4 | Não existe endereço, data de nascimento nem código institucional no sistema | **DECIDIDO PELA EVIDÊNCIA** |
| 5 | O gatilho é a **convocação vigente**, não a classificação | **RECOMENDAÇÃO** — a `019` já chama suplente, e a suplência passa a funcionar sem exceção |
| 6 | Dois momentos bastam (`NA_INSCRICAO`, `NA_CONVOCACAO`); o terceiro é representável pela chamada para vaga inicial | **RECOMENDAÇÃO** |
| 7 | O endereço mora no Requerimento, com **cópia para a frente** a partir do último requerimento enviado | **RECOMENDAÇÃO** |
| 8 | Persistir código IBGE; **não** persistir latitude/longitude nesta feature | **RECOMENDAÇÃO** |
| 9 | Base local de CEP, com degradação para digitação manual | **RECOMENDAÇÃO** |
| 10 | A retirada do Anexo assinado é **decisão de cada Edital** | **DECIDIDO PELO USUÁRIO** em 16/09/2026 |
| 11 | A renda é coletada em faixa de salário mínimo, medindo a **soma da família** — e o destino continua significando per capita | **DECIDIDO PELO USUÁRIO** em 16/09/2026; a divergência fica nomeada, não corrigida |
| 12 | Título/zona/seção eleitoral vêm do documento de quitação | **HIPÓTESE** |
| 13 | A declaração de que o Edital exige Requerimento é o que confina a feature a processos de alunos | **RECOMENDAÇÃO** — evita criar taxonomia de natureza do Processo |
| 14 | O e-mail exportado é o da credencial provada, e o requerimento não tem campo próprio | **DECIDIDO PELO USUÁRIO** em 16/09/2026 |
| 15 | Nome social e identidade de gênero **não** são coletados aqui; viram spec própria, com alcance nomeado | **DECIDIDO PELO USUÁRIO** em 16/09/2026 |

---

## 5. Entregável 5 — Proposta mínima de domínio

**Uma entidade, uma linha por Inscrição, dois estados persistidos.**

```
RequerimentoDeMatricula
  inscricao            1:1, PROTECT
  status               RASCUNHO | ENVIADO
  disponibilizado_em   quando o gatilho abriu
  enviado_em           nulo até o envio
  revision             controle otimista, como na Inscrição

  data_de_nascimento · sexo · cor_raca · estado_civil · nacionalidade
  municipio_natal · uf_natal
  nome_da_mae · nome_do_pai
  rg · rg_orgao_emissor · rg_expedido_em
  telefone_celular · telefone_residencial
  necessidades_especiais

  cep · logradouro · numero · complemento · bairro · municipio · uf · codigo_ibge
  endereco_origem      DECLARADO | REFERENCIA_CONFIRMADA

  versao_aceita        FK VersaoConsolidada
  declaracao_hash      o texto exato que foi exibido
  declaracao_aceita_em
```

**Por que uma tabela e não três.** O endereço não tem ciclo de vida próprio, não é lista e não é
compartilhado: uma tabela `Endereco` acrescentaria identidade e junção a um objeto que nunca é
endereçado sozinho. É a mesma recusa que a `019` escreveu sobre `Vaga` e a `013` sobre `Ocorrencia`
— entidade nasce quando a regra que a consome nasce.

**Por que nenhum JSON.** Os campos são institucionais e estáveis: o mesmo Requerimento serve o 58, o
77 e o 78, e o 46 pede os mesmos dados. Diferença pequena entre Editais não justifica form builder.

**Por que não é append-only.** Ela muda legitimamente enquanto é rascunho — exatamente como
`Inscricao` e `Retificacao`, que `TABELAS_APPEND_ONLY` exclui de propósito: *"a imutabilidade delas
é condicional ao estado final, o que só a trigger consegue expressar"*. A guarda de imutabilidade
depois do envio é a de `Inscricao.save`.

**Os cinco estados da Área do Candidato, e só dois são coluna.**

| Estado | Como é sabido |
|---|---|
| Não aplicável | o Edital não exige requerimento |
| Ainda indisponível | exige, mas o gatilho do momento declarado não ocorreu |
| Disponível | gatilho ocorreu e não há linha |
| Em preenchimento | linha em `RASCUNHO` |
| Enviado | linha em `ENVIADO` |

Os três primeiros são **derivados** — ausência de linha lida contra a configuração. É o mesmo
desenho que a `016` e a `019` usam para vigência: *"vigência não é coluna"*.

---

## 6. Entregável 6 — Fluxo ponta a ponta

**A — coleta antecipada (77, 58).** Edital declara `NA_INSCRICAO`. Ao abrir a inscrição, o cartão do
requerimento aparece como *Disponível*. O sistema já mostra nome, CPF, e-mail e o Perfil; pede o que
falta; o candidato confirma o telefone, informa nascimento, filiação, documento, endereço; aceita a
declaração; envia. A seleção segue sem tocar nos dados. A submissão da inscrição **não** depende do
requerimento salvo se o Edital o listar como exigência — e aí a recusa é anunciada antes da
tentativa, não depois.

**B — coleta após o resultado (46).** O Edital declara `NA_CONVOCACAO`. A pessoa se inscreve com o
mínimo, participa, é aprovada dentro das vagas e é **convocada para vaga inicial** pela `019`. A
convocação abre o requerimento. Ela complementa e envia dentro do prazo que a convocação informou.

**C — suplência (77, 6.10; 69, 9.2).** A pessoa fica suplente e não preenche nada. Alguém desiste, a
`016` apura a vaga faltante, a `019` a convoca com espécie *suplência* — e o requerimento abre pelo
mesmo caminho da B, sem exceção nenhuma no código.

**D — não selecionado.** Nenhuma linha é criada, nenhum dado de matrícula é coletado. É o desenho da
minimização: quem não chega à vaga não entrega dado de vínculo.

**E — endereço conhecido.** Havendo requerimento enviado anterior da mesma identidade, o rascunho
nasce preenchido com aquele endereço, marcado como *"conferido da sua última matrícula"*. Editar
altera **este** requerimento, e nunca o anterior.

**F — CEP reconhecido.** Digitado o CEP, o sistema traz logradouro, bairro, município, UF e código
IBGE; município e UF ficam somente leitura enquanto o CEP for reconhecido; logradouro, número,
complemento e bairro seguem editáveis.

**G — serviço indisponível.** O campo diz que não foi possível consultar, e **todos** os campos de
endereço ficam editáveis, incluindo município e UF. O código IBGE fica vazio, e o requerimento é
enviável assim. Nada bloqueia.

---

## 7. As três perguntas finais

### O Requerimento deve ser feature própria?

**Sim — por responsabilidade de domínio, e não por conveniência.** Três razões, nesta ordem:

1. **O ato é outro.** A Inscrição é o ato pelo qual alguém **disputa** uma vaga, e o projeto a
   congelou na submissão justamente por isso. O Requerimento é o ato pelo qual alguém **habilita o
   vínculo** que a disputa lhe deu — praticado por uma pessoa em outra situação jurídica, às vezes
   meses depois, às vezes por quem foi convocado por suplência.
2. **Estender a Inscrição é impossível nos cenários B e C.** Inscrição enviada não muda — `save`
   recusa, e a `009` não tem retificação. Um campo de matrícula nela seria inalcançável exatamente
   quando ele deveria ser preenchido.
3. **A fronteira semântica é o produto da feature.** Guardar dado de matrícula dentro da Inscrição
   diria, na estrutura, que ele é dado de seleção — que é a confusão que esta feature existe para
   desfazer.

### Fronteira com a ocupação de vagas / convocação

A `019` responde *quem pode ocupar a vaga, e até quando*. A `029` responde *quais dados dessa pessoa
o vínculo exige*. A dependência é **de leitura, num sentido só**: o requerimento **lê** a convocação
vigente para saber se abriu. Ele não cria convocação, não registra desfecho, não defere, não
indefere e não cancela matrícula — tudo isso já é da `019`, com ator, fundamento e auditoria
próprios. E o requerimento **não é** condição de nada na `016`: uma vaga continua ocupada ou não
pelos desfechos da `019`, tenha o requerimento sido enviado ou não.

### Fronteira com a exportação para o Registro Acadêmico

A `029` garante que **cada dado tem origem única, estruturada e identificada**. A exportação é
**composição**: `identidade + inscrição + requerimento + resultado + oferta + configuração`. Ela
precisa de três coisas que esta feature declaradamente **não** entrega — os códigos institucionais
(L-2), a regra de faixa de renda (C-1) e a correspondência de modalidade → forma de ingresso. O
contrato de saída fica escrito aqui; a planilha nasce em feature própria.
