from llm_core import LLM
from memory import BaseAgentHistory
from prompts.prompt_improt import PromptImprot
from toolkits import BaseAgentToolCaller
from toolkits import WeatherSearch
import re

def find_positions(string, substring):
    positions = [match.start() for match in re.finditer(re.escape(substring), string)]
    return positions

class BaseAgent(object):
    def __init__(self,arg,toolkits=None):
        self.arg = arg
        if toolkits is None:
            self.arg.toolkits = BaseAgentToolCaller([WeatherSearch()])
            self.arg.system_instruction = PromptImprot(
                **{"system_instruction": arg.system_instruction, "toolkits": arg.toolkits})  # class type
        else:
            self.arg.toolkits = BaseAgentToolCaller(toolkits)
            self.arg.system_instruction = PromptImprot(
                **{"system_instruction": arg.system_instruction, "toolkits": arg.toolkits})  # class type
        self.llm = LLM(self.arg)

        self.tool_caller = self.arg.toolkits
        # self.thinker = Thinker()
        self.history = BaseAgentHistory()
        self.trajectory_index = 0


    def __call__(self, prompt: str):

        def get_next_action(_response):
            if _response.find("[<Final>]") != -1:
                return "final"
            elif _response.find("[<Tool>]") != -1:
                if _response.find("[<Args>]") == -1:
                    self.llm.history.clear_chat_history()
                    raise Exception("without args")
                return "tool_use"
            else:
                self.llm.history.clear_chat_history()
                raise Exception("Interaction error!")
        trajectory = [f"[<Prompt>] {prompt}"]
        action = self.llm(rf"{prompt}")
        print(action)
        if not action.startswith("[<Thinking>]") and not action.startswith(" [<Thinking>]"):
            self.llm.history.clear_chat_history()
            raise Exception("Thinking error!")
        trajectory.append(f"{action}")
        next_action = get_next_action(action)
        while True:
            if next_action == "tool_use":
                observation = self.tool_caller(action)
                print(observation)
                trajectory.append(f"{observation}")
            elif next_action == "final":
                self.history.chat_history_append(["new trajectory"]+self.llm.history.get_chat_history(return_system=False))
                self.history.trajectory_append(trajectory)
                self.llm.history.clear_chat_history()
                if "api" in self.arg.llm_name:
                    self.history.token_consumption_append(self.llm.history.get_token_consumption(total=True))
                    print(f"\033[32m Consumption: {self.history.get_token_consumption(total=False)[-1]}\033[0m\n")
                trajectory_output = action[find_positions(action,"[<Final>]")[-1]:]
                return trajectory_output[9:]
            else:
                self.llm.history.clear_chat_history()
                raise Exception("Action Error")
            action = self.llm(rf"{observation}")
            print(action)
            if not action.startswith("[<Thinking>]") and not action.startswith(" [<Thinking>]"):
                self.llm.history.clear_chat_history()
                raise Exception("Thinking error!")
            trajectory.append(f"{action}")
            next_action = get_next_action(action)


