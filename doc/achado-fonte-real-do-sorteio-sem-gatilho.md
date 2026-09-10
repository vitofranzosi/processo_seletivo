# Achado — o teste que prova a fonte externa não roda em lugar nenhum

Encontrado em 10/09/2026, investigando por que a suíte contra PostgreSQL fecha em **2 pulados** e
não em 1, como o `AGENTS.md` registra.

> **Não é defeito, e não vira escopo por estar escrito aqui.** O que se registra é uma decisão
> correta à qual falta a outra metade, o que ela custa, e o que uma spec teria de decidir.
> Priorizar é do usuário.

## O que se observou

A suíte fecha em `4358 passed, 2 skipped`. Os dois pulados, nomeados com `-rs`:

```
tests/integration/test_database_permissions.py:260
    a recusa por vendor só aparece fora do PostgreSQL
tests/interface/test_sorteio_com_a_fonte_de_producao.py:119
    E2E contra a fonte de produção: depende de rede e do serviço da Caixa.
    Ligue com SORTEIO_E2E_FONTE_REAL=1.
```

**O primeiro é por construção e é o histórico.** `test_o_comando_recusa_banco_que_nao_seja_postgresql`
verifica que o comando recusa banco que não seja PostgreSQL — só roda fora dele, e portanto é
sempre pulado na suíte de verdade. É o "1 pulado" do `AGENTS.md`.

**O segundo veio da `021`** (`9582c14`), tem um único caso no arquivo, e é o que fecha a conta:
`test_o_percurso_inteiro_da_presidencia_contra_a_fonte_real` percorre o sorteio inteiro pela
interface — Edital publicado, comissão constituída, universo congelado cinco dias antes, extração
real, ordem produzida e verificada — contra o **serviço real da Caixa**.

**E a CI não liga a chave.** `SORTEIO_E2E_FONTE_REAL` não aparece em `.github/workflows/`. Nem no
`make test-pg`. O teste não roda na CI de PR, não roda no comando de verificação do projeto, e não
roda em nenhuma rotina agendada — porque não existe rotina agendada.

## Por que a decisão de tirá-lo do caminho crítico está certa

Um teste que depende de rede e de serviço de terceiro **não pode** bloquear merge. Ele quebraria por
indisponibilidade da Caixa, por manutenção, por latência — e o sinal diria "defeito no produto"
quando o fato é "o mundo estava fora do ar". Um verde que depende de terceiro não é verde; é sorte.
A `021` acertou ao pô-lo atrás de uma chave.

## O que falta é a outra metade da decisão

Tirar do caminho crítico e **não pôr em lugar nenhum** são duas coisas, e só a primeira foi feita.

O que esse teste exercita não é detalhe de implementação: é a **garantia central da `021` para o
cidadão** — que a semente vem de ocorrência futura, pública e externa, e não de dentro do sistema.
A frase que governa a feature diz *"uma ocorrência futura e previamente determinada de fonte pública
externa fixa a semente"*. O contrato com essa fonte — o formato da extração, o endereço, a forma dos
números — é a única parte do sorteio que **este repositório não controla**, e é justamente a que
nenhum gatilho observa.

Se a Caixa mudar o formato amanhã, o sistema descobre no dia do sorteio de um certame real.

## O estado hoje, medido

Rodado em 10/09/2026 com a chave ligada, contra a `main` em `4640858`:

```
SORTEIO_E2E_FONTE_REAL=1 … pytest tests/interface/test_sorteio_com_a_fonte_de_producao.py
1 passed in 10.87s
```

**O contrato com a fonte está de pé nesta data.** O que não existe é quem repita essa medição sem
alguém lembrar de fazê-la à mão.

## O que uma spec — ou um workflow — teria de decidir

Nenhuma destas se decide lendo código:

1. **Onde o gatilho vive.** Workflow agendado próprio, separado do CI de PR, é o padrão para teste de
   contrato com serviço externo. Com que frequência é escolha: diária diz cedo, semanal faz menos
   ruído.
2. **O que a falha significa, e a quem ela chega.** Falhar sem bloquear merge é o requisito óbvio.
   Menos óbvio: uma falha aí é indistinguível, à primeira vista, entre *"a Caixa está fora do ar"* e
   *"a Caixa mudou o formato"* — e as duas pedem reações opostas. O gatilho precisa separá-las, ou
   admitir que não separa.
3. **A âncora.** O teste aponta hoje para o concurso `6098`, de 06/09/2026, fixo por variável — e a
   escolha é deliberada: *"a extração é história, e não um alvo em movimento"*, o que o torna
   reprodutível. Um gatilho periódico sobre uma extração congelada testa o **formato**, e não a
   disponibilidade; sobre a última extração, testa as duas e deixa de ser reprodutível. São
   objetivos diferentes, e talvez dois testes.
4. **Se o `AGENTS.md` passa a dizer 2 pulados.** Ele registra 1, medido antes da `021`. A conta certa
   hoje é 2, e ambos são deliberados.

## O que não muda por enquanto

Nada. O sorteio funciona, o contrato está de pé na medição de hoje, e o teste continua atrás da
chave — que é onde ele deve estar. O que este documento registra é que **ninguém está olhando**, e
que a data acima é a última vez em que alguém olhou.
