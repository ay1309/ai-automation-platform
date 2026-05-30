import { useEffect, useState } from "react";
import axios from "axios";
import { API_URL } from "../services/apiConfig";

function DocumentList() {
    const [documents, setDocuments] = useState([]);
    const [status, setStatus] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        async function fetchDocuments() {
            try {
                const res = await axios.get(`${API_URL}/documents`);
                setDocuments(res.data);
            } catch (error) {
                console.error(error);
                setStatus("Could not load documents.");
            }
        }

        fetchDocuments();
    }, []);

    async function refreshDocuments() {
        try {
            setLoading(true);
            setStatus("Refreshing documents...");

            const res = await axios.get(`${API_URL}/documents`);
            setDocuments(res.data);

            setStatus("Documents refreshed.");
        } catch (error) {
            console.error(error);
            setStatus("Could not refresh documents.");
        } finally {
            setLoading(false);
        }
    }

    async function deleteDocument(filename) {
        try {
            setLoading(true);
            setStatus("Deleting document...");

            await axios.delete(
                `${API_URL}/documents/${encodeURIComponent(filename)}`
            );

            const res = await axios.get(`${API_URL}/documents`);
            setDocuments(res.data);

            setStatus("Document deleted. Please reindex the knowledge base.");
        } catch (error) {
            console.error(error);
            setStatus("Could not delete document.");
        } finally {
            setLoading(false);
        }
    }

    async function reindexDocuments() {
        try {
            setLoading(true);
            setStatus("Reindexing knowledge base...");

            await axios.post(`${API_URL}/reindex`);

            setStatus("Knowledge base reindexed.");
        } catch (error) {
            console.error(error);
            setStatus("Could not reindex knowledge base.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="documents-box">
            <h3>Documents</h3>

            {documents.length === 0 && (
                <p className="muted-text">No documents uploaded.</p>
            )}

            {documents.map((doc) => (
                <div key={doc.name} className="document-item">
                    <div>
                        <strong>{doc.name}</strong>
                        <p>{doc.size_kb} KB</p>
                    </div>

                    <button
                        className="danger-button"
                        onClick={() => deleteDocument(doc.name)}
                        disabled={loading}
                    >
                        Delete
                    </button>
                </div>
            ))}

            <div className="documents-actions">
                <button onClick={refreshDocuments} disabled={loading}>
                    Refresh Documents
                </button>

                <button onClick={reindexDocuments} disabled={loading}>
                    {loading ? "Processing..." : "Reindex Knowledge Base"}
                </button>
            </div>

            {status && (
                <p className="status-text">{status}</p>
            )}
        </div>
    );
}

export default DocumentList;