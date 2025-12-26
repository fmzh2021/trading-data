#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票实时监控脚本
支持从多个数据源获取股票信息并推送
支持监控多个股票代码（逗号分隔）
"""

import os
import sys
import time
import requests
from datetime import datetime
from typing import Dict, Optional, List
from urllib.parse import quote
import argparse


class StockDataFetcher:
    """股票数据获取器 - 支持多个数据源"""
    
    def __init__(self, stock_code: str = "600036"):
        """
        初始化
        :param stock_code: 股票代码，如 600036（上海）、000001（深圳）、300001（创业板）
        """
        self.stock_code = stock_code.strip()
        self._detect_market()
    
    def _detect_market(self):
        """检测股票所属市场"""
        code = self.stock_code
        if code.startswith('6'):
            self.market = 'sh'  # 上海
            self.secid_prefix = '1'  # 东方财富用1表示上海
        elif code.startswith('0') or code.startswith('3'):
            self.market = 'sz'  # 深圳
            self.secid_prefix = '0'  # 东方财富用0表示深圳
        else:
            # 默认上海
            self.market = 'sh'
            self.secid_prefix = '1'
    
    def fetch_from_sina(self) -> Optional[Dict]:
        """从新浪财经获取股票数据"""
        try:
            # 新浪股票API: http://hq.sinajs.cn/list=sh600036 或 sz000001
            url = f"http://hq.sinajs.cn/list={self.market}{self.stock_code}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://finance.sina.com.cn'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gbk'
            
            if response.status_code == 200:
                data = response.text
                # 解析数据格式: var hq_str_sh600036="招商银行,42.50,42.60,..."
                if 'var hq_str' in data:
                    content = data.split('"')[1]
                    fields = content.split(',')
                    
                    if len(fields) >= 32:
                        return {
                            'source': '新浪财经',
                            'name': fields[0],
                            'open': float(fields[1]) if fields[1] else 0,
                            'yesterday_close': float(fields[2]) if fields[2] else 0,
                            'current': float(fields[3]) if fields[3] else 0,
                            'high': float(fields[4]) if fields[4] else 0,
                            'low': float(fields[5]) if fields[5] else 0,
                            'volume': int(float(fields[8])) if fields[8] else 0,
                            'amount': float(fields[9]) if fields[9] else 0,
                            'time': f"{fields[30]} {fields[31]}",
                        }
        except Exception as e:
            print(f"从新浪获取数据失败: {e}")
        return None
    
    def fetch_from_eastmoney(self) -> Optional[Dict]:
        """从东方财富获取股票数据"""
        try:
            # 东方财富API
            url = f"http://push2.eastmoney.com/api/qt/stock/get"
            params = {
                'secid': f"{self.secid_prefix}.{self.stock_code}",  # 1表示上海，0表示深圳
                'fields': 'f57,f58,f107,f137,f46,f44,f45,f47,f48,f60,f170',
                'fltt': 2
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://quote.eastmoney.com'
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    d = data['data']
                    return {
                        'source': '东方财富',
                        'name': d.get('f58', ''),
                        'code': d.get('f57', ''),
                        'current': d.get('f43', 0) / 100 if d.get('f43') else 0,
                        'open': d.get('f46', 0) / 100 if d.get('f46') else 0,
                        'yesterday_close': d.get('f60', 0) / 100 if d.get('f60') else 0,
                        'high': d.get('f44', 0) / 100 if d.get('f44') else 0,
                        'low': d.get('f45', 0) / 100 if d.get('f45') else 0,
                        'volume': d.get('f47', 0),
                        'amount': d.get('f48', 0) / 10000 if d.get('f48') else 0,
                        'change_percent': d.get('f170', 0) / 100 if d.get('f170') else 0,
                    }
        except Exception as e:
            print(f"从东方财富获取数据失败: {e}")
        return None
    
    def fetch_from_xueqiu(self) -> Optional[Dict]:
        """从雪球获取股票数据"""
        try:
            # 雪球API需要symbol格式: SH600036 或 SZ000001
            market_prefix = 'SH' if self.market == 'sh' else 'SZ'
            symbol = f"{market_prefix}{self.stock_code}"
            url = f"https://stock.xueqiu.com/v5/stock/quote.json"
            params = {
                'symbol': symbol,
                'extend': 'detail'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://xueqiu.com',
                'Cookie': 'xq_a_token=your_token'  # 可能需要token
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    d = data['data']
                    quote = d.get('quote', {})
                    return {
                        'source': '雪球',
                        'name': quote.get('name', ''),
                        'code': quote.get('symbol', ''),
                        'current': quote.get('current', 0),
                        'open': quote.get('open', 0),
                        'yesterday_close': quote.get('last_close', 0),
                        'high': quote.get('high', 0),
                        'low': quote.get('low', 0),
                        'volume': quote.get('volume', 0),
                        'amount': quote.get('amount', 0),
                        'change_percent': quote.get('percent', 0),
                    }
        except Exception as e:
            print(f"从雪球获取数据失败: {e}")
        return None
    
    def fetch_data(self) -> Optional[Dict]:
        """尝试从多个数据源获取数据，返回第一个成功的结果"""
        sources = [
            self.fetch_from_sina,
            self.fetch_from_eastmoney,
            self.fetch_from_xueqiu,
        ]
        
        for fetch_func in sources:
            data = fetch_func()
            if data:
                return data
            time.sleep(0.5)  # 避免请求过快
        
        return None


class StockNotifier:
    """股票信息推送器 - 使用 Bark 推送"""
    
    def __init__(self):
        self.bark_url = "http://notice.xmwefun.cn/"
    
    def format_message(self, data: Dict, stock_code: str = '') -> str:
        """格式化股票信息为消息"""
        if not data:
            return "获取股票数据失败"
        
        change = data.get('current', 0) - data.get('yesterday_close', 0)
        change_percent = data.get('change_percent', 0)
        if not change_percent and data.get('yesterday_close'):
            change_percent = (change / data.get('yesterday_close', 1)) * 100
        
        # 判断涨跌
        trend = "📈" if change >= 0 else "📉"
        color = "🔴" if change >= 0 else "🟢"
        
        stock_name = data.get('name', '未知股票')
        code = self._get_stock_code(data, stock_code)
        
        message = f"""
{trend} {stock_name} 股票实时信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
数据来源: {data.get('source', '未知')}
股票代码: {code}
当前价格: {color} {data.get('current', 0):.2f} 元
涨跌金额: {change:+.2f} 元
涨跌幅度: {change_percent:+.2f}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
今日开盘: {data.get('open', 0):.2f} 元
昨日收盘: {data.get('yesterday_close', 0):.2f} 元
今日最高: {data.get('high', 0):.2f} 元
今日最低: {data.get('low', 0):.2f} 元
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
成交量: {self._format_volume(data.get('volume', 0))}
成交额: {self._format_amount(data.get('amount', 0))}
更新时间: {data.get('time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()
        
        return message
    
    def _get_stock_code(self, data: Dict, default_code: str = '') -> str:
        """获取股票代码"""
        code = data.get('code', '')
        if not code:
            return default_code if default_code else '600036'
        return code.replace('SH', '').replace('SZ', '')
    
    def _format_volume(self, volume: int) -> str:
        """格式化成交量"""
        if volume >= 100000000:
            return f"{volume / 100000000:.2f} 亿手"
        elif volume >= 10000:
            return f"{volume / 10000:.2f} 万手"
        else:
            return f"{volume} 手"
    
    def _format_amount(self, amount: float) -> str:
        """格式化成交额"""
        if amount >= 100000000:
            return f"{amount / 100000000:.2f} 亿元"
        elif amount >= 10000:
            return f"{amount / 10000:.2f} 万元"
        else:
            return f"{amount:.2f} 元"
    
    def push_to_bark(self, title: str, message: str):
        """Bark 推送"""
        try:
            # URL 编码标题和消息内容
            title_encoded = quote(title)
            msg_encoded = quote(message)
            
            url = f"{self.bark_url}?type=bark&title={title_encoded}&msg={msg_encoded}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print("✅ Bark 推送成功")
                    return True
                else:
                    print(f"❌ Bark 推送失败: {result.get('errmsg', '未知错误')}")
            else:
                print(f"❌ Bark 推送失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Bark 推送失败: {e}")
        
        return False
    
    def push(self, message: str, data: Optional[Dict] = None, stock_code: str = ''):
        """推送消息到 Bark"""
        # 生成标题
        if data:
            change = data.get('current', 0) - data.get('yesterday_close', 0)
            change_percent = data.get('change_percent', 0)
            if not change_percent and data.get('yesterday_close'):
                change_percent = (change / data.get('yesterday_close', 1)) * 100
            
            trend = "📈" if change >= 0 else "📉"
            stock_name = data.get('name', '未知股票')
            title = f"{trend} {stock_name} {data.get('current', 0):.2f}元 ({change_percent:+.2f}%)"
        else:
            title = "股票监控"
        
        # 同时输出到控制台
        print(message)
        
        # 推送到 Bark
        self.push_to_bark(title, message)


def parse_stock_codes() -> List[str]:
    """解析股票代码列表"""
    # 优先从命令行参数获取
    parser = argparse.ArgumentParser(description='股票实时监控脚本')
    parser.add_argument('--codes', '-c', type=str, help='股票代码，多个用逗号分隔，如: 600036,000001,300001')
    args = parser.parse_args()
    
    # 从命令行参数或环境变量获取
    stock_codes_str = args.codes or os.getenv('STOCK_CODES', '600036')
    
    # 解析股票代码列表
    stock_codes = [code.strip() for code in stock_codes_str.split(',') if code.strip()]
    
    return stock_codes


def monitor_stock(stock_code: str, notifier: StockNotifier) -> bool:
    """监控单个股票"""
    print(f"\n{'='*50}")
    print(f"正在获取股票 {stock_code} 的信息...")
    print(f"{'='*50}")
    
    # 获取股票数据
    fetcher = StockDataFetcher(stock_code=stock_code)
    data = fetcher.fetch_data()
    
    if not data:
        print(f"❌ 无法从任何数据源获取股票 {stock_code} 的信息")
        return False
    
    # 格式化并推送消息
    message = notifier.format_message(data, stock_code)
    notifier.push(message, data, stock_code)
    
    return True


def main():
    """主函数"""
    # 解析股票代码列表
    stock_codes = parse_stock_codes()
    
    if not stock_codes:
        print("❌ 未指定股票代码")
        print("使用方法:")
        print("  1. 设置环境变量: export STOCK_CODES=600036,000001")
        print("  2. 命令行参数: python stock_monitor.py --codes 600036,000001")
        sys.exit(1)
    
    print(f"开始监控 {len(stock_codes)} 只股票: {', '.join(stock_codes)}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建推送器
    notifier = StockNotifier()
    
    # 统计结果
    success_count = 0
    fail_count = 0
    
    # 遍历每个股票代码
    for stock_code in stock_codes:
        try:
            if monitor_stock(stock_code, notifier):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"❌ 处理股票 {stock_code} 时发生错误: {e}")
            fail_count += 1
        
        # 避免请求过快，多个股票之间稍作延迟
        if stock_code != stock_codes[-1]:
            time.sleep(1)
    
    # 输出总结
    print(f"\n{'='*50}")
    print(f"✅ 监控任务完成")
    print(f"成功: {success_count} 只, 失败: {fail_count} 只")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()

