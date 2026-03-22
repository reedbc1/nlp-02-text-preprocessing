import os
from pathlib import Path

from dotenv import load_dotenv
from xdk import Client

ROOT_PATH = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT_PATH / "data"
ENV_PATH = ROOT_PATH / ".env"
OUTPUT_PATH = DATA_PATH / "text_data_reed.txt"
QUERY = "AI"
TARGET_POST_COUNT = 100
PAGE_SIZE = 100


def get_post_text(post: object) -> str:
    """Return post text for either SDK models or dict-like payloads."""
    post_text = getattr(post, "text", None)
    if post_text is not None:
        return str(post_text)
    if isinstance(post, dict):
        return str(post.get("text", ""))
    return ""


def fetch_posts(client: Client, query: str, target_count: int) -> list[str]:
    """Collect up to target_count recent posts for the supplied query."""
    posts: list[str] = []

    for page in client.posts.search_recent(
        query=query,
        max_results=min(target_count, PAGE_SIZE),
    ):
        page_data = getattr(page, "data", None) or []
        for post in page_data:
            post_text = get_post_text(post).strip()
            if post_text:
                posts.append(post_text.replace("\r", " ").replace("\n", " "))
            if len(posts) >= target_count:
                return posts

    return posts


def append_posts(output_path: Path, posts: list[str]) -> None:
    """Append posts so each record stays on a single line."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as file:
        for post in posts:
            file.write(f"{post}\n")


def main() -> None:
    load_dotenv(dotenv_path=ENV_PATH)

    bearer_token = os.getenv("X_BEARER_TOKEN", "").strip()
    if not bearer_token:
        raise RuntimeError("X_BEARER_TOKEN is not set in the repo .env file.")

    client = Client(bearer_token=bearer_token)
    posts = fetch_posts(client=client, query=QUERY, target_count=TARGET_POST_COUNT)

    if not posts:
        print("No posts found.")
        return

    append_posts(output_path=OUTPUT_PATH, posts=posts)
    print(f"Appended {len(posts)} posts to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
