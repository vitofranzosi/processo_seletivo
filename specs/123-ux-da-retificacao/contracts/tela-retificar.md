# Contrato de tela: Retificar e as telas do «Antes» (123)

O que cada tela promete a quem a usa e aos testes. Os textos entre aspas são literais; o que está
entre `<>` é preenchido.

## 1. Retificar — criação (`interface:retificar`)

### 1.1 Frase da base (FR-3935, FR-3937)

No «Como funciona» e acima da tabela do resumo, o fragmento `_versao_base.html`:

- incorpora: "A versão-base é a Publicação original de <dd/mm/aaaa>" ou "A versão-base reúne a
  Publicação original de <dd/mm/aaaa> e as Retificações nº <n> (<dd/mm/aaaa>) e nº <m>
  (<dd/mm/aaaa>)";
- situação, uma de:
  - "Ela vigora desde <dd/mm/aaaa hh:mm>."
  - "Ela ainda não vigora: passa a vigorar em <dd/mm/aaaa hh:mm>. Até lá vigora uma versão
    anterior."
  - "Ela vigorou a partir de <dd/mm/aaaa hh:mm> e já não é a versão em vigor."

O «Como funciona» da criação diz "Abaixo está o conteúdo da versão-base do Edital." (o da edição,
em §2). A palavra "vigente" não qualifica a base. "Vigente hoje" não aparece em lugar nenhum da tela.
"Retificação nº N" usa a numeração do detalhe do Edital: N é a ordem da publicação (D-006).

### 1.2 Seção de impeditivos (FR-3940 a FR-3944, D-009)

Na conferência com proposta e com impeditivo ou recusa de guarda, e na resposta de «Criar» ou
«Gravar» recusada por conteúdo (além da recusa no alto, que continua), antes do resumo:

```html
<section id="impeditivos" aria-labelledby="impeditivos-titulo" class="impeditivos">
  <h2 id="impeditivos-titulo">O que impede criar esta Retificação (<n>)</h2>
  <p>«Criar Retificação» será recusado enquanto houver <um impeditivo|estes impeditivos>.</p>
  <ul>
    <li><mensagem> <a href="#cartao-<ref>">Ir ao cartão</a></li>
    <li><mensagem></li>   <!-- sem destino -->
  </ul>
</section>
```

Na edição, "Gravar a Retificação" no lugar de "Criar Retificação".

### 1.3 Resumo (FR-3932, FR-3937)

Colunas: «Onde», «Campo», «Na versão-base», «Passará a ser», e uma última sem título visível
(`<th scope="col"><span class="visualmente-oculto">Ir</span></th>`, se a classe já existir; senão
`aria-label` na célula) com:

- `<a class="ir-ao-campo" href="#c-<campo>">Ir ao campo</a>`, nome acessível "Ir ao campo
  <rótulo> — <onde>"; ou
- `<a class="ir-ao-campo" href="#cartao-<cartao>">Ir ao cartão</a>` quando a linha é do cartão
  inteiro.

### 1.4 Cartões (FR-3927, FR-3929)

`fieldset.linha[data-na-proposta]` com, na legenda, `<span class="na-proposta">na proposta</span>`,
antes do selo «alterada» quando os dois existirem. Linha nova: `id="cartao-novo-<prefixo>-<indice>"`.

### 1.5 Barra (FR-3930, FR-3934)

Sinais do servidor, no `form`, **depois** de `data-conferido` (que continua como está):
`data-modo="edicao"` (só na edição), `data-enviado` (toda resposta a POST), `data-proposta`,
`data-proposta-cartoes`, `data-proposta-remocoes` (R-007).

Dentro de `.barra-de-acoes`, o script escreve dois elementos, ambos `aria-live="polite"`: primeiro a
`span.contagem` de hoje, com a frase "desde a conferência"; depois a `span.estado-da-proposta`. A
segunda coluna abaixo vale **com `data-enviado`**; sem ele, valem as frases de "antes de conferir".

| `data-proposta` | Frase da proposta | Frase desde a conferência |
|---|---|---|
| `nao-conferida` (GET da criação) | "Proposta ainda não conferida" | "Nenhum campo alterado ainda" / "1 campo alterado" / "<n> campos alterados" |
| `conferida`, N = 0 | "Nenhuma alteração na proposta" | "Nenhuma alteração nova desde a última conferência" / "1 campo alterado desde a última conferência" / "<n> campos alterados desde a última conferência" |
| `conferida`, N ≥ 1 | "1 cartão com alteração na proposta" / "<n> cartões com alteração na proposta" | idem |
| `recusada` | "Proposta não conferida — veja a recusa acima" | idem a `conferida` |

Na edição, `data-proposta="conferida"` desde o GET (a proposta é o ato que já existe), e a frase da
proposta ganha " e 1 remoção já declarada" / " e <k> remoções já declaradas" quando
`data-proposta-remocoes` > 0. Na edição **sem** `data-enviado`, a segunda frase é "Nenhuma alteração
nova nesta edição" / "1 campo alterado nesta edição" / "<n> campos alterados nesta edição".

### 1.6 Busca (FR-3917 a FR-3926)

Criada pelo script, como hoje, só com 12 ou mais cartões:

```html
<div class="filtro-da-retificacao">
  <label for="filtro-da-retificacao">Encontrar</label>
  <input type="search" id="filtro-da-retificacao" placeholder="campo, valor ou cartão — vagas, remuneração, Término…">
  <span class="marca"><input type="checkbox" id="so-alteradas"><label for="so-alteradas">Só o que eu alterei</label></span>
  <span class="achados" aria-live="polite"><n> resultados em <m> cartões | Nenhum campo corresponde | Mostrando 25 de <n> resultados — refine a busca</span>
  <ol class="resultados-da-busca">
    <li><span class="onde"><seção> › <cartão></span> <span class="rotulo"><rótulo></span>
        <span class="valor"><valor, até 80 caracteres></span>
        <a class="ir-ao-campo" href="#c-<ref>" aria-label="Ir ao campo <rótulo> — <cartão>">Ir ao campo</a></li>
    <li><span class="onde"><seção> › <cartão></span>   <!-- resultado de cartão (FR-3917) -->
        <a class="ir-ao-campo" href="#cartao-<ref>" aria-label="Ir ao cartão <cartão>">Ir ao cartão</a></li>
  </ol>
</div>
```

Nenhum elemento da caixa tem `name`.

## 2. Retificar — edição (`interface:retificacao-editar`)

Igual à criação, com: a base é a da Retificação; a coluna «No rascunho» no lugar de «Na
versão-base»; o título "O que muda em relação ao rascunho"; a proposta é o ato inteiro (R-003),
calculada desde o GET. O «Como funciona» da edição diz: "Abaixo está o conteúdo *proposto* por esta
Retificação: a versão-base com o que ela já declara. Altere o que precisa mudar; o que já foi
declarado e você não tocar continua no ato, e o campo que voltar ao valor da versão-base deixa de ser
alterado. Nada muda para o público até a Retificação ser publicada.", seguido da frase da base.

## 3. Retificar — somente leitura

Título "Conteúdo da versão-base" (no lugar de "Conteúdo vigente"), o aviso "Abaixo está o conteúdo
da versão-base do Edital, como referência." e a frase da base logo abaixo.

## 4. Detalhe da Retificação e confirmações (FR-3938)

Em `retificacao_detalhe.html` e em `retificacao_confirmar.html` (homologar, devolver, publicar),
imediatamente antes da tabela com «Antes», o fragmento, prefixado: "«Antes» é o conteúdo da
versão-base desta Retificação." A coluna continua «Antes»; nada mais nessas telas muda.

## 5. O que não muda

Rotas, nomes de campo do formulário (`campo:<ref>`, `remover:<ref>`, `arquivo:<ref>`, `base`,
`revisao`, `gesto`, `aplicar`, `confirmar`, `justificativa`, `vigencia`, `desfazer-remocao`),
`chave_idempotencia`, o `action` do formulário e os status das respostas.
