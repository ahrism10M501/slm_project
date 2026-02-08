import datetime

class MyMCP:
    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

    def run(self, tool_name, **kwargs):
        if tool_name in self.tools:
            try:
                return str(self.tools[tool_name](**kwargs))
            except Exception as e:
                return f"Error: {e}"
        return "Tool not found"

    def get_tools(self):
        docs = []
        for name, fn in self.tools.items():
            doc = fn.__doc__.strip() if fn.__doc__ else ""
            docs.append(f"[tool_name]: {name}\n[tool_doc]: {doc}")
        return "\n".join(docs)

mcp = MyMCP()

if __name__ == "__main__":
    @mcp.tool()
    def get_current_time():
        """현재 시간을 반환합니다."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @mcp.tool()
    def get_weather(city: str):
        """특정 도시의 날씨를 반환합니다."""
        return f"{city}의 날씨는 맑습니다."

    print(mcp.get_tools())
    print(mcp.run("get_current_time"))
    print(mcp.run("get_weather", city="Seoul"))