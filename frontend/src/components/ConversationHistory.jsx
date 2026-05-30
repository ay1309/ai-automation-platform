import { useEffect, useState } from "react";
import axios from "axios";
import { API_URL } from "../services/apiConfig";

function ConversationHistory() {
    const [conversations, setConversations] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        async function fetchConversations() {
            setLoading(true);

            try {
                const res = await axios.get(
                    `${API_URL}/conversations`
                );

                setConversations(res.data);
            } catch (error) {
                console.error("Error loading conversations:", error);
            }

            setLoading(false);
        }

        fetchConversations();
    }, []);

    return (
        <div className="history-box">
            <h3>History</h3>

            {loading && (
                <p className="muted-text">Loading history.</p>
            )}

            {!loading && conversations.length === 0 && (
                <p className="muted-text">No available conversations yet.</p>
            )}

            {conversations.map((conv) => (
                <div key={conv.id} className="history-item">
                    <p>
                        <strong>Q:</strong> {conv.user_message}
                    </p>

                    <p>
                        <strong>A:</strong> {conv.ai_response}
                    </p>
                </div>
            ))}
        </div>
    );
}

export default ConversationHistory;