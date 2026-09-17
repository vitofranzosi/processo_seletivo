# Runbook — a base de referência de CEP

Quem opera o sistema lê este arquivo. Ele responde: **o que instalar uma vez, o que rodar todo mês,
o que o deploy confere, e o que fazer quando alerta.**

A decisão de operação é de 17/09/2026: **carga inicial no provisionamento, atualização por job
agendado.** Nem recarregar a cada deploy, nem depender de alguém lembrar.

## O que esta base é, e o que acontece sem ela

O Requerimento de Matrícula preenche município e UF a partir do CEP, e deriva o código IBGE do
município — que é o campo que o Registro Acadêmico consome e que ninguém digita.

**Ela é auxiliar, e a ausência dela não bloqueia nada** (`FR-390`). Sem base carregada, a pessoa
digita o endereço inteiro à mão, o código IBGE fica vazio, e o envio conclui. Inscrição, convocação
e matrícula seguem. É por isso que **nenhuma verificação daqui derruba o readiness**: transformar um
serviço de referência em porta de entrada do processo é exatamente o que a decisão de carregar
localmente existe para evitar.

O que se perde sem ela é conveniência e qualidade de dado — não o processo.

## O artefato

| | |
|---|---|
| Fonte | `gpfconfea/banco-ceps` (MIT), sobre Correios + IBGE |
| Forma | **um arquivo JSON por CEP**, dentro de um `.zip` |
| Volume | 1.209.314 arquivos · 379 MB comprimidos · 278 MB descomprimidos |
| Carga | ~40 s, lendo o `.zip` em fluxo |

**O `.zip` mora em storage controlado da instituição — não no Git, e não na imagem Docker.** Ele é
grande, muda sozinho, e não é código. O que o repositório guarda é o `sha256` do instantâneo em uso,
registrado na própria linha da carga.

**O comando lê o `.zip` direto.** Descompactar produziria 1,2 milhão de inodes para serem lidos uma
vez — mais caro que a carga inteira, e em alguns volumes suficiente para esgotar o limite de
arquivos.

## 1. Primeira instalação

Depois das migrations, e **uma vez**:

```bash
make DB_NAME=<banco> CEPS_ZIP=/caminho/para/banco-ceps.zip ceps
```

**Confira o `sha256` do arquivo antes**, contra o que o storage publica. O comando registra o resumo
que carregou, e é por ele que se responde depois *"esta base é de qual instantâneo?"*.

**Não está no `make preparar` de propósito.** Aquele alvo roda em toda máquina de desenvolvimento e
em cada banco de teste; 379 MB de CEPs não têm lugar ali.

## 2. Atualização mensal

Job **externo**, fora do processo web, uma vez por mês:

```bash
make DB_NAME=<banco> CEPS_ZIP=/caminho/para/banco-ceps.zip ceps
```

O que ele faz, nesta ordem:

1. Confere o `sha256`. Igual ao vigente com `--se-mudou`, **não faz nada** e sai com 0.
2. Toma uma trava consultiva do PostgreSQL. Já havendo carga em andamento, **recusa** — não espera.
3. Escreve uma **geração nova**, invisível para quem consulta.
4. Numa transação, a vigência muda de dono.
5. Recolhe a geração anterior.

**A ativação é atômica, e é isso que torna o job seguro.** Interrupção no meio não ativa nada: a
geração anterior continua inteira e respondendo. E a geração nova só tem o que a fonte mandou — de
modo que um CEP que os Correios desativaram some, em vez de ficar respondendo para sempre.

**Fora do processo web**, porque a carga é longa e escreve 1,2 milhão de linhas. Rodá-la dentro de um
`worker` que atende requisição disputa conexão com quem está preenchendo formulário.

**A trava é consultiva, e não uma coluna.** Ela é liberada quando a conexão cai — um job morto não
deixa a trava pendurada, que é o defeito de quem a implementa com um campo `em_andamento`.

## 3. Deploy comum

**Confere e informa. Não baixa, não reimporta, não bloqueia.**

```bash
make DB_NAME=<banco> ceps-situacao
```

Sai com `0` quando está tudo bem, e com `1` quando alguém precisa olhar. A saída legível vai para
`stdout`; os alertas, para `stderr`. Com `--json`, a mesma informação para coletor de métrica.

**Sair com 1 não deve derrubar o deploy.** Ele é sinal para o canal de alerta, não portão.

## 4. Alertas, e o que fazer com cada um

| Alerta | O que aconteceu | O que fazer |
|---|---|---|
| *não há base de CEP carregada* | instalação nova, ou banco recriado | rodar a carga inicial (§1) |
| *a base tem N dias* | o job mensal parou | conferir o agendador; rodar à mão para recuperar |
| *a última tentativa de carga falhou* | rede, disco, ou arquivo corrompido | ler a falha registrada; rodar de novo |

A idade que dispara o alerta é **60 dias**, e não 30: o job é mensal, e alertar em 30 faria toda
execução atrasada por um dia virar incidente. O dobro do intervalo distingue *"atrasou"* de
*"parou"*.

**A idade é medida da conclusão, e não do início.** Carga que começou e não terminou não é base
nova; é base que não existe.

## 5. Recuperação manual

Execução à mão é **só para recuperação** — nunca rotina.

```bash
# O que está carregado agora
make DB_NAME=<banco> ceps-situacao

# Recarregar, ignorando o resumo igual
make DB_NAME=<banco> CEPS_ZIP=/caminho/banco-ceps.zip ceps
```

Havendo dúvida sobre a integridade da base vigente, recarregar é seguro: a geração nova é construída
ao lado, e a vigente só é substituída quando a nova está completa.

## 6. O que este runbook **não** promete

Sincronização incremental com os Correios, consulta a serviço de terceiro em tempo de requisição, e
qualquer coordenada geográfica — latitude e longitude vêm no arquivo da fonte e são **descartadas na
leitura** (`D-008`): a própria fonte adverte que a confiabilidade delas é variável, e a coordenada de
um CEP não é a casa de ninguém.
