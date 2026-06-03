interface FitWarningProps {
  summary: string;
  sessionId: string;
}

export default function FitWarning({ summary, sessionId }: FitWarningProps) {
  const postAnswer = async (answer: string) => {
    await fetch(`http://localhost:8000/answer/${sessionId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer }),
    });
  };

  return (
    <div className="fit-warning-card">
      <div className="fit-warning-label">Svak match</div>
      <p className="fit-warning-text">{summary}</p>
      <div className="fit-warning-actions">
        <button className="fit-warning-abort" onClick={() => postAnswer("avbryt")}>
          Avbryt
        </button>
        <button className="fit-warning-continue" onClick={() => postAnswer("fortsett")}>
          Fortsett likevel
        </button>
      </div>
    </div>
  );
}
