param(
    [Parameter(Mandatory = $true)][string]$TreeRoot,
    [Parameter(Mandatory = $true)][string]$InventoryPath,
    [Parameter(Mandatory = $true)][string]$InventorySha256
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Import-Module -Name (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Management/Microsoft.PowerShell.Management.psd1')
Import-Module -Name (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Utility/Microsoft.PowerShell.Utility.psd1')

# The inventory digest must come from independent retained trust, before this tree is executed.
if ($InventorySha256 -notmatch '^[0-9a-fA-F]{64}$' -or
    (Get-FileHash -LiteralPath $InventoryPath -Algorithm SHA256).Hash -ne $InventorySha256) {
    throw 'Inventory differs from the independent pin'
}
$record = Get-Content -LiteralPath $InventoryPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($record.format -cne 'BYTE-TREE-SHA256-NFC' -or @($record.excludes).Count -ne 0) {
    throw 'Only complete private inventories are supported'
}
$absoluteRoot = [IO.Path]::GetFullPath($TreeRoot)
$root = $absoluteRoot.TrimEnd('\', '/')
if ($root -eq [IO.Path]::GetPathRoot($absoluteRoot).TrimEnd('\', '/')) { throw 'Bundle must be a subdirectory' }
$ancestor = Get-Item -LiteralPath $root -Force
if (-not $ancestor.PSIsContainer) { throw 'Missing bundle directory' }
while ($null -ne $ancestor) {
    if ($ancestor.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse point in bundle root' }
    $ancestor = $ancestor.Parent
}
$expected = [Collections.Generic.Dictionary[string,object]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($entry in $record.entries) {
    $name = [string]$entry.path
    $parts = $name.Split('/')
    if (-not $name -or $name.Contains('\') -or -not [StringComparer]::Ordinal.Equals($name, $name.Normalize()) -or
        $name.StartsWith('/') -or $name.Contains(':') -or
        @($parts | Where-Object { $_ -in @('', '.', '..') -or $_.EndsWith('.') -or $_.EndsWith(' ') }).Count -ne 0 -or
        $entry.type -cnotin @('file', 'directory') -or $expected.ContainsKey($name)) {
        throw 'Unsupported or duplicate inventory path'
    }
    $expected.Add($name, $entry)
}
$pending = [Collections.Generic.Queue[string]]::new()
$pending.Enqueue($root)
$count = 0
while ($pending.Count -gt 0) {
    foreach ($item in Get-ChildItem -LiteralPath $pending.Dequeue() -Force) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse point in bundle' }
        $relative = $item.FullName.Substring($root.Length + 1).Replace('\', '/')
        if (-not $expected.ContainsKey($relative)) { throw "Unexpected bundle entry: $relative" }
        $entry = $expected[$relative]
        if ($item.PSIsContainer) {
            if ($entry.type -ne 'directory') { throw "Entry type changed: $relative" }
            $pending.Enqueue($item.FullName)
        } else {
            if ($entry.type -ne 'file' -or $item.Length -ne $entry.size -or
                (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash -ne $entry.sha256) {
                throw "Bundle bytes changed: $relative"
            }
        }
        $count++
    }
}
if ($count -ne $expected.Count) { throw 'Missing bundle entries' }
@{ format = 'WINDOWS-OFFLINE-BUNDLE-VERIFICATION'; status = 'PASS'; entries = $count;
   inventory_sha256 = $InventorySha256; scope = 'Windows bytes and entry types; POSIX mode restoration is checked separately' } | ConvertTo-Json -Compress
