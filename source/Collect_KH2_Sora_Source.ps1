param([string]$SourceDirectory='', [string]$OutputDirectory='')
# Windows PowerShell5.1. Read extracted KH2 assets; write a separate capture.
# Never copies saves, executables, HED/PKG containers or unrelated character data.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
try {
    if ([string]::IsNullOrWhiteSpace($SourceDirectory)) {
        Add-Type -AssemblyName System.Windows.Forms
        $Dialog=New-Object System.Windows.Forms.FolderBrowserDialog
        $Dialog.Description='Choose your EXTRACTED KH2 data folder containing obj\P_EX100.mdlx and P_EX100.mset.'
        $Dialog.ShowNewFolderButton=$false
        if ($Dialog.ShowDialog() -ne [Windows.Forms.DialogResult]::OK) {exit 0}
        $SourceDirectory=$Dialog.SelectedPath
        $Dialog.Dispose()
    }
    $Root=(Resolve-Path -LiteralPath $SourceDirectory).ProviderPath
    if (-not [IO.Directory]::Exists($Root)) {throw 'The selected path is not a directory.'}
    if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {$OutputDirectory=$PSScriptRoot}
    [void][IO.Directory]::CreateDirectory($OutputDirectory)
    $Capture=Join-Path $OutputDirectory ('KH2_Sora_Source_'+(Get-Date -Format 'yyyyMMdd_HHmmss')+'_'+[guid]::NewGuid().ToString('N').Substring(0,6))
    [void][IO.Directory]::CreateDirectory($Capture)
    $Prefix=$Root.TrimEnd([char[]]'\/')+[IO.Path]::DirectorySeparatorChar
    $Queue=New-Object 'System.Collections.Generic.Queue[string]'
    $Queue.Enqueue($Root)
    $Rows=New-Object 'System.Collections.Generic.List[object]'
    $Notes=New-Object 'System.Collections.Generic.List[string]'
    [long]$Total=0
    while ($Queue.Count -gt 0) {
        foreach ($Item in @(Get-ChildItem -LiteralPath $Queue.Dequeue() -Force -ErrorAction SilentlyContinue)) {
            if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {continue}
            if ($Item.PSIsContainer) {
                if ($Item.Name -notlike 'KH2_Sora_Source_*') {$Queue.Enqueue($Item.FullName)}
                continue
            }
            if ($Item.Name -notin @('P_EX100.mdlx','P_EX100.mset')) {continue}
            $Relative=$Item.FullName.Substring($Prefix.Length)
            if ($Item.Length -lt 16 -or $Item.Length -gt 32MB -or ($Total+$Item.Length) -gt 64MB) {
                $Notes.Add('Skipped invalid/oversize candidate: '+$Relative);continue
            }
            $Stream=[IO.File]::OpenRead($Item.FullName)
            try {
                $Magic=New-Object byte[] 4
                [void]$Stream.Read($Magic,0,4)
                if ([BitConverter]::ToUInt32($Magic,0) -ne 0x01524142) {
                    $Notes.Add('Skipped candidate without KH2 BAR header: '+$Relative);continue
                }
            } finally {$Stream.Dispose()}
            $Destination=Join-Path (Join-Path $Capture 'Sources') $Relative
            [void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Destination))
            Copy-Item -LiteralPath $Item.FullName -Destination $Destination
            $Total+=$Item.Length
            $Rows.Add([pscustomobject]@{Source=$Relative;Bytes=$Item.Length;SHA256=(Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash})
        }
    }
    $Rows | Export-Csv -LiteralPath (Join-Path $Capture 'Sources.csv') -NoTypeInformation -Encoding UTF8
    if ($Rows.Count -eq 0) {$Notes.Add('No loose default KH2 Sora BAR files found. Select an extracted KH2 data/obj folder. Valor P_EX100_BTLF is not default Sora. This helper does not extract PKG files.')}
    $Notes | Set-Content -LiteralPath (Join-Path $Capture 'Notes.txt') -Encoding UTF8
    @('DEFAULT KH2 SORA SOURCE CAPTURE',('Files copied: '+$Rows.Count),
      'Needed: P_EX100.mdlx (skeleton) and P_EX100.mset (normal Sora motions).',
      'Upload this ZIP to finish the KH2 damage and knockback replacement.',
      'The Aqua v18 test currently uses native KH1 Sora reactions.') |
      Set-Content -LiteralPath (Join-Path $Capture 'README.txt') -Encoding UTF8
    $Inputs=@((Get-ChildItem -LiteralPath $Capture -Force).FullName)
    Compress-Archive -LiteralPath $Inputs -DestinationPath ($Capture+'.zip') -CompressionLevel Optimal
    Write-Host ('Created: '+$Capture+'.zip') -ForegroundColor Green
    Write-Host ('Copied '+$Rows.Count+' matching source files. See Notes.txt if either file is absent.')
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
