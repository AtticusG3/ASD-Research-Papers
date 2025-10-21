# PowerShell script to ensure we're in the project directory
$ProjectDir = "C:\Users\Kev\Nextcloud\Documents\ASD Research Papers"
Set-Location $ProjectDir
Write-Host "Current directory: $(Get-Location)"
Write-Host "Running command: $($args -join ' ')"
& $args
