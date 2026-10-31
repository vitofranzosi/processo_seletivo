# Data Model: Cadastro de unidades administrado pela aplicação (110)

**Nenhuma tabela nova, nenhuma coluna nova.** O que muda no banco é um par de gatilhos em
`processos` (D-013). O resto é quem escreve no que já existe.

## Unidade (`unidades`, existe)

| Campo | Origem | Nesta feature |
|---|---|---|
| `id` | `060` | — |
| `codigo` | `060` | escolhido no cadastro; **imutável** (gatilho `unidade_codigo_imutavel`, inalterado); a tela não o oferece na edição |
| `sigla`, `nome`, `local` | `060` | editáveis; preenchidos |
| `cabecalho` | `060` | editável; uma ou duas linhas preenchidas |
| `atendimento` | `109` | editável; vazio ou uma linha de até 255 caracteres |
| `ativa` | `060` | muda só por desativar e reativar |
| `registrada_em` | `060` | gravado no cadastro |
| `alterada_em` | `060` | gravado em toda edição, desativação e reativação |

**Não se exclui** (gatilho `unidade_nao_se_exclui`, inalterado). **Não é append-only** e continua
fora de `TABELAS_APPEND_ONLY`: a história dela é a trilha.

### Validação (D-005) — uma regra para semente, cadastro e edição

| Campo | Regra | Recusa |
|---|---|---|
| `codigo` | `^[a-z0-9]+(?:-[a-z0-9]+)*$`, até 100 | `codigo_invalido` |
| `codigo` | diferente de `institucional` | `codigo_reservado` |
| `codigo` | único (constraint existente) | `codigo_ja_registrado` |
| `sigla`, `nome`, `local` | texto preenchido depois de aparado; limites das colunas (30, 255, 120) | `campo_obrigatorio` |
| `cabecalho` | lista de 1 ou 2 textos preenchidos | `cabecalho_invalido` |
| `atendimento` | vazio, ou uma linha preenchida de até 255 | `atendimento_invalido` |

Todos os textos são aparados antes de gravar e antes de comparar (EC-4).

### Transições de `ativa`

```text
            cadastrar
    (nada) ───────────▶ ATIVA ◀──────────┐
                          │              │ reativar (motivo)
              desativar   │              │
              (motivo)    ▼              │
                       DESATIVADA ───────┘
```

Desativar `DESATIVADA` e reativar `ATIVA` são recusadas (`unidade_ja_desativada`,
`unidade_ja_ativa`). Não há transição para "excluída".

**O que a situação decide** (já implementado pela `060` e pela `106`, e só exercitado aqui):

| | ATIVA | DESATIVADA |
|---|---|---|
| criar Processo, criar Edital | sim | **não** (`exigir_unidade(ativa=True)`) |
| conceder vínculo | sim | **não** (`_exigir_unidade` da `106`) |
| conduzir Processo e Edital existentes | sim | sim |
| vínculos vigentes valem | sim | sim |
| manter autoridades | sim | sim |
| aparecer na identificação de um Edital dela | sim | sim |
| contar para "uma unidade ativa" da moldura *(109)* | sim | não |

## Evento da trilha (`RegistroAuditoria`, existe, append-only)

Ver D-008 do [research](research.md). Resumo do que esta feature grava:

| Campo | Valor |
|---|---|
| `institution_scope` | o código da unidade afetada |
| `actor_subject` | `pessoa-<uuid>` de quem praticou; `implantacao` na semente |
| `permission` | `unidade:administrar`; `implantacao` na semente, como hoje |
| `operation` | `REGISTRAR_UNIDADE` ou `ALTERAR_UNIDADE` |
| `aggregate_type`, `aggregate_id` | `Unidade` e o `id` dela |
| `previous_state`, `new_state` | `ATIVA` / `DESATIVADA` |
| `reason` | o motivo |
| `detalhe` | `{"depois": {...}}` no registro; `{"antes": {...}, "depois": {...}}` na alteração, com os seis campos |

## Catálogo de permissões (`seguranca/acessos.py`, existe)

```text
PAPEIS_INSTITUCIONAIS
    "administrador-institucional"  "Administrador institucional de acessos"  [acesso:administrar]   (sem mudança)
    "administrador-de-unidades"    "Administrador do registro de unidades"   [unidade:administrar]  (novo, D-002)
```

Nenhum papel de unidade, nenhum papel do `PAPEIS` (seletor) recebe a permissão. **Nenhuma migration**:
o papel é catálogo, e `Vinculo.papel` é texto sem restrição no banco. O vínculo do papel novo é um
`Vinculo` como os outros, no escopo `institucional`, concedido só pela implantação, com o motivo e
o evento `ACESSO_CONCEDER` da `106`; a retirada é a `RevogacaoDeVinculo` de sempre.

**Na reversão** para uma release que não conhece o papel, os vínculos dele continuam no banco
(append-only) e não dão permissão nenhuma: `permissoes_dos_papeis` ignora papel desconhecido.

## Gatilhos novos (`processos`, D-013)

| Gatilho | Tabela | Quando recusa |
|---|---|---|
| `processo_escopo_imutavel` | `processos_processoseletivo` | `BEFORE UPDATE`, `OLD.institution_scope IS DISTINCT FROM NEW.institution_scope` |
| `edital_escopo_imutavel` | `processos_edital` | idem |

Sem mudança de privilégio. Reversíveis (`DROP TRIGGER`, `DROP FUNCTION`). Entram no incremento A
(D-019).

## O que não é dado

O provedor de homologação (D-018) não grava nada próprio: o bilhete é o do provedor simulado, na
memória do processo, e sai dela no retorno. A pessoa que ele autentica é uma `Pessoa` com `IdentidadeExterna(provedor="homologacao")`,
criada pelo fluxo da `106` — e só existe no banco sintético da instância de validação.

## Semente (`unidades/unidades.json`, existe)

O formato não muda: a chave é o código, e os campos são `sigla`, `nome`, `cabecalho`, `local`,
`ativa` (booleano, conferido pelo leitor da semente, e não pela regra única) e `atendimento`,
opcional e, quando presente, preenchido. **Lido só quando a tabela de Unidades está vazia** (D-001).
