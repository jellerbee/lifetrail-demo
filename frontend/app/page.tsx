"use client";
import React, { useEffect, useState } from "react";
import { api } from "./lib/api";

function ImageDisplay({ s3Key, thumbnail = false }: { s3Key: string, thumbnail?: boolean }) {
  const [imageUrl, setImageUrl] = useState<string>("");
  
  useEffect(() => {
    api.getImageUrl(s3Key).then(setImageUrl);
  }, [s3Key]);

  if (!imageUrl) {
    return thumbnail ? (
      <div style={{ 
        width: "100%", 
        height: "100%", 
        backgroundColor: "#f5f5f5", 
        borderRadius: 4,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "#999"
      }}>
        📷
      </div>
    ) : null;
  }

  const style = thumbnail ? {
    width: 80,
    height: 80,
    objectFit: "cover" as const,
    borderRadius: 4,
    display: "block"
  } : {
    maxWidth: 300,
    maxHeight: 200,
    objectFit: "cover" as const,
    borderRadius: 4,
    display: "block"
  };

  return (
    <div style={thumbnail ? {} : { marginBottom: 8 }}>
      <img
        src={imageUrl}
        alt="Life moment"
        style={style}
        onLoad={(e) => {
          console.log(`Image loaded: ${imageUrl}, natural size: ${e.currentTarget.naturalWidth}x${e.currentTarget.naturalHeight}, display size: ${e.currentTarget.width}x${e.currentTarget.height}`);
        }}
        onError={(e) => {
          console.log(`Image failed: ${imageUrl}`);
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
  heic_metadata?: any;
  original_filename?: string;
  photo_taken_at?: string;
  created_at: string;
};

function QuestionMark({ questions }: { questions: string[] }) {
  const [showQuestions, setShowQuestions] = useState(false);

  if (!questions || questions.length === 0) {
    return null;
  }

  return (
    <>
      <button
        onClick={() => setShowQuestions(!showQuestions)}
        style={{
          width: 24,
          height: 24,
          borderRadius: "50%",
          backgroundColor: "#007bff",
          color: "white",
          border: "none",
          fontSize: 12,
          cursor: "pointer",
          marginLeft: 8,
          animation: "pulse 2s infinite",
          flexShrink: 0
        }}
        title="AI wants to know more about this moment"
      >
        ?
      </button>
      
      {showQuestions && (
        <div style={{
          position: "absolute",
          top: "100%",
          left: 0,
          right: 0,
          backgroundColor: "#f8f9fa",
          border: "1px solid #dee2e6",
          borderRadius: 6,
          padding: 12,
          marginTop: 4,
          zIndex: 10,
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
        }}>
          <div style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>
            Help me understand this moment better:
          </div>
          {questions.map((question, index) => (
            <div key={index} style={{
              fontSize: 13,
              color: "#495057",
              marginBottom: index < questions.length - 1 ? 4 : 0,
              cursor: "pointer",
              padding: "2px 4px",
              borderRadius: 3,
              backgroundColor: "white",
              border: "1px solid #e9ecef"
            }}>
              {question}
            </div>
          ))}
        </div>
      )}
    </>
  );
}

export default function Page() {
  const [text, setText] = useState("");
  const [caption, setCaption] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"text" | "image">("text");

  async function refresh() {
    try { 
      setEvents(await api.events());
    } catch (e) { 
      console.error('API Error:', e); 
    }
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

  function isHeicFile(filename: string): boolean {
    return /\.(heic|heif)$/i.test(filename);
  }

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 16 }}>
      <style jsx>{`
        @keyframes pulse {
          0% {
            box-shadow: 0 0 0 0 rgba(0, 123, 255, 0.7);
          }
          70% {
            box-shadow: 0 0 0 10px rgba(0, 123, 255, 0);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(0, 123, 255, 0);
          }
        }
      `}</style>
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
              accept="image/*,.heic,.heif"
              onChange={handleFileSelect}
              style={{ marginBottom: 8 }}
            />
            <div style={{ fontSize: 12, color: "#666", marginTop: 4 }}>
              Supports JPEG, PNG, HEIC/HEIF, and other image formats
            </div>
          </div>
          {selectedFile && (
            <div style={{ marginBottom: 8 }}>
              {isHeicFile(selectedFile.name) ? (
                <div style={{
                  width: 200,
                  height: 150,
                  backgroundColor: "#f5f5f5",
                  border: "2px dashed #ccc",
                  borderRadius: 4,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexDirection: "column",
                  color: "#666",
                  fontSize: 14
                }}>
                  <div style={{ fontSize: 24, marginBottom: 8 }}>📷</div>
                  <div>{selectedFile.name}</div>
                  <div style={{ fontSize: 12, marginTop: 4 }}>HEIC/HEIF Preview</div>
                </div>
              ) : (
                <img
                  src={URL.createObjectURL(selectedFile)}
                  alt="Preview"
                  style={{ maxWidth: 200, maxHeight: 200, objectFit: "cover", borderRadius: 4 }}
                />
              )}
            </div>
          )}
          <div style={{ display: "flex", gap: 8 }}>
            <input
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="Add a caption for this image... (optional - leave blank to see AI questions)"
              style={{ flex: 1, padding: 8, border: "1px solid #ccc", borderRadius: 4 }}
            />
            <button 
              disabled={loading || !selectedFile} 
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

      <h2>Life Timeline</h2>
      <div style={{ maxWidth: 600, margin: "0 auto" }}>
        {events.filter(ev => ev.kind === "image").map((ev, index, filteredEvents) => {
          // Simple grouping logic for demo: group photos with generic summaries
          const isGeneric = ev.summary.includes("A moment from today") || 
                           ev.summary.includes("Life happening") || 
                           ev.summary.includes("Just a regular day") ||
                           ev.summary.includes("Another memory captured");
          
          const nextEvent = filteredEvents[index + 1];
          const nextIsGeneric = nextEvent && (
            nextEvent.summary.includes("A moment from today") || 
            nextEvent.summary.includes("Life happening") || 
            nextEvent.summary.includes("Just a regular day") ||
            nextEvent.summary.includes("Another memory captured")
          );
          
          // Demo grouping stub: show expandable indicator for generic photos
          const shouldShowGroup = isGeneric && !nextIsGeneric;
          // Use photo_taken_at if available, otherwise fall back to created_at
          let eventDate = new Date();
          if (ev.photo_taken_at) {
            eventDate = new Date(ev.photo_taken_at);
          } else if (ev.created_at) {
            eventDate = new Date(ev.created_at);
          }
          
          const formatDate = (date: Date) => {
            const now = new Date();
            const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
            
            if (diffDays === 0) return "Today";
            if (diffDays === 1) return "Yesterday";
            if (diffDays < 7) return `${diffDays} days ago`;
            if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
            if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
            return date.toLocaleDateString('en-US', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            });
          };

          return (
            <div key={ev.id}>
              <div style={{ 
                display: "flex", 
                marginBottom: shouldShowGroup ? 8 : 24, 
                padding: 16,
                backgroundColor: "white",
                borderRadius: 8,
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                position: "relative"
              }}>
                {/* Thumbnail */}
                <div style={{ 
                  width: 80, 
                  height: 80, 
                  marginRight: 16, 
                  flexShrink: 0,
                  minWidth: 80,
                  minHeight: 80,
                  backgroundColor: "#f5f5f5",
                  borderRadius: 4,
                  overflow: "hidden"
                }}>
                  {ev.source && (
                    <ImageDisplay s3Key={ev.source} thumbnail={true} />
                  )}
                </div>
                
                {/* Content */}
                <div style={{ flex: 1 }}>
                  {/* Date */}
                  <div style={{ 
                    fontSize: 12, 
                    color: "#666", 
                    marginBottom: 4,
                    fontWeight: 500 
                  }}>
                    {formatDate(eventDate)}
                  </div>
                  
                  {/* AI Summary - First Person with Question Mark */}
                  <div style={{ 
                    display: "flex",
                    alignItems: "flex-start",
                    fontSize: 14, 
                    lineHeight: 1.4,
                    color: "#333"
                  }}>
                    <div style={{ flex: 1 }}>
                      {ev.processing_status === "pending" ? (
                        <span style={{ color: "#999", fontStyle: "italic" }}>
                          Processing memory...
                        </span>
                      ) : ev.processing_status === "failed" ? (
                        <span style={{ color: "#999", fontStyle: "italic" }}>
                          Couldn't quite make out what happened here...
                        </span>
                      ) : (
                        ev.summary || "A moment in time..."
                      )}
                    </div>
                    {ev.processing_status === "completed" && ev.ai_results?.clarification_questions && (
                      <QuestionMark questions={ev.ai_results.clarification_questions} />
                    )}
                  </div>
                </div>
              </div>
              
              {/* Demo grouping stub */}
              {shouldShowGroup && (
                <div style={{ 
                  marginBottom: 24,
                  padding: 12,
                  backgroundColor: "#f8f9fa",
                  borderRadius: 6,
                  border: "1px dashed #dee2e6",
                  textAlign: "center" as const,
                  color: "#6c757d",
                  fontSize: 13,
                  cursor: "pointer"
                }}>
                  ⋯ 3 more similar moments from this time period ⋯
                  <div style={{ fontSize: 11, marginTop: 2 }}>
                    (Click to expand - demo only)
                  </div>
                </div>
              )}
            </div>
          );
        })}
        
        {events.filter(ev => ev.kind === "image").length === 0 && (
          <div style={{ 
            textAlign: "center", 
            padding: 40, 
            color: "#666",
            fontStyle: "italic" 
          }}>
            No photos yet. Start building your timeline by uploading some images!
          </div>
        )}
      </div>
    </div>
  );
}