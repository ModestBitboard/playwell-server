import pytest
from sqlmodel import SQLModel, create_engine, Session

@pytest.fixture(name="db_session")
def db_session_fixture():
    """
    Isolate sqlite database to in-memory object rather than real database
    """

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    # Implicitly clean up tables after tests
    SQLModel.metadata.drop_all(engine)
