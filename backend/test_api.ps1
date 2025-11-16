# AI API 完整测试脚本
$baseUrl = "http://localhost:8000"

Write-Host "=== UniPulse AI API 测试 ===" -ForegroundColor Cyan
Write-Host ""

# 步骤1：登录获取token
Write-Host "[1] 登录获取JWT Token..." -ForegroundColor Green
try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/login/" `
      -Method POST `
      -ContentType "application/json" `
      -Body (@{
        email = "g0184036940@gmail.com"
        password = "Jeffrey0418."
      } | ConvertTo-Json)
    
    $token = $loginResponse.data.access
    Write-Host "✅ 登录成功！" -ForegroundColor Green
    Write-Host "Token: $($token.Substring(0,30))..." -ForegroundColor Yellow
    
    # 设置headers
    $headers = @{
        "Authorization" = "Bearer $token"
    }
} catch {
    Write-Host "❌ 登录失败: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 步骤2：测试健康检查
Write-Host "[2] 测试健康检查API..." -ForegroundColor Green
try {
    $healthResponse = Invoke-RestMethod -Uri "$baseUrl/api/ai/health/" `
      -Method GET `
      -Headers $headers
    
    Write-Host "✅ 健康检查成功！" -ForegroundColor Green
    Write-Host ($healthResponse | ConvertTo-Json -Depth 3)
} catch {
    Write-Host "❌ 健康检查失败: $_" -ForegroundColor Red
}

Write-Host ""

# 步骤3：测试同步聊天
Write-Host "[3] 测试同步聊天API..." -ForegroundColor Green
try {
    $syncResponse = Invoke-RestMethod -Uri "$baseUrl/api/ai/chat/sync/" `
      -Method POST `
      -Headers ($headers + @{"Content-Type" = "application/json"}) `
      -Body (@{
        question = "用一句话解释微积分"
        use_rag = $false
      } | ConvertTo-Json)
    
    Write-Host "✅ 同步聊天成功！" -ForegroundColor Green
    Write-Host "问题: 用一句话解释微积分"
    Write-Host "回答: $($syncResponse.answer)"
    Write-Host "响应时间: $($syncResponse.elapsed_ms)ms"
} catch {
    Write-Host "❌ 同步聊天失败: $_" -ForegroundColor Red
}

Write-Host ""

# 步骤4：测试流式聊天（简化版，完整流式需要特殊处理）
Write-Host "[4] 测试RAG问答..." -ForegroundColor Green
try {
    $ragResponse = Invoke-RestMethod -Uri "$baseUrl/api/ai/chat/sync/" `
      -Method POST `
      -Headers ($headers + @{"Content-Type" = "application/json"}) `
      -Body (@{
        question = "如何申请图书馆卡？"
        use_rag = $true
      } | ConvertTo-Json)
    
    Write-Host "✅ RAG问答成功！" -ForegroundColor Green
    Write-Host "问题: 如何申请图书馆卡？"
    Write-Host "回答: $($ragResponse.answer)"
} catch {
    Write-Host "❌ RAG问答失败: $_" -ForegroundColor Red
    Write-Host "错误详情: $_"
}

Write-Host ""
Write-Host "=== 测试完成 ===" -ForegroundColor Cyan