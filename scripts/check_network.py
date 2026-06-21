import asyncio
import os

import httpx

from src.config.env_loader import load_project_env
from src.services.openrouter_client import OpenRouterClient

load_project_env()


async def main():
    print("=== Network diagnostic ===\n")

    urls = [
        ("GET", "https://huggingface.co", None),
        ("GET", "https://cems-it.com", None),
        ("GET", "https://openrouter.ai", None),
    ]

    async with httpx.AsyncClient(timeout=30.0) as client:
        for method, url, _ in urls:
            try:
                r = await client.get(url, follow_redirects=True)
                print(f"OK  {url} -> {r.status_code}")
            except Exception as e:
                print(f"FAIL {url} -> {type(e).__name__}: {e}")

    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    print(f"\nAPI key: {'SET (' + str(len(key)) + ' chars)' if key else 'MISSING'}")

    or_client = OpenRouterClient()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                or_client.base_url_chat,
                headers=or_client.headers,
                json={
                    "model": "openrouter/free",
                    "messages": [{"role": "user", "content": "hi"}],
                    "max_tokens": 5,
                },
            )
            print(f"\nOpenRouter API -> {r.status_code}")
            if r.status_code != 200:
                print(r.text[:200])
    except Exception as e:
        print(f"\nOpenRouter API -> FAIL {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
