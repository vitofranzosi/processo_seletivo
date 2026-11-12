# Implementation Plan: Entrega documental controlada ao setor da formalização

**Branch**: `claude/gps-entrega-documental-627460` | **Date**: 2026-11-04 (ajustado depois da revisão independente) | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), [diagnostico.md](diagnostico.md) e [data-model.md](data-model.md).

> **Desenho aprovado pelo usuário em 04/11.** A `115` está na `main` desde 04/11 (PR #369, merge
> `f563b5a3`), e a implementação pode começar. A primeira tarefa aplica a revisão aprovada da FR-069
> da `009` e da FR-3606 da `115` (T002).

## Summary

O setor que formaliza recebe da gestão de acessos o papel Formalização e uma designação no Edital, com
Perfis opcionais. Na página **Documentos para formalização** ele vê os aptos (desfecho vigente da
chamada mais recente), com os documentos que a condução **definiu**, de qualquer momento. Pode:

- visualizar e baixar um por vez;
- exportar um ZIP, por pessoa, por seleção ou por recorte.

Para mais de uma pessoa, uma **verificação** lê e confere tudo e mostra o resultado (*completo* ou
*parcial*, com os excluídos e o motivo) e devolve um **comprovante assinado pelo servidor**. O
**download** exige o comprovante, revalida as autorizações, relê tudo e só serve se o resultado inteiro
for o mesmo. Nada se guarda. O Documento Exigido e o conteúdo publicado não mudam. O molde é a `031`, e as fontes são a
`019`, a `009` e a `115`.

## Technical Context

**Language/Version**: Python 3.13, Django (o do repositório)
**Primary Dependencies**: nenhuma nova. `zipfile`, `tempfile`, `hashlib`, `csv` e `unicodedata`, da
biblioteca padrão; `django.core.signing`, do framework
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
│   ├── application/exportar.py           # verificação, montagem, registro
│   ├── application/comprovante.py        # emitir / conferir (django.core.signing), resumo canônico
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
  *(Desde a revisão de 12/11, D-025: também pela presidência do Processo, na tela da definição. Ver
  a seção da revisão, ao fim.)*
- `pode_acessar(ator, edital, inscricao=None)` → `ok` | `404` | `403(papel)`. É o único ponto de
  decisão.

### 3. O seletor (FR-3669 a FR-3674)

`aptos_com_conjunto(edital, perfis, definicao)`, em lote:

1. raiz da chamada → chamada mais recente → vigente → desfecho que inclui;
2. definição vigente;
3. **convocação**: itens definidos → conferência vigente *conforme* → `fonte_do_arquivo`
   (`convocacao/application/documentos.py:420`, na `main` desde a `115`);
4. **inscrição**: `DocumentoSubmetido` definidos;
5. deduplicação (FR-3659);
6. situação e última exportação.

### 4. Verificação e download (FR-3682 a FR-3698, FR-3689a, FR-3689b, FR-3714)

```text
compor_e_ler(alcance)            # usado pelos dois passos, uma leitura por arquivo
  ├─ pode_acessar por pessoa; qualquer 404 → recusa inteira
  ├─ Σ tamanhos gravados > limite → "Exportação recusada", antes de ler
  └─ por pessoa do alcance, por arquivo: abre → sha256 em blocos
        FileNotFoundError/OSError → INDISPONIVEL (evento em transação própria)
        hash ≠ esperado         → INTEGRIDADE (evento existente, transação própria)
     → Resultado(incluídas[itens, hashes], excluídas[item, motivo], definição, designação)
     resumo = canonical_sha256(Resultado)                 # FR-3689b

POST verificar (seleção | recorte), >1 pessoa
  └─ with transaction.atomic():
        pg_try_advisory_xact_lock(CLASSE, resumo(servidor)) ou "já está em andamento"
        r = compor_e_ler(alcance)                          # só lê, não copia
     comprovante = signing.dumps({v, sujeito, unidade, edital, designação, alcance, recorte,
                                  pessoas pedidas, definição, resultado, resumo, emitido_em},
                                 salt="formalizacao.verificacao", compress=True)
     evento "Verificação de exportação"
  → tela: RESULTADO primeiro; excluídos e motivos;
          botão "Baixar pacote [parcial] (N pessoas)" com o comprovante no corpo do POST

POST baixar (comprovante)
  ├─ signing.loads(comprovante, salt=…, max_age=15 min)
  │     BadSignature → "verificação inválida"; SignatureExpired → "verificação expirada"
  │     sujeito/unidade ≠ ator → "verificação inválida"        (nenhum arquivo lido)
  ├─ pode_acessar revalidado para cada pessoa pedida (403/404 da matriz)
  └─ with transaction.atomic():
        trava
        TemporaryFile()                                   # sem nome; O_TMPFILE no Linux
        r' = compor_e_ler(alcance)  — e, na mesma leitura, cada arquivo de pessoa incluída
             vai para SpooledTemporaryFile, e a pessoa completa entra no ZIP
        resumo(r') ≠ comprovante.resumo, ou definição/designação ≠ → "verificação defasada"
             (rollback; nada servido; ZIP descartado)
        manifesto.csv (FR-3713) com as incluídas e as excluídas de r'
        sha256 do pacote
        ExportacaoDeFormalizacao(resultado) + evento
     # commit: a trava sai aqui. A transferência começa depois, sem trava
  → FileResponse(temporário, attachment, no-store, "-parcial" se for)

POST exportar esta pessoa  — sem comprovante: compor_e_ler + montagem na mesma transação;
     qualquer falha → página com o motivo, sem ZIP e sem registro
except Exception → rollback; fecha temporários; "Exportação interrompida" em transação própria
```

**Uma leitura por arquivo em cada passo.** No download, `compor_e_ler` e a montagem são a mesma
passagem: cada arquivo é lido uma vez, conferido e, se a pessoa estiver incluída, copiado. Os arquivos
das excluídas são lidos só para conferir que continuam excluídas pelo mesmo motivo. Só depois de
comparar o resumo é que o pacote, já montado, é servido ou descartado.

**O comprovante não leva o conteúdo.** Ele leva o resumo. O servidor nunca toma como dado o que o
cliente manda: ele recompõe e compara.

**Ciclo de vida, em cada caso**:

| Caso | Registro | Trava | Temporário | O operador vê |
|---|---|---|---|---|
| Sucesso | gravado | sai no commit | fechado pelo `FileResponse` ao fim ou na desconexão | o ZIP |
| Comprovante inválido, fabricado, expirado ou de outro ator | não | não chega a ser tomada | não chega a existir | página com *verificar de novo*; nenhum arquivo lido |
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
| `specs/009-…/spec.md`, `specs/115-…/spec.md` | FR-069 e FR-3606 revistas, com a nota da D-016. É a única mudança nessas specs, além da FR-3695 no código (FR-3705) | **T002** |
| `CLAUDE.md`/`AGENTS.md` | `M` das append-only de 49, desde a `115`, para 53 | T005 |
| `README.md` | a linha da `117` | T037 |
| `specs/033-…/inventario-das-negativas.md` | os 404 novos | T021 |
| `doc/implantacao-em-producao-ubuntu.md` | o limite e o roteiro de validação da §5.4 do diagnóstico | T036 |

## Riscos

| Risco | Mitigação |
|---|---|
| Transferência cortada pelo tempo-limite | o registro só diz *disponibilizado*; o ZIP truncado é inválido; validação na VM; reduzir o limite |
| Disco do sistema | temporário sem nome; pior caso documentado; validação na VM |
| Leitura dupla (verificação e download) e transferência | dentro do limite; o CI mede verificação e montagem em separado (SC-1111); a VM mede as duas e a transferência (homologação, item 5) |
| Comprovante fabricado ou reaproveitado | assinatura do servidor, validade de 15 min, vínculo ao ator; autorização revalidada; reuso só gera outra exportação registrada |
| Definição generosa demais | vazia por padrão, avisos, motivo, histórico ao auditor |
| Nome hostil no ZIP ou no CSV | FR-3712, FR-3713, SC-1114 |
| O setor guarda em pasta aberta | fora do GPS |

## Complexity Tracking

Não há violação. As quatro tabelas são quatro atos com donos distintos. A verificação em dois passos
custa uma leitura extra e evita guardar pacote, processar em segundo plano ou servir um resultado que
o operador não viu.

## Revisão de 12/11/2026 — a presidência também designa (D-025)

**Escopo.** FR-6700 a FR-6708, UX-700 a UX-702, SC-2200 a SC-2204. Nenhuma tabela, migration, tela
ou evento de trilha novo.

**Desenho.**

- **Um predicado**, `pode_designar(ator, edital)`, em `formalizacao/domain/autorizacao.py`. Devolve a
  base que autoriza, ou `None`: `acesso:gerir` na unidade do Edital, ou `comissao:presidir` quando o
  ator é membro ativo com a função de presidente da comissão do Processo do Edital (`membro_ativo`,
  da `011`). Não passa por `pode_gerir_comissao`, que aceitaria `comissao:gerir` (FR-6700).
- **O mesmo comando.** `designar.designar` e `designar.revogar` buscam o Edital ou a designação com o
  filtro de `institution_scope` (404) e só depois perguntam o predicado, com
  `require_authorization_base` nomeando as duas bases (403, FR-6707). A base vai ao `record_event`,
  e a trilha diz quem autorizou (FR-6705). As recusas da FR-3663 (papel, autodesignação, vigente,
  Perfil) não mudam e valem para as duas bases.
- **A trava da `011`.** Dentro da transação, os dois comandos trancam o `ProcessoSeletivo` do Edital
  antes da pessoa e releem a base depois da trava, como os comandos da comissão. A presidência
  rebaixada ou removida entre a view e a gravação é recusada, e a base que vai à trilha é a relida.
  A conferência de fora da transação continua, para não trabalhar por quem não pode.
- **Quem tem o papel.** `pessoas_com_o_papel` passa a receber o Edital e pergunta o mesmo predicado,
  para a tela da presidência desenhar a escolha (FR-6701).
- **A tela.** A seção "Quem acessa os documentos" da definição ganha o formulário de designar e o
  "Revogar" por linha quando `pode_designar` é verdadeiro (UX-700). Dois POST novos, filhos da
  definição: `editais/<id>/formalizacao/designar` e
  `editais/<id>/formalizacao/designacoes/<id>/revogar`. A recusa de negócio e o sucesso voltam à
  seção pela sessão (UX-702). A designação de outro Edital é inexistente, e entra no inventário da
  `033`.
- **A jornada (`153`).** O andamento e a advertência do encerramento trocam `ator.can(GERIR)` pelo
  predicado, e o link pela tela de cada base (FR-6708). O responsável e a frase de a quem pedir passam
  a nomear a presidência.

**Testes.** `tests/integration/formalizacao/test_acesso.py`: `test_a_presidencia_nao_designa` vira a
prova da regra nova e dos limites (SC-2200 a SC-2204), mais a tela. `tests/interface/test_passagem_ao_setor.py`
acompanha a FR-6708.

**Riscos.** A presidência que também tem o papel continua sem se designar; outra pessoa pode
designá-la, e então ela acessa pela designação, como qualquer acúmulo de papéis da matriz (FR-6704).
