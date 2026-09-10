# Percurso conduzido — SPEC 025 · Quadro de Vagas por Modalidade

**Data:** 10/09/2026 · **Branch:** `claude/speckit-implement-025-f79c6c` · **Base:** commit `138090a`
**Ambiente:** banco `ps_demo_025`, `seed_demo` aplicado, `INTERFACE_SELETOR_IDENTIDADE=true`,
servidor em `http://localhost:8025` (entrada `quadro-025` do `launch.json`).

**Escopo:** o percurso do [quickstart](../../../specs/025-quadro-de-vagas-por-modalidade/quickstart.md),
conduzido pela interface administrativa contra o servidor real — declarar, publicar e retificar o
quadro de vagas do `57/2026`. O Edital foi montado **à mão pela tela**: o `seed_demo` não produz este
certame, e o elenco dele colide com o que o percurso precisa.

## Sobre as evidências

**Não há PNGs em `screenshots/`, e é limitação da sessão, não esquecimento** — o mesmo registrado
pela auditoria da `020`. O painel de navegador desta ferramenta devolve as capturas para a conversa e
não as grava em disco, e nesta sessão ele esteve oculto durante o percurso, de modo que a leitura foi
feita por `get_page_text`, `read_page` e consulta ao DOM. Cada achado abaixo traz, no lugar da
imagem, a **URL, o seletor e o texto literal observado**, que é o que o torna reproduzível.

---

## 1. Veredito

**A feature está entregue pelo canal do ator, e o percurso do gate da §9 fecha inteiro.** Declarar,
recusar, publicar, ler no documento e retificar por identidade — os cinco passos acontecem pela
interface, sem shell e sem banco. O ciclo do `57/2026` foi percorrido do começo ao fim e o conteúdo
publicado saiu como a spec descreve: `AC 56`, `PcD 4`, `PPI 20`, total 80, e depois `PPI 18` com
total 78 por um ato só.

**Seis defeitos foram encontrados, e os seis foram corrigidos nesta mesma sessão, com teste que os
prende.** Cinco deles só apareceriam a quem usasse a tela: quatro estavam na composição — a linha
que não nascia, a linha que nascia sem forma, a recusa que não ancorava e o número que a duplicata
sobrescrevia — e um estava no documento publicado, que passou a ter duas tabelas com o mesmo nome
dizendo coisas diferentes. Nenhum deles seria pego por teste de domínio, e é exatamente por isso que
o percurso conduzido existe.

**O que a spec deixou aberto continua aberto, e continua registrado.** No Edital que declara uma
Modalidade chamada "Ampla concorrência" — o formato que a própria spec diz ser o normal —, o quadro
nunca fica completo e a igualdade da `FR-161` não roda. O limite superior da `FR-177` roda e pega a
direção perigosa. É a lacuna da `R-006`, e a escolha entre as duas saídas é do usuário.

---

## 2. Os seis achados

### `E2E25-001` — o Perfil recém-acrescentado não oferecia linha nenhuma

**Onde:** `/gestao/editais/<id>/compor/perfis`, botão **Acrescentar Perfil**.

A seção **Quadro de vagas** aparecia com o título e mais nada: `section.quadro` continha
`div#quadro-<i>` vazio. Quem compõe um Edital do zero — que é todo Edital — não tinha onde escrever a
quantidade da ampla concorrência até salvar e recarregar a tela. O caminho natural da `US1` começava
com um beco.

**Causa:** `fragmento_perfil` montava o Perfil novo sem a chave `quadro`, e o template itera sobre
ela.

**Correção:** o Perfil novo nasce com a linha geral oferecida. As reservadas continuam nascendo com
as Modalidades, uma a uma, porque é delas que vêm o rótulo e a identidade que a linha aponta.

**Fechado por:** `tests/interface/test_compor_quadro.py::test_o_perfil_acrescentado_pela_tela_ja_oferece_a_linha_geral`.

### `E2E25-002` — a linha vinha, e vinha sem forma

**Onde:** mesma tela, botão **Acrescentar Modalidade**.

A linha do quadro correspondente **chegava** — os campos estavam lá, com os nomes certos —, mas sem o
`div.linha-do-quadro` que a desenha: os `input` e o `<p>` caíam soltos dentro da seção. Observado no
DOM: `#quadro-<i>` com 13 filhos e apenas 1 `.linha-do-quadro`.

**Causa:** o htmx swapa o **conteúdo** do elemento marcado com `hx-swap-oob`, e não o elemento. A
marcação estava na própria linha, e o invólucro era descartado junto.

**Correção:** um envelope existe só para ser jogado fora, e o `div.linha-do-quadro` vai dentro dele.

**Fechado por:** `tests/interface/test_compor_quadro.py::test_a_modalidade_acrescentada_traz_a_linha_do_quadro_com_a_forma_dela`.

### `E2E25-003` — a recusa da linha não ancorava no controle

**Onde:** mesma tela, ao enviar duas linhas gerais no mesmo Perfil.

A recusa aparecia no resumo — *"A ampla concorrência tem uma linha só no quadro de vagas do
Perfil."* — e não junto do campo: `[aria-invalid=true]` vazio, nenhum `.recusa` na seção. Num Edital
de sete polos, quem lê o resumo não sabe em qual deles o número está errado.

**Causa:** o cálculo da âncora descia até a linha, mas o template da linha nunca chamava
`recusa_de`; e a tag compunha o `id` com três partes, e o da linha tem quatro.

**Correção:** `recusa_de` aceita a quarta parte, e a linha exibe a recusa ao lado do campo. Quando a
linha recusada não está entre as oferecidas — o caso da duplicata —, a âncora recua para a linha
daquele recorte, que é onde a pessoa corrige.

**Fechado por:** `tests/interface/test_compor_quadro.py::test_a_recusa_da_segunda_linha_geral_devolve_o_que_foi_digitado`.

### `E2E25-004` — a duplicata sobrescrevia o número certo na reexibição

**Onde:** mesma tela, depois da recusa acima.

Quem tinha `56` na ampla concorrência e enviava uma segunda linha geral recebia de volta a
quantidade **da duplicata** — observado: a linha geral voltou com `4`, e o `56` sumiu na tela que
existe para mostrá-lo. A gravação seguinte gravaria o número errado sem que ninguém percebesse.

**Causa:** a reexibição indexava as linhas digitadas por recorte num dicionário, e a última vencia.

**Correção:** a primeira ocorrência vence, porque é a que a pessoa vê primeiro e é a que ela está
corrigindo.

**Fechado por:** o mesmo teste do `E2E25-003`.

### `E2E25-005` — o documento publicava duas tabelas chamadas "Quadro de vagas"

**Onde:** documento publicado de um Edital com mais de um Perfil.

`Tabela 1 — Quadro de vagas` era a comparativa de Perfis (código, localidade, vagas, reserva, carga
horária) e `Tabela 3 — Quadro de vagas — TEC-INFO` era a repartição por lista de concorrência. Duas
tabelas homônimas no mesmo documento, dizendo coisas diferentes.

**Causa:** a `T001` renomeou a **função** privada e não a legenda — e quem lê o Edital lê a legenda.
O achado só existe porque esta feature passou a publicar a segunda tabela.

**Correção:** a comparativa diz o que tabula: `Perfis de vaga`.

**Fechado por:** `tests/contract/test_documento_publicado.py::test_as_duas_tabelas_de_vagas_nao_se_chamam_a_mesma_coisa`.

### `E2E25-006` — a opção vazia da lista de concorrência dizia "Sem restrição"

**Onde:** `/gestao/editais/<id>/retificar`, campo **Lista de concorrência** da linha do quadro.

O `select` oferecia `Sem restrição`, `PCD — …`, `PPI — …`. Mas o vazio, ali, **é** a ampla
concorrência — a lista de que todos participam —, e "sem restrição" diz o oposto: que a linha não se
restringe a lista nenhuma.

**Causa:** o rótulo da opção vazia era literal no template, escrito para o Documento Exigido, onde
`null` de fato significa "sem restrição".

**Correção:** o rótulo do vazio passa a vir do campo; fora da linha do quadro, o texto continua o que
era.

**Fechado por:** `tests/interface/test_retificar_quadro.py::test_a_tela_oferece_a_colecao_do_quadro_com_a_modalidade_como_escolha`.

---

## 3. O percurso, passo a passo

### Percurso 1 — Declarar (`US1`, `SC-048`)

Edital `57/2026` montado com dois Perfis: `TEC-INFO` (80 vagas, Modalidades `PCD` e `PPI`) e
`TEC-EDIF` (40 vagas, Modalidade `PPI`).

- A seção **Quadro de vagas** oferece as linhas a partir das Modalidades declaradas, com o rótulo
  vindo do código e da denominação. **Só as quantidades são digitáveis** — quatro números no
  `TEC-INFO`, e nenhum rótulo redigitado (`UX-021`, `SC-048`).
- Digitado `56`, `4`, `20`; gravado; recarregado. As três quantidades voltam (`FR-153`).
- `TEC-EDIF` ficou **sem quadro**, com as duas linhas em branco. Gravou. A ausência não virou zero
  (`FR-159`, `FR-160`, `D-006`).

**As recusas, com o texto literal observado:**

| Ato | Resposta da tela |
|---|---|
| segunda linha geral no `TEC-INFO` | *"A ampla concorrência tem uma linha só no quadro de vagas do Perfil."* (`FR-154`) |
| linha do `TEC-INFO` apontando a `PPI` do `TEC-EDIF` | *"A linha do quadro aponta uma modalidade que não pertence ao Perfil declarado."* (`FR-158`) |
| `PPI 19` com total `80`, na Revisão | **IMPEDE** *"O quadro de vagas do Perfil 'TEC-INFO' soma 79 e o Perfil declara 80 vagas imediatas — diferença de 1."*, com o link **Ir para Perfis de Vaga** (`FR-161`, `UX-023`, `SC-054`) |

A recusa da soma aparece na Revisão, e não na gravação — que é o certo: recusá-la ao salvar
impediria guardar o trabalho pela metade, que é o que compor um Edital de sete polos exige.

### Percurso 2 — Publicar (`US2`, `SC-053`)

Submetido, homologado por `ana.elaboradora` e publicado por `bruno.publicador` — atores distintos,
como a segregação de funções exige, e a tela **não oferece** publicar a quem homologou.

- Conteúdo publicado: `schemaVersion 12`; `TEC-INFO` com as três linhas, `modalityId: null` na geral;
  `TEC-EDIF` com `vacancyTable: []` (`FR-164`, `FR-167`).
- Documento publicado, seção `4.2`: `Tabela 3 — Quadro de vagas — TEC-INFO`, colunas
  `Lista de concorrência` / `Vagas imediatas`, **`Ampla concorrência 56` em primeiro lugar**, depois
  `Pessoa com deficiência (PCD) 4` e `Pretos, pardos e indígenas (PPI) 20` (`FR-169`).
- Seção `4.1`, do `TEC-EDIF`: **a tabela não existe** — sem título, sem cabeçalho, sem frase de
  ausência (`FR-169`).

**O acervo anterior** (`SC-050`): os três Editais do `seed_demo` leem com `vacancyTable: []` na
versão 12, e nenhuma tela passou a afirmar zero vaga por causa do quadro. O `0 vagas imediatas agora`
que a página do `01/2026` exibe é o total do Perfil de cadastro reserva, declarado muito antes desta
feature — e não o quadro.

### Percurso 3 — Retificar (`US3`, `SC-049`)

- A tela de Retificação oferece as três linhas como grupos próprios — *"Linha do quadro de vagas
  PPI — Pretos, pardos e indígenas — TEC-INFO"* — com a Modalidade como **escolha**, e nenhum caminho
  normativo no HTML entregue (`FR-019` da `004`, `FR-171`).
- **A recusa que prova a `FR-161`:** alterar só a linha da `PPI` de `20` para `18` foi recusada já na
  criação do ato — *"O conteúdo que esta Retificação produz possui erros impeditivos: O quadro de
  vagas do Perfil 'TEC-INFO' soma 78 e o Perfil declara 80 vagas imediatas — diferença de 2."*
- **Os dois movimentos como um ato só:** a mesma alteração **com** o total `80 → 78` passou. As duas
  Alterações declaradas foram, literalmente:

  ```
  REPLACE /profiles/id=…/immediateVacancies                          80 → 78
  REPLACE /profiles/id=…/vacancyTable/id=c1b8d7e6-…/immediateVacancies  20 → 18
  ```

  A linha é endereçada **por identidade**, e nunca por posição (`FR-170`).
- Publicada, as duas versões consolidadas coexistem: a anterior com `56 / 4 / 20` e total `80`, a
  vigente com `56 / 4 / 18` e total `78`. **Nenhuma outra linha mudou, e nada foi recalculado**
  (`FR-162`, `FR-173`, `SC-049`, `D-007`).

### Percurso 4 — O Edital grande (`US4`, `SC-052`)

Não foi percorrido à mão: montar sete polos pela tela repetiria, sete vezes, o que os três primeiros
percursos já provaram. A medida está em teste, que é onde ela não envelhece —
`tests/interface/test_compor_quadro.py::test_sete_perfis_de_tres_modalidades_pedem_no_maximo_vinte_e_oito_campos`
conta **28** campos digitáveis em 7 × 3, e nenhum deles é rótulo, código ou denominação.

---

## 4. O que fica registrado, e não vira escopo

- **A lacuna da `R-006` continua aberta.** No Edital que declara uma Modalidade chamada "Ampla
  concorrência", seguir a `FR-176` deixa essa Modalidade sem linha e o quadro nunca fica completo:
  a igualdade da `FR-161` não roda ali. O limite superior da `FR-177` roda e pega a direção
  perigosa; o que sobra é o quadro que soma **menos** do que o total nesse formato. As duas saídas
  que fechariam o resto estão nomeadas na `research.md`, com o custo de cada uma, e a escolha é do
  usuário. Verificado por
  `tests/interface/test_compor_quadro.py::test_a_igualdade_nao_roda_onde_uma_modalidade_fica_sem_linha`.
- **A recusa da referência cruzada não ancora no controle.** Quando a linha aponta Modalidade de
  outro Perfil, ela não corresponde a nenhuma das linhas oferecidas — nem por identidade, nem por
  recorte —, e a mensagem fica no resumo. O texto nomeia o caso com precisão, e inferir a linha
  seria adivinhar; fica como registro.
- **A emissão do snapshot cresce com o número de Perfis, e não por causa do quadro.** Medido: 16
  consultas com um Perfil e 38 com sete. O quadro entra no `prefetch_related` e custa **uma**
  consulta em qualquer dos dois casos — o crescimento vem de `profile.modalidades.order_by("code")`,
  que refaz a consulta a cada Perfil e é anterior a esta feature. Verificado por
  `tests/integration/publicacoes/test_quadro_na_publicacao.py::test_a_emissao_de_sete_perfis_nao_acrescenta_consulta_por_perfil`.
- **A página pública da seleção não exibe o quadro.** Nenhum requisito o pede — a `FR-169` fala do
  documento publicado —, e a `§7` não pôs a apresentação no portal em escopo. Fica como pergunta
  para quem decidir a próxima feature de transparência.
