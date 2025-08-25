type Props = { role: "user" | "maia"; text: string };

export default function Message({ role, text }: Props) {
  const isUser = role === "user";
  return (
    <div style={{
      display: "flex",
      justifyContent: isUser ? "flex-end" : "flex-start",
      margin: "8px 0"
    }}>
      <div style={{
        maxWidth: "75%",
        whiteSpace: "pre-wrap",
        lineHeight: 1.4,
        padding: "10px 12px",
        borderRadius: 12,
        borderTopRightRadius: isUser ? 2 : 12,
        borderTopLeftRadius: isUser ? 12 : 2,
        background: isUser ? "#1f6feb" : "#22272e",
        color: "white",
        boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
      }}>
        {text}
      </div>
    </div>
  );
}
