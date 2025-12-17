import * as path from "path";
import * as fs from "fs";
import * as vscode from "vscode";

/**
 * Utility functions for the VS Code Aster extension.
 * Includes helper functions for UUID generation, timezone handling,
 * version information, and HTTP requests for telemetry.
 */

/**
 * Generates a v4 UUID for unique identification.
 * Uses dynamic import to support the ESM-only `uuid` package in a CommonJS module.
 * Falls back to a default UUID string if the uuid package fails to load.
 * 
 * @returns A promise that resolves to a v4 UUID string
 */
export async function generateUuid(): Promise<string> {
  try {
    const mod = (await import("uuid")) as any;
    const v4 = mod.v4 ?? mod.default?.v4 ?? mod.default ?? mod;
    if (typeof v4 === "function") {
      return v4();
    }
    throw new Error("uuid.v4 is not a function");
  } catch (err) {
    console.log(
      `[telemetry] Failed to load uuid dynamically: ${
        err instanceof Error ? err.message : String(err)
      }`
    );
    return "00000000-0000-0000-0000-000000000000";
  }
}

/**
 * Gets the current timezone offset as a formatted string.
 * Returns the offset in the format ±HH:MM (e.g., "+02:00" or "-05:30").
 * 
 * @returns Formatted timezone offset string
 */
export function getTimezoneOffsetString(): string {
  const offset = new Date().getTimezoneOffset();
  const sign = offset <= 0 ? "+" : "-";
  const absMin = Math.abs(offset);
  const hours = Math.floor(absMin / 60)
    .toString()
    .padStart(2, "0");
  const minutes = (absMin % 60).toString().padStart(2, "0");
  return `${sign}${hours}:${minutes}`;
}

/**
 * Retrieves the extension package version from package.json.
 * Falls back to "0.0.0" if the package.json file cannot be read or parsed.
 * 
 * @returns The extension version string or "0.0.0" if unavailable
 */
export function getPackageVersion(): string {
  try {
    const pkgPath = path.resolve(__dirname, "..", "package.json");
    if (!fs.existsSync(pkgPath)) {
      return "0.0.0";
    }
    const raw = fs.readFileSync(pkgPath, { encoding: "utf8" });
    const parsed = JSON.parse(raw);
    return typeof parsed.version === "string" && parsed.version.length
      ? parsed.version
      : "0.0.0";
  } catch (e) {
    return "0.0.0";
  }
}

/**
 * Gets the VS Code version information for telemetry purposes.
 * Returns the VS Code application name and version in the format "app/version".
 * 
 * @returns A promise that resolves to the version string or "unknown" if unavailable
 */
export async function getVSCodeVersion(): Promise<string> {
  try {
    // Prefer the IDE/app name if available, otherwise fall back to 'vscode'
    const appName = ((vscode.env as any).appName as string) || "vscode";
    const version = vscode.version || "unknown";
    const safeApp = appName.replace(/\s+/g, "_");
    return `${safeApp}/${version}`;
  } catch (err) {
    return "unknown";
  }
}

/**
 * Sends a JSON POST request with a timeout.
 * Automatically aborts the request if it exceeds the specified timeout.
 * Used primarily for sending telemetry data to the server.
 * 
 * @param urlStr The URL to send the request to
 * @param obj The data object to send as JSON
 * @param timeoutMs Request timeout in milliseconds (default: 3000)
 * @returns A promise that resolves when the request completes or is aborted
 */
export async function sendJsonRequestWithTimeout(
  urlStr: string,
  obj: any,
  timeoutMs = 3000
): Promise<void> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    await fetch(urlStr, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(obj),
      signal: controller.signal,
    });
  } finally {
    clearTimeout(id);
  }
}

