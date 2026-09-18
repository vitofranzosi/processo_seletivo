# Contrato de saída — as 34 colunas do formato do Registro Acadêmico

**Isto não é implementado por esta feature** (`FR-404`). É o **mapa** que a `FR-403` manda manter e o
artefato que a `SC-133` verifica: para cada coluna do formato de destino, de onde o valor sairia — ou,
quando não há de onde, a questão aberta que precisa ser respondida antes de alguém tentar.

**Onde não há regra, o mapa diz que não há.** Nenhuma conversão é inventada aqui. Uma tabela de
correspondência escrita de memória — códigos de curso, de turno, de nacionalidade — produziria dado
errado com aparência de dado certo, e o erro só apareceria no Registro Acadêmico, depois da
matrícula, com a pessoa no meio.

**A fonte é a linha `1` da aba `Import_ModeloCefor` da planilha `Import_LIBB_58_78-2026.xlsx`**, cujo
resumo criptográfico está registrado na §0 de
[doc/descoberta-029-requerimento-de-matricula.md](../../doc/descoberta-029-requerimento-de-matricula.md).
A planilha não entra no repositório, e a linha `2` — de uma pessoa real — não é reproduzida em lugar
nenhum: a varredura `backend/tests/test_sem_dado_pessoal_da_amostra.py` guarda essa promessa.

## As 34 colunas, na ordem da planilha

| # | Coluna | Origem | De onde sai | Ressalva |
|---|---|---|---|---|
| 1 | `INSC` | inscrição | `Inscricao.protocolo` | formato divergente do que o destino espera |
| 2 | `NOME` | identidade | `CandidateIdentity.nome` | — |
| 3 | `CLASSIF_CURSO_FINAL` | classificação | posição na ordem vigente | o destino pede numeração sequencial das linhas, não a classificação |
| 4 | `COD_CURSO` | — | **sem fonte** | `D-001` da [`031`](../031-exportacao-de-matriculas/spec.md): vocabulário do sistema acadêmico, e a célula sai vazia |
| 5 | `COD_TURNO` | — | **sem fonte** | `D-001` da [`031`](../031-exportacao-de-matriculas/spec.md): turno não é dado que o Edital declare, e a célula sai vazia |
| 6 | `COD_FORMA_INGRESSO` | oferta | `ModalidadeConcorrencia.code` | correspondência inexistente entre os dois vocabulários |
| 7 | `CPF` | identidade | `cpf_normalizado`, sem pontuação | — |
| 8 | `SEXO` | requerimento | `sexo` | — |
| 9 | `ESTADO_CIVIL` | requerimento | `estado_civil` | a flexão que o destino exige é **derivada** de `sexo` |
| 10 | `EMAIL` | identidade | credencial principal (`FR-378`) | — |
| 11 | `DATA_NASCIMENTO` | requerimento | `data_de_nascimento` | — |
| 12 | `COR` | requerimento | `cor_raca` | **o destino não comporta *indígena*** (`R-4`) |
| 13 | `NOME_MAE` | requerimento | `nome_da_mae` | vazio é ausência declarada, e não falta (`FR-384`) |
| 14 | `NOME_PAI` | requerimento | `nome_do_pai` | idem |
| 15 | `CIDADE_NATAL` | requerimento | `municipio_natal` | a **UF de nascimento não tem coluna** no destino |
| 16 | `COD_NACIONALIDADE` | requerimento | `nacionalidade` | correspondência inexistente: o sistema guarda texto, o destino pede código |
| 17 | `RG` | requerimento | `rg` | — |
| 18 | `EMISSOR` | requerimento | `rg_orgao_emissor` | — |
| 19 | `IDENTIDADE_DATA` | requerimento | `rg_expedido_em` | — |
| 20 | `TITULO_ELE` | — | **sem fonte** | `Q-4`: título eleitoral não é coletado |
| 21 | `ZONA_ELE` | — | **sem fonte** | `Q-4` |
| 22 | `SECAO_ELE` | — | **sem fonte** | `Q-4` |
| 23 | `CEP` | requerimento | `cep`, normalizado (`FR-387`) | — |
| 24 | `ENDEREÇO` | requerimento | `logradouro` | — |
| 25 | `NÚMERO` | requerimento | `numero` | `""` admitido — *"s/n"* existe |
| 26 | `COMPLEMENTO` | requerimento | `complemento` | `""` é ausência, e nem todo endereço tem |
| 27 | `BAIRRO` | requerimento | `bairro` | — |
| 28 | `CIDADE` | requerimento | `municipio` | — |
| 29 | `ESTADO` | requerimento | `uf` | — |
| 30 | `CELULAR` | requerimento | `telefone_celular` | — |
| 31 | `RENDA_PER_CAPITA_PNP` | requerimento | `renda_familiar_faixa` | **a faixa mede a soma da família; a coluna significa per capita** (`R-7`) |
| 32 | `NECESSIDADES_ESPECIAIS` | requerimento | `necessidade_especifica` | distinto da cota PcD (`FR-385`) |
| 33 | `NOME_POLO` | oferta | `PerfilVaga.locality` | texto livre dos dois lados |
| 34 | `COD_POLO` | — | **sem fonte** | `D-001` da [`031`](../031-exportacao-de-matriculas/spec.md): vocabulário do sistema acadêmico, e a célula sai vazia |

## A conta

| Origem | Colunas |
|---|---|
| requerimento | 21 |
| identidade | 3 |
| oferta | 2 |
| inscrição | 1 |
| classificação | 1 |
| **sem fonte** | 6 |
| **total** | **34** |

**Seis colunas sem fonte, e nenhuma delas é descuido.** Código de curso, de turno e de polo são
vocabulário do sistema acadêmico, que este sistema não conhece; título, zona e seção eleitorais são
dado que o Requerimento **decidiu não coletar** — nenhum Edital da amostra os exige para inscrição, e
coletar sem propósito institucional demonstrado é o que a `FR-382` proíbe.

**Uma divergência de significado, e ela é conhecida** (`R-7`). `RENDA_PER_CAPITA_PNP` recebe uma
faixa que mede a **soma da família**. A decisão de 16/09/2026 foi coletar como o formulário
institucional já coleta, e nomear a divergência aqui em vez de inventar uma conversão — dividir uma
faixa por um número não produz uma faixa, e o número de pessoas do domicílio não é coletado.

## O caminho inverso: o que se coleta e o destino não pede

| Campo | Por que existe mesmo sem coluna |
|---|---|
| `codigo_ibge` | identifica o município sem ambiguidade de grafia; é o que torna o endereço conferível (`FR-388`) |
| `uf_natal` | o destino tem `CIDADE_NATAL` e não a UF; sem ela, *"Vitória"* é ambíguo entre dois estados |
| `endereco_conferido_por_referencia` | diz se o endereço foi confirmado contra a base ou apenas digitado |

**Coletar o que o destino não pede não contradiz a `FR-382`.** O propósito institucional dos três é
interno e demonstrado: desambiguar município e saber a procedência do endereço. O que a regra proíbe
é coletar sem propósito — e não coletar sem coluna de destino.
