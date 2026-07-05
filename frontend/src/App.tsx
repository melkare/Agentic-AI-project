import { useState } from 'react';

interface GenerationResponse {
  status: string;
  result: Record<string, unknown>;
}

export default function App() {
  const [prompt, setPrompt] = useState('A cinematic birthday celebration with warm lighting');
  const [images, setImages] = useState<string[]>([]);
  const [progress, setProgress] = useState('Idle');
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  const handleGenerate = async () => {
    setProgress('Generating...');
    const response = await fetch('http://localhost:8000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, images }),
    });
    const data: GenerationResponse = await response.json();
    setProgress(data.status || 'Completed');
    const output = (data.result?.render_result as { output_path?: string } | undefined)?.output_path;
    if (output) {
      setVideoUrl(output);
    }
  };

  return (
    <main style={{ fontFamily: 'sans-serif', padding: 24, maxWidth: 900, margin: '0 auto' }}>
      <h1>AI Video Studio</h1>
      <p>Upload images, describe the scene, and generate a storyboard-driven video.</p>
      <label htmlFor="prompt">Prompt</label>
      <textarea
        id="prompt"
        value={prompt}
        onChange={(event) => setPrompt(event.target.value)}
        rows={4}
        style={{ width: '100%', marginTop: 8, marginBottom: 16 }}
      />
      <label htmlFor="images">Image Upload</label>
      <input
        id="images"
        type="file"
        multiple
        onChange={(event) => {
          const files = Array.from(event.target.files ?? []);
          setImages(files.map((file) => file.name));
        }}
        style={{ display: 'block', marginTop: 8, marginBottom: 16 }}
      />
      <button onClick={handleGenerate}>Generate</button>
      <p>Progress: {progress}</p>
      {videoUrl ? (
        <div>
          <video controls src={videoUrl} style={{ width: '100%', marginTop: 16 }} />
          <a href={videoUrl} download>Download</a>
        </div>
      ) : null}
    </main>
  );
}
