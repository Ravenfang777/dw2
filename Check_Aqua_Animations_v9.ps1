param([string]$OpenKHRoot)
$ErrorActionPreference = 'Stop'
$lines = New-Object 'System.Collections.Generic.List[string]'
function Note([string]$Text) {
    $lines.Add($Text)
    Write-Host $Text
}
$reportPath = Join-Path $PSScriptRoot 'Aqua_Animation_Check_v9.txt'
try {
    Note 'KH1FM AQUA ANIMATION TEST v9 - READ-ONLY INSTALLATION AND CRASH CHECK'
    Note ('Checked: ' + (Get-Date).ToString('o'))
    if ([string]::IsNullOrWhiteSpace($OpenKHRoot)) {
        $OpenKHRoot = Join-Path $env:USERPROFILE 'Desktop\Organized Projects\0 Kingdom Hearts Mods\openkh'
    }
    $OpenKHRoot = [System.IO.Path]::GetFullPath($OpenKHRoot)
    $compiled = Join-Path $OpenKHRoot 'mod\kh1'
    Note ('OpenKH: ' + $OpenKHRoot)
    Note ('Compiled KH1 folder: ' + $compiled)
    $installOK = $true
    if (-not (Test-Path -LiteralPath $compiled -PathType Container)) {
        Note 'FAIL: Compiled KH1 folder not found. Drag your OpenKH folder onto CHECK_AQUA_V9.cmd.'
        $installOK = $false
    } else {
        $expected = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'expected_assets.json') -Raw | ConvertFrom-Json
        foreach ($asset in $expected.assets) {
            $target = Join-Path $compiled $asset.name
            if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
                Note ('FAIL: Missing compiled asset: ' + $target)
                $installOK = $false
                continue
            }
            $hash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
            Note ($asset.name + ' SHA256=' + $hash)
            if ($hash -eq $asset.sha256) {
                Note ('PASS: Aqua v9 asset matches: ' + $asset.name)
            } else {
                Note ('FAIL: Compiled file does not match the Aqua v9 asset: ' + $asset.name)
                $installOK = $false
            }
        }
        $legacy = @(Get-ChildItem -LiteralPath $compiled -Recurse -File -Filter 'kh1-dual-wield.dll' -ErrorAction SilentlyContinue)
        if ($legacy.Count -gt 0) {
            $installOK = $false
            foreach ($dll in $legacy) { Note ('FAIL: v52/dual-wield DLL remains in compiled mods: ' + $dll.FullName) }
            Note 'Disable the Nine Styles / Dual Wield mod and rebuild. If the DLL remains, move that compiled DLL to a backup folder outside openkh\mod and rerun this check.'
        } else { Note 'PASS: No kh1-dual-wield.dll in the compiled KH1 folder.' }
    }
    $games = @(Get-Process -Name 'KINGDOM HEARTS FINAL MIX' -ErrorAction SilentlyContinue)
    foreach ($game in $games) {
        Note ('Game process is running: PID ' + $game.Id + '. Fully exit before the next launch.')
        try {
            foreach ($module in $game.Modules) {
                if ($module.ModuleName -ieq 'kh1-dual-wield.dll') {
                    Note ('FAIL: Old DLL is already loaded in the running process: ' + $module.FileName)
                    $installOK = $false
                }
            }
        } catch { Note 'Could not inspect running modules; installation-file checks above still apply.' }
    }
    if ($installOK) {
        Note 'INSTALL CHECK PASSED. This verifies files and the old DLL path, not gameplay stability.'
    } else { Note 'INSTALL CHECK FAILED. Resolve the FAIL entries before testing again.' }
    Note ''
    Note 'RECENT KH1 APPLICATION CRASH EVENTS'
    try {
        $events = @(Get-WinEvent -FilterHashtable @{LogName='Application'; ProviderName='Application Error'; StartTime=(Get-Date).AddDays(-2)} -MaxEvents 100 -ErrorAction Stop)
        $matched = @($events | Where-Object { $_.Message -match 'KINGDOM HEARTS FINAL MIX\.exe' } | Select-Object -First 3)
        if ($matched.Count -eq 0) { Note 'No matching recent Windows Application Error event was found.' }
        foreach ($event in $matched) {
            Note ('Event time: ' + $event.TimeCreated.ToString('o') + '; ID=' + $event.Id)
            Note $event.Message
            Note ''
        }
    } catch { Note ('Application crash events unavailable: ' + $_.Exception.Message) }
} catch {
    Note ('CHECK ERROR: ' + $_.Exception.Message)
} finally {
    $lines | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Host ''
    Write-Host ('Report saved: ' + $reportPath)
    Write-Host 'Return Aqua_Animation_Check_v9.txt with your test result.'
}
