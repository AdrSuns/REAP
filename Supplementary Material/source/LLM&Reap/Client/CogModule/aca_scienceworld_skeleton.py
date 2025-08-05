import json
import requests
import re
from collections import defaultdict
from CogModule.sleep_method import *
from CogModule.prompt import *


def clean_llm_output(text):
    # 去掉三重引号、markdown包裹符
    text = text.strip()
    for quote in ["```", "'''"]:
        if text.startswith(quote):
            text = text[len(quote):].strip()
        if text.endswith(quote):
            text = text[:-len(quote)].strip()
    return text


class LLMCommunicator:
    def __init__(self, llm_call_function):
        self.llm_call = llm_call_function      
        self.sleep_step = 3
        self.sleep_counter = 0  
        self.if_event = True

    def record_basic(self, taskNum, score, reward, action, step, if_raw, variation):
        path = "ScienceWorld-main/examples/logs/basic/task_" + str(taskNum) + ".txt"
        text = ""
        try:
            with open(path, 'r') as f:
                text = f.read() + "\n"
        except FileNotFoundError:
            with open(path, "w") as f:
                f.write("")
        with open(path, "w") as f:
            text += ("(Raw)" if if_raw else "(No Sleep)" if self.sleep_step >= 100 else  "No Event" if self.if_event else "") + f"TaskNum:{taskNum} Varaition:{variation} Step:{step} Score:{score} Reward:{reward} Action:{action}" + "\n"
            f.write(text)

    def ask_llm(self, prompt):        
        url = 'http://127.0.0.1:8080/completion'

        payload = {
            "prompt": analyse_system_message + "\n" + prompt,
            "n_predict": 1024,
            "ignore_eos": True, 
            "stop": ["]"],
            "temperature": 0.7,
            "reasoning_format": "deepseek"
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            #print(response.json())  # 如果 llama-server 返回的是 application/json
            result = response.json()
            print("🌟 Prompt内容：" + analyse_system_message + "\n" + prompt)
            print("🌟 模型回答内容：", result['content'])
            print("Over")
        else:
            print("Error:", response.status_code, response.text)

    def get_action_and_update(self, prompt, aca_agent, observation, if_raw=False, taskNum=-1, variation=0):        
        prompt = prompt.replace("\\n", "").replace("\"", "'")
        #print("Prompt: " + prompt)
        prompt_with_obs = prompt + f"\\n\\nLatest Observation:\\n{observation}\\n"

        #self.ask_llm(prompt_with_obs)
        #return False, "look around"

        #print("Prompt_with_obs: " + prompt_with_obs)

        response = None
        while response is None or len(response.text.split("json")) < 2:
            response = requests.get('http://192.168.1.131:5010/' + ('raw' if if_raw else 'analyse' if self.if_event else 'analyse_ne'), json=json.dumps({"system_message": "", "user_message": prompt_with_obs}))
        #print(clean_llm_output(response.text).split("json"))
        text = response.text.split("json")[-1]   
        #text = "Okay, so I'm trying to figure out what action to take next. My goal is to focus on the life stages of the avocado plant, starting from the earliest to the latest, and the plants are located outside. Looking at the available actions, I see options like 'look in {obj}', 'focus on {obj}', and others. Since the plants are outside, I should probably go outside to observe them. But first, I need to check if I can access the outside. The latest observation mentions a door to the outside that's closed, so maybe I need to open it.Wait, the available actions include 'open {obj}', and the door to the outside is an object. So, I can try opening the door. But I don't see 'door' in the available objects for 'open {obj}'. The available objects for 'open' are 'cupboard', 'fridge', 'freezer', 'oven'. Hmm, that's a problem. Maybe I can't open the door directly with the available actions.Alternatively, maybe I can 'focus on outside' to see if there's a way to get there without opening the door. The 'focus on' action is available for 'outside', so that might be a good first step. By focusing on the outside, I can gather more information about the avocado plants and their life stages.So, I think the best action is to 'focus on outside' to start observing the plants. This will help me understand their current state and proceed with the goal.</think>```json{  'action': 'focus on outside',  'updated_working_memory': {},  'updated_semantic_memory': []}```"
        #text = text.split("json")[1]   
        text = text.replace("\\n", "").replace("\\\"", "\"").replace("```", "").replace("'", "\"")
        if if_raw:
            text = text.replace("}\"", "}")
        else:
            text = text.replace("]}\"", "]}")

        #rest = "Okay, so I'm trying to figure out the life stages of an avocado plant, starting from the earliest to the latest. The plant is located outside, so I need to think about its growth process in a natural outdoor setting.\n\nFirst, I know that all plants start from a seed, so the earliest stage must be the seed stage. The avocado seed would be in the ground, probably after falling from the tree or being planted by someone. From there, the seed would germinate, which is the next stage. Germination is when the seed starts to grow into a young plant.\n\nAfter germination, the plant would enter the sapling stage. This is when it's a young tree, starting to grow taller and develop more leaves. The sapling stage is crucial because it's when the tree establishes its root system and starts to grow branches.\n\nOnce the sapling has grown enough, it becomes a mature tree. This is when the avocado tree is fully grown and capable of producing flowers and fruits. Mature trees have a well-developed canopy and can support the growth of avocados.\n\nFinally, the tree will start to produce fruit, which is the avocado itself. This is the reproductive stage where the tree flowers, gets pollinated, and then the fruit develops. The avocados will grow on the branches until they're ready to be harvested.\n\nI should make sure I'm not missing any stages. Sometimes, people talk about the juvenile stage before maturity, but I think in the context of life stages, sapling covers that. Also, after maturity, the tree continues to produce fruit each season, so the fruiting stage is ongoing once the tree is mature.\n\nSo, putting it all together, the life stages from earliest to latest are: Seed, Germination, Sapling, Mature Tree, and Fruiting.\n</think>\n\nThe life stages of an avocado plant, from earliest to latest, are as follows:\n\n1. **Seed**: The avocado plant begins as a seed, typically found in the ground after falling from a tree or being planted.\n2. **Germination**: The seed germinates, initiating growth into a young plant.\n3. **Sapling**: The plant grows into a sapling, developing roots and branches.\n4. **Mature Tree**: The sapling matures into a full-grown tree with a developed canopy.\n5. **Fruiting**: The mature tree produces flowers, which after pollination, develop into avocados.\n\n```json\n{\n  \"action\": \"provide_information\",\n  \"updated_working_memory\": {\n    \"life_stages\": [\n      \"Seed\",\n      \"Germination\",\n      \"Sapling\",\n      \"Mature Tree\",\n      \"Fruiting\"\n    ]\n  },\n  \"updated_semantic_memory\": {\n    \"life_stages_of_avocado_plant\": [\n      \"Seed\",\n      \"Germination\",\n      \"Sapling\",\n      \"Mature Tree\",\n      \"Fruiting\"\n    ]\n  }\n}\n```"

        #print(text.split("json"))
        try:
            parsed = json.loads(text)
        except Exception:
            print(Exception)
            return True, "look around"
        action = parsed.get("action", "").replace('(','').replace(')','').replace(' the', '')
        invalid_actions = []
        while action not in aca_agent.pm.all_actions:
            invalid_actions.append(action)
            response = requests.get('http://192.168.1.131:5010/' + ('raw' if if_raw else 'analyse' if self.if_event else 'analyse_ne'), json=json.dumps({"system_message": "", "user_message": 
                  #str(aca_agent.pm.action_pairs[parsed.get("action_template", "").lower()]) 
                  #+ "or choose another action template that contains that object from:"
                  #+ aca_agent.pm.get_object(action.split(' ')[-1])
                  #+ "\n" + 
                  prompt_with_obs + "\nMoreover, actions:" + str(invalid_actions) + " are not available"}))            
            print(clean_llm_output(response.text).split("json"))
            text = response.text.split("json")[1]   
            text = text.replace("\\n", "").replace("\\\"", "\"").replace("```", "").replace("'", "\"").replace("]}\"", "]}")
            #print(text)
            try:
                parsed = json.loads(text)
            except Exception:
                print(Exception)
                print(text)
                return True, "look around"
            action = parsed.get("action", "")

        if if_raw:
            aca_agent.em.record(observation, action)
            return True, action
        
        updated_wm = parsed.get("updated_working_memory", {})
        updated_sm = parsed.get("updated_semantic_memory", {})

        # 更新WM
        if isinstance(updated_wm, dict):
            for obj, attrs in updated_wm.items():
                aca_agent.wm.update(obj, attrs)

        # 更新SM
        if isinstance(updated_sm, dict):
            for obj, props in updated_sm.items():
                aca_agent.sm.add_object(obj, props)

        # 更新EM
        #aca_agent.em.record(aca_agent.wm, action)

        if self.sleep_counter >= self.sleep_step:
            self.sleep_counter = 0
            self.sleep_and_update(prompt, aca_agent, observation, taskNum, variation)
        else:
            self.sleep_counter += 1

        aca_agent.em.record(observation, action)

        return True, action
    
    def sleep_and_update(self, prompt, aca_agent, observation, taskNum, variation):
        prompt = f"""
            [输入]
            ## 近期情景记忆（Episodic Memory）：
            {str(aca_agent.em.history)}

            ## 已有的语义记忆（Semantic Memory）：
            {str(aca_agent.sm.objects)}
            """
        prompt = prompt.replace("\\n", "").replace("\"", "'")
        #print("Prompt: " + prompt)
        prompt_with_obs = prompt + f"\\n\\nLatest Observation:\\n{observation}\\n"
        #print("Prompt_with_obs: " + prompt_with_obs)

        response = requests.get('http://192.168.1.131:5010/' + ('sleep' if self.if_event else 'sleep_ne'), json=json.dumps({"system_message": "", "user_message": prompt_with_obs}))
        #print(clean_llm_output(response.text).split("json"))
        text = response.text.split("json")[-1]   
        #text = "Okay, so I'm trying to figure out what action to take next. My goal is to focus on the life stages of the avocado plant, starting from the earliest to the latest, and the plants are located outside. Looking at the available actions, I see options like 'look in {obj}', 'focus on {obj}', and others. Since the plants are outside, I should probably go outside to observe them. But first, I need to check if I can access the outside. The latest observation mentions a door to the outside that's closed, so maybe I need to open it.Wait, the available actions include 'open {obj}', and the door to the outside is an object. So, I can try opening the door. But I don't see 'door' in the available objects for 'open {obj}'. The available objects for 'open' are 'cupboard', 'fridge', 'freezer', 'oven'. Hmm, that's a problem. Maybe I can't open the door directly with the available actions.Alternatively, maybe I can 'focus on outside' to see if there's a way to get there without opening the door. The 'focus on' action is available for 'outside', so that might be a good first step. By focusing on the outside, I can gather more information about the avocado plants and their life stages.So, I think the best action is to 'focus on outside' to start observing the plants. This will help me understand their current state and proceed with the goal.</think>```json{  'action': 'focus on outside',  'updated_working_memory': {},  'updated_semantic_memory': []}```"
        #text = text.split("json")[1]   
        text = text.replace("\\n", "").replace("\\\"", "\"").replace("```", "").replace("'", "\"").replace("]}\"", "]}")

        #rest = "Okay, so I'm trying to figure out the life stages of an avocado plant, starting from the earliest to the latest. The plant is located outside, so I need to think about its growth process in a natural outdoor setting.\n\nFirst, I know that all plants start from a seed, so the earliest stage must be the seed stage. The avocado seed would be in the ground, probably after falling from the tree or being planted by someone. From there, the seed would germinate, which is the next stage. Germination is when the seed starts to grow into a young plant.\n\nAfter germination, the plant would enter the sapling stage. This is when it's a young tree, starting to grow taller and develop more leaves. The sapling stage is crucial because it's when the tree establishes its root system and starts to grow branches.\n\nOnce the sapling has grown enough, it becomes a mature tree. This is when the avocado tree is fully grown and capable of producing flowers and fruits. Mature trees have a well-developed canopy and can support the growth of avocados.\n\nFinally, the tree will start to produce fruit, which is the avocado itself. This is the reproductive stage where the tree flowers, gets pollinated, and then the fruit develops. The avocados will grow on the branches until they're ready to be harvested.\n\nI should make sure I'm not missing any stages. Sometimes, people talk about the juvenile stage before maturity, but I think in the context of life stages, sapling covers that. Also, after maturity, the tree continues to produce fruit each season, so the fruiting stage is ongoing once the tree is mature.\n\nSo, putting it all together, the life stages from earliest to latest are: Seed, Germination, Sapling, Mature Tree, and Fruiting.\n</think>\n\nThe life stages of an avocado plant, from earliest to latest, are as follows:\n\n1. **Seed**: The avocado plant begins as a seed, typically found in the ground after falling from a tree or being planted.\n2. **Germination**: The seed germinates, initiating growth into a young plant.\n3. **Sapling**: The plant grows into a sapling, developing roots and branches.\n4. **Mature Tree**: The sapling matures into a full-grown tree with a developed canopy.\n5. **Fruiting**: The mature tree produces flowers, which after pollination, develop into avocados.\n\n```json\n{\n  \"action\": \"provide_information\",\n  \"updated_working_memory\": {\n    \"life_stages\": [\n      \"Seed\",\n      \"Germination\",\n      \"Sapling\",\n      \"Mature Tree\",\n      \"Fruiting\"\n    ]\n  },\n  \"updated_semantic_memory\": {\n    \"life_stages_of_avocado_plant\": [\n      \"Seed\",\n      \"Germination\",\n      \"Sapling\",\n      \"Mature Tree\",\n      \"Fruiting\"\n    ]\n  }\n}\n```"

        #print(text.split("json"))
        print(text)
        parsed = json.loads(text)
        sm, em, pm = save_incremental_memory(parsed, observation=aca_agent.get_all_obs(observation))
        aca_agent.sm.objects.update(em)
        aca_agent.sm.methods = sm
        aca_agent.pm.procedure_mem = pm
        
class WorkingMemory:
    def __init__(self):
        self.memory = {}
        self.memories = []

    def update2(self, obs):
        self.memories.append(obs)

    def update(self, obj, attr):
        if obj not in self.memory:
            self.memory[obj] = {}
        try:
            if attr is str:
                self.memory[obj].update({attr: ""})
            else:
                self.memory[obj].update(attr)
        except:
            pass

    def to_dict(self):
        return self.memory


class ShortTermMemory:
    def __init__(self, max_len=5):
        self.buffer = []
        self.max_len = max_len

    def add(self, item):
        self.buffer.append(item)
        if len(self.buffer) > self.max_len:
            self.buffer.pop(0)

    def get_recent(self):
        return self.buffer

    def clear(self):
        self.buffer = []


class TriggeredMethod:
    def __init__(self, name, conditions, effects, confidence=1.0):
        self.name = name
        self.conditions = conditions
        self.effects = effects
        self.confidence = confidence

class SemanticMemory:
    def __init__(self):
        self.objects = {}
        self.methods = []

    def add_object(self, name, properties):
        self.objects[name] = properties

    def add_method(self, method):
        self.methods.append(method)

class EpisodicMemory:
    def __init__(self):
        self.history = []

    def record(self, obs, action):
        self.history.append({"wm": obs, "action": action})

class ProceduralMemory:
    def __init__(self):
        self.all_actions = ""
        self.actions = []
        self.action_pairs = {}
        self.action_templates = []
        self.procedure_mem = []
        self.object_lists = set()

    def total_action_num(self):
        n = 0
        for k, v in self.action_pairs.items():
            for obj in v:
                n += 1
        print("Total Actions: " + str(n))
        return n

    def get_object(self, obj: str):
        obl = []
        for k, v in self.action_pairs.items():
            if obj in str(v):
                obl.append({k: v})
        return str(obl)
    
    def longestequence(self, s1, s2):
        len1=len(s1)
        len2=len(s2)
        array=[[0]*(len2+1) for _ in range(len1+1)]
        for i in range(1,len1+1):
            for j in range(1,len2+1):
                if s1[i-1]==s2[j-1]:
                    array[i][j]=array[i-1][j-1]+1
                else:
                    array[i][j]=max(array[i][j-1],array[i-1][j])
        return array[len1][len2]
    
    #def filter_actions(self, obs):
    #    obl = [{'look around': [('', '')]}]
    #    for k, v in self.action_pairs.items():
    #        for vi in v:
    #            if '(' in str(vi):
    #                if vi[0] in obs and vi[1] in obs:
    #                    if {k: vi} not in obl:
    #                        exist = False
    #                        for d in obl:
    #                            if k in d:
    #                                exist = True
    #                                d[k].append((vi[0], vi[1]))
    #                        if not exist:
    #                            obl.append({k: [(vi[0], vi[1])]})
    #                    continue
    #            elif vi in obs:
    #                if {k: vi} not in obl:
    #                    exist = False
    #                    for d in obl:
    #                        if k in d:
    #                            exist = True
    #                            d[k].append((vi, ''))
    #                    if not exist:
    #                        obl.append({k: [(vi, '')]})
    #                continue
    #    print(obl)
    #    return str(obl) if len(obl) < 300 else str(self.action_templates)
    
    def filter_actions(self, actions_list, obs=""):
        filtered = []
        for action in actions_list:
            i = -1
            spl = action.split(' ')
            go_on = True
            while go_on and i < len(spl) - 1:
                i += 1
                word = spl[i]
                if word in obs:
                    filtered.append(action)
                    go_on = False                    
        return filtered
    
    def set_actions(self, actions_list, obs=""):
        self.all_actions = actions_list
        actions_list = self.filter_actions(actions_list, obs)
        self.actions = str(self.extract_templates(actions_list)).replace("'", "\"").replace(",)", ")")
        #print(self.actions)

    def extract_templates(self, actions_list, verbose=False):
        actions = []
        preps = ['to', 'for', 'at', 'in', 'on' , 'up', 'down', 'into']
        verb_templates = {}
        self.object_lists = set()
        for action in actions_list:            
            #print("action:" + action)
            words = action.split(' ')
            verb = words[0]
            substring = words[1:]
            prep_list = []
            obj_list = []
            i = 0
            j = -1
            for word in substring:
                j += 1
                if word in preps:
                    prep_list.append(word)
                    if j != 0:
                        obj_list.append(substring[i:j])   
                    i = j + 1
            if i != len(substring):
                obj_list.append(substring[i:])

            verb_template = verb
            perp_first = len(prep_list) == len(obj_list)
            for k in range(len(obj_list)):
                if perp_first:
                    verb_template += ' ' + prep_list[k] + ' ' + f'(obj{k + 1})'
                else:
                    verb_template += ' ' + f'(obj{k + 1})'
                    if k < len(prep_list):
                        verb_template += ' ' + prep_list[k]
            if verb_template not in verb_templates:
                verb_templates[verb_template] = []

            obj_list_words = []
            for obj_words in obj_list:
                obj = ""
                for word in obj_words:
                    obj += word + ' '
                obj_list_words.append(obj.strip())
                self.object_lists.add(obj.strip())
            verb_templates[verb_template].append(tuple(obj_list_words))

            #print(verb_template)
            #print(obj_list_words)
            #print("\n")
        self.action_pairs = verb_templates
        return verb_templates
"""
    def set_actions(self, actions_list):
        self.all_actions = str(actions_list)
        l = [item['action'] for item in actions_list]
        self.actions = str(self.extract_templates(l)).replace("'", "\"")

    def extract_templates(self, actions, verbose=False):
        slot_dict = defaultdict(list)
        unmatched = []

        prepositions = {'to', 'from', 'in', 'on', 'with', 'under', 'into', 'onto', 'at'}

        for act in actions:
            tokens = act.strip().split()

            if len(tokens) == 2:
                # e.g. open door
                verb, obj = tokens
                template = f"{verb} {{obj}}"
                slot_dict[template].append(obj)

            elif len(tokens) == 3:
                # e.g. focus on turtle
                verb, prep, obj = tokens
                if prep in prepositions:
                    template = f"{verb} {prep} {{obj}}"
                    slot_dict[template].append(obj)
                else:
                    unmatched.append(act)

            elif len(tokens) == 4:
                # e.g. move cat to box
                verb, obj1, prep, obj2 = tokens
                if prep in prepositions:
                    template = f"{verb} {{obj1}} {prep} {{obj2}}"
                    slot_dict[template].append((obj1, obj2))
                else:
                    unmatched.append(act)

            else:
                # fallback
                unmatched.append(act)

        # 过滤低频模板
        slot_dict = {k: v for k, v in slot_dict.items()}
        self.action_pairs = slot_dict
        for k, v in slot_dict.items():
            self.action_templates.append(k)

        if verbose:
            print("✅ Extracted Templates:")
            for k, v in slot_dict.items():
                print(f"  {k}  ({len(v)} examples)")

            if unmatched:
                print("\n⚠️ Unmatched or skipped actions:")
                for u in unmatched:
                    print(f"  {u}")

        return slot_dict"""


class GoalModule:
    def __init__(self, desire):
        self.desire = desire

class ACAAgent:
    def __init__(self, goal_desire):
        self.wm = WorkingMemory()
        self.sm = SemanticMemory()
        self.em = EpisodicMemory()
        self.pm = ProceduralMemory()
        self.goal = GoalModule(goal_desire)
        self.llm_communicator: LLMCommunicator

    def update_all(self, observation, actions_available):
        self.pm.set_actions(actions_available)
        self.wm.update("raw_observation", "text", observation)
        
        return self.build_prompt()
    
    def sleep(self):
        """
        Sleep mechanism: consolidate episodic memory into semantic memory
        """
        sleep_prompt = f"""
        You are entering the sleep phase to consolidate memory.

        Goal: {self.goal.desire}

        Episodic Memory (recent steps):
        {self.em.history}

        Semantic Memory (current methods):
        {self.sm.methods}

        Your task is to:
        1. Summarize new generalizable rules (Triggered Methods).
        2. Each rule must have: name, conditions, effects, confidence (0-1).
        3. Select important episodes to keep and discard redundant ones.

        Respond ONLY in the following JSON format:
        {{
          'new_methods': [{{'name': ..., 'conditions': ..., 'effects': ..., 'confidence': ...}}],
          'compressed_em': [ ... ]
        }}
        """
        response = self.llm_communicator.llm_call(sleep_prompt)

        import json
        try:
            parsed = json.loads(response)
            for method in parsed["new_methods"]:
                new_method = TriggeredMethod(
                    method["name"],
                    method["conditions"],
                    method["effects"],
                    method["confidence"]
                )
                self.sm.add_method(new_method)

            #self.em.history = parsed["compressed_em"]
            print("[Sleep] Memory consolidation completed.")
        except json.JSONDecodeError:
            print("[Sleep] Invalid LLM output during sleep phase, skipped.")
    
    def get_all_obs(self, obs):
        #return self.pm.filter_actions(str(self.sm.objects) + str(self.em.history) + obs + ' outside')
        return str(self.em.history[-3:]) + obs + ' outside'

    def build_prompt(self, obs=""):
        prompt = (
            f"You are an intelligent cognitive agent.\\n"
            f"Your goal: {self.goal.desire}\\n\\n"
            f"Current Working Memory:\\n{self.wm.to_dict()}\\n\\n"
            f"Semantic Memory (Objects):\\n{self.sm.objects}\\n\\n"
            f"Semantic Memory (Methods with confidence):\\n"
            f"{[{'name': m.name, 'conditions': m.conditions, 'effects': m.effects, 'confidence': m.confidence} for m in self.sm.methods]}\\n\\n"
            f"Episodic Memory:\\n{self.em.history}\\n\\n"
            f"Procedural Memory:\\n{str(self.pm.procedure_mem)}\\n\\n" +
            #(f"Available Actions:\\n{[{'actions': str([k for k, v in self.pm.action_pairs.items()]), 'obejcts':str(self.pm.object_lists)}]}\\n\\n" 
            #(f"Available Actions:\\n{self.pm.actions[:int(len(self.pm.actions) * 300 / self.pm.total_action_num())]}\\n\\n" 
            #if self.pm.total_action_num() > 300 else f"Available Actions:\\n{self.pm.actions}\\n\\n")+
            f"Available Actions:\\n{self.pm.actions}\\n\\n" +
            f"Based on the goal, working memory, semantic memory, and available actions, "
            f"select the best action from the provided actions to achieve the goal. "
            f"If necessary, provide the updated working memory in JSON format after executing this action.\\n\\n"            
        )
        return prompt
    #def build_prompt(self, obs=""):
    #    prompt = (
    #        f"You are an intelligent cognitive agent.\\n"
    #        f"Your goal: {self.goal.desire}\\n\\n"
    #        f"Current Working Memory:\\n{self.wm.to_dict()}\\n\\n"
    #        f"Semantic Memory (Objects):\\n{self.sm.objects}\\n\\n"
    #        f"Semantic Memory (Methods with confidence):\\n"
    #        f"{[{'name': m.name, 'conditions': m.conditions, 'effects': m.effects, 'confidence': m.confidence} for m in self.sm.methods]}\\n\\n"
    #        f"Episodic Memory (recent 3):\\n{self.em.history[-3:]}\\n\\n"
    #        f"Procedural Memory:\\n{str(self.pm.procedure_mem)}\\n\\n"
    #        f"Available Actions:\\n{self.get_all_obs(obs)}\\n\\n"
    #        f"Based on the goal, working memory, semantic memory, and available actions, "
    #        f"select the best action from the provided actions to achieve the goal. "
    #        f"If necessary, provide the updated working memory in JSON format after executing this action.\\n\\n"            
    #    )
    #    return prompt

