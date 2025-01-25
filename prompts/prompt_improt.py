from prompts import *
def PromptImprot(**kwargs):
    name = kwargs.get("system_instruction","system_template")
    if name == "system_template":
        toolkits = kwargs.get("toolkits",None)
        return SystemTemplate(toolkits)
    elif name in ["None","none","no prompt", None, 0, -1, "Null","null"]:
        return None
    else:
        return ""
