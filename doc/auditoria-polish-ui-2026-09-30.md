# Auditoria de polish de UI/UX

**Data:** 2026-09-30 · **Natureza:** auditoria de acabamento — nada foi implementado.

> **Não vira escopo por estar escrito aqui.** É registro e proposta de priorização; decidir se, quando
> e em que lotes corrigir é do usuário.

---

## 1. Protocolo

| Item | Valor |
|---|---|
| Commit auditado | `c0f5ad3d` (`main`, merge do PR 239) |
| Branch | `claude/audit-recruitment-ui-polish-a1a41c` |
| Execução | nativa, `runserver` na porta 8060, com `INTERFACE_SELETOR_IDENTIDADE` e `PORTAL_IDENTIDADE_DEMO` |
| Banco | `ps_polish_audit`, exclusivo, `migrate` + `seed_demo` (mantido para a medição de depois) |
| Janela | 1280 × 900 |
| Identidades | `ana.gestora` com todos os papéis; `joana.avaliadora`; candidata `MARIA` do fixture (`m@ex.br`) |
| Método | tela renderizada, com larguras, alturas e posições medidas por JavaScript na própria página; leitura das duas folhas de estilo |

**Premissa.** É polish, não redesenho. Domínio, regras, campos, fluxos, permissões e arquitetura da
informação ficam como estão. O critério de corte de cada item foi: *se esta mudança sair da proposta,
a interface fica perceptivelmente pior?*

**O que não foi coberto:**
- a largura de celular (375 px) não foi percorrida de forma sistemática;
- a avaliação em rascunho (no seed todas estão concluídas);
- telas de recurso com dados (o seed tem zero recursos);
- as telas de sorteio;
- a prévia e o PDF — o PDF é o documento oficial e está fora do propósito de polish.

**Registros anteriores que esta auditoria toca:**
- [achado-numeros-da-ocupacao-espremidos.md](achado-numeros-da-ocupacao-espremidos.md) descreveu o
  sintoma da Ocupação; aqui está a causa (G1), que alcança também o Corte;
- [analise-ux-colecoes-repetidas-2026-09-29.md](analise-ux-colecoes-repetidas-2026-09-29.md) tratou
  os Perfis como mestre-detalhe e apontou o Cronograma como caso de densidade; F2 é essa densidade;
- [achado-grade-dos-cartoes.md](achado-grade-dos-cartoes.md) registrou que as linhas de campo não
  compartilham colunas; F6 e F7 não dependem dele e não o resolvem.

---

## 2. Resumo: respostas às 10 perguntas

1. **Telas já refinadas:** Minhas Etapas, Mesa do avaliador, Criar Processo, Resultado público,
   Minhas inscrições e, quase, a Visão Geral e a Vitrine.
2. **Ainda "formulário administrativo":** Conteúdo do Edital, Retificar, Revisão, Cronograma e o
   editor de Perfil.
3. **Desperdício de espaço:**
   - no assistente de composição, o conteúdo de cada etapa começa a 58% da altura da janela;
   - o Conteúdo do Edital tem 5,3 telas de rolagem, quase todas de caixas vazias;
   - caixas de largura total guardam dois ou três dados.
4. **Densidade excessiva:**
   - colunas de ações com 5 ou 6 botões iguais, que deixam cada linha com 125 px;
   - o Retificar tem 183 campos abertos ao mesmo tempo.
5. **O que deveria ficar lado a lado:** "Início" e "Término" no Cronograma, e as ações ↑ ↓ 🗑 de cada
   item junto ao título do item.
6. **Largura, espaçamento e hierarquia inadequados:**
   - padding de célula de tabela;
   - três alturas de botão;
   - títulos h3 maiores que h2;
   - campos curtos com 1.190 a 1.232 px de largura.
7. **Problemas globais:** a folha de estilo (tabelas, botões, controles, títulos, barra de filtro) e
   uma colisão de nome de classe.
8. **Problemas específicos:** Conteúdo do Edital, grade da página da seleção, alocação e o botão sem
   estilo do portal.
9. **Maior ganho com pouca mudança:** os itens 1 a 6 da matriz (§8).
10. **Execução sem over-engineering:** três lotes, sem tokens novos e sem componentes novos.
    Reaproveitar os padrões que já existem: `ul.resumo`, `details.como-preencher` e a lista de
    documentos da mesa do avaliador.

---

## 3. A folha de estilo, em números

Levantado nas duas folhas: `interface/templates/interface/base.html` (gestão) e
`portal/templates/portal/base.html` (portal).

- **Tokens.** `shared/_tokens.css.html` define só cores (17) e duas larguras (`--leitura:68ch`,
  `--pagina:96rem`). Não há token de espaçamento, tamanho de fonte, raio ou sombra.
- **Espaçamento.** A gestão tem 430 declarações de margin/padding/gap, com 30 comprimentos
  distintos; o portal, 26.
- **Tamanho de fonte.** 17 valores distintos na gestão e 15 em tela no portal. `visao_geral.html`
  acrescenta outros 7 e usa uma paleta cinza própria (17 hex fora dos tokens).
- **O que as duas folhas compartilham:** só o arquivo de tokens. Botões, campos, títulos e tabelas
  estão duplicados, com deriva. Nenhum nome de classe de botão coincide entre elas, e o mesmo nome
  significa coisas diferentes: `.situacao` é pílula na gestão e texto colorido no portal; `.codigo` é
  pílula verde na gestão e monoespaçado cinza no portal.
- **Caixas.** São ~34 classes que desenham caixa com borda ou fundo na gestão e ~16 no portal. O
  `<fieldset>` sem classe herda borda global, e dentro de `form.confirmar` vira caixa dentro de caixa.

**Não se recomenda** consolidar tokens de espaçamento agora. É o tipo de mudança que mexe em tudo e
não melhora nenhuma tela em particular. Os lotes do §9 pedem só três valores novos: uma escala de
títulos, uma altura de controle e o padding de célula.

---

## 4. Ajustes globais de polish

### G1 — A classe `.resumo` quebra a Ocupação e o Corte

- **Tela:** Ocupação de vagas; Corte e progressão.
- **Problema observado:**
  - `.resumo` é a classe dos blocos de números (`display:flex;flex-wrap:wrap`, base da gestão, l. 88).
  - `ocupacao.html` (l. 50) a aplica numa `<section>`. Título, números e links viram itens de uma
    mesma linha flex, e o `dl.meta` dos números fica com **70 px**, empilhado ao lado do h2.
  - `corte.html` (l. 98) e `corte_historico.html` usam `dl.resumo`. A faixa calculada lê como
    "Alvo declarado 2 Alvo apurado 2 Suplentes 1 Progridem 3 Ficam fora 1 Última posição alcançada 2º",
    numa linha só.
- **Por que prejudica:**
  - No Corte, cada número fica equidistante do rótulo da esquerda e do da direita, então a leitura é
    ambígua — numa tela de ato irreversível.
  - A Convocação mostra os mesmos quatro números da Ocupação (Publicadas, Efetivas, Ocupadas,
    A ocupar) de forma correta, como `ul.resumo`.
- **Ajuste sugerido:** usar `ul.resumo` nas duas telas, como a Convocação faz, e trocar a classe da
  `<section>`.
- **Tipo:** sistêmico na raiz, duas telas. **Impacto:** alto. **Esforço:** baixo. **Risco:** baixo.

### G2 — Padding de célula de tabela

- **Tela:** todas as tabelas da gestão.
- **Problema observado:**
  - A regra global `th,td{padding:.7rem 1.25rem}` (base da gestão, l. 117) dá 11 × 20 px por célula.
  - Nas Inscrições, são 7 colunas × 40 px, ou seja 280 px só de padding.
  - Por isso protocolo, nome, perfil e data quebram em duas linhas, e cada linha fica com **70 px**.
  - A tabela de resultado do portal usa `.5rem .75rem` e fica com 41 px.
- **Por que prejudica:** menos da metade das linhas cabe na tela, e o olho costura pedaços de texto.
- **Ajuste sugerido:** usar `.5rem .75rem` como padrão global, igual ao portal.
- **Tipo:** sistêmico. **Impacto:** alto. **Esforço:** baixo. **Risco:** baixo.

### G3 — Números alinhados à esquerda

- **Tela:** ordem do marco (e demais tabelas com colunas numéricas).
- **Problema observado:**
  - Na ordem calculada do marco, a pontuação aparece como "26", "22", à esquerda.
  - No resultado do portal, a mesma coluna fica à direita e com vírgula ("26,00").
  - Coluna numérica tem cinco grafias hoje: `.numero`, `.num`, `td.numero`, as classes da Visão Geral
    e o `td:last-child` do portal.
- **Por que prejudica:** comparar números desalinhados é mais lento, e a mesma informação fica com
  duas aparências.
- **Ajuste sugerido:** uma classe só para coluna numérica, alinhada à direita.
- **Tipo:** sistêmico. **Impacto:** médio. **Esforço:** baixo. **Risco:** baixo.

### G4 — Três alturas de botão

- **Tela:** toda etapa do assistente e toda confirmação.
- **Problema observado:**
  - `.acao` tem 25 px, `.botao` 36 px e `.botao.secundario` 38 px.
  - A diferença entre os dois últimos é a borda de 1 px que só o secundário tem (base da gestão,
    l. 708).
  - Na barra de navegação do assistente aparecem lado a lado: ‹ Voltar com 25 px, Salvar rascunho
    com 38 px e Avançar com 36 px.
- **Por que prejudica:** desalinhamento visível em toda etapa do assistente e em toda confirmação.
- **Ajuste sugerido:** a mesma caixa para primário e secundário (borda de 1 px da cor do fundo no
  primário). Em barras de ação, `.acao` passa a ter a altura dos demais botões.
- **Tipo:** sistêmico. **Impacto:** alto. **Esforço:** baixo. **Risco:** baixo.

### G5 — A ação única da tela aparece como o elemento mais fraco

- **Tela:** Matrículas, Inscrições, Distribuição, Comissão, Convocação, Requerimento (portal).
- **Problema observado:**
  - A única ação da tela é um `.acao` de 25 px em "Ver o que sairá vazio" (Matrículas), em
    "Filtrar" (Inscrições, Distribuição, Comissão) e em "Chamar uma pessoa da fila".
  - No portal, "Guardar e continuar depois" é um `<button>` **sem classe** (`requerimento.html`,
    l. 204).
  - Ele renderiza como botão nativo do navegador (Arial 13 px, borda *outset*), ao lado do principal.
- **Por que prejudica:** contradiz a hierarquia, e o botão do portal parece defeito.
- **Ajuste sugerido:**
  - regra: a ação principal de uma tela nunca é `.acao`;
  - o botão do portal recebe `class="secundario"`.
- **Tipo:** padrão. **Impacto:** alto. **Esforço:** baixo. **Risco:** baixo.

### G6 — Títulos fora de escala

- **Tela:** Convocação, Processo, Revisão, Retificar.
- **Problema observado:**
  - Não há regra global para h3, então ele herda 1.17em (18,72 px) e fica **maior que o h2**
    (16 a 18,4 px) na Convocação e no Processo.
  - No Processo, "Atenção" é h3 com 18,72 px e o h2 da mesma página tem 16 px.
  - Na Revisão, dois h2 irmãos têm 16 e 18,4 px.
  - Só o Retificar põe o h2 em caixa-alta.
- **Por que prejudica:** a hierarquia visual contradiz a do documento.
- **Ajuste sugerido:** escala global h1/h2/h3 (1,6 / 1,15 / 1 rem). Remover as sobreposições por
  contêiner que só mudam o tamanho.
- **Tipo:** sistêmico. **Impacto:** médio. **Esforço:** baixo. **Risco:** baixo.

### G7 — Alturas de controle desiguais

- **Tela:** Visão Geral, Requerimento (portal), Comissão.
- **Problema observado:**
  - Na Visão Geral, text e search têm 38 px e select tem 40 px.
  - No Requerimento do portal, 39 e 41 px **na mesma linha**.
  - Na Comissão, 35, 36 e 38 px na mesma tela.
  - A causa são duas regras de padding na gestão: `.campo input` com `.5rem` e a lista global de
    tipos com `.55rem`.
- **Por que prejudica:** linhas de formulário ficam tortas.
- **Ajuste sugerido:** uma `min-height` única para input e select.
- **Tipo:** sistêmico. **Impacto:** médio. **Esforço:** baixo. **Risco:** baixo.

### G8 — Três barras de filtro diferentes

- **Tela:** Inscrições, Distribuição, Comissão, Visão Geral, Vitrine.
- **Problema observado:**
  - `.filtros` usa `align-items:flex-end` com o texto de ajuda sob o campo de busca.
  - Na Distribuição, o select fica em y=1126 e o input em y=1104 (22 px de desnível).
  - "Filtrar" (`.acao`, 25 px) flutua entre os dois.
  - A Visão Geral joga o checkbox e o botão para uma segunda linha.
  - A Vitrine já resolve bem: rótulos no topo e botão da altura dos controles.
- **Por que prejudica:** é a primeira coisa que o operador usa em toda lista.
- **Ajuste sugerido:** adotar o desenho da Vitrine e tirar a ajuda de dentro da linha (ou reduzi-la
  a placeholder).
- **Tipo:** padrão. **Impacto:** médio. **Esforço:** baixo. **Risco:** baixo.

---

## 5. Formulários e composição

### F1 — Stepper do assistente em duas linhas

- **Tela:** assistente de composição, todas as etapas.
- **Problema observado:**
  - O stepper de 9 etapas usa `flex:1 1 160px` com wrap e vira 7 + 2.
  - As duas últimas etapas ficam com **613 px** cada, e o stepper soma 174 px de altura.
  - Somados trilha, h1, subtítulo e aviso de origem (96 px), o conteúdo da etapa começa em
    **y = 524 de 900**.
  - Em Perfis, a tabela só começa em y = 755.
- **Ajuste sugerido:** stepper numa linha só (9 colunas de ~130 px e ~56 px de altura), mantendo o
  status em texto. Sobe ~120 px em todas as etapas.
- **Tipo:** padrão. **Impacto:** alto. **Esforço:** baixo. **Risco:** baixo.

### F2 — Coleções em caixas

- **Tela:** Cronograma, Etapas de Avaliação, Documentos exigidos, Modalidades.
- **Problema observado:**
  - Cada item é um `fieldset.linha` com uma **linha inteira só para ↑ ↓ 🗑** (~60 px vazios por
    item).
  - A legenda é genérica ("MODALIDADE DE CONCORRÊNCIA", repetida em todo item).
  - No Cronograma, **Início e Término ficam em linhas diferentes**.
  - A Descrição (obrigatória, e truncada) tem 258 px, enquanto "Onde acontece" (opcional,
    geralmente vazio) tem 436 px.
- **Ajuste sugerido:**
  - ações do item no canto da legenda;
  - a legenda leva o identificador do item ("Evento 1 — Inscrições"), como o Retificar já faz;
  - no Cronograma: Tipo, Descrição (flexível), Início e Término numa linha; "Onde acontece" embaixo.
- **Tipo:** padrão. **Impacto:** alto. **Esforço:** médio. **Risco:** médio (`remocao.js` e a
  ordenação localizam os botões; há testes de fragmento).

### F3 — Conteúdo do Edital

- **Tela:** etapa Conteúdo do assistente.
- **Problema observado:**
  - 22 caixas de 1.232 px com textarea de 685 px, então 45% de cada caixa fica vazio à direita.
  - As 17 seções vazias têm 171 px cada.
  - As 5 seções geradas têm de 121 a 139 px só para dizer "composta automaticamente".
  - A página soma **4.790 px, ou 5,3 telas**.
- **Ajuste sugerido:**
  - caixa na largura do texto (`--leitura`);
  - textarea vazia com 2 ou 3 linhas;
  - seção gerada em uma linha só;
  - "(VAZIA — NÃO SAI NO DOCUMENTO)" vira um marcador curto.
- **Tipo:** local. **Impacto:** alto. **Esforço:** baixo. **Risco:** baixo.

### F4 — Revisão em texto corrido

- **Tela:** etapa Revisão do assistente.
- **Problema observado:** 8,9 telas de "Rótulo: valor" em texto corrido.
- **Ajuste sugerido:** usar o mesmo `dl` em grade de "Dados da inscrição" (rótulo numa coluna, valor
  na outra).
- **Tipo:** local. **Impacto:** médio. **Esforço:** baixo. **Risco:** baixo.

### F5 — Texto longo em campo de uma linha

- **Tela:** Perfil, Documentos exigidos, Retificar.
- **Problema observado:**
  - "Descrição" do Perfil é input de 386 px, e o texto sai truncado.
  - No Retificar, Título, Descrição e **Declaração do Requerimento** são inputs de 312 px.
  - "Instrução ao candidato" é input de 499 px.
  - No Compor, a mesma Descrição do Edital é textarea.
- **Ajuste sugerido:** o mesmo campo usa o mesmo controle nas duas telas, e texto longo vira
  textarea de 2 linhas.
- **Tipo:** padrão. **Impacto:** médio. **Esforço:** baixo. **Risco:** médio (a detecção de
  alteração do Retificar lê pelos nomes, que não mudam).

### F6 — Retificar e Compor desenham a mesma entidade de jeitos diferentes

- **Tela:** Retificar, comparado ao Compor.
- **Problema observado:**
  - No Retificar, o Perfil começa por "Requisitos → Modalidade AC → Denominação".
  - No Compor, começa por "Código → Denominação → Localidade".
  - Os botões "Aplicar aos demais Perfis" têm 38 px no Retificar e 25 px no Compor.
- **Ajuste sugerido:** alinhar a ordem dos campos do Retificar à do Compor.
- **Tipo:** padrão. **Impacto:** médio. **Esforço:** médio. **Risco:** médio.

### F7 — Largura sem relação com o conteúdo

- **Tela:** Comissão, Requerimento (portal), Anexos.
- **Problema observado:**
  - Na Comissão, "Identificador institucional" (~20 caracteres) e Nome têm **1.190 px**, enquanto a
    Função, logo abaixo, tem 685 px.
  - No Requerimento do portal:
    - **Telefone celular tem 1.232 px**;
    - a faixa de renda e o nome da mãe/pai também têm 1.232 px;
    - a UF fica sozinha numa linha.
  - No Anexos, o arquivo tem 1.190 px e o rótulo 685 px.
- **Ajuste sugerido:**
  - campo curto por padrão;
  - `.largo` só para nome e logradouro, com limite de ~40 rem.
- **Tipo:** padrão. **Impacto:** médio. **Esforço:** baixo. **Risco:** baixo.

### F8 — Números e datas fora do padrão pt-BR

- **Tela:** Revisão, campos numéricos, Retificar, Supervisão.
- **Problema observado:**
  - Valores como "Peso: 2.0000", "Nota mínima: 6.0000", "20.0000%" e "versão 2014-06-09".
  - Campos numéricos mostram "2,0000".
  - "vaga(s)" aparece em mais de 8 lugares (`revisao.py`, `retificacao.py`, `supervisao.py`,
    `conducao_do_marco.py`).
- **Ajuste sugerido:** um formatador único — vírgula, sem zeros à direita, dd/mm/aaaa e plural
  correto. Conferir o renderizador do PDF à parte, porque o PDF é o documento oficial.
- **Tipo:** sistêmico. **Impacto:** médio. **Esforço:** médio. **Risco:** baixo.

---

## 6. Tabelas e coleções

### T1 — Coluna de ações da Lista de Editais

- **Tela:** Processos Seletivos (lista inicial da gestão).
- **Problema observado:**
  - A coluna "O que posso fazer" (384 px) tem 5 ou 6 botões de mesmo peso, e cada linha fica com
    **125 px**.
  - "Cancelar" fica sozinho numa terceira linha.
  - Contadores "(0)" vão dentro do rótulo do botão.
  - O título repete o número que a coluna ao lado já mostra.
- **Ajuste sugerido:**
  - ações frequentes primeiro;
  - Encerrar e Cancelar agrupados no fim e separados;
  - rótulos curtos ("Inscrições (7)");
  - contador zero esmaecido.
- **Tipo:** padrão. **Impacto:** alto. **Esforço:** médio. **Risco:** baixo.

### T2 — Hierarquia de ações no Detalhe do Edital e na Condução

- **Tela:** Detalhe do Edital; Condução do marco.
- **Problema observado:**
  - No Detalhe, 7 botões ficam empilhados, um por linha.
  - **Cancelar é o único preenchido**: o gesto destrutivo e excepcional é o elemento mais forte da
    tela.
  - "Quem atuou" tem 515 px de altura para ~160 px de conteúdo, esticado pela coluna vizinha.
  - Na Condução, 4 botões primários ficam empilhados.
- **Ajuste sugerido:**
  - grupo de ações com uma primária e as secundárias em linha;
  - destrutivas separadas e **só contornadas**;
  - `align-items:start` nas colunas.
- **Tipo:** padrão. **Impacto:** alto. **Esforço:** baixo. **Risco:** baixo.

### T3 — Caixa dentro de caixa

- **Tela:** Processo, Auditoria, Detalhe da inscrição, Distribuição, Minha etapa.
- **Problema observado:**
  - No Processo, a seção "Atenção" tem 6 cartões com borda dentro de um cartão, e com **faixa verde**
    (a cor de sucesso) para itens de atenção.
  - Na Auditoria, cada evento é um cartão de ~97 px.
  - No Detalhe da inscrição, os documentos apresentados ocupam um cartão de largura total cada.
  - Na Distribuição e na Minha etapa, fichas de 1.232 px guardam 2 dados.
- **Ajuste sugerido:**
  - listas com divisor no lugar dos cartões;
  - faixa âmbar para atenção;
  - documentos no formato da mesa do avaliador, que é o mesmo conceito e já é melhor;
  - fichas na largura do conteúdo.
- **Tipo:** padrão. **Impacto:** médio. **Esforço:** baixo. **Risco:** baixo.

### T4 — Matriz de Alocação por Etapa

- **Tela:** Alocação por Etapa.
- **Problema observado:**
  - Com 9 Etapas, a **página** inteira rola na horizontal: 1.398 px numa janela de 1.280.
  - O cabeçalho da matriz tem 174 px, com 5 elementos por coluna, e "01/2026" se repete 3 vezes.
  - A rolagem é uma decisão registrada no comentário de `.distribuicao-moldura` (base da gestão,
    l. 433–446), para manter o cabeçalho fixo.
  - Com 5 Editais, a matriz chega a ~2.300 px.
- **Ajuste sugerido:** manter a decisão e estreitar as colunas — número do Edital como linha de grupo
  e controles do cabeçalho mais compactos.
- **Tipo:** local. **Impacto:** médio. **Esforço:** médio. **Risco:** baixo.

---

## 7. Telas específicas

### D1 — Página da seleção reserva a área do sorteio

- **Tela:** página da seleção, no portal.
- **Problema observado:**
  - A grade reserva a área "sorteio" mesmo quando não há sorteio (base do portal, l. 254).
  - Por isso o Cronograma começa **335 px** abaixo do topo do corpo (y = 819 contra 484).
- **Ajuste sugerido:** retirar a área quando não houver sorteio.
- **Impacto:** médio. **Esforço:** trivial. **Risco:** baixo.

### D2 — Glossário repetido antes da ação

- **Tela:** Marco, Condução, Corte, Ocupação, Convocação e Matrículas.
- **Problema observado:** o mesmo glossário ("Recorte é…, Faixa é…, Geração é…") aparece nas seis
  telas antes da ação, somando ~150 a 200 px.
- **Ajuste sugerido:** levar o glossário ao `details.como-preencher`, que já existe, e manter só a
  faixa "não pratica nada".
- **Impacto:** médio. **Esforço:** baixo. **Risco:** baixo a médio (há testes de vocabulário).

### D3 — Número do Edital repetido no cabeçalho

- **Tela:** Detalhe, Compor, Auditoria, Supervisão, Vitrine.
- **Problema observado:**
  - "Edital 01/2026" aparece no h1 e de novo no subtítulo.
  - Na Auditoria, o subtítulo lê **"Edital 51/2026 — Edital 51/2026 — seleção concluída"**.
  - Parte vem do título do seed, que já começa com o número.
- **Ajuste sugerido:** confirmar com Editais reais antes de decidir. Se a convenção se confirmar, uma
  forma canônica de cabeçalho.
- **Impacto:** médio. **Esforço:** baixo. **Risco:** baixo.

### D4 — Anexos com três larguras

- **Tela:** etapa Anexos do assistente.
- **Problema observado:**
  - O estado vazio tem 685 px, o formulário 1.232 px e a navegação 685 px.
  - Por isso "Avançar" fica no meio da tela, e não na borda direita como nas outras etapas.
- **Ajuste sugerido:** as mesmas larguras das outras etapas.
- **Impacto:** baixo. **Esforço:** trivial. **Risco:** baixo.

### D5 — Envio de documento no portal em duas linhas

- **Tela:** Sua inscrição (portal), bloco de documentos.
- **Problema observado:** "Escolher arquivo" e "Enviar" ficam em duas linhas, com a dica de formato
  depois de "Enviar".
- **Ajuste sugerido:** uma linha só — seletor, nome do arquivo e Enviar —, com a dica junto do
  seletor.
- **Impacto:** baixo. **Esforço:** baixo. **Risco:** baixo.

### Sem oportunidade material de polish

Minhas Etapas, Mesa do avaliador, Criar Processo, Resultado público, Minhas inscrições e Etapas de
Avaliação (tirando o F2).

### Observações estruturais (fora do polish, só registro)

- **Retificar:** 15,3 telas e 183 campos para um Edital de 2 Perfis, com tudo aberto ao mesmo tempo.
  O filtro "Só o que eu alterei" existe, mas não recolhe nada no começo.
- **Processo e Supervisão:** repetem o mesmo bloco de pulso, série de submissões e próximos marcos.
- **Perfis:** "Como a convocação é comunicada" e "Reverter vaga reservada" aparecem no bloco comum *e*
  de novo no editor de cada Perfil. É questão de domínio, não de acabamento.

---

## 8. Matriz de priorização

| # | ID | Problema | Abrangência | Impacto | Esforço | Risco | Recomendação |
|---|---|---|---|---|---|---|---|
| 1 | G1 | `.resumo` quebra Ocupação e Corte | 2 telas críticas | alto | baixo | baixo | Fazer já |
| 2 | G2 + G3 | Padding de célula e números à direita | todas as tabelas | alto | baixo | baixo | Fazer já |
| 3 | G4 + G5 | Alturas e pesos de botão; botão sem estilo no portal | global | alto | baixo | baixo | Fazer já |
| 4 | F1 | Stepper numa linha | 9 etapas | alto | baixo | baixo | Fazer já |
| 5 | F3 | Conteúdo do Edital compacto | 1 tela | alto | baixo | baixo | Fazer já |
| 6 | T2 | Hierarquia de ações no Detalhe e na Condução | padrão | alto | baixo | baixo | Fazer já |
| 7 | T1 | Coluna de ações da Lista de Editais | 1 tela, uso diário | alto | médio | baixo | Fazer |
| 8 | F2 | Coleções: ações na legenda e larguras do Cronograma | 4 etapas | alto | médio | médio | Fazer |
| 9 | G6 + G7 + G8 | Escala de títulos, altura de controle, barra de filtro | global | médio | baixo | baixo | Fazer |
| 10 | D1 | Grade da página da seleção | 1 tela pública | médio | trivial | baixo | Fazer |
| 11 | F7 | Larguras de campo por conteúdo | padrão | médio | baixo | baixo | Fazer |
| 12 | F4, D2, T3 | Revisão em `dl`; glossário recolhido; listas no lugar de caixas | padrão | médio | baixo | baixo | Fazer |
| 13 | F8 | Formatação pt-BR | sistêmico | médio | médio | baixo | Fazer |
| 14 | F5, F6 | Mesmo campo, mesmo controle; ordem do Retificar | padrão | médio | médio | médio | Avaliar |
| 15 | T4, D3, D4, D5 | Alocação, cabeçalhos, Anexos, envio de arquivo | local | baixo a médio | variado | baixo | Se sobrar |

---

## 9. Proposta de execução

Três lotes, uma spec cada.

1. **Folha e componentes** — itens 1 a 3, 9, 10 e 11 da matriz. Quase tudo é CSS; nos templates
   entram só G1, D1 e o botão do portal. Sem token novo além da escala de títulos, da altura de
   controle e do padding de célula.
2. **Assistente de composição** — itens 4, 5, 8 e 14, mais F4 e D4. É onde a sensação de "formulário
   administrativo" se concentra.
3. **Telas de operação** — itens 6, 7, 12, 13 e 15: hierarquia de ações, glossário, listas no lugar de
   caixas e formatação.

### Restrições que o código impõe

- **Teto do HTML da distribuição.** `tests/performance/test_escala_da_mesa.py:326` limita o **HTML
  inteiro** dessa página a 120.000 caracteres.
  - A folha da gestão ocupa ~81,5K disso.
  - Desses, ~36,8K são comentários `/* */`, enviados em toda página.
  - Regra nova precisa sair de regra antiga, ou alguém precisa decidir sobre esses comentários — o
    que é decisão do usuário, não deste registro.
- **Classe sem regra reprova.** Toda classe usada em template precisa de regra na folha
  (`tests/interface/test_acessibilidade.py:556`).
- **Sem `max-width` em px.** `tests/interface/test_larguras.py` proíbe `max-width` em px e exige que
  as duas larguras continuem nos tokens.
- **Peso dos botões de envio.** Todo botão de envio da gestão declara o seu peso
  (`test_todo_botao_de_envio_declara_o_seu_peso`).

### Como medir antes e depois

Repetir as medições desta auditoria no mesmo banco (`ps_polish_audit`), a 1280 × 900, antes e depois
de cada lote:

| Medida | Antes |
|---|---:|
| Altura de linha das Inscrições (Edital 51/2026) | 70 px |
| Altura de linha da Lista de Editais | 125 px |
| Topo do conteúdo da etapa Perfis | y = 524 |
| Topo da tabela da etapa Perfis | y = 755 |
| Conteúdo do Edital | 4.790 px (5,3 telas) |
| Revisão | 7.987 px (8,9 telas) |
| Retificar (Edital 01/2026) | 13.735 px (15,3 telas) |
| Editor de um Perfil aberto | 3.283 px (3,6 telas) |
| Largura da página da Alocação por Etapa | 1.398 px em janela de 1.280 |
| Desnível entre controles do filtro da Distribuição | 22 px |

Também passar por 375 px, que esta auditoria não cobriu.
