# Contrato das telas: Minhas atividades

Nenhuma rota nova e nenhuma rota de API nova. Muda o conteúdo de `/gestao/minhas-etapas`. Mudam
também o nome visível na barra e nas trilhas, e a nota da faixa da Lista.

## `GET /gestao/minhas-etapas` — "Minhas atividades"

Rota `interface:minhas-etapas`, view `minhas_etapas`, as mesmas de hoje (FR-6852). Sem identidade:
pede identificação, como hoje. Não exige permissão: o estado vazio não é recusa.

### Cabeçalho

- `<title>` e `h1`: "Minhas atividades".
- Trilha do cabeçalho de contexto: o produto e "Minhas atividades" com `aria-current="page"`.
- `p.sub`: "O que é seu nos Editais das comissões que você integra."

### 1. "Para fazer agora" — `section` com `aria-labelledby="para-fazer-titulo"`

- `h2#para-fazer-titulo`: "Para fazer agora", com a contagem dentro do título, em
  `span.contagem-da-secao`: "N ato(s) em M Edital(is)" (UX-711). Sem linha, só "Para fazer agora".
- `ul.providencias` (as regras do nível 1 do Centro, sem o fundo de destaque). Cada `li.atividade`
  traz:
  - o sinal e a palavra da situação (`span.situacao-do-andamento`, UX-715), **só quando ela não é
    *Pendente*** — todas as linhas da seção são *Pendente* ou *Obsoleto*, e o *Obsoleto* precisa ser
    visto (revisão visual de 12/11);
  - o ato, em `strong.ato`, com o texto da derivação;
  - `p.onde-da-atividade`: "Edital N/AAAA · <lugar> · <fase>". Num grupo: "N Editais · <lugar comum,
    se houver> · <fase>";
  - `span.base-da-atividade`: "Presidência" ou "Alocação" (FR-6861);
  - **linha única**: `a.botao` com o verbo da tela de destino e o link com âncora da derivação;
  - **grupo**: `details.editais-do-grupo`, com `summary` "Ver os N" e uma `ul` com um `li` por Edital,
    cada um com o seu link.
- Sem linha: `p.vazio[role=status]` — "Nada depende de você agora no que esta página cobre." (FR-6873)

### 2. "Em espera nos seus Editais" — `details.em-espera` (fechado)

- `summary`: "Em espera nos seus Editais · N" (UX-712). Ausente quando N = 0.
- `p.explicacao`: "Ninguém precisa agir até a data; cada uma diz de onde ela vem."
- `ul.providencias.em-espera`. Cada `li` traz o sinal e a palavra (*Aguarda* ou *Impedido*), o ato, o
  Edital ou "N Editais", e `span.razao` com a razão da derivação, que diz a origem da data (FR-6869):
  "o prazo do candidato corre até …". No *Impedido*, quem o resolve (`texto_de_quem_resolve`). Sem
  link de ato e **sem marca de base**: a espera não é ato da pessoa, e o que vem depois pode ser do
  Publicador ou do candidato (revisão visual de 12/11).
- Nenhum texto da seção diz "seu prazo" nem "atrasado" (SC-2277).

### 3. "Suas Etapas de avaliação" — `ul.comissao[aria-label]`

Os cartões de hoje: o medidor, "Concluída", "Nenhuma inscrição distribuída a você ainda" e "Abrir".
As Etapas com avaliação pendente ficam abertas; as concluídas e as sem inscrição distribuída ficam em
`details.etapas-recolhidas`, com o `summary` "Concluídas ou sem inscrição distribuída · N" (revisão
visual de 12/11). O `h2` "Suas Etapas de avaliação · N" vem antes. Sem alocação, o estado vazio de hoje,
revisto (FR-6876):
- **quem preside**: "Presidir uma comissão não atribui trabalho de avaliação." O resto da frase de
  hoje fica;
- **os demais**: "Você não tem Etapa de avaliação atribuída." Os atos de Edital e de Retificação
  continuam em Processos Seletivos, com o link.

### Os Editais não lidos — `p.aviso.nao-lidos[role=status]`

Antes da seção 1, quando houver: "N Edital(is) não pôde(puderam) ser lido(s) agora:", seguido dos
links para o detalhe de cada um (FR-6874). A frase vazia da seção 1 não aparece se houver Edital não
lido e nenhum ato.

### A nota de cobertura — `p.cobertura-da-pagina`

Depois da seção 1, sempre (FR-6871, FR-6872):

> Esta página reúne os atos da presidência nos Editais que você preside, a avaliação e a conferência
> de documentos a que você foi alocado. Ficam fora, e estão em outro lugar:
> - a formalização, em Formalização, na barra;
> - os atos de Edital e de Retificação e os recursos a julgar, em Processos Seletivos;
> - publicar o resultado, a publicação das inscrições e das convocações, os avisos aos candidatos, o
>   Requerimento de Matrícula e o encerramento, no Centro de Controle de cada Edital.

Ao Gestor, acrescenta-se: "O que você pode fazer por permissão de gestão fica no Centro de Controle de
cada Edital."

### "Comissões que você integra"

O bloco de hoje, sem mudança, depois das três seções (FR-6875).

## Barra lateral e trilhas

- A `Secao` de `navegacao.py`: "Minhas atividades", no mesmo grupo e com o mesmo ícone e destino.
- `minha_etapa.html` e `mesa_inscricao.html`: o elo da trilha diz "Minhas atividades".
- `lista.html`: "Ver minhas atividades".

## `GET /gestao/` — a faixa da Lista

- Os itens e a contagem da faixa ficam como hoje. Nenhuma contagem de "Minhas atividades" (FR-6880).
- A nota (`p.cobertura-da-faixa`) e a frase vazia continuam contendo `trabalho.FORA_DA_FAIXA` por
  inteiro. A constante é **uma frase, só com o que fica fora**: as oito famílias da FR-4324 da
  `129`, que ficam no detalhe de cada Edital, e "o que é da sua comissão está reunido em", seguida
  do link `a.para-minhas-atividades` "Minhas atividades", para `interface:minhas-etapas` (R-010). O
  que a faixa reúne é dito antes: na nota com itens, "Esta faixa reúne atos de Edital e de
  Retificação, recursos e avaliações."; na vazia, a frase própria dela. Assim a enumeração não se
  repete (revisões de 12/11).
- A Lista não chama a derivação do andamento (FR-6882).

## A 375 px (UX-714)

Sem rolagem horizontal. A seção 1 começa na primeira tela. O botão da linha vai para baixo do texto,
pela regra da folha, sem `nowrap` que alargue o cartão.

## A revisão de UX de 12/11 (FR-6885 a FR-6888)

Prevalece sobre o que estiver acima:

- **Título de "Para fazer agora"**: com uma base só, "· N atos em M Editais · pela presidência" (ou
  "· pela alocação"), e as linhas sem `span.base-da-atividade`. Com bases misturadas, o título sem a
  base, e a marca em cada linha.
- **Filtro**, com mais de um Edital: `form.filtro-de-edital` (GET, para a própria página), com
  `label[for=filtro-edital]` "Edital", `select#filtro-edital[name=edital]` — a primeira opção
  "Todos os Editais (N)", as demais "Edital N/AAAA · K atos" ou "· só em espera" — e o botão
  `.botao.secundario` "Filtrar". Valor que não serve mostra tudo, com status 200.
- **Nota de cobertura**: `p.cobertura-da-pagina` com a frase de `atividades.COBERTURA`, e
  `details.onde-encontrar` fechado, com o `summary` "Onde encontro as outras operações?" e um item por
  destino (`atividades.ONDE_ENCONTRAR`); só Processos Seletivos é link. Ao Gestor, mais um item, o de
  `COBERTURA_DO_GESTOR`.
- **Avaliação sem atribuição**: o `h2` "Suas Etapas de avaliação · nenhuma", sem `p.vazio`. A quem
  preside, `p.nota-da-secao`.
- **Comissões**: `details.comissoes-da-pessoa`, com o `summary` "Comissões que você integra · N",
  fechado, e `open` só quando a página não tem nada a fazer, nada em espera, nenhum não lido e
  nenhuma Etapa. Os caminhos da presidência em `span.links-da-comissao`, separados por "·".
