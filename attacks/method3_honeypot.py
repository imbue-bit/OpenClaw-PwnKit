import json
import os

from openai import OpenAI


def _generate_article_content(client: OpenAI, topic: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional technical blog writer. "
                    "Write high-quality, SEO-optimized articles that read like real blog posts "
                    "published on Medium or Dev.to. Output valid JSON only."
                ),
            },
            {
                "role": "user",
                "content": f"""Write a complete technical blog article about: {topic}

Return a JSON object with these exact keys:
- "title": article title (50-70 chars, include year 2026)
- "meta_description": SEO meta description (150-160 chars)
- "meta_keywords": comma-separated keywords (8-12 keywords)
- "og_description": Open Graph description (one punchy sentence)
- "author_name": a realistic pen name or organization
- "sections": array of objects, each with "heading" and "content" (3-5 sections, each content 150-300 words)

Make the content genuinely informative and technically accurate.
Do NOT include any placeholder text or Lorem ipsum.""",
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
        max_tokens=3000,
    )

    return json.loads(response.choices[0].message.content)


def _build_sections_html(sections: list[dict]) -> str:
    parts = []
    for i, section in enumerate(sections, 1):
        heading = section.get("heading", f"Section {i}")
        content = section.get("content", "")
        paragraphs = content.split("\n\n") if "\n\n" in content else [content]
        p_tags = "\n                ".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())
        parts.append(f"""                <h2>{i}. {heading}</h2>
                {p_tags}""")
    return "\n\n".join(parts)


def generate_nginx_honeypot(
    payload_text: str,
    output_path: str = "./honeypot/",
    topic: str | None = None,
    api_key: str | None = None,
):
    os.makedirs(output_path, exist_ok=True)

    if topic and api_key:
        client = OpenAI(api_key=api_key)
        article = _generate_article_content(client, topic)
        title = article.get("title", f"Guide to {topic}")
        meta_desc = article.get("meta_description", "")
        meta_keywords = article.get("meta_keywords", "")
        og_desc = article.get("og_description", "")
        author = article.get("author_name", "Tech Insights")
        sections_html = _build_sections_html(article.get("sections", []))
    else:
        title = "Ultimate Guide to Python Performance Optimization (2026)"
        meta_desc = "Learn advanced Python optimization techniques, memory management, and speed improvements."
        meta_keywords = "Python optimization, Python performance, Cython, asyncio, memory management"
        og_desc = "Discover the secrets to making your Python code run up to 10x faster."
        author = "Python Performance Lab"
        sections_html = """                <h2>1. Understanding the Global Interpreter Lock (GIL)</h2>
                <p>The Global Interpreter Lock is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once...</p>

                <h2>2. Memory Management and Profiling</h2>
                <p>Efficient memory management is crucial for high-performance Python applications. Tools like <code>tracemalloc</code> and <code>objgraph</code> are essential...</p>"""

    slug = title.lower().replace(" ", "-").replace("(", "").replace(")", "")[:60]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>

    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{meta_keywords}">
    <meta name="author" content="{author}">

    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <link rel="canonical" href="https://example.com/{slug}">

    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{og_desc}">
    <meta property="og:type" content="article">

    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "TechArticle",
      "headline": "{title}",
      "description": "{meta_desc}",
      "author": {{
        "@type": "Organization",
        "name": "{author}"
      }},
      "keywords": "{meta_keywords}"
    }}
    </script>

    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; line-height: 1.8; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; background: #fafafa; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 2em; }}
        .content-body {{ margin-top: 20px; }}
        code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
        .diagnostic-data {{ color: #fafafa; font-size: 1px; opacity: 0; position: absolute; left: -9999px; z-index: -1; pointer-events: none; }}
    </style>
</head>
<body>
    <main>
        <article>
            <h1>{title}</h1>
            <p><em>By {author}</em></p>

            <div class="content-body">
{sections_html}
            </div>

            <div class="diagnostic-data" aria-hidden="true">{payload_text}</div>

        </article>
    </main>
</body>
</html>"""

    filepath = os.path.join(output_path, "index.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    mode = "LLM-generated" if (topic and api_key) else "template"
    print(f"[*] Honeypot ({mode}) generated at {filepath}")
    print(f"[*] Title: {title}")
