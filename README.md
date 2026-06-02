# scenic-dh-admin-api

智慧景区数字人平台 — 运营管理接口。

## 快速开始

```bash
cd scenic-dh-admin-api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

http://localhost:8002/health
http://localhost:8002/docs

## 鉴权

所有管理端点需要 `x-admin-token` 头（MVP 默认值: `adm-dev-token`）。

## 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /v1/knowledge/status | 知识库状态 |
| POST | /v1/knowledge/sources | 登记资料来源 |
| POST | /v1/knowledge/reindex | 触发重建索引 |
| GET | /v1/personas/{id} | 人设查询 |
| PUT | /v1/personas/{id} | 人设更新 |
| POST | /v1/broadcasts | 人工播报 |
| GET | /v1/broadcasts | 播报列表 |
| GET | /v1/sessions | 会话审计 |
| GET | /v1/sessions/{id} | 会话详情 |
| GET | /v1/messages | 消息审计 |
| POST | /v1/messages/{id}/adopt | 采纳问答 |
| GET | /v1/analytics/overview | 运营总览 |
| GET | /v1/analytics/hot-questions | 热问分析 |
| GET | /v1/analytics/rag | RAG 分析 |
| GET | /v1/analytics/avatar | 数字人分析 |
| GET | /v1/runtime/status | 运行状态 |
| POST | /v1/runtime/microphone/toggle | 麦克风开关 |
| POST | /v1/runtime/clear-queue | 清空播报队列 |
