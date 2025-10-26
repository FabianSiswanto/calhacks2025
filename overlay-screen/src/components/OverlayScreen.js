import React, { useEffect, useRef, useState } from "react";
import "./OverlayScreen.css";
import screenshotService from "../services/screenshotService";
import wsClient from "../services/webSocket";

const OverlayScreen = () => {
  const [header, setHeader] = useState("Waiting for updates…");
  const [body, setBody] = useState("This will update when a message arrives.");
  const hasRealtimeRef = useRef(false);

  useEffect(() => {
    console.log("🚀 OverlayScreen useEffect started");

    const url = process.env.REACT_APP_WS_URL || "ws://localhost:5000/ws";
    console.log("🔌 Connecting to WebSocket:", url);
    wsClient.connectWebSocket(url);

    const unsubscribe = wsClient.subscribeWebSocket(({ header, body }) => {
      console.log("🔄 OverlayScreen received WebSocket update:", {
        header,
        body,
      });
      console.log("📝 Setting header to:", header);
      console.log("📝 Setting body to:", body);
      hasRealtimeRef.current = true;
      setHeader(header);
      setBody(body);
    });

    // Also subscribe to IPC fallback if available
    let removeIpc = null;
    if (window.electronAPI && window.electronAPI.onOverlaySetContent) {
      const ipcHandler = (payload) => {
        try {
          const h = (payload && (payload.header || payload.title)) || "Step";
          const b = (payload && (payload.body || payload.message)) || "";
          console.log("🔄 OverlayScreen received IPC update:", {
            header: h,
            body: b,
          });
          setHeader(h);
          setBody(b);
        } catch (e) {
          console.error("IPC content handler error:", e);
        }
      };
      window.electronAPI.onOverlaySetContent(ipcHandler);
      removeIpc = () => {
        try {
          window.electronAPI.onOverlaySetContent(() => {});
        } catch (_e) {}
      };
    }

    return () => {
      console.log("🧹 Cleaning up WebSocket connection");
      unsubscribe();
      wsClient.disconnectWebSocket();
      if (removeIpc) removeIpc();
    };
  }, []);

  return (
    <div className="overlay-screen">
      <h1 className="overlay-header">{header}</h1>
      <p className="overlay-body">{body}</p>
    </div>
  );
};

export default OverlayScreen;
