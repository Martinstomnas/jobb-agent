import { useRef, useState } from "react";
import { API_URL } from "../config";

interface InputFormProps {
  onSubmit: (data: { jobPosting: string; cv: string }) => void;
  running: boolean;
}

export default function InputForm({ onSubmit, running }: InputFormProps) {
  const [jobPosting, setJobPosting] = useState("");
  const [cv, setCv] = useState("");
  const [extraInfo, setExtraInfo] = useState("");
  const [cvFile, setCvFile] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handlePdfUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_URL}/extract-pdf`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        alert(err.detail ?? "Kunne ikke lese PDF");
        return;
      }
      const { text } = await res.json();
      setCv(text);
      setCvFile(file.name);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!jobPosting.trim() || !cv.trim()) return;
    const combined = extraInfo.trim()
      ? `${cv}\n\n---\nEkstra informasjon:\n${extraInfo}`
      : cv;
    onSubmit({ jobPosting, cv: combined });
  };

  return (
    <form className="input-form" onSubmit={handleSubmit}>
      <div className="field">
        <label>Stillingsannonse</label>
        <textarea
          value={jobPosting}
          onChange={(e) => setJobPosting(e.target.value)}
          placeholder="Lim inn hele stillingsannonsen her..."
          rows={6}
          disabled={running}
        />
      </div>

      <div className="field">
        <div className="upload-row">
          <label>CV</label>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            style={{ display: "none" }}
            onChange={handlePdfUpload}
            disabled={running || uploading}
          />
          <button
            type="button"
            className="upload-btn"
            onClick={() => fileInputRef.current?.click()}
            disabled={running || uploading}
          >
            {uploading ? <span className="spinner" /> : "Last opp PDF"}
          </button>
          {cvFile && <span className="pdf-indicator">{cvFile}</span>}
        </div>
        <textarea
          value={cv}
          onChange={(e) => { setCv(e.target.value); setCvFile(null); }}
          placeholder="Lim inn CV som ren tekst, eller last opp PDF over..."
          rows={5}
          disabled={running}
        />
      </div>

      <div className="field">
        <label>Ekstra informasjon (valgfritt)</label>
        <textarea
          value={extraInfo}
          onChange={(e) => setExtraInfo(e.target.value)}
          placeholder="Tilleggsinfo som ikke er i CV-en: lenker, prosjekter, motivasjon, spesielle omstendigheter..."
          rows={3}
          disabled={running}
        />
      </div>

      <button type="submit" className="submit-btn" disabled={running}>
        {running ? (
          <>
            <span className="spinner" />
            Analyserer...
          </>
        ) : (
          "Analyser"
        )}
      </button>

      <p className="privacy-note">
        Stillingsannonse og CV sendes til Anthropics API for analyse. Innholdet
        lagres ikke av denne appen.
      </p>
    </form>
  );
}
