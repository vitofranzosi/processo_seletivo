<#
Roteiro operacional preparado em 16/10/2026. Não executa cópia, exclusão ou acesso a banco.
Localizar lê metadados. Manifestar e Verificar leem somente extensões de mídia abaixo.
Confirmar raízes, origem e destino antes de executar. Não apontar para diretórios de credenciais.
Fontes/scripts e projetos fora desta lista exigem inventário próprio, não são cobertos pelo aceite.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Localizar', 'Manifestar', 'Verificar')]
    [string]$Acao,
    [string[]]$Raizes,
    [string]$Origem,
    [string]$Manifesto
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$extensoesMidia = @('.mp4', '.mov', '.webm', '.mkv', '.avi', '.m4v', '.wav', '.mp3',
    '.m4a', '.aac', '.flac', '.ogg', '.png', '.jpg', '.jpeg', '.webp', '.svg', '.pdf')

function Obter-PastaReal([string]$Caminho) {
    if ([string]::IsNullOrWhiteSpace($Caminho)) { throw 'Informe uma pasta aprovada' }
    $pasta = Get-Item -LiteralPath $Caminho -Force
    if ($pasta.PSProvider.Name -ne 'FileSystem' -or -not $pasta.PSIsContainer) {
        throw 'A origem deve ser uma pasta do sistema de arquivos'
    }
    # Um ancestral que seja junção também muda o alcance real da busca.
    $ancestral = $pasta
    while ($null -ne $ancestral) {
        if ($ancestral.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw 'Pasta ou ancestral é atalho/junção; confirme o caminho físico'
        }
        $ancestral = $ancestral.Parent
    }
    return $pasta.FullName
}

function Obter-Midias([string]$Pasta) {
    foreach ($item in Get-ChildItem -LiteralPath $Pasta -Force) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
        if ($item.PSIsContainer) {
            if ($item.Name -in @('.git', '.venv', 'node_modules')) { continue }
            Obter-Midias $item.FullName
        }
        elseif ($item.Extension.ToLowerInvariant() -in $extensoesMidia) {
            $item
        }
    }
}

function Obter-Registros([string]$Pasta) {
    $prefixo = $Pasta.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    foreach ($arquivo in @(Obter-Midias $Pasta | Sort-Object FullName)) {
        $tamanhoAntes = $arquivo.Length
        $alteracaoAntes = $arquivo.LastWriteTimeUtc
        $hash = (Get-FileHash -LiteralPath $arquivo.FullName -Algorithm SHA256).Hash
        $depois = Get-Item -LiteralPath $arquivo.FullName -Force
        if ($depois.Length -ne $tamanhoAntes -or $depois.LastWriteTimeUtc -ne $alteracaoAntes) {
            throw 'Arquivo mudou durante leitura; interrompa produção e gere novo manifesto'
        }
        [pscustomobject]@{
            CaminhoRelativo = $arquivo.FullName.Substring($prefixo.Length).Replace('\', '/')
            Bytes = $tamanhoAntes
            SHA256 = $hash
        }
    }
}

if ($Acao -eq 'Localizar') {
    if (-not $Raizes) { throw 'Informe somente as raízes de busca aprovadas' }
    foreach ($raiz in $Raizes) {
        $pasta = Obter-PastaReal $raiz
        $midias = @(Obter-Midias $pasta)
        $midias | Select-Object FullName, Length, LastWriteTimeUtc
        [pscustomobject]@{
            Raiz = $pasta
            ArquivosDeMidia = $midias.Count
            BytesDeMidia = ($midias | Measure-Object Length -Sum).Sum
        }
    }
    return
}

$pastaMidia = Obter-PastaReal $Origem
if ([string]::IsNullOrWhiteSpace($Manifesto)) { throw 'Informe o caminho do manifesto' }
$caminhoManifesto = [IO.Path]::GetFullPath($Manifesto)
$prefixoMidia = $pastaMidia.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
if ($caminhoManifesto.StartsWith($prefixoMidia, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Guarde o manifesto fora da pasta de mídia'
}

if ($Acao -eq 'Manifestar') {
    if (Test-Path -LiteralPath $caminhoManifesto) { throw 'Manifesto existente; não sobrescrever' }
    $pastaManifesto = Obter-PastaReal ([IO.Path]::GetDirectoryName($caminhoManifesto))
    $registros = @(Obter-Registros $pastaMidia)
    if ($registros.Count -eq 0) { throw 'Nenhuma mídia; não gerar manifesto vazio' }
    $registros | Export-Csv -LiteralPath $caminhoManifesto -NoTypeInformation -Encoding UTF8 -NoClobber
    Get-FileHash -LiteralPath $caminhoManifesto -Algorithm SHA256
    [pscustomobject]@{ Arquivos = $registros.Count; Bytes = ($registros | Measure-Object Bytes -Sum).Sum }
    return
}

$esperados = @(Import-Csv -LiteralPath $caminhoManifesto -Encoding UTF8)
if ($esperados.Count -eq 0) { throw 'Manifesto vazio' }
$mapaEsperado = @{}
foreach ($registro in $esperados) {
    if ([string]::IsNullOrWhiteSpace($registro.CaminhoRelativo) -or
        $registro.CaminhoRelativo -match '(^[\\/]|^[A-Za-z]:|(^|[\\/])\.\.([\\/]|$))' -or
        $registro.SHA256 -notmatch '^[A-Fa-f0-9]{64}$' -or $registro.Bytes -notmatch '^\d+$') {
        throw 'Manifesto inválido; não usar como evidência'
    }
    if ($mapaEsperado.ContainsKey($registro.CaminhoRelativo)) { throw 'Caminho duplicado no manifesto' }
    $mapaEsperado[$registro.CaminhoRelativo] = $registro
}
$atuais = @(Obter-Registros $pastaMidia)
if ($atuais.Count -ne $esperados.Count) { throw 'Quantidade de mídias diverge do manifesto' }
foreach ($registro in $atuais) {
    if (-not $mapaEsperado.ContainsKey($registro.CaminhoRelativo)) { throw 'Mídia extra ou caminho divergente' }
    $esperado = $mapaEsperado[$registro.CaminhoRelativo]
    if ([int64]$registro.Bytes -ne [int64]$esperado.Bytes -or $registro.SHA256 -ne $esperado.SHA256) {
        throw 'Tamanho ou SHA-256 divergente; backup não comprovado'
    }
}
[pscustomobject]@{ Resultado = 'Mídias verificadas'; Arquivos = $atuais.Count; Algoritmo = 'SHA256' }
