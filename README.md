# Canada28 Data Analysis Tool

加拿大28 / PC28 开奖数据抓取、分析工具。

## Features

- 实时获取加拿大28、加拿大西、台湾宾果、比特币PC28四个彩种的开奖数据
- 大小单双趋势统计分析
- 和值频率与遗漏值计算
- 历史数据导出为 CSV
- 走势图数据预处理

## Data Source

数据来源于 janada28.cc / janada28.com / janada28vip.com，通过 API 接口获取实时开奖数据。

## Usage

```bash
# 获取最新开奖数据
python3 analysis.py --lottery 10029 --count 50

# 查看趋势统计
python3 analysis.py --lottery 10029 --trend

# 导出 CSV
python3 analysis.py --lottery 10029 --export results.csv
```

## Supported Lotteries

| Code | Name | Interval |
|------|------|----------|
| 10029 | 加拿大PC28 | 3分30秒 |
| 10039 | 加拿大西PC28 | 5分钟 |
| 10027 | 台湾宾果PC28 | 5分钟 |
| 10049 | 比特币3分PC28 | 3分钟 |

## License

MIT
