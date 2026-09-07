# 020 — Anexos do Edital

Prompt do `/speckit-specify`. Escrito em 07/09/2026 depois da avaliação dos sete Editais anexos;
revisado no mesmo dia, com quatro decisões vindas de revisão externa e com a leitura do
[Edital 73/2026](https://cefor.ifes.edu.br/index.php/processo-seletivo/bolsistas-e-estagiarios/17703-edital-73-2026-processo-de-selecao-de-cadastro-de-reserva-de-assistente-pedagogico-para-atuar-nos-cursos-do-programa-universidade-aberta-do-brasil-uab-ofertados-pelo-ifes),
que fechou duas perguntas que estavam em aberto.

**Frase que governa:**

> Um Edital que exige documento em forma própria precisa publicar essa forma — sob a mesma vigência,
> a mesma Retificação e a mesma consulta histórica do resto do seu conteúdo.

**E a frase que mantém o corte:**

> Isto não é uma feature de documentos. É uma feature de **conteúdo normativo binário versionado**.

## CONTEXTO OBRIGATÓRIO, ANTES DO /specify

Ler, nesta ordem:

- `doc/avaliacao-de-capacidade-editais-2026-09-07.md` — **L-5** é esta feature; **L-1** não é
- `doc/descoberta-escopo-sorteio-e-anexos.md` §"Parte 2 · Anexos" — a bifurcação e o teste
- `doc/achados-editais-externos.md` — os Editais são EVIDÊNCIA, nunca especificação
- `backend/processo_seletivo/editais/models/documentos.py` — `DocumentoExigido`, e **a recusa que
  esta spec não pode desfazer**
- `backend/processo_seletivo/editais/models/secoes.py` — o precedente exato da D1: identidade
  estável, conteúdo que muda, **sem tabela de versões própria**
- `backend/processo_seletivo/publicacoes/models.py` — `Publicacao`, `DocumentoPublicado`
  (bytes + hash, append-only) e `VersaoConsolidada`
- `backend/processo_seletivo/publicacoes/models_retificacao.py` — `AlteracaoNormativa`, e em
  especial `expected_previous_hash`: **a concorrência entre Retificações já está resolvida**
- `backend/processo_seletivo/publicacoes/domain/changes.py` — o seletor só aceita UUID; coleção
  inendereçável é coleção irretificável
- `specs/004-enderecamento-normativo-estavel/spec.md` — identidade estável, nunca posição
- `specs/009-inscricao-simples-documentos/spec.md` — `DocumentoSubmetido`, `versao_reconhecida` e
  `versao_aceita`

## A DISTINÇÃO CENTRAL, QUE A SPEC NÃO PODE PERDER

```
anexo como ARQUIVO      o autor sobe o formulário; o candidato baixa, preenche, assina,
                        digitaliza e devolve; a banca lê e defere.
                        O sistema NUNCA lê os campos.          ← ESTA FEATURE

anexo com CAMPOS        o autor declara campos; o candidato preenche dentro do sistema;
que o sistema conhece   o sistema gera o documento preenchido.  ← NÃO É ESTA FEATURE
```

**Esta spec entrega a primeira, e recusa a segunda.** A `009` já escreveu a recusa, e ela vale
palavra por palavra:

> não há quinta forma, não há operador e não há expressão — e é essa recusa que separa isto de um
> construtor de formulários

O critério para quando um campo **é** legítimo já está escrito, na docstring de `FatoDeclarado`
(`015`): *o campo existe porque uma regra publicada o consome*. Onde consome, ele já tem casa e não
precisa de anexo estruturado. Onde não consome, é tela — e o arquivo basta.

Na amostra há **um** campo que uma regra consome: a coluna "Expectativa de pontuação pelo candidato"
das fichas do 14/2026 e do 173/2025, vinculante no segundo. Ele é do **barema**, não desta feature.
Trazê-lo para cá é como esta spec incha até virar outra.

## O CICLO INTEIRO, E QUANTO DELE JÁ EXISTE

```
elaboração    o autor inclui no Edital o documento que o candidato devolverá        ← FALTA
     ↓
publicação    o anexo viaja com o Edital, sob a mesma vigência e Retificação        ← FALTA
     ↓
inscrição     o candidato baixa, preenche, assina, digitaliza e anexa               ← existe (009)
     ↓
avaliação     a banca lê e conclui — defere ou indefere                             ← existe (012/013)
```

**Dois terços já existem, e a spec não os reinventa.** O que falta é a primeira perna: hoje o Edital
exige o anexo e manda o candidato a um anexo que o documento publicado não contém.

Metade desses anexos exige assinatura e carimbo. O ciclo passa por imprimir e digitalizar porque a
**norma** exige, não porque o sistema seja pobre. Isso não é limitação a superar.

## A EVIDÊNCIA QUE GOVERNA AS DECISÕES ABAIXO

O Edital 73/2026 publica doze anexos, e o que a página dele mostra vale mais que qualquer argumento
de projeto:

```
Edital        publicacoes.ifes.edu.br/cef/Edital-73-2026.pdf              publicado 16.07
Anexo I       drive.google.com/file/d/1Tgs2ip1eo…                         RETIFICADO 31.08
Anexo II–XII  publicacoes.ifes.edu.br/cef/Anexo-II-Requerimento-…pdf      nomes sem versão
```

Três fatos, e nenhum é hipótese:

1. **O anexo é retificado sozinho**, quarenta e cinco dias depois, com o Edital permanecendo na
   versão original;
2. **os nomes não comportam duas versões** — caminho estável, sem data e sem revisão;
3. **a retificação vazou do acervo institucional para o Google Drive** — assim como o Resultado
   preliminar retificado e dois dos três Comunicados, enquanto os artefatos originais estão no
   servidor de publicações.

O terceiro é o Drive que a docstring de `DocumentoSubmetido` diz que o sistema veio substituir,
reaparecendo do outro lado — no conteúdo normativo.

## AS QUATRO DECISÕES QUE ESTA SPEC JÁ RECEBE TOMADAS

Não são perguntas para o `/plan`. Reabrir qualquer uma exige evidência nova.

**D1 · Identidade normativa estável, separada do artefato binário.** O anexo tem identidade própria
no conteúdo publicado; cada versão referencia um artefato imutável por hash. Retificação substitui o
artefato **da mesma identidade** — não cria silenciosamente um "Anexo VII".

```
Anexo VI  ← identidade normativa estável
   │
   ├─ conteúdo canônico da versão 3 → { id, título, hash A }
   └─ conteúdo canônico da versão 4 → { id, título, hash B }
```

As versões 3 e 4 são **do Edital**, não do anexo: não existe tabela de versões por anexo, pela mesma
razão que não existe por Seção. Este é o padrão do `SecaoEdital`, e por isso a D1 custa zero.

**D2 · Os anexos acompanham a publicação; não se incorporam ao PDF principal.** A justificativa é a
prática observada, não uma limitação técnica: o Anexo I do 73/2026 foi retificado sozinho.
Incorporar faria a correção de um cronograma **reescrever o documento normativo inteiro**, que é o
que a instituição demonstradamente não faz. O PDF do Edital lista e referencia; não carrega os
bytes.

**D3 · Seção estruturada rotulada como "Anexo" continua sendo seção.** A numeração editorial não
determina a entidade de domínio. O Cronograma é gerado pelo catálogo, é retificável por campos
estruturados e é "Anexo I" em cinco dos sete Editais lidos — e continua sendo Seção. Um anexo
binário é opaco, o sistema não conhece seus campos, e é retificado por substituição do artefato.
Fundir os dois porque ambos aparecem sob o título "ANEXO" é confundir forma editorial com natureza
de conteúdo.

**D4 · A `versao_aceita` da Inscrição precisa resolver qual artefato estava vigente.** Dada a
`versao_aceita`, o sistema tem de conseguir dizer exatamente qual artefato publicado correspondia a
cada anexo referenciado pelos documentos exigidos **naquela versão**. Isso responde o caso normal —
o candidato baixou o Anexo VI sob a versão 3, a Retificação o substituiu na versão 4, ele submete o
antigo preenchido — e responde **sem guardar nada novo**: o hash já está no conteúdo canônico daquela
versão, e a resolução é uma consulta. Guardar o hash redundantemente em cada submissão, ou rastrear
downloads, exige demonstração de necessidade no `/plan`.

## O QUE A EVIDÊNCIA FECHOU

**O anexo é PDF.** Doze de doze no 73/2026; nenhum Edital lido publica anexo editável. Admitir
`.docx` seria construir para um caso que não existe, contra a disciplina que o próprio projeto
escreve em `EtapaAvaliacao` — *"admitir não é exigir"*. Entra quando aparecer o Edital que o exija, e
com ele entram conversão, visualizador e a pergunta de renderização — todos hoje inexistentes.

**Não há dupla política de formato.** Anexo publicado e documento submetido são ambos PDF. O que
separa os dois não é formato, é **regime**: um é conteúdo público versionado, o outro é documento
privado do candidato. É essa fronteira que a spec precisa afirmar.

## O QUE SOBRA PARA A SPEC DECIDIR

- **operações semânticas da Retificação** sobre a coleção — acrescentar, substituir o artefato,
  alterar rótulo, alterar ordem editorial, remover da versão futura —, todas por UUID e nunca por
  posição. "Remover" significa **deixar de existir na versão consolidada seguinte**, e nunca `DELETE`
  no histórico;
- **referência pendurada**: se um `DocumentoExigido` aponta o anexo como modelo e a Retificação o
  remove, o vínculo não pode sobreviver ao alvo. O repositório já tem a forma da resposta em
  `EtapaAvaliacao.evento` — *"remover o Evento não pode remover a Etapa; o que não pode é o vínculo
  sobreviver a ele"*;
- **numeração editorial atravessa as duas coleções** — se o Cronograma renderiza como "Anexo I" e os
  binários vêm em seguida, o rótulo é da renderização, e não campo de nenhuma das duas entidades;
- **regime de acesso do armazenamento**: pode reutilizar infraestrutura física, mas o regime é de
  conteúdo público versionado, e **não** o da raiz privada da `009`. A spec não precisa exigir dois
  buckets; precisa não perder a fronteira de autorização;
- **quem substitui um anexo, e sob qual ato**;
- **integridade da cadeia** `versão histórica → identidade → hash publicado → bytes`, como garantia
  interna. Expor verificação ao usuário é decisão de produto e não entra por esta porta.

## O QUE JÁ EXISTE E NÃO DEVE SER REINVENTADO

- `DocumentoExigido` e `DocumentoSubmetido` — o que se exige e o que volta;
- Etapa decisória com rótulos publicados pelo Edital, mesa de avaliação e `ResultadoEtapa` — o
  deferimento já funciona, e **esta feature não acrescenta máquina de avaliação nenhuma**;
- `DocumentoPublicado` — bytes com hash, append-only;
- Retificação, `VersaoConsolidada` e consulta temporal;
- **controle otimista entre Retificações concorrentes** — `AlteracaoNormativa.expected_previous_hash`
  já resolve o caso de duas Retificações sobre o mesmo anexo. A spec herda; não desenha;
- **a cardinalidade do vínculo não é decisão**: uma referência anulável no `DocumentoExigido`
  apontando o anexo já é `N:1` por construção. Não há o que escolher nem o que adiar.

## FORA DE ESCOPO — cada um é feature própria

- **formato que não seja PDF**, e tudo que ele arrastaria: conversão, visualizador, pacote ZIP,
  concatenação;
- **quadro de vagas estruturado** (L-1). Se alguém propuser publicá-lo como anexo binário para ganhar
  tempo, a nota de descoberta registra o preço: conteúdo publicado não se remodela, e o acervo se
  bifurca em definitivo;
- **barema estruturado e autopontuação vinculante** (D-4 da `015`, P-7);
- **campos legíveis pelo sistema**, de qualquer natureza; **geração de documento preenchido**;
  **preenchimento web**; **editor online**;
- **assinatura digital, ICP-Brasil, validação de assinatura**;
- **OCR, extração ou qualquer leitura do conteúdo do que o candidato devolve** — a `009` já recusou;
- **limite de páginas e limite de arquivo declarados pelo Edital** — pressão registrada contra
  FR-046, feature própria;
- **Comunicados e atos normativos complementares** — o 73/2026 tem três, e o 14/2026 os prevê
  ("incorporar-se-ão a este Edital quaisquer editais complementares"). São publicação posterior que
  altera o certame sem ser Retificação, e o sistema não tem essa figura. Achado novo, e não é daqui;
- **relação de inscritos publicada** — o 73/2026 a publica sem haver sorteio, o que a torna artefato
  universal e não consequência do sorteio. Também não é daqui;
- sorteio, corte e progressão, ocupação de vagas, convocação.

## O TESTE QUE A SPEC PRECISA PASSAR

Descrever, sem lacuna, o ciclo do **173/2025** — nove anexos, entre eles autodeclaração
étnico-racial, declaração de pertencimento quilombola e anuência da chefia imediata:

1. o autor publica o Edital com os nove anexos;
2. uma Retificação substitui um deles e preserva o anterior;
3. o candidato baixa o vigente **na data em que se inscreve**;
4. devolve preenchido e assinado, como `DocumentoSubmetido`;
5. a banca defere ou indefere lendo o que voltou;
6. a consulta pública, perguntada por um instante anterior à Retificação, devolve **o anexo de
   então**;
7. **os dois artefatos coexistem** — abrir a publicação histórica baixa o antigo, abrir a vigente
   baixa o novo, e os hashes são distintos.

O passo 7 é o emblemático: é ele que separa esta feature de um gerenciador de arquivos, e é
exatamente o que a prática atual perde quando substitui o arquivo no mesmo caminho.

Se qualquer um dos sete passos não couber na spec, ela ainda não está pronta.
