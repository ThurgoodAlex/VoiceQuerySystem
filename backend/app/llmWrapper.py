from langchain_experimental.sql import SQLDatabaseChain
from langchain.sql_database import SQLDatabase
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate

from .config import DATABASE_URL, GROQ_API_KEY

db = SQLDatabase.from_uri(DATABASE_URL)

prompt = PromptTemplate.from_template("""
You are an expert SQLite query generator.
Only use the following tables:

{table_info}
Do not use any other tables or columns.

Question: {input}
Write a single, correct SQLite SELECT statement to answer the question.
Do not explain anything. Return only valid SQL, no markdown or commentary.
""")

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY,
    temperature=0,
    max_tokens=512
)

sql_chain = SQLDatabaseChain.from_llm(
    llm=llm,
    prompt=prompt,
    db=db,
    return_intermediate_steps=True,
    verbose=True
)