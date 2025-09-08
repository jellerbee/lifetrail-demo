const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

// Debug logging for production
if (typeof window !== 'undefined') {
  console.log('Frontend API Base URL:', BASE_URL);
  console.log('NEXT_PUBLIC_BACKEND_URL env var:', process.env.NEXT_PUBLIC_BACKEND_URL);
}

let s3Config: { bucket_name: string; region: string } | null = null;
let imageUrlCache: { [key: string]: string } = {};

export const api = {
  base: BASE_URL,
  async upload(file: File, caption: string) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("caption", caption);
    
    const res = await fetch(`${this.base}/api/upload`, {
      method: "POST",
      body: formData
    });
    if (!res.ok) throw new Error("Upload failed");
    return res.json();
  },
  async events() {
    const res = await fetch(`${this.base}/api/events`, { cache: "no-store" });
    if (!res.ok) throw new Error("Request failed");
    return res.json();
  },
  async getS3Config() {
    if (!s3Config) {
      const res = await fetch(`${this.base}/api/s3-config`);
      if (res.ok) {
        s3Config = await res.json();
      }
    }
    return s3Config;
  },
  async getImageUrl(s3Key: string) {
    // Use backend proxy for images
    return `${this.base}/api/image/${s3Key}`;
  },
  async truncateEvents() {
    // TODO: Implement backend endpoint to truncate all events from database
    const res = await fetch(`${this.base}/api/truncate-events`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Truncate failed");
    return res.json();
  }
};