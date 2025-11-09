# app/main.py
from datetime import datetime
import os
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select


DATABASE_URL = os.environ["DATABASE_URL"]


engine = create_engine(DATABASE_URL, echo=True)


# --- MODELS ---------------------------------------------------------


class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    image: str
    text: str
    user: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PostCreate(SQLModel):
    image: str
    text: str
    user: str


# --- APP & DB SESSION ----------------------------------------------


app = FastAPI(title="Simple Social Media API")


def get_session():
    with Session(engine) as session:
        yield session


@app.on_event("startup")
def on_startup():
    """
    - Create tables if they don't exist.
    - Insert 3 example posts (image, text, user) once.
    """
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Check if we already have posts
        any_post = session.exec(select(Post)).first()
        if any_post is None:
            demo_posts = [
                Post(
                    image="https://example.com/images/cat.png",
                    text="Hello from our very first post! 😺",
                    user="alice",
                ),
                Post(
                    image="https://example.com/images/dog.png",
                    text="Just testing this cool new app 🐶",
                    user="bob",
                ),
                Post(
                    image="https://example.com/images/bird.png",
                    text="Third time’s a charm! 🐦",
                    user="charlie",
                ),
            ]
            session.add_all(demo_posts)
            session.commit()


# --- ROUTES --------------------------------------------------------


@app.get("/posts", response_model=List[Post])
def list_posts(session: Session = Depends(get_session)):
    """
    Return all posts ordered by creation time (oldest first).
    """
    statement = select(Post).order_by(Post.created_at.asc())
    posts = session.exec(statement).all()
    return posts


@app.post("/posts", response_model=Post, status_code=201)
def create_post(post_in: PostCreate, session: Session = Depends(get_session)):
    """
    Create a new post (image, text, user) and store it in the DB.
    """
    # pydantic v2: model_dump(); v1: dict()
    data = post_in.model_dump() if hasattr(post_in, "model_dump") else post_in.dict()
    post = Post(**data)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@app.get("/posts/latest", response_model=Post)
def get_latest_post(session: Session = Depends(get_session)):
    """
    Retrieve the latest post based on 'created_at'.
    """
    statement = select(Post).order_by(Post.created_at.desc()).limit(1)
    latest = session.exec(statement).first()
    if latest is None:
        raise HTTPException(status_code=404, detail="No posts found")
    return latest
