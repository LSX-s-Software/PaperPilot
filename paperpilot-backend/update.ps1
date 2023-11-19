$projects = @("coordinator", "file", "paper", "project", "reflection", "test", "translation", "user", "monitor", "monitor-client", "ai", "im")

$command = "git pull"
Write-Host "run: $command"
Invoke-Expression $command

foreach ($project in $projects) {
    $prefix = "paperpilot-backend-$project"
    $branch = "main"
    $subtree = "https://github.com/Nagico/$prefix.git"
    
    if (-not (Test-Path -Path $prefix -PathType Container)) {
        $command = "git subtree add --prefix=$prefix $subtree $branch"
        Write-Host "run: $command"
        Invoke-Expression $command
    } else {
        $command = "git subtree pull --prefix=$prefix $subtree $branch"
        Write-Host "run: $command"
        Invoke-Expression $command
    }
}
