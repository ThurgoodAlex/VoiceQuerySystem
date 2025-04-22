from fastapi import FastAPI, UploadFile, File, HTTPException
import sqlite3
import speech_recognition as sr
from .config import SCHEMA_INFO
from fastapi.middleware.cors import CORSMiddleware
from .llmWrapper import sql_chain
from .schema import NLQuery
import re


app = FastAPI(title="VoiceQuerySystem")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe")
def transcribe_endpoint(audio: UploadFile = File(...)):
    #converting audio to text using speech recognition
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio.file) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        return {"transcribed_text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Speech recognition failed: {str(e)}")

def execute_query(sql_query: str):
    # Execute the SQL query and return the results
    conn = sqlite3.connect("test_db.sqlite")
    try:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        return cursor 
    except Exception as e:
        return f"SQL Error: {str(e)}"


@app.post("/query")
def query_endpoint(payload: NLQuery):
    # Process the natural language query and convert it to SQL
    # using the SQLDatabaseChain and return the SQL query
    try:
        output = sql_chain.invoke({"query": payload.query,
                                   "schema": SCHEMA_INFO})
        result_text = output["result"]
        print("results", result_text)
        print("Raw output:", output["result"])
        sql_lines = []
        capture = False

        cleaned_result = clean_sql(result_text)

        sql_lines = []
        capture = False
        for line in cleaned_result.splitlines():
            line = line.strip()
            if line.lower().startswith("select"):
                capture = True
            if capture:
                sql_lines.append(line)

        if not sql_lines:
            raise ValueError("No SQLQuery found in cleaned output.")

        sql_query = " ".join(sql_lines).strip()
        
        
        
        return {
            "natural_language_query": payload.query,
            "sql_query": sql_query,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def clean_sql(raw_output: str) -> str:
    # Remove Markdown-style ```sql or ``` from both ends
    return re.sub(r"^```sql\s*|\s*```$", "", raw_output.strip(), flags=re.IGNORECASE)

@app.post("/voice-query")
def voice_query_endpoint(audio: UploadFile = File(...)):
    # Process the audio file, transcribe it, and execute the SQL query
    # using the SQLDatabaseChain and return the results
    transcribed_text = transcribe_endpoint(audio)
    response = query_endpoint(NLQuery(query=transcribed_text["transcribed_text"]))
    print("this is the response", response)
    cursor = execute_query(response["sql_query"])
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    results = [dict(zip(columns, row)) for row in rows]
    cursor.close()

    return {
        "transcribed_text": transcribed_text["transcribed_text"],
        "sql_query": response["sql_query"],
        "results": results, 
        "natural_language_query": response["natural_language_query"]
    }