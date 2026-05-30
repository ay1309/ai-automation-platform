import { useState } from "react";
import axios from "axios";
import { API_URL } from "../services/apiConfig";

function UploadBox() {
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState("");
    const [loading, setLoading] = useState(false);

    async function uploadFile() {
        if (!file) {
            setStatus("Please select a PDF first.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        setLoading(true);
        setStatus("Uploading PDF");

        try {
            await axios.post(`${API_URL}/upload`, formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });

            setStatus("PDF uploaded. Now ingesting...");

            const ingestRes = await axios.post(`${API_URL}/ingest`);   

            setStatus(ingestRes.data.message || "PDF uploaded and ingested.");
        } catch (error) {
            console.error(error);
            setStatus("Upload or ingestion failed.");
        }

        setLoading(false);
    }

    return (
        <div className="upload-box">
            <h3>Upload PDF</h3>

            <input
                type="file"
                accept="application/pdf"
                onChange={(e) => setFile(e.target.files[0])}
            />

            <button onClick={uploadFile} disabled={loading}>
                {loading ? "Processing document" : "Upload & Ingest"}
            </button>

            {status && <p className="status-text">{status}</p>}
        </div>
    );
}

export default UploadBox;