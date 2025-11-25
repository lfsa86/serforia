$path = 'D:\D-Gilmer\lilab\DIN\naturai-serfor-demo\init\entrypoint.sh'
$text = [System.IO.File]::ReadAllText($path) -replace "`r",''
[System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "File converted to Unix format without BOM"
