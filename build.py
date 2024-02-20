import json
from glob import glob
from os import path, mkdir

main_layout = open("src/main_layout.html").read()
math_head = open("src/math_head.html").read()

def build_page(page_meta):
  page, meta = page_meta
  title = meta.get("title", "[[Add a title in meta.json]]")
  ishome = meta.get("ishome", False)
  needsmath = meta.get("needsmath", False)

  page_dir = path.dirname(page)
  page_name = path.basename(page_dir)
  body = open(f"{page_dir}/body.html").read()

  page_out = main_layout
  page_out = page_out.replace("[[TITLE]]", title)
  page_out = page_out.replace("[[SITEINDEX]]", site_index)
  page_out = page_out.replace("[[BODY]]", body)
  if needsmath:
    page_out = page_out.replace("[[MATH]]", math_head)
  else:
    page_out = page_out.replace("[[MATH]]", "")

  if ishome:
    page_name = ""
  if not path.exists(f"build/{page_name}"):
    mkdir(f"build/{page_name}")
  file_out = open(f"build/{page_name}/index.html","w")
  file_out.write(page_out)
  file_out.close()

# todo order by date
def build_index(page_metas):
  index = '<ul>\n<li><a href="/">home</a></li>'
  for page, meta in page_metas:
    ishome = meta.get("ishome", False)
    if ishome:
      continue
    page_dir = path.dirname(page)
    page_name = path.basename(page_dir)
    index += f'\n<li><a href="/{page_name}">{page_name}</a></li>'
  index += '\n</ul>'
  return index

pages = glob("src/pages/*/meta.json")
page_metas = [(page, json.load(open(page))) for page in pages]

site_index = build_index(page_metas)

for page_meta in page_metas:
  build_page(page_meta)
