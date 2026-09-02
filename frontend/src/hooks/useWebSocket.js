import { useEffect, useRef, useState } from "react";

const WS_URL = "ws://127.0.0.1:8000/ws";

export function useWebSocket(onEvent) {
  const socketRef = useRef(null);
  const callbackRef = useRef(onEvent);

  const [connected, setConnected] = useState(false);

  useEffect(() => {
    callbackRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    let reconnectTimer = null;
    let manuallyClosed = false;

    const connect = () => {
      if (manuallyClosed) return;

      const socket = new WebSocket(WS_URL);

      socketRef.current = socket;

      socket.onopen = () => {
        console.log("[WS] Connected to EMERGE-AI");
        setConnected(true);
      };

      socket.onmessage = (message) => {
        try {
          const payload = JSON.parse(message.data);

          console.log("[WS] Event:", payload);

          callbackRef.current?.(payload);
        } catch (error) {
          console.error("[WS] Invalid message:", error);
        }
      };

      socket.onclose = () => {
        console.log("[WS] Connection closed");

        setConnected(false);

        if (!manuallyClosed) {
          reconnectTimer = setTimeout(() => {
            console.log("[WS] Reconnecting...");
            connect();
          }, 2000);
        }
      };

      socket.onerror = (error) => {
        console.error("[WS] Error:", error);
      };
    };

    connect();

    return () => {
      manuallyClosed = true;

      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }

      socketRef.current?.close();
    };
  }, []);

  return {
    connected,
  };
}