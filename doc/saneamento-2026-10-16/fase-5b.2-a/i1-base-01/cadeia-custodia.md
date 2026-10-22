# Cadeia de custódia local

Investigação FASE-5B.2-A-I1-BASE-01; executor Codex; 20/10/2026, America/Sao_Paulo (UTC−03:00).
Repositório: D:\projetos\cefor\processo_seletivo. Branch: 001-decisoes-pendentes. HEAD observado: 4ec10ba52636ef54b56dee35970333f5742548df.

I1 bloqueado; I2–I6 não autorizados; G1–G6 bloqueados individualmente. Nenhuma nova baseline aprovada.

## Aquisição e autorização

Início da verificação de identidade: 2026-10-20T09:07:50-03:00. Preparação documental posterior à coleta de 09:09:32-03:00. Horário de término e hashes finais serão publicados no fechamento da conversa após selagem; o manifesto registra sete hashes sem autorreferência.

Autorização humana: prompt anexado I1-BASE-01, recebido nesta conversa em C:\Users\1952484\.codex\attachments\2b10f9a0-8d2b-407c-ae2d-f0f2cf20a2cc\Pasted text.txt. Não constitui autorização I1 ou operacional. Executor: Codex, terminal PowerShell no Windows, workspace compartilhado. Relógio local UTC−03:00, sem timestamp confiável.

## Sequência de comandos e resultados

1. Get-Content UTF8 no anexo: escopo restrito lido.
2. Get-Location, git rev-parse --show-toplevel, branch --show-current, rev-parse HEAD: identidade e referência atual confirmadas.
3. git status --porcelain=v1 --untracked-files=all, diff --name-status, diff --cached --name-status: 15 não rastreados, nenhum diff rastreado ou staged.
4. git cat-file -t nos dois IDs: ambos commit.
5. git merge-base, log fuller -15, log antigo..atual, diff --name-status/--stat, rev-list --left-right --count: ancestral antigo, cinco commits incorporados, seis arquivos de código/teste diferentes.
6. git diff --no-ext-diff --no-textconv dos dois módulos modificados e log por caminho: extração e trajetória identificadas; nenhum teste reexecutado.
7. Get-Item/Get-ChildItem, Get-FileHash SHA256, Get-Content e ConvertFrom-Json: 15 metadados e hashes, A.4/A.5, matriz e plano consultados. JSON dos controles examinado estruturalmente, valores de autorização não divulgados. Não houve execução de arquivos encontrados.
8. rg --files para AGENTS sob doc: nenhuma regra adicional encontrada; diretórios ancestrais e diretórios inventariados sem reparse points.
9. Get-Content .gitattributes: política LF observada; causa histórica não estabelecida.
10. Escrita permitida: somente sete Markdown e manifesto no destino i1-base-01, antes inexistente, dentro do workspace gravável; sem necessidade de sobrescrita, sem alteração de índice. Encerramento inclui SHA-256 finais, releitura dos protegidos e estado Git, com resultado externo na conversa.

## Erros e correções de coleta

Tentativa de análise em memória com python falhou antes de executar: python.exe indisponível. Não instalado nem executado substituto operacional; análise refeita com cmdlets PowerShell. Uma saída extensa de JSON foi truncada e não foi usada como evidência completa. Um parser preliminar resolveu README.md na raiz indevidamente; esses resultados foram descartados. Nova coleta usa explicitamente a pasta do manifesto, resultando em 239 comparações corretas sem divergência. Nenhum erro implicou gravação em arquivos anteriores.

## Evidências e limites

Diretas: Git local, metadados de sistema, hashes físicos e estrutura documental. Históricas: conclusões CRLF e preservação antes/depois nas etapas anteriores. Inferência: evolução de HEAD explicada pelos merges locais e compatibilidade com política LF. Não confirmados: autoria pessoal, transformação histórica concreta, confiança do runtime, prontidão operacional e validade administrativa dos controles locais.

Sem custódia independente, assinatura digital, lacre externo, cópia forense ou bloqueio de escrita concorrente. Conferência antes/depois detecta diferenças de bytes no conjunto inventariado, sem provar ausência de mudanças transitórias entre medições. Não declarar preservação integral de arquivos fora desse conjunto.

Finalização: sete Markdown primeiro; manifesto-entrega.sha256 em seguida, contendo hashes daqueles sete. Hash do manifesto e término no relatório final; nenhuma alteração de conteúdo depois da medição final. Se conferência falhar, interromper sem corrigir automaticamente.

