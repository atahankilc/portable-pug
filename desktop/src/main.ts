import { app, BrowserWindow } from "electron";
import path from "path";
import { startSidecar, stopSidecar } from "./sidecar";

const DEPLOYMENT_MODE = process.env.DEPLOYMENT_MODE ?? "local";
const isDev = !app.isPackaged;
const needsSidecar = !isDev && DEPLOYMENT_MODE !== "cloud";
const EXPO_DEV_URL = "http://localhost:8081";

let mainWindow: BrowserWindow | null = null;

function getWebRoot(): string {
  // In packaged app: resources/web/  (copied by electron-builder extraResources)
  // In dev: ../resources/web/       (copied by build script or symlinked)
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "web");
  }
  return path.join(__dirname, "..", "resources", "web");
}

async function createWindow(): Promise<void> {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (isDev) {
    await mainWindow.loadURL(EXPO_DEV_URL);
    mainWindow.webContents.openDevTools();
  } else {
    const webRoot = getWebRoot();
    await mainWindow.loadFile(path.join(webRoot, "index.html"));
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  if (needsSidecar) {
    try {
      await startSidecar();
    } catch (err) {
      console.error("Failed to start backend sidecar:", err);
      app.quit();
      return;
    }
  }

  await createWindow();

  app.on("activate", async () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      await createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("will-quit", () => {
  stopSidecar();
});
