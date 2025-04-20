import React, { useState, useRef } from 'react';
import RecordRTC from 'recordrtc';
import './VoiceQueryApp.css'; // Styling

const VoiceQueryApp = () => {
  const [status, setStatus] = useState('Idle');
  const [data, setData] = useState(null);
  const recorderRef = useRef(null);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    const recorder = new RecordRTC(stream, {
      type: 'audio',
      mimeType: 'audio/wav',
      recorderType: RecordRTC.StereoAudioRecorder,
      desiredSampRate: 16000,
      numberOfAudioChannels: 1,
    });

    recorder.startRecording();
    recorderRef.current = recorder;

    setStatus('🎙 Recording...');
  };

  const stopRecording = () => {
    recorderRef.current.stopRecording(async () => {
      const audioBlob = recorderRef.current.getBlob();
      const formData = new FormData();
      formData.append('audio', audioBlob, 'voice.wav');

      setStatus('⏳ Uploading...');

      try {
        const response = await fetch('http://localhost:5000/voice-query', {
          method: 'POST',
          body: formData,
        });

        const json = await response.json();
        setData(json);
        setStatus('✅ Query complete');
      } catch (error) {
        setStatus(`❌ Failed: ${error.message}`);
        setData(null);
      }
    });
  };

  const extractHeaders = (sql, row = []) => {
    if (/select\s+\*\s+from/i.test(sql)) {
      return row.map((_, i) => `Column ${i + 1}`);
    }

    const match = sql.match(/select\s+(.*?)\s+from/i);
    if (!match) return [];

    return match[1].split(',').map(field => {
      let name = field.trim();
      if (name.toLowerCase().includes(' as ')) {
        name = name.split(/\s+as\s+/i).pop();
      }
      if (name.includes('.')) {
        name = name.split('.').pop();
      }
      return name
        .replace(/^["'`]+|["'`]+$/g, '')
        .replace(/_/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase());
    });
  };

  return (
    <div className="vqa-container">
      <h1>🎙 Voice to SQL Query</h1>

      <div className="vqa-controls">
        <button onClick={startRecording}>Start</button>
        <button onClick={stopRecording}>Stop & Submit</button>
      </div>

      <p className="vqa-status">Status: {status}</p>

      {data && (
        <div className="vqa-result">
          <h2>🎯 Query Response</h2>
          <p><strong>🗣 Transcribed Text:</strong> {data.transcribed_text}</p>
          <p><strong>📄 SQL Query:</strong></p>
          <pre className="vqa-sql">{data.sql_query}</pre>

          <p><strong>📊 Results:</strong></p>
          <table>
            <thead>
              <tr>
                {extractHeaders(data.sql_query, data.results[0]).map((h, i) => (
                  <th key={i}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.results.map((row, i) => (
                <tr key={i}>
                  {row.map((cell, j) => (
                    <td key={j}>{String(cell)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default VoiceQueryApp;
