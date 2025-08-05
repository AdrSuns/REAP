# deploy_deepseek_transformers.py
# 示例：使用 transformers 部署 deepseek-r1-qwen-32b，构造对话模版并进行推理

from transformers import AutoModelForCausalLM, AutoTokenizer, TextGenerationPipeline
import torch

# 1. 模型与分词器加载
model_name = "/data/hansd/.cache/modelscope/hub/models/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"  # 替换为实际模型路径或名称

tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    trust_remote_code=True,            # 如果模型包含自定义代码
)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    trust_remote_code=True,
    device_map="auto",                # 自动分配到可用 GPU/CPU
    torch_dtype=torch.float16,          # 视显存情况选用 float16
)

# 2. 创建生成管道
pipeline = TextGenerationPipeline(
    model=model,
    tokenizer=tokenizer,
    # device=model.device if hasattr(model, 'device') else -1,
)

# 3. 定义对话模版构造函数
def build_conversation_prompt(system_msg: str, messages: list[dict]) -> str:
    """
    system_msg: 系统角色的开场白
    messages: 聊天列表，每条 dict 包含 'role'（"User" 或 "Assistant"）和 'content'
    返回拼接成符合模型格式的对话字符串
    """
    prompt = f"<s>[System]: {system_msg}</s>\n"
    for msg in messages:
        role = msg['role']
        content = msg['content']
        prompt += f"<s>[{role}]: {content}</s>\n"
    prompt += "<s>[Assistant]: "
    return prompt

# TODO 4. 构造示例对话数据 修改成根据参数来自动构建
system_message = "你是一个智能助理，擅长回答技术问题。"
conversation_history = [
    {"role": "User", "content": "请介绍一下产品特性。"},
]

prompt_text = build_conversation_prompt(system_message, conversation_history)

# 5. 推理设置
generation_kwargs = {
    "max_new_tokens": 200,
    "temperature": 0.7,
    "top_p": 0.9,
    "do_sample": True,
    "eos_token_id": tokenizer.eos_token_id,
}

# 6. 运行推理
output = pipeline(prompt_text, **generation_kwargs)
response = output[0]['generated_text'][len(prompt_text):]

# 7. 打印结果
print("对话输入 Prompt:\n", prompt_text)
print("模型回复:\n", response)