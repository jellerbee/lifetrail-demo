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
  getImageUrl(s3Key: string) {
    // Assuming AWS S3 bucket URL format
    const bucketName = "your-bucket-name"; // This should come from env or API
    return `https://${bucketName}.s3.amazonaws.com/${s3Key}`;
  }
};