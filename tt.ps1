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
        & "C:\Users\larry\usr\Python\Python38\python.exe" "C:\projects\desktop-writer\texteditor_cli.py" $args
        return
    }
    
    # 如果命令行为空，直接传递 $args
    if ([string]::IsNullOrWhiteSpace($line)) {
        & "C:\Users\larry\usr\Python\Python38\python.exe" "C:\projects\desktop-writer\texteditor_cli.py" $args
        return
    }
    
    # 解析命令行，处理引号和空格
    $processedArgs = @()
    $currentArg = ""
    $inQuotes = $false
    $quoteChar = $null
    
    for ($i = 0; $i -lt $line.Length; $i++) {
        $char = $line[$i]
        
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
    & "C:\Users\larry\usr\Python\Python38\python.exe" "C:\projects\desktop-writer\texteditor_cli.py" $processedArgs
}