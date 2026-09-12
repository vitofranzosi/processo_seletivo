# Inventário de capturas — revisão de S-00

**Revisa o `§F` de `00-arquitetura-do-manual.md` (commit `152a57c`), como manda o `§I.0`.** O
inventário original foi montado a partir das telas, antes de existir uma página diagramada; o piloto
diagramou quatro páginas e produziu doze capturas, e o que aprendeu está aqui.

> **Este documento não substitui o §F: complementa-o.** As colunas *Estado necessário* e *O que
> precisa estar visível* do §F continuam valendo para toda entrada que não apareça na tabela de
> alterações do §3. O que muda para **todas** as entradas está no §1.

**Total revisado: 89 capturas** (eram 88): uma removida, duas acrescentadas.

---

## 1 · Regras de enquadramento — valem para todas as 89

Substituem e ampliam o `§F.2`.

1. **Viewport de gestão: 1 000 px, não 1 280.** Corrige o §F.2. A 1 280 px a interface de gestão
   abre calhas laterais vazias que sobram no recorte e reduzem o texto útil; a 1 000 px o mesmo
   recorte chega ao manual com a tela cheia de conteúdo. O portal público continua a 1 000 px, e as
   capturas marcadas `celular` continuam a **375 px** com emulação de dispositivo móvel.
2. **Recorte é o padrão; tela inteira é a exceção declarada.** Toda entrada abaixo traz
   `recorte`, `tela inteira` ou `celular` na coluna *Enquadramento*. Uma captura mostra **uma**
   afirmação: se a legenda precisa dizer "e também", ela é duas capturas.
3. **O recorte começa e termina em fronteira de elemento.** A faixa de contexto acima é o elemento
   anterior **inteiro**, nunca "N pixels acima". Margens: 22 px nas laterais, 8 px embaixo.
4. **Resolução 2×**, arquivo guardado com o dobro da largura em pixels CSS do recorte. Doze
   capturas do piloto ocuparam 2,3 MB; 89 devem caber em cerca de 18 MB.
5. **A anotação não é gravada no PNG.** O retângulo de acento e os marcadores `①②③` são desenhados
   por CSS sobre a imagem. Cada entrada abaixo traz, na coluna *Anelar*, o **seletor** do que
   destacar — o roteiro de captura emite as coordenadas em porcentagem a partir do mesmo DOM que
   recortou. Não estimar coordenadas à mão.
6. **Os marcadores seguem a ordem de leitura da imagem**, de cima para baixo e da esquerda para a
   direita — não a ordem de importância na legenda. Um alvo só não recebe número.
7. **Nenhum dado pessoal real, nenhum e-mail real, nenhum CPF de pessoa existente.** Mantida do
   §F.2.
8. **Toda captura de gestão precisa da identidade certa na sessão.** A coluna *Ator* do §F deixa de
   ser informativa e passa a ser instrução: é o nome que se digita no seletor de identidade antes de
   navegar.

---

## 2 · O certame-exemplo: como montá-lo, já que `seed_demo` não o produz

O `§F.1` diz que `seed_demo` "não cobre comissão-a-recurso com o realismo necessário". O piloto
verificou que o problema é maior: **`seed_demo` não produz o certame do §F.1 em nenhuma parte.**

| O que o §F.1 pede | O que `seed_demo` cria |
|---|---|
| Perfil único *Auxiliar de Biblioteca* | dois perfis — *Professor de Informática* e *Técnico de Laboratório* |
| Etapa 1 *Análise de requisitos* (decisória), Etapa 2 *Avaliação de títulos* (pontuada 0–100, mín. 60, peso 2) | três Etapas — duas pontuadas (0–10, mín. 6) e uma decisória |
| Elena, Wagner, Paula, Alice | `ana.elaboradora`, `bruno.homologador`, `carla.publicadora`, `joana.avaliadora` |
| Candidatos Ana, Bruno, Carla, Diego, Elisa, Helena | Ana Silva, Bruno Costa, Clara Dias, Daniel Rocha, Elisa Moraes |
| Um Processo, um Edital | um Processo com **dois** Editais |

A terceira e a quarta linhas juntas produzem um problema que não é de estética: o elenco de
`seed_demo` **colide** com os candidatos — `ana.elaboradora` e a candidata *Ana Silva*,
`bruno.homologador` e o candidato *Bruno Costa*, `carla.publicadora` e a candidata *Clara Dias*. Num
manual que ensina segregação de funções mostrando que são pessoas diferentes, isso é exatamente o
que não pode acontecer.

**Decisão para S-01: o certame do §F.1 é montado à mão, pela interface, com o seletor de identidade
digitando os nomes do elenco.** O seletor aceita nome livre, e o piloto percorreu a cadeia
completa — Elena submete, Wagner homologa, Paula publica — confirmando que a segregação é
percorrível pela interface, sem atalho.

Três apoios que continuam valendo:

- **`--dias-atras N`** do `seed_demo` desloca o certame para trás. É o único jeito de ter, no
  navegador, uma janela recursal **já encerrada** — necessária para `SS-079` e para a publicação
  definitiva. Se o certame for montado à mão, a janela encerrada exige o mesmo recurso ou esperar
  cinco dias.
- **Correio local obrigatório.** O mecanismo padrão de e-mail imprime o código de acesso do
  candidato no terminal do servidor. Para automatizar as onze capturas do candidato é preciso um
  destinatário SMTP local (`DJANGO_EMAIL_BACKEND=…smtp.EmailBackend`, `EMAIL_HOST=localhost`) de onde
  o roteiro leia o código.
- **Um pedido de código por candidato.** Pedir outro código para o mesmo e-mail é recusado por cerca
  de um minuto.

---

## 3 · Alterações entrada por entrada

Entradas não listadas mantêm a linha do §F, com as regras do §1 aplicadas e enquadramento
`recorte`.

### 3.1 Removida

| ID | Motivo |
|---|---|
| **SS-010** *Criar Edital* | **A tela não existe.** `/gestao/processos/criar` cria o Processo **junto com** o primeiro Edital, numa tela só (`Criar Processo e Edital`); acrescentar um segundo Edital a um Processo existente só existe na API. `SS-008` passa a cobrir número, ano e título do Edital, que estão no mesmo formulário. Ver §4 |

### 3.2 Acrescentadas

| ID | Ator | Tela | Estado necessário | O que precisa estar visível | Anelar | Enquadr. | Capítulo |
|---|---|---|---|---|---|---|---|
| **SS-089** | Candidata | *Seus dados* | Primeiro acesso da candidata, antes de qualquer inscrição | Nome completo, CPF e a frase "Pedimos uma única vez. Nas próximas inscrições, não perguntamos de novo" | a frase | recorte | C-12 |
| **SS-090** | Elaboradora | Passo *Classificação* — a janela recursal | Marco com `Admite recurso` marcado, prazo 5, dias corridos | Os **três** modos lado a lado: admite com prazo, não admite, não declarar | o bloco dos três | recorte | C-08 |

`SS-089` faltava: a tela existe, aparece uma vez na vida do candidato e é onde ele descobre que o
CPF não será pedido de novo. `SS-090` desdobra `SS-018`, ver abaixo.

### 3.3 Alteradas

| ID | Alteração | Por quê |
|---|---|---|
| **SS-008** | Passa a ser *Novo Processo e primeiro Edital*. Anelar: o campo do código institucional **e** o par número/ano | Absorve `SS-010`. Uma tela, um formulário, dois assuntos — é o caso legítimo de `①②` |
| **SS-011** | *Estado necessário* passa a exigir um rascunho com, ao mesmo tempo, um passo `CONCLUÍDA`, um `PENDENTE` e um `PRONTA PARA REVISAR`, estando o leitor num quarto | O passo em que se está mostra `ETAPA ATUAL` **no lugar** do seu estado. Sem essa combinação, os três estados não cabem numa captura só |
| **SS-018** | Fica só com os **critérios de desempate**, e ganha `①②③④` nos quatro campos de um critério: *Ordem*, *Critério*, *O que ele compara*, *Quando o valor não existe*. A janela recursal sai para `SS-090` | O espécime de C-08 mostrou que são dois assuntos: um cartão de critério com quatro campos já é a captura mais densa do manual, e a janela recursal é outra decisão, com três modos próprios |
| **SS-023** | `tela inteira` | O assunto é o documento montado, não um trecho dele |
| **SS-034** | Continua desktop; anelar o campo de e-mail | — |
| **SS-035** | Passa a **`celular 375`** | É a tela mais consultada pelo celular de toda a jornada, cabe inteira sem rolagem, e é onde o candidato entende que não há senha. Como desktop ela é uma caixa de texto no meio do branco |
| **SS-036** | *Estado necessário*: a modalidade já **gravada**, não em escolha. Anelar: `①` o seletor de modalidade, `②` o cartão do documento que ela fez aparecer | O documento extra só entra na lista depois que a escolha é gravada. Fotografar durante a escolha mostra a lista antiga |
| **SS-037** | Anelar o botão `Baixar o modelo: ANEXO I — …` | O vínculo do modelo é o assunto; o arquivo enviado é contexto |
| **SS-038** | *Estado necessário* ganha: **todos os documentos obrigatórios já enviados** | Com documento faltando, a tela de revisão **não exibe** o bloco *Dados exigidos pelo Edital* nem o botão `Enviar inscrição`. A captura é impossível no estado descrito no §F |
| **SS-039** | Continua `tela inteira`. Anelar o protocolo. Nota: a tela mostra também um *código de verificação* e um resumo por arquivo — o texto os trata como "detalhe técnico do registro" | — |
| **SS-060, SS-064, SS-085** | Marcadas `larga`: em 375 px deslocam-se dentro da moldura em vez de encolher | São tabelas; reduzidas a 327 px ficam ilegíveis |
| **SS-063** | Mantida, com receita: abrir a prévia em duas abas, publicar por uma, confirmar pela outra. **Se a receita se mostrar frágil na coleta, C-18 usa `SS-079` como captura de recusa** e `SS-063` cai | O piloto usou a recusa da definitiva por prazo aberto, que é trivial de produzir e ensina a mesma coisa: a recusa protege |
| **SS-064** | Anelar o **título**, que nomeia a natureza — e não a tabela | Quem chega por um link precisa saber, sem perguntar, se aquele resultado ainda admite recurso |
| **SS-066** | *Estado necessário* passa a ser **um participante considerado e sem posição** (não um classificado). Anelar o bloco *Resultado divulgado* com o motivo escrito | É a única tela que prova que quem não aparece na lista pública ainda assim sabe o que aconteceu com ele. Com um classificado, a captura repete a lista pública |
| **SS-073** | Anelar as três espécies utilizáveis; a quarta recebe a tarja no HTML, **não no PNG** | Coerente com a regra 5. E a tarja precisa poder mudar se o produto corrigir `H.2` |
| **SS-062** | Anelar `①` a lista *O que acontece ao confirmar*, `②` a natureza, `③` a autoridade signatária. Recorte terminando no botão `Publicar este resultado` | Foi assim no piloto e a captura carrega o capítulo inteiro. A lista de consequências é escrita pelo próprio sistema e diz "imutável e não se despublica" — melhor prova do vocabulário do manual do que qualquer frase nossa |

### 3.4 Confirmadas sem alteração

As cinco capturas de recusa (`SS-004`, `SS-063`, `SS-074`, `SS-078`, `SS-079`) continuam
deliberadas, e o piloto confirmou o motivo: a recusa da definitiva por prazo aberto nomeia o
impedimento, dá a data e oferece a saída, numa tela só — ensina a regra melhor do que o caminho
feliz ensinaria em três.

As três `celular` originais (`SS-065`, `SS-086`, `SS-087`) continuam, agora acompanhadas de
`SS-035`. São quatro.

---

## 4 · O que sai do inventário e entra em `G-03`

**Não existe tela para acrescentar um Edital a um Processo já criado.** O Processo nasce com o
primeiro Edital, numa tela só; a capacidade de acrescentar outros existe no domínio e na API e não
tem interface.

Pelo roteamento do `§H.0` isto **não** vira alerta inline — não muda o que o leitor deve fazer
agora, já que a tela o conduz corretamente pelo caminho que existe. Vai para `G-03`, em uma linha,
junto das capacidades sem tela do `H.14`. E a ficha de **C-06** em `§C.bis` precisa de dois ajustes:
sai a promessa de ensinar "um Processo com vários Editais", e sai `SS-010` da lista de capturas.

---

## 5 · Contagem final

| | §F original | Revisão de S-00 |
|---|---|---|
| Capturas | 88 | **89** |
| Removidas | — | 1 (`SS-010`) |
| Acrescentadas | — | 2 (`SS-089`, `SS-090`) |
| Alteradas | — | 17 |
| `celular 375` | 3 | **4** (entra `SS-035`) |
| De recusa | 5 | 5 |

O enquadramento de cada entrada — `recorte`, `tela inteira` ou `celular` — é decidido na coleta pela
regra 2 do §1, e **declarado na ficha da captura no momento em que ela é tirada**. S-00 já decidiu
quatro: `SS-023` (Prévia do Edital) e `SS-039` (Comprovante) são `tela inteira`, porque o assunto é o
documento inteiro; `SS-035` e as três `celular` originais são `celular 375`. Todas as demais nascem
`recorte` até que a coleta declare o contrário — e uma tela inteira não declarada é motivo para
refazer a captura, não para aceitá-la.

**Divisão por sessão de coleta**, ajustada:

| Sessão | Entradas | Total |
|---|---|---|
| `S-01` | `SS-001` a `SS-042` (sem `SS-010`), mais `SS-089` e `SS-090` | **43** |
| `S-02` | `SS-043` a `SS-067` | **25** |
| `S-03` | `SS-068` a `SS-088` | **21** |

`SS-090` fica em `S-01` porque é o assistente de elaboração, e não uma tela de exceção — o
`§I.2` já mandava colher as fases 1 a 5 na primeira sessão.
