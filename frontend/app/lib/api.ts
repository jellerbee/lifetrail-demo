const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export const api = {
  base: BASE_URL,
  async process(text: string) {
    const res = await fetch(`${this.base}/api/process`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (!res.ok) throw new Error("Request failed");
    return res.json();
  },
  async events() {
    const res = await fetch(`${this.base}/api/events`, { cache: "no-store" });
    if (!res.ok) throw new Error("Request failed");
    return res.json();
  }
};