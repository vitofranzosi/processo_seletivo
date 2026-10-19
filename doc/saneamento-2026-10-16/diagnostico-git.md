# Diagnóstico Git — 16/10/2026

## Referências observadas

| Referência | Commit |
|---|---|
| HEAD / `001-decisoes-pendentes` | `6fc3a85a9ce58a973dc0e29bc38085dfd055f171` |
| `origin/001-decisoes-pendentes` | `6fc3a85a` |
| `origin/main` local | `6fc3a85a` |
| `main` local | `ebb56717` |
| Base histórica | `db428b30` |

As refs `origin/*` são o estado armazenado neste clone; não houve fetch ou comprovação de toda a
situação remota nesta fase. O HEAD é ancestral da `main` local. A divergência é **10 × 0**:
dez commits exclusivos da `main`, nenhum exclusivo de `001-decisoes-pendentes`. Entre esta branch
e `origin/main`, **0 × 0**. Não há conflito instalado no índice nem alterações preexistentes.

Única worktree registrada: `D:/projetos/cefor/processo_seletivo`, branch `001-decisoes-pendentes`.
Isto não inventaria clones ou worktrees de outras máquinas. `db428b30` é ancestral do HEAD.

## Dez commits exclusivos da `main` local

| Commit | Assunto |
|---|---|
| `ebb56717` | Merge branch 'main' of https://github.com/vitofranzosi/processo_seletivo |
| `cecbecff` | Merge branch 'main' of https://github.com/vitofranzosi/processo_seletivo |
| `5accdd3e` | Merge branch 'main' of https://github.com/vitofranzosi/processo_seletivo |
| `1f984ebc` | Merge branch 'main' of https://github.com/vitofranzosi/processo_seletivo |
| `973a8b97` | Merge branch 'main' of https://github.com/vitofranzosi/processo_seletivo |
| `daef5b79` | Merge branch 'main' of https://github.com/vitofranzosi/processo_seletivo |
| `3a5cbbef` | Merge branch 'main' of https://github.com/vitofranzosi/processo_seletivo |
| `682250ae` | Merge branch 'main' of https://github.com/vitofranzosi/processo_seletivo |
| `62bb8b60` | Merge branch 'main' of https://github.com/vitofranzosi/processo_seletivo |
| `ea4d4fc4` | Atualização da main |

## Diferença efetiva: checkout → `main`

Cinco arquivos, **24 inserções e 6 exclusões**; a diferença está no commit `ea4d4fc4` e permanece
no resultado acumulado dos merges. Não são somente commits redundantes de integração.

| Arquivo em `backend/` | Diferença observada na `main` local |
|---|---|
| `processo_seletivo/comissoes/models.py` | Constraint para valores de função do membro |
| `processo_seletivo/editais/models/perfis.py` | Unicidade composta de identificador e Perfil na Modalidade |
| `processo_seletivo/inscricoes/models.py` | Comentário passa a apontar proteção PostgreSQL da inscrição enviada |
| `processo_seletivo/processos/models.py` | Unicidade composta de Processo/escopo e constraints de estado de Processo e Edital |
| `tests/integration/inscricoes/test_fatos_congelados.py` | Caso passa a editar identidade em vez de inscrição enviada |

Não há migration no diff entre as pontas. Não se conclui daí que as constraints foram migradas,
que o desenho está correto ou que há autorização para integrá-lo. Esse exame pertence a uma
revisão posterior, sem executar migrations nesta fase. Também não foi executada suíte nessa branch.

## Riscos

- Resetar a `main` para `origin/main` descartaria da referência o trabalho exclusivo acima.
- Apagar branch, clone ou worktree antes de backup pode retirar evidência disponível.
- Fast-forward até a `main` local importaria alterações funcionais não autorizadas nesta fase,
  embora a ancestralidade permita essa operação tecnicamente.
- Bundle não guarda working tree, arquivos ignorados/não rastreados nem bancos. Estes documentos
  ainda sem commit precisam de preservação separada, se autorizada.

Nenhuma dessas operações foi realizada. Preservar ambas as referências e revisar o diff é a
próxima medida recomendada, sem integração automática.

## Comandos somente de diagnóstico

```powershell
git status --short --branch
git worktree list --porcelain
git rev-list --left-right --count main...001-decisoes-pendentes
git rev-list --left-right --count origin/main...001-decisoes-pendentes
git log --left-right --oneline main...001-decisoes-pendentes
git diff --stat 001-decisoes-pendentes main
git diff 001-decisoes-pendentes main
```

## Bundle — aguarda destino e autorização operacional

Executar somente após confirmar diretório externo existente, espaço e acesso restrito. O conteúdo
do histórico pode incluir dados que não devem ser publicados. Não enviar bundle a serviço público.
O destino abaixo é marcador; não foi criado nem usado.

```powershell
$destinoPreservacao = Read-Host 'Diretório externo aprovado e existente'
if (-not (Test-Path -LiteralPath $destinoPreservacao -PathType Container)) { throw 'Destino ausente' }
$arquivoBundle = Join-Path $destinoPreservacao 'processo-seletivo-2026-10-16.bundle'
if (Test-Path -LiteralPath $arquivoBundle) { throw 'Destino já existe; não sobrescrever' }
git bundle create $arquivoBundle --all
if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar bundle' }
git bundle verify $arquivoBundle
if ($LASTEXITCODE -ne 0) { throw 'Bundle não verificado' }
git bundle list-heads $arquivoBundle
Get-FileHash -Algorithm SHA256 -LiteralPath $arquivoBundle
```

Conferir a presença das refs `main` e `001-decisoes-pendentes`, registrar hash, tamanho, data e
custodiante. A verificação estrutural deve ser complementada por restauração em diretório novo
autorizado e conferência dos commits esperados. Não criar ou restaurar nada antes dessa autorização.
