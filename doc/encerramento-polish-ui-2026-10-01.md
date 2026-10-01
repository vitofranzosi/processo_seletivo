# Encerramento da série de polish de UI/UX

**Data:** 2026-10-01 · **Natureza:** verificação final e encerramento da série aberta pela
[auditoria de polish de 30/09](auditoria-polish-ui-2026-09-30.md). Nada foi implementado aqui.

> **A série está encerrada por decisão do usuário (01/10/2026).** O que ficou de fora está decidido
> ou registrado (§4), e não há lote pendente. Uma rodada nova, se houver, começa pelas telas que a
> série não cobriu (§5), com auditoria própria.

---

## 1. A série

| Documento ou spec | O que foi | PR |
|---|---|---|
| [Auditoria](auditoria-polish-ui-2026-09-30.md) | 24 achados de polish, matriz de prioridade, três lotes | 240 |
| [`055`](../specs/055-polish-folha-e-componentes/) | lote 1, a folha e os componentes | 242 |
| conversão dos comentários da folha | `/* */` → `{% comment %}`; a distribuição de 119.884 para 83.093 caracteres | 244 |
| [`056`](../specs/056-polish-assistente-de-composicao/) | lote 2, o assistente de composição | 245 |
| [`057`](../specs/057-polish-telas-de-operacao/) | lote 3, as telas de operação | 246 |
| [Reavaliação](reavaliacao-polish-ui-2026-10-01.md) | 19 atendidos, 5 parciais, 3 problemas novos | 247 |
| [`058`](../specs/058-polish-residuos/) | os resíduos: os problemas novos e os parciais que tinham correção | 248 |

Os prompts de sessão autônoma de cada lote estão em [`doc/prompt/`](prompt/), de
`055-polish-folha-e-componentes.md` a `058-polish-residuos.md`.

## 2. Protocolo da verificação final

| Item | Valor |
|---|---|
| Commit verificado | `62ed26dd` (`main`, merge do PR 248) |
| Banco | cópia de `ps_polish_audit`, o banco da auditoria, para as medidas serem comparáveis às de 30/09 |
| Janelas | 1280 × 900; e **375 px em 20 telas da gestão** |
| Método | a página servida, renderizada num `iframe` `srcdoc` da largura da janela, com `getBoundingClientRect` e `scrollWidth`; a Lista e a Condução também no viewport emulado (`scrollWidth` **e** `innerWidth`) |
| Identidade | `ana.gestora` com todos os papéis |

**Sem medição nova** (o número vem da `verificacao.md` da spec): a seção da Matrículas, que só
aparece com uma população escolhida (conferida no template), e o total da suíte.

## 3. O resultado

### Os 24 achados da auditoria

- **21 atendidos:**
  - folha e componentes: G1, G3, G4, G5, G6, G7, G8;
  - assistente de composição: F1, F3, F4, F5, F6, F7;
  - telas: D1, D4, D5;
  - telas de operação: T1, T2, T3, T4;
  - formatação: F8, na parte que é só tela.
- **3 como estão, por decisão:**
  - **G2**, a marca de CPF repetido: decisão do usuário em 01/10;
  - **F2**, o cartão de Evento: a geometria não comporta "Onde acontece" na primeira linha;
  - **D2**, o glossário: a faixa "não pratica nada" fica visível de propósito.
- **Fora da série:** o **D3** (número repetido no cabeçalho), que é do título do seed e não da
  interface.

### Os três problemas que a reavaliação encontrou

| Problema | Situação |
|---|---|
| Processo: Encerrar e Cancelar preenchidos | ✅ contornados, com "IRREVERSÍVEL" |
| Lista e Condução a 375 px | ✅ molduras com rolagem; páginas com 375 px |
| Revisão: valores desalinhados entre blocos | ⚠️ de 9 posições para 2 (a caixa de irreversíveis tem recuo próprio, `058` D-012) |
| Motivo de sucessão com dois controles | ✅ área de texto de 685 × 72 px nas quatro telas |

### Medidas finais, contra a auditoria

| Medida | 30/09 | 01/10 |
|---|---:|---:|
| Linha da Lista de Editais | 125 px | 82 px |
| Linha das Inscrições (com a marca de CPF) | 70 px | 63 px |
| Detalhe do Edital: "Quem atuou" | 515 px | 237 px |
| Detalhe e Condução: ações cheias | Cancelar; 4 empilhadas | uma, não destrutiva |
| Stepper do assistente | 174 px | 66 px |
| Perfis: topo do h2 da etapa | y = 524 | y = 416 |
| Conteúdo do Edital | 4.790 px | 2.875 px |
| Alocação: largura da página / `thead` | 1.398 / 174 px | 1.280 / 127 px |
| Revisão: números | "2.0000", "20.0000%", "2014-06-09" | "2", "20%", "09/06/2014" |
| Etapas: valor dos campos numéricos | "6.0000", "2.0000" | "6", "2" |
| Resultados: coluna de notas | à esquerda | à direita |
| 20 telas da gestão a 375 px | não medidas | todas com 375 px, nenhum controle recortado |
| HTML da distribuição (teto 120.000) | 119.953 | 82.498 (`058`) |
| Suíte contra PostgreSQL | 8.964 passando, 11 pulados | 9.129 passando, 11 pulados (`058`) |

**Sem regressão:** as medidas da `055`, da `056` e da `057` repetidas depois da `058` são as mesmas
da reavaliação.

## 4. O que fica, e onde está registrado

- **Decisões:**
  - [achado-marca-de-cpf-repetido-alarga-a-lista.md](achado-marca-de-cpf-repetido-alarga-a-lista.md),
    fechado pelo usuário;
  - [reavaliação](reavaliacao-polish-ui-2026-10-01.md) §4, com o cartão de Evento e o glossário.
- **Textos que gravam ato**, mantidos com "(s)" de propósito:
  [achado-f8-textos-que-saem-da-tela.md](achado-f8-textos-que-saem-da-tela.md), "Sai da tela"
  (`objeto_legivel`, `validation.py`, `ocupacao.html`).
- **Observação sem proposta:** no Detalhe do Edital, a ação cheia é "Inscrições recebidas (0)"
  mesmo com zero inscrições, enquanto a Lista esmaece o contador zero. É a regra de preferência da
  `057` (D-002). Se incomodar, é decisão de regra, não de acabamento.

## 5. O que a série não cobriu

A auditoria de 30/09 e as duas verificações percorreram a gestão (lista, Edital, Processo,
assistente, marco, distribuição, comissão, alocação, auditoria, Retificar) e parte do portal
(vitrine, página da seleção, inscrição, Requerimento, Minhas inscrições, resultado público).

**Ficaram de fora**, porque o `seed_demo` não produz esses estados ou porque a série não chegou
neles:
- o percurso logado do portal depois do envio: acompanhamento, comprovante, recurso, convocação;
- as telas de Recursos com dados (o seed tem zero recursos);
- as telas de Sorteio, além do campo de motivo;
- a avaliação em rascunho (no seed todas estão concluídas);
- a prévia e o PDF. O PDF é o documento oficial e está fora do propósito de polish.

Uma rodada nova rende mais ali, e pede montar esses estados antes de medir.
