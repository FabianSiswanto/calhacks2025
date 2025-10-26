import { io } from "socket.io-client";

let socket = null;
let listener = null;
let mockTimers = [];
let mockStarted = false;

function deriveBaseUrl(inputUrl) {
  try {
    const u = new URL(inputUrl);
    const isWs = u.protocol === "ws:" || u.protocol === "wss:";
    const protocol = isWs
      ? u.protocol === "wss:"
        ? "https:"
        : "http:"
      : u.protocol;
    return `${protocol}//${u.host}`; // strip path; socket.io uses /socket.io
  } catch (_e) {
    return inputUrl; // fallback if malformed
  }
}

export function connectWebSocket(url) {
  if (socket && socket.connected) {
    return socket;
  }

  const baseUrl = deriveBaseUrl(url || "http://localhost:5000");
  console.log("🔌 Connecting to WebSocket:", baseUrl);

  socket = io(baseUrl, {
    transports: ["polling"], // force polling to avoid websocket handshake issues with Werkzeug
    withCredentials: false,
  });

  // Log all incoming events for debugging
  socket.onAny((event, ...args) => {
    try {
      console.log("📥 onAny:", event, args);
    } catch (_e) {}
  });

  // Connection events
  socket.on("connect", () => {
    console.log("✅ WebSocket connected:", socket.id);
    console.log("📤 Emitting join_user_room event for overlay-user");
    // Join the overlay-user room
    socket.emit("join_user_room", { user_id: "overlay-user" }, (response) => {
      console.log("📥 join_user_room response:", response);
    });

    // Optionally start mock messages when connected
    if (process.env.REACT_APP_WS_MOCK === "1" && !mockStarted) {
      console.log("🧪 Starting mock WebSocket schedule (on connect)");
      startMockMessages();
    }
  });

  socket.on("disconnect", () => {
    console.log("❌ WebSocket disconnected");
  });

  socket.on("connect_error", (error) => {
    console.error("💥 WebSocket connection error:", error);
    // If mocking enabled, kick off schedule even if we cannot connect
    if (process.env.REACT_APP_WS_MOCK === "1" && !mockStarted) {
      console.log("🧪 Starting mock WebSocket schedule (connect_error)");
      startMockMessages();
    }
  });

  // Optional connection status event from backend
  socket.on("status", (data) => {
    console.log("📡 WebSocket status:", data);
  });

  // Core popup channel from Flask-SocketIO
  socket.on("popup_message", (data) => {
    console.log("📨 Received popup_message:", data);
    console.log("🔍 Listener function exists:", typeof listener === "function");
    if (typeof listener === "function") {
      // Map backend shape -> UI-consumed shape
      const mapped = {
        header: data?.header || "Step",
        body: data?.body || data?.message || "",
        raw: data,
      };
      console.log("🔄 Mapped data:", mapped);
      console.log("📤 Calling listener with:", mapped);
      try {
        listener(mapped);
        console.log("✅ Listener called successfully");
      } catch (e) {
        console.error("❌ Error in listener:", e);
      }
    } else {
      console.warn("⚠️ No listener function registered");
    }
  });

  return socket;
}

export function subscribeWebSocket(callback) {
  if (typeof callback === "function") {
    listener = callback;
    return () => {
      if (listener === callback) listener = null;
    };
  }
  return () => {};
}

export function disconnectWebSocket() {
  if (socket) {
    try {
      socket.removeAllListeners();
      socket.disconnect();
    } catch (_e) {}
    socket = null;
  }
  listener = null;
  stopMockMessages();
}

function schedule(messages) {
  stopMockMessages();
  mockStarted = true;
  mockTimers = messages.map(({ delayMs, header, body }) =>
    setTimeout(() => {
      if (typeof listener === "function") {
        try {
          listener({ header, body, raw: { header, body, mock: true } });
        } catch (e) {
          console.error("❌ Error in mock listener call:", e);
        }
      }
    }, Math.max(0, delayMs || 0))
  );
}

export function startMockMessages(customMessages) {
  const defaults = [
    {
      delayMs: 1000,
      header: "Welcome",
      body: "Go to www.figma.com, click 'Get started', enter your details, and complete a quick verification activity.",
    },
    {
      delayMs: 3000,
      header: "Step 1",
      body: "Click the 'New Project' button on the Figma dashboard.",
    },
    { delayMs: 6000, header: "Tip", body: "Use F to quickly create frames." },
    {
      delayMs: 9000,
      header: "Step 2",
      body: "Open the Main menu, hover over 'View', and select 'Rulers'.",
    },
    {
      delayMs: 12000,
      header: "Reminder",
      body: "Click and drag on the canvas to create a new frame.",
    },
    {
      delayMs: 15000,
      header: "Step 3",
      body: "Click the 'Rectangle' tool in the toolbar and click and drag on the canvas to create a new rectangle.",
    },
    {
      delayMs: 1500,
      header: "Step 4",
      body: "Select the rectangle layer, go to the 'Arrange' menu, and select 'Align' to center the rectangle horizontally and vertically",
    },
    {
      delayMs: 1500,
      header: "Step 5",
      body: "Use the zoom controls in the toolbar or the keyboard shortcuts to zoom in and out of the canvas",
    },
  ];
  const scheduleList =
    Array.isArray(customMessages) && customMessages.length > 0
      ? customMessages
      : defaults;
  console.log("🧪 Scheduling mock messages:", scheduleList);
  schedule(scheduleList);
}

export function stopMockMessages() {
  if (mockTimers && mockTimers.length) {
    try {
      mockTimers.forEach((t) => clearTimeout(t));
    } catch (_e) {}
  }
  mockTimers = [];
  mockStarted = false;
}

export default {
  connectWebSocket,
  subscribeWebSocket,
  disconnectWebSocket,
  startMockMessages,
  stopMockMessages,
};
