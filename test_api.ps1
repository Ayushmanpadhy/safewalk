$resp = Invoke-WebRequest -Uri "http://localhost:5000/api/scores/heatmap" -UseBasicParsing -TimeoutSec 10
$body = $resp.Content
Write-Host "Status:" $resp.StatusCode
Write-Host "Length:" $body.Length
Write-Host "First300:" $body.Substring(0, [Math]::Min(300, $body.Length))
