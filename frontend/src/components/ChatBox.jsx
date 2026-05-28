import { useState } from "react";

import api from "../services/api";

import MessageBubble from "./MessageBubble";

function ChatBox() {

    const [message, setMessage] = useState("");

    const [messages, setMessages] = useState([]);

    const [loading, setLoading] = useState(false);


    async function sendMessage() {

        if (!message.trim()) return;

        const userMessage = {
            role: "user",
            content: message
        };

        setMessages((prev) => [
            ...prev,
            userMessage
        ]);

        setLoading(true);

        try {

            const res = await api.post(
                "/webhook/support-rag",
                {
                    message: message
                }
            );

            const aiMessage = {
                role: "assistant",
                content: res.data.answer,
                sources: res.data.sources || []
            };

            setMessages((prev) => [
                ...prev,
                aiMessage
            ]);

        } catch (error) {

            console.error(error);

            const errorMessage = {
                role: "assistant",
                content: "Request failed"
            };

            setMessages((prev) => [
                ...prev,
                errorMessage
            ]);
        }

        setMessage("");

        setLoading(false);
    }


    return (

        <div style={{
            padding: "40px",
            fontFamily: "Arial"
        }}>

            <h1>
                Enterprise Assistant - AFMB
            </h1>

            {/* CHAT HISTORY */}

            <div className="messages-container">

                {messages.map((msg, index) => (

                    <MessageBubble
                        key={index}
                        message={msg}
                    />

                ))}

            </div>

            <br />

            {/* INPUT */}

            <textarea
                rows="5"
                cols="50"
                value={message}
                onChange={(e) =>
                    setMessage(e.target.value)
                }
            />

            <br /><br />

            <button onClick={sendMessage}>
                Ask
            </button>

            <br /><br />

            {loading && <p>Loading</p>}

        </div>
    );
}

export default ChatBox; 
