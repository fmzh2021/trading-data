#!/bin/bash
# 触发 GitHub Actions Workflow 的便捷脚本
# 使用方法: ./trigger_workflow.sh [股票代码]
# 示例: ./trigger_workflow.sh 600036,000001,300001

# 配置信息（请修改为您的实际值）
GITHUB_TOKEN="${GITHUB_TOKEN:-YOUR_GITHUB_TOKEN}"
OWNER="${GITHUB_OWNER:-your-username}"
REPO="${GITHUB_REPO:-trading-data}"
BRANCH="${GITHUB_BRANCH:-main}"
WORKFLOW_FILE="stock-monitor.yml"

# 股票代码（从命令行参数获取，或使用默认值）
STOCK_CODES="${1:-600036}"

# 检查 token 是否配置
if [ "$GITHUB_TOKEN" = "YOUR_GITHUB_TOKEN" ]; then
    echo "❌ 错误: 请设置 GITHUB_TOKEN 环境变量"
    echo "使用方法:"
    echo "  export GITHUB_TOKEN=your_token"
    echo "  export GITHUB_OWNER=your-username"
    echo "  export GITHUB_REPO=trading-data"
    echo "  ./trigger_workflow.sh 600036,000001"
    exit 1
fi

# 构建 API URL
API_URL="https://api.github.com/repos/${OWNER}/${REPO}/actions/workflows/${WORKFLOW_FILE}/dispatches"

# 发送请求
echo "🚀 触发股票监控 workflow..."
echo "📊 股票代码: ${STOCK_CODES}"
echo "🔗 API URL: ${API_URL}"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "${API_URL}" \
  -d "{\"ref\":\"${BRANCH}\",\"inputs\":{\"stock_codes\":\"${STOCK_CODES}\"}}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "204" ]; then
    echo "✅ Workflow 触发成功！"
    echo "📱 请查看 GitHub Actions 页面查看执行状态"
else
    echo "❌ Workflow 触发失败"
    echo "HTTP 状态码: ${HTTP_CODE}"
    echo "响应内容: ${BODY}"
    exit 1
fi

