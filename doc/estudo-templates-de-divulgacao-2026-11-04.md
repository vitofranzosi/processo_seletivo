# Estudo: adotar os templates da comunicação no kit de divulgação

**Data**: 04/11/2026. **Fonte**: os 21 arquivos `.pptx` em `~/Downloads/templates/`, fornecidos pelo
usuário, renderizados pelo PowerPoint e lidos slide a slide. **Ponto de partida**: o kit da `111`,
com o incremento B mergeado (#364): uma peça feed 1080 × 1350, um desenho só, marca oficial do
Cefor, PNG pelo `resvg-py`.

Este documento é estudo e plano. Nada foi implementado.

**Decisões T-1 a T-9 aceitas pelo usuário em 04/11/2026, todas como recomendadas na seção 4.** O
que depende da comunicação — as licenças e o banco de imagens (T-4), a substituta da Helvetica Neue
(T-5), o tamanho do banner (T-8) e a aprovação de cada template — continua com ela.

---

## 1. O que existe nos arquivos

**Sete famílias, três formatos cada.** Cada família é uma identidade visual para um tipo de
certame; cada formato, um destino.

| Família | Paleta e tipografia | Imagem | Exemplos | Orientação embutida |
|---|---|---|---|---|
| **FIC** | Amarelo e roxo; Archivo Black, Barlow Semi Condensed, Space Mono | Ilustrações 3D (megafone, pessoa ao computador, foguete) | 8 | 2 slides "NÃO EDITE": balão móvel, campo livre |
| **Libras** (FIC de Libras) | Amarelo e preto; Unbounded, Helvetica Neue | Foto recortada em círculo; ícone de mãos | 2 | "Mantenha centralizado" |
| **Pós Lato Sensu** | Roxo com padrão em chevron, amarelo; Poppins | Foto de estudante | 5 | Retângulo amarelo de altura variável; balão móvel |
| **Pós Aperfeiçoamento** | Azul e verde-limão; Unbounded, Lexend, Poppins | Foto presa por clipe | 5 | — |
| **TMD** (Técnico em Multimeios Didáticos) | Roxo e lilás; Archivo Black, Helvetica Neue | Ilustração plana | 1 | — |
| **UAB / Seleção de bolsista** | Cinza claro, escuro ou mostarda, com título em magenta, verde ou branco; Anton, Poppins | Foto em faixa | 5 | — |
| **Internos** (servidores e alunos) | Verde com losangos; Unbounded, Helvetica Neue | Fotos em losango | 2 | Uma arte para servidores, outra para alunos; "mantenha alinhado à esquerda" |

| Formato | Tamanho | Uso |
|---|---|---|
| Post | 4:5, **1080 × 1350** | Feed do Instagram (o formato da peça atual) |
| Story | 9:16, **1080 × 1920** | Stories do Instagram |
| Site | ≈1,76:1 (750 × 425 px a 96 dpi no arquivo) | Banner do site do Cefor |

**O que todas têm em comum**, e é o esqueleto do template:

1. **Chamada** curta no alto: "INSCRIÇÕES ABERTAS", "PROCESSO SELETIVO", "SELEÇÃO DE BOLSISTA",
   "Edital Unificado", "CURSO".
2. **Título grande**: o nome do curso ou da seleção.
3. **Ofertas**, quando há mais de uma, com **carga horária** (FIC: "Assistente Administrativo –
   180h") ou só o nome (Aperfeiçoamento).
4. **Prazo** em destaque: "Prazo: 18/02/2025", "Inscrições até 09/11", "Até o dia 30 de abril".
5. **Número do Edital**: "Edital nº 149/2025", às vezes num balão.
6. **Atributos**: "Gratuita e 100% a distância", "Modalidade a distância", "Vagas remanescentes".
7. **Chamada à ação**: "Acesse o link na bio", "Para mais informações, acesse o edital".
8. **Contato** (só FIC): e-mail e telefone do setor.
9. **Rodapé fixo**: @ifescefor no Instagram, "Ifes Cefor" no YouTube e a marca do Cefor.
10. **Faixa de situação** (só FIC): "ATENÇÃO!! EDITAL PRORROGADO", "INFORMAÇÃO COMPLEMENTAR",
    "EDITAL DE VAGAS REMANESCENTES".

---

## 2. O que o sistema já sabe, e o que não sabe

Cada texto da peça precisa vir da ficha publicada ou de uma frase fixa aprovada (FR-3423 da `111`).
Os templates foram feitos para preenchimento à mão, e por isso escrevem coisas que o sistema não
tem como comprovar.

| Elemento do template | No sistema | Situação |
|---|---|---|
| Título do curso | Título do Edital, do Processo, nome do Perfil | **Já existe** |
| Ofertas | Perfis com nome e localidade, teto de quatro | **Já existe** |
| Carga horária | `workload` do Perfil, publicado (texto livre, pode ser vazio) | **Existe; falta levar à ficha** |
| Prazo | Término do período publicado, data absoluta | **Já existe** |
| Edital nº | Número e ano | **Já existe** |
| "Edital prorrogado" | Prorrogação comprovada pela Retificação | **Já existe** (selo atual) |
| "Informação complementar" | Retificação publicada | **Existe; falta levar à ficha** |
| Contato | `atendimento` da Unidade (109), quando declarado | **Existe; falta levar à ficha** |
| Rodapé (@ifescefor, YouTube) | Nada | Ativo fixo da família, aprovado com o template |
| Família (FIC, Pós, UAB…) | **Nada**: o Processo não tem tipo nem categoria | **Falta** (decisão T-2) |
| "Gratuita", "100% a distância", "Modalidade a distância" | **Nada** | **Afirmação sem fonte** (decisão T-3) |
| "Vagas remanescentes", "Seleção de bolsista", "Curso técnico" | Só se estiver no título | **Afirmação sem fonte** (decisão T-3) |
| "Inscrições abertas" | Proibido pela FR-3414 | **Conflito** (decisão T-1) |
| "Inscrições até 09/11", sem ano | A FR-3424 pede data absoluta | **Conflito** (decisão T-1) |
| Fotos e ilustrações | Nada | **Licença desconhecida** (decisão T-4) |

---

## 3. Viabilidade técnica

**O motor serve sem troca.** O `resvg` desenha tudo o que os templates usam: retângulos arredondados,
formas livres (os balões, as manchas), padrões (o chevron do Lato Sensu), recorte de foto em círculo
e losango, gradiente. O SVG continua sendo a fonte, e o PNG sai do mesmo arquivo.

**As fontes são quase todas livres.** Archivo Black, Barlow Semi Condensed, Space Mono, Unbounded,
Poppins, Anton e Lexend estão sob a SIL OFL, e entram como a Edital Sans entrou: subconjunto
versionado, com `ORIGEM.md` e resumo conferido. **A Helvetica Neue não** (Libras, TMD, Internos): é
proprietária, e precisa de substituta livre aprovada pela comunicação.

**O compositor precisa generalizar, não ser reescrito.** Hoje ele tem uma fonte, um tamanho de
página e um desenho fixos no código. O plano é separar em três camadas:

1. **Formato**: o tamanho e a área útil (post, story, banner).
2. **Família**: a paleta, as fontes, os ativos (marca, ilustrações, fotos, padrões) e as frases
   fixas aprovadas.
3. **Template = família × formato**: uma declaração das caixas — onde vão a chamada, o título, as
   ofertas, o prazo, o número, a chamada à ação, o contato e o rodapé, com o corpo máximo e mínimo
   de cada uma. O compositor mede, quebra e recusa como hoje.

O que já existe e se reaproveita inteiro: a ficha e a impressão; a medida e a quebra pela fonte; a
recusa que não trunca; o teste geométrico; a conferência peça ⊂ textos; os SVG de referência; a
prévia e a exportação com registro na trilha.

**Volume**: 7 famílias × 3 formatos = 21 templates, cada um com o seu SVG de referência e a sua
aprovação humana. É o custo maior, e é por isso que o plano entrega por família.

---

## 4. Decisões que destravam o plano (aceitas em 04/11)

| # | Pergunta | Recomendação |
|---|---|---|
| **T-1** | Os templates escrevem "Inscrições abertas" e datas sem ano. A `111` proíbe as duas coisas: o material circula por semanas e a frase do dia vira falsa no seguinte. Mantém-se a regra? | **Manter.** Os próprios templates já usam "Inscrições até": basta escrever a data com ano ("Inscrições até 09/11/2026"). "Inscrições abertas" sai. |
| **T-2** | O sistema não sabe se um Edital é FIC, Pós ou bolsista. Quem escolhe a família? | **Quem gera escolhe, numa lista fechada**, como a manchete: a escolha vai para a trilha da exportação. Um campo de categoria no Processo seria mais correto, mas é mudança de modelo e fica para depois, se a escolha manual errar. |
| **T-3** | "Gratuita", "100% a distância", "modalidade a distância", "vagas remanescentes": o Edital publicado não tem esses campos. | **Fora da peça até virarem dado publicado.** Carga horária entra (já é campo do Perfil). Para modalidade e gratuidade, uma spec própria acrescenta os campos ao Edital, com o rito normativo. Enquanto isso, a família pode trazer uma frase fixa **genérica** aprovada pela comunicação, desde que verdadeira para todo Edital daquela família. |
| **T-4** | As fotos e ilustrações são de banco de imagens? Com que licença? | **A comunicação confirma a licença e escolhe um banco curto por família** (3 a 6 imagens), versionado com `ORIGEM.md`. Quem gera escolhe uma da lista. **Sem envio de imagem pela tela**: foto de pessoa é dado pessoal e superfície nova. |
| **T-5** | A Helvetica Neue é proprietária. | **Substituir por uma livre** parecida (Inter ou Archivo, por exemplo), aprovada pela comunicação. |
| **T-6** | Os textos dos templates mandam "acessar o link na bio". O sistema não controla a bio. | **Chamada à ação fixa por formato**: "Acesse o link na bio" no post e no story, "Acesse o edital" no banner. A linha "busque por 91/2026 – Cefor" continua, menor, para quem chega sem o link. |
| **T-7** | O "Dúvidas?" usa e-mail e telefone do setor. | **Usar o `atendimento` da Unidade** (109), quando declarado; sem ele, a linha não sai. |
| **T-8** | Qual é o tamanho exato do banner no site do Cefor? | **Perguntar à comunicação**: o arquivo diz só a proporção. |
| **T-9** | Isso amplia o escopo da `111`, que limitou o MVP a um template e excluiu stories e banner. | **Spec nova**, que generaliza o kit e herda as regras da `111`. A `111` fecha com o incremento C (pacote e galeria), que vira a ferramenta de aprovação dos 21 templates. |

---

## 5. Plano

**Etapa 0 — Decisões** (usuário e comunicação): T-1 a T-9. A T-4 é a que mais atrasa, porque
depende de levantar licenças.

**Etapa 1 — Fechar a `111` com o incremento C** (T028–T036): pacote ZIP e **galeria**. A galeria
publica os cenários de referência e mostra cada peça lado a lado; é nela que a comunicação aprova.

**Etapa 2 — Spec nova: templates por família e formato.** Requisitos herdados da `111` (coerência,
datas absolutas, recusa sem truncar, determinismo, registro); novos requisitos para a escolha da
família e da imagem, a carga horária, o contato e a faixa de Retificação.

**Etapa 3 — Motor generalizado**, sem mudar nenhuma peça: formato e família como dados; fontes como
objetos (hoje são duas constantes da Edital Sans); a peça atual vira a primeira família ("GPS
neutro"), e os SVG de referência dela não mudam. É a prova de que a generalização não quebrou nada.

**Etapa 4 — Uma família nos três formatos.** Sugestão: **Pós Lato Sensu** — uma fonte só
(Poppins), estrutura simples (título, número, atributos, prazo, chamada), e o caso com mais
exemplos. Entrega post, story e banner, com referências, geometria e aprovação na galeria.

**Etapa 5 — As outras seis famílias**, uma por PR, na ordem de uso: FIC (inclui Libras como
variante), UAB/bolsista, Aperfeiçoamento, Internos, TMD.

**Etapa 6 — Ligar em produção** família a família, conforme a comunicação aprova (a chave
`KIT_DE_DIVULGACAO_PECA` passa a valer por família).

---

## 6. Riscos

- **Afirmação sem fonte entrar pela frase fixa.** "Gratuita" verdadeira para FIC hoje pode não ser
  amanhã. Cada frase fixa de família precisa de aprovação explícita, e a varredura de vocabulário
  passa a ler todas.
- **Texto que não cabe.** Os templates foram desenhados para os exemplos deles. Um título de pós com
  120 caracteres no story cabe; no banner, talvez não. O compositor recusa com motivo, nunca
  trunca, e a manchete da lista fechada continua como saída.
- **Volume de revisão.** 21 templates com aprovação humana. A galeria reduz o custo, mas não o
  elimina.
- **Imagens pesadas.** As fotos dos arquivos têm 2 a 4 MB cada. Reduzidas para o tamanho de uso,
  como a marca, ficam em dezenas de kB.
