const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

// Debug logging for production
if (typeof window !== 'undefined') {
  console.log('Frontend API Base URL:', BASE_URL);
  console.log('NEXT_PUBLIC_BACKEND_URL env var:', process.env.NEXT_PUBLIC_BACKEND_URL);
}

let s3Config: { bucket_name: string; region: string } | null = null;

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
    const config = await this.getS3Config();
    if (config && config.bucket_name && config.region) {
      return `https://${config.bucket_name}.s3.${config.region}.amazonaws.com/${s3Key}`;
    }
    // Fallback
    return `https://your-bucket.s3.amazonaws.com/${s3Key}`;
  }
};