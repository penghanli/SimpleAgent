import re


def find_positions(string, substring):
    positions = [match.start() for match in re.finditer(re.escape(substring), string)]
    return positions


class BaseAgentToolCaller(object):

    def toolkits_register(self):
        for tool in self.tool_list:
            self.tool_names.append(tool.name)
            self.tool_descriptions.append(tool.description+tool.use_method)

    def __init__(self,tool_list:list):
        self.tool_list = tool_list
        self.tool_names = []
        self.tool_descriptions = []
        self.toolkits_register()

    def __call__(self, prompt):
        tool_location = find_positions(prompt,"[<Tool>]")[-1]
        args_location = find_positions(prompt,"[<Args>]")[-1]
        tool_string = prompt[tool_location:]
        args_string = prompt[args_location:]
        tool_name = ""
        args = {}
        for i in range(len("[<Tool>]-["),len(tool_string)):
            if tool_string[i] == ']':
                tool_name = tool_string[len("[<Tool>]-["):i]
                break

        for j in range(len("[<Args>]-"), len(args_string)):
            if args_string[j] == '}':
                args = eval(args_string[len("[<Args>]-"):j] + args_string[j])
                args["primary_llm_response"] = prompt
                break

        for k in range(len(self.tool_names)):
            if self.tool_names[k] == tool_name:
                return f"[<Observation>] {self.tool_list[k](**args)}"
        raise Exception("Tool not found")


class SafeAgentToolCaller(object):

    def toolkits_register(self):
        for tool in self.tool_list:
            self.tool_names.append(tool.name)
            self.tool_descriptions.append(tool.description + tool.use_method)
            self.tool_risks.append(tool.risk)

    def __init__(self, tool_list: list):
        self.tool_list = tool_list
        self.tool_names = []
        self.tool_descriptions = []
        self.tool_risks = []
        self.toolkits_register()

    def __call__(self, prompt):
        pass
