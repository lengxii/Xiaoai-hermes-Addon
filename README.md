<p align="center">
  <img src="assets/ui/favicon.svg" alt="XiaoAI Cloud Plugin Logo" width="176" height="176">
</p>

<p align="center">将小爱音箱接入 Hermes Agent</p>

<p align="center">
  <img src="https://img.shields.io/badge/Hermes-Plugin-8b5cf6?style=flat-square" alt="Hermes Plugin">
  <img src="https://img.shields.io/badge/Node.js-22%2B-339933?style=flat-square&logo=node.js&logoColor=white" alt="Node.js 22+">
  <img src="https://img.shields.io/badge/TypeScript-5.x-3178c6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript 5">
</p>

## 这是什么

从 [Xiaoai-Claw-Addon](https://github.com/ZhengXieGang/Xiaoai-Claw-Addon)（OpenClaw 版本）适配而来的 **Hermes Agent** 插件。

**运行方式**：Hermes 插件 + Node.js 后端服务
- Python 插件注册 Hermes 工具，调用 Node.js HTTP API
- Node.js 服务处理小米 API、语音轮询、音箱控制
- 语音转发优先走 Hermes API，fallback 到直接 LLM

核心功能：
- 语音拦截与转发（拦截小爱语音，转发给 Hermes 处理）
- 小爱播报与远程唤醒
- 小爱本地执行指令
- 音量、唤醒词、工作模式、上下文记忆控制
- 内嵌登录、设备切换、事件流和对话控制台
- 音频回复处理

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                     Hermes Agent                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  xiaoai-cloud Python Plugin                        │  │
│  │  - 注册 xiaoai_* 工具                              │  │
│  │  - 调用 Node.js HTTP API                           │  │
│  │  - 发送通知 (send_message)                         │  │
│  └─────────────────────┬─────────────────────────────┘  │
│                        │ HTTP                            │
│  ┌─────────────────────▼─────────────────────────────┐  │
│  │  Hermes API Server (port 8642)                     │  │
│  │  - /v1/chat/completions                            │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          │ 语音转发 (优先 Hermes API,
                          │          fallback 直接 LLM)
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Node.js 后端服务 (port 17890)               │
│  - 小米账号登录 / 设备发现                                │
│  - 语音轮询 / 唤醒词检测                                  │
│  - 音箱控制 (播报/音量/唤醒)                              │
│  - Web 控制台                                            │
│  - HTTP API (xiaoai_speak, xiaoai_play_audio, ...)      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   小米云端 API                            │
│  - MiIO / MiNA 协议                                      │
│  - 小爱音箱控制                                           │
└─────────────────────────────────────────────────────────┘
```

## 快速开始

### 环境要求
- Node.js 22+
- Python 3.10+
- 小米账号 + 小爱音箱
- Hermes Agent 已安装并运行

### 1. 安装 Node.js 后端

```bash
git clone https://github.com/lengxii/Xiaoai-hermes-Addon.git
cd Xiaoai-hermes-Addon
npm install
npm run build
```

### 2. 配置

```bash
mkdir -p ~/.hermes/xiaoai-cloud
cp config.example.json ~/.hermes/xiaoai-cloud/config.json
```

编辑 `~/.hermes/xiaoai-cloud/config.json`：

```json
{
  "hermesApiUrl": "http://127.0.0.1:8642",
  "llmApiUrl": "https://api.openai.com",
  "llmApiKey": "sk-...",
  "llmModel": "gpt-4o-mini"
}
```

### 3. 安装 Hermes 插件

```bash
cp -r hermes-plugin ~/.hermes/plugins/xiaoai-cloud
```

### 4. 启动 Node.js 后端

```bash
npm start
```

或使用 systemd：

```bash
sudo cp xiaoai-cloud.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now xiaoai-cloud
```

### 5. 重启 Hermes

```bash
hermes gateway restart
# 或在 CLI 中: /reset
```

## 语音转发流程

1. 用户对小爱说话 → Node.js 服务轮询检测到
2. Node.js 服务调用 **Hermes API** (`http://127.0.0.1:8642/v1/chat/completions`)
3. Hermes Agent 处理请求（包括工具调用、记忆、上下文等）
4. 返回结果 → Node.js 服务让小爱播报
5. 如果 Hermes API 不可用，fallback 到直接调用 LLM API

## HTTP API

Node.js 服务监听端口 17890，提供以下 API：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/xiaoai/tools` | 列出所有工具 |
| POST | `/api/xiaoai/speak` | 让音箱说话 |
| POST | `/api/xiaoai/play-audio` | 播放音频 URL |
| POST | `/api/xiaoai/set-volume` | 设置音量 |
| GET | `/api/xiaoai/get-volume` | 获取当前音量 |
| POST | `/api/xiaoai/wake-up` | 远程唤醒 |
| POST | `/api/xiaoai/execute` | 发送指令到音箱 |
| POST | `/api/xiaoai/set-mode` | 切换拦截模式 |
| GET | `/api/xiaoai/status` | 获取完整状态 |
| GET | `/console` | Web 控制台 |

## 工作模式

- **唤醒模式**（默认）：命中唤醒词或在免唤醒窗口期内才接管
- **代理模式**：完全接管所有语音
- **静默模式**：不接管，只保留主动播报

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `XIAOAI_PORT` | 17890 | Node.js 服务端口 |
| `XIAOAI_HOST` | 0.0.0.0 | Node.js 服务绑定地址 |
| `XIAOAI_API_URL` | http://127.0.0.1:17890 | Python 插件调用的 API 地址 |
| `HERMES_API_URL` | http://127.0.0.1:8642 | Hermes API 地址 |

## 配置项

完整配置见 `config.example.json`，主要配置项：

| 配置项 | 说明 |
|--------|------|
| `hermesApiUrl` | Hermes API 地址（默认 http://127.0.0.1:8642） |
| `llmApiUrl` | 直接 LLM API 地址（fallback） |
| `llmApiKey` | LLM API Key |
| `llmModel` | 模型名称 |
| `account` | 小米账号 |
| `speakerName` | 米家中的设备名称 |
| `wakeWordPattern` | 唤醒词正则 |

## 与原版的区别

| 项目 | OpenClaw 版 | Hermes 版 |
|------|------------|-----------|
| 运行方式 | OpenClaw 插件 | Hermes 插件 + Node.js 服务 |
| 语音转发 | OpenClaw Gateway SDK | Hermes API (优先) + 直接 LLM (fallback) |
| 通知机制 | openclaw CLI | Hermes send_message |
| 数据目录 | `~/.openclaw/` | `~/.hermes/xiaoai-cloud/` |
| 工具注册 | OpenClaw API | Hermes 插件 API |

## 测试环境
- 阿里云轻量应用服务器2C2G (Debian)
- 小爱音箱Play增强版 (L05C)

## 致谢

原项目：[ZhengXieGang/Xiaoai-Claw-Addon](https://github.com/ZhengXieGang/Xiaoai-Claw-Addon)（OpenClaw 版本）

## 如果帮到了你，可以捐赠支持原作者
<img width="30%" alt="mm_reward_qrcode_1775163379040" src="https://github.com/user-attachments/assets/f04e53d0-72aa-4cf7-a50c-f79e6606c786" />
