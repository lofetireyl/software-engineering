# tests/test_posts.py
import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session
from sqlalchemy import delete


@pytest.fixture(scope="session")
def app_module(tmp_path_factory):
    """
    - Create a temporary SQLite DB file for the whole test session.
    - Set DATABASE_URL so app.main uses this DB.
    - Import app.main once and create tables.
    """
    db_file = tmp_path_factory.mktemp("data") / "test.db"
    db_url = f"sqlite:///{db_file}"

    # Make sure the app uses THIS DB
    os.environ["DATABASE_URL"] = db_url

    # Import the FastAPI app module (only once)
    import app.main as main

    # Create tables once
    SQLModel.metadata.create_all(main.engine)

    return main


@pytest.fixture
def client(app_module):
    """
    Before each test:
    - Clear all rows from the Post table.
    - Then create a TestClient. When the client starts, the FastAPI
      startup event will run and insert the 3 demo posts if none exist.
    """
    # Clear existing posts
    with Session(app_module.engine) as session:
        session.exec(delete(app_module.Post))
        session.commit()

    # Now, startup will see an empty table and insert the 3 demo posts
    with TestClient(app_module.app) as c:
        yield c


def test_startup_creates_demo_posts(client):
    """
    On startup, the app should:
    - Create the tables (if needed)
    - Insert 3 example posts if the DB is empty
    """
    response = client.get("/posts")
    assert response.status_code == 200

    posts = response.json()
    # We expect exactly the 3 demo posts from on_startup()
    assert len(posts) == 3

    # Check order + sample content
    assert posts[0]["user"] == "alice"
    assert posts[1]["user"] == "bob"
    assert posts[2]["user"] == "charlie"


def test_latest_post_initially_is_third_demo_post(client):
    """
    /posts/latest should return the newest of the 3 demo posts.
    """
    response = client.get("/posts/latest")
    assert response.status_code == 200

    latest = response.json()
    assert latest["user"] == "charlie"
    assert "Third time" in latest["text"]  # matches your seeded text


def test_create_post_and_latest_updates(client):
    """
    After creating a new post via POST /posts, /posts/latest
    should return this new post.
    """
    new_post = {
        "image": "https://example.com/images/new.png",
        "text": "A brand new post",
        "user": "david",
    }

    # Create a new post
    resp_create = client.post("/posts", json=new_post)
    assert resp_create.status_code == 201

    created = resp_create.json()
    assert created["user"] == "david"
    assert created["text"] == "A brand new post"
    assert created["image"] == "https://example.com/images/new.png"

    # Now the latest post should be this one
    resp_latest = client.get("/posts/latest")
    assert resp_latest.status_code == 200

    latest = resp_latest.json()
    assert latest["user"] == "david"
    assert latest["text"] == "A brand new post"
    assert latest["image"] == "https://example.com/images/new.png"

