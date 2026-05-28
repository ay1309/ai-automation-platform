import SourceList from "./SourceList";

function MessageBubble({ message }) {
    const isUser = message.role === "user";

    return (
        <div
            className={`message-row ${isUser ? "user-row" : "assistant-row"}`}
        >
            <div
                className={`message-bubble ${isUser ? "user-bubble" : "assistant-bubble"}`}
            >
                <p>{message.content}</p>

                {!isUser && (
                    <SourceList sources={message.sources} />
                )}
            </div>
        </div>
    );
}

export default MessageBubble;