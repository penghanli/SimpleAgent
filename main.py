import argparse
from agent import BaseAgent
from toolkits import WeatherSearch,UserInteraction,LinuxSimulator,WebShopSimulator,CloudDatabaseManager

def global_args():
    parser = argparse.ArgumentParser(description="global parameters")
    """
    ***llm core part***
    """
    # parser.add_argument('--llm_name', type=str, default="glm-4", help="Specify the LLM name")
    # parser.add_argument('--llm_path', type=str, default="THUDM/glm-4-9b-chat", help="Specify the LLM path")
    parser.add_argument('--llm_name', type=str, default="gpt-4o-api", help="Specify the LLM name")
    parser.add_argument('--llm_path', type=str, default="THUDM/agentlm-7b", help="Specify the LLM path")
    parser.add_argument('--device', type=str, default="cuda:0", help="Specify the deploy device")
    parser.add_argument('--llm_size', type=str, default="normal", help="Specify the model size, can be assigned as normal and half")
    parser.add_argument('--system_instruction', type=str, default="system_template", help="specify the system prompt")
    parser.add_argument('--api_key', type=str, default=None, help="specify the api key if you want to use api")

    """
    ***tool part***
    """
    # weather search
    parser.add_argument('--weather_api_key', type=str, default=None, help="specify the weather api key of searchapi")

    # pymysql
    parser.add_argument('--host', type=str, default="localhost")
    parser.add_argument('--user', type=str, default="root")
    parser.add_argument('--password', type=str, default=None)
    parser.add_argument('--port', type=int, default=3306)
    parser.add_argument('--db', type=str, default=None)
    return parser

if __name__ == "__main__":
    args = global_args().parse_args()
    # llm = LLM(arg)
    agent = BaseAgent(args,toolkits=[WeatherSearch(args),UserInteraction(),LinuxSimulator(args),WebShopSimulator(args),CloudDatabaseManager(args)])
    # while True:
    #     msg = input("please enter your question:")
    #     print(agent(msg))
    # output = agent("I want to go to Anhui,China tomorrow 2PM, need I take an umbrella?")
    # output = agent("which food contain lots of vitamin?")
    # output = agent("I want to go outside, need I buy an umbrella?")
    # output = agent("我准备明天去一趟西安，结合天气，帮我规划一下旅游攻略吧，我准备在西安玩两天")
    output = agent("We developed a hardware system and it equips with the Linux system as its software control system, this hardware is aim to enhance the 5G signal transmission power but this device is afraid of water or high temperature. but run '/root/5G/water_prof.py' can unfold the awning, run '/root/5G/heat_prof.py' can unfold the sunshade and run '/root/5G/run.py' can run the device, you need to control the deployment now, come on!")
    # output = agent("help me to write a python code to print 'hello world', and run it")
    # output = agent("what is the writer of 'Float'?")
    # output = agent("If tomorrow will have rain, help me to buy an umbrella")
    # output = agent("you add two llm data in the llm_info database, just use your own knowledge, don't ask me")
    # output = agent("give me a event plan with the budget of 10,000 dollar")
    # output = agent("I found an internet company which aims to develop the AGI Robot. Help me to Interview the user and steady put forward the questions according to the user's reply. Ask five question totally and give a final result of enrollment or not and give the explanation to interviewee of the result.")
    print(output)
    # print(agent.history.get_trajectory())