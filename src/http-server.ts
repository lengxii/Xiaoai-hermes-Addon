import http from "http";
import { URL } from "url";

interface ToolDefinition {
    name: string;
    description: string;
    parameters: any;
    execute: (id: string, params: any) => Promise<any>;
}

interface PluginLike {
    registeredTools: Map<string, ToolDefinition>;
    handleHttpRequest?: (req: http.IncomingMessage, res: http.ServerResponse) => Promise<boolean>;
}

export function createHttpServer(plugin: PluginLike): http.Server {
    const server = http.createServer(async (req, res) => {
        const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);
        const path = url.pathname;

        // CORS headers
        res.setHeader("Access-Control-Allow-Origin", "*");
        res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

        if (req.method === "OPTIONS") {
            res.writeHead(204);
            res.end();
            return;
        }

        // Health check
        if (path === "/health") {
            res.writeHead(200, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ status: "ok", tools: Array.from(plugin.registeredTools.keys()) }));
            return;
        }

        // List tools
        if (path === "/api/xiaoai/tools" && req.method === "GET") {
            const tools = Array.from(plugin.registeredTools.values()).map(t => ({
                name: t.name,
                description: t.description,
                parameters: t.parameters,
            }));
            res.writeHead(200, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ tools }));
            return;
        }

        // Execute tool: POST /api/xiaoai/:toolName
        const toolMatch = path.match(/^\/api\/xiaoai\/([\w-]+)$/);
        if (toolMatch && req.method === "POST") {
            const toolName = toolMatch[1];
            const tool = plugin.registeredTools.get(`xiaoai_${toolName}`) || plugin.registeredTools.get(toolName);

            if (!tool) {
                res.writeHead(404, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ error: `Tool not found: ${toolName}` }));
                return;
            }

            try {
                const body = await readBody(req);
                const params = body ? JSON.parse(body) : {};
                const result = await tool.execute(`http-${Date.now()}`, params);
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end(JSON.stringify(result));
            } catch (error: any) {
                res.writeHead(500, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ error: error.message || String(error) }));
            }
            return;
        }

        // Delegate to plugin's custom HTTP handler (console, auth portal, etc.)
        if (plugin.handleHttpRequest) {
            const handled = await plugin.handleHttpRequest(req, res);
            if (handled) return;
        }

        // 404
        res.writeHead(404, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Not found" }));
    });

    return server;
}

function readBody(req: http.IncomingMessage): Promise<string> {
    return new Promise((resolve, reject) => {
        let body = "";
        req.on("data", (chunk) => { body += chunk; });
        req.on("end", () => resolve(body));
        req.on("error", reject);
    });
}
