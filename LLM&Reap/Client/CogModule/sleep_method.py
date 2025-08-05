import json
import os


sm_path = "./memory/semantic_memory.jsonl"
pm_path = "./memory/procedural_memory.jsonl"
cm_path = "./memory/contextual_memory.jsonl"

def load_existing_memory(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return [json.loads(line) for line in f]

def is_rule_duplicate(new_rule, existing_rules):
    for rule in existing_rules:
        if (rule.get("name") == new_rule.get("name") and
            rule.get("conditions") == new_rule.get("conditions") and
            rule.get("effects") == new_rule.get("effects")):
            return True
    return False

def load_jsonl(path):
    data = []
    with open(path, "r") as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def save_incremental_memory(llm_output, observation):
    # Semantic Memory
    existing_sm = load_existing_memory(sm_path)

    with open(sm_path, "a") as f:
        for rule in llm_output["new_semantic_memory"]:
            if not is_rule_duplicate(rule, existing_sm):
                json.dump(rule, f)
                f.write("\n")
    
    # Procedural Memory
    existing_pm = load_existing_memory(pm_path)
#
    with open(pm_path, "a") as f:
        for rule in llm_output["new_procedural_memory"]:
            if not is_rule_duplicate(rule, existing_pm):
                json.dump(rule, f)
                f.write("\n")
    
    # Contextual Memory (for episodic facts, usually append)
    existing_cm = load_existing_memory(cm_path)

    with open(cm_path, "a") as f:
        for fact in llm_output["new_contextual_memory"]:
            if not is_rule_duplicate(fact, existing_cm):
                json.dump(fact, f)
                f.write("\n")
            #if fact not in [item["event"] for item in existing_cm]:
            #    json.dump({"event": fact}, f)
            #    f.write("\n")

    sm_filt = []
    em_filt = []
    pm_filt = []
    sm_ex = load_jsonl(sm_path)
    for item in sm_ex:
        if item["name"] in observation:
            sm_filt.append(item)
    cm_ex = load_jsonl(cm_path)
    for item in cm_ex:
        if item["name"] in observation:
            em_filt.append(item)
    pm_ex = load_jsonl(pm_path)
    for item in pm_ex:
        if item["target"] in observation:
            pm_filt.append(item)
    
    return sm_filt, em_filt, pm_filt
