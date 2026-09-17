# Modelo de dados — Requerimento de Matrícula (`029`)

**Fase 1** · 16/09/2026 · decisões em [spec.md](spec.md) §6 e §11; medições em
[research.md](research.md).

> **Duas tabelas novas, e a segunda não guarda dado pessoal.** Uma é o requerimento; a outra é a
> base de referência de CEP, que é infraestrutura de consulta e não tem dono.

---

## 1. `requerimentos.RequerimentoDeMatricula`

Aplicação Django nova: `processo_seletivo/requerimentos/`, com `domain`, `application`, `models.py` e
`migrations` — a divisão que todo módulo deste repositório já pratica.

### 1.1 Campos

| Campo | Tipo | Nulo | Notas |
|---|---|:--:|---|
| `id` | `UUIDField` pk | — | `default=uuid4`, como todo agregado |
| `inscricao` | FK → `inscricoes.Inscricao`, `PROTECT` | não | a Inscrição não desaparece sob o requerimento que a cita |
| `status` | `CharField(20)` | não | `RASCUNHO` \| `ENVIADO` (`§12`) |
| `disponibilizado_em` | `DateTimeField` | não | quando o gatilho abriu — nasce com a linha |
| `enviado_em` | `DateTimeField` | **sim** | nulo até o envio |
| `revision` | `PositiveBigIntegerField` | não | controle otimista, o mesmo padrão da `Inscricao` |
| `created_at` | `DateTimeField` | não | |
| **Sucessão** | | | |
| `requerimento_anterior` | FK → `self`, `PROTECT` | sim | `FR-408`; nulo é raiz |
| `convocacao_autorizadora` | FK → `convocacao.Convocacao`, `PROTECT` | sim | obrigatória no sucessor; preenchida também na raiz aberta por chamada |
| **Pessoa** | | | |
| `data_de_nascimento` | `DateField` | **sim** | obrigatória **para enviar**, não para existir — ver abaixo |
| `municipio_natal` | `CharField(120)` | não | |
| `uf_natal` | `CharField(2)` | não | |
| `nacionalidade` | `CharField(60)` | não | texto, não código — o código institucional é da exportação (`§24`) |
| `sexo` | `CharField(1)` | não | `F` \| `M`, o que o destino admite |
| `cor_raca` | `CharField(20)` | não | seis valores, com **indígena** (`FR-383`) |
| `estado_civil` | `CharField(20)` | não | lista fechada |
| `nome_da_mae` | `CharField(255)` | não | `""` é ausência declarada (`FR-384`) |
| `nome_do_pai` | `CharField(255)` | não | idem |
| **Documento** | | | |
| `rg` | `CharField(30)` | não | |
| `rg_orgao_emissor` | `CharField(30)` | não | |
| `rg_expedido_em` | `DateField` | **sim** | idem |
| **Contato** | | | |
| `telefone_celular` | `CharField(30)` | não | pré-preenchido da Inscrição (`FR-379`) |
| **Acolhimento** | | | |
| `necessidade_especifica` | `TextField` | não | `""` = nenhuma; distinto da cota PcD (`FR-385`) |
| **Renda** | | | |
| `renda_familiar_faixa` | `CharField(24)` | não | sete valores (`FR-412`); mede a **soma da família** |
| **Endereço** | | | |
| `cep` | `CharField(8)` | não | normalizado, só dígitos (`FR-387`) |
| `logradouro` | `CharField(255)` | não | |
| `numero` | `CharField(20)` | não | `""` admitido — "s/n" existe |
| `complemento` | `CharField(120)` | não | `""` = ausente |
| `bairro` | `CharField(120)` | não | |
| `municipio` | `CharField(120)` | não | |
| `uf` | `CharField(2)` | não | |
| `codigo_ibge` | `CharField(7)` | não | `""` quando o CEP não foi reconhecido (`FR-390`); nunca digitado (`FR-388`) |
| `endereco_conferido_por_referencia` | `BooleanField` | não | `True` quando o município/UF vieram da base |
| **Aceite** | | | |
| `versao_aceita` | FK → `publicacoes.VersaoConsolidada`, `PROTECT` | sim | nulo em rascunho |
| `declaracao_hash` | `CharField(64)` | não | `sha256` do texto **publicado**; `""` em rascunho |
| `declaracao_aceita_em` | `DateTimeField` | sim | |

**As duas datas são anuláveis, e obrigatório aqui significa obrigatório para *enviar*.** O rascunho
nasce vazio de propósito: são vinte campos, preenchidos em mais de uma sessão, e uma coluna `NOT
NULL` exigiria da linha recém-aberta o que a pessoa ainda não digitou. A obrigatoriedade mora em
dois lugares, e os dois são o envio — a `ck_requerimento_enviado_completo`, que as exige no estado
*enviado*, e `faltando_para_enviar()`, que nomeia em palavras o que ainda falta antes da tentativa
(`UX-054`). É a mesma repartição que a `Inscricao` já pratica entre rascunho e submissão.

Os campos de **texto** não precisam disso: `""` já distingue vazio de preenchido, e é o que a
restrição do envio confere.

**O resumo da declaração sai do conteúdo publicado, e não do texto recebido no `POST`.** Resumir o
que o cliente manda deixaria o resumo à escolha de quem monta a requisição — e a `SC-129`
reconstituiria a declaração que ele escolheu, não a que o Edital publicou. O texto recebido continua
sendo **conferido** contra o publicado, e a divergência recusa com `edital_updated`.

**Texto ausente é `""`, nunca `null`** — a convenção que `description`, `locality` e
`motivo_da_sucessao` já seguem neste repositório. Duas formas de dizer "não informado" na mesma linha
seria o defeito.

**Não há campo de latitude, longitude, foto, tipo sanguíneo, renda em valor, número de filhos,
profissão, condição de trabalhador, composição do domicílio nem telefone residencial.** A ausência é
requisito (`FR-382`, `FR-391`), e não esquecimento.

### 1.2 Restrições de banco

| Nome | O que garante | Forma |
|---|---|---|
| `uq_requerimento_raiz_por_inscricao` | uma raiz por Inscrição (`FR-376`) | `UniqueConstraint(fields=["inscricao"], condition=Q(requerimento_anterior__isnull=True))` |
| `uq_requerimento_sucessor_unico` | um sucessor por requerimento (`FR-376`) | `UniqueConstraint(fields=["requerimento_anterior"], condition=Q(requerimento_anterior__isnull=False))` |
| `ck_requerimento_sucessor_autorizado` | sucessor cita a convocação que o autorizou (`FR-408`) | `CheckConstraint(Q(requerimento_anterior__isnull=True) \| Q(convocacao_autorizadora__isnull=False))` |
| `ck_requerimento_enviado_completo` | *enviado* exige instante, versão, resumo e aceite (`FR-394`) | `CheckConstraint` no molde de `ck_inscricao_submetida_completa` |
| `ck_requerimento_status` | os dois estados e nada mais | `CheckConstraint(Q(status__in=[…]))` |

**As duas primeiras são parciais pela mesma cirurgia que a `019` documentou**: no PostgreSQL dois
`NULL` não colidem, e uma restrição total deixaria passar duas raízes da mesma Inscrição.

### 1.3 O gatilho de imutabilidade

```sql
CREATE TRIGGER requerimento_enviado_imutavel
BEFORE UPDATE OR DELETE ON requerimentos_requerimentodematricula
FOR EACH ROW WHEN (OLD.status = 'ENVIADO')
EXECUTE FUNCTION reject_sent_enrollment_request_mutation();
```

Cópia de forma da migration que congela a Retificação em estado final
([research.md](research.md), `T-005`). A função apenas levanta exceção — nunca retorna linha —, de
modo que a armadilha do `RETURN OLD` num `BEFORE UPDATE` não a alcança.

**A tabela não entra em `TABELAS_APPEND_ONLY`, e o total continua `31`.** A imutabilidade é
condicional ao estado, e privilégio de tabela não sabe ler estado — é literalmente a razão que a
política de privilégios escreve para excluir `Inscricao` e `Retificacao`.

### 1.4 Guarda na aplicação

`save()` e `delete()` recusam quando a linha persistida está em `ENVIADO`, no molde de
`Inscricao.save` e `DocumentoSubmetido._recusar_se_enviada`. **É a primeira camada, nunca a única**
(`FR-396`).

### 1.5 Estados

`RASCUNHO → ENVIADO` é a única transição sobre a mesma linha. O sucessor é **linha nova**, em
`RASCUNHO`, apontando a anterior. Os três estados restantes da `§12` da spec — *não aplicável*,
*ainda indisponível*, *disponível* — são derivados da ausência de linha vigente lida contra a
declaração do Edital, e **não são coluna**.

---

## 2. `requerimentos.ReferenciaDeCep`

| Campo | Tipo | Notas |
|---|---|---|
| `cep` | `CharField(8)` pk | só dígitos |
| `logradouro` | `CharField(255)` | `""` para CEP de localidade |
| `bairro` | `CharField(120)` | |
| `municipio` | `CharField(120)` | |
| `uf` | `CharField(2)` | |
| `codigo_ibge` | `CharField(7)` | o que a `FR-388` consome |

**Sem latitude e longitude** — a base as oferece e a `D-008` as recusa, agora com a razão externa
medida em `T-008`: a própria fonte adverte que a confiabilidade delas é variável.

**Não é dado pessoal**: é tabela de referência pública, sem vínculo com pessoa alguma. Carregada por
comando de manutenção, substituível por inteiro, e ausente sem consequência — a `FR-390` faz o
sistema funcionar com a tabela vazia.

**A porta do domínio** é `referencia_de_cep(cep) -> EnderecoDeReferencia | None`, e é ela que a
aplicação conhece. O domínio não sabe se atrás dela há tabela, arquivo ou serviço (`FR-389`).

---

## 3. Campos novos no conteúdo publicado do Edital

Na **raiz** do snapshot, um objeto:

```json
"matriculationRequest": {
  "moment": "AT_ENROLLMENT" | "AT_CALL",
  "declarationText": "Declaro, sob as penas da Lei, que as informações…"
}
```

**`null`, com a chave presente, significa que o Edital não exige requerimento** (`FR-368`) — a
grafia que `vacancyReversion` e `callForm` já usam no mesmo emissor. **A chave não se omite**; quem
omitir faz o mesmo fato ter duas formas conforme o Edital.

| Chave do contrato | Natureza proposta | Razão |
|---|---|---|
| `(RAIZ, "matriculationRequest/moment")` | **não retificável** | o momento define o que foi exigido de quem já se inscreveu; mudá-lo depois invalida inscrição submetida ou cobra dado de quem já cumpriu |
| `(RAIZ, "matriculationRequest/declarationText")` | **retificável** | é texto normativo como os demais, e o resumo criptográfico do aceite preserva o que cada pessoa leu |

No banco, dois campos em `processos.Edital`: `requerimento_momento` (`CharField`, `""` = não
declarado) e `requerimento_declaracao` (`TextField`, `""`). **Vazio, e não nulo** — a mesma grafia de
`especie_de_reversao` e `forma_de_convocacao`, que existem pela mesma razão.

---

## 4. O que **não** entra no modelo

| Recusado | Razão |
|---|---|
| Entidade `Endereco` | um endereço por requerimento, sem ciclo de vida próprio e sem reuso — junção e identidade sem regra que as consuma |
| `JSONField` de campos | o conjunto é institucional e estável nos cinco Editais lidos |
| Estado *em análise* / *deferido* / *indeferido* | já são desfechos da convocação (`§16`) |
| Histórico de versões do rascunho | rascunho é rascunho; o que vira peça de ato é o envio |
| Latitude, longitude, fonte e qualidade da geocodificação | `D-008`, confirmada por `T-008` |
| Tabela de conversão de faixa de renda | não há conversão possível (`R-7`) |
| Permissão nova | o candidato possui a Inscrição; quem conduz já tem a de consulta |
