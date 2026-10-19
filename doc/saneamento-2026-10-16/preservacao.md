# Checklist de preservação — procedimentos não executados

Data: 16/10/2026. Este arquivo prepara ações; caixas abertas não são prova de conclusão.
Os comandos de escrita aguardam confirmação de caminhos, destino e autorização operacional.

## GO-09 — comprovação sanitizada pelo titular

- [ ] Titular identificar a chave antiga no painel do OpenRouter por nome/identificador mascarado,
  sem revelar valor, abrir arquivo de credencial ou reenviar a captura exposta.
- [ ] Confirmar revogação/exclusão da chave antiga; substituir arquivo não comprova revogação.
- [ ] Registrar data da exposição conhecida (14/10), data da revogação e responsável.
- [ ] Consultar consumo entre exposição e revogação e após a revogação, considerando fuso e atraso
  de contabilização; registrar período consultado, total agregado e eventual anomalia.
- [ ] Se houver consumo suspeito, preservar evidência restrita e encaminhar pelo titular ao provedor
  e responsável institucional; não concluir ausência de incidente apenas por ausência de cobrança.
- [ ] Entregar declaração ou captura recortada/mascarada mostrando estado, data e identificador
  não secreto. Não anexar prompts, dados pessoais, saldo detalhado desnecessário ou chaves.

Modelo de registro: responsável; chave antiga identificada de forma mascarada; estado confirmado;
instante/fuso da revogação; intervalo da análise de consumo; resultado agregado; link restrito da
evidência sanitizada; anomalias/encaminhamentos. **Pendente de comprovação pelo titular.**
Não fazer chamada com a chave exposta para testar revogação nesta fase.

## GO-46 e divergência Git

- [x] Código e artefatos da 074 alcançáveis pelo HEAD; integração `6f8f8b50`.
- [x] Divergência da `main` local identificada: dez commits exclusivos, cinco arquivos diferentes.
- [ ] Definir destino externo aprovado para bundle e espaço disponível.
- [ ] Criar/verificar bundle segundo [diagnóstico](diagnostico-git.md), depois de autorizado.
- [ ] Registrar hash e realizar restauração isolada autorizada.
- [ ] Preservar separadamente documentos novos ainda sem commit; bundle não os contém.

## GO-47 — localizar, medir e manifestar

Locais históricos: `.claude/worktrees/ifes-launch-film-cabb9f/filme-de-lancamento/` (2,1 GB) e
`.claude/worktrees/processo-seletivo-video-519ad6/video/` (19 GB), na máquina que produziu os vídeos.
Esses caminhos relativos não estabelecem o caminho absoluto daquela máquina.
Neste clone há somente 46 arquivos de fontes/roteiro no filme, totalizando 481638 bytes; pasta
`video/` ausente. Não há comprovação da localização atual dos binários.

- [ ] Titular confirmar máquina e raízes de busca. Não varrer discos inteiros ou diretórios pessoais
  por padrão. O roteiro não segue diretórios de atalho/junção (reparse points).
- [ ] Executar `Localizar` do [roteiro PowerShell](preservar-videos.ps1) somente nas raízes aprovadas.
- [ ] Confirmar pastas completas das duas produções, inclusive imagens, áudio, projetos e saídas.
- [ ] Registrar arquivos e bytes atuais. Os 21 GB históricos são estimativa, não aceite de capacidade.
- [ ] Revisar a pasta aprovada para excluir do escopo credenciais e dados pessoais desnecessários;
  não abrir/copiar chaves. O manifesto usa uma lista de extensões de mídia, não arquivos de segredo.
- [ ] Gerar manifesto por produção, fora da origem, com caminho relativo, tamanho e SHA-256.

Exemplos preparados; os caminhos devem ser confirmados antes de execução:

```powershell
# Somente procura e apresenta metadados de mídia nas raízes explicitamente fornecidas.
.\preservar-videos.ps1 -Acao Localizar -Raizes @('D:\RAIZ-APROVADA')
# Só após confirmação da pasta de mídia e do local novo do manifesto:
.\preservar-videos.ps1 -Acao Manifestar -Origem 'D:\PRODUCAO-APROVADA' -Manifesto 'E:\BACKUP-APROVADO\origem.csv'
```

O roteiro inventaria extensões de mídia documentadas nele. Isso não constitui backup completo de
fontes: roteiro/scripts já versionados ficam no Git/bundle; qualquer outro projeto, fonte ou
arquivo fora da lista deve ser inventariado separadamente, com revisão humana do escopo.

## Copiar e verificar — somente após autorização

Escolher armazenamento externo com acesso restrito, capacidade para ambas as produções e margem,
e diretórios novos/vazios por produção. Confirmar que destino não está dentro da origem nem o
contrário. Nenhuma origem deve ser removida, movida, sobrescrita ou sincronizada por espelhamento.

Para copiar a pasta de mídia inteira, o responsável deve primeiro confirmar que todos os seus
arquivos podem ser copiados e que ela não contém segredos. Se a pasta misturar credenciais ou
outros dados, preparar escopo restrito em nova autorização; não usar a cópia integral abaixo.

```powershell
$origemVideo = (Resolve-Path -LiteralPath (Read-Host 'Pasta integral de mídia aprovada')).Path
$destinoVideo = (Resolve-Path -LiteralPath (Read-Host 'Pasta externa aprovada, existente e vazia')).Path
if (@(Get-ChildItem -LiteralPath $destinoVideo -Force).Count -ne 0) { throw 'Destino não vazio' }
$origemComparada = $origemVideo.TrimEnd('\') + '\'
$destinoComparado = $destinoVideo.TrimEnd('\') + '\'
if ($destinoComparado.StartsWith($origemComparada, [StringComparison]::OrdinalIgnoreCase) -or
    $origemComparada.StartsWith($destinoComparado, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Origem e destino sobrepostos'
}
# /XJ não acompanha junções. Não acrescentar /MIR, /PURGE, /MOV ou /MOVE.
robocopy $origemVideo $destinoVideo /E /COPY:DAT /DCOPY:DAT /XJ /R:1 /W:1
if ($LASTEXITCODE -ge 8) { throw 'Falha de cópia; preservar origem e investigar' }
```

Código de retorno de cópia não comprova integridade. Depois da cópia autorizada, executar:

```powershell
.\preservar-videos.ps1 -Acao Verificar -Origem 'E:\BACKUP-APROVADO\MIDIA' -Manifesto 'E:\BACKUP-APROVADO\origem.csv'
```

- [ ] Comparação sem arquivos de mídia ausentes/extras, com tamanhos e hashes iguais.
- [ ] Manifesto preservado fora da pasta de mídia, com seu próprio hash registrado.
- [ ] Conferência separada dos arquivos fora da lista de mídia, se copiados.
- [ ] Reprodução dos vídeos copiados, incluindo áudio, duração e trechos de início/meio/fim.
- [ ] Custodiante, caminho externo, data, contagens e evidências registrados; origens preservadas.

## Bancos `ps_filme` e `ps_video`

São mencionados pela auditoria como bancos com atos irreversíveis de filmagem. Sua presença neste
ambiente não foi consultada. Código e vídeos não permitem reconstruir necessariamente esse estado.

- [ ] Titular identificar host/instância, nomes reais, versão PostgreSQL e existência atual.
- [ ] Autorizar backup consistente por banco, com `pg_dump` em formato customizado, em arquivo novo;
  autenticação por mecanismo seguro existente, sem senha em comando, log ou documento.
- [ ] Registrar versões de servidor/ferramenta, horário, tamanho e SHA-256 do dump.
- [ ] Listar conteúdo com `pg_restore --list`; isso é inspeção estrutural, não teste de restauração.
- [ ] Autorizar restauração em instância/banco novos e isolados; comprovar estados usados nas cenas.
- [ ] Inventariar dependências externas (arquivos de mídia e papéis/privilégios) sem exportar segredos
  de autenticação. Não pressupor que dump de um banco leva arquivos externos ou papéis globais.

Nenhuma conexão, dump, restauração, seed, truncamento ou migration executada. Não usar bancos
originais para teste nem apagar atos de filmagem. Encerramento somente com evidência de restauração.
