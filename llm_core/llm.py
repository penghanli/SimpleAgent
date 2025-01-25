import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from zhipuai import ZhipuAI
from openai import OpenAI

from memory import LLMHistory

class LLM(object):
    def __init__(self, arg):
        self.arg = arg
        self.llm_name = self.arg.llm_name
        self.llm_path = self.arg.llm_path
        self.device = torch.device(self.arg.device)
        self.llm_size = self.arg.llm_size
        self.system_instruction = getattr(arg, "system_instruction", None)
        self.history = LLMHistory(self.system_instruction)

        if self.llm_name == "glm-4":
            self.tokenizer = AutoTokenizer.from_pretrained(self.llm_path, trust_remote_code=True)
            if self.llm_size == "half":
                self.model = AutoModelForCausalLM.from_pretrained(self.llm_path, trust_remote_code=True).half()
            elif self.llm_size == "normal":
                self.model = AutoModelForCausalLM.from_pretrained(self.llm_path, trust_remote_code=True)
            self.model = self.model.to(self.device)

        elif self.llm_name == "agentlm":
            self.tokenizer = AutoTokenizer.from_pretrained(self.llm_path,trust_remote_code=True)
            if self.llm_size == "half":
                self.model = AutoModelForCausalLM.from_pretrained(self.llm_path, trust_remote_code=True).half()
            elif self.llm_size == "normal":
                self.model = AutoModelForCausalLM.from_pretrained(self.llm_path, trust_remote_code=True)
            self.model = self.model.to(self.device)

        elif self.llm_name == 'glm-4-api':
            self.model = ZhipuAI(api_key=arg.api_key)

        elif self.llm_name == 'gpt-4o-api':
            self.model = OpenAI(api_key=arg.api_key)

        self.max_token = 16*1024
        self.temperature = 0.01
        self.top_p = 0.05


    def __call__(self, prompt: str):

        if self.llm_name == 'glm-4':
            if prompt == "\\clear":
                return self.history.clear_chat_history()
            self.history.chat_history_append(role="user",content=prompt)
            inputs = self.tokenizer.apply_chat_template(self.history.get_chat_history(return_system=True),
                                                        add_generation_prompt=False,
                                                        tokenize=True,
                                                        return_tensors="pt",
                                                        return_dict=True
                                                        )
            inputs.to(self.device)
            # temp1 = inputs["input_ids"][0]
            # temp2 = self.tokenizer.all_special_tokens
            # temp3 = self.tokenizer.all_special_ids
            # temp4 = self.tokenizer.decode(temp1,skip_special_tokens=False)
            outputs = self.model.generate(**inputs,
                                          max_length=2500,
                                          do_sample=True)[:, inputs['input_ids'].shape[1]:]
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            self.history.chat_history_append(role="assistant", content=response, metadata={})
            # self.history_manage(self.history_manage_mode)
            return response

        elif self.llm_name == "agentlm":
            if prompt == "\\clear":
                return self.history.clear_chat_history()
            self.history.chat_history_append(role="user", content=prompt)

            def build_inputs(messages):
                inputs = ''
                # for msg in messages:
                #     if msg['role'] == 'system':
                #         inputs += f"{msg['content']}\n"
                #     elif msg['role'] == 'user':
                #         inputs += f"<|user|> {msg['content']}\n"
                #     elif msg['role'] == 'assistant':
                #         inputs += f"<|assistant|> {msg['content']}\n"
                # inputs += "<|assistant|> "
                for msg in messages:
                    if msg['role'] == 'system':
                        inputs += f"{msg['content']}\n"
                    elif msg['role'] == 'user':
                        inputs += f"{msg['content']}\n"
                    elif msg['role'] == 'assistant':
                        inputs += f"{msg['content']}\n"
                return inputs

            inputs = self.tokenizer(build_inputs(self.history.get_chat_history(return_system=True)),return_tensors="pt")
            inputs.to(torch.device("cuda:0"))
            outputs = self.model.generate(**inputs)
            outputs = outputs[:, inputs['input_ids'].shape[1]:]
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            self.history.chat_history_append(role="assistant", content=response, metadata={})
            # self.history_manage(self.history_manage_mode)
            return response

        elif self.llm_name == 'glm-4-api':

            if prompt == "\\clear":
                return self.history.clear_chat_history()

            self.history.chat_history_append(role="user", content=prompt)
            completion = self.model.chat.completions.create(
                model="glm-4",
                messages=self.history.get_chat_history(return_system=True)
            )
            response = completion.choices[0].message.content
            self.history.chat_history_append(role="assistant", content=response, metadata={})
            self.history.token_consumption_append(completion)
            return response

        elif self.llm_name == "gpt-4o-api":
            if prompt == "\\clear":
                return self.history.clear_chat_history()
            self.history.chat_history_append(role="user", content=prompt)
            completion = self.model.chat.completions.create(
                model="gpt-4o",
                messages=self.history.get_chat_history(return_system=True)
            )
            response = completion.choices[0].message.content
            self.history.chat_history_append(role="assistant", content=response,metadata={})
            self.history.token_consumption_append(completion)
            return response

