# RoadSense Administrator Registration Script
$body = @{
    username = "roadsense_admin"
    email    = "admin@roadsense.gov"
    password = "12345678"
    is_admin = "True"
} | ConvertTo-Json

# Execute the POST request
$params = @{
    Uri         = "http://127.0.0.1:6969/auth/signup"
    Method      = "POST"
    Headers     = @{ "Content-Type" = "application/json; charset=utf-8" }
    Body        = $body
}

try {
    Invoke-RestMethod @params
    Write-Host "RoadSense Admin created successfully!" -ForegroundColor Green
} catch {
    $_.Exception.Response.GetResponseStream() | ForEach-Object {
        $reader = New-Object System.IO.StreamReader($_)
        $reader.ReadToEnd()
    }
}