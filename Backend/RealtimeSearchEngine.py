import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re
import time

print("╭────────────────────────────────────────────╮")
print("│  🤖 J.A.R.V.I.S Online — Hello Shivam! │")
print("│  Ask me any topic — I’ll generate a 3000-word report │")
print("╰────────────────────────────────────────────╯\n")

# ────────────────────────────────────────────────
# 🔍 UNIVERSAL SEARCH SCRAPER (Works Everywhere)
# ────────────────────────────────────────────────
def universal_search(query, num_results=5):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # 1️⃣ Try Google Search (Fallback to Brave if blocked)
    try:
        google_url = f"https://www.google.com/search?q={quote(query)}&hl=en"
        r = requests.get(google_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        results = []
        for a in soup.select("a"):
            href = a.get("href")
            if href and href.startswith("http") and "google" not in href and "youtube" not in href:
                results.append(href)
            if len(results) >= num_results:
                break
        if results:
            return results
    except Exception:
        pass

    # 2️⃣ Try Brave Search
    try:
        brave_url = f"https://search.brave.com/search?q={quote(query)}"
        r = requests.get(brave_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for a in soup.select("a.result-header"):
            href = a.get("href")
            if href and href.startswith("http"):
                results.append(href)
            if len(results) >= num_results:
                break
        if results:
            return results
    except Exception:
        pass

    # 3️⃣ As last fallback, use “I’m Feeling Lucky”
    try:
        lucky_url = f"https://www.google.com/search?q={quote(query)}&btnI"
        return [lucky_url]
    except:
        return []

# ────────────────────────────────────────────────
# 🧠 TEXT EXTRACTOR
# ────────────────────────────────────────────────
def extract_text_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        for script in soup(["script", "style", "noscript"]):
            script.extract()

        text = " ".join(soup.stripped_strings)
        text = re.sub(r"\s+", " ", text)
        return text[:8000]
    except Exception:
        return ""

# ────────────────────────────────────────────────
# 🧾 REPORT GENERATOR
# ────────────────────────────────────────────────
def generate_report(query):
    print(f"⏳ Gathering live web content...\n")
    print(f"🌐 Fetching search results for: {query}\n")

    links = universal_search(query)
    if not links:
        print("⚠️ No results found.\n")
        return

    all_text = ""
    for idx, link in enumerate(links, start=1):
        print(f"🔗 [{idx}] {link}")
        content = extract_text_from_url(link)
        if content:
            all_text += f"\n\n--- Article {idx} ---\n{content}"
        time.sleep(1)

    if not all_text.strip():
        print("⚠️ Unable to extract readable content.\n")
        return

    report = all_text[:15000] + "..." if len(all_text) > 15000 else all_text
    print("\n🧠 Generating 3000-word report...\n")
    print(report[:15000])

# ────────────────────────────────────────────────
# 💬 MAIN LOOP
# ────────────────────────────────────────────────
while True:
    query = input("🗣️ You: ").strip()
    if not query:
        continue
    if query.lower() in ["exit", "quit", "bye"]:
        print("👋 Goodbye, Shivam! Have a productive day.")
        break
    generate_report(query)
    print("\n" + "-" * 90 + "\n")
