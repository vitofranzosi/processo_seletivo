# Implementation Plan: Entrega documental controlada ao setor da formalização

**Branch**: `claude/gps-entrega-documental-627460` | **Date**: 2026-11-04 (revisto) | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), [diagnostico.md](diagnostico.md) e [data-model.md](data-model.md).

> **Este plano não autoriza a implementação.** Ele depende das quatro pendências bloqueantes da spec:
> a exceção à FR-069 da `009` e à FR-3606 da `115` (D-016), a definição interna (D-009), o acesso pela
> gestão de acessos (D-013) e o merge do PR #369.

## Summary

O setor que formaliza ganha uma página por Edital, **Documentos para formalização**. Ele chega a ela
com o papel Formalização **e** uma designação no Edital, com Perfis opcionais, os dois concedidos pela
gestão de acessos. A página lista os aptos (desfecho vigente da chamada mais recente) com os
documentos que a condução **definiu** para a formalização, de qualquer momento, e permite:

- visualizar e baixar um por vez, com registro;
- exportar por pessoa, por seleção ou por recorte, num ZIP com manifesto, prévia, confirmação,
  limite, atomicidade por pessoa, temporário sem nome e registro com hash.

Nada se guarda. O Documento Exigido e o conteúdo publicado não mudam. O molde é a `031`, e as fontes
são a `019`, a `009` e a `115`.

## Technical Context

**Language/Version**: Python 3.13, Django (o do repositório)
**Primary Dependencies**: nenhuma nova. `zipfile`, `tempfile` e `hashlib` da biblioteca padrão
**Storage**: PostgreSQL; a raiz privada existente, só leitura
**Testing**: pytest contra PostgreSQL (`make test-pg`); Playwright no grupo `navegador`
**Target Platform**: o monólito, atrás de nginx e gunicorn síncrono (5 workers, 120 s)
**Project Type**: web, monólito
**Performance Goals**: Cenário A em menos de 30 s; consultas constantes no número de pessoas
**Constraints**:
- nada persistido além do registro;
- nada pessoal em log ou URL;
- CSP sem inline;
- 404/403 pelo ponto único e pelo inventário da `033`;
- 400 MB por exportação;
- uma exportação por servidor de cada vez.

**Scale/Scope**: dezenas de aptos por Edital

## Constitution Check

| Princípio | Como o plano o cumpre |
|---|---|
| Publicação é ato imutável | Nada publicado muda: a definição fica fora do snapshot (FR-3657) |
| Nada é excluído | Quatro tabelas append-only. O pacote não é guardado |
| Negar por padrão | Definição vazia, papel não concedido, lista sem marcação, predicado com papel + designação + apto na mesma requisição |
| Verificação de escopo | Unidade do Edital = unidade ativa; Perfis da designação; 404 para fora do alcance, inclusive em POST forjado |
| Rastreabilidade | Eventos distintos; registro com ids, hashes, versão da definição e resultado |

A exceção à FR-069 da `009` é revisão de requisito de outra feature (D-016), e não violação da
Constituição.

## Project Structure

### Documentation

```text
specs/117-entrega-documental-controlada/
├── spec.md · diagnostico.md · plan.md · data-model.md · quickstart.md · tasks.md
└── checklists/requirements.md
```

### Source Code

```text
backend/processo_seletivo/
├── formalizacao/                         # app novo
│   ├── models.py                         # Definicao…, Designacao…, Revogacao…, Exportacao…
│   ├── migrations/0001_inicial.py        # tabelas + gatilhos
│   ├── domain/nomes.py                   # capacidade, recusas, situações, operações
│   ├── domain/autorizacao.py             # pode_acessar (predicado único)
│   ├── application/definir.py            # definição (condução)
│   ├── application/designar.py           # designar / revogar (gestão de acessos)
│   ├── application/conjunto.py           # aptos e conjunto (seletor único, em lote)
│   ├── application/exportar.py           # prévia, assinatura, geração, registro
│   └── infrastructure/pacote.py          # ZIP_STORED em TemporaryFile, hash numa passagem
├── interface/identidade.py               # papel em PAPEIS/DESCRICOES
├── interface/views_formalizacao.py       # módulo novo, em MODULOS_DE_VIEW
├── interface/acessos.py                  # tela de designação junto do vínculo
├── interface/navegacao.py                # Secao "Formalização"
├── interface/templates/interface/formalizacao_*.html
├── interface/telas/formalizacao.css
├── portal/arquivos.py                    # ArquivoIndisponivel (FR-3695)
└── seguranca/papeis.py                   # TABELAS_APPEND_ONLY + 4
```

**Structure Decision: um app novo, `formalizacao`.** A designação não é da comissão nem da `107`
genérica. A exportação não é da convocação, que é ato da seleção. O app **lê** `convocacao`,
`inscricoes` e `editais`, e não escreve neles. As views vão num módulo próprio, e não no `views.py`.

## Desenho

### 1. A definição (FR-3653 a FR-3660)

- **Tela**: na condução do Edital, *Documentos para a formalização*. É uma lista de todos os
  requisitos das versões publicadas, agrupados por momento, com caixa de seleção e motivo.
- **Aviso** quando o recorte do requisito é por modalidade (FR-3658).
- **Gravação**: `pode_gerir_comissao` sobre o Processo do Edital, e uma linha nova.
- **Leitura**: a mais recente.

### 2. Papel e designação (FR-3661 a FR-3668)

- **Papel**: `PAPEIS["formalizacao"] = {"formalizacao:acessar"}`. A tela da `107` já o oferece, porque
  oferece todo papel de `PAPEIS` (`interface/acessos.py:87`).
- **Designação**: na página da pessoa, em **Acessos**, uma seção *Editais da formalização*, visível
  quando ela tem o papel. Os passos de `designar(ator, pessoa, edital, perfis, motivo)`:
  - `require_permission(acesso:gerir, unidade do Edital)`;
  - recusa de autodesignação;
  - `select_for_update` na pessoa;
  - papel vigente;
  - Perfis do Edital;
  - linha nova;
  - trilha da unidade e do Edital.
- **Predicado**: `pode_acessar(ator, edital, inscricao=None)` → `ok` | `404` | `403(papel)`. É o
  **único** ponto de decisão das views e da exportação.
- **Leitura pela condução**: na condução, *Setor da formalização* lista as designações vigentes, sem
  ação (FR-3668).

### 3. O seletor (FR-3669 a FR-3674)

`aptos_com_conjunto(edital, perfis, definicao)`, em consultas por lote:

1. convocações do Edital → raiz da chamada → chamada mais recente por inscrição → vigente → desfecho
   vigente ∈ `DESFECHOS_QUE_INCLUEM`;
2. requisitos da definição vigente;
3. **convocação**: itens da lista das raízes escolhidas cujo `requisito_id` está na definição;
   conferência vigente; apresentação julgada; `fonte_do_arquivo`;
4. **inscrição**: `DocumentoSubmetido` das inscrições, cujo `requirement_id` está na definição;
5. **deduplicação** (FR-3659): o documento da inscrição que um item incluído aproveita sai pelo item;
6. situação por item e *última exportação* por pessoa.

`raiz_da_chamada`, `vigente_da_chamada` e `fonte_do_arquivo` ([#369]
`convocacao/application/documentos.py`) são reutilizadas. Se alguma for por linha, ganha variante em
lote **lá**, com teste.

### 4. A exportação (FR-3682 a FR-3698)

```text
POST alcance (pessoa | seleção[ids] | recorte[perfil])
  └─ pode_acessar para cada pessoa; qualquer 404 → recusa inteira
prévia (>1 pessoa) ─► compor → linhas, existência dos arquivos (os.stat), tamanhos,
                      assinatura sha256(pessoas, itens, hashes)          [só trilha]
confirma ─► pg_try_advisory_lock(hash do servidor) ou recusa "já está sendo gerada"
         ─► compor de novo; assinatura ≠ → 409 prévia defasada
         ─► Σ tamanhos > limite → recusa antes de ler
         ─► TemporaryFile()  (sem nome; O_TMPFILE no Linux)
         ─► por pessoa: cada fonte → SpooledTemporaryFile + sha256 numa leitura
              FileNotFoundError/OSError → INDISPONIVEL; hash ≠ → INTEGRIDADE + evento
              pessoa completa → copia as entradas ao ZIP (ZipInfo.date_time = envio)
         ─► manifesto.csv; sha256 do pacote ao fechar
         ─► ExportacaoDeFormalizacao(resultado) + evento
         ─► libera a trava
         ─► SEM_PACOTE: tela com o resultado; senão FileResponse(attachment, no-store)
```

**Por que a trava cobre a geração e não a transferência.** Depois de devolvida, a resposta passa ao
nginx, que a guarda no buffer, até 1 GB por padrão, e o worker se libera. A transferência lenta não
segura nada do GPS.

**Determinismo**:

- `ZIP_STORED`;
- ordem fixa: Perfil, nome, protocolo, requisito;
- `date_time` do envio;
- permissões fixas.

Só o manifesto muda entre duas exportações iguais.

**Nome da pasta**: protocolo + nome, em NFC, sem `/ \ : * ? " < > |`, com até 80 caracteres.

### 5. Arquivo indisponível (FR-3695)

`copia_verificada` passa a converter `FileNotFoundError` e `OSError` em `ArquivoIndisponivel`. As
views de documento da inscrição, da mesa e da convocação, e as novas, respondem 409 *"Arquivo
indisponível"* com evento. É uma mudança pequena num caminho existente, com regressão nas três views
atuais.

### 6. Interface

- **Barra**: `Secao("Formalização", alcanca=lambda a: a.can("formalizacao:acessar"))`, sem consulta.
- **Lista de Editais designados**: uma consulta.
- **Página do Edital**:
  - um `<form method="post">` só;
  - grupos por Perfil;
  - caixa de seleção por pessoa e *Selecionar todos*;
  - documentos com *Visualizar* e *Baixar*;
  - *Exportar esta pessoa* na linha;
  - **um** seletor de Perfil, só se houver mais de um;
  - *Exportar selecionados* no rodapé.
- **Prévia**: uma página com o alcance, a tabela de pessoas e o botão *Confirmar e baixar*.
- **Resultado**: a tela diz *completo*, *parcial* ou *sem pacote* antes de tudo.
- **Histórico**: no fim da página.
- **Estilo**: em `interface/telas/formalizacao.css`, sem inline (CSP). O vocabulário é guardado por
  teste.

### 7. O que muda fora do app

| Arquivo | Mudança |
|---|---|
| `specs/009-…/spec.md`, `specs/115-…/spec.md` | FR-069 e FR-3606 revistas, **depois da aprovação** |
| `CLAUDE.md`/`AGENTS.md` | o `M` das append-only passa de 46 para 50 |
| `README.md` | a linha da `117` |
| `specs/033-…/inventario-das-negativas.md` | os 404 novos |
| `doc/implantacao-em-producao-ubuntu.md` | a nota sobre `EXPORTACAO_DE_FORMALIZACAO_LIMITE_MB` e o buffer do nginx |

## Riscos

| Risco | Mitigação |
|---|---|
| Exportação grande em requisição síncrona | limite antes de ler; trava por servidor; medição da SC-1111 |
| Disco do sistema | temporário sem nome; pior caso de 4 GB documentado; a TI confirma |
| O papel concedido a muitos | sem designação ele não dá nada; a `107` registra motivo; o auditor vê |
| Definição generosa demais | aviso de reserva; motivo; versão gravada em cada exportação |
| O setor guarda em pasta aberta | fora do GPS: dependência institucional |
| Seletor da `115` por linha | orçamento de consultas com 5 e 45 pessoas |

## Complexity Tracking

Não há violação. São quatro tabelas, e cada uma corresponde a um ato com dono distinto: definir,
designar, revogar e exportar. A alternativa mais barata, uma marca no Documento Exigido e a designação
pela presidência, foi revista porque misturava obrigação com encaminhamento e seleção com acesso
(D-009, D-013).
