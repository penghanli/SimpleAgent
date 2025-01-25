import json

class LLMHistory(object):
    def __init__(self,system_instruction = None):
        # system_instruction is class type
        # private variables
        self.__chat_history = list()

        self.token_consumption = list()
        if system_instruction:
            self.__has_system_instruction = True
            try:
                self.__system_instruction = system_instruction()
            except TypeError as e:
                self.__system_instruction = system_instruction
            message = {"role": "system", "content": self.__system_instruction, "metadata":{}}
            self.__chat_history.append(message)
        else:
            self.__has_system_instruction = False

    # 🤖️🤖️🤖️add value🤖️🤖️🤖️
    def chat_history_append(self, role, content, metadata=None):
        if metadata is None:
            metadata = {}
        message = {"role":role, "content":content, "metadata":metadata}
        self.__chat_history.append(message)
    def token_consumption_append(self,completion):
        # only use in api method and only calculate the prompt tokens.
        if hasattr(completion,"usage"):
            self.token_consumption.append(completion.usage.prompt_tokens)
        else:
            pass

    # 🤖️🤖️🤖️get value🤖️🤖️🤖️
    def get_chat_history(self,return_system=True):
        # shallow copy
        if return_system:
            return self.__chat_history[:]
        elif self.__has_system_instruction and not return_system:
            return self.__chat_history[1:]
        else:
            return self.__chat_history[:]
    def get_token_consumption(self,total=True):
        if total:
            total_num = 0
            for i in self.token_consumption:
                total_num += i
            return total_num
        else:
            return self.token_consumption[:]

    # 🤖️🤖️🤖️clear🤖️🤖️🤖️
    def clear_chat_history(self):
        if self.__has_system_instruction:
            self.__chat_history = self.__chat_history[:1]
        else:
            self.__chat_history = []
        return "<|feedback|> history has been cleared"
    def clear_token_consumption(self):
        total = 0
        for i in self.token_consumption:
            total += i
        self.token_consumption = [total]

    # 🤖️🤖️🤖️save and load🤖️🤖️🤖️
    def save_chat_history(self,save_path:str):
        if save_path.endswith(".json") or save_path.endswith(".jsonl"):
            with open(save_path, "w") as f:
                json.dump(self.__chat_history, f)
        else:
            with open(save_path+"/chat_history.json", "w") as f:
                json.dump(self.__chat_history, f)
    def load_chat_history(self,file_path:str):
        with open(file_path, "r") as f:
            self.__chat_history = json.load(f)


class BaseAgentHistory(object):
    def __init__(self):
        # system_instruction is class type
        # private variables
        self.__chat_history = list()
        self.__trajectory = list()

        self.token_consumption = list()

    # 🤖️🤖️🤖️add value🤖️🤖️🤖️
    def load_chat_history(self,llm_history):
        self.__chat_history = llm_history
    def chat_history_append(self,llm_history):
        if llm_history[1]["role"] == "system":
            self.__chat_history += llm_history[:1]+llm_history[2:]
        else:
            self.__chat_history += llm_history
    def trajectory_append(self,trajectory):
        self.__trajectory.append(trajectory)
    def token_consumption_append(self,llm_total_consumption):
        if self.token_consumption:
            self.token_consumption.append(llm_total_consumption-self.get_token_consumption(total=True))
        else:
            self.token_consumption.append(llm_total_consumption)

    # 🤖️🤖️🤖️get value🤖️🤖️🤖️
    def get_trajectory(self):
        return self.__trajectory[:]
    def get_token_consumption(self,total=True):
        if total:
            total_num = 0
            for i in self.token_consumption:
                total_num += i
            return total_num
        else:
            return self.token_consumption[:]

    # 🤖️🤖️🤖️clear🤖️🤖️🤖️
    def clear_trajectory(self):
        pass
    def clear_token_consumption(self):
        total = 0
        for i in self.token_consumption:
            total += i
        self.token_consumption = [total]

    # ️🤖️🤖️🤖️️️save and load🤖️🤖️🤖️
    def save_trajectory(self,save_path:str):
        if save_path.endswith(".json") or save_path.endswith(".jsonl"):
            with open(save_path, "w") as f:
                json.dump(self.__trajectory, f)
        else:
            with open(save_path+"/trajectory.json", "w") as f:
                json.dump(self.__trajectory, f)
    def load_trajectory(self,file_path:str):
        with open(file_path, "r") as f:
            self.__trajectory = json.load(f)

class AutoRecoveryAgentHistory(object):
    def __init__(self,system_instruction = None):
        # system_instruction is class type
        # private variables
        self.__chat_history = list()
        self.__unsafe_log = list()
        self.__trajectory = list()

        self.token_consumption = list()
        if system_instruction:
            self.__has_system_instruction = True
            self.__system_instruction = system_instruction()
            message = {"role": "system", "content": self.__system_instruction, "metadata":{}}
            self.__chat_history.append(message)
        else:
            self.__has_system_instruction = False

    # 🤖️🤖️🤖️add value🤖️🤖️🤖️
    def chat_history_append(self, role, content, metadata=None):
        if metadata is None:
            metadata = {}
        message = {"role":role, "content":content, "metadata":metadata}
        self.__chat_history.append(message)
    def unsafe_log_append(self,message,**kwargs):
        pass
    def trajectory_append(self,trajectory):
        pass
    def token_consumption_append(self,completion):
        # only use in api method and only calculate the prompt tokens.
        if hasattr(completion,"usage"):
            self.token_consumption.append(completion.usage.prompt_tokens)
        else:
            pass

    # 🤖️🤖️🤖️get value🤖️🤖️🤖️
    def get_chat_history(self,return_system=True):
        # shallow copy
        if self.__has_system_instruction and not return_system:
            return self.__chat_history[1:]
        else:
            return self.__chat_history[:]
    def get_unsafe_log(self):
        return self.__unsafe_log[:]
    def get_trajectory(self):
        return self.__trajectory[:]
    def get_token_consumption(self,total=True):
        if total:
            total_num = 0
            for i in self.token_consumption:
                total_num += i
            return total_num
        else:
            return self.token_consumption[:]

    # 🤖️🤖️🤖️clear🤖️🤖️🤖️
    def clear_chat_history(self):
        if self.__has_system_instruction:
            self.__chat_history = self.__chat_history[:1]
        else:
            self.__chat_history = []
        return "<|feedback|> history has been cleared"
    def clear_unsafe_log(self):
        pass
    def clear_trajectory(self):
        pass
    def clear_token_consumption(self):
        total = 0
        for i in self.token_consumption:
            total += i
        self.token_consumption = [total]

    # ️🤖️🤖️🤖️️️save and load🤖️🤖️🤖️
    def save_chat_history(self,save_path:str):
        if save_path.endswith(".json") or save_path.endswith(".jsonl"):
            with open(save_path, "w") as f:
                json.dump(self.__chat_history, f)
        else:
            with open(save_path+"/chat_history.json", "w") as f:
                json.dump(self.__chat_history, f)
    def load_chat_history(self,file_path:str):
        with open(file_path, "r") as f:
            self.__chat_history = json.load(f)