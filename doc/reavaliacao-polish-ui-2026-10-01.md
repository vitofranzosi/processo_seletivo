# Reavaliação do polish de UI/UX, depois da 055, da 056 e da 057

**Data:** 2026-10-01 · **Natureza:** reavaliação da
[auditoria de polish de 30/09](auditoria-polish-ui-2026-09-30.md) depois dos três lotes. Nada foi
implementado aqui.

> **Não vira escopo por estar escrito aqui.** O lote de resíduos proposto no §6 tem prompt próprio
> ([`058`](prompt/058-polish-residuos.md)); decidir se e quando rodá-lo é do usuário.

---

## 1. Protocolo

| Item | Valor |
|---|---|
| Commit avaliado | `39c9ec40` (`main`, merge do PR 246) |
| Lotes avaliados | `055` (PR 242), conversão dos comentários da folha (PR 244), `056` (PR 245), `057` (PR 246) |
| Banco | cópia de `ps_polish_audit`, o banco da auditoria, para as medidas serem comparáveis |
| Janela | 1280 × 900; passada pontual a 375 px na Lista de Editais e na Condução |
| Identidade | `ana.gestora` com todos os papéis |
| Método | as medidas da auditoria repetidas na tela renderizada; leitura da `verificacao.md`, do `research.md` e dos achados de cada spec |

**Sem medição nova** (o número vem da `verificacao.md` da spec): Revisão em `dl`, Requerimento do
portal, envio de documento do portal (D5), Visão Geral.

## 2. Resumo

**Dos 24 achados que entraram nos lotes, 19 estão atendidos e 5 parciais. Nenhum foi abandonado.**
O D3 saiu antes dos lotes, por ser do seed e não da interface.

- **O que mais melhorou:**
  - o assistente de composição: o stepper numa linha e o Conteúdo do Edital na largura do texto;
  - a hierarquia das ações do Edital e da Condução;
  - os números ambíguos do Corte e da Ocupação;
  - a matriz de Alocação.
- **O que ficou:** cinco metas parciais, três achados ainda abertos e **três problemas que a
  auditoria não tinha visto** (§5). O mais visível deles é o Processo com as ações irreversíveis
  preenchidas. O mais grave é a 375 px: ações da Lista inalcançáveis.
- **O teto de 120.000 caracteres deixou de apertar.** A página da distribuição foi de 119.953 para
  82.477 caracteres, com a conversão dos comentários da folha para `{% comment %}` (PR 244) e com
  o estilo de página da `057`.

## 3. Antes e depois, medido na tela

| Achado | Tela e medida | Auditoria (30/09) | Agora (01/10) | |
|---|---|---:|---:|---|
| G1 | Corte: faixa calculada | 12 itens numa fileira, número entre dois rótulos | 6 blocos, número sobre o rótulo | ✅ |
| G1 | Ocupação: os quatro números | `dl` de 70 px ao lado do título | 4 blocos, como na Convocação | ✅ |
| G2 | Inscrições do 51/2026: altura da linha | 70 px | **63 px** | ⚠️ |
| G8 | Filtro das Inscrições e da Distribuição: desnível entre controles | 21 e 22 px | 0, com o botão de 40 px | ✅ |
| T1 | Lista de Editais: altura da linha | 125 px | **82 px** | ✅ |
| T2 | Detalhe do Edital: ação cheia | Cancelar (vermelho) | Inscrições recebidas; Encerrar e Cancelar contornados, à parte | ✅ |
| T2 | Detalhe do Edital: "Quem atuou" | 515 px | **237 px** | ✅ |
| T2 | Condução: ações cheias | 4 empilhadas | 1 cheia + 3 secundárias em linha | ✅ |
| D2 | Condução, Corte, Ocupação: glossário | parágrafo antes da ação | "Termos desta tela", fechado | ⚠️ (32–53 px de ganho; meta ≥ 120) |
| T3 | Processo: Atenção | 6 caixas com faixa verde | lista com divisor e faixa âmbar | ✅ |
| T3 | Auditoria: altura média por evento | 97 px | **61 px** | ✅ |
| T3 | Distribuição: ficha de dois dados | 1.232 px | 433 px | ✅ |
| T4 | Alocação: largura da página / `thead` | 1.398 / 174 px | **1.280 / 127 px** | ✅ |
| G6 | Processo: h2 / h3 "Atenção" | 16 / 18,7 px | 18,4 / 16 px | ✅ |
| F7 | Comissão: Identificador institucional | 1.190 px | 320 px | ✅ |
| G7 | Comissão: alturas de controle | 35, 36 e 38 px | 40 px em todos | ✅ |
| D1 | Seleção (portal) sem sorteio: Cronograma abaixo das Vagas | 335 px | 0 | ✅ |
| F1 | Stepper do assistente | 174 px, 7 + 2 | **66 px**, uma linha | ✅ |
| F1 | Perfis: topo do h2 da etapa | y = 524 | y = 416 | ✅ |
| F2 | Cronograma: Início e Término | linhas diferentes | mesma linha | ✅ |
| F2 | Cronograma: cartão de Evento | ~230 px | **217 px** | ⚠️ (meta ≤ 150) |
| F2 | Etapas: cartão | 388 / 388 / 468 px | 296 / 296 / 376 px | ✅ |
| F3 | Conteúdo do Edital | 4.790 px, cartões de 1.232 | **2.875 px**, cartões de 719 | ✅ |
| F4 | Revisão: altura | 7.987 px | 8.326 px (+4%, dentro do teto de +10%) | ✅ |
| F8 | Revisão: números | "Peso: 2.0000", "20.0000%", "2014-06-09", "vaga(s)" | "Peso: 2", "20%", "09/06/2014", "2 vagas imediatas" | ✅ |
| F8 | Etapas: valor dos campos numéricos | "6.0000", "2.0000" | igual | ⚠️ |
| G5 | Portal: "Guardar e continuar depois" | `<button>` sem classe | `class="secundario"` (conferido no template) | ✅ |

## 4. Os parciais, e o que cada spec disse deles

- **G2 — Inscrições (055, D-021).** O padding de célula põe a linha numa linha só. A marca
  "⚠ CPF repetido neste Perfil" a devolve a duas, e no seed ela está nas cinco inscrições.
  **Decisão do usuário em 01/10/2026: a marca fica como está.** A linha que pede atenção fica em
  duas, e as demais já têm 39,5 px. O achado
  [achado-marca-de-cpf-repetido-alarga-a-lista.md](achado-marca-de-cpf-repetido-alarga-a-lista.md) é
  fechado com essa decisão.
- **F2 — cartão de Evento (056, D-006).** Pôr "Onde acontece" na primeira linha pede ~1.510 px numa
  faixa de 1.232. A geometria não comporta sem tirar campo, e tirar campo está fora do polish.
  **Aceito como está.**
- **D2 — glossário (057, D-020).** O ganho foi menor que a meta porque a faixa "abrir esta tela não
  pratica nada" ficou visível, por decisão do próprio prompt. **Aceito como está.**
- **F8 — o resto (057).** [achado-f8-textos-que-saem-da-tela.md](achado-f8-textos-que-saem-da-tela.md)
  separa duas coisas:
  - o que sai da tela e grava ato (`objeto_legivel`, `validation.py`, `ocupacao.html` l. 207): fica,
    porque mudar a grafia mudaria o que os atos gravam;
  - o que é só tela (plurais com parênteses em `distribuicao.html`, `matriculas.html`,
    `recurso.html`, `ocupacao_historico.html`) e o valor dos campos numéricos das Etapas: vai para
    a `058`.
- **G3 — coluna numérica (055, D-011).** Só a ordem do marco foi corrigida. Em `resultados.html` a
  tabela não tem `class="tabela"`, e a regra não pega
  ([achado-coluna-numerica-dos-resultados.md](achado-coluna-numerica-dos-resultados.md)). Vai para a
  `058`.

## 5. O que a auditoria não tinha visto

1. **Processo, "O que fazer agora": as ações irreversíveis estão preenchidas.** "Encerrar Processo"
   é verde cheio e "Cancelar Processo" é vermelho cheio, os dois ativos, logo acima do aviso de que
   estão impedidos. A causa está em `processo_detalhe.html`: a classe do botão segue a regra antiga
   (irreversível → `botao`, interrupção → `botao perigoso`), e o `hierarquia()` da `057`
   (`interface/acoes.py`) não é usado ali. É o mesmo defeito que o T2 corrigiu no Edital. A auditoria
   não rolou a tela até essa seção.
2. **375 px.** Confirma
   [achado-lista-e-conducao-a-375px.md](achado-lista-e-conducao-a-375px.md):
   - na Lista, a tabela de 570 px fica dentro de um cartão com `overflow:hidden`, e a coluna de ações
     (x de 343 a 595) é **cortada sem rolagem**;
   - na Condução, a página vai a 486 px.
3. **Menores.**
   - **Revisão:** cada bloco de `dl` tem a coluna de rótulos na largura do seu rótulo mais longo, e os
     valores de DOC-INFO e de TEC-LAB começam em posições diferentes (visto na captura, não medido).
   - **Ocupação e Sorteio:** o motivo que sucede um ato é campo de uma linha (1.232 px na Ocupação).
     Na Ordenação e no Corte, o mesmo motivo é área de texto de 3 linhas: o mesmo conceito com dois
     controles.
   - **Matrículas:** a `section.resumo` põe o título e a nota lado a lado. É o mesmo defeito do G1
     ([achado-resumo-na-secao-das-matriculas.md](achado-resumo-na-secao-das-matriculas.md)), fora da
     lista da `055`.

**Observação, sem proposta:** no Detalhe do Edital, a ação cheia é "Inscrições recebidas (0)",
mesmo com zero inscrições, enquanto a Lista esmaece o contador zero. É a regra de preferência da
`057` (D-002), aplicada sem olhar a contagem.

## 6. Inconsistências na documentação dos lotes

- `056`, D-003: diz que o grupo de ações volta ao fluxo abaixo de **48 rem**, e o PR e a folha usam
  **60 rem**.
- PR 246 (`057`): a descrição cita 83.444 caracteres para a página da distribuição, valor anterior à
  D-024. A `verificacao.md` registra 82.477.
- `057`: não registra o total da suíte completa depois da última correção (o teste do consolidado
  datado).

## 7. O lote de resíduos

Proposto como **[`058`](prompt/058-polish-residuos.md)**:
- os dois problemas novos (Processo e 375 px);
- os dois achados de uma linha (Matrículas e coluna numérica);
- o F8 que é só tela;
- os dois desalinhamentos menores (Revisão, e o motivo da Ocupação e do Sorteio);
- a correção das inconsistências do §6 que estão no repositório.

**Ficam fora, aceitos:**
- a marca de CPF (decisão do usuário);
- o cartão de Evento (geometria);
- o glossário (a faixa visível é decisão);
- os textos que gravam ato.
