# 股票实时监控

这是一个基于 GitHub Actions 的股票监控项目，可以定时获取多只股票的实时信息并推送到指定渠道。支持监控多只股票（用逗号分隔）。

## 功能特点

- ✅ 支持多个股票代码：可同时监控多只股票（用逗号分隔）
- ✅ 支持多个数据源：新浪财经、东方财富、雪球
- ✅ 自动故障转移：如果一个数据源失败，自动尝试下一个
- ✅ 自动识别市场：自动识别上海、深圳、创业板股票
- ✅ Bark 推送：使用 Bark 服务推送股票信息到手机
- ✅ 定时监控：支持在交易时间段自动执行
- ✅ 手动触发：支持通过 GitHub Actions 手动触发

## 项目结构

```
.
├── .github/
│   └── workflows/
│       └── stock-monitor.yml    # GitHub Actions 工作流配置
├── stock_monitor.py              # 股票监控主程序
├── requirements.txt              # Python 依赖
├── trigger_workflow.sh           # 触发 workflow 的便捷脚本
└── README.md                     # 项目说明文档
```

## 使用方法

### 1. 配置股票代码

#### GitHub Actions 配置（推荐）

**方式一：Repository Variables（推荐）**

在 GitHub 仓库的 Settings > Secrets and variables > Actions > Variables 标签页中添加：

- 变量名：`STOCK_CODES`
- 变量值：`600036,000001,300001`（多个用逗号分隔）

**方式二：Repository Secrets**

在 GitHub 仓库的 Settings > Secrets and variables > Actions > Secrets 标签页中添加：

- Secret 名：`STOCK_CODES`
- Secret 值：`600036,000001,300001`（多个用逗号分隔）

**方式三：手动触发时输入**

在 GitHub Actions 页面手动触发时，可以在输入框中直接输入股票代码。

**优先级说明：**
1. 手动触发时输入的股票代码（最高优先级）
2. Repository Variables 中的 `STOCK_CODES`
3. Repository Secrets 中的 `STOCK_CODES`
4. 默认值 `600036`（招商银行）

**股票代码示例：**
- `600036` - 招商银行（上海）
- `000001` - 平安银行（深圳）
- `300001` - 特锐德（创业板）

#### 本地运行配置

**方式一：环境变量**
```bash
export STOCK_CODES=600036,000001,300001
python stock_monitor.py
```

**方式二：命令行参数**
```bash
python stock_monitor.py --codes 600036,000001,300001
# 或使用简写
python stock_monitor.py -c 600036,000001,300001
```

### 2. 推送服务说明

本项目使用 Bark 推送服务，推送地址为：`http://notice.xmwefun.cn/?type=bark&title=${title}&msg=${msg}`

推送服务会自动将股票信息推送到您的设备，无需额外配置。每只股票会单独推送一条消息。

### 3. 修改监控时间

编辑 `.github/workflows/stock-monitor.yml` 文件中的 cron 表达式来调整监控时间：

```yaml
schedule:
  - cron: '30 1,2,3,5,6,7 * * 1-5'  # 周一至周五
```

时间说明：
- GitHub Actions 使用 UTC 时间
- 北京时间 = UTC + 8
- 示例：`30 1` (UTC) = `09:30` (北京时间)

### 4. 手动触发

#### 方式一：GitHub Web 界面

在 GitHub 仓库的 Actions 页面，选择 "股票实时监控" 工作流，点击 "Run workflow" 按钮，可选择输入股票代码，然后点击 "Run workflow" 即可手动触发。

#### 方式二：使用 curl 命令

通过 GitHub API 使用 curl 命令触发 workflow：

```bash
# 基本命令（使用默认或配置的股票代码）
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/stock-monitor.yml/dispatches \
  -d '{"ref":"main"}'

# 指定股票代码
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/stock-monitor.yml/dispatches \
  -d '{"ref":"main","inputs":{"stock_codes":"600036,000001,300001"}}'
```

**参数说明：**
- `YOUR_GITHUB_TOKEN`: 您的 GitHub Personal Access Token（需要 `repo` 权限）
- `OWNER`: GitHub 用户名或组织名
- `REPO`: 仓库名称
- `stock-monitor.yml`: workflow 文件名（如果文件名不同，请修改）
- `main`: 分支名称（根据您的默认分支修改）
- `stock_codes`: 股票代码，多个用逗号分隔（可选，不传则使用配置的默认值）

**获取 GitHub Token：**
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" > "Generate new token (classic)"
3. 设置名称和过期时间
4. 勾选 `repo` 权限
5. 生成并复制 token

**示例（替换为实际值）：**
```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ghp_xxxxxxxxxxxxxxxxxxxx" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/your-username/trading-data/actions/workflows/stock-monitor.yml/dispatches \
  -d '{"ref":"main","inputs":{"stock_codes":"600036,000001"}}'
```

#### 方式三：使用便捷脚本（推荐）

项目提供了便捷脚本 `trigger_workflow.sh`，使用更简单：

```bash
# 1. 设置环境变量（只需设置一次）
export GITHUB_TOKEN=your_github_token
export GITHUB_OWNER=your-username
export GITHUB_REPO=trading-data

# 2. 运行脚本（使用默认股票代码 600036）
./trigger_workflow.sh

# 3. 或指定股票代码
./trigger_workflow.sh 600036,000001,300001
```

**脚本说明：**
- 脚本会自动检查配置并给出提示
- 支持通过命令行参数指定股票代码
- 显示执行状态和结果

### 5. 推送消息说明

推送消息包含：
- **标题**：股票名称、当前价格和涨跌幅（如：📈 招商银行 42.50元 (+1.23%)）
- **内容**：详细的股票信息，包括开盘价、收盘价、最高价、最低价、成交量、成交额等

## 数据源说明

### 新浪财经
- API: `http://hq.sinajs.cn/list=sh600036` 或 `sz000001`
- 优点：响应快，数据实时
- 缺点：需要解析特殊格式
- 自动识别：上海（6开头）或深圳（0/3开头）

### 东方财富
- API: `http://push2.eastmoney.com/api/qt/stock/get`
- 优点：数据完整，接口稳定
- 缺点：需要正确的股票代码格式
- 自动识别：上海（secid=1）或深圳（secid=0）

### 雪球
- API: `https://stock.xueqiu.com/v5/stock/quote.json`
- 优点：数据详细
- 缺点：可能需要登录 token
- 自动识别：SH（上海）或 SZ（深圳）

## 推送消息格式

推送的消息包含以下信息：
- 股票名称和代码
- 当前价格
- 涨跌金额和幅度
- 今日开盘价、昨日收盘价
- 今日最高价、最低价
- 成交量和成交额
- 更新时间

## 本地测试

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行脚本

**监控单只股票（默认招商银行）：**
```bash
python stock_monitor.py
```

**监控多只股票：**
```bash
# 使用命令行参数
python stock_monitor.py --codes 600036,000001,300001

# 或使用环境变量
export STOCK_CODES=600036,000001,300001
python stock_monitor.py
```

### 推送服务

推送服务使用 Bark，无需配置环境变量，脚本会自动推送到 `http://notice.xmwefun.cn/` 服务。

## 注意事项

1. **API 限制**：免费 API 可能有请求频率限制，请合理设置监控频率
2. **数据准确性**：本工具仅用于监控，不保证数据的绝对准确性
3. **交易时间**：建议只在交易时间段（9:30-15:00）监控
4. **隐私安全**：请妥善保管 GitHub Secrets，不要泄露敏感信息

## 股票代码说明

### 支持的股票类型

- **上海股票**：6开头，如 `600036`（招商银行）、`600519`（贵州茅台）
- **深圳主板**：0开头，如 `000001`（平安银行）、`000002`（万科A）
- **创业板**：3开头，如 `300001`（特锐德）、`300015`（爱尔眼科）

### 股票代码示例

常见股票代码：
- `600036` - 招商银行（上海）
- `600519` - 贵州茅台（上海）
- `000001` - 平安银行（深圳）
- `000002` - 万科A（深圳）
- `300001` - 特锐德（创业板）
- `300015` - 爱尔眼科（创业板）

## 扩展功能

### 修改监控股票

通过环境变量或命令行参数配置，无需修改代码：

```bash
# 方式一：环境变量
export STOCK_CODES=600036,000001,300001

# 方式二：命令行参数
python stock_monitor.py --codes 600036,000001,300001
```

### 添加新的数据源

在 `StockDataFetcher` 类中添加新的获取方法，并在 `fetch_data` 方法中调用。

### 修改推送服务

如需修改推送服务地址，编辑 `stock_monitor.py` 中的 `StockNotifier` 类的 `bark_url` 属性。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

