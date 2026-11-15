# Implementation Plan: O polimento das telas do candidato na verificação por vídeo

**Branch**: `claude/174-polimento-da-verificacao-do-candidato`, sobre a `main` em `499491be` | **Date**:
2026-11-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/174-polimento-da-verificacao-do-candidato/spec.md`, com as
respostas Q-1 a Q-4 do usuário (as recomendações).

## Summary

Forma, e não comportamento. O que muda são dois templates, uma folha, o script da página e duas
frases do acompanhamento; o que se grava, o que se envia e as rotas ficam como estão.

1. **A página centrada.** Um envoltório `.jornada` nas três páginas da verificação (gravação,
   comprovante, situação sem gravação), com a coluna de 44rem da `172` e o cabeçalho "onde estou"
   (T-009). O título passa ao nome publicado da Etapa, e o texto fixo da Modalidade ao nome publicado
   dela, que a `Situacao` da `166` passa a carregar (T-007).
2. **O palco.** O teste da câmera e a gravação viram uma seção só, com dois estados (preparo e
   gravando) e **um** elemento de vídeo. "Continuar" já abre a câmera; a instrução, o "Passo N de 4",
   o selo e "Próximo" ficam sobre a prévia, empilhados na mesma célula de grade; no celular o palco é
   fixo e ocupa a altura visível. A página pede a tela acesa enquanto o palco está aberto (T-001 a
   T-006).
3. **As telas de antes e de depois.** Escolha em dois cartões iguais, preparo em três itens e "Quem vê
   o seu vídeo", idade em opções grandes com a recusa só depois do gesto (T-010, T-011); revisão com a
   duração e os megabytes; comprovante que abre pela confirmação, com os dados para conferência no fim
   e folha de impressão (T-012).
4. **O acompanhamento.** O selo provisório vira pílula com ícone em todas as situações (T-008); a linha
   do prazo e o rótulo novo da ação do passo saem de `portal/situacao.py`.
5. **A prova.** Uma jornada no navegador com a câmera simulada do Chromium mede as larguras, a altura do
   palco, os gestos e os elementos escondidos (T-015); as capturas antes e depois saem do mesmo
   roteiro; os aparelhos reais seguem o quickstart (T-016).

As decisões técnicas estão em [research.md](research.md) (`T-001` a `T-016`); a forma de cada tela, os
ganchos do script e as frases, em [contracts/telas.md](contracts/telas.md); o único acréscimo de dado,
em [data-model.md](data-model.md); o roteiro de verificação, em [quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2; templates do portal; JavaScript sem dependência, como o
`gravacao.js` de hoje.

**Primary Dependencies**: as do projeto; nenhuma nova. A jornada no navegador usa o grupo opcional
`navegador` (Playwright), que o CI já instala.

**Storage**: nenhuma migration, nenhuma tabela. O `M` da preparação continua o mesmo.

**Testing**: pytest contra PostgreSQL, com `DB_NAME` próprio, rodando os diretórios que a mudança toca;
`node --test` para as funções puras do script; a suíte inteira uma vez, no fim.

- unidade: as frases do degrau (`test_situacao_do_passo.py`), o filtro da duração, a modalidade na
  `Situacao`;
- portal: as páginas renderizadas (`test_verificacao_por_video.py`), a política de conteúdo, o
  vocabulário (`test_vocabulario_do_passo.py`);
- JavaScript: as funções puras novas (rótulo do passo, proteção contra toque duplo, megabytes, nível
  de fala) em `tests/javascript/gravacao.test.js`;
- guardiões de interface: classe com regra na folha, folha estática, larguras;
- navegador: `tests/navegador/test_jornada_do_video.py`, nova, com câmera simulada, a 375 e a 1280 px;
- humano: iPhone e Android reais, e três pessoas de fora da equipe técnica (SC-2655, SC-2658).

**Target Platform**: o portal do candidato, no Safari do iPhone, no Chrome do Android e nos três
navegadores principais do computador.

**Project Type**: aplicação web, backend com templates.

**Performance Goals**: nenhuma consulta a mais nas páginas da verificação nem no acompanhamento; o nome
da Modalidade sai do conteúdo vigente que a página já lê.

**Constraints**: CSP sem `unsafe-inline` e sem diretiva nova (FR-7889); `img-src 'self'`, por isso os
ícones são SVG no próprio HTML, e não `data:` na folha; nenhuma leitura da imagem (FR-7890); os
contratos e testes de envio da `166` sem mudança (FR-7887); tudo em português.

**Scale/Scope**: três templates, uma folha, um script, um módulo de frases; cerca de 15 telas medidas
em quatro larguras.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como a feature o cumpre |
|---|---|
| I. Linguagem ubíqua | o nome publicado da Etapa e da Modalidade no lugar de texto fixo; as frases da `166` e da `171` mantidas; termo técnico só em "Dados para conferência" |
| II. Integridade normativa e imutabilidade | nada do conteúdo publicado, do vídeo nem da trilha muda; o roteiro exibido é o da versão gravada (D-003) |
| III. Segurança, proteção de dados e auditoria | nenhuma leitura da imagem (FR-7890); a CSP e a `Permissions-Policy` iguais; nenhuma voz sintetizada que entraria no vídeo (D-006); as tomadas continuam só no aparelho |
| IV. Regras explícitas | o avanço só pelo gesto (D-001); a recusa só depois do gesto; o descarte quando a página some, como na `166` |
| V. Rastreabilidade e simplicidade | sem dado novo persistido; os testes da `166` como prova de que o envio não mudou; cada FR- com teste ou verificação nomeada |
| VI. Completude de jornada | do acompanhamento ao comprovante, no celular e no computador, demonstrado na jornada no navegador e em aparelhos reais |

**Gate: aprovado.** Nenhuma exceção.

**Re-check depois do desenho: aprovado.** O desenho acrescentou só um campo em memória (`Situacao.
modalidade`) e funções puras no script; nenhuma rota, permissão, tabela ou diretiva.

## Project Structure

### Documentation (this feature)

```text
specs/174-polimento-da-verificacao-do-candidato/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/telas.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/domain/alcance.py        # `nome_da_modalidade`, movida de portal/passo_da_etapa.py (T-007)
├── verificacao/application/
│   ├── disponibilidade.py           # `Situacao.modalidade` (T-007)
│   └── envio.py                     # contexto_do_titular preenche a modalidade
├── portal/
│   ├── passo_da_etapa.py            # passa a usar `alcance.nome_da_modalidade`
│   ├── situacao.py                  # o rótulo da ação e a linha do prazo do passo (T-008)
│   ├── verificacao.py               # o contexto das páginas (nomes, megabytes, teto)
│   ├── templatetags/                # `duracao_por_extenso` (T-012)
│   ├── templates/portal/
│   │   ├── acompanhamento.html      # o selo com ícone; a linha do prazo
│   │   ├── _icone.html              # novo: os ícones em SVG no HTML (T-008)
│   │   ├── verificacao.html         # a página inteira (T-001, T-009 a T-011)
│   │   └── verificacao_comprovante.html  # (T-012)
│   └── static/portal/
│       ├── portal.css               # o bloco da 166 reescrito; o selo provisório
│       └── gravacao.js              # o palco, a tela acesa, as funções puras novas
└── shared/static/shared/tokens.css  # `--controle-g` (D-007), depois do #564

backend/tests/
├── unit/portal/test_situacao_do_passo.py      # frases novas
├── unit/verificacao/test_modalidade_na_situacao.py  # novo
├── portal/test_verificacao_por_video.py       # as páginas renderizadas
├── portal/test_vocabulario_do_passo.py        # as frases novas na varredura
├── javascript/gravacao.test.js                # as funções puras novas
└── navegador/test_jornada_do_video.py         # novo: câmera simulada, medidas (T-015)

doc/polimento-da-verificacao-2026-11/          # capturas antes e depois e o script delas (FR-7893)
```

**Structure Decision**: o monólito existente; nenhum app novo, nenhuma rota nova.

## Ordem de entrega

Um PR, em quatro incrementos que se verificam sozinhos:

| Incremento | O que entra | Fecha |
|---|---|---|
| A | a composição centrada, o nome publicado, a recusa escondida, o acompanhamento (selo, prazo, ação) | US3, problemas 1, 2, 4 (a recusa) e 8 |
| B | a escolha, o preparo, a idade, as telas de saída | US4, problemas 3 e 4 |
| C | o palco: câmera ao continuar, instrução sobre o vídeo, "Próximo" no polegar, tela acesa, revisão e envio | US1, US2, US6, problemas 5, 6 e 9 |
| D | o comprovante e a impressão; as capturas; a jornada no navegador; os aparelhos reais | US5, problema 7, SC-2650 a SC-2659 |

O incremento C é o de maior risco (script e aparelhos) e não depende de B; A vem primeiro porque muda
a moldura de todas as telas.

## Complexity Tracking

Nenhuma violação a justificar.
