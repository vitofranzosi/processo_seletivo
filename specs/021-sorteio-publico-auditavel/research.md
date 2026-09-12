# Pesquisa — 021 · Sorteio público auditável

Fase 0 do plano. Cada decisão é de **desenho**, e nenhuma reabre as doze da §2 da spec: elas chegam
fechadas e aqui só ganham forma. Onde a decisão custa alguma coisa, o custo está dito.

---

## R-001 · A dimensão da lista no ato, sem quebrar a garantia que já existe

**Problema.** `uq_ato_raiz_por_marco` é única em `(edital, perfil_id, marco_id)` entre atos raiz
(`classificacao/models.py:44`). A D-006 exige três atos raiz — AC, PPI, PcD — para o mesmo Perfil e
o mesmo marco. Colidem.

**Decisão.** `AtoDeOrdenacao` ganha `lista_id` (`UUIDField`, anulável), que guarda a **identidade
publicada da modalidade** quando o ato é de uma lista de reserva, e `NULL` quando é da ampla
concorrência. A constraint única é substituída por **duas parciais**:

```text
uq_ato_raiz_por_marco          (edital, perfil_id, marco_id)             where ato_anterior IS NULL
                                                                           and lista_id IS NULL
uq_ato_raiz_por_marco_e_lista  (edital, perfil_id, marco_id, lista_id)   where ato_anterior IS NULL
                                                                           and lista_id IS NOT NULL
```

**Rationale.** Uma constraint só, com `lista_id` incluído, seria **mais fraca** do que a de hoje: no
PostgreSQL dois `NULL` não colidem, e dois atos raiz de ampla concorrência passariam. As duas
parciais preservam exatamente a garantia atual para o caso sem lista e acrescentam a nova sem
tocá-la. O repositório já usa `UniqueConstraint` com `condition` em vários lugares — não é forma
nova.

**`NULL` = ampla concorrência não é convenção inventada aqui:** `Inscricao.modality_id` já é anulável
com esse mesmo significado, e `PosicaoNaOrdem.modalidade_id` também.

**Alternativas consideradas.**

- *Um marco por lista.* Recusada na spec (D-006): a janela recursal é do marco (`018`) e os
  Editais publicam **um** período de recurso para as três listas — teríamos de declarar três vezes
  o que o Edital declara uma.
- *Sentinela não nula para ampla concorrência* (um UUID fixo). Uma constraint só resolveria, ao
  preço de um valor mágico que nada mais no repositório entende, e de divergir de `modality_id`.

---

## R-002 · Onde mora a relação congelada

**Problema.** `PublicacaoResultado` exige um `AtoDeOrdenacao` (`divulgacao/models.py:43`), e relação
numerada não é ordem. A relação também não é da `classificacao`: ela existe **antes** de qualquer
ordem, e é o compromisso do universo.

**Decisão.** Módulo novo `processo_seletivo/sorteios/`, com domínio, aplicação, API e persistência,
como os demais. Ele hospeda a relação de habilitados, o método declarado, a ocorrência da fonte, o
manifesto e a verificação pública. `classificacao` ganha apenas a dimensão da lista e a proveniência
de origem; `divulgacao` não muda.

**Direção da dependência:** `sorteios → classificacao` (constitui o ato), `sorteios → inscricoes`,
`sorteios → publicacoes` (versão vigente). Nunca o contrário. É a mesma direção que `resultados →
avaliacoes` já pratica.

**Rationale.** O vocabulário é próprio — universo, compromisso, semente, manifesto, verificação — e o
ciclo de vida também. Enfiá-lo em `classificacao` faria o módulo da ordem responder por um artefato
que existe antes da ordem e sobrevive à anulação dela.

**Alternativa considerada.** *Tudo em `classificacao`.* Menos arquivos, e um módulo com duas
linguagens dentro.

---

## R-003 · A função de resumo, e a forma exata da chave

**Decisão.** SHA-256 sobre `canonical_bytes` (`shared/canonical.py`), com separador de domínio.
Identificador normativo do método: **`IFES-SORTEIO-SHA256-v1`**.

```text
chave(participante) = SHA256(canonical_bytes({
    "domain":       "processo-seletivo/sorteio/v1",
    "relationHash": <sha256 canônico da relação congelada>,
    "drawScopeId":  <identidade do recorte: perfil + lista>,
    "seed":         <semente normalizada, string>,
    "publicNumber": <número público do participante, inteiro>
}))
```

**Rationale.** `canonical_bytes` já resolve ordenação de chaves, separadores, normalização Unicode
NFC e serialização de decimais e UUIDs; reimplementá-la para o sorteio criaria uma segunda grafia
canônica no mesmo repositório. SHA-256 é o que `canonical_sha256`, `DocumentoPublicado.document_hash`
e `ArtefatoAnexo.document_hash` já usam — a instituição não passa a depender de mais uma primitiva.

**`relationHash` na chave** separa sorteios distintos que porventura recebam a mesma semente — dois
recortes cujo método aponte a mesma ocorrência não produzem a mesma permutação relativa.

**Alternativa considerada.** *HMAC com a semente como chave.* Equivalente em força para este uso e
mais difícil de reimplementar corretamente por terceiro: HMAC tem detalhes de padding que um
verificador amador erra. O critério aqui é **reimplementabilidade**, não sofisticação.

---

## R-004 · Ordenação e colisão

**Decisão.** Ordem crescente do **resumo binário completo** (32 bytes). Colisão desempata pelo número
público crescente (D-005). Como o resumo é sempre hexadecimal minúsculo de comprimento fixo, a ordem
lexicográfica da representação hexadecimal é idêntica à do binário — o verificador de terceiro pode
usar qualquer das duas.

**Vetor normativo obrigatório, e a forma dele importa.** O desempate precisa de prova executável, e
**não existe entrada válida do sistema que produza duas chaves iguais**: mesmo `publicNumber` em
relações distintas tem `relationHash` distinto, e na mesma relação a numeração é única por
constraint. Colisão real de SHA-256 ninguém constrói.

O vetor honesto exercita o **§4 do contrato**, e não o §3: entrega ao ordenador chaves já iguais e
afirma a ordem resultante.

```json
{"name": "desempate-por-numero-publico",
 "ordering": {"keys": {"7": "<64 hex>", "3": "<mesmo 64 hex>", "5": "<outro>"}},
 "expectedOrder": [3, 7, 5]}
```

Apresentá-lo como "colisão de SHA-256" seria vender como propriedade criptográfica o que é regra de
ordenação — e a tarefa que tentasse gerá-lo assim ficaria impossível de fechar. O nome do vetor
mudou junto com a forma: `desempate-por-numero-publico`, e não `colisao-de-chave`.

---

## R-005 · A fonte da semente: o que é normativo e o que é implementação

**Decisão.** A **identidade** da fonte, a ocorrência, a derivação a partir da data programada, a
normalização e a regra de substituição são **conteúdo normativo publicado** — vivem no método
declarado do sorteio, e alterá-las é ato da classe da Retificação (FR-013, FR-014). O **acesso** à
fonte é implementação: uma porta com adaptadores.

**Corrigido na revisão: o adaptador não é escolhido por ambiente** (FR-076). Esta decisão dizia
"configurada por ambiente", e a implementação a seguiu — havia um `SORTEIO_FONTE_ADAPTADOR` no
`settings`. Isso deixava a fonte declarada no Edital sem efeito algum: o adaptador da Loteria
Federal ignorava o argumento `fonte` e consultava a Caixa fosse qual fosse a declaração, de modo
que um Edital podia publicar `Random.org` e o manifesto anunciaria uma origem que a semente não
teve. O vocabulário de fontes passou a ser **fechado e ligado ao adaptador que cada uma executa**,
e o que resta de ambiente é o que sempre foi operação: tempo limite e tentativas.

**Adaptador de referência:** extração da Loteria Federal, que é ocorrência pública, futura,
previamente determinada por número de concurso e data, e amplamente usada como fonte de
aleatoriedade em atos administrativos brasileiros. A escolha institucional é do usuário; a spec fixa
as propriedades, não a fonte.

**Regra de substituição.** Publicada, mecânica e sem escolha humana — tipicamente "a ocorrência
imediatamente seguinte da mesma fonte". Aplicá-la MUST registrar a evidência da indisponibilidade
(FR-015, e ver R-006).

**Onde o método vive** (D-013): não em tabela própria, mas no conteúdo canônico do Edital, como
objeto do marco de classificação — `drawMethod`, ao lado da `appealWindow` que o degrau 8 já pôs
ali. É o que faz "alterá-lo é Retificação" deixar de ser analogia: o caminho
`/profiles/id=…/classificationMilestones/id=…/drawMethod/…` já resolve na gramática existente.

**Onde a semente derivada não vive** (D-016): não na ocorrência. Normalizar é regra do método, a
ocorrência é única por `(fonte, referência)`, e guardar ali a semente normalizada congelaria a regra
do primeiro método que a lesse. A ocorrência guarda material bruto; a semente é do `Sorteio`.

**Alternativas consideradas.**

- *Semente do próprio sistema, gerada ao vivo.* Recusada na D-003.
- *Compromisso criptográfico publicado pela comissão.* Recusado na D-003: conhecendo o universo, ela
  mói sementes e publica o resumo da conveniente.

---

## R-006 · Atomicidade, rede e o modelo de ameaça honesto

**Problema.** Obter a semente é I/O de rede; constituir o ato é transação de banco. Fazer rede dentro
da transação é ruim; fazer fora parece contrariar a D-010.

**Decisão.** Duas etapas, e a fronteira é o que a D-010 de fato proíbe. **A FR-029 foi reescrita
para dizer isto**: na redação anterior ela exigia obter a semente, calcular e constituir num comando
único, e o plano entregava dois — a spec pedia literalmente o que o desenho recusava, e uma das duas
tinha de ceder. Cedeu o texto, porque o desenho está certo: fundir a ida à rede com a transação não
acrescenta garantia nenhuma e troca uma falha de rede por uma transação longa.

```text
1. observar   busca a ocorrência na fonte e grava OcorrenciaDaFonte (append-only, idempotente
              por (fonte, ocorrência)). NÃO calcula ordem, NÃO cria ato.
2. constituir comando único, atômico e idempotente: lê a ocorrência gravada, calcula a ordem
              e constitui o ato, tudo numa transação.
```

**O que a D-010 proíbe é prévia da ordem, e não observação da semente.** Nenhum caminho do sistema
calcula ou exibe a ordem antes de constituir o ato.

**O modelo de ameaça, dito por inteiro.** Depois que a ocorrência existe, ela é pública e o algoritmo
é publicado: **qualquer pessoa — inclusive a comissão — pode calcular a ordem por fora.** Isso não é
falha do desenho; é consequência necessária da auditabilidade. O que resta como risco é a comissão
**deixar de emitir** e invocar a regra de substituição para pegar outra ocorrência. Três controles,
nenhum deles perfeito sozinho:

1. a substituição só se aplica nas hipóteses publicadas, e exige **evidência registrada** da
   indisponibilidade;
2. a execução é transmitida ao vivo, na data e hora publicadas;
3. a trilha de auditoria registra cada observação de ocorrência, inclusive as que não viraram ato.

O controle 3 é o que torna o abuso **visível**: uma ocorrência observada e descartada aparece.

---

## R-007 · O manifesto é derivado, não copiado

**Decisão.** O manifesto não é uma segunda cópia dos dados: é **função determinística** da relação
congelada, da ocorrência e do ato. O que se grava no ato é o `manifesto_hash`, calculado na
constituição. O download regenera o manifesto e o resumo prova que nada mudou.

**Rationale.** Duas cópias divergem, e a que diverge sempre é a que ninguém lê. É a mesma razão pela
qual a Seção gerada não persiste texto (`020`, FR-040).

---

## R-008 · A segunda implementação, e onde ela vive

**Decisão.** Uma implementação de referência em JavaScript, exercitada pelos vetores normativos em
`backend/tests/javascript/sorteio.test.js`, rodada pelo `node --test` que `backend/tests/
test_javascript.py` já dispara dentro do `pytest`.

**Rationale.** A SC-002 exige duas implementações independentes reproduzindo os vetores. O
repositório já tem a máquina para isso, e ela roda na mesma CI. Sem isso, "reimplementável" é
promessa; com isso, é teste que quebra.

**Cuidado registrado:** `node --test` muda de relator entre terminal e pipe — asserção sobre o
resumo do runner passa local e reprova na CI. Afirmar sobre o resultado, nunca sobre o texto do
relatório.

---

## R-009 · O degrau canônico 10

**Decisão.** `SCHEMA_VERSION` 9 → 10, acrescentando `location` a cada evento de `/schedule`. Degrau
em `publicacoes/domain/elevacao.py`, na cadeia que já existe.

**A conversão é legítima pelo critério que o módulo declara:** a ausência tem significado declarado e
**verdadeiro** — `""` diz "este Edital não declarou onde o evento acontece", e isso é verdade sobre
todo Edital publicado antes do degrau, porque a capacidade não existia.

**A Retificação não ganha gramática:** `/schedule/id=…/location` é alcançável pelo endereçamento por
identidade da `004`, do jeito que `isRegistrationPeriod` demonstrou (`009`, FR-008).

---

## R-010 · A verificação pública, e por que ela não pode olhar o resultado

**Decisão.** A verificação vive no `portal`, é anônima, e **recalcula a partir das entradas** —
relação, semente, método —, comparando com as posições publicadas apenas no fim, para reportar.

**Rationale.** É a regra que `reproducao.py` já carrega: *"A posição gravada nunca é usada como
entrada do motor"*. Um verificador que lesse a ordem publicada e a conferisse contra si mesma
provaria apenas que sabe copiar.

---

## R-011 · A numeração pública da relação

**Decisão.** Números inteiros de 1 a N, atribuídos na projeção em ordem crescente de **protocolo da
inscrição**, que é único, público para o titular, estável e alheio a qualquer juízo.

**Rationale.** A numeração precisa de regra determinística e reproduzível — ela entra na chave
(D-004). Ordenar por instante de submissão publicaria quem chegou primeiro; ordenar por nome
dependeria de dado editável e não único; sortear a numeração seria sortear antes do sorteio.

**Consequência aceita:** o participante que figura em duas listas recebe **números diferentes** em
cada uma, porque cada relação é numerada de 1 a N. É o que o Edital faz — a relação é publicada por
lista.

---

## R-012 · Quem entra na relação

**Decisão.** Projeção, na versão vigente do Edital, de:

```text
lista de ampla concorrência   todas as inscrições SUBMETIDAS do recorte de vaga
lista de reserva              as inscrições SUBMETIDAS do recorte cuja modalidade é a da lista
```

Havendo Etapa anterior de habilitação declarada no Edital, entram apenas as inscrições com
`ResultadoEtapa` vigente favorável naquela Etapa. Não havendo, entram todas as submetidas — que é o
caso dos quatro Editais lidos, em que a análise documental vem **depois** do sorteio.

**Rationale.** FR-002: a relação é projeção de fatos oficiais. A regra precisa ser legível numa
frase, porque ela é publicada junto com a relação.

---

## R-013 · Autorização

**Decisão.** Os comandos são **quatro**, e a lista anterior contava mal: publicar a relação **é**
congelá-la — o próprio `data-model.md` abre dizendo isso —, e anular é constituir um sorteio
sucessor, não comando à parte. Em compensação, faltavam dois que escrevem e não tinham autorização
declarada.

| Comando | Quem pode | Por quê |
|---|---|---|
| declarar o método | quem elabora e retifica o Edital (`001`) | é conteúdo normativo do Edital, e não ato do sorteio (D-013) |
| observar a ocorrência | `comando_de_comissao` | escreve registro auditado, e o descarte de ocorrência é controle da R-006 |
| publicar a relação (= congelar) | `comando_de_comissao` | é o compromisso do universo |
| constituir o sorteio (raiz ou sucessor) | `comando_de_comissao` | é o ato, e a anulação é o sucessor dele |

Presidência como base suficiente, como `013`, `015` e `017` já fazem. Nenhum papel novo.

**Segregação:** quem constitui o sorteio não precisa ser distinto de quem publicou a relação — o
sorteio não é juízo, e a garantia contra manipulação está na semente, não na separação de pessoas.
A `001` continua valendo onde já valia: elaborar, homologar e publicar o Edital.

---

## R-014 · A leitura do vigente, quando o ato não veio de Etapa

**Problema.** `ato_vigente` procura um ato por `(edital, marco_id)` e devolve o primeiro sem
sucessor; `estado_do_marco` recomputa a classificação por Etapas e compara com `vigente.universo`
para decidir obsolescência; `aferir` consome esse veredito. Nenhum dos três foi escrito para um ato
que não vem de Etapa nem para três atos no mesmo marco. Deixados como estão, a US4 sorteia, o
seletor escolhe uma das três ordens ao acaso e a publicabilidade recusa todas como obsoletas.

**Decisão.** Despachar por `lista_id` na leitura e por `universo["origem"]` na aferição.

- `ato_vigente` passa a receber `lista_id` — sem ele, "o vigente do marco" não é pergunta com uma
  resposta;
- `estado_do_marco`, vendo `origem == "SORTEIO"`, **não** recomputa: a obsolescência de um ato de
  sorteio é a da relação que o originou (a relação foi sucedida?), e não a divergência contra um
  cálculo que jamais o produziu. É a mesma pergunta — "o ato ainda reflete o fato de origem?" — feita
  ao fato de origem certo;
- `aferir` não muda de regra: consome o estado já despachado.

**Alternativa considerada.** *Fazer o ato de sorteio gravar um `universo` no formato de Etapas, para
atravessar a comparação sem tocar em `classificacao`.* Recusada: seria escrever, num campo de
proveniência, uma origem que não existiu — e a comparação passaria a acusar divergência a cada
mudança de Etapa num marco que não depende de Etapa nenhuma.

**Regressão obrigatória:** o caminho de hoje — marco sem lista, ato computado — sai bit a bit igual.
É o que autoriza a alteração.

---

## R-015 · O resumo público tem de ser recalculável por quem o lê

**Problema.** O conteúdo canônico da relação incluía `registrationId`. A FR-005 e a regra 1 do
`manifesto.md` proíbem identificador interno no canal público. O cidadão recebia, então, um
`relationHash` que **entra na chave de cada participante** e que ele não tinha como recalcular a
partir da relação publicada — só aceitar. Isso desmonta a SC-002 por dentro: reimplementar o
algoritmo continuaria possível, verificar a entrada dele não.

**Decisão.** O conteúdo canônico da relação **é** a projeção pública da FR-005 — `publicNumber`,
`name`, `protocol` —, mais o recorte, a versão, o critério e o `methodHash`. Nada que o portal não
mostre entra no resumo público.

**Consequência aceita:** corrigir o nome de um participante muda o `relationHash`. Está certo que
mude — é fato de origem sucedido, e a D-011 já manda por aí: nova relação, nova ocorrência, novo ato.

**Alternativa considerada.** *Dois resumos, um interno e um público.* Não recusada em definitivo, mas
não construída agora: um resumo interno só se justifica quando houver um uso interno que o peça, e
hoje não há. O que a análise recusa é o resumo único cobrir o que o canal público não pode exibir.
