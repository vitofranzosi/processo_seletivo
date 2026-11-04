# Implementation Plan: Entrega documental controlada ao setor da formalização

**Branch**: `claude/gps-entrega-documental-627460` | **Date**: 2026-11-04 (consolidado) | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), [diagnostico.md](diagnostico.md) e [data-model.md](data-model.md).

> **Desenho aprovado pelo usuário em 04/11.** A implementação começa só depois do merge do PR #369,
> que traz a implementação da `115`. A primeira tarefa aplica a revisão aprovada da FR-069 da `009` e
> da FR-3606 da `115` (T002).

## Summary

O setor que formaliza recebe da gestão de acessos o papel Formalização e uma designação no Edital, com
Perfis opcionais. Na página **Documentos para formalização** ele vê os aptos (desfecho vigente da
chamada mais recente), com os documentos que a condução **definiu**, de qualquer momento. Pode:

- visualizar e baixar um por vez;
- exportar um ZIP, por pessoa, por seleção ou por recorte.

Para mais de uma pessoa, uma **verificação** lê e confere tudo e mostra o resultado (*completo* ou
*parcial*, com os excluídos e o motivo). O **download** remonta e só serve se nada mudou. Nada se
guarda. O Documento Exigido e o conteúdo publicado não mudam. O molde é a `031`, e as fontes são a
`019`, a `009` e a `115`.

## Technical Context

**Language/Version**: Python 3.13, Django (o do repositório)
**Primary Dependencies**: nenhuma nova. `zipfile`, `tempfile`, `hashlib`, `csv` e `unicodedata`, da
biblioteca padrão
**Storage**: PostgreSQL; a raiz privada existente, só leitura
**Testing**: pytest contra PostgreSQL (`make test-pg`); Playwright no grupo `navegador`
**Target Platform**: o monólito atrás de nginx e gunicorn síncrono (5 workers, 120 s), sem
`ATOMIC_REQUESTS`
**Project Type**: web, monólito
**Performance Goals**: cada passo do Cenário A em menos de 30 s no CI; consultas constantes. A
capacidade da VM é medida na homologação
**Constraints**:
- nada persistido além do registro;
- nada pessoal em log ou URL;
- CSP sem inline;
- 404/403 pelo ponto único e pelo inventário da `033`;
- limite inicial de 400 MB;
- uma operação por servidor.

**Scale/Scope**: dezenas de aptos por Edital

## Constitution Check

| Princípio | Como o plano o cumpre |
|---|---|
| Publicação é ato imutável | A definição fica fora do snapshot (FR-3657) |
| Nada é excluído | Quatro tabelas append-only; o pacote não é guardado |
| Negar por padrão | Definição vazia, papel não concedido, lista sem marcação; o predicado exige papel, designação e apto |
| Verificação de escopo | Unidade, Perfis, 404 inclusive em POST forjado |
| Rastreabilidade | Eventos distintos; registro com ids, hashes, versão e resultado |

## Project Structure

```text
backend/processo_seletivo/
├── formalizacao/                         # app novo
│   ├── models.py                         # Definicao…, Designacao…, Revogacao…, Exportacao…
│   ├── migrations/0001_inicial.py        # tabelas + gatilhos
│   ├── domain/nomes.py                   # capacidade, recusas, situações, operações
│   ├── domain/autorizacao.py             # pode_acessar (predicado único)
│   ├── domain/caminhos.py                # normalização de nomes e colisões (FR-3712)
│   ├── application/definir.py            # definição e histórico (condução)
│   ├── application/designar.py           # designar / revogar (gestão de acessos)
│   ├── application/conjunto.py           # aptos e conjunto (seletor único, em lote)
│   ├── application/exportar.py           # verificação, assinatura, montagem, registro
│   └── infrastructure/pacote.py          # ZIP_STORED em TemporaryFile; manifesto (FR-3713)
├── interface/identidade.py               # papel em PAPEIS/DESCRICOES
├── interface/views_formalizacao.py       # módulo novo, em MODULOS_DE_VIEW
├── interface/acessos.py                  # designação junto do vínculo
├── interface/navegacao.py                # Secao "Formalização"
├── interface/templates/interface/formalizacao_*.html
├── interface/telas/formalizacao.css
├── portal/arquivos.py                    # ArquivoIndisponivel (FR-3695)
└── seguranca/papeis.py                   # TABELAS_APPEND_ONLY + 4
```

**Structure Decision: um app novo, `formalizacao`.** Ele lê `convocacao`, `inscricoes` e `editais` e não
escreve neles. As views ficam em módulo próprio.

## Desenho

### 1. A definição (FR-3653 a FR-3660, FR-3711)

- **Tela** na condução: todos os requisitos das versões publicadas, por momento, sem marcação na
  primeira vez, com campo de motivo obrigatório.
- **Avisos**, a partir de dados existentes:
  - recorte por modalidade;
  - momento da inscrição.
- **Histórico** na mesma tela: versões, com o que entrou e saiu em relação à anterior. Visível à
  condução e ao auditor.

### 2. Papel e designação (FR-3661 a FR-3668)

- `PAPEIS["formalizacao"] = {"formalizacao:acessar"}`. A tela da `107` já o oferece.
- **Designação** em **Acessos**, na pessoa: `acesso:gerir`, sem autodesignação, `select_for_update`
  na pessoa, papel vigente, Perfis do Edital, trilha.
- `pode_acessar(ator, edital, inscricao=None)` → `ok` | `404` | `403(papel)`. É o único ponto de
  decisão.

### 3. O seletor (FR-3669 a FR-3674)

`aptos_com_conjunto(edital, perfis, definicao)`, em lote:

1. raiz da chamada → chamada mais recente → vigente → desfecho que inclui;
2. definição vigente;
3. **convocação**: itens definidos → conferência vigente *conforme* → `fonte_do_arquivo` [#369];
4. **inscrição**: `DocumentoSubmetido` definidos;
5. deduplicação (FR-3659);
6. situação e última exportação.

### 4. Verificação e download (FR-3682 a FR-3698, FR-3714)

```text
POST verificar (seleção | recorte), >1 pessoa
  ├─ pode_acessar por pessoa; qualquer 404 → recusa inteira
  ├─ Σ tamanhos gravados > limite → "Exportação recusada", antes de ler
  └─ with transaction.atomic():
        pg_try_advisory_xact_lock(CLASSE, resumo(servidor)) ou "já está em andamento"
        por pessoa, por arquivo: abre → sha256 em blocos (sem copiar)
           FileNotFoundError/OSError → INDISPONIVEL (evento em transação própria)
           hash ≠ esperado         → INTEGRIDADE (evento existente, transação própria)
        assinatura = sha256 canônico(pessoas incluídas, itens, hashes, versão da definição)
     evento "Verificação de exportação" (resultado, contagens)
  → tela: RESULTADO primeiro; excluídos e motivos; botão "Baixar pacote [parcial] (N pessoas)"
          com a assinatura num campo oculto (POST)

POST baixar (assinatura)  — e "Exportar esta pessoa", sem assinatura
  ├─ pode_acessar; limite (como acima)
  └─ with transaction.atomic():
        trava (como acima)
        recompõe o conjunto; ≠ assinatura → "verificação defasada" (nada servido)
        TemporaryFile()                          # sem nome; O_TMPFILE no Linux
        por pessoa incluída: cada fonte → SpooledTemporaryFile + sha256 numa leitura
           qualquer falha ou hash ≠ → aborta: "verificação defasada"
             (na pessoa única: página com o motivo)
           pessoa completa → entradas no ZIP (nome pela FR-3712, date_time do envio)
        manifesto.csv (FR-3713) com as incluídas e as não incluídas da verificação
        sha256 do pacote
        ExportacaoDeFormalizacao(resultado COMPLETO | PARCIAL) + evento
     # commit: a trava sai aqui. A transferência começa depois, sem trava
  → FileResponse(temporário, attachment, no-store, nome sem dado pessoal, "-parcial" se for)
  except Exception → rollback (sem registro); fecha temporários; evento "Exportação interrompida"
                     em transação própria; página "A exportação não foi concluída…"
```

**Ciclo de vida, em cada caso**:

| Caso | Registro | Trava | Temporário | O operador vê |
|---|---|---|---|---|
| Sucesso | gravado | sai no commit | fechado pelo `FileResponse` ao fim ou na desconexão | o ZIP |
| Verificação defasada | não | sai no rollback | fechado | página com *verificar de novo* |
| Exceção | não | sai no rollback | fechado no `finally` | página *não concluída* |
| Worker morto na montagem | não (transação não comitada) | sai com a conexão | some com o processo, porque não tem nome | erro do proxy |
| Worker morto na transferência | gravado, e diz só *disponibilizado* | já tinha saído | some com o processo | ZIP truncado e inválido; exporta de novo |

**Por que trava de transação, e não de sessão.** A de sessão sobrevive numa conexão reaproveitada
(`CONN_MAX_AGE`) e depende de liberação explícita. A de transação sai sozinha no commit ou no rollback.
O preço é segurar uma transação aberta durante a leitura, sem trava de linha, por segundos.

**O que não se presume.** O desenho não presume buffering do nginx nem liberação antecipada do worker.
A transferência ocupa o worker e conta no tempo-limite (§5.2 do diagnóstico). A medição é da
homologação.

**Determinismo**: `ZIP_STORED`; ordem fixa (Perfil, nome, protocolo, requisito); `date_time` do envio;
permissões fixas.

### 5. Nomes e manifesto (FR-3712, FR-3713)

`domain/caminhos.py` é puro e testado em unidade:

- `componente(texto)`: NFC, sem controles nem reservados, até 80 caracteres, `sem-nome` se vazio;
- `caminhos(pessoas)`: `‹protocolo› ‹nome›/‹requisito›.pdf`, com sufixos `-2`, `-3`… por ordem do
  requisito.

O ZIP é escrito com `ZipInfo` montado a partir desses caminhos, nunca de entrada externa.

O manifesto usa `csv` com `QUOTE_MINIMAL`, BOM e a função `neutralizar(celula)`.

### 6. Arquivo indisponível (FR-3695)

`copia_verificada` converte `FileNotFoundError` e `OSError` em `ArquivoIndisponivel`. As três views
existentes e as novas respondem 409 *"Arquivo indisponível"*, com evento.

### 7. Interface

- **Barra**: `Secao("Formalização", alcanca=lambda a: a.can("formalizacao:acessar"))`.
- **Página do Edital**:
  - um formulário POST, grupos por Perfil;
  - caixa por pessoa e *Selecionar todos*;
  - *Exportar esta pessoa* na linha;
  - um seletor de Perfil, só se houver mais de um;
  - *Verificar e exportar* no rodapé;
  - histórico no fim.
- **Tela da verificação**: o resultado em destaque no topo; a tabela das pessoas não incluídas com o
  motivo; a tabela das incluídas; o botão com o número de pessoas e a palavra *parcial*, quando for.
- **Estilo** em `interface/telas/formalizacao.css`.

### 8. O que muda fora do app

| Arquivo | Mudança | Quando |
|---|---|---|
| `specs/009-…/spec.md`, `specs/115-…/spec.md` | FR-069 e FR-3606 revistas, com a nota da D-016 | **T002**, depois do merge do #369 |
| `CLAUDE.md`/`AGENTS.md` | `M` das append-only de 46 para 50 | T005 |
| `README.md` | a linha da `117` | T037 |
| `specs/033-…/inventario-das-negativas.md` | os 404 novos | T021 |
| `doc/implantacao-em-producao-ubuntu.md` | o limite e o roteiro de validação da §5.4 do diagnóstico | T036 |

## Riscos

| Risco | Mitigação |
|---|---|
| Transferência cortada pelo tempo-limite | o registro só diz *disponibilizado*; o ZIP truncado é inválido; validação na VM; reduzir o limite |
| Disco do sistema | temporário sem nome; pior caso documentado; validação na VM |
| Leitura dupla (verificação e download) | dentro do limite; cada passo cabe no tempo-limite (SC-1111) |
| Definição generosa demais | vazia por padrão, avisos, motivo, histórico ao auditor |
| Nome hostil no ZIP ou no CSV | FR-3712, FR-3713, SC-1114 |
| O setor guarda em pasta aberta | fora do GPS |

## Complexity Tracking

Não há violação. As quatro tabelas são quatro atos com donos distintos. A verificação em dois passos
custa uma leitura extra e evita guardar pacote, processar em segundo plano ou servir um resultado que
o operador não viu.
