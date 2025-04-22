let recorder;

const startBtn = document.getElementById("start");
const stopBtn = document.getElementById("stop");
const statusText = document.getElementById("status");

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
  statusText.textContent = "Recording in progress...";
};

stopBtn.onclick = () => {
  recorder.stopRecording(async () => {
    const audioBlob = recorder.getBlob();
    console.log("Recorded audio size:", audioBlob.size, "bytes");

    const formData = new FormData();
    formData.append("audio", audioBlob, "voice.wav");
    statusText.textContent = "Uploading...";

    try {
      const response = await fetch("http://localhost:5000/voice-query", {
        method: "POST",
        body: formData,
      });

      const json = await response.json();
      const sql = json.sql_query || "";
      const transcribed = json.natural_language_query || json.transcribed_text || "";
      const results = json.results || [];

      document.getElementById("nlQuery").textContent = transcribed;
      document.getElementById("sqlQuery").textContent = sql;
      document.getElementById("querySummary").classList.remove("hidden");

      const table = document.getElementById("resultsTable");
      const resultBox = document.getElementById("queryResults");
      table.innerHTML = "";

      if (results.length > 0) {
        // Create table headers and rows dynamically. Ai helped me with this.
        const headers = Object.keys(results[0]);

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
          headers.forEach(h => {
            const td = document.createElement("td");
            td.textContent = row[h];
            tr.appendChild(td);
          });
          tbody.appendChild(tr);
        });
        table.appendChild(tbody);

      } else {
        table.innerHTML = "<tr><td colspan='100%'>No results returned.</td></tr>";
      }

      resultBox.classList.remove("hidden");
      statusText.textContent = "Results ready!";
    } catch (err) {
      statusText.textContent = `Error: ${err.message}`;
    }

    startBtn.disabled = false;
    stopBtn.disabled = true;
  });
};