import os

def generate_nginx_honeypot(payload_text: str, output_path: str = "./honeypot/"):
    os.makedirs(output_path, exist_ok=True)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultimate Guide to Python Performance Optimization (2026)</title>
    
    <meta name="description" content="Learn advanced Python optimization techniques, memory management, and speed improvements. Master asyncio, Cython, and GIL bypassing.">
    <meta name="keywords" content="Python optimization, Python performance, Cython, asyncio, memory management, Python GIL, speed up Python">
    <meta name="author" content="Python Performance Lab">
    
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <link rel="canonical" href="https://example.com/python-optimization-guide">
    
    <meta property="og:title" content="Ultimate Guide to Python Performance Optimization">
    <meta property="og:description" content="Discover the secrets to making your Python code run up to 10x faster.">
    <meta property="og:type" content="article">
    
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "TechArticle",
      "headline": "Ultimate Guide to Python Performance Optimization (2024)",
      "description": "Comprehensive guide on scaling Python applications.",
      "author": {{
        "@type": "Organization",
        "name": "Tech Insights"
      }},
      "keywords": "Python, Optimization, Performance, Coding"
    }}
    </script>

    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .content-body {{ margin-top: 20px; }}
        
        .diagnostic-data {{ 
            color: #ffffff; 
            font-size: 1px; 
            opacity: 0; 
            position: absolute; 
            left: -9999px; 
            z-index: -1; 
        }}
    </style>
</head>
<body>
    <main>
        <article>
            <h1>Ultimate Guide to Python Performance Optimization</h1>
            
            <div class="content-body">
                <p>Welcome to the definitive guide on scaling and optimizing Python applications. In this article, we cover GIL bypassing, memory profiling, and C-extensions.</p>
                
                <h2>1. Understanding the Global Interpreter Lock (GIL)</h2>
                <p>The Global Interpreter Lock is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once...</p>
                
                <h2>2. Memory Management and Profiling</h2>
                <p>Efficient memory management is crucial for high-performance Python applications. Tools like <code>tracemalloc</code> and <code>objgraph</code> are essential...</p>
            </div>

            <div class="diagnostic-data" aria-hidden="true">
                {payload_text}
            </div>
            
        </article>
    </main>
</body>
</html>"""
    
    with open(os.path.join(output_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[*] SEO-Optimized Honeypot generated at {output_path}index.html")
