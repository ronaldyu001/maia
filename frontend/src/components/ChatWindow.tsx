import { useEffect, useRef, useState } from "react";
import Message from "./Message";
import { sendMessage } from "../api/chat";

type Turn = { role: "user" | "maia"; text: string };

export default function ChatWindow() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const sessionIdRef = useRef<string>("");

  useEffect(() => {
    sessionIdRef.current = crypto.randomUUID();
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [turns]);

  async function handleSend() {
    const msg = input.trim();
    if (!msg) { setInput(""); return; }
    const next = [...turns, { role: "user" as const, text: msg }];
    setTurns(next);
    setInput("");
    try {
      const reply = await sendMessage(msg, String(sessionIdRef.current));
      setTurns([...next, { role: "maia" as const, text: reply }]);
    } catch (e) {
      setTurns([...next, { role: "maia" as const, text: "⚠️ Error talking to backend." }]);
      console.error(e);
    }
  }

  function handleKey(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: "linear-gradient(135deg, #232526 0%, #414345 100%)",
      display: "flex",
      alignItems: "stretch",
      justifyContent: "center",
      padding: 0,
      margin: 0,
      overflow: "hidden",
    }}>
      <div style={{
        width: "100%",
        maxWidth: "100%",
        height: "100vh",
        background: "#181c23",
        borderRadius: 20,
        boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.25)",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        border: "1px solid #23272f",
      }}>
        {/* Header */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "20px 28px 16px 28px",
          background: "rgba(24,28,35,0.98)",
          borderBottom: "1px solid #23272f",
        }}>
          <div style={{
            width: 36,
            height: 36,
            borderRadius: "50%",
            background: "linear-gradient(135deg, #238636 0%, #1f6feb 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 700,
            fontSize: 20,
            color: "#fff",
            boxShadow: "0 2px 8px rgba(35,134,54,0.15)",
            userSelect: "none",
          }}>
            M
          </div>
          <span style={{
            fontWeight: 700,
            fontSize: 20,
            letterSpacing: 0.5,
            color: "#fff",
          }}>
            Maia
          </span>
        </div>

        {/* Message history */}
        <div
          ref={scrollRef}
          style={{
            flex: 1,
            overflowY: "auto",
            background: "#181c23",
            padding: "24px 18px 18px 18px",
            display: "flex",
            flexDirection: "column",
            gap: 0,
          }}
        >
          {turns.length === 0 && (
            <div style={{
              color: "#7a8599",
              textAlign: "center",
              marginTop: 40,
              fontSize: 16,
              letterSpacing: 0.1,
            }}>
              Start a conversation with Maia!
            </div>
          )}
          {turns.map((t, i) => (
            <Message key={i} role={t.role} text={t.text} />
          ))}
        </div>

        {/* Input bar */}
        <div style={{
          padding: "18px 20px 18px 20px",
          background: "rgba(24,28,35,0.98)",
          borderTop: "1px solid #23272f",
        }}>
          <form
            style={{ display: "flex", gap: 10 }}
            onSubmit={e => { e.preventDefault(); handleSend(); }}
            autoComplete="off"
          >
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Message Maia…"
              style={{
                flex: 1,
                padding: "14px 16px",
                borderRadius: 12,
                border: "1.5px solid #23272f",
                background: "#23272f",
                color: "#e6edf3",
                fontSize: 16,
                outline: "none",
                transition: "border 0.2s",
                boxShadow: "0 1px 4px rgba(0,0,0,0.07)",
              }}
            />
            <button
              type="submit"
              style={{
                padding: "0 22px",
                borderRadius: 10,
                border: "none",
                background: input.trim() ? "linear-gradient(135deg, #238636 0%, #1f6feb 100%)" : "#23272f",
                color: input.trim() ? "#fff" : "#7a8599",
                fontWeight: 700,
                fontSize: 16,
                cursor: input.trim() ? "pointer" : "not-allowed",
                boxShadow: input.trim() ? "0 2px 8px rgba(35,134,54,0.10)" : "none",
                transition: "background 0.2s, color 0.2s",
              }}
              disabled={!input.trim()}
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
