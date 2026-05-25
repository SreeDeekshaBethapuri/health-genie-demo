"use client";

import { useState, useEffect, useRef } from "react";
import { sendChat, Option, CTA } from "../lib/api";

interface Message {
  role: "assistant" | "user";
  text: string;
  cta?: CTA | null;
  isEnd?: boolean;
}

type UserBranch = "new_user" | "returning_user" | null;

const FOLLOWUP_OPTIONS: Option[] = [
  { label: "Yes, I need help with something else", value: "continue_help" },
  { label: "I'm good for now", value: "end_chat" },
];

export default function HealthGenieWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [options, setOptions] = useState<Option[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<string | null>(null);
  const [userBranch, setUserBranch] = useState<UserBranch>(null);
  const [chatEnded, setChatEnded] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [isSending, setIsSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, options]);

  const handleOpen = async () => {
    setOpen(true);
    if (messages.length === 0) {
      await fetchStep(null, null, null, null);
    }
  };

  const fetchStep = async (
    sid: string | null,
    step: string | null,
    option: string | null,
    branch: UserBranch
  ) => {
    try {
      const data = await sendChat({
        session_id: sid,
        current_step: step,
        selected_option: option,
        user_branch: branch,
      });

      setSessionId(data.session_id);
      setCurrentStep(data.step);
      if (data.user_branch) setUserBranch(data.user_branch);

      const isEnd = data.step === "end_chat";
      const isTerminalCta = data.cta !== null && data.options.length === 0;

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.message, cta: data.cta, isEnd },
      ]);

      if (isEnd) {
        setChatEnded(true);
        setOptions([]);
      } else if (isTerminalCta) {
        // Show follow-up after a natural pause
        setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            { role: "assistant", text: "Is there anything else I can help you with today?" },
          ]);
          setOptions(FOLLOWUP_OPTIONS);
        }, 700);
      } else {
        setOptions(data.options);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Sorry, something went wrong. Please try again." },
      ]);
      setOptions([]);
    }
  };

  const handleOption = async (opt: Option) => {
    setMessages((prev) => [...prev, { role: "user", text: opt.label }]);
    setOptions([]);

    // Resolve the branch before the async call — state update is async so we
    // compute the new value synchronously and pass it directly
    let nextBranch: UserBranch = userBranch;
    if (opt.value === "new_user" || opt.value === "returning_user") {
      nextBranch = opt.value;
      setUserBranch(nextBranch);
    }

    await fetchStep(sessionId, currentStep, opt.value, nextBranch);
  };

  const handleSend = async () => {
    const text = inputValue.trim();
    if (!text || isSending) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInputValue("");
    setOptions([]);
    setIsSending(true);

    try {
      const data = await sendChat({
        session_id: sessionId,
        current_step: currentStep,
        selected_option: null,
        user_branch: userBranch,
        message: text,
      });

      setSessionId(data.session_id);
      setCurrentStep(data.step);
      if (data.user_branch) setUserBranch(data.user_branch);

      const isEnd = data.step === "end_chat";

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.message, cta: data.cta, isEnd },
      ]);

      if (isEnd) {
        setChatEnded(true);
        setOptions([]);
      } else {
        setOptions(data.options);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <>
      {/* Floating launcher */}
      {!open && (
        <button onClick={handleOpen} style={styles.fab} aria-label="Open Health Genie">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
            stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          <span>Health Genie</span>
        </button>
      )}

      {/* Chat panel */}
      {open && (
        <div style={styles.panel}>
          <div style={styles.panelHeader}>
            <div>
              <div style={styles.panelTitle}>Health Genie</div>
              <div style={styles.panelSub}>Your Health Vibe guide</div>
            </div>
            <button onClick={() => setOpen(false)} style={styles.closeBtn} aria-label="Close">
              ✕
            </button>
          </div>

          <div style={styles.messages}>
            {messages.map((msg, i) => (
              <div key={i} style={styles.messageRow}>
                <div
                  style={{
                    ...styles.bubble,
                    ...(msg.role === "user" ? styles.bubbleUser : styles.bubbleAssistant),
                  }}
                >
                  {msg.text}
                </div>

                {msg.cta && (
                  <a href={msg.cta.url} style={styles.ctaBtn}
                    target="_blank" rel="noopener noreferrer">
                    {msg.cta.label} →
                  </a>
                )}

                {msg.isEnd && (
                  <p style={styles.endHelper}>
                    You can reopen Health Genie anytime if you need help.
                  </p>
                )}
              </div>
            ))}

            {!chatEnded && options.length > 0 && (
              <div style={styles.optionList}>
                {options.map((opt) => (
                  <button key={opt.value} onClick={() => handleOption(opt)} style={styles.optionBtn}>
                    {opt.label}
                  </button>
                ))}
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {!chatEnded && (
            <div style={styles.inputArea}>
              <input
                type="text"
                placeholder="Ask a question…"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") handleSend(); }}
                disabled={isSending}
                style={styles.input}
                aria-label="Type a question"
              />
              <button
                onClick={handleSend}
                disabled={isSending}
                style={{
                  ...styles.sendBtn,
                  opacity: isSending ? 0.6 : 1,
                  cursor: isSending ? "not-allowed" : "pointer",
                }}
              >
                Send
              </button>
            </div>
          )}
        </div>
      )}
    </>
  );
}

const styles: Record<string, React.CSSProperties> = {
  fab: {
    position: "fixed",
    bottom: 28,
    right: 28,
    background: "var(--purple)",
    color: "#fff",
    border: "none",
    borderRadius: 32,
    padding: "12px 20px",
    display: "flex",
    alignItems: "center",
    gap: 8,
    cursor: "pointer",
    boxShadow: "0 4px 14px rgba(124,58,237,0.45)",
    fontSize: 14,
    fontWeight: 600,
    zIndex: 1000,
  },
  panel: {
    position: "fixed",
    bottom: 28,
    right: 28,
    width: 360,
    maxHeight: "75vh",
    background: "#fff",
    borderRadius: 16,
    boxShadow: "0 20px 40px rgba(0,0,0,0.15)",
    display: "flex",
    flexDirection: "column",
    zIndex: 1000,
    overflow: "hidden",
    border: "1px solid var(--border)",
  },
  panelHeader: {
    background: "var(--purple)",
    color: "#fff",
    padding: "16px 18px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    flexShrink: 0,
  },
  panelTitle: {
    fontWeight: 700,
    fontSize: 15,
  },
  panelSub: {
    fontSize: 12,
    opacity: 0.85,
    marginTop: 2,
  },
  closeBtn: {
    background: "none",
    border: "none",
    color: "#fff",
    fontSize: 16,
    cursor: "pointer",
    lineHeight: 1,
    padding: 4,
    opacity: 0.85,
  },
  messages: {
    flex: 1,
    overflowY: "auto",
    padding: "16px 14px 20px",
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
  messageRow: {
    display: "flex",
    flexDirection: "column",
    gap: 6,
  },
  bubble: {
    maxWidth: "85%",
    padding: "10px 13px",
    borderRadius: 12,
    fontSize: 13.5,
    lineHeight: 1.5,
    wordBreak: "break-word",
  },
  bubbleAssistant: {
    background: "var(--purple-light)",
    color: "var(--text)",
    borderBottomLeftRadius: 3,
    alignSelf: "flex-start",
  },
  bubbleUser: {
    background: "var(--purple)",
    color: "#fff",
    borderBottomRightRadius: 3,
    alignSelf: "flex-end",
  },
  ctaBtn: {
    display: "inline-block",
    alignSelf: "flex-start",
    background: "var(--purple)",
    color: "#fff",
    borderRadius: 8,
    padding: "9px 14px",
    fontSize: 13,
    fontWeight: 600,
    textDecoration: "none",
  },
  endHelper: {
    fontSize: 12,
    color: "var(--text-muted)",
    lineHeight: 1.5,
    alignSelf: "flex-start",
    maxWidth: "85%",
  },
  optionList: {
    display: "flex",
    flexDirection: "column",
    gap: 7,
    alignSelf: "stretch",
    marginTop: 2,
  },
  optionBtn: {
    background: "#fff",
    border: "1.5px solid var(--purple)",
    color: "var(--purple)",
    borderRadius: 8,
    padding: "8px 12px",
    fontSize: 13,
    fontWeight: 500,
    cursor: "pointer",
    textAlign: "left",
    lineHeight: 1.4,
  },
  inputArea: {
    display: "flex",
    gap: 8,
    padding: "10px 12px",
    borderTop: "1px solid var(--border)",
    flexShrink: 0,
    background: "#fff",
  },
  input: {
    flex: 1,
    border: "1.5px solid var(--border)",
    borderRadius: 8,
    padding: "8px 10px",
    fontSize: 13,
    outline: "none",
    color: "var(--text)",
    background: "#fafafa",
  },
  sendBtn: {
    background: "var(--purple)",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    padding: "8px 14px",
    fontSize: 13,
    fontWeight: 600,
    flexShrink: 0,
  },
};
