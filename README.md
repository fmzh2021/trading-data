# 招商银行股票实时监控

这是一个基于 GitHub Actions 的股票监控项目，可以定时获取招商银行（600036）的实时股票信息并推送到指定渠道。

## 功能特点

- ✅ 支持多个数据源：新浪财经、东方财富、雪球
- ✅ 自动故障转移：如果一个数据源失败，自动尝试下一个
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
└── README.md                     # 项目说明文档
```

## 使用方法

### 1. 推送服务说明

本项目使用 Bark 推送服务，推送地址为：`http://notice.xmwefun.cn/?type=bark&title=${title}&msg=${msg}`

推送服务会自动将股票信息推送到您的设备，无需额外配置。

### 2. 修改监控时间

编辑 `.github/workflows/stock-monitor.yml` 文件中的 cron 表达式来调整监控时间：

```yaml
schedule:
  - cron: '30 1,2,3,5,6,7 * * 1-5'  # 周一至周五
```

时间说明：
- GitHub Actions 使用 UTC 时间
- 北京时间 = UTC + 8
- 示例：`30 1` (UTC) = `09:30` (北京时间)

### 3. 手动触发

在 GitHub 仓库的 Actions 页面，选择 "招商银行股票监控" 工作流，点击 "Run workflow" 即可手动触发。

### 4. 推送消息说明

推送消息包含：
- **标题**：股票名称、当前价格和涨跌幅（如：📈 招商银行 42.50元 (+1.23%)）
- **内容**：详细的股票信息，包括开盘价、收盘价、最高价、最低价、成交量、成交额等

## 数据源说明

### 新浪财经
- API: `http://hq.sinajs.cn/list=sh600036`
- 优点：响应快，数据实时
- 缺点：需要解析特殊格式

### 东方财富
- API: `http://push2.eastmoney.com/api/qt/stock/get`
- 优点：数据完整，接口稳定
- 缺点：需要正确的股票代码格式

### 雪球
- API: `https://stock.xueqiu.com/v5/stock/quote.json`
- 优点：数据详细
- 缺点：可能需要登录 token

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

```bash
python stock_monitor.py
```

### 推送服务

推送服务使用 Bark，无需配置环境变量，脚本会自动推送到 `http://notice.xmwefun.cn/` 服务。

## 注意事项

1. **API 限制**：免费 API 可能有请求频率限制，请合理设置监控频率
2. **数据准确性**：本工具仅用于监控，不保证数据的绝对准确性
3. **交易时间**：建议只在交易时间段（9:30-15:00）监控
4. **隐私安全**：请妥善保管 GitHub Secrets，不要泄露敏感信息

## 扩展功能

### 修改监控股票

编辑 `stock_monitor.py` 中的股票代码：

```python
fetcher = StockDataFetcher(stock_code="600036")  # 改为其他股票代码
```

### 添加新的数据源

在 `StockDataFetcher` 类中添加新的获取方法，并在 `fetch_data` 方法中调用。

### 修改推送服务

如需修改推送服务地址，编辑 `stock_monitor.py` 中的 `StockNotifier` 类的 `bark_url` 属性。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

