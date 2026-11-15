# Implementation Plan: A orientação da verificação da autodeclaração

**Branch**: `claude/spec-orientacao-da-verificacao-8d618e`, sobre a `main` em `7d5c6ade` | **Date**: 2026-11-14
| **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/171-orientacao-da-verificacao/spec.md`

## Summary

Quatro peças pequenas, cada uma no lugar que já existe:

1. **O degrau no acompanhamento.** Um módulo novo, `portal/passo_da_etapa.py`, deriva da versão
   vigente que a view já lê e de duas consultas por Etapa restrita que alcança a inscrição o "passo"
   de cada uma: rótulo, porquê, período, consequência da ausência e, com a chave do vídeo, o estado da
   `166`. `situacao_da_inscricao` recebe esses passos e insere o degrau entre a eliminação e as
   classificadas. O cartão da `166` sai. Sem Etapa restrita que alcance a inscrição, nenhuma consulta
   a mais.
2. **O aviso do passo.** Uma quarta origem dos avisos, `PASSO`, no caminho da `RESULTADO` (prévia,
   gesto, motivos, despacho). Uma migration torna `marco_id` nulo para ela e acrescenta `etapa_id`, e
   os CHECKs passam a exigir um ou outro pela origem. Um quarto modelo inicial, com marca própria.
3. **As pendências no Centro e em Minhas atividades.** Fatos novos no `_Leitor` só para Etapa restrita
   (pareceres que faltam por membro, alcançados não avisados, participantes sem desfecho depois do fim)
   e para a Etapa que admite o vídeo (a encaminhar). As células entram em `situacoes_da_etapa`. Uma
   natureza nova, `AVISAR`, só para a pendência do aviso. A linha de avaliar ganha o fim do período.
4. **Vocabulário, advertência e cenário.** Uma varredura própria do candidato; uma advertência
   `WARNING` na validação de publicação; o cenário C18.

As decisões técnicas estão em [research.md](research.md) (`T-001` a `T-010`); os dados, em
[data-model.md](data-model.md); as frases, em [contracts/frases.md](contracts/frases.md); o roteiro,
em [quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2; templates do portal e da gestão, sem JavaScript novo.

**Primary Dependencies**: as do projeto; nenhuma nova.

**Storage**: PostgreSQL, com **uma** migration, `avisos/0004_origem_passo`:

- a origem `PASSO` nas choices e nos CHECKs;
- `aviso.marco_id` e `aviso.perfil_id` nulos e `aviso.etapa_id` novo, nulo, com o CHECK "`PASSO` ⇔
  `etapa_id` e não `marco_id`";
- `modelodeaviso.chave_inicial`, vazia por padrão, para o modelo inicial do passo.

Nenhuma tabela nova; o `M` da preparação continua **65**. A contagem de migrations por app (`avisos`)
sobe uma.

**Testing**: pytest contra PostgreSQL, rodando o diretório que a mudança toca (`make test-pg` com
`DB_NAME` próprio); a suíte inteira uma vez, no fim.

- unidade: o degrau (função pura, todos os estados e precedências), as células da Etapa, as frases;
- integração: o aviso do passo (universo, já avisado, CHECK, modelo inicial), os fatos do `_Leitor`,
  a participação com o conteúdo dado;
- interface: o acompanhamento renderizado, o Centro, Minhas atividades, a advertência na composição,
  a confirmação do aviso;
- vocabulário: a varredura nova;
- orçamento: o acompanhamento sem Etapa restrita custa o mesmo; os tetos de performance do Centro e
  de Minhas atividades continuam valendo;
- navegador: o percurso no cenário C18, no painel, com captura.

**Target Platform**: o monólito Django: portal, `/gestao/` e o despacho de avisos.

**Project Type**: aplicação web, backend com templates.

**Performance Goals**: zero consulta a mais no acompanhamento e no Centro quando nenhuma Etapa restrita
existe. Por Etapa restrita: até 6 consultas no acompanhamento (participação reduzida, parecer,
Resultado) e até 4 no Centro (carga por membro, avisados).

**Constraints**: a CSP sem `unsafe-inline`; tudo em português; `situacao_da_inscricao` continua pura;
nenhuma tela, rota de gestão ou natureza "verificação" nova.

**Scale/Scope**: Etapas de até milhares de inscrições; o degrau é por inscrição.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como a feature o cumpre |
|---|---|
| I. Linguagem ubíqua | "passo", "aviso do passo", o nome publicado da Etapa e da Modalidade; os termos técnicos ficam fora do texto fixo do candidato |
| II. Integridade normativa e imutabilidade | nada do conteúdo publicado muda; o degrau e as pendências são derivados; o aviso continua append-only (os gatilhos não mudam, só os CHECKs) |
| III. Segurança, proteção de dados e auditoria | o e-mail não traz a Modalidade (dado sensível); o aviso é gesto autorizado com prévia e trilha; a contagem por membro nunca traz sentido |
| IV. Regras explícitas | o degrau só afirma o que os dados mostram; a precedência é declarada; a advertência não impede |
| V. Rastreabilidade e simplicidade | sem estado persistido para o degrau e as pendências; uma migration; cada FR- com teste; o `CLAUDE.md` registra a quarta linha dos modelos de aviso |
| VI. Completude de jornada | candidato (acompanhamento e e-mail), comissão (Minhas atividades), presidência (Centro e confirmação), demonstrados no cenário C18 |

**Gate: aprovado.** Nenhuma exceção. A coluna `chave_inicial` e o `etapa_id` são o mínimo para a
origem nova sem reaproveitar `marco_id` com outro significado (T-004, T-005).

**Re-check depois do desenho: aprovado.** O desenho não acrescentou tabela, natureza "verificação" nem
estado guardado.

## Project Structure

### Documentation (this feature)

```text
specs/171-orientacao-da-verificacao/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/frases.md
└── checklists/requirements.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── portal/
│   ├── passo_da_etapa.py          # novo: deriva os passos (T-001, T-002)
│   ├── situacao.py                # o degrau e a linha na convocação (T-003)
│   ├── views.py                   # acompanhamento: passa os passos; tira `verificacoes`
│   └── templates/portal/
│       ├── acompanhamento.html    # sai o include da 166
│       └── _verificacao_por_video.html  # removido
├── editais/domain/cronograma.py   # `periodo_da_etapa`, movido da 166 (T-002)
├── editais/domain/validation.py   # a advertência do nome (T-009)
├── resultados/application/prontidao.py  # `participa_da_etapa(conteudo=, modalidade=)` (T-001)
├── verificacao/application/disponibilidade.py  # usa `periodo_da_etapa`
├── avisos/                        # origem PASSO (T-004, T-005)
│   ├── domain/{nomes,variaveis,modelos_iniciais}.py
│   ├── application/{destinatarios,confirmar,comando,previa,modelos}.py
│   ├── models.py
│   └── migrations/0004_origem_passo.py
├── interface/
│   ├── andamento.py               # fatos e células da Etapa restrita (T-006, T-007)
│   ├── centro.py, conceitos.py    # a natureza AVISAR
│   ├── atividades.py              # `ate` na linha de avaliar (T-008)
│   ├── avisos.py, urls.py         # a confirmação do aviso do passo
│   └── templates/interface/{aviso_previa,aviso,avisos_do_edital,_atividade}.html
├── comissoes/application/selectors.py  # o fim do período no item da Atribuição (T-008)
└── treinamento/{catalogo,construcao}.py  # C18 (T-010)

backend/tests/
├── unit/portal/test_passo_da_etapa.py
├── portal/test_degrau_do_passo.py, test_vocabulario_do_passo.py
├── integration/avisos/test_aviso_do_passo.py
├── interface/test_pendencias_da_etapa_restrita.py
└── integration/treinamento/test_cenario_c18.py
```

**Structure Decision**: o monólito existente; nenhum app novo.

## Complexity Tracking

Nenhuma violação a justificar.
