import { useState, useRef, useEffect } from "react";
import { sendChat } from "../api";

const WELCOME = {
  role: "bot",
  text: "Hi! Ask me anything about laptops — battery life, performance, thermals, pricing, comparisons, and more.",
  meta: null,
};

export default function Chatbot() {
  const [open, setOpen]       = useState(false);
  const [msgs, setMsgs]       = useState([WELCOME]);
  const [input, setInput]     = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef             = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs]);

  const send = async () => {
    const q = input.trim();
    if (!q || loading) return;
    setInput("");
    setMsgs(p => [...p, { role: "user", text: q, meta: null }]);
    setLoading(true);
    try {
      const r = await sendChat(q);
      setMsgs(p => [...p, { role: "bot", text: r.data.answer, meta: r.data.meta }]);
    } catch {
      setMsgs(p => [...p, {
        role: "bot",
        text: "Could not reach the API. Make sure the backend is running on port 8000.",
        meta: null,
      }]);
    }
    setLoading(false);
  };

  const onKey = e => { if (e.key === "Enter") send(); };

  return (
    <>
      <button className="chat-fab" onClick={() => setOpen(o => !o)} title="Ask AI">
        {open ? "×" : "AI"}
      </button>

      {open && (
        <div className="chat-window">
          <div className="chat-header">
            <div>
              <div style={{ fontWeight: 700 }}>Laptop AI Assistant</div>
              <div style={{ fontSize: "0.72rem", opacity: 0.85, fontWeight: 400 }}>
                RAG + Gemini powered
              </div>
            </div>
            <button onClick={() => setOpen(false)}
              style={{ background: "none", border: "none", color: "#fff", fontSize: "1.2rem", cursor: "pointer", lineHeight: 1 }}>
              ×
            </button>
          </div>

          <div className="chat-messages">
            {msgs.map((m, i) => (
              <div key={i} className={`chat-msg ${m.role}`}>
                <div style={{ whiteSpace: "pre-wrap" }}>{m.text}</div>
                {m.meta && (
                  <div className="chat-meta">
                    <span style={{ fontWeight: 600 }}>{m.meta.product}</span>
                    {" · "}{m.meta.brand}
                    {" · "}Sentiment: <span style={{
                      color: m.meta.tone === "positive" ? "#16a34a" : m.meta.tone === "negative" ? "#dc2626" : "#64748b",
                      fontWeight: 600,
                    }}>{m.meta.tone}</span>
                    {" · "}{m.meta.sources} sources
                    {m.meta.gemini && <span style={{ marginLeft: 6, color: "#4f46e5", fontWeight: 600 }}>· Gemini</span>}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="chat-msg bot" style={{ color: "#94a3b8", fontStyle: "italic" }}>
                Searching reviews and generating answer...
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="chat-input-row">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={onKey}
              placeholder="e.g. best battery life laptop..."
              disabled={loading}
            />
            <button onClick={send} disabled={loading || !input.trim()}>Send</button>
          </div>
        </div>
      )}
    </>
  );
}
