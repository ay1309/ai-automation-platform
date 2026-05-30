import ChatBox from "./components/ChatBox";
import UploadBox from "./components/UploadBox";
import ConversationHistory from "./components/ConversationHistory";
import "./styles/app.css";
import DocumentList from "./components/DocumentList";

function App() {
    return (
        <div className="app">
            <aside className="sidebar">
                <h2>Talent Acquisition Platform</h2>
                <p className="sidebar-text">
                    Upload resumes and job descriptions to build a searchable AI recruiting knowledge base.
                </p>

                <UploadBox />
                <DocumentList />
                <ConversationHistory />
            </aside>
        

            <main className="main-content">
                <ChatBox />
            </main>
        </div>
    );
}

export default App;