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
        return "\n\n".join(docs)

mcp = MyMCP()