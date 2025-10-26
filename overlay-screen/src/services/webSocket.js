import { io } from "socket.io-client";

let socket = null;
let listener = null;

function deriveBaseUrl(inputUrl) {
  try {
    const u = new URL(inputUrl);
    const isWs = u.protocol === "ws:" || u.protocol === "wss:";
    const protocol = isWs ? (u.protocol === "wss:" ? "https:" : "http:") : u.protocol;
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
  });

  socket.on("disconnect", () => {
    console.log("❌ WebSocket disconnected");
  });

  socket.on("connect_error", (error) => {
    console.error("💥 WebSocket connection error:", error);
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
    } catch (_e) {
    }
    socket = null;
  }
  listener = null;
}

export default {
  connectWebSocket,
  subscribeWebSocket,
  disconnectWebSocket,
};
