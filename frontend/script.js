let recorder;

const startBtn = document.getElementById("start");
const stopBtn = document.getElementById("stop");
const status = document.getElementById("status");

startBtn.onclick = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

  recorder = RecordRTC(stream, {
    type: "audio",
    mimeType: "audio/wav",
    recorderType: StereoAudioRecorder,
    desiredSampRate: 16000,
    numberOfAudioChannels: 1
  });

  recorder.startRecording();
  startBtn.disabled = true;
  stopBtn.disabled = false;
  status.textContent = "🎙 Recording in progress...";
};

stopBtn.onclick = () => {
  recorder.stopRecording(async () => {
    const audioBlob = recorder.getBlob();
    console.log("Recorded audio size:", audioBlob.size, "bytes");

    const formData = new FormData();
    formData.append("audio", audioBlob, "voice.wav");
    status.textContent = "⏳ Uploading...";

    try {
      const response = await fetch("http://localhost:5000/voice-query", {
        method: "POST",
        body: formData,
      });

      const json = await response.json();
      const sql = json.sql_query || "";
      const transcribed = json.natural_language_query || json.transcribed_text || "";
      const results = json.results || [];

      // Show the natural language query and SQL
      document.getElementById("nlQuery").textContent = transcribed;
      document.getElementById("sqlQuery").textContent = sql;
      document.getElementById("querySummary").classList.remove("hidden");

      // Render the results table
      const table = document.getElementById("resultsTable");
      const resultBox = document.getElementById("queryResults");
      table.innerHTML = "";

      if (results.length > 0) {
        // Guess headers from SQL or default to Column 1, 2, ...
        const headers = sql.match(/select\s+(.*?)\s+from/i)?.[1]
          ?.split(",")
          .map(h => h.split(" as ").pop().split(".").pop().replace(/["`]/g, "").trim())
          || results[0].map((_, i) => `Column ${i + 1}`);

        const thead = document.createElement("thead");
        const headRow = document.createElement("tr");
        headers.forEach(h => {
          const th = document.createElement("th");
          th.textContent = h;
          headRow.appendChild(th);
        });
        thead.appendChild(headRow);
        table.appendChild(thead);

        const tbody = document.createElement("tbody");
        results.forEach(row => {
          const tr = document.createElement("tr");
          row.forEach(cell => {
            const td = document.createElement("td");
            td.textContent = cell;
            tr.appendChild(td);
          });
          tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        resultBox.classList.remove("hidden");
      } else {
        table.innerHTML = "<tr><td colspan='100%'>No results returned.</td></tr>";
        resultBox.classList.remove("hidden");
      }

      status.textContent = "✅ Results ready!";
    } catch (err) {
      status.textContent = `❌ Error: ${err.message}`;
    }

    startBtn.disabled = false;
    stopBtn.disabled = true;
  });
};
