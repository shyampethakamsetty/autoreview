import React, { useState } from 'react';

const SAMPLE_JSON = `[
  {
    "id": 1,
    "location": "NYC - Manhattan",
    "rating": 5,
    "text": "Amazing service! The staff was incredibly helpful and professional.",
    "date": "2025-09-01"
  },
  {
    "id": 2,
    "location": "SF - Mission",
    "rating": 2,
    "text": "Poor service, waited 30 minutes just to be acknowledged.",
    "date": "2025-09-02"
  },
  {
    "id": 3,
    "location": "LA - Hollywood",
    "rating": 4,
    "text": "Good food quality and clean environment. Will come back!",
    "date": "2025-09-03"
  }
]`;

export default function Ingest() {
  const [text, setText] = useState(SAMPLE_JSON);
  const [fileName, setFileName] = useState<string | null>(null);
  const [enrich, setEnrich] = useState(true);
  const [apiKey, setApiKey] = useState('supersecret');
  const [status, setStatus] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const loadSample = () => {
    setText(SAMPLE_JSON);
    setFileName(null);
    setStatus(null);
  };

  const handleFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      setText(e.target?.result as string);
    };
    reader.readAsText(file);
    setFileName(file.name);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setStatus(null);

    try {
      const url = `/api/ingest${enrich ? '?enrich=true' : '?enrich=false'}`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey,
        },
        body: JSON.stringify(JSON.parse(text)),
      });

      if (response.ok) {
        setStatus('Successfully ingested reviews');
      } else {
        const error = await response.text();
        setStatus(`Error: ${error}`);
      }
    } catch (err) {
      setStatus(`Error: ${err}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ padding: 20, maxWidth: 800 }}>
      <h2>Ingest Customer Reviews</h2>
      
      <div style={{ marginBottom: 20, padding: 15, backgroundColor: '#f5f5f5', borderRadius: 5 }}>
        <h3>JSON Format Requirements</h3>
        <p>Upload reviews as a JSON array with the following structure:</p>
        <pre style={{ backgroundColor: '#fff', padding: 10, borderRadius: 3, overflow: 'auto' }}>
{`[
  {
    "id": number,           // Unique review identifier
    "location": string,     // Business location (e.g., "NYC - Manhattan")
    "rating": number,       // Rating 1-5
    "text": string,         // Review content
    "date": string          // Date in YYYY-MM-DD format
  }
]`}
        </pre>
        <button onClick={loadSample} style={{ marginTop: 10, padding: '5px 10px' }}>
          Load Sample Data
        </button>
      </div>

      <div style={{ marginBottom: 10 }}>
        <label style={{ display: 'block', marginBottom: 6 }}>API Key (demo only)</label>
        <input type="password" value={apiKey} onChange={(e: any) => setApiKey(e.target.value)} style={{ width: '100%', padding: 8 }} />
      </div>

      <div style={{ marginBottom: 10 }}>
        <label style={{ display: 'block', marginBottom: 6 }}>Upload JSON file</label>
        <input type="file" accept="application/json" onChange={(e: any) => e.target.files && handleFile(e.target.files[0])} />
        <div style={{ marginTop: 6 }}>{fileName}</div>
      </div>

      <div style={{ marginBottom: 10 }}>
        <label style={{ display: 'block', marginBottom: 6 }}>Or paste JSON</label>
        <textarea value={text} onChange={(e: any) => setText(e.target.value)} rows={15} style={{ width: '100%', padding: 8, fontFamily: 'monospace' }} />
      </div>

      <div style={{ marginBottom: 10 }}>
        <label>
          <input type="checkbox" checked={enrich} onChange={(e: any) => setEnrich(e.target.checked)} />
          Enrich reviews with AI features (sentiment analysis, categorization)
        </label>
      </div>

      <button disabled={submitting} onClick={handleSubmit} style={{ padding: '10px 20px', backgroundColor: '#007cba', color: 'white', border: 'none', borderRadius: 3 }}>
        {submitting ? 'Submitting...' : 'Submit Reviews'}
      </button>

      {status && <div style={{ marginTop: 10, padding: 10, backgroundColor: status.includes('Error') ? '#ffeeee' : '#eeffee', borderRadius: 3 }}>{status}</div>}
    </div>
  );
}
