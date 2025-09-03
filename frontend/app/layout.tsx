export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ maxWidth: 900, margin: "2rem auto", padding: "0 1rem", fontFamily: "ui-sans-serif, system-ui" }}>
        <h1>Life Moments AI</h1>
        <p>FastAPI + Next.js on Render • AI summarized timeline</p>
        {children}
      </body>
    </html>
  );
}