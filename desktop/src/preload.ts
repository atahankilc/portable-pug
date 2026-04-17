import { contextBridge } from "electron";

contextBridge.exposeInMainWorld("electronAPI", {
  isElectron: true,
  deploymentMode: process.env.DEPLOYMENT_MODE ?? "local",
});
