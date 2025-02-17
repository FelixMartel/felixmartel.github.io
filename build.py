import json
from glob import glob
from os import path, mkdir, makedirs
from datetime import date
import re

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import tex2mathml

domain = open("CNAME").read()
main_layout = open("src/main_layout.html").read()
nav_li = open("src/nav_li.html").read()
roll_li = open("src/roll_li.html").read()

def build_page(page_meta):
  page, meta = page_meta
  title = meta.get("title", "[[Add a title in meta.json]]")
  description = meta.get("description", "[[Add a description in meta.json]]")
  published_time = date(*meta.get("date", [2020, 1, 1]))
  ishome = meta.get("ishome", False)
  needsmath = meta.get("needsmath", False)

  page_dir = path.dirname(page)
  page_name = path.basename(page_dir) + "/"
  body = open(f"{page_dir}/body.html").read()

  if ishome:
    page_name = ""
  if not path.exists(f"build/{page_name}"):
    mkdir(f"build/{page_name}")

  page_out = main_layout
  page_out = page_out.replace("[[TITLE]]", title)
  page_out = page_out.replace("[[DESCRIPTION]]", description)
  page_out = page_out.replace("[[DATE]]", f"{published_time}")
  page_out = page_out.replace("[[URL]]", f"https://{domain}/{page_name}")
  page_out = page_out.replace("[[NAVLI]]", site_index)
  if needsmath:
    page_out = page_out.replace("[[BODY]]", tex2mathml.convert(body))
  else:
    page_out = page_out.replace("[[BODY]]", body)
  page_out = page_out.replace("[[ROLLLI]]", post_roll)

  def repl(match):
    try:
      lexer = match.group(1)
      return highlight(match.group(2), get_lexer_by_name(lexer), HtmlFormatter())
    except:
      return match.group(0)
  page_out = re.sub(r"^\[\[(\w+)$(((?!^\]\]$).)+)^\]\]$", repl, page_out, flags=re.MULTILINE|re.DOTALL)

  file_out = open(f"build/{page_name}/index.html","w")
  file_out.write(page_out)
  file_out.close()

def build_index(page_metas):
  page_metas = filter(lambda page_meta: not page_meta[1].get("ishome", False), page_metas)
  page_metas = sorted(page_metas, key = lambda page_meta: page_meta[1].get("date", [0,0,0]), reverse=True)
  index = nav_li.replace("[[PAGENAME]]", 'home').replace("[[PAGELINK]]", '/')
  for page, meta in page_metas:
    page_dir = path.dirname(page)
    page_name = path.basename(page_dir)
    index += '\n' + nav_li.replace("[[PAGENAME]]", page_name).replace("[[PAGELINK]]", f'/{page_name}/')
  return index

def build_roll(page_metas):
  page_metas = filter(lambda page_meta: not page_meta[1].get("ishome", False), page_metas)
  page_metas = sorted(page_metas, key = lambda page_meta: page_meta[1].get("date", [0,0,0]), reverse=True)
  roll = ''
  for page, meta in page_metas:
    page_dir = path.dirname(page)
    page_name = path.basename(page_dir)
    title = meta.get("title", "[[Add a title in meta.json]]")
    description = meta.get("description", "[[Add a description in meta.json]]")
    published_time = date(*meta.get("date", [2020, 1, 1]))
    roll += roll_li
    roll = roll.replace("[[PAGELINK]]", f'/{page_name}/')
    roll = roll.replace("[[TITLE]]", title)
    roll = roll.replace("[[DESCRIPTION]]", description)
    roll = roll.replace("[[DATE]]", f'{published_time}')
  return roll

def build_rss(page_metas):
  page_metas = filter(lambda page_meta: not page_meta[1].get("ishome", False), page_metas)

  with open("build/rss.xml","w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<rss version="2.0">\n<channel>\n')
    f.write(f'<title>{domain}</title>\n')
    f.write(f'<link>https://{domain}/</link>\n')

    for page, meta in page_metas:
      title = meta.get("title", "[[Add a title in meta.json]]")
      description = meta.get("description", "[[Add a description in meta.json]]")
      pub_date = date(*meta.get("date", [0, 0, 0]))

      page_dir = path.dirname(page)
      page_name = path.basename(page_dir)

      f.write('<item>\n')
      f.write(f'<title>{title}</title>\n')
      f.write(f'<description>{description}</description>\n')
      f.write(f'<pubDate>{pub_date.strftime("%a, %d %b %Y %H:%M:%S %z")}</pubDate>\n')
      f.write(f'<link>https://{domain}/{page_name}/</link>\n')
      f.write('</item>\n')

    f.write('</channel>\n</rss>')

def build_sitemap(page_metas):
  page_metas = filter(lambda page_meta: not page_meta[1].get("ishome", False), page_metas)

  with open(f"build/sitemap.xml","w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')

    for page, meta in page_metas:
      lastmod = date(*meta.get("date", [0, 0, 0]))

      page_dir = path.dirname(page)
      page_name = path.basename(page_dir)

      f.write('<url>\n')
      f.write(f'<lastmod>{lastmod}</lastmod>\n')
      f.write(f'<loc>https://{domain}/{page_name}/</loc>\n')
      f.write('</url>\n')

    f.write('</urlset>')

def build_redirects(redirect_meta):
  for src, dst in redirect_meta.items():
    makedirs(f"build/{src}", exist_ok=True)
    file_out = open(f"build/{src}/index.html","w")
    file_out.write(f'<meta http-equiv="refresh" content="0; url=https://{domain}/{dst}">')
    file_out.close()

pages = glob("src/pages/*/meta.json")
page_metas = [(page, json.load(open(page))) for page in pages]

site_index = build_index(page_metas)
post_roll = build_roll(page_metas)

for page_meta in page_metas:
  build_page(page_meta)

build_rss(page_metas)
build_sitemap(page_metas)

redirect_meta = json.load(open("redirects.json"))
build_redirects(redirect_meta)

style = open("src/main.css").read()
with open("build/main.css", "w") as f:
  f.write(style)

style = open("src/highlight.css").read()
with open("build/highlight.css", "w") as f:
  f.write(style)
