import warnings
warnings.filterwarnings("ignore")
import torch
import json
import traceback
from gevent import pywsgi
from flask import Flask, jsonify, request
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig, pipeline
from prompt_message import *
from transformers import BitsAndBytesConfig
from prompt_message import *

from peft import prepare_model_for_kbit_training



model_name_or_path = "/data/hansd/.cache/modelscope/hub/models/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
# model_name_or_path = "/data/zhangx/.cache/modelscope/hub/AI-ModelScope/Mixtral-8x7B-Instruct-v0___1"
quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=200.0)

config = AutoConfig.from_pretrained(model_name_or_path)
config.use_cache = True
config.gradient_checkpointing = False

torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

quant_config = BitsAndBytesConfig(
    load_in_8bit=True,              # ✅ 量化为 8-bit
    llm_int8_threshold=6.0,         # 可选，控制哪些层量化
    llm_int8_skip_modules=None,     # 可选，跳过某些模块
    llm_int8_enable_fp32_cpu_offload=True  # 可选，省显存
)
model = AutoModelForCausalLM.from_pretrained(
    model_name_or_path,
    device_map="auto",
    torch_dtype=torch_dtype,
    trust_remote_code=True,
    quantization_config=None,  # 禁用 bnb 量化
    attn_implementation="flash_attention_2"
)
#model = AutoModelForCausalLM.from_pretrained(model_name_or_path,
#                                            #  config=config,
#                                             trust_remote_code=False,
#                                             quantization_config=quant_config,   # ✅ 新方式
#                                             device_map="auto",
#                                             torch_dtype=torch_dtype,
#                                             attn_implementation="flash_attention_2"
#                                            )


tokenizer = AutoTokenizer.from_pretrained(model_name_or_path,
                        trust_remote_code=False,
                        use_fast=True)

#print(model)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=2048,
    do_sample=False,
    temperature=0.3,
    top_p=0.9,
    repetition_penalty=1.0,
    return_full_text = True,
    eos_token_id=tokenizer.eos_token_id
    # pad_token_id=tokenizer.eos_token_id, 
)
terminators = [
            pipe.tokenizer.eos_token_id,
            pipe.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]
app = Flask(__name__)
@app.route("/predict", methods=['GET', 'POST'])
def tactics_predict():
    input = request.json
    print(input)
    try:
        
        message = [
            {"role": "system", "content": predict_system_message},
            {"role": "user", "content": input.get('user_message')}
        ]
        # message = "<s>[INST] <<SYS>>" + predict_system_message + "<</SYS>>" + input.get('user_message') + "[/INST]"  
        prompt = tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
        outputs = pipe(prompt, eos_token_id=terminators)[0]['generated_text']
        print("outputs:",outputs)
        return jsonify(outputs)
    except:
        return "None"
    
# @app.route("/infer", methods=['GET', 'POST'])
# def tactics_infer():
#     # print(request.json)
#     # input = request.json
#     try:
#         input = json.loads(str(request.json))
#         message = [
#             {"role": "system", "content": infer_system_message},
#             {"role": "user", "content": input.get('user_message')}
#         ]
#         # message = "<s>[INST] <<SYS>>" + predict_system_message + "<</SYS>>" + input.get('user_message') + "[/INST]"  
#         prompt = tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
#         print(prompt)
#         outputs = pipe(prompt, eos_token_id=terminators)[0]['generated_text']
#         # logits = model.generate(**tokenizer(message, return_tensors="pt", max_length=1024, return_full_text=False))
#         print(outputs)
#         return jsonify(outputs)
#     except:
#         return "None"
@app.route("/raw", methods=['GET', 'POST'])
def raw():
    input = request.json
    print(input)   
    print(model.device)
    try:
        input = json.loads(input)
        message = [
            {"role": "system", "content": raw_analyse_system_message},
            {"role": "user", "content": input.get('user_message')}
        ]
        
        prompt = tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
        outputs = pipe(prompt)[0]['generated_text']
        print(outputs)
        return jsonify(outputs)
    except Exception as e:
        print("Error:", e)
        return "None"
        

@app.route("/analyse_ne", methods=['GET', 'POST'])
def analyse_ne():
    input = request.json
    print(input)   
    print(model.device)
    try:
        input = json.loads(input)
        message = [
            {"role": "system", "content": analyse_system_message_no_event},
            {"role": "user", "content": input.get('user_message')}
        ]
        
        prompt = tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
        outputs = pipe(prompt)[0]['generated_text']
        print(outputs)
        return jsonify(outputs)
    except Exception as e:
        print("Error:", e)
        return "None"

@app.route("/analyse", methods=['GET', 'POST'])
def analyse():
    input = request.json
    print(input)   
    print(model.device)
    try:
        input = json.loads(input)
        message = [
            {"role": "system", "content": analyse_system_message},
            {"role": "user", "content": input.get('user_message')}
        ]
        
        prompt = tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
        outputs = pipe(prompt)[0]['generated_text']
        print(outputs)
        return jsonify(outputs)
    except Exception as e:
        print("Error:", e)
        return "None"
        

@app.route("/sleep", methods=['GET', 'POST'])
def sleep():
    input = request.json
    print(input)   
    print(model.device)
    try:
        input = json.loads(input)
        message = [
            {"role": "system", "content": sleep_message},
            {"role": "user", "content": input.get('user_message')}
        ]
        
        prompt = tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
        outputs = pipe(prompt)[0]['generated_text']
        print(outputs)
        return jsonify(outputs)
    except Exception as e:
        print("Error:", e)
        return "None"

@app.route("/sleep_ne", methods=['GET', 'POST'])
def sleep_ne():
    input = request.json
    print(input)   
    print(model.device)
    try:
        input = json.loads(input)
        message = [
            {"role": "system", "content": sleep_message_no_event},
            {"role": "user", "content": input.get('user_message')}
        ]
        
        prompt = tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
        outputs = pipe(prompt)[0]['generated_text']
        print(outputs)
        return jsonify(outputs)
    except Exception as e:
        print("Error:", e)
        return "None"

@app.route("/infer_enemy", methods=['GET', 'POST'])
def tactics_infer_enemy2():
    # print(request.json)
    input = request
    try:
        # input = json.loads(str(request.json))
        message = [
            {"role": "system", "content": infer_enemy_message},
            {"role": "user", "content": input.get('user_message').replace("\"", "'")}
        ]
        # message = "<s>[INST] <<SYS>>" + predict_system_message + "<</SYS>>" + input.get('user_message') + "[/INST]"  
        prompt = tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
        print(prompt)
        outputs = pipe(prompt, eos_token_id=terminators)[0]['generated_text']
        # logits = model.generate(**tokenizer(message, return_tensors="pt", max_length=1024, return_full_text=False))
        print(outputs)
        return jsonify(outputs)
    except:
        return "None"
    
@app.route("/infer", methods=['GET', 'POST'])
def tactics_infer_enemy():
    input = str(request.json).replace('\'', '\"')
    print(input)
    try:
        input = json.loads(input)
        message = [
            {"role": "system", "content": infer_enemy_message},
            {"role": "user", "content": input.get('user_message')}
        ]
        
        prompt = tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
        outputs = pipe(prompt)[0]['generated_text']
        print(outputs)
        return jsonify(outputs)
    except Exception as e:
        print("Error:", e)
        return "None"
    
#@app.route("/infer", methods=['GET', 'POST'])
#def tactics_infer_ally():
#    print(request.json)
#    input = request.json
#    print(input)
#    try:
#        input = json.loads(str(request.json))
#        message = [
#            {"role": "system", "content": infer_ally_message},
#            {"role": "user", "content": input['user_message']}
#        ]
#        # message = "<s>[INST] <<SYS>>" + predict_system_message + "<</SYS>>" + input.get('user_message') + "[/INST]"  
#        prompt = tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
#        outputs = pipe(prompt, eos_token_id=terminators)[0]['generated_text']
#        # logits = model.generate(**tokenizer(message, return_tensors="pt", max_length=1024, return_full_text=False))
#        print(outputs)
#        return jsonify(outputs)
#    except:        
#        print(traceback.format_exc())
#        return "None"

# app.run(host='0.0.0.0', port=5005)
server = pywsgi.WSGIServer(('0.0.0.0', 5010),app)
server.serve_forever()