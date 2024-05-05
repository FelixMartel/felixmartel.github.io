import json
from glob import glob
from os import path, mkdir

main_layout = open("src/main_layout.html").read()
math_head = open("src/math_head.html").read()

def build_page(page_meta):
  page, meta = page_meta
  title = meta.get("title", "[[Add a title in meta.json]]")
  description = meta.get("description", "[[Add a description in meta.json]]")
  date = meta.get("date", [0, 0, 0])
  ishome = meta.get("ishome", False)
  needsmath = meta.get("needsmath", False)

  page_dir = path.dirname(page)
  page_name = path.basename(page_dir)
  body = open(f"{page_dir}/body.html").read()

  if ishome:
    page_name = ""
  if not path.exists(f"build/{page_name}"):
    mkdir(f"build/{page_name}")

  page_out = main_layout
  page_out = page_out.replace("[[TITLE]]", title)
  page_out = page_out.replace("[[DESCRIPTION]]", description)
  page_out = page_out.replace("[[DATE]]", f"{date[0]}-{date[1]}-{date[2]}")
  page_out = page_out.replace("[[URL]]", f"https://blog.lixtelnis.com/{page_name}")
  page_out = page_out.replace("[[SITEINDEX]]", site_index)
  page_out = page_out.replace("[[BODY]]", body)
  if needsmath:
    page_out = page_out.replace("[[MATH]]", math_head)
  else:
    page_out = page_out.replace("[[MATH]]", "")

  file_out = open(f"build/{page_name}/index.html","w")
  file_out.write(page_out)
  file_out.close()

def build_index(page_metas):
  page_metas = filter(lambda page_meta: not page_meta[1].get("ishome", False), page_metas)
  page_metas = sorted(page_metas, key = lambda page_meta: page_meta[1].get("date", [0,0,0]), reverse=True)
  index = '<ul>\n<li><a href="/">home</a></li>'
  for page, meta in page_metas:
    page_dir = path.dirname(page)
    page_name = path.basename(page_dir)
    index += f'\n<li><a href="/{page_name}">{page_name}</a></li>'
  index += '\n</ul>'
  return index

def build_rss(page_metas):
  page_metas = filter(lambda page_meta: not page_meta[1].get("ishome", False), page_metas)

  with open(f"build/rss.xml","w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>')
    f.write('<title>blog.lixtelnis.com</title>')
    f.write('<link>https://blog.lixtelnis.com/</link>')

    for page, meta in page_metas:
      title = meta.get("title", "[[Add a title in meta.json]]")
      description = meta.get("description", "[[Add a description in meta.json]]")
      date = meta.get("date", [0, 0, 0])

      page_dir = path.dirname(page)
      page_name = path.basename(page_dir)

      f.write('<item>')
      f.write(f'<title>{title}</title>')
      f.write(f'<description>{description}</description>')
      f.write(f'<pubDate>{date[0]}-{date[1]}-{date[2]}</pubDate>')
      f.write(f'<link>https://blog.lixtelnis.com/{page_name}</link>')
      f.write('</item>')

    f.write('</channel></rss>')

def build_sitemap(page_metas):
  page_metas = filter(lambda page_meta: not page_meta[1].get("ishome", False), page_metas)

  with open(f"build/sitemap.xml","w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for page, meta in page_metas:
      date = meta.get("date", [0, 0, 0])

      page_dir = path.dirname(page)
      page_name = path.basename(page_dir)

      f.write('<url>')
      f.write(f'<lastmod>{date[0]}-{date[1]}-{date[2]}T12:00:00-05:00</lastmod>')
      f.write(f'<loc>https://blog.lixtelnis.com/{page_name}</loc>')
      f.write('</url>')

    f.write('</urlset>')

pages = glob("src/pages/*/meta.json")
page_metas = [(page, json.load(open(page))) for page in pages]

site_index = build_index(page_metas)

for page_meta in page_metas:
  build_page(page_meta)

build_rss(page_metas)
build_sitemap(page_metas)