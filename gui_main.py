import re
import gradio as gr
from load_model import get_exaone_pipeline
from mcps import mcp

pipe = get_exaone_pipeline(do_download=False)

def predict(message, history, system_prompt):
    tools_doc = mcp.get_tools()
    system_prompt_with_tools = (
        f"{system_prompt}\n\n"
        f"너는 다음과 같은 mcp 도구를 사용할 수 있어:\n{tools_doc}\n\n"
        "도구를 사용하고 싶다면, [TOOL:tool_name] 형식으로 출력해줘.\n"
        "예시: 현재 시간을 얻으려면 [TOOL:get_current_time] 라고 출력해줘."
    )

    messages = [{"role": "system", "content": system_prompt_with_tools}]
    
    for entry in history:
        messages.append({"role": entry["role"], "content": entry["content"][0]["text"]})

    messages.append({"role": "user", "content": message})

    # 1차 추론
    outputs = pipe(
        messages, 
        max_new_tokens=1024, 
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )
    response = outputs[0]["generated_text"][-1]["content"]
    
    # 도구 호출 확인 (간단한 정규식으로 [TOOL:이름] 패턴 찾기)
    tool_pattern = r"\[TOOL:(\w+)\]"
    match = re.search(tool_pattern, response)
    
    if match:
        tool_name = match.group(1)
        print(f"Tool call detected: {tool_name}")
        tool_result = mcp.run(tool_name)

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
    gr.Markdown("# Chatbot with EXAONE-3.5")
    
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
        ]
    )

if __name__ == "__main__":
    demo.launch()