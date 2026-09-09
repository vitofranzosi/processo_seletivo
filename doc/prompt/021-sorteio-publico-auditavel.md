# 021 — Sorteio público auditável

Prompt do `/speckit-specify`. Escrito em 08/09/2026 a partir de uma proposta de feature, revisada
contra o código em `9ab8013` e contra o que o repositório já decidiu sobre sorteio em
[`descoberta-escopo-sorteio-e-anexos.md`](../descoberta-escopo-sorteio-e-anexos.md) §Parte 1.

**Frase que governa:**

> Congelado o universo, qualquer pessoa reproduz a mesma ordem com os dados públicos — e a comissão
> não escolhe a semente depois de conhecer o resultado que ela produz.

**E a frase que mantém o corte:**

> Sorteio não classifica e não ocupa vaga. Ele **constitui uma ordem** sobre um universo congelado;
> quem decide o que essa ordem produz é o resto do sistema.

## CONTEXTO OBRIGATÓRIO, ANTES DO /specify

Ler, nesta ordem:

- `doc/descoberta-escopo-sorteio-e-anexos.md` §"Parte 1 · Sorteio" — **as três formas A, B e C, e o
  que a leitura inicial errou**. É o documento que impede esta spec de repetir premissa
- `doc/avaliacao-de-capacidade-editais-2026-09-08.md` — o sorteio é o bloqueio de maior alcance,
  4 dos 7; e o que **não** é dele
- `doc/achados-editais-externos.md` — os Editais são EVIDÊNCIA, nunca especificação
- `backend/processo_seletivo/resultados/models.py` — `ResultadoEtapa.Origem`, e a docstring da `013`
  que deixou a porta aberta: *"o sorteio e a verificação de reserva de vaga, que a 013 vai hospedar
  depois, produzem desfecho favorável por caminho que não é avaliação"*
- `backend/processo_seletivo/classificacao/models.py` — `AtoDeOrdenacao`, com `universo`,
  `ato_anterior` e `motivo_da_sucessao`: sucessão de ordem **já existe**
- `backend/processo_seletivo/classificacao/application/reproducao.py` — reproduzir uma ordem a
  partir do universo congelado **já é capacidade do sistema**
- `backend/processo_seletivo/classificacao/domain/combinacao.py:131` — marco só de portas devolve
  pontuação **nula**, e o comentário diz que os critérios publicados é que particionam o grupo
- `backend/processo_seletivo/classificacao/domain/desempate.py` — os três tipos de critério, e a
  ordenação nas duas direções
- `backend/processo_seletivo/divulgacao/models.py:43` — `PublicacaoResultado` **exige** um
  `AtoDeOrdenacao`: não há hoje como publicar uma relação que não seja ordem
- `backend/processo_seletivo/shared/canonical.py` — serialização canônica e resumo; a integridade da
  lista de entrada não se inventa aqui
- `.specify/memory/constitution.md` §VI — a capacidade precisa ser observável pelo canal do ator

## O QUE A REVISÃO CORRIGIU NA PROPOSTA

Seis pontos. Nenhum invalida a proposta; todos mudam o que a spec pode prometer.

**1 · O sorteio não conduz nenhum dos quatro Editais até o fim.** Ele remove o **primeiro e maior**
bloqueio de 77, 76, 57 e 28. O 77 manda analisar a documentação até o limite de vagas e parar
quando elas se preencherem — regra de parada por ocupação, que é `014`/`016`. Prometer "quatro
Editais desbloqueados" é o erro que a descoberta de escopo já registrou.

**2 · "Sorteio não é classificação" está certo como princípio e não decide onde a ordem entra.** A
descoberta registrou três formas candidatas, e a spec escolhe uma:

```
A · Resultado individual   ResultadoEtapa por inscrição, e o marco ordena
                           custo: o número sorteado teria de ser pontuação, com o sentido
                           invertido — ou o marco ganha direção

B · Ordem coletiva         AtoDeOrdenacao ganha origem "constituída por sorteio", e não
                           "computada a partir de Etapas"
                           custo: mexe na abstração central da 015

C · Critério de desempate  marco só de portas devolve pontuação nula, e um critério publicado
                           "ordem sorteada" particiona o grupo
                           custo: o menor
```

E a leitura de hoje acrescenta um obstáculo a C que ainda não estava escrito: **o veículo do
número não existe.** Os três tipos de critério são `MAIOR_PONTUACAO_NA_ETAPA`,
`MAIOR_VALOR_DE_FATO` e `MENOR_VALOR_DE_FATO`, e `FatoDeclarado` é, por docstring, *"um fato que o
Edital exige do candidato"*. A ordem sorteada não é declarada por ninguém: é produzida pelo
sistema. C exige, portanto, ou um quarto tipo de critério, ou um fato de origem institucional —
e a segunda alternativa abre uma porta que a `015` fechou de propósito.

**3 · A transmissão ao vivo impede reexecutar, não impede escolher.** A proposta já vê isso e
prefere semente externa; a spec precisa **decidir**, não preferir. Nada impede ensaiar fora do ar e
digitar ao vivo a semente já escolhida. Só fecha essa porta a semente que não é do operador:
origem pública imprevisível **posterior** ao congelamento, ou compromisso publicado antes.

**4 · Recurso contra a relação de habilitados não vem junto.** Publicar a relação e admitir recurso
contra ela são duas capacidades. A segunda é a P-4, que a `018` excluiu explicitamente, e o 76/2026
não prevê recurso nenhum. O fluxo da proposta — *"relação preliminar → recurso → relação final"* —
embute a P-4 sem dizer que a está embutindo.

**5 · O "Lote de Sorteio" já tem parente no código.** `AtoDeOrdenacao` tem `perfil_id`, `marco_id` e
`universo` congelado, e `reproducao.py` já reexecuta a ordem a partir dele. Criar entidade nova sem
antes perguntar se o universo do ato serve é criar a segunda resposta para a mesma pergunta.

**6 · Não há onde publicar a relação.** `PublicacaoResultado` exige um `AtoDeOrdenacao`
(`divulgacao/models.py:43`). A relação de habilitados não é ordem — é conjunto com numeração —, e
por isso ela **é artefato novo**, não configuração de um existente. O 020 já registrou que a relação
de inscritos é universal: o 73/2026 a publica sem haver sorteio nenhum.

## O QUE A PROPOSTA ACERTOU, E A SPEC RECEBE TOMADO

- **Sortear o universo inteiro, e nunca "as 40 vagas".** A ordem é completa e histórica; desistência
  não gera sorteio novo. Isto é o que separa a feature de um gerador de listas.
- **Chave por participante, e não o embaralhador da linguagem.** `random.shuffle` acopla a prova à
  implementação de uma versão de um runtime. Uma chave `SHA-256` por participante, ordenada, é
  reproduzível em qualquer linguagem com a regra de composição publicada.
- **O algoritmo é conteúdo normativo publicado e versionado**, não detalhe de implementação:
  trocá-lo é evento da classe da Retificação, e não deploy.
- **Execução única.** Não existe "executar de novo": havendo nulidade, nasce **outro** sorteio,
  ligado ao anterior e com motivo — que é exatamente a forma de `AtoDeOrdenacao.ato_anterior` +
  `motivo_da_sucessao`, já no código.
- **Manifesto, verificador público e vetores de teste no repositório.** É o que transforma
  reprodutibilidade em auditabilidade de terceiro.
- **A transmissão é evidência, não garantia.** O canal continua sendo o YouTube; o sistema entrega
  uma tela que valha a transmissão e uma verificação que sobreviva ao vídeo.
- **Nada de CPF no pacote público.**

## AS DECISÕES QUE A SPEC PRECISA TOMAR

Cada uma tem recomendação, e recomendação não é decisão.

**D-1 · Onde a ordem sorteada entra — A, B ou C.** *Recomendação:* **B**, com C examinado e
recusado por escrito. B é a única em que o artefato produzido **é** o que o Edital publica — uma
ordem —, e as três coisas que ela exigiria de novo (origem do ato, universo constituído, sucessão)
já existem em `AtoDeOrdenacao`. C economiza modelagem e paga com um quarto tipo de critério ou com
um fato que ninguém declarou; A exige inverter o sentido de um número, que é o sistema decidindo o
que o número significa.

**D-2 · A relação de habilitados entra no recorte?** *Recomendação:* **sim, no mínimo indispensável**
— relação congelada, com numeração pública e resumo canônico, publicada como artefato próprio.
Sem ela não há o que sortear em público nem como reproduzir depois, e a Constituição §VI não aceita
capacidade que nenhum canal alcança. O que **não** entra é recurso contra ela (P-4) e a relação de
inscritos como artefato universal de todo Edital.

**D-3 · Origem e compromisso da semente.** *Recomendação:* fonte pública externa, imprevisível e
**declarada no Edital ou no ato do sorteio antes do congelamento** — a spec define o formato de
normalização do material bruto em semente. Semente gerada pelo próprio sistema durante a transmissão
é a alternativa mais fraca, e se for a escolhida precisa dizer por quê.

**D-4 · Qual identificador público entra na chave.** O protocolo da inscrição já existe e é público
para o titular; a numeração da relação é o que os Editais de fato publicam. São coisas diferentes, e
a chave precisa de uma só. *Recomendação:* a numeração da relação congelada, porque é ela que a
audiência vê e que o verificador de terceiro recebe.

**D-5 · Empate de chave.** Improvável não é impossível, e "improvável" não é regra publicada. A spec
declara o desempate determinístico — pela numeração, presumivelmente — e o vetor de teste que o
prova.

**D-6 · O universo do sorteio.** Perfil, polo, modalidade, grupo ou global: a spec declara quais
recortes existem e **recusa regra de cota dentro do algoritmo**. Concorrência concomitante em AC e
em cota é `016`, e hoje a modalidade é coluna da posição, não lista própria.

**D-7 · Corte e progressão entram?** *Recomendação:* **não.** Sem eles o 77 não fecha, e a spec deve
dizer isso na própria frase de valor em vez de deixar a expectativa correr solta. Incluí-los é
escolha legítima de escopo — e dobra a feature.

**D-8 · Carona candidata:** o local/canal do evento (L-6). O Cronograma publica data e hora e não
publica onde. "Sorteio às 10h, canal do Cefor no YouTube" é o evento desta feature. Pequena, de
autoria, e alheia ao domínio do sorteio — entra ou não por decisão de escopo, não por consequência.

## O QUE JÁ EXISTE E NÃO DEVE SER REINVENTADO

- **Integridade e resumo canônico** (`shared/canonical.py`): a lista congelada não inventa hash.
- **Trilha append-only** (`auditoria`): ator, ato, estados, motivo e correlação já são inalteráveis.
- **Sucessão de ordem com motivo** (`AtoDeOrdenacao.ato_anterior`): a anulação do sorteio é isso.
- **Reprodução a partir do universo congelado** (`classificacao/application/reproducao.py`).
- **Publicação de ordem e sua natureza preliminar/final** (`divulgacao`).
- **Portal público e consulta temporal**: o verificador é uma tela a mais, não um sistema à parte.

## FORA DE ESCOPO — cada um é feature própria

- **Ocupação de vagas, cotas, remanejamento e concorrência concomitante** (`016`);
- **Convocação, chamada e suplência** (`019`);
- **Corte e progressão entre Etapas** (`014`), salvo decisão explícita em D-7;
- **Recurso ou impugnação contra a relação de habilitados** (P-4);
- **Relação de inscritos como artefato universal de todo Edital**;
- **Heteroidentificação** e **aplicabilidade da Etapa** (L-2);
- **Integração com API de transmissão** — o canal é externo e continua externo;
- **Prova objetiva e importação de notas de fora**: é o outro mecanismo ausente, e não é este.

## O TESTE QUE A SPEC PRECISA PASSAR

Descrever, sem lacuna, o ciclo do **77/2026** até a ordem publicada — e **parar ali**, dizendo por
que para:

1. encerradas as inscrições, a comissão publica a relação de habilitados, numerada e com resumo;
2. a relação é **congelada**, e o congelamento registra quantidade, identificadores e resumo;
3. o método já está declarado — algoritmo, versão, universo, fonte da semente e regra de ordenação —
   e não muda em silêncio;
4. a semente vem da fonte pública declarada, **depois** do congelamento;
5. o sorteio é executado **uma vez**, com a tela transmitida, e produz a ordem **de todos** os
   participantes;
6. o resultado é selado e publicado, com manifesto e ordem completa;
7. **um terceiro reproduz a ordem por conta própria**, com SHA-256 e os dados públicos, sem
   depender do vídeo e sem falar com o Ifes;
8. anulado o sorteio, nasce outro ligado ao primeiro, com motivo — e o primeiro continua legível.

O passo 7 é o emblemático: é ele que separa esta feature de um sorteador com semente no rodapé, e é
o que a prática atual não entrega. O passo 8 é o que impede que "refazer" seja um botão.

E o que o teste **não** cobre, deliberadamente: quem ocupa as 39 vagas do 77, quem é suplente, e
até onde a análise documental desce. Isso é `014` e `016`, e a spec que prometer isso está
prometendo outra feature.
