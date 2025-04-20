


engine = create_engine(
    POSTGRES_URL,
    pool_pre_ping=True,
    echo=True,
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
