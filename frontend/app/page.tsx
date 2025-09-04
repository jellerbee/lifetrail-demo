"use client";
import React, { useEffect, useState } from "react";
import { api } from "./lib/api";

function ImageDisplay({ s3Key }: { s3Key: string }) {
  const [imageUrl, setImageUrl] = useState<string>("");
  
  useEffect(() => {
    api.getImageUrl(s3Key).then(setImageUrl);
  }, [s3Key]);

  if (!imageUrl) return null;

  return (
    <div style={{ marginBottom: 8 }}>
      <img
        src={imageUrl}
        alt="Life moment"
        style={{ maxWidth: 300, maxHeight: 200, objectFit: "cover", borderRadius: 4 }}
        onError={(e) => {
          e.currentTarget.style.display = "none";
        }}
      />
    </div>
  );
}

type Event = { 
  id: number; 
  kind: string; 
  source?: string; 
  summary: string; 
  labels?: string;
  processing_status: string;
  ai_results?: any;
};

export default function Page() {
  const [text, setText] = useState("");
  const [caption, setCaption] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"text" | "image">("text");

  async function refresh() {
    try { setEvents(await api.events()); } catch (e) { console.error(e); }
  }
  useEffect(() => { refresh(); }, []);

  async function onSubmitText(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await api.process(text);
      setText("");
      await refresh();
    } finally { setLoading(false); }
  }

  async function onSubmitImage(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedFile) return;
    
    setLoading(true);
    try {
      await api.upload(selectedFile, caption);
      setCaption("");
      setSelectedFile(null);
      await refresh();
    } finally { setLoading(false); }
  }

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 16 }}>
      <h1>Life Moments AI</h1>
      
      {/* Tab Navigation */}
      <div style={{ marginBottom: 16 }}>
        <button
          onClick={() => setActiveTab("text")}
          style={{
            padding: "8px 16px",
            marginRight: 8,
            backgroundColor: activeTab === "text" ? "#007bff" : "#f8f9fa",
            color: activeTab === "text" ? "white" : "black",
            border: "1px solid #ccc",
            borderRadius: 4,
            cursor: "pointer"
          }}
        >
          Add Text
        </button>
        <button
          onClick={() => setActiveTab("image")}
          style={{
            padding: "8px 16px",
            backgroundColor: activeTab === "image" ? "#007bff" : "#f8f9fa",
            color: activeTab === "image" ? "white" : "black",
            border: "1px solid #ccc",
            borderRadius: 4,
            cursor: "pointer"
          }}
        >
          Upload Image
        </button>
      </div>

      {/* Text Form */}
      {activeTab === "text" && (
        <form onSubmit={onSubmitText} style={{ marginBottom: 24 }}>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste a sentence about a life moment..."
              style={{ flex: 1, padding: 8, border: "1px solid #ccc", borderRadius: 4 }}
            />
            <button 
              disabled={loading || !text} 
              type="submit"
              style={{ padding: "8px 16px", backgroundColor: "#007bff", color: "white", border: "none", borderRadius: 4 }}
            >
              Add
            </button>
          </div>
        </form>
      )}

      {/* Image Form */}
      {activeTab === "image" && (
        <form onSubmit={onSubmitImage} style={{ marginBottom: 24 }}>
          <div style={{ marginBottom: 8 }}>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              style={{ marginBottom: 8 }}
            />
          </div>
          {selectedFile && (
            <div style={{ marginBottom: 8 }}>
              <img
                src={URL.createObjectURL(selectedFile)}
                alt="Preview"
                style={{ maxWidth: 200, maxHeight: 200, objectFit: "cover", borderRadius: 4 }}
              />
            </div>
          )}
          <div style={{ display: "flex", gap: 8 }}>
            <input
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="Add a caption for this image..."
              style={{ flex: 1, padding: 8, border: "1px solid #ccc", borderRadius: 4 }}
            />
            <button 
              disabled={loading || !selectedFile || !caption} 
              type="submit"
              style={{ padding: "8px 16px", backgroundColor: "#007bff", color: "white", border: "none", borderRadius: 4 }}
            >
              Upload
            </button>
          </div>
        </form>
      )}

      {/* Refresh Button */}
      <div style={{ marginBottom: 16 }}>
        <button 
          onClick={refresh}
          style={{ padding: "6px 12px", backgroundColor: "#28a745", color: "white", border: "none", borderRadius: 4 }}
        >
          Refresh Timeline
        </button>
      </div>

      <h2>Recent Moments</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {events.map(ev => (
          <li key={ev.id} style={{ padding: 16, border: "1px solid #eee", borderRadius: 8, marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <div style={{ fontSize: 12, opacity: 0.7 }}>
                {ev.kind} • {ev.labels || "No labels"}
              </div>
              {ev.processing_status === "pending" && (
                <div style={{ fontSize: 12, color: "#ffc107", fontWeight: "bold" }}>Processing...</div>
              )}
              {ev.processing_status === "failed" && (
                <div style={{ fontSize: 12, color: "#dc3545", fontWeight: "bold" }}>Failed</div>
              )}
            </div>
            
            <div style={{ fontWeight: 600, marginBottom: 8 }}>{ev.summary}</div>
            
            {ev.kind === "image" && ev.source && (
              <ImageDisplay s3Key={ev.source} />
            )}
            
            {ev.kind === "text" && (
              <div style={{ fontSize: 12, marginTop: 4, whiteSpace: "pre-wrap", opacity: 0.7 }}>
                {ev.source}
              </div>
            )}

            {ev.ai_results && (
              <details style={{ marginTop: 8, fontSize: 12 }}>
                <summary style={{ cursor: "pointer", fontWeight: "bold" }}>AI Analysis</summary>
                <div style={{ marginTop: 8, padding: 8, backgroundColor: "#f8f9fa", borderRadius: 4 }}>
                  {ev.ai_results.event_type && (
                    <div><strong>Event Type:</strong> {ev.ai_results.event_type}</div>
                  )}
                  {ev.ai_results.faces && ev.ai_results.faces.length > 0 && (
                    <div><strong>Faces Detected:</strong> {ev.ai_results.faces.length}</div>
                  )}
                  {ev.ai_results.ocr_text && (
                    <div><strong>Text in Image:</strong> {ev.ai_results.ocr_text}</div>
                  )}
                  {ev.ai_results.location && (
                    <div><strong>Location:</strong> {ev.ai_results.location.city}, {ev.ai_results.location.country}</div>
                  )}
                </div>
              </details>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}