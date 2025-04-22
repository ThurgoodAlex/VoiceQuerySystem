from langchain_experimental.sql import SQLDatabaseChain
from langchain.sql_database import SQLDatabase
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate

from .config import DATABASE_URL, GROQ_API_KEY

db = SQLDatabase.from_uri(DATABASE_URL)

#This is a helper file to feed the SQL query to the LLM and get the results back.
# It uses the langchain library to create a SQLDatabaseChain that connects to the SQLite database and generates SQL queries based on natural language input. it uses the schema from the database to generate the SQL queries.


prompt = PromptTemplate.from_template("""
You are an expert SQLite query generator.
Only use the following tables:

{table_info}
Do not use any other tables or columns.

Question: {input}
Write a single, syntactically correct SQLite SELECT statement that accurately answers the given question. If the question refers to a month or date, return both a numeric format (e.g., '2025-03') and a readable format (e.g., 'March') using appropriate strftime and CASE statements. Use exact table and column names from the provided schema. Do not include any explanation, comments, formatting, or markdown. Return only the SQL query in a single line, with no extra whitespace. The query must be valid and executable in any SQLite environment. If it is a numerical value, such as money, round it to the nearest dollar and prepend a dollar sign (e.g., "$104"). If the result is a product, exclude the description column. Ensure all GROUP BY clauses use full expressions (not aliases), and all ORDER BY clauses reference valid columns from the table schema.

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