import os from "os";
import path from "path";

export const XIAOAI_CLOUD_PLUGIN_SUBDIR = "xiaoai-cloud";

function readString(value: unknown): string | undefined {
    if (typeof value !== "string") {
        return undefined;
    }
    const trimmed = value.trim();
    return trimmed ? trimmed : undefined;
}

function expandHomePath(value: string) {
    if (!value.startsWith("~")) {
        return value;
    }
    const homeDir =
        readString(process.env.HOME) ||
        readString(process.env.USERPROFILE) ||
        os.homedir() ||
        process.cwd();
    if (value === "~") {
        return homeDir;
    }
    if (value.startsWith("~/") || value.startsWith("~\\")) {
        return path.join(homeDir, value.slice(2));
    }
    return value;
}

function resolveHermesHomeRoot() {
    const configuredHome = readString(process.env.HERMES_HOME);
    if (configuredHome) {
        return path.resolve(expandHomePath(configuredHome));
    }
    return (
        readString(process.env.HOME) ||
        readString(process.env.USERPROFILE) ||
        os.homedir() ||
        process.cwd()
    );
}

export function fallbackHermesStateDir() {
    return path.join(resolveHermesHomeRoot(), ".hermes");
}

export function resolveActiveHermesStateDir(options?: {
    serviceStateDir?: string;
}) {
    return (
        readString(options?.serviceStateDir) ||
        readString(process.env.HERMES_STATE_DIR) ||
        fallbackHermesStateDir()
    );
}

export function resolveHermesConfigPath(options?: {
    serviceStateDir?: string;
}) {
    return (
        readString(process.env.XIAOAI_CONFIG_PATH) ||
        path.join(resolvePluginStorageDir(options), "config.json")
    );
}

export function resolvePluginStorageDir(options?: {
    serviceStateDir?: string;
}) {
    return path.join(
        resolveActiveHermesStateDir(options),
        XIAOAI_CLOUD_PLUGIN_SUBDIR
    );
}

export function defaultPluginStorageDir(baseStorageDir?: string) {
    return readString(baseStorageDir) || resolvePluginStorageDir();
}

// Backward-compat aliases (will be removed later)
export const resolveOpenclawConfigPath = resolveHermesConfigPath;
export const resolveActiveOpenclawStateDir = resolveActiveHermesStateDir;
export const fallbackOpenclawStateDir = fallbackHermesStateDir;
