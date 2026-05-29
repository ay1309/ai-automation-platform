import { useState } from "react";
import api from "../services/api";
import MessageBubble from "./MessageBubble";

function ChatBox() {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    async function sendMessage() {
        if (!message.trim()) return;

        const currentMessage = message;

        setMessages((prev) => [
            ...prev,
            {
                role: "user",
                content: currentMessage,
            },
        ]);

        setMessage("");
        setLoading(true);

        try {
            const res = await api.post("/webhook/support-rag", {
                message: currentMessage,
            });

            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    content: res.data.answer || "No answer received.",
                    sources: res.data.sources || [],
                },
            ]);
        } catch (error) {
            console.error(error);

            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    content: "Error: Request failed.",
                    sources: [],
                },
            ]);
        }

        setLoading(false);
    }

    return (
        <section className="chat-section">
            <h1>Enterprise Assistant - AFMB</h1>

            <div className="messages-container">
                {messages.map((msg, index) => (
                    <MessageBubble key={index} message={msg} />
                ))}

                {loading && (
                    <div className="assistant-row message-row">
                        <div className="message-bubble assistant-bubble">
                            Thinking
                        </div>
                    </div>
                )}
            </div>

            <div className="input-area">
                <textarea
                    value={message}
                    placeholder="Ask something about the uploaded documents"
                    onChange={(e) => setMessage(e.target.value)}
                />

                <button onClick={sendMessage} disabled={loading}>
                    {loading ? "Thinking..." : "Ask"}
                </button>
            </div>
        </section>
    );
}

export default ChatBox;