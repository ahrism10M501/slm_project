import re
import gradio as gr
from load_model import get_exaone_pipeline
from mcps import mcp
import json

pipe = get_exaone_pipeline(do_download=False)

def predict(message, history, system_prompt):
    tools_doc = mcp.get_tools()
    system_prompt_with_tools = (
        f"{system_prompt}\n\n"
        f"너는 다음과 같은 mcp 도구를 사용할 수 있어:\n{tools_doc}\n\n"
        "도구를 사용하려면 반드시 [TOOL:tool_name{\"arg\": \"value\"}] 형식으로 출력해.\n"
        "예시 1 (인자 없음): [TOOL:get_current_time]\n"
        "예시 2 (인자 있음): [TOOL:get_naver_news{\"query\": \"경제\", \"display\": 5}]\n"
        "인자는 반드시 유효한 JSON 형식이어야 해."
    )

    messages = [{"role": "system", "content": system_prompt_with_tools}]
    
    for entry in history:
        messages.append({"role": entry["role"], "content": entry["content"][0]["text"]})

    messages.append({"role": "user", "content": message})

    outputs = pipe(
        messages, 
        max_new_tokens=1024, 
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )
    response = outputs[0]["generated_text"][-1]["content"]
    
    # 도구 호출 확인 (간단한 정규식으로 [TOOL:이름] 패턴 찾기)
    tool_pattern = r"\[TOOL:(\w+)(\{.*?\})?\]"
    match = re.search(tool_pattern, response)
    
    if match:
        tool_name = match.group(1)
        tool_args_str = match.group(2)
        tool_args = {}
        if tool_args_str:
            try:
                tool_args = json.loads(tool_args_str)
            except json.JSONDecodeError:
                print("JSON 파싱 에러 - 인자 형식이 잘못되었습니다.")

        print(f"Tool call detected: {tool_name} with args: {tool_args}")

        try:
            tool_result = mcp.run(tool_name, **tool_args)
        except Exception as e:
            tool_result = f"Error executing tool: {e}"

        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": f"Tool execution result: {tool_result}\nPlease provide the final answer based on this result."})
        
        outputs = pipe(
            messages, 
            max_new_tokens=1024, 
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )

        final_response = outputs[0]["generated_text"][-1]["content"]
        return final_response

    return response

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Chatbot with EXAONE")
    
    with gr.Accordion("⚙️ 설정", open=False):
        system_input = gr.Textbox(
            label="System Prompt", 
            value="너는 똑똑하고 친절한 AI 어시스턴트야. 사용자의 질문에 전문적으로 답해줘.",
            placeholder="AI의 역할을 지정해주세요..."
        )

    # 채팅 인터페이스
    gr.ChatInterface(
        fn=predict,
        additional_inputs=[system_input],
        examples=[
            ["EXAONE 모델에 대해 설명해줘", "너는 똑똑하고 친절한 AI 어시스턴트야."],
            ["지금 몇 시야?", "너가 가진 mcp 툴을 이용해서 답변해줘"],
            ["파이썬으로 피보나치 수열을 출력하는 코드를 작성해줘.", "너는 리눅스 개발자였던 과거를 가지고 있어. C언어 스타일의 코딩을 주로 하는 편이야."],
            ["get_naver_news를 이용해 최신 '경제' 뉴스 '3개'를 찾아줘", "가지고 있는 Tool을 적극적으로 사용해"],
            ["찾은 뉴스 중 두 번째 뉴스에 대한 세부적인 내용이 알고 싶어", "너는 이지적이고 철저한 분석가야. 사용자의 질문에 정중히 답해"]
        ]
    )

if __name__ == "__main__":
    demo.launch()