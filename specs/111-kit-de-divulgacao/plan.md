# Implementation Plan: Kit de Divulgação do Edital

**Branch**: `claude/gps-kit-divulgacao-viabilidade-63c68e` | **Date**: 2026-10-31 | **Spec**: [spec.md](spec.md)

**Input**: a [spec](spec.md), as decisões do [research](research.md) e o código experimental da
[POC](../../doc/poc-kit-de-divulgacao-2026-10-31/), que serve de referência, e não de código a copiar.

## Summary

Três leituras existentes descem para `publicacoes`, sem mudar de comportamento, para servir à ficha
sem que o portal importe a gestão (D-002). Uma leitura nova, `portal/ficha.py`, reúne o que a
página pública da seleção já calcula para um Edital publicado. Sobre ela trabalham:

- o kit textual, com formas fechadas;
- a peça 1080 × 1350, um modelo de caixas medido pela fonte do Edital, serializado em SVG e
  rasterizado em PNG pelo `resvg-py`;
- o pacote ZIP com manifesto.

A gestão ganha uma tela, uma ação no detalhe do Edital, uma capacidade própria e um evento de
exportação na trilha. Não há migration, tabela nova, gancho na publicação nem fila.

A entrega se faz em três incrementos (D-001):

- **A**: ficha, textos, tela, porta e rastreio;
- **B**: peça, depois da verificação do motor;
- **C**: pacote e galeria de revisão.

## Technical Context

| | |
|---|---|
| **Language/Version** | Python 3.13 |
| **Primary Dependencies** | Django 5.2, DRF (já presentes). **Nova, no incremento B, sujeita à D-007:** `resvg-py` (versão fixada) |
| **Storage** | PostgreSQL; **nenhuma tabela nova**. Exportação registrada em `auditoria.RegistroAuditoria` (D-005) |
| **Testing** | pytest + pytest-django contra PostgreSQL (`make test-pg`); `node --test` para o script de cópia |
| **Target Platform** | Gestão web (moldura da `076`), Linux na implantação |
| **Project Type** | Monólito Django (`backend/processo_seletivo`) |
| **Performance Goals** | Tela com prévia e ZIP abaixo de 2 s cada, num lote de 20 (SC-1057); POC: ~45 ms por PNG |
| **Constraints** | CSP `'self'` sem inline; nenhum `import PIL`; dado só publicado e vigente; determinismo |
| **Scale/Scope** | Dezenas de exportações por Edital; Editais de até ~70 Perfis |

## Constitution Check

| Princípio | Como o plano o cumpre |
|---|---|
| **I. Linguagem ubíqua** | "Perfil", "localidade", "vagas", "cadastro reserva" ditos como a página pública; nada de "curso" ou "polo" inferido (FR-3409) |
| **II. Integridade normativa** | A ficha deriva da versão vigente, a fonte autoritativa. Nenhum dado de divulgação vira dado independente: a manchete não é guardada no Edital (D-013). Fuso institucional para todo instante (FR-3415) |
| **III. Segurança e auditoria** | Negar por padrão: capacidade própria, não concedida (D-012). Escopo por unidade e 404 fora dela. Exportação registrada com ator, instante, versão e impressão (D-005). Nenhum dado pessoal. **P-2 registrada**: a política vigente de leitura do rascunho não muda aqui |
| **IV. Regras explícitas** | O modo do material é derivado por regra escrita (FR-3410). O que o sistema deriva aparece antes da exportação, com a origem (FR-3408), como pede o princípio sobre derivação visível |
| **V. Simplicidade e testes** | Uma dependência, justificada e verificada (D-007); sem fila, sem tabela, sem guarda de arquivo. Testes de autorização, de temporalidade (Retificação a vigorar), de coerência, de geometria e de determinismo |
| **VI. Jornada completa** | A comunicação sai do detalhe do Edital com os textos e a peça, pela interface, sem shell. A demonstração ponta a ponta está no [quickstart](quickstart.md) |

**Gates**: nenhuma violação. Uma ressalva vai no Complexity Tracking: a dependência nova.

## Project Structure

### Documentation (this feature)

```text
specs/111-kit-de-divulgacao/
├── spec.md
├── plan.md                 # este arquivo
├── research.md             # D-001 a D-021
├── data-model.md           # a ficha, o evento de exportação, a chave e a capacidade
├── contracts/kit.md        # rotas, métodos, respostas e cabeçalhos
├── quickstart.md           # demonstração ponta a ponta e galeria de revisão
├── tasks.md
├── rastreabilidade.md      # FR/SC/EC → tarefa → teste
├── revisao-critica.md      # a revisão independente e o que mudou por ela
├── verificacao-do-motor.md # criado na T024 (D-007)
└── checklists/
    ├── requirements.md
    └── seguranca-acessibilidade-grafica.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── publicacoes/
│   ├── application/selectors.py       # + retificacoes_a_vigorar, versoes_original_e_vigente,
│   │                                  #   prorrogacao, numeração das Retificações (movidas, D-002)
│   ├── domain/origem.py               # NOVO — origens/acrescimos, movidos de duvidas/ (D-002)
│   └── infrastructure/pdf.py          # apelido público de _quebrar (D-009)
├── duvidas/domain/origem.py           # passa a importar de publicacoes/domain/origem.py
├── interface/agenda.py                # importa retificacoes_a_vigorar de publicacoes
├── interface/relatorio_do_edital.py   # usa as leituras movidas; a regra em linha desaparece
├── portal/
│   └── ficha.py                       # NOVO — a ficha (D-002, D-003, D-004, D-018)
├── interface/
│   ├── kit_de_divulgacao.py           # NOVO — views: tela, prévia, exportações (D-012, D-014)
│   ├── kit_textos.py                  # NOVO — formas fechadas, Markdown e texto (FR-3412 a FR-3421)
│   ├── kit_peca.py                    # NOVO — modelo de caixas, regras de composição, SVG (D-008)
│   ├── kit_pacote.py                  # NOVO — PNG, manifesto, ZIP (D-006, D-007)
│   ├── kit_ativos/                    # NOVO — marca oficial + ORIGEM.md (D-010, P-3)
│   ├── acoes.py                       # ação "Kit de divulgação" em _navegacao
│   ├── identidade.py                  # capacidade material:gerar, papel comunicacao, descrição
│   ├── demonstracao.py                # ícone do papel; decisão sobre LIMIAR_DA_BUSCA (9 papéis)
│   ├── views.py                       # OPERACOES: rótulo de EXPORTAR_MATERIAL
│   ├── relatorio_trilha.py            # OPERACOES_QUE_NAO_CONTAM: EXPORTAR_MATERIAL
│   ├── urls.py                        # rotas do kit
│   ├── templates/interface/kit_de_divulgacao.html
│   ├── static/interface/telas/kit-de-divulgacao.css
│   └── static/interface/kit-de-divulgacao.js      # copiar (D-015)
└── config/settings/{base,development,test,production}.py  # KIT_DE_DIVULGACAO_PECA (D-010)

backend/tests/
├── integration/kit/                   # cenários de referência pelo corpus (fluxo real)
├── unit/kit/                          # textos, composição, geometria, manchete, impressão
├── interface/test_kit_de_divulgacao.py  # porta, ação, tela, cabeçalhos, CSP
├── fixtures/kit_referencias/          # SVG de referência por cenário (D-016)
├── test_vocabulario_do_kit.py         # varredura do material gerado (D-017)
└── javascript/kit-de-divulgacao.test.js
```

**Structure Decision**: o padrão da `099` — derivação e composição em `interface/`, ao lado de
`relatorio_do_edital.py`, `relatorio_pdf.py` e `diagramacao.py` — com uma exceção: a ficha fica no
portal (D-002), porque é leitura pública e a página da seleção é a referência dela.

## Fluxo de uma requisição

```
GET  /gestao/editais/<id>/kit-de-divulgacao/
     ator → obter_edital (escopo) → base material:gerar → publicado? (409) → agora
     ficha = portal.ficha.ler(edital, agora, host)              # só vigente; host local → sem link
     exportacoes = trilha EXPORTAR_MATERIAL do Edital (D-005) → por impressão ≠ atual → "de → para"
     sem material + exportações → faixa "não deve mais circular" (FR-3445)
     textos = kit_textos.compor(ficha)
     peca   = kit_peca.compor(ficha, manchete?) se a chave estiver ligada e o host for público
     render(tela, impressao=ficha.impressao)                    # não registra

GET  /gestao/editais/<id>/kit-de-divulgacao/previa.png?impressao=…[&manchete=…]
     mesma porta → ficha → impressão igual? (409) → peça → PNG (privado, inline)   # não registra

POST /gestao/editais/<id>/kit-de-divulgacao/exportar/<formato>   formato ∈ png|svg|md|txt|zip
     mesma porta → ficha → impressão igual? (409) → material → bytes
     → record_event(EXPORTAR_MATERIAL, previous_state=status, detalhe) → anexo
```

Cada requisição toma **um** `agora`, e toda a leitura usa esse instante.

## Integração com o que existe

| Ponto | Mudança | Risco | Contenção |
|---|---|---|---|
| `interface/acoes.py` (`_navegacao`) | Uma `Acao` nova, condicionada à capacidade, com motivo fora dos estados | A lista também monta ações | `com_relatorio`/detalhe-apenas, como a `099` (a lista não consulta) |
| `interface/identidade.py` | Papel e descrição novos | `DESCRICOES == PAPEIS` (`test_entrada_da_gestao`); `len(PAPEIS) == 8` (`tests/seguranca/test_vinculos.py:311`); o nono papel cruza `LIMIAR_DA_BUSCA = 8` (`demonstracao.py:40`) e faz aparecer a busca no seletor (FR-1695 da `075`); `ICONES` por papel; comentários de "oito papéis" em `navegacao.py` e `acessos.py` | Atualizar tudo na T004, e decidir lá se o limiar sobe para 9 ou se a busca passa a aparecer |
| Leituras movidas para `publicacoes` (D-002) | Três funções mudam de módulo | Chamadores da agenda, do relatório e da `070` | Mover com os chamadores no mesmo commit; as suítes da `070`, da `099` e da `101` provam que nada mudou |
| `pdf._quebrar` | Apelido público, sem renomear | Bytes do Edital | Fixtures de contrato do PDF verdes |
| Trilha | Operação nova | Rótulo cru; o evento como transição; atos normativos diluídos | `OPERACOES`, `previous_state` igual ao atual, `OPERACOES_QUE_NAO_CONTAM`; guardião `test_trilha_legivel.py` estendido a `interface/*.py` |
| Settings | Chave nova | `production.py` recusa chaves de desenvolvimento | Esta chave **não** é recusada: só é desligada por padrão |
| Inventário da `033` | Rotas novas com `Http404` | `test_gramatica_das_portas` | Linhas no inventário; módulo em `MODULOS_DE_VIEW` |
| Folhas e CSP | Folha de tela nova, script novo | Guardiões de folha, acessibilidade e CSP | Registro em `FOLHAS_DA_GESTAO`/bloco `estilo_da_pagina`; classes com regra |
| Dependência | `resvg-py` (incremento B) | Licença, manutenção, plataforma | D-007; `verificacao-do-motor.md` antes do `pyproject` |

O fluxo de publicação e de Retificação **não** muda (FR-3405). Em `publicacoes/application/` só entram
as leituras movidas para `selectors.py`, e nenhum comando é tocado.

## Riscos

| # | Risco | Prob. | Impacto | Resposta |
|---|---|---|---|---|
| R-1 | A marca oficial não chega | Média | O B fica sem produção | D-010: A em produção; B desligado |
| R-2 | `resvg-py` reprova na verificação | Baixa | Sem PNG | D-007: CairoSVG; senão só SVG |
| R-3 | Pessoa da comunicação vê rascunho, Retificação em curso e pendências | Alta (política vigente) | Exposição interna de ato ainda não publicado | P-2: nenhuma atribuição do papel antes da decisão do usuário |
| R-7 | Falso alarme ou alarme perdido de desatualização | Média | Faixa ignorada, ou peça errada circulando | Impressão versionada, com identidade e sem host (D-018); todas as exportações, e não só a última; desfecho (FR-3445) |
| R-8 | Mover leituras de lugar quebra quem as usa | Baixa | Regressão na agenda, no relatório ou na `070` | Mover sem mudar o corpo; as suítes das três features |
| R-4 | Template muda e quebra legibilidade em caso raro | Média | Peça ruim | Geometria + SVG de referência + galeria (D-016) |
| R-5 | A ficha diverge da página | Baixa | Duas verdades | Teste de equivalência (FR-3407) |
| R-6 | Custo de manutenção do template | Média | Tempo da equipe | Um template; sem variação por unidade; aprovação só por versão |

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples recusada porque |
|---|---|---|
| Dependência nova (`resvg-py`) | Rede social pede PNG, e nada no projeto rasteriza | Pillow é barrado pelo guardião e não desenha SVG; Chromium é desproporcional; rasterizador próprio é outro projeto (D-007) |
