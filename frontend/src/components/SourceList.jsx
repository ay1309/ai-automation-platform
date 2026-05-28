function SourceList({ sources }) {
    if (!sources || sources.length === 0) {
        return null;
    }

    return (
        <div className="sources-box">
            <h4>Sources</h4>

            {sources.map((source, index) => (
                <div key={index} className="source-item">
                    <strong>{source.source || "Unknown file"}</strong>
                    <span>Page: {source.page ?? "N/A"}</span>
                    <span>Chunk: {source.chunk ?? "N/A"}</span>
                    <span>
                        Distance: {
                            source.distance
                                ? source.distance.toFixed(4)
                                : "N/A"
                        }
                    </span>
                </div>
            ))}
        </div>
    );
}

export default SourceList;