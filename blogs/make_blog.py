'''Generate a static HTML page for a blog post from a markdown file.

Usage:
    python make_blog.py path/to/post.md --author "First Last"

Copies the .md into blogs/, updates blogs/blogs.json, and writes blog/<slug>.html.
'''

import sys, json, re, shutil, html, argparse
from pathlib import Path
from datetime import date
import markdown

ROOT = Path(__file__).resolve().parent.parent
BLOGS_DIR = ROOT / 'blogs'
OUT_DIR = ROOT / 'blog'
MANIFEST = BLOGS_DIR / 'blogs.json'
AUTHORS = BLOGS_DIR / 'authors.json'
SITE_URL = 'https://www.gptomics.com'
GA_ID = 'G-WC0W8D6J20'

TEMPLATE = '''<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <meta name='description' content='{description}' />
  <title>{title} | GPTomics</title>
  <meta property='og:site_name' content='GPTomics' />
  <meta property='og:title' content='{title}' />
  <meta property='og:description' content='{description}' />
  <meta property='og:url' content='{url}' />
  <meta property='og:type' content='article' />
  {article_author_meta}
  <meta property='article:published_time' content='{iso_date}' />
  <meta name='twitter:card' content='summary' />
  <meta name='twitter:site' content='@gptomics' />
  <meta name='twitter:creator' content='@gptomics' />
  <meta name='twitter:title' content='{title}' />
  <meta name='twitter:description' content='{description}' />
  <link rel='canonical' href='{url}' />
  <link rel='icon' type='image/svg+xml' href='../resources/logo.svg' />
  <link rel='icon' href='../resources/favicon.ico' sizes='any' />
  <link rel='icon' type='image/png' sizes='16x16' href='../resources/favicon-16x16.png' />
  <link rel='icon' type='image/png' sizes='32x32' href='../resources/favicon-32x32.png' />
  <link rel='icon' type='image/png' sizes='48x48' href='../resources/favicon-48x48.png' />
  <link rel='icon' type='image/png' sizes='192x192' href='../resources/favicon-192x192.png' />
  <link rel='apple-touch-icon' sizes='180x180' href='../resources/apple-touch-icon.png' />
  <link rel='manifest' href='../resources/site.webmanifest' />
  <link rel='preconnect' href='https://www.googletagmanager.com' />
  <meta name='author' content='{author}' />
  <meta name='robots' content='index, follow' />
  <script type='application/ld+json'>
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{title}",
    "description": "{description}",
    "datePublished": "{iso_date}",
    "dateModified": "{iso_date}",
    "author": {author_jsonld},
    "publisher": {{
      "@type": "Organization",
      "name": "GPTomics",
      "url": "{SITE_URL}",
      "logo": {{
        "@type": "ImageObject",
        "url": "{SITE_URL}/resources/logo_square.png"
      }}
    }},
    "mainEntityOfPage": {{
      "@type": "WebPage",
      "@id": "{url}"
    }}
  }}
  </script>
  <style>
    :root{{
      --bg: #fbfafe;
      --bg2: #ffffff;
      --ink: #16122e;
      --muted: #4d4666;
      --border: #e4dff0;
      --brand: #5d44a8;
      --brand-tint: rgba(93,68,168,0.07);
      --brand-tint-soft: rgba(93,68,168,0.04);
      --brand-edge: rgba(93,68,168,0.28);
      --brand-pale: #d4cce4;
      --editorial: #c2483a;
      --spark: #00b7f3;
      --shadow: 0 8px 26px rgba(22, 18, 46, 0.07);
      --radius: 14px;
      --maxw: 1280px;
    }}
    *{{box-sizing:border-box}}
    body{{
      margin:0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
      color: var(--ink);
      background: var(--bg);
      line-height: 1.6;
    }}
    a{{color: var(--editorial); text-decoration:none}}
    a:hover{{text-decoration: underline}}
    .wrap{{max-width:var(--maxw); margin:0 auto; padding:30px 18px 46px}}

    header{{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:18px;
      padding:0;
      margin:0 0 22px 0;
    }}
    .brand{{display:flex; align-items:flex-start; gap:14px; min-width:0}}
    .brand a.brand-link{{display:flex; align-items:flex-start; gap:14px; color:inherit}}
    .brand a.brand-link:hover{{text-decoration:none}}
    .logo{{width:58px; height:58px; object-fit:contain; flex:0 0 auto}}
    .brand h1{{margin:6px 0 0; font-weight:750; letter-spacing:0.2px; font-size:24px}}
    .brand p{{margin:2px 0 0; color:var(--muted); font-size:13.8px; max-width:60ch}}
    nav{{display:flex; align-items:center; gap:14px; flex-wrap:wrap; justify-content:flex-end}}
    nav a{{
      font-size:13.8px;
      padding:7px 10px;
      border-radius:10px;
      border:1px solid transparent;
      color: var(--ink);
    }}
    nav a:hover{{
      border-color: var(--border);
      background: var(--brand-tint);
      text-decoration:none;
    }}
    nav a.active{{color: var(--brand); border-color: var(--brand-edge); background: var(--brand-tint)}}
    nav a.icon{{padding:7px; color: var(--muted)}}
    nav a.icon:hover{{color: var(--brand)}}
    nav a.icon svg{{width:18px; height:18px; display:block}}

    main{{max-width:800px; margin:0 auto; padding:8px 0 0}}
    .back-link{{
      display:inline-flex;
      align-items:center;
      gap:6px;
      color: var(--muted);
      font-size:13.5px;
      margin-bottom: 22px;
    }}
    .back-link:hover{{color: var(--brand)}}
    .back-link svg{{width:12px; height:12px}}

    article .post-date{{
      font-size:13px;
      color: var(--editorial);
      letter-spacing:1.5px;
      text-transform:uppercase;
      font-weight:700;
      margin-bottom:10px;
    }}
    article h1{{
      margin:0 0 6px;
      font-size: clamp(26px, 4vw, 38px);
      font-weight:800;
      line-height:1.2;
      letter-spacing:-0.2px;
      color: var(--ink);
    }}
    article .byline{{
      color: var(--muted);
      font-size: 15px;
      margin: 0 0 28px;
      font-style: italic;
    }}
    article .byline a{{color: inherit; text-decoration: underline; text-underline-offset: 3px}}
    article .byline a:hover{{color: var(--brand); text-decoration: none}}
    article h2{{
      margin: 36px 0 12px;
      font-size: 20px;
      font-weight: 800;
      letter-spacing: 0.1px;
      color: var(--ink);
    }}
    article h3{{
      margin: 26px 0 10px;
      font-size: 17px;
      font-weight: 700;
      color: var(--ink);
    }}
    article p{{
      margin: 0 0 16px;
      color: var(--ink);
      font-size: 16.5px;
      line-height: 1.75;
    }}
    article a{{color: var(--editorial); text-decoration: underline; text-underline-offset: 3px}}
    article a:hover{{text-decoration: none}}
    article ul, article ol{{
      color: var(--ink);
      font-size: 16.5px;
      line-height: 1.75;
      margin: 0 0 16px;
      padding-left: 22px;
    }}
    article li{{margin-bottom: 6px}}
    article blockquote{{
      border-left: 3px solid var(--spark);
      padding-left: 16px;
      margin: 20px 0;
      color: var(--muted);
      font-style: italic;
    }}
    article .hl{{background: rgba(0,183,243,0.20); padding: 0 3px; border-radius: 2px; box-decoration-break: clone; -webkit-box-decoration-break: clone}}
    article code{{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 14px;
      background: var(--brand-tint);
      color: var(--brand);
      padding: 2px 6px;
      border-radius: 4px;
    }}
    article pre{{
      background: var(--bg2);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px 18px;
      margin: 20px 0;
      overflow-x: auto;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 14px;
      line-height: 1.6;
    }}
    article pre code{{background: none; color: var(--ink); padding: 0}}
    article img{{max-width: 100%; height: auto; margin: 20px 0; border-radius: 8px; cursor: zoom-in}}
    article .figure-pair{{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 12px;
      margin: 20px 0;
    }}
    article .figure-pair img{{width: 100%; margin: 0}}
    .lightbox{{
      position: fixed;
      inset: 0;
      background: rgba(22, 18, 46, 0.88);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 28px;
      z-index: 9999;
      cursor: zoom-out;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.18s ease;
    }}
    .lightbox.is-open{{opacity: 1; pointer-events: auto}}
    .lightbox img{{max-width: 96vw; max-height: 92vh; width: auto; height: auto; background: var(--bg); border-radius: 10px; box-shadow: 0 24px 60px rgba(0,0,0,0.45)}}
    .lightbox-close{{
      position: absolute;
      top: 14px;
      right: 18px;
      color: rgba(255,255,255,0.85);
      font-size: 28px;
      line-height: 1;
      background: transparent;
      border: 0;
      cursor: pointer;
      padding: 6px 10px;
    }}
    .lightbox-close:hover{{color: #fff}}
    article hr{{border: none; border-top: 1px solid var(--border); margin: 32px 0}}
    article .katex-display{{overflow-x: auto; overflow-y: hidden; padding: 4px 0; max-width: 100%; -webkit-overflow-scrolling: touch}}
    article .katex-display > .katex{{white-space: nowrap}}
    @media (max-width: 700px){{
      article .katex-display .katex{{font-size: 0.85em}}
    }}
    @media (max-width: 480px){{
      article .katex-display .katex{{font-size: 0.72em}}
    }}
    article .table-wrap{{overflow-x: auto; margin: 22px 0}}
    article table{{
      width: 100%;
      border-collapse: collapse;
      font-size: 14.5px;
      line-height: 1.5;
      font-variant-numeric: tabular-nums;
      color: var(--ink);
    }}
    article thead th{{
      text-align: left;
      font-weight: 700;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.6px;
      font-size: 11.5px;
      padding: 10px 12px;
      border-bottom: 1.5px solid var(--ink);
      background: transparent;
    }}
    article tbody td{{
      padding: 9px 12px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }}
    article tbody tr:last-child td{{border-bottom: 1px solid var(--ink)}}
    article tbody tr:hover td{{background: rgba(0,183,243,0.10)}}
    article th[style*='right']{{text-align: right}}
    article td[style*='right']{{text-align: right}}
    article table a{{color: var(--editorial)}}

    html{{scroll-behavior:smooth}}
    footer{{
      margin-top:40px;
      padding-top:14px;
      border-top:1px solid rgba(22,18,46,0.10);
      color: rgba(22,18,46,0.55);
      font-size:12.5px;
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:10px;
    }}
    footer a{{color: var(--brand)}}

    @media (max-width: 720px){{
      header{{flex-direction:column; align-items:flex-start}}
      nav{{justify-content:flex-start}}
    }}
    @media (max-width: 500px){{
      footer{{flex-direction:column; text-align:center}}
    }}
  </style>
  <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css' integrity='sha384-nB0miv6/jRmo5UMMR1wu3Gz6NLsoTkbqJghGIsx//Rlm+ZU03BU6SQNC66uf4l5+' crossorigin='anonymous' />
  <script defer src='https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js' integrity='sha384-7zkQWkzuo3B5mTepMUcHkMB5jZaolc2xDwL6VFqjFALcbeS9Ggm/Yr2r3Dy4lfFg' crossorigin='anonymous'></script>
  <script defer src='https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js' integrity='sha384-43gviWU0YVjaDtb/GhzOouOXtZMP/7XUzwPTstBeZFe/+rCMvRwr4yROQP43s0Xk' crossorigin='anonymous'
    onload='renderMathInElement(document.body, {{ delimiters: [{{ left: "$$", right: "$$", display: true }}, {{ left: "\\\\(", right: "\\\\)", display: false }}, {{ left: "\\\\[", right: "\\\\]", display: true }}], throwOnError: false }});'></script>
  <!-- Google tag (gtag.js) -->
  <script async src='https://www.googletagmanager.com/gtag/js?id={GA_ID}'></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA_ID}');
  </script>
</head>
<body id='top'>
  <div class='wrap'>
    <header>
      <div class='brand'>
        <a class='brand-link' href='../index.html'>
          <img class='logo' src='../resources/logo.svg' alt='GPTomics logo' />
          <div>
            <h1>GPTomics</h1>
          </div>
        </a>
      </div>
      <nav aria-label='Primary'>
        <a href='../blog.html' class='active'>Blog</a>
        <a href='../index.html#contact'>Contact</a>
        <a class='icon' href='https://github.com/GPTomics' target='_blank' rel='noopener' aria-label='GitHub'>
          <svg viewBox='0 0 24 24' fill='currentColor'><path d='M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12'/></svg>
        </a>
        <a class='icon' href='https://x.com/gptomics' target='_blank' rel='noopener' aria-label='X'>
          <svg viewBox='0 0 24 24' fill='currentColor'><path d='M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z'/></svg>
        </a>
      </nav>
    </header>

    <main>
      <a class='back-link' href='../blog.html'>
        <svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><path d='M19 12H5M12 19l-7-7 7-7'/></svg>
        All posts
      </a>
      <article>
        <div class='post-date'>{display_date}</div>
        <h1>{title_html}</h1>
        <p class='byline'>{author_html}</p>
        {body_html}
      </article>
    </main>

    <footer>
      <div>&copy; {year} GPTomics. Just figure things out.</div>
      <div><a href='#top'>I'm lazy, take me to the top</a></div>
    </footer>
  </div>
  <div class='lightbox' id='lightbox' role='dialog' aria-modal='true' aria-hidden='true'>
    <button class='lightbox-close' type='button' aria-label='Close'>&times;</button>
    <img alt='' />
  </div>
  <script>
    (function(){{
      var box = document.getElementById('lightbox');
      var img = box.querySelector('img');
      function open(src, alt){{
        img.src = src;
        img.alt = alt || '';
        box.classList.add('is-open');
        box.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
      }}
      function close(){{
        box.classList.remove('is-open');
        box.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        img.src = '';
      }}
      document.querySelectorAll('article img').forEach(function(el){{
        el.addEventListener('click', function(){{ open(el.currentSrc || el.src, el.alt); }});
      }});
      box.addEventListener('click', close);
      document.addEventListener('keydown', function(e){{ if(e.key === 'Escape') close(); }});
    }})();
  </script>
</body>
</html>
'''


def extract_title(md_text):
    for line in md_text.splitlines():
        m = re.match(r'^#\s+(.+?)\s*$', line)
        if m:
            return m.group(1).strip()
    return None


def strip_title(md_text):
    lines = md_text.splitlines()
    for i, line in enumerate(lines):
        if re.match(r'^#\s+', line):
            del lines[i]
            while i < len(lines) and lines[i].strip() == '':
                del lines[i]
            break
    return '\n'.join(lines)


def extract_description(md_body, limit=155):
    for line in md_body.splitlines():
        s = line.strip()
        if not s or s.startswith('#') or s.startswith('>') or s.startswith('-') or s.startswith('*'):
            continue
        s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s)
        s = re.sub(r'[*_`]', '', s)
        s = s.strip()
        if not s:
            continue
        if len(s) <= limit:
            return s
        cut = s[:limit].rsplit(' ', 1)[0]
        return cut + '…'
    return 'Writing from GPTomics.'


def format_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime('%B %-d, %Y').upper()


def load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return []


def load_authors():
    if AUTHORS.exists():
        return json.loads(AUTHORS.read_text())
    return {}


def save_manifest(entries):
    entries_sorted = sorted(entries, key=lambda e: e['date'], reverse=True)
    MANIFEST.write_text(json.dumps(entries_sorted, indent=2) + '\n')


def upsert_manifest(manifest, file_name, iso_date, title, author):
    for entry in manifest:
        if entry['file'] == file_name:
            entry['title'] = title
            entry['author'] = author
            return manifest
    manifest.append({'file': file_name, 'date': iso_date, 'title': title, 'author': author})
    return manifest


def parse_args():
    p = argparse.ArgumentParser(description='Generate a blog post HTML page from markdown.')
    p.add_argument('markdown', help='path to the .md post')
    p.add_argument('--author', required=True, nargs='+', help='one or more authors (space-separated, quote multi-word names); homepage URLs come from blogs/authors.json')
    return p.parse_args()


def main():
    args = parse_args()
    src = Path(args.markdown).expanduser().resolve()
    if not src.exists() or src.suffix.lower() != '.md':
        print(f'Error: {src} is not a markdown file')
        sys.exit(1)

    slug = src.stem
    md_dest = BLOGS_DIR / f'{slug}.md'
    html_dest = OUT_DIR / f'{slug}.html'
    OUT_DIR.mkdir(exist_ok=True)
    BLOGS_DIR.mkdir(exist_ok=True)

    if src.resolve() != md_dest.resolve():
        shutil.copyfile(src, md_dest)
        print(f'copied {src.name} -> blogs/{md_dest.name}')

    md_text = md_dest.read_text()
    title = extract_title(md_text) or slug.replace('_', ' ').title()
    body_md = strip_title(md_text)
    description = extract_description(body_md)

    author_names = args.author
    author_field = author_names[0] if len(author_names) == 1 else author_names

    manifest = load_manifest()
    existing = next((e for e in manifest if e['file'] == md_dest.name), None)
    iso_date = existing['date'] if existing else date.today().isoformat()
    manifest = upsert_manifest(manifest, md_dest.name, iso_date, title, author_field)
    save_manifest(manifest)

    authors_map = load_authors()
    author_pairs = [(name, authors_map.get(name)) for name in author_names]

    def author_link(name, url):
        n = html.escape(name)
        if url:
            return f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{n}</a>'
        return n

    links = [author_link(n, u) for n, u in author_pairs]
    if len(links) == 1:
        author_html = links[0]
    elif len(links) == 2:
        author_html = f'{links[0]} and {links[1]}'
    else:
        author_html = ', '.join(links[:-1]) + f', and {links[-1]}'

    article_author_meta = '\n  '.join(f"<meta property='article:author' content='{html.escape(n)}' />" for n in author_names)

    def author_jsonld_entry(name, url):
        obj = {'@type': 'Person', 'name': name}
        if url:
            obj['url'] = url
        return json.dumps(obj)

    if len(author_pairs) == 1:
        author_jsonld = author_jsonld_entry(*author_pairs[0])
    else:
        author_jsonld = '[' + ', '.join(author_jsonld_entry(n, u) for n, u in author_pairs) + ']'

    body_html = markdown.markdown(body_md, extensions=['extra', 'sane_lists', 'nl2br', 'toc'])
    body_html = re.sub(r'(<table>.*?</table>)', r'<div class="table-wrap">\1</div>', body_html, flags=re.DOTALL)

    url = f'{SITE_URL}/blog/{slug}.html'
    page = TEMPLATE.format(
        title=html.escape(title),
        title_html=html.escape(title),
        description=html.escape(description),
        author=html.escape(', '.join(author_names)),
        author_html=author_html,
        article_author_meta=article_author_meta,
        author_jsonld=author_jsonld,
        url=url,
        iso_date=iso_date,
        display_date=format_date(iso_date),
        year=date.today().year,
        body_html=body_html,
        SITE_URL=SITE_URL,
        GA_ID=GA_ID,
    )
    html_dest.write_text(page)
    print(f'wrote blog/{html_dest.name}')
    print(f"manifest: {md_dest.name} @ {iso_date} by {', '.join(author_names)}")


if __name__ == '__main__':
    main()
