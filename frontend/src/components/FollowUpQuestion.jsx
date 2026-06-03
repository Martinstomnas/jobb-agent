import { useState } from "react";

export default function FollowUpQuestion({ question, sessionId }) {
  const [answer, setAnswer] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const postAnswer = async (text) => {
    setSubmitting(true);
    await fetch(`http://localhost:8000/answer/${sessionId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer: text }),
    });
    // Ikke oppdater lokal state her — SSE-strømmen sender "answered" og
    // eventuelt neste "question", og App.jsx håndterer mounting/unmounting.
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    postAnswer(answer.trim());
  };

  const handleSkip = () => postAnswer("");

  return (
    <div className="followup-card">
      <div className="followup-label">Oppfølgingsspørsmål</div>
      <p className="followup-question">{question}</p>
      <form onSubmit={handleSubmit}>
        <textarea
          className="followup-textarea"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Skriv svaret ditt her..."
          rows={3}
          disabled={submitting}
          autoFocus
        />
        <div className="followup-actions">
          <button
            type="button"
            className="followup-skip"
            onClick={handleSkip}
            disabled={submitting}
          >
            Hopp over
          </button>
          <button
            type="submit"
            className="followup-submit"
            disabled={submitting || !answer.trim()}
          >
            {submitting ? "Sender..." : "Send svar"}
          </button>
        </div>
      </form>
    </div>
  );
}
