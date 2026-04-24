# Xiaoai-Claw-Addon → Hermes 适配方案

## 项目现状
- 26,549 行 TypeScript (Node.js 22+)
- 核心类 `XiaoaiCloudPlugin` 在 provider.ts (20,149 行)
- 18 个 xiaoai_* 工具
- 深度耦合 OpenClaw (6 个主要耦合点)

## OpenClaw 耦合点清单

| # | 耦合点 | 位置 | 替换方案 |
|---|--------|------|----------|
| 1 | `this.api.registerTool()` | provider.ts:19154+ | 独立 HTTP API 服务端点 |
| 2 | `this.api.registerHttpRoute()` | provider.ts:7056 | Express HTTP 服务器 |
| 3 | `sendOpenclawNotification()` | provider.ts:18559 | Hermes `send_message()` webhook |
| 4 | `loadGatewayClientCtor()` | provider.ts:18443 | 移除，改用 HTTP API |
| 5 | `runOpenclawGatewayCall()` | provider.ts:18522 | 移除，改用 Hermes API |
| 6 | `deliverAgentPrompt()` | provider.ts:18826 | Hermes API / delegate_task |
| 7 | `this.api.runtime.system.runCommandWithTimeout()` | provider.ts:18358 | child_process.execFile |
| 8 | `~/.openclaw/` 路径 | openclaw-paths.ts | `~/.hermes/xiaoai-cloud/` |
| 9 | `openclaw.json` 配置 | openclaw-paths.ts:75 | `~/.hermes/xiaoai-cloud/config.json` |

## 适配策略：保留 TypeScript + 独立服务 + Hermes 集成

### 阶段 1: 路径与配置解耦 (最小改动)
- [ ] 修改 `openclaw-paths.ts`: `~/.openclaw/` → `~/.hermes/xiaoai-cloud/`
- [ ] 修改 `state-store.ts`: 路径跟随
- [ ] 修改 `package.json`: 重命名项目

### 阶段 2: 移除 OpenClaw SDK 依赖
- [ ] 删除 `openclaw-gateway-runtime.ts` (GatewayClient)
- [ ] 删除 `openclaw-agent-wrapper.ts` (CLI wrapper)
- [ ] 修改 `provider.ts`: 移除所有 `loadGatewayClientCtor` 调用
- [ ] 修改 `provider.ts`: 移除 `runOpenclawGatewayCall()` 方法
- [ ] 修改 `provider.ts`: 移除 `ensureOpenclawGatewayClient()` 方法

### 阶段 3: HTTP API 服务化
- [ ] 创建 `src/http-server.ts`: Express/fetch HTTP 服务器
- [ ] 暴露 18 个工具为 REST API 端点:
  - POST /api/xiaoai/speak
  - POST /api/xiaoai/play-audio
  - POST /api/xiaoai/tts-bridge
  - POST /api/xiaoai/set-volume
  - POST /api/xiaoai/get-volume
  - POST /api/xiaoai/new-session
  - POST /api/xiaoai/wake-up
  - POST /api/xiaoai/execute
  - POST /api/xiaoai/set-mode
  - POST /api/xiaoai/set-wake-word
  - GET  /api/xiaoai/status
  - POST /api/xiaoai/login-begin
  - GET  /api/xiaoai/login-status
  - GET  /api/xiaoai/console
  - POST /api/xiaoai/calibration
  - POST /api/xiaoai/set-dialog-window
  - POST /api/xiaoai/update-settings
- [ ] 保留原有 console web UI 路由

### 阶段 4: 通知机制替换
- [ ] 修改 `sendOpenclawNotification()`: 改为 HTTP webhook 通知
- [ ] 支持配置 Hermes webhook URL 或直接调用 Hermes API
- [ ] 保留 bestEffort 降级逻辑

### 阶段 5: 语音转发对接 Hermes
- [ ] 修改 `deliverAgentPrompt()`: 改为调用 Hermes API
- [ ] 方案 A: 调用 Hermes HTTP API (如果启用 api-server)
- [ ] 方案 B: 通过 webhook 触发 Hermes cron job
- [ ] 方案 C: 直接调用 LLM API (绕过 Hermes，最简单)
- [ ] 保留会话上下文管理逻辑

### 阶段 6: Hermes 技能与工具
- [ ] 创建 `xiaoai-cloud` Hermes skill (SKILL.md)
- [ ] 创建 Python 工具脚本调用 HTTP API
- [ ] 创建 systemd service 文件
- [ ] 创建安装/配置脚本

## 文件变更预估

| 文件 | 操作 | 改动量 |
|------|------|--------|
| `openclaw-paths.ts` | 重写 | 小 (~50 行) |
| `openclaw-gateway-runtime.ts` | 删除 | - |
| `openclaw-agent-wrapper.ts` | 删除 | - |
| `state-store.ts` | 修改 | 小 (路径) |
| `provider.ts` | 修改 | 中 (移除 OpenClaw 调用) |
| `src/http-server.ts` | 新增 | 中 (~300 行) |
| `index.ts` | 重写 | 小 (~30 行) |
| `package.json` | 修改 | 小 |
| `hermes-skill/SKILL.md` | 新增 | 小 (~100 行) |
| `scripts/install.sh` | 新增 | 小 (~50 行) |

## 实施顺序

1. **先做路径解耦** (阶段 1) - 最小风险
2. **再做 HTTP 服务化** (阶段 3) - 核心架构变更
3. **然后移除 OpenClaw** (阶段 2) - 清理依赖
4. **最后对接 Hermes** (阶段 4-6) - 集成测试

## 语音转发方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| A: Hermes HTTP API | 最紧密集成 | 需要 Hermes api-server 运行 |
| B: Webhook + Cron | 解耦，可靠 | 延迟高，不适合实时对话 |
| C: 直接调用 LLM | 最简单，无依赖 | 绕过 Hermes，丢失上下文 |

**推荐**: 方案 C 作为默认，方案 A 作为可选增强。
