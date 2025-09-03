"use client";
import { useEffect, useState } from "react";
import { api } from "./lib/api";

type Event = { id: number; kind: string; source?: string; summary: string; labels?: string };

export default function Page() {
  const [text, setText] = useState("");
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);

  async function refresh() {
    try { setEvents(await api.events()); } catch (e) { console.error(e); }
  }
  useEffect(() => { refresh(); }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await api.process(text);
      setText("");
      await refresh();
    } finally { setLoading(false); }
  }

  return (
    <div>
      <form onSubmit={onSubmit} style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste a sentence about a life moment..."
          style={{ flex: 1, padding: 8 }}
        />
        <button disabled={loading || !text} type="submit">Add</button>
      </form>
      <h2 style={{ marginTop: 24 }}>Recent Moments</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {events.map(ev => (
          <li key={ev.id} style={{ padding: 12, border: "1px solid #eee", borderRadius: 8, marginTop: 8 }}>
            <div style={{ fontSize: 12, opacity: 0.7 }}>{ev.labels}</div>
            <div style={{ fontWeight: 600 }}>{ev.summary}</div>
            <div style={{ fontSize: 12, marginTop: 4, whiteSpace: "pre-wrap" }}>{ev.source}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}