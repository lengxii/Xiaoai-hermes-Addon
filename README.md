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

从 [Xiaoai-Claw-Addon](https://github.com/ZhengXieGang/Xiaoai-Claw-Addon)（OpenClaw 版本）适配而来的 **Hermes Agent** 插件。独立运行，不依赖 OpenClaw，通过 OpenAI 兼容的 LLM API 实现语音对话。

核心功能：
- 语音拦截与转发（拦截小爱语音，转发给 LLM）
- 小爱播报与远程唤醒
- 小爱本地执行指令
- 音量、唤醒词、工作模式、上下文记忆控制
- 内嵌登录、设备切换、事件流和对话控制台
- 音频回复处理

## 与原版的区别

| 项目 | OpenClaw 版 | Hermes 版 |
|------|------------|-----------|
| 运行方式 | OpenClaw 插件 | 独立 Node.js 服务 |
| LLM 调用 | OpenClaw Gateway SDK | 直接调用 OpenAI 兼容 API |
| 通知机制 | openclaw CLI | Webhook HTTP POST |
| 数据目录 | `~/.openclaw/plugins/xiaoai-cloud/` | `~/.hermes/xiaoai-cloud/` |
| 工具注册 | `this.api.registerTool()` | HTTP API 端点 |
| 配置文件 | `openclaw.plugin.json` | `hermes.plugin.json` |

## 快速开始

### 环境要求
- Node.js 22+
- 小米账号 + 小爱音箱
- OpenAI 兼容的 LLM API（如 OpenAI、DeepSeek、GLM 等）

### 安装

```bash
git clone https://github.com/lengxii/Xiaoai-hermes-Addon.git
cd Xiaoai-hermes-Addon
npm install
npm run build
```

### 配置

复制示例配置并编辑：

```bash
mkdir -p ~/.hermes/xiaoai-cloud
cp config.example.json ~/.hermes/xiaoai-cloud/config.json
```

编辑 `~/.hermes/xiaoai-cloud/config.json`，至少填写：

```json
{
  "llmApiUrl": "https://api.openai.com",
  "llmApiKey": "sk-...",
  "llmModel": "gpt-4o-mini"
}
```

### 启动

```bash
npm start
```

或使用环境变量：

```bash
XIAOAI_PORT=17890 LLM_API_URL=https://api.openai.com LLM_API_KEY=sk-... npm start
```

### systemd 服务（可选）

```bash
sudo cp xiaoai-cloud.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now xiaoai-cloud
```

## HTTP API

服务启动后监听端口 17890（可配置），提供以下 API：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/xiaoai/tools` | 列出所有工具 |
| POST | `/api/xiaoai/speak` | 让音箱说话 |
| POST | `/api/xiaoai/play-audio` | 播放音频 URL |
| POST | `/api/xiaoai/set-volume` | 设置音量 |
| GET | `/api/xiaoai/get-volume` | 获取当前音量 |
| POST | `/api/xiaoai/new-session` | 重置语音上下文 |
| POST | `/api/xiaoai/wake-up` | 远程唤醒 |
| POST | `/api/xiaoai/execute` | 发送指令到音箱 |
| POST | `/api/xiaoai/set-mode` | 切换拦截模式 |
| GET | `/api/xiaoai/status` | 获取完整状态 |
| POST | `/api/xiaoai/login-begin` | 开始小米登录 |
| GET | `/api/xiaoai/login-status` | 检查登录状态 |
| GET | `/console` | Web 控制台 |

## 首次使用

1. 启动服务后打开控制台：http://localhost:17890/console
2. 登录小米账号
3. 选择要控制的音箱
4. 开始使用

## 工作模式

- **唤醒模式**（默认）：命中唤醒词或在免唤醒窗口期内才接管
- **代理模式**：完全接管所有语音
- **静默模式**：不接管，只保留主动播报

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `XIAOAI_PORT` | 17890 | HTTP 服务端口 |
| `XIAOAI_HOST` | 0.0.0.0 | HTTP 服务绑定地址 |
| `LLM_API_URL` | (必填) | OpenAI 兼容 API 地址 |
| `LLM_API_KEY` | (可选) | API Key |
| `LLM_MODEL` | gpt-4o-mini | 模型名称 |
| `HERMES_HOME` | ~/.hermes | Hermes 主目录 |

## 配置项

完整配置见 `config.example.json`，主要配置项：

| 配置项 | 说明 |
|--------|------|
| `account` | 小米账号 |
| `serverCountry` | 云端区域，默认 cn |
| `speakerName` | 米家中的设备名称 |
| `llmApiUrl` | LLM API 地址（必填） |
| `llmApiKey` | LLM API Key |
| `llmModel` | 模型名称 |
| `wakeWordPattern` | 唤醒词正则 |
| `dialogWindowSeconds` | 免唤醒窗口时长 |
| `notificationWebhookUrl` | 通知 webhook |

## 排障

**音箱找不到**：通过控制台登录并选择设备

**语音没被拦截**：检查唤醒词模式和工作模式

**LLM 没响应**：检查 `llmApiUrl` 和 `llmApiKey` 配置

**端口冲突**：修改 `XIAOAI_PORT` 环境变量

## 测试环境
- 阿里云轻量应用服务器2C2G (Debian)
- 小爱音箱Play增强版 (L05C)

## 致谢

原项目：[ZhengXieGang/Xiaoai-Claw-Addon](https://github.com/ZhengXieGang/Xiaoai-Claw-Addon)（OpenClaw 版本）

## 如果帮到了你，可以捐赠支持原作者
<img width="30%" alt="mm_reward_qrcode_1775163379040" src="https://github.com/user-attachments/assets/f04e53d0-72aa-4cf7-a50c-f79e6606c786" />
