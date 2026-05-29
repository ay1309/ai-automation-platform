import ChatBox from "./components/ChatBox";
import UploadBox from "./components/UploadBox";
import "./styles/app.css";

function App() {
    return (
        <div className="app">
            <aside className="sidebar">
                <h2>AFMB Platform</h2>
                <p className="sidebar-text">
                    Upload PDFs, ingest them, and ask questions using RAG.
                </p>

                <UploadBox />
            </aside>

            <main className="main-content">
                <ChatBox />
            </main>
        </div>
    );
}

export default App;