import trafilatura
import json

from .MyMCP import mcp

@mcp.tool()
def get_news_specific(link: str):
    try:
        # 1. URL 다운로드 (네트워크 요청 및 인코딩 자동 처리)
        downloaded = trafilatura.fetch_url(link)
        
        if downloaded is None:
            return json.dumps({"error": "페이지를 다운로드할 수 없습니다.", "link": link}, ensure_ascii=False)

        # 2. 본문 및 메타데이터 추출
        # include_comments=False: 댓글 제외
        # output_format='json': JSON 형태로 메타데이터까지 포함해서 받기
        result = trafilatura.extract(
            downloaded, 
            include_comments=False,
            include_tables=False,
            output_format='json',
            with_metadata=True
        )

        if result:
            # trafilatura는 JSON 문자열을 반환하므로 다시 객체로 변환
            data = json.loads(result)
            
            output = {
                "title": data.get('title', '제목 없음'),
                "content": data.get('text', ''),
                "link": link,
            }
            return json.dumps(output, ensure_ascii=False, indent=2)
        else:
            return json.dumps({"error": "본문을 추출하지 못했습니다.", "link": link}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e), "link": link}, ensure_ascii=False)