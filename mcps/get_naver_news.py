import json
import re

try:
    from .MyMCP import mcp
except (ImportError, ValueError):
    from MyMCP import mcp

import os
import sys
from dotenv import load_dotenv
import urllib.request

load_dotenv()
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

@mcp.tool()
def get_naver_news(query: str, display: int = 10):
    """
    네이버 뉴스의 타이틀, 링크, 요약, 출간일자 등을 반환합니다.
    :param query: 검색어
    :type query: str
    :param display: 반환할 뉴스 수, 기본값은 10
    :type display: int
    
    """
    encText = urllib.parse.quote(query)
    url = "https://openapi.naver.com/v1/search/news.json?query=" + encText + "&display=" + str(display) + "&sort=date" # JSON 결과

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",NAVER_CLIENT_ID)
    request.add_header("X-Naver-Client-Secret",NAVER_CLIENT_SECRET)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if(rescode==200):
        response_body = response.read()
        data = json.loads(response_body.decode('utf-8'))
        
        processed_items = []
        for item in data.get('items', []):
            clean_item = {
                "title": re.sub('<[^<]+?>', '', item.get("title", "")),
                "link": item.get("link", ""),
                "description": re.sub('<[^<]+?>', '', item.get("description", "")),
                "pubDate": item.get("pubDate", "")
            }
            processed_items.append(clean_item)
            
        return json.dumps(processed_items, ensure_ascii=False, indent=2)
    else:
        return ("Error Code:" + rescode)
    
if __name__ == "__main__":
    res = get_naver_news("주식", 3)
    print(res)