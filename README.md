# 抖音分析系统 - Python版本

基于 Python 重写的抖音账号诊断分析系统，直接调用 TikHub API 进行数据分析。

## 🚀 功能特性

### 1. 爆款视频分析
- **全量爆款(同赛道)**: 互动数据排名 TOP 5%-10%
- **同层级爆款**: 基于粉丝量级的互动数据分析
- **低粉爆款**: 最低粉丝等级的高互动视频
- **互动热度计算**: 点赞 + 评论×1.5 + 转发 + 收藏×1.5

### 2. 对标账号分析
- **单个账号热度**: 获取账号详细热度信息
- **热度榜单**: 对标账号热度排行榜
- **分类榜单**: 按账号类型筛选（认证、企业、普通）
- **同层级账号**: 基于粉丝数量范围的账号分析

### 3. 商品带货分析
- **视频商品数据**: 单个视频的带货商品销量/销售额
- **商品销售数据**: 单个商品的销售历史
- **TOP销售榜单**: 按销售额排序的商品榜单
- **分类销售**: 按商品类目的销售数据分析

## 📁 项目结构

```
douyin_analysis_python/
├── app/
│   ├── api/                    # API 控制器
│   │   ├── popular_video_api.py
│   │   ├── competitor_account_api.py
│   │   └── product_sales_api.py
│   ├── schemas/                # 数据模型
│   │   ├── tikhub_models.py
│   │   └── business_models.py
│   └── services/               # 业务服务
│       ├── tikhub_client.py
│       ├── popular_video_service.py
│       ├── competitor_account_service.py
│       └── product_sales_service.py
├── config/
│   └── settings.py             # 配置文件
├── main.py                     # 主应用入口
├── requirements.txt            # 依赖包列表
├── config.env.example          # 配置文件示例
├── start.sh                    # 启动脚本
└── README.md                   # 项目文档
```

## 🛠️ 安装和使用

### 1. 环境要求
- Python 3.8+
- TikHub API Key

### 2. 快速启动
```bash
# 克隆项目后进入目录
cd douyin_analysis_python

# 运行启动脚本（自动创建虚拟环境并安装依赖）
./start.sh
```

### 3. 手动安装
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp config.env.example .env
# 编辑 .env 文件，设置你的 TIKHUB_API_KEY

# 启动应用
python main.py
```

### 4. 配置说明
编辑 `.env` 文件，设置以下关键配置：

```env
# TikHub API 配置
TIKHUB_API_KEY=your_tikhub_api_key_here

# 其他可选配置
TIKHUB_TIMEOUT=30
LOG_LEVEL=INFO
```

## 📚 API 使用说明

### 启动后访问地址
- **API 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

### 主要接口

#### 1. 爆款视频分析
```http
# 获取单条视频互动数据
GET /api/v1/popular-videos/{video_id}/interaction

# 获取全量爆款视频榜单
GET /api/v1/popular-videos/full-popular?limit=20

# 获取同层级爆款视频
GET /api/v1/popular-videos/same-level?min_followers=10000&max_followers=100000&limit=20

# 获取低粉爆款视频
GET /api/v1/popular-videos/low-fan?max_followers=10000&limit=20

# 获取爆款视频综合榜单
GET /api/v1/popular-videos/ranking?video_type=full_popular&limit=20
```

#### 2. 对标账号分析
```http
# 获取单个账号热度信息
GET /api/v1/competitor-accounts/{account_id}/heat

# 获取对标账号热度榜单
GET /api/v1/competitor-accounts/heat-ranking?limit=20

# 获取指定类型账号榜单
GET /api/v1/competitor-accounts/heat-ranking/{account_type}?limit=20

# 获取同层级账号
GET /api/v1/competitor-accounts/same-level?min_followers=10000&max_followers=100000&limit=20

# 获取认证账号榜单
GET /api/v1/competitor-accounts/verified-ranking?limit=20
```

#### 3. 商品带货分析
```http
# 获取视频商品带货数据
GET /api/v1/product-sales/video/{video_id}

# 获取商品销售数据
GET /api/v1/product-sales/product/{product_id}

# 获取TOP销售商品榜单
GET /api/v1/product-sales/top-sales?limit=10

# 获取指定类目商品销售数据
GET /api/v1/product-sales/category/{category}?limit=10

# 获取销售汇总数据
GET /api/v1/product-sales/summary?time_range=7
```

## 🔧 技术架构

### 技术栈
- **Web框架**: FastAPI
- **HTTP客户端**: httpx
- **数据验证**: Pydantic
- **日志**: loguru
- **异步支持**: asyncio

### 核心特性
- **异步处理**: 全异步API调用，提高并发性能
- **类型安全**: 基于Pydantic的强类型数据模型
- **自动文档**: FastAPI自动生成API文档
- **错误处理**: 全局异常处理和日志记录
- **可配置**: 灵活的配置管理系统

### 数据流程
```
前端请求 → FastAPI路由 → 业务服务 → TikHub API → 数据处理 → 返回结果
```

## 📊 数据分析说明

### 互动热度计算公式
```
互动分数 = 点赞数×1.0 + 评论数×1.5 + 转发数×1.0 + 收藏数×1.5
```

### 账号热度计算公式
```
热度分数 = 粉丝数×0.3 + 平均播放量×0.4 + 平均点赞数×0.2 + 平均评论数×0.1
```

### TOP榜单逻辑
- **爆款视频**: 按互动分数排序，取TOP 5%-10%
- **账号热度**: 按热度分数排序
- **商品销售**: 按销售额排序

## 🚧 开发说明

### 扩展功能
1. **数据库支持**: 可添加 PostgreSQL/MySQL 进行数据持久化
2. **缓存支持**: 可添加 Redis 进行数据缓存
3. **认证授权**: 可添加 JWT Token 认证
4. **监控告警**: 可添加 Prometheus 监控

### 部署建议
1. **Docker 容器化部署**
2. **Nginx 反向代理**
3. **Gunicorn + Uvicorn 生产环境部署**
4. **日志聚合和监控**

## 📝 更新日志

### v1.0.0 (2024-01-XX)
- ✅ 完成爆款视频分析功能
- ✅ 完成对标账号分析功能  
- ✅ 完成商品带货分析功能
- ✅ 完成 TikHub API 集成
- ✅ 完成 FastAPI 接口开发
- ✅ 完成项目文档

## 📞 技术支持

如有问题或建议，请提交 Issue 或联系开发团队。

---

**注意**: 本项目为 Java 版本的 Python 重写版本，直接调用 TikHub API，无需额外的 Java 服务依赖。 