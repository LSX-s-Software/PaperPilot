# 定义一个存储子仓库的列表
$subtrees = @("coordinator", "file", "paper", "project", "reflection", "test", "translation", "user", "monitor", "monitor-client")

$command = "git pull"
Write-Host "run: $command"
# 执行 git pull
Invoke-Expression $command

# 遍历子仓库列表并执行 git subtree pull 命令
foreach ($subtree in $subtrees) {
    $prefix = "paperpilot-backend-$subtree"
    $branch = "main"
    
    $command = "git subtree pull --prefix=$prefix $subtree $branch"
    
    Write-Host "run: $command"
    
    # 执行 git subtree pull 命令
    Invoke-Expression $command
}
