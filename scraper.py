
import datetime
import asyncio
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def scrape_url(url: str):
    pages = [url]
    clicks = []
    scrolls = 0
    errors = []
    html = ""

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            html = (await client.get(url)).text
    except Exception as e:
        errors.append({"message": str(e), "phase": "fetch"})

    if len(html) < 500:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle")

                for _ in range(3):
                    await page.mouse.wheel(0, 3000)
                    await asyncio.sleep(1)
                    scrolls += 1

                lm = page.locator("text=Load more")
                if await lm.count() > 0:
                    await lm.first.click()
                    clicks.append("load_more")

                html = await page.content()
                await browser.close()
        except Exception as e:
            errors.append({"message": str(e), "phase": "render"})

    soup = BeautifulSoup(html, "html.parser")

    content_node = (
        soup.find("article")
        or soup.find(id="mw-content-text")
        or soup.find("main")
    )

    if content_node:
        text = content_node.get_text(" ", strip=True)
        raw_html = str(content_node)
    else:
        text = soup.get_text(" ", strip=True)
        raw_html = str(soup)

    return {
        "url": url,
        "scrapedAt": datetime.datetime.utcnow().isoformat() + "Z",
        "meta": {
            "title": soup.title.text if soup.title else "",
            "description": "",
            "language": "en",
            "canonical": url
        },
        "sections": [{
            "id": "main-0",
            "type": "section",
            "label": "Main Content",
            "sourceUrl": url,
            "content": {
                "headings": [],
                "text": text[:800],
                "links": [],
                "images": [],
                "lists": [],
                "tables": []
            },
            "rawHtml": raw_html[:1200],
            "truncated": True
        }],
        "interactions": {
            "clicks": clicks,
            "scrolls": scrolls,
            "pages": pages
        },
        "errors": errors
    }
