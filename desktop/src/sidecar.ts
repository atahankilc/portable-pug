import { app } from "electron";
import { ChildProcess, spawn } from "child_process";
import path from "path";
import http from "http";

const SIDECAR_HOST = "127.0.0.1";
const SIDECAR_PORT = 8000;
const HEALTH_CHECK_URL = `http://${SIDECAR_HOST}:${SIDECAR_PORT}/api/`;
const HEALTH_CHECK_TIMEOUT_MS = 30_000;
const HEALTH_CHECK_INTERVAL_MS = 500;

let sidecarProcess: ChildProcess | null = null;

function getSidecarPath(): string {
  if (app.isPackaged) {
    const ext = process.platform === "win32" ? ".exe" : "";
    return path.join(process.resourcesPath, "sidecar", `run_server${ext}`);
  }
  // Dev mode: point to PyInstaller output
  return path.join(__dirname, "..", "resources", "sidecar", "run_server");
}

function healthCheck(): Promise<boolean> {
  return new Promise((resolve) => {
    const req = http.get(HEALTH_CHECK_URL, (res) => {
      resolve(res.statusCode !== undefined && res.statusCode < 500);
    });
    req.on("error", () => resolve(false));
    req.setTimeout(2000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

function waitForHealthy(): Promise<void> {
  return new Promise((resolve, reject) => {
    const start = Date.now();

    const check = async () => {
      if (Date.now() - start > HEALTH_CHECK_TIMEOUT_MS) {
        reject(new Error(`Sidecar did not become healthy within ${HEALTH_CHECK_TIMEOUT_MS}ms`));
        return;
      }
      const ok = await healthCheck();
      if (ok) {
        resolve();
      } else {
        setTimeout(check, HEALTH_CHECK_INTERVAL_MS);
      }
    };

    check();
  });
}

export async function startSidecar(): Promise<void> {
  const sidecarPath = getSidecarPath();

  console.log(`Starting sidecar: ${sidecarPath}`);

  sidecarProcess = spawn(sidecarPath, [], {
    env: {
      ...process.env,
      DJANGO_SETTINGS_MODULE: "core_api.settings.local",
    },
    stdio: ["ignore", "pipe", "pipe"],
  });

  sidecarProcess.stdout?.on("data", (data: Buffer) => {
    console.log(`[sidecar] ${data.toString().trim()}`);
  });

  sidecarProcess.stderr?.on("data", (data: Buffer) => {
    console.error(`[sidecar] ${data.toString().trim()}`);
  });

  sidecarProcess.on("exit", (code) => {
    console.log(`Sidecar exited with code ${code}`);
    sidecarProcess = null;
  });

  await waitForHealthy();
  console.log("Sidecar is healthy");
}

export function stopSidecar(): void {
  if (!sidecarProcess) return;

  console.log("Stopping sidecar...");

  if (process.platform === "win32") {
    sidecarProcess.kill();
  } else {
    sidecarProcess.kill("SIGTERM");
    // Force kill after 5 seconds if still alive
    const forceKillTimer = setTimeout(() => {
      if (sidecarProcess) {
        sidecarProcess.kill("SIGKILL");
      }
    }, 5000);
    sidecarProcess.on("exit", () => clearTimeout(forceKillTimer));
  }
}
