from load_model import get_exaone_pipeline

def set_system_prompt():
    system_prompt = "너는 똑똑하고 친절한 AI 어시스턴트야. 사용자의 질문에 전문적으로 답해줘."

    print("Set system prompt")

    p1 = input("[0:defalut]; my: ")
    if p1.lower() != "0" and p1.strip() != "":
        system_prompt = p1

    return system_prompt
        

def main():
    pipe = get_exaone_pipeline()
    system_prompt = set_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    while True:
        user_input = input("\nMy: ")
        if user_input.lower() in ['exit', 'quit', '종료']:
            print("Shutting down")
            break
        
        messages.append({"role": "user", "content": user_input})

        print("\n답변 생성 중...", end="\r")
        
        outputs = pipe(messages)
        res = outputs[0]["generated_text"][-1]["content"]

        print("Model: ", res)

        messages.append({"role": "assistant", "content": res})

if __name__ == "__main__":
    main()