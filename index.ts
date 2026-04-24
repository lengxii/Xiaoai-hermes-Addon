import { createXiaoaiCloudPlugin } from "./src/provider.js";
import { createHttpServer } from "./src/http-server.js";

const PORT = Number(process.env.XIAOAI_PORT || 18790);
const HOST = process.env.XIAOAI_HOST || "0.0.0.0";

async function main() {
    console.log("[XiaoAI Cloud] Starting Hermes XiaoAI Cloud service...");

    const plugin = createXiaoaiCloudPlugin();
    plugin.registerTools();

    // Start the HTTP API server
    const httpServer = createHttpServer(plugin);
    httpServer.listen(PORT, HOST, () => {
        console.log(`[XiaoAI Cloud] HTTP API server listening on http://${HOST}:${PORT}`);
        console.log(`[XiaoAI Cloud] Console: http://${HOST}:${PORT}/console`);
        console.log(`[XiaoAI Cloud] API base: http://${HOST}:${PORT}/api/xiaoai/`);
    });

    // Start the voice interception service
    await plugin.startService();

    // Graceful shutdown
    const shutdown = async () => {
        console.log("[XiaoAI Cloud] Shutting down...");
        await plugin.stopService();
        httpServer.close();
        process.exit(0);
    };

    process.on("SIGINT", shutdown);
    process.on("SIGTERM", shutdown);
}

main().catch((error) => {
    console.error("[XiaoAI Cloud] Fatal error:", error);
    process.exit(1);
});
