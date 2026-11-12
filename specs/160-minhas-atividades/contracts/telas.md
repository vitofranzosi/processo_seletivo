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
- `ul.providencias.suas` (as regras do nível 1 do Centro). Cada `li.atividade` traz:
  - o sinal e a palavra da situação (`span.situacao`, UX-715);
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
  Edital ou "N Editais", e `span.razao` com a razão da derivação, que diz a origem da data (FR-6869).
  No *Impedido*, quem o resolve (`texto_de_quem_resolve`). Sem link de ato.
- Nenhum texto da seção diz "seu prazo" nem "atrasado" (SC-2277).

### 3. "Suas Etapas de avaliação" — `ul.comissao[aria-label]`

Os cartões de hoje, sem mudança: o medidor, "Concluída", "Nenhuma inscrição distribuída a você ainda"
e "Abrir". O `h2` "Suas Etapas de avaliação · N" vem antes. Sem alocação, o estado vazio de hoje,
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
  inteiro. A constante passa a dizer onde está cada família (R-010). Depois dela vem
  `a.para-minhas-atividades` "Minhas atividades", para `interface:minhas-etapas`.
- A Lista não chama a derivação do andamento (FR-6882).

## A 375 px (UX-714)

Sem rolagem horizontal. A seção 1 começa na primeira tela. O botão da linha vai para baixo do texto,
pela regra da folha, sem `nowrap` que alargue o cartão.
