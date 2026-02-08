import torch
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, pipeline, BitsAndBytesConfig

def download_model(save_path):
    model_id = "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct"

    # 현재 디렉토리의 'exaone_model' 폴더에 다운로드
    snapshot_download(
        repo_id=model_id,
        local_dir=save_path,
        local_dir_use_symlinks=False  # 실제 파일을 다운로드 (심볼릭 링크 X)
    )
    print("다운로드 완료!")

def get_exaone_pipeline(do_download=True):
    if do_download:
        download_model("./exaone_model")
    model_id = "./exaone_model"


    # 노트북 4GB에서 돌리려면 어쩔 수 없이 양자화를 해야한다
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )

    gen_config = GenerationConfig.from_pretrained(model_id)
    gen_config.max_length = None
    gen_config.max_new_tokens = 1024
    gen_config.do_sample = True
    gen_config.temperature = 0.7
    gen_config.repetition_penalty = 1.1
    gen_config.pad_token_id = tokenizer.eos_token_id

    model.generation_config = gen_config

    pipe = pipeline(
        "text-generation", 
        model=model, 
        tokenizer=tokenizer)
    
    return pipe

if __name__ == "__main__":
    pipe = get_exaone_pipeline()

    messages = [
        {"role": "system", "content": "너는 똑똑하고 친절한 AI 어시스턴트야. 사용자의 질문에 전문적으로 답해줘."},
        {"role": "user", "content": "반도체 8대 공정을 간단히 설명해줘."}
    ]

    print("답변 생성 중...\n")
    outputs = pipe(messages)

    print(outputs[0]["generated_text"][-1]["content"])