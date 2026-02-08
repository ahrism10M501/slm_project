import datetime
from .MyMCP import mcp

@mcp.tool()
def get_current_time():
    """현재 시간을 반환합니다."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")