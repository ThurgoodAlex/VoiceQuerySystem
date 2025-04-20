from fastapi import FastAPI, UploadFile, File, HTTPException, Form

import sqlite3
import speech_recognition as sr
from .config import SCHEMA_INFO
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from .nl2sql import sql_chain
from .schema import NLQuery

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
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio.file) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        return {"transcribed_text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Speech recognition failed: {str(e)}")

def execute_query(sql_query: str):
    conn = sqlite3.connect("test_db.sqlite")
    cur = conn.cursor()
    try:
        cur.execute(sql_query)
        return cur.fetchall()
    except Exception as e:
        return f"SQL Error: {str(e)}"
    finally:
        conn.close()

@app.post("/query")
def query_endpoint(payload: NLQuery):
    try:
        output = sql_chain.invoke({"query": payload.query,
                                   "schema": SCHEMA_INFO})

        result_text = output["result"]
        print("results", result_text)

        sql_line = None
        for line in result_text.splitlines():
            line = line.strip()
            if line.lower().startswith("sqlquery:"):
                sql_line = line.split(":", 1)[-1].strip()
                break

        if not sql_line:
            raise ValueError("No SQLQuery found in output.")
        
        return {
            "natural_language_query": payload.query,
            "sql_query": sql_line,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/voice-query")
def voice_query_endpoint(audio: UploadFile = File(...)):
    transcribed_text = transcribe_endpoint(audio)
    response = query_endpoint(NLQuery(query=transcribed_text["transcribed_text"]))
    print("this is the response", response)
    results = execute_query(response["sql_query"])
    return {
        "transcribed_text": transcribed_text["transcribed_text"],
        "sql_query": response["sql_query"],
        "results": results, 
        "natural_language_query": response["natural_language_query"]
    }