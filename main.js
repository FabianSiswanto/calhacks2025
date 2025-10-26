const {
  app,
  BrowserWindow,
  ipcMain,
  globalShortcut,
  desktopCapturer,
  screen,
} = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const mouseHook = require("mac-mouse-hook");
const { io } = require("socket.io-client");

let mainWindow;
let overlayWindow = null; // Track the overlay window

// Mouse hook state
let isMouseHookActive = false;

// Service processes
let backendProcess = null;
let frontendProcess = null;
let overlayProcess = null;

// Service management functions
function startBackendService() {
  if (backendProcess) {
    console.log("Backend service already running");
    return;
  }

  console.log("Starting backend service...");
  backendProcess = spawn(path.join(__dirname, "backend/venv/bin/python"), ["backend/app.py"], {
    cwd: __dirname,
    env: { ...process.env, PYTHONPATH: path.join(__dirname, "backend") },
    stdio: ["pipe", "pipe", "pipe"]
  });

  backendProcess.stdout.on("data", (data) => {
    try {
      console.log(`Backend: ${data}`);
    } catch (e) {
      // Ignore EPIPE errors when process exits
    }
  });

  backendProcess.stderr.on("data", (data) => {
    try {
      console.error(`Backend Error: ${data}`);
    } catch (e) {
      // Ignore EPIPE errors when process exits
    }
  });

  backendProcess.on("close", (code) => {
    console.log(`Backend process exited with code ${code}`);
    backendProcess = null;
  });

  // Wait a moment for backend to start
  return new Promise((resolve) => {
    setTimeout(resolve, 2000);
  });
}

function startFrontendService() {
  if (frontendProcess) {
    console.log("Frontend service already running");
    return;
  }

  console.log("Starting frontend service...");
  frontendProcess = spawn("npm", ["start"], {
    cwd: path.join(__dirname, "frontend"),
    stdio: ["pipe", "pipe", "pipe"]
  });

  frontendProcess.stdout.on("data", (data) => {
    try {
      console.log(`Frontend: ${data}`);
    } catch (e) {
      // Ignore EPIPE errors when process exits
    }
  });

  frontendProcess.stderr.on("data", (data) => {
    try {
      console.error(`Frontend Error: ${data}`);
    } catch (e) {
      // Ignore EPIPE errors when process exits
    }
  });

  frontendProcess.on("close", (code) => {
    console.log(`Frontend process exited with code ${code}`);
    frontendProcess = null;
  });

  // Wait for React dev server to start
  return new Promise((resolve) => {
    setTimeout(resolve, 5000);
  });
}

function startOverlayService() {
  if (overlayProcess) {
    console.log("Overlay service already running");
    return;
  }

  console.log("Starting overlay service...");
  overlayProcess = spawn("npm", ["start"], {
    cwd: path.join(__dirname, "overlay-screen"),
    stdio: ["pipe", "pipe", "pipe"]
  });

  overlayProcess.stdout.on("data", (data) => {
    try {
      console.log(`Overlay: ${data}`);
    } catch (e) {
      // Ignore EPIPE errors when process exits
    }
  });

  overlayProcess.stderr.on("data", (data) => {
    try {
      console.error(`Overlay Error: ${data}`);
    } catch (e) {
      // Ignore EPIPE errors when process exits
    }
  });

  overlayProcess.on("close", (code) => {
    console.log(`Overlay process exited with code ${code}`);
    overlayProcess = null;
  });

  // Wait for React dev server to start
  return new Promise((resolve) => {
    setTimeout(resolve, 5000);
  });
}

async function startAllServices() {
  console.log("Starting all services...");
  
  try {
    await startBackendService();
    await startFrontendService();
    await startOverlayService();
    console.log("All services started successfully!");
  } catch (error) {
    console.error("Error starting services:", error);
  }
}

function stopAllServices() {
  console.log("Stopping all services...");
  
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
  
  if (frontendProcess) {
    frontendProcess.kill();
    frontendProcess = null;
  }
  
  if (overlayProcess) {
    overlayProcess.kill();
    overlayProcess = null;
  }
}

// Overlay screen function triggered by '/' key - creates a new Electron window
function triggerOverlayScreen() {
  // Check if overlay window already exists
  if (overlayWindow && !overlayWindow.isDestroyed()) {
    console.log("Overlay window already exists - closing it");
    overlayWindow.close();
    overlayWindow = null;
    return null;
  }

  console.log(
    'Overlay screen triggered by "/" key press - creating new window'
  );

  // Create a new overlay window - independent from main window
  overlayWindow = new BrowserWindow({
    width: 400,
    height: 175,
    minWidth: 200,
    minHeight: 150,
    // backgroundColor: "#00000000", // Fully transparent if needed
    // Remove parent property to make it independent
    // parent: mainWindow, // Removed - now independent
    // modal: false, // Not needed for independent window
    alwaysOnTop: true, // Keep it above other windows
    frame: false, // Frameless window required for transparency on macOS
    transparent: true, // Enable window transparency
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
      webSecurity: false,
    },
    title: "Overlay Screen",
    show: false, // Don't show until ready
    x: 100, // Position on desktop
    y: 100,
  });

  // Load content for the overlay window
  const isDev = !app.isPackaged;

  if (isDev) {
    // In development, try dev server first; fallback to built files if it fails
    overlayWindow.loadURL("http://localhost:3001").catch(() => {
      console.log(
        "Overlay dev server not available; falling back to built files"
      );
      overlayWindow.loadFile(
        path.join(__dirname, "overlay-screen/public/index.html")
      );
    });

    // Also handle async load failures
    overlayWindow.webContents.on(
      "did-fail-load",
      (_event, _errorCode, _errorDescription, validatedURL) => {
        if (validatedURL && validatedURL.startsWith("http://localhost:3001")) {
          console.log(
            "Overlay failed to load dev server; loading built files instead"
          );
          overlayWindow.loadFile(
            path.join(__dirname, "overlay-screen/public/index.html")
          );
        }
      }
    );
  } else {
    // In production, load the built React app
    overlayWindow.loadFile(
      path.join(__dirname, "overlay-screen/public/index.html")
    );
  }

  // Show and initialize after content is fully loaded
  overlayWindow.webContents.once("did-finish-load", () => {
    overlayWindow.show();
    console.log("Overlay window opened");
    
    // Open devtools automatically in development
    if (!app.isPackaged) {
      overlayWindow.webContents.openDevTools();
    }

    // Start WebSocket → IPC bridge so overlay receives messages via IPC too
    startOverlayIpcBridge();
  });

  // Handle overlay window closed
  overlayWindow.on("closed", () => {
    console.log("Overlay window closed");
    overlayWindow = null; // Reset the reference when closed

    // Tear down bridge socket if active
    if (global.__overlaySocket) {
      try {
        global.__overlaySocket.removeAllListeners();
        global.__overlaySocket.disconnect();
      } catch (_e) {}
      global.__overlaySocket = null;
    }
  });

  // Send message to main window that overlay was created
  if (mainWindow) {
    mainWindow.webContents.send(
      "child-process-output",
      "Overlay window created"
    );
  }

  return overlayWindow;
}

// Socket.IO → IPC bridge: forwards backend popup_message events to overlay renderer
function startOverlayIpcBridge() {
  try {
    // Avoid duplicate connections
    if (global.__overlaySocket && global.__overlaySocket.connected) {
      return;
    }

    const baseUrl = "http://localhost:5000";
    const socket = io(baseUrl, {
      transports: ["polling"],
      withCredentials: false,
      timeout: 10000,
      reconnection: true,
      reconnectionAttempts: 3,
      reconnectionDelay: 1000,
    });

    socket.on("connect", () => {
      console.log("Overlay IPC bridge connected:", socket.id);
      // Join the same room used by overlay
      socket.emit("join_user_room", { user_id: "overlay-user" }, (resp) => {
        console.log("join_user_room (bridge) resp:", resp);
      });
    });

    socket.on("popup_message", (data) => {
      const payload = {
        header: (data && (data.header || data.title)) || "Step",
        body: (data && (data.body || data.message)) || "",
        raw: data,
      };
      console.log("Bridge received popup_message; forwarding via IPC:", payload);
      if (overlayWindow && !overlayWindow.isDestroyed()) {
        overlayWindow.webContents.send("overlay-set-content", payload);
      }
    });

    socket.on("status", (data) => {
      console.log("Bridge status:", data);
    });

    socket.on("disconnect", () => {
      console.log("Overlay IPC bridge disconnected");
    });

    socket.on("connect_error", (err) => {
      console.warn("Overlay IPC bridge connect_error:", err && err.message);
      // Don't spam errors - this is expected during development
    });

    global.__overlaySocket = socket;
  } catch (error) {
    console.error("Failed to start Overlay IPC bridge:", error);
  }
}

// Mouse hook functions
function startMouseMonitoring() {
  if (isMouseHookActive) {
    console.log("Mouse hook already active");
    return;
  }

  try {
    mouseHook.start((event) => {
      // Print coordinates and timestamp
      console.log(
        `Mouse click: x=${event.x}, y=${
          event.y
        }, timestamp=${new Date().toISOString()}`
      );

      // Trigger action on every click
      triggerDebugAction(event);
    });

    isMouseHookActive = true;
  } catch (error) {
    console.error("Failed to start mouse hook:", error.message);

    if (error.message.includes("Accessibility permissions")) {
      console.log(
        "Please enable accessibility permissions in System Preferences > Security & Privacy > Privacy > Accessibility"
      );
    }
  }
}

function stopMouseMonitoring() {
  if (!isMouseHookActive) {
    return;
  }

  try {
    mouseHook.stop();
    isMouseHookActive = false;
  } catch (error) {
    console.error("Failed to stop mouse hook:", error.message);
  }
}

function triggerDebugAction(lastEvent) {
  console.log(
    `Action triggered: x=${lastEvent.x}, y=${
      lastEvent.y
    }, timestamp=${new Date().toISOString()}`
  );

  // Send debug message to main window if it exists
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send("mouse-hook-debug", {
      action: "click-detected",
      clickData: lastEvent,
      timestamp: new Date().toISOString(),
    });
  }

  // Send debug message to overlay window if it exists
  if (overlayWindow && !overlayWindow.isDestroyed()) {
    overlayWindow.webContents.send("mouse-hook-debug", {
      action: "click-detected",
      clickData: lastEvent,
      timestamp: new Date().toISOString(),
    });
  }
}

async function createWindow() {
  // Start all services first
  await startAllServices();

  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
      webSecurity: false, // Allow localhost requests
    },
    icon: path.join(__dirname, "assets/icon.png"), // Optional: add an icon
    show: false, // Don't show until ready
  });

  // Load the React app
  const isDev = !app.isPackaged;

  if (isDev) {
    // In development, load from React dev server
    mainWindow.loadURL("http://localhost:3000");
  } else {
    // In production, load from built React app
    mainWindow.loadFile(path.join(__dirname, "frontend/public/index.html"));
  }

  // Show window when ready
  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
  });

  // Handle window closed
  mainWindow.on("closed", () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    require("electron").shell.openExternal(url);
    return { action: "deny" };
  });
}

// This method will be called when Electron has finished initialization
app.whenReady().then(() => {
  createWindow();

  // Register global shortcut for '/' key
  // Toggle behavior: creates overlay if none exists, closes it if it exists
  const ret = globalShortcut.register("/", () => {
    console.log('Global shortcut "/" pressed');
    triggerOverlayScreen();
  });

  if (!ret) {
    console.log('Registration of global shortcut "/" failed');
  }

  // Start mouse monitoring automatically
  startMouseMonitoring();

  app.on("activate", () => {
    // On macOS, re-create window when dock icon is clicked
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed
app.on("window-all-closed", () => {
  // Close overlay window if it exists
  if (overlayWindow && !overlayWindow.isDestroyed()) {
    overlayWindow.close();
    overlayWindow = null;
  }

  // Unregister all global shortcuts
  globalShortcut.unregisterAll();

  // Stop all services
  stopAllServices();

  // On macOS, keep app running even when all windows are closed
  if (process.platform !== "darwin") {
    app.quit();
  }
});

// Handle app before quit to ensure proper cleanup
app.on("before-quit", () => {
  // Stop mouse monitoring
  if (isMouseHookActive) {
    stopMouseMonitoring();
  }

  // Close overlay window if it exists
  if (overlayWindow && !overlayWindow.isDestroyed()) {
    overlayWindow.close();
    overlayWindow = null;
  }

  // Stop all services
  stopAllServices();
});

// Security: Prevent new window creation
app.on("web-contents-created", (event, contents) => {
  contents.on("new-window", (event, navigationUrl) => {
    event.preventDefault();
    require("electron").shell.openExternal(navigationUrl);
  });
});

// IPC handlers for communication with renderer process
ipcMain.handle("get-backend-status", () => ({ 
  isRunning: backendProcess !== null,
  pid: backendProcess ? backendProcess.pid : null
}));

ipcMain.handle("restart-backend", async () => {
  try {
    if (backendProcess) {
      backendProcess.kill();
      backendProcess = null;
    }
    await startBackendService();
    return { success: true, pid: backendProcess ? backendProcess.pid : null };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// IPC handler to trigger overlay screen from renderer
ipcMain.handle("trigger-child-process", () => {
  try {
    const process = triggerOverlayScreen();
    return {
      success: true,
      pid: process ? process.pid : null,
      action: overlayWindow ? "opened" : "closed",
    };
  } catch (error) {
    console.error("Error triggering overlay screen:", error);
    return { success: false, error: error.message };
  }
});

// IPC handler for taking screenshots
ipcMain.handle("take-screenshot", async () => {
  try {
    const sources = await desktopCapturer.getSources({
      types: ["screen"],
      thumbnailSize: { width: 1920, height: 1080 },
    });

    if (sources.length === 0) {
      throw new Error("No screen sources available");
    }

    // Get the primary display
    const primaryDisplay = screen.getPrimaryDisplay();
    const source =
      sources.find(
        (source) =>
          source.name === "Entire Screen" || source.name === "Screen 1"
      ) || sources[0];

    // Convert to base64
    const screenshot = source.thumbnail.toPNG();
    const base64Image = screenshot.toString("base64");

    return {
      success: true,
      data: base64Image,
      size: screenshot.length,
      display: {
        width: primaryDisplay.bounds.width,
        height: primaryDisplay.bounds.height,
      },
    };
  } catch (error) {
    console.error("Error taking screenshot:", error);
    return { success: false, error: error.message };
  }
});

// Mouse hook IPC handlers
ipcMain.handle("start-mouse-monitoring", () => {
  startMouseMonitoring();
  return { success: true, active: isMouseHookActive };
});

ipcMain.handle("stop-mouse-monitoring", () => {
  stopMouseMonitoring();
  return { success: true, active: isMouseHookActive };
});

ipcMain.handle("get-mouse-hook-status", () => {
  return {
    active: isMouseHookActive,
  };
});

// Handle app activation (macOS)
app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
