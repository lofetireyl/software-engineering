import os
import app  # this will be your colleague's module

TEST_DB = "test_posts.db"


def setup_function():
    # Runs before each test
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    app.init_db(TEST_DB)


def teardown_function():
    # Runs after each test
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_store_and_get_latest_post():
    # Arrange: create 3 posts
    app.create_post(TEST_DB, "image1.png", "First post", "alice")
    app.create_post(TEST_DB, "image2.png", "Second post", "bob")
    app.create_post(TEST_DB, "image3.png", "Third post", "charlie")

    # Act: get latest post
    latest = app.get_latest_post(TEST_DB)

    # Assert: latest is the last one we inserted
    assert latest["image"] == "image3.png"
    assert latest["text"] == "Third post"
    assert latest["user"] == "charlie"

