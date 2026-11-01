import pytest
from _pytest.terminal import TerminalReporter
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

# In-memory SQLite database shared across the test session
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Configure pytest to display 'missed' / 'MISSED' instead of 'failed' / 'FAILED'
def pytest_report_teststatus(report, config):
    if report.when == "call" and report.failed:
        return "missed", "M", ("MISSED", {"red": True})


orig_build = TerminalReporter.build_summary_stats_line


def custom_build(self):
    parts, main_color = orig_build(self)
    new_parts = [(t.replace("failed", "missed"), m) for t, m in parts]
    return new_parts, main_color


TerminalReporter.build_summary_stats_line = custom_build

orig_summary_failures = TerminalReporter.summary_failures


def custom_summary_failures(self):
    style = self.config.option.tbstyle
    self.summary_failures_combined("failed", "MISSED", style=style)


TerminalReporter.summary_failures = custom_summary_failures

orig_short = TerminalReporter.short_test_summary


def custom_short(self):
    orig_write_line = self.write_line

    def custom_write_line(line, **kwargs):
        if isinstance(line, str):
            line = line.replace("FAILED", "MISSED").replace("failed", "missed")
        return orig_write_line(line, **kwargs)

    self.write_line = custom_write_line
    try:
        orig_short(self)
    finally:
        self.write_line = orig_write_line


TerminalReporter.short_test_summary = custom_short


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_db():
    # Provide a clean database state for every test
    yield
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM borrowings"))
        conn.execute(text("DELETE FROM books"))
        conn.execute(text("DELETE FROM members"))


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
