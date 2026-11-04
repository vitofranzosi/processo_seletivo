# Data Model: Entrega documental controlada

São quatro tabelas novas no app `formalizacao`. Todas são append-only em três camadas: `save` e
`delete` recusam, um gatilho recusa e o privilégio está ausente (`TABELAS_APPEND_ONLY`). Nenhuma
guarda arquivo.

**O Documento Exigido não muda.** A finalidade fica fora do conteúdo publicado (D-009).

## DefinicaoDosDocumentosDaFormalizacao

Uma linha por versão. A vigente do Edital é a mais recente.

| Campo | Tipo | Nota |
|---|---|---|
| `id` | UUID | gravado em cada exportação |
| `edital` | FK `Edital`, `PROTECT` | |
| `requisitos` | `ArrayField(UUID)` | ids de Documento Exigido do Edital, de qualquer momento; pode ser vazia |
| `motivo` | texto, obrigatório | `CheckConstraint`: não vazio (FR-3655) |
| `definido_por` | `CharField(255)` | |
| `unidade_de_atuacao` | `CharField(100)` | |
| `definido_em` | datetime | |

- Os requisitos são conferidos na gravação contra **todas** as versões publicadas do Edital: um
  requisito que só existia numa versão anterior continua válido para as chamadas gravadas sob ela.
- **Sem definição, o conjunto é vazio** (FR-3660).
- **Histórico** (FR-3711): as linhas do Edital por `definido_em`. A diferença entre versões é calculada
  na leitura, sem coluna.

**Por que array de UUID, e não FK.** O requisito é identificado por UUID estável entre versões, como
na `ItemDaListaDaConvocacao.requisito_id` da `115`. As linhas relacionais do rascunho são recriadas a
cada gravação, e uma FK se perderia.

## DesignacaoParaFormalizacao

| Campo | Tipo | Nota |
|---|---|---|
| `id` | UUID | |
| `edital` | FK `Edital`, `PROTECT` | |
| `pessoa` | `CharField(255)` | `identity_subject` |
| `perfis` | `ArrayField(UUID)`; vazio = todos | conferidos contra os Perfis do Edital |
| `motivo` | texto, obrigatório | |
| `designado_por` | `CharField(255)` | MUST ser diferente de `pessoa` (constraint) |
| `unidade_de_atuacao` | `CharField(100)` | |
| `designado_em` | datetime | |

Há no máximo **uma designação vigente por (edital, pessoa)**. A regra é garantida na aplicação, com
`select_for_update` na pessoa, como a concessão da `107`, e por teste de concorrência.

## RevogacaoDaDesignacao

| Campo | Tipo | Nota |
|---|---|---|
| `id` | UUID | |
| `designacao` | `OneToOne`, `PROTECT` | uma por designação |
| `motivo` | texto, obrigatório | |
| `revogado_por`, `unidade_de_atuacao`, `revogado_em` | | |

**Vigente**: designação sem revogação. O papel vigente e a pessoa não suspensa são conferidos **no
predicado**, a cada requisição, e não gravados. É assim que revogar o papel corta todas as designações
(FR-3667).

## ExportacaoDeFormalizacao

| Campo | Tipo | Nota |
|---|---|---|
| `id` | UUID | vai no manifesto |
| `edital` | FK `Edital`, `PROTECT` | |
| `designacao` | FK, `PROTECT` | a que autorizou |
| `definicao` | FK `DefinicaoDos…`, `PROTECT` | a versão aplicada (FR-3655) |
| `alcance` | `PESSOA` \| `SELECAO` \| `RECORTE` | |
| `perfil_id` | UUID, nulo | o recorte por Perfil |
| `resultado` | `COMPLETO` \| `PARCIAL` | FR-3697. Só existe registro para pacote gerado |
| `pessoas` | JSON | `[{inscricao, convocacao, situacao: INCLUIDA \| NAO_INCLUIDA, motivo?: INDISPONIVEL \| INTEGRIDADE}]`, como a verificação as mostrou |
| `documentos` | JSON | `[{inscricao, origem: "apresentacao" \| "documento", id, sha256}]`, só dos incluídos |
| `quantidade_de_arquivos` | int | |
| `tamanho` | bigint | bytes do pacote |
| `hash_do_pacote` | char(64), não vazio | |
| `exportado_por`, `unidade_de_atuacao`, `exportado_em` | | |

Constraints:

- `hash_do_pacote <> ''` e `quantidade_de_arquivos > 0`;
- `resultado = 'COMPLETO' ⇔` nenhuma pessoa com `NAO_INCLUIDA`, conferido na aplicação, porque é JSON;
- `alcance = 'PESSOA' ⇒ perfil_id IS NULL AND resultado = 'COMPLETO'`. A pessoa única com falha não gera
  pacote (FR-3685).

**Quando é gravado** (FR-3698): na transação da montagem, depois do pacote pronto e antes da resposta.
Verificação, verificação defasada, recusa e interrupção **não** gravam registro: vão para a trilha.

**Sem dado pessoal**: nenhum nome, CPF, nome de arquivo ou motivo de conferência (FR-3700).

**Por que JSON, e não tabelas filhas.** O registro é lido para o histórico, a auditoria e a coluna
*"última exportação"*. A `031` usa o mesmo desenho (`GeracaoDeArquivo.requerimentos`). Tabelas filhas
seriam mais duas append-only sem consulta que as exija.

## O que é derivado, e não gravado

- **Apto**: desfecho vigente da chamada mais recente (FR-3669).
- **Situação do item**: *incluído*, *não se aplica*, *não apresentado*, *não conferido*,
  *indisponível*, *integridade* (FR-3672). As duas últimas só se conhecem lendo o arquivo.
- **Última exportação** da pessoa: a `ExportacaoDeFormalizacao` mais recente do Edital que a inclui.

Não há outra situação por pessoa (FR-3701).

## Papel no catálogo (existente)

`PAPEIS["formalizacao"] = {"formalizacao:acessar"}` e `DESCRICOES["formalizacao"]`, em
`interface/identidade.py`. O modelo de vínculo da `107` não muda.

## Eventos na trilha (`RegistroAuditoria`)

| `operation` | Rótulo | `aggregate` | `reason` |
|---|---|---|---|
| `FORMALIZACAO_DEFINIR` | Definição dos documentos gravada | Edital | id da versão |
| `FORMALIZACAO_DESIGNAR` / `FORMALIZACAO_REVOGAR` | Designação concedida / revogada | Edital (e unidade) | id da designação |
| `FORMALIZACAO_VISUALIZAR` | Documento visualizado | Apresentação ou Documento | `requisito ‹id›` |
| `FORMALIZACAO_DOWNLOAD` | Download individual disponibilizado | idem | `requisito ‹id›` |
| `FORMALIZACAO_VERIFICAR` | Verificação de exportação | Edital | alcance, resultado e contagens |
| `FORMALIZACAO_EXPORTAR` | Pacote gerado e disponibilizado para download | Edital | id da exportação e resultado |
| `FORMALIZACAO_RECUSAR` | Exportação recusada | Edital | `verificacao_defasada`, `limite` ou `pessoa_incompleta` |
| `FORMALIZACAO_INTERROMPER` | Exportação interrompida | Edital | a classe do erro, sem mensagem |
| `ARQUIVO_INDISPONIVEL` | Arquivo indisponível | Apresentação ou Documento | `requisito ‹id›` |
| `INTEGRIDADE` | (existente) | idem | `requisito ‹id›` |

Os eventos de falha e de interrupção são gravados **em transação própria**, para sobreviver ao rollback
da operação.

Não há *obtido*, *encaminhado*, *recebido* nem *entregue*.

## Trava consultiva (não é tabela)

`pg_try_advisory_xact_lock(CLASSE_DA_FORMALIZACAO, resumo_int4(identity_subject))`:

- é tomada no início da transação da verificação ou da montagem;
- é liberada no commit, no rollback ou no fechamento da conexão;
- não cobre a transferência (FR-3692).
