# 谷歌新闻爬虫

这个项目用于爬取谷歌新闻中特定城市和行业关键词组合的搜索结果，并统计真实有效的结果数量。程序会验证每个链接的有效性，并筛选出仅包含简体中文的结果。

## 功能特点

- 支持指定城市和行业关键词组合进行搜索
- 支持设定日期范围（默认为2012年1月1日至2024年12月31日）
- 验证链接有效性，过滤无效链接
- 仅保留简体中文结果，过滤繁体中文和其他语言
- 支持批量处理多个城市和关键词组合
- 生成详细的CSV报告，包含标题、链接、来源、日期和摘要等信息
- 生成汇总报告，统计每个组合的总结果数和有效结果数

## 安装依赖

在使用前，请确保已安装以下依赖：

```bash
pip install selenium beautifulsoup4 requests langdetect
```

此外，您还需要安装Chrome浏览器和对应版本的ChromeDriver。

## 使用方法

### 单个关键词组合爬取

```bash
python google_news_scraper.py --city 哈尔滨 --keyword 大数据 --start_date 01/01/2012 --end_date 31/12/2024 --output results.csv
```

### 批量爬取多个关键词组合

```bash
python batch_scraper.py --cities 哈尔滨,北京,上海 --keywords 大数据,互联网金融,人工智能 --start_date 01/01/2012 --end_date 31/12/2024
```

## 参数说明

### google_news_scraper.py 参数

- `--city`: 城市名称（必需）
- `--keyword`: 行业关键词（必需）
- `--start_date`: 开始日期，格式为DD/MM/YYYY，默认为01/01/2012
- `--end_date`: 结束日期，格式为DD/MM/YYYY，默认为31/12/2024
- `--max_pages`: 最大爬取页数，默认为None（爬取所有页面）
- `--output`: 输出文件名，默认为results.csv
- `--headless`: 使用无头模式（不显示浏览器界面），默认不启用

### batch_scraper.py 参数

- `--cities`: 城市列表，用逗号分隔（必需）
- `--keywords`: 关键词列表，用逗号分隔（必需）
- `--start_date`: 开始日期，格式为DD/MM/YYYY，默认为01/01/2012
- `--end_date`: 结束日期，格式为DD/MM/YYYY，默认为31/12/2024
- `--max_pages`: 最大爬取页数，默认为None（爬取所有页面）
- `--headless`: 使用无头模式（不显示浏览器界面），默认不启用

## 输出说明

程序会在results目录下生成以下文件：

1. 每个城市和关键词组合的详细结果CSV文件，包含以下字段：
   - city: 城市名称
   - keyword: 行业关键词
   - title: 新闻标题
   - link: 新闻链接
   - source: 新闻来源
   - date: 发布日期
   - snippet: 新闻摘要

2. 汇总CSV文件，包含以下字段：
   - city: 城市名称
   - keyword: 行业关键词
   - total_results: 总结果数
   - valid_results: 有效结果数（仅简体中文）

## 注意事项

1. 谷歌可能会限制频繁的爬取行为，建议适当调整爬取间隔
2. 程序默认使用Chrome浏览器，请确保已正确安装
3. 爬取大量数据可能需要较长时间，请耐心等待
4. 如遇到验证码或IP被封，可尝试使用代理或更换IP