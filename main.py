import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

BASE_URL = "https://ja.wikipedia.org/wiki/"
# 除外ワード
IGNORED_KEYWORDS = ["語", "学"]
# 最大ループ数
MAX_COUNT = 20

def get_summary_links(keyword):
  try:
    response = requests.get(BASE_URL + keyword)
    soup = BeautifulSoup(response.text, 'html.parser')

    # div.mw-parser-outputにある最初のpタグ要素を取得
    paragraph = soup.select_one("div.mw-parser-output > p")
    if not paragraph:
      return []
    
    # pタグ内のリンクを取得
    links = [urllib.parse.unquote(a['href'].split('/')[-1]) for a in paragraph.find_all('a', href=True) if a['href'].startswith('/wiki/')]

    return links
  except Exception as e:
    print("検索ワードが見つかりませんでした。")
    return []


def get_related_keywords_tree(keyword, depth=1, visited=None):
  if visited is None:
    visited = set()

  # アクセス制限回数を超えたら終了
  if len(visited) >= MAX_COUNT:
    return {keyword + "$": {}}

  # 探索済であれば探索しない
  if keyword in visited:
    return {keyword + "@": {}}

  # 探索を追いかけないワードがあれば探索を終了する
  if keyword.endswith(tuple(IGNORED_KEYWORDS)):
    return {keyword + "$": {}}

  visited.add(keyword)
  
  # 探索回数デバッグ用
  # print(len(visited))

  children = {}
  
  for child_keyword in get_summary_links(keyword):
    # Wikipediaへの過多なアクセスを避ける
    time.sleep(1) 
    children.update(get_related_keywords_tree(child_keyword, depth+1, visited))

  if not children:
    return {keyword + "$": {}}

  return {keyword: children}


def print_tree(tree, level=0):
  for key, value in tree.items():
    print("    " * level + "- " + key)
    if value:
      print_tree(value, level+1)


# コマンド実行時に以下の処理を実行する
if __name__ == "__main__":
  keyword = input("入力: ")
  print('start')
  tree = get_related_keywords_tree(keyword)
  print_tree(tree)
  print('end')
