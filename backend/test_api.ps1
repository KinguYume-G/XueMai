# UniPulse AI API 完整测试脚本
# 用法: powershell -ExecutionPolicy Bypass -File test_api.ps1

param(
    [string]$BaseUrl = "http://localhost:8000/api",
    [switch]$Verbose
)

Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "    UniPulse Asia - AI API 测试套件" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════`n" -ForegroundColor Cyan

# 自动获取 Token
Write-Host "🔑 正在获取 JWT Token..." -ForegroundColor Yellow

if (Test-Path ".jwt_token") {
    $token = Get-Content ".jwt_token" -Raw
    $token = $token.Trim()
    Write-Host "✅ 从缓存读取 Token" -ForegroundColor Green
} else {
    try {
        $tokenOutput = python get_token.py 2>&1 | Out-String
        $tokenMatch = [regex]::Match($tokenOutput, "eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*")
        
        if ($tokenMatch.Success) {
            $token = $tokenMatch.Value
            Write-Host "✅ Token 生成成功" -ForegroundColor Green
        } else {
            Write-Host "❌ Token 生成失败" -ForegroundColor Red
            Write-Host $tokenOutput
            exit 1
        }
    } catch {
        Write-Host "❌ 无法生成 Token: $_" -ForegroundColor Red
        exit 1
    }
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json; charset=utf-8"
}

# 测试计数器
$passed = 0
$failed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Endpoint,
        [hashtable]$Body = $null,
        [switch]$ExpectError
    )
    
    Write-Host "`n🧪 测试: $Name" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    
    try {
        $uri = "$BaseUrl$Endpoint"
        $params = @{
            Uri = $uri
            Method = $Method
            Headers = $headers
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10 -Compress)
            $params.ContentType = "application/json; charset=utf-8"
        }
        
        $startTime = Get-Date
        $response = Invoke-RestMethod @params
        $elapsed = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($ExpectError) {
            Write-Host "❌ 应该返回错误但成功了" -ForegroundColor Red
            $script:failed++
            return $false
        }
        
        Write-Host "✅ 成功 (耗时: $([math]::Round($elapsed, 0))ms)" -ForegroundColor Green
        
        if ($Verbose) {
            $response | ConvertTo-Json -Depth 5 | Write-Host
        } else {
            # 显示关键信息
            if ($response.status) {
                Write-Host "   状态: $($response.status)" -ForegroundColor White
            }
            if ($response.answer) {
                $preview = $response.answer.Substring(0, [Math]::Min(80, $response.answer.Length))
                Write-Host "   回答: $preview..." -ForegroundColor White
            }
            if ($null -ne $response.used_rag) {
                Write-Host "   RAG: $($response.used_rag)" -ForegroundColor White
            }
            if ($response.model) {
                Write-Host "   模型: $($response.model)" -ForegroundColor White
            }
            if ($response.elapsed_ms) {
                Write-Host "   AI耗时: $($response.elapsed_ms)ms" -ForegroundColor White
            }
        }
        
        $script:passed++
        return $true
    } catch {
        if ($ExpectError) {
            Write-Host "✅ 正确返回错误: $($_.Exception.Message)" -ForegroundColor Green
            $script:passed++
            return $true
        }
        
        Write-Host "❌ 失败: $($_.Exception.Message)" -ForegroundColor Red
        
        if ($Verbose -and $_.Exception.Response) {
            try {
                $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                $responseBody = $reader.ReadToEnd()
                Write-Host "   响应详情: $responseBody" -ForegroundColor Red
            } catch {}
        }
        
        $script:failed++
        return $false
    }
}

# 检查服务器
Write-Host "`n🔍 检查 Django 服务器..." -ForegroundColor Yellow
try {
    $null = Invoke-WebRequest -Uri "http://localhost:8000" -UseBasicParsing -TimeoutSec 2
    Write-Host "✅ Django 服务器正在运行`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Django 服务器未运行！" -ForegroundColor Red
    Write-Host "   请先运行: python manage.py runserver`n" -ForegroundColor Yellow
    exit 1
}

# 执行测试
Test-Endpoint -Name "健康检查" -Method "GET" -Endpoint "/ai/health/"

Test-Endpoint -Name "同步聊天（无 RAG，英文）" -Method "POST" -Endpoint "/ai/chat/sync/" `
    -Body @{question = "Hello, who are you?"; use_rag = $false}

Test-Endpoint -Name "同步聊天（无 RAG，中文）" -Method "POST" -Endpoint "/ai/chat/sync/" `
    -Body @{question = "你好，介绍一下你自己"; use_rag = $false}

Test-Endpoint -Name "同步聊天（有 RAG）" -Method "POST" -Endpoint "/ai/chat/sync/" `
    -Body @{question = "APU的全称是什么？"; use_rag = $true}

Test-Endpoint -Name "错误处理（空问题）" -Method "POST" -Endpoint "/ai/chat/sync/" `
    -Body @{question = ""; use_rag = $false} -ExpectError

# 流式聊天测试
Write-Host "`n🧪 测试: 流式聊天（SSE）" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "⚠️  流式响应测试（显示前 5 个事件）..." -ForegroundColor Yellow

$streamUrl = "$BaseUrl/ai/chat/stream/"
$streamBody = @{question = "What is AI?"; use_rag = $false} | ConvertTo-Json -Compress

try {
    $response = Invoke-WebRequest -Uri $streamUrl -Method POST `
        -Headers $headers -Body $streamBody -ContentType "application/json; charset=utf-8" -UseBasicParsing
    
    $lines = $response.Content -split "`n"
    $eventCount = 0
    
    foreach ($line in $lines) {
        if ($line.StartsWith("data: ")) {
            $eventCount++
            if ($eventCount -le 5) {
                Write-Host "   $line" -ForegroundColor White
            }
        }
    }
    
    Write-Host "✅ 流式聊天成功 (共 $eventCount 个事件)" -ForegroundColor Green
    $script:passed++
} catch {
    Write-Host "❌ 流式聊天失败: $($_.Exception.Message)" -ForegroundColor Red
    $script:failed++
}

# 总结
Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "    测试结果" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ 通过: $passed" -ForegroundColor Green
Write-Host "❌ 失败: $failed" -ForegroundColor Red

if ($failed -eq 0) {
    Write-Host "`n🎉 所有测试通过！系统运行正常！" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  部分测试失败，请检查日志" -ForegroundColor Yellow
}

Write-Host "═══════════════════════════════════════════════════`n" -ForegroundColor Cyan