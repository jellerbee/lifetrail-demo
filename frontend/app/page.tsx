"use client";
import React, { useEffect, useState, useRef } from "react";
import { api } from "./lib/api";
import heic2any from "heic2any";

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
  user_caption?: string;
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

function PreviewImage({ file }: { file: File }) {
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isHeicFile = file.type === 'image/heic' || file.type === 'image/heif' || 
                    file.name.toLowerCase().endsWith('.heic') || 
                    file.name.toLowerCase().endsWith('.heif');

  useEffect(() => {
    let cancelled = false;

    async function processFile() {
      setIsLoading(true);
      setError(null);
      
      try {
        if (isHeicFile) {
          console.log('Converting HEIC to JPEG for preview...');
          
          // Convert HEIC to JPEG blob for preview
          const convertedBlob = await heic2any({
            blob: file,
            toType: "image/jpeg",
            quality: 0.8
          }) as Blob;
          
          if (cancelled) return;
          
          const url = URL.createObjectURL(convertedBlob);
          setPreviewUrl(url);
          console.log('HEIC converted successfully for preview');
        } else {
          // For regular images, use the file directly
          const url = URL.createObjectURL(file);
          setPreviewUrl(url);
        }
        
        setIsLoading(false);
      } catch (err) {
        console.error('Failed to process image for preview:', err);
        if (!cancelled) {
          setError(`Failed to process ${isHeicFile ? 'HEIC' : 'image'} file`);
          setIsLoading(false);
        }
      }
    }

    processFile();

    return () => {
      cancelled = true;
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [file, isHeicFile]);

  if (isLoading) {
    return (
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
        <div style={{ fontSize: 24, marginBottom: 8 }}>⏳</div>
        <div>{file.name}</div>
        <div style={{ fontSize: 12, marginTop: 4 }}>
          {isHeicFile ? 'Converting HEIC...' : 'Loading...'}
        </div>
      </div>
    );
  }

  if (error) {
    return (
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
        <div style={{ fontSize: 24, marginBottom: 8 }}>⚠️</div>
        <div>{file.name}</div>
        <div style={{ fontSize: 12, marginTop: 4, color: "#dc3545" }}>{error}</div>
      </div>
    );
  }

  return (
    <img
      src={previewUrl}
      alt="Preview"
      style={{ maxWidth: 200, maxHeight: 200, objectFit: "cover", borderRadius: 4 }}
      onError={() => {
        console.log('Converted preview failed to load');
        setError('Preview failed to load');
      }}
    />
  );
}

export default function Page() {
  const [caption, setCaption] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingDateFor, setEditingDateFor] = useState<number | null>(null);
  
  // Auto-refresh state management
  const autoRefreshInterval = useRef<NodeJS.Timeout | null>(null);
  const autoRefreshTimeout = useRef<NodeJS.Timeout | null>(null);
  
  // Check if debug mode is enabled
  const isDebugMode = process.env.NEXT_PUBLIC_DEBUG === 'true';

  async function refresh() {
    try { 
      setEvents(await api.events());
    } catch (e) { 
      console.error('API Error:', e); 
    }
  }
  useEffect(() => { refresh(); }, []);

  // Cleanup intervals on component unmount
  useEffect(() => {
    return () => {
      stopAutoRefresh();
    };
  }, []);


  async function onSubmitImage(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedFile) return;
    
    setLoading(true);
    try {
      await api.upload(selectedFile, caption);
      setCaption("");
      setSelectedFile(null);
      
      // Reset file input element
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fileInput.value = '';
      }
      
      await refresh();
      
      // Start auto-refresh after successful upload
      startAutoRefresh();
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

  async function updateEventDate(eventId: number, newDate: string) {
    // TODO: Implement backend API call to update event's photo_taken_at field
    // Example API call:
    // await api.updateEvent(eventId, { photo_taken_at: newDate });
    
    // For now, just update the UI optimistically
    setEvents(prevEvents => 
      prevEvents.map(event => 
        event.id === eventId 
          ? { ...event, photo_taken_at: newDate }
          : event
      )
    );
    setEditingDateFor(null);
  }

  async function handleTruncateEvents() {
    if (confirm('Are you sure you want to delete ALL events? This cannot be undone.')) {
      try {
        await api.truncateEvents();
        window.location.reload(); // Refresh the entire page
      } catch (error) {
        console.error('Failed to truncate events:', error);
        alert('Failed to truncate events. Check console for details.');
      }
    }
  }

  function startAutoRefresh() {
    // Clear any existing intervals
    stopAutoRefresh();
    
    // Start refreshing every 3 seconds
    autoRefreshInterval.current = setInterval(() => {
      refresh();
    }, 3000);
    
    // Stop auto-refresh after 2 minutes (120 seconds)
    autoRefreshTimeout.current = setTimeout(() => {
      stopAutoRefresh();
    }, 120000);
    
    console.log('Auto-refresh started: 3s interval, stops after 2 minutes');
  }

  function stopAutoRefresh() {
    if (autoRefreshInterval.current) {
      clearInterval(autoRefreshInterval.current);
      autoRefreshInterval.current = null;
    }
    if (autoRefreshTimeout.current) {
      clearTimeout(autoRefreshTimeout.current);
      autoRefreshTimeout.current = null;
    }
    console.log('Auto-refresh stopped');
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
      {/* Image Form */}
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
              <PreviewImage file={selectedFile} />
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

      {/* Refresh Button */}
      <div style={{ marginBottom: 16, display: "flex", gap: 8 }}>
        <button 
          onClick={refresh}
          style={{ padding: "6px 12px", backgroundColor: "#28a745", color: "white", border: "none", borderRadius: 4 }}
        >
          Refresh Timeline
        </button>
        
        {/* Debug-only Truncate Button */}
        {isDebugMode && (
          <button 
            onClick={handleTruncateEvents}
            style={{ 
              padding: "6px 12px", 
              backgroundColor: "#dc3545", 
              color: "white", 
              border: "none", 
              borderRadius: 4,
              fontWeight: "bold"
            }}
          >
            🗑️ Clear All Events
          </button>
        )}
      </div>

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
          let eventDate;
          if (ev.photo_taken_at) {
            eventDate = new Date(ev.photo_taken_at);
          } else if (ev.created_at) {
            eventDate = new Date(ev.created_at);
          } else {
            eventDate = new Date(); // Fallback to current time if no dates available
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
                    fontWeight: 500,
                    position: "relative"
                  }}>
                    {editingDateFor === ev.id ? (
                      <input
                        type="date"
                        defaultValue={eventDate.toISOString().split('T')[0]}
                        onBlur={(e) => {
                          if (e.target.value) {
                            updateEventDate(ev.id, e.target.value + 'T12:00:00Z');
                          } else {
                            setEditingDateFor(null);
                          }
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            if (e.currentTarget.value) {
                              updateEventDate(ev.id, e.currentTarget.value + 'T12:00:00Z');
                            } else {
                              setEditingDateFor(null);
                            }
                          } else if (e.key === 'Escape') {
                            setEditingDateFor(null);
                          }
                        }}
                        autoFocus
                        style={{
                          fontSize: 12,
                          border: "1px solid #007bff",
                          borderRadius: 3,
                          padding: "2px 4px",
                          outline: "none"
                        }}
                      />
                    ) : (
                      <span
                        onClick={() => setEditingDateFor(ev.id)}
                        title="Click to change date"
                        style={{
                          cursor: "pointer",
                          padding: "2px 4px",
                          borderRadius: 3,
                          transition: "background-color 0.2s ease"
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = "#f0f8ff";
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = "transparent";
                        }}
                      >
                        {formatDate(eventDate)}
                      </span>
                    )}
                  </div>
                  
                  {/* User Caption */}
                  {ev.user_caption && (
                    <div style={{
                      fontSize: 14,
                      lineHeight: 1.4,
                      color: "#333",
                      marginBottom: 6
                    }}>
                      {ev.user_caption}
                    </div>
                  )}
                  
                  {/* AI-Generated Summary with Icon */}
                  <div style={{ 
                    display: "flex",
                    alignItems: "flex-start",
                    fontSize: 13, 
                    lineHeight: 1.4,
                    color: "#666"
                  }}>
                    <div style={{ 
                      display: "flex", 
                      alignItems: "flex-start", 
                      flex: 1 
                    }}>
                      <span style={{ 
                        fontSize: 11,
                        marginRight: 6,
                        marginTop: 1,
                        opacity: 0.7
                      }}>
                        ✦✦✦
                      </span>
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
                    </div>
                    {ev.processing_status === "completed" && ev.ai_results?.clarification_questions && (
                      <QuestionMark questions={ev.ai_results.clarification_questions} />
                    )}
                  </div>
                  
                  {/* Debug Information */}
                  {isDebugMode && (
                    <div style={{ 
                      marginTop: 12,
                      padding: 8,
                      backgroundColor: "#f8f9fa",
                      borderRadius: 4,
                      border: "1px solid #e9ecef",
                      fontSize: 11,
                      fontFamily: "monospace"
                    }}>
                      <div style={{ fontWeight: "bold", marginBottom: 6, color: "#495057" }}>
                        🐛 DEBUG INFO:
                      </div>
                      
                      {ev.labels && (
                        <div style={{ marginBottom: 4 }}>
                          <strong>Labels:</strong> {ev.labels}
                        </div>
                      )}
                      
                      {ev.original_filename && (
                        <div style={{ marginBottom: 4 }}>
                          <strong>File:</strong> {ev.original_filename}
                        </div>
                      )}
                      
                      {ev.ai_results && (
                        <div style={{ marginBottom: 4 }}>
                          <strong>AI Results:</strong>
                          <pre style={{ 
                            margin: "4px 0 0 0",
                            whiteSpace: "pre-wrap",
                            fontSize: 10,
                            maxHeight: 200,
                            overflow: "auto",
                            backgroundColor: "white",
                            padding: 4,
                            borderRadius: 3
                          }}>
                            {JSON.stringify(ev.ai_results, null, 2)}
                          </pre>
                        </div>
                      )}
                      
                      {ev.heic_metadata && (
                        <div style={{ marginBottom: 4 }}>
                          <strong>HEIC Metadata:</strong>
                          <pre style={{ 
                            margin: "4px 0 0 0",
                            whiteSpace: "pre-wrap",
                            fontSize: 10,
                            maxHeight: 100,
                            overflow: "auto",
                            backgroundColor: "white",
                            padding: 4,
                            borderRadius: 3
                          }}>
                            {JSON.stringify(ev.heic_metadata, null, 2)}
                          </pre>
                        </div>
                      )}
                      
                      <div style={{ marginBottom: 4 }}>
                        <strong>Status:</strong> {ev.processing_status}
                      </div>
                      
                      <div style={{ fontSize: 10, color: "#6c757d" }}>
                        ID: {ev.id} | Kind: {ev.kind} | Source: {ev.source || 'N/A'}
                      </div>
                    </div>
                  )}
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