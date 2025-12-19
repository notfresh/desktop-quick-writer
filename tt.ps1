function Say-Hello { "Hello, World!" }

function mingw{
    $env:PATH = "C:\usr\msys64\mingw64\bin;C:\usr\msys64\usr\bin;$env:PATH";$env:MSYSTEM = "MINGW64";
    & "C:\usr\msys64\usr\bin\bash.exe" 
}

function tt{
    # 获取原始命令行，解析包含 # 的参数
    $line = $MyInvocation.Line.Trim()
    
    # 更精确地移除函数名 "tt"，确保不会误匹配
    # 匹配模式：开头的 "tt" 后面跟空格或行尾
    if ($line -match '^tt\s+(.+)$') {
        $line = $matches[1]
    } elseif ($line -match '.*?;\s*tt\s+(.+)$') {
        # 处理 ". $PROFILE; tt add ..." 这种情况
        $line = $matches[1]
    } elseif ($line -eq 'tt') {
        # 如果只有 "tt"，没有参数
        $line = ""
    } else {
        # 如果无法匹配，尝试使用 $args
        python "C:\projects\desktop-writer\texteditor_cli.py" $args
        return
    }
    
    # 如果命令行为空，直接传递 $args
    if ([string]::IsNullOrWhiteSpace($line)) {
        python "C:\projects\desktop-writer\texteditor_cli.py" $args
        return
    }
    
    # 先让PowerShell展开变量（替换 $变量名 为实际值）
    # 使用双引号字符串让PowerShell自动展开变量
    try {
        # 方法：将 $line 作为双引号字符串的一部分，让PowerShell展开变量
        # 使用 Invoke-Expression 来执行双引号字符串，这样变量会被自动展开
        # 但我们需要小心，只展开变量，不执行命令
        $expandedLine = Invoke-Expression "`"$line`""
        
        # 如果展开失败或结果异常，回退到手动查找
        if (-not $expandedLine -or $expandedLine -eq $line) {
            # 手动查找变量
            $variablePattern = '\$([a-zA-Z_][a-zA-Z0-9_]*)'
            $matches = [regex]::Matches($line, $variablePattern)
            
            if ($matches.Count -gt 0) {
                $expandedLine = $line
                # 从后往前替换
                for ($i = $matches.Count - 1; $i -ge 0; $i--) {
                    $match = $matches[$i]
                    $varName = $match.Groups[1].Value
                    
                    # 尝试查找变量（优先全局作用域）
                    $varValue = $null
                    try {
                        $varValue = Get-Variable -Name $varName -Scope Global -ErrorAction Stop
                    } catch {
                        try {
                            $varValue = Get-Variable -Name $varName -Scope Local -ErrorAction Stop
                        } catch {
                            for ($scope = 0; $scope -le 5; $scope++) {
                                try {
                                    $varValue = Get-Variable -Name $varName -Scope $scope -ErrorAction Stop
                                    break
                                } catch {
                                    continue
                                }
                            }
                        }
                    }
                    
                    if ($varValue) {
                        $value = $varValue.Value
                        $valueStr = if ($value -is [string]) { $value } else { $value.ToString() }
                        if ($valueStr -match '\s' -or $valueStr -match "`n" -or $valueStr -match "`r" -or $valueStr.Contains('"')) {
                            $valueStr = $valueStr.Replace('"', '`"')
                            $valueStr = "`"$valueStr`""
                        }
                        $expandedLine = $expandedLine.Substring(0, $match.Index) + $valueStr + $expandedLine.Substring($match.Index + $match.Length)
                    }
                }
            } else {
                $expandedLine = $line
            }
        }
    } catch {
        # 如果展开失败，使用原始行
        $expandedLine = $line
    }
    
    # 使用PowerShell内置的参数解析，更可靠
    # 将命令行字符串转换为参数数组
    try {
        # 更简单的方法：使用PowerShell的解析功能
        # 注意：现在使用展开后的行
        $processedArgs = $expandedLine -split '\s+(?=(?:[^'']*''[^'']*'')*[^'']*$)' | Where-Object { $_ -ne '' }
        
        # 执行命令
        python "C:\projects\desktop-writer\texteditor_cli.py" $processedArgs
    } catch {
        # 如果解析失败，尝试使用更简单的方法：直接传递整个命令行
        # 但argparse需要参数数组，所以我们需要手动解析
        # 注意：使用展开后的行
        $processedArgs = @()
        $currentArg = ""
        $inQuotes = $false
        $quoteChar = $null
        
        for ($i = 0; $i -lt $expandedLine.Length; $i++) {
            $char = $expandedLine[$i]
            
            if ($char -eq '"' -or $char -eq "'") {
                if (-not $inQuotes) {
                    $inQuotes = $true
                    $quoteChar = $char
                } elseif ($char -eq $quoteChar) {
                    $inQuotes = $false
                    $quoteChar = $null
                } else {
                    $currentArg += $char
                }
            } elseif ($char -eq ' ' -and -not $inQuotes) {
                if ($currentArg -ne "") {
                    $processedArgs += $currentArg
                    $currentArg = ""
                }
            } else {
                $currentArg += $char
            }
        }
        
        # 添加最后一个参数
        if ($currentArg -ne "") {
            $processedArgs += $currentArg
        }
        
        # 执行命令
        python "C:\projects\desktop-writer\texteditor_cli.py" $processedArgs
    }
}