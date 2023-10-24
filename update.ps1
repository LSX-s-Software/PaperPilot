$subtrees = @("coordinator", "file", "paper", "project", "reflection", "test", "translation", "user", "monitor", "monitor-client")

$command = "git pull"
Write-Host "run: $command"
Invoke-Expression $command

foreach ($subtree in $subtrees) {
    $prefix = "paperpilot-backend-$subtree"
    $branch = "main"
    
    $command = "git subtree pull --prefix=$prefix $subtree $branch"
    
    Write-Host "run: $command"
    
    Invoke-Expression $command
}
