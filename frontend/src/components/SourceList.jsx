function SourceList({ sources }) {
    let safeSources = [];

    if (Array.isArray(sources)) {
        safeSources = sources;
    } else if (typeof sources === "string") {
        try {
            const parsed = JSON.parse(sources);
            safeSources = Array.isArray(parsed) ? parsed : [];
        } catch {
            safeSources = [];
        }
    }

    if (safeSources.length === 0) {
        return null;
    }

    return (
        <div className="sources-box">
            <h4>Sources</h4>

            {safeSources.map((source, index) => (
                <div key={index} className="source-item">
                    <strong>{source?.source || "Unknown file"}</strong>
                    <span>Page: {source?.page ?? "N/A"}</span>
                    <span>Chunk: {source?.chunk ?? "N/A"}</span>
                    <span>
                        Distance:{" "}
                        {typeof source?.distance === "number"
                            ? source.distance.toFixed(4)
                            : "N/A"}
                    </span>
                </div>
            ))}
        </div>
    );
}

export default SourceList;