import * as vscode from "vscode";
import * as utils from "./utils";

/**
 * Telemetry event types
 */
export enum TelemetryType {
  VIEWER_OPENED = 1, // Sent when the viewer is opened
  EXPORT_SAVED = 2, // Sent when an export file is saved
}

/**
 * Telemetry data structure
 */
interface TelemetryData {
  user_id: string;
  time_execution: number;
  valid_result: boolean;
  timezone: string;
  version: string;
  id_docker: string;
  type: TelemetryType;
}

/**
 * Default telemetry server URL
 */
const TELEMETRY_SERVER_URL =
  "https://7a98391a395292bd9f0f.lambda.simvia-app.fr/";
const TELEMETRY_USER_ID_KEY = "telemetryUserId";

/**
 * Global extension context for telemetry
 */
let extensionContext: vscode.ExtensionContext | undefined;

/**
 * Sets the extension context for telemetry
 * @param context VS Code extension context
 */
export function setTelemetryContext(context: vscode.ExtensionContext): void {
  extensionContext = context;
}

/**
 * Gets or creates a persistent user telemetry ID using VS Code's Memento storage
 * @param context VS Code extension context for persistent storage
 * @returns A promise that resolves to the user telemetry ID
 */
export async function getOrCreateUserTelemetryID(
  context: vscode.ExtensionContext
): Promise<string> {
  // Try to get the existing user ID from persistent storage
  const existingId = context.globalState.get<string>(TELEMETRY_USER_ID_KEY);

  if (existingId) {
    return existingId;
  }

  // If no existing ID, generate a new one and store it
  const newId = await utils.generateUuid();
  await context.globalState.update(TELEMETRY_USER_ID_KEY, newId);
  return newId;
}

/**
 * Sends telemetry data to the server
 * @param type The type of telemetry event
 */
export async function sendTelemetry(type: TelemetryType): Promise<void> {
  try {
    // Check if telemetry is enabled
    const config = vscode.workspace.getConfiguration("vs-code-aster");
    const isTelemetryEnabled = config.get<boolean>("enableTelemetry", true);

    if (!isTelemetryEnabled) {
      console.log(
        `[telemetry] Skipped event (telemetry disabled): ${TelemetryType[type]}`
      );
      return;
    }

    // Get or create persistent user ID
    const userId = extensionContext
      ? await getOrCreateUserTelemetryID(extensionContext)
      : await utils.generateUuid();

    // Generate telemetry data
    const telemetryData: TelemetryData = {
      user_id: userId,
      time_execution: 0,
      valid_result: true,
      timezone: utils.getTimezoneOffsetString(),
      version: utils.getPackageVersion(),
      id_docker: await utils.getVSCodeVersion(),
      type: type,
    };

    // Send telemetry data to server
    await utils.sendJsonRequestWithTimeout(TELEMETRY_SERVER_URL, telemetryData);

    console.log(`[telemetry] Sent event: ${TelemetryType[type]}`);
  } catch (error) {
    console.error(
      `[telemetry] Failed to send telemetry: $
      ${error instanceof Error ? error.message : String(error)}`
    );
  }
}
