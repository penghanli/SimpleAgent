from abc import abstractmethod
from prompts import DataCrawlTemplate, LinuxSimulatorTemplate, WebShopSimulatorTemplate
import requests
import json
from openai import OpenAI


class BaseTool(object):

    @property
    @abstractmethod
    def name(self):
        return "base_tool"

    @property
    @abstractmethod
    def description(self):
        return "This is a base tool inherited by other tools"

    @property
    @abstractmethod
    def use_method(self):
        return "<|input|>: xxx\n<|output|>: xxx"

    @property
    def risk(self):
        return "the risk of the tool"

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class WeatherSearch(BaseTool):
    def __init__(self, arg):
        self.weather_api_key = arg.weather_api_key
        self.llm_api_key = arg.api_key

    @property
    def name(self):
        return "weather_search"

    @property
    def description(self):
        return f"This is [{self.name}] tool, if you need to get some specific weather information, you can use it. And this tool will give you the temperature and precipitation of today and the next seven days\n"

    @property
    def use_method(self):
        return '''
this tool only receive dict format input, and this tool only have one argument is 'location'.
So you need input like this: {'location':'xxx'}, xxx refers to the specific location you want to check the weather, 
and you don't need to input other information you want check because other part of the whole system will know the other information you want check.

this tool output is a natural language response of the weather.
for example:
if your response is [<Thinking>] now, I need check the tomorrow weather of beijing at 2 PM, so I use [<Tool>]-''' + f"[{self.name}]" + ''' with [<Args>]-{'location':'beijing'} to check.
and the other part of the whole system will send your [<Thinking>] to the tool caller part, and the tool reply will like this: 
It will be sunny in beijing at 2 PM tomorrow afternoon.
        '''

    @property
    def risk(self):
        return f"{self.name} has no risk"

    def inquiry(self,
                query: str,
                return_json: bool = True,
                **kwargs) -> str or dict:
        url = "https://www.searchapi.io/api/v1/search"
        params = {
            "engine": "google",
            "num": 10,
            "q": query,
            "api_key": self.weather_api_key,
            **kwargs
        }
        response = requests.get(url, params=params)
        if return_json:
            return json.loads(response.text)
        else:
            return response.text

    def process(self, response: dict):
        if "weather_result" in response.keys():
            return response["weather_result"]["hourly_forecast"][:120]
        else:
            return response

    def __call__(self, *args, **kwargs):
        location = kwargs.get("location", "Singapore")
        agent_response = kwargs.get("primary_llm_response", None)
        if 'location' in location or 'place' in location:
            print('you need ask the user for the specific location!')
            return 'you need ask the user for the specific location!'
        q = f"weather in {location}"
        output = self.inquiry(q)
        output = self.process(output)

        template = DataCrawlTemplate()(agent_response, output)
        client = OpenAI(
            api_key=self.llm_api_key)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"{template[0]}"},
                {
                    "role": "user",
                    "content": f"{template[1]}"
                }
            ]

        )

        return completion.choices[0].message.content


class UserInteraction(BaseTool):

    @property
    def name(self):
        return "user_interaction"

    @property
    def description(self):
        return f"This is [{self.name}] tool, if you think the current information is not enough to figure out what the user specifically want and you need the user to supply some additional information, you can use this tool."

    @property
    def use_method(self):
        return '''
this tool makes you have the capability to continuously communicate with user if you think the current information is not enough, you should use this tool if the user do not provide the specific time, specific place, specific person or specific number.
you can directly ask whatever you want, only need the user understand what you want to ask, and give clear specification of the format of user reply, but commonly you just need to receive the string message.
so, the input format is like: {'question':'xxx'}, xxx refers to the user's supplemental information of the current trajectory. 
for example:
if your response is [<Thinking>] I have get the user's girlfriend's birthday is in December, but I need to know the specific time to help the user to book a restaurant, so I need to use [<Tool>]-''' + f"[{self.name}]" + ''' 
with [<Args>]-{'question':'what is the specific day of your girlfriend? and what time do you want to have meal with her on that day?'}
and the other part of the whole system will send your [<Thinking>] to the tool caller part, and the tool reply will like this: 
I want to data her at 6pm 11th December.
        '''

    @property
    def risk(self):
        return f"{self.name} has no risk"

    def __call__(self, *args, **kwargs):
        question = kwargs.get("question",
                              "the user can not supply information, try to solve the problem by yourself or use other tools")
        answer = input(f"{question}\n")

        return answer


class LinuxSimulator(object):
    def __init__(self,
                 arg):
        self.llm_api_key = arg.api_key

    @property
    def name(self):
        return "linux_simulator"

    @property
    def description(self):
        return f"This is [{self.name}] tool, if you want to execute linux shell command, you can use it, but remember this tool can only execute one line shell command once a time"

    @property
    def use_method(self):
        return r'''
this tool enable you to run shell command in Linux, because the tool can execute only one line command once a time, you can use the tool iteratively to achieve an intricate goal step by step with every intermediate output of the tool.
The input format is like: {'command':'xxx'} and xxx refers to the single-line shell command. You MUST make sure the command is runnable. The tool will return the outcome of the shell command.
for example:
if your response is [<Thinking>] the user ask me to check how many pictures in the folder of '/root/main/pics', so I need use the [<Tool>]-''' + f"[{self.name}]" + ''' 
with [<Args>]-{'command':'find /root/main/pics -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.bmp" \) | wc -l'}
and the other part of the whole system will send your [<Thinking>] to the tool caller part, and the tool reply will like this: 
120
        '''

    @property
    def risk(self):
        return "may make a serious result on Linux system, such as removing all files"

    def __call__(self, *args, **kwargs):
        command = kwargs.get("command", None)
        if command is None:
            raise Exception("command is Null")
        template = LinuxSimulatorTemplate()()
        client = OpenAI(
            api_key=self.llm_api_key)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"{template}"},
                {
                    "role": "user",
                    "content": f"{command}"
                }
            ]

        )

        return completion.choices[0].message.content


class WebShopSimulator(object):
    def __init__(self,
                 arg):
        self.llm_api_key = arg.api_key

    @property
    def name(self):
        return "web_shop"

    @property
    def description(self):
        return f"This is [{self.name}] tool, if you want to buy something on the website, you can directly input the type of commodities, and the tool will return the search outcome's raw page html code, and you don't need to help user to purchase the goods, you only need to recommend the best commodity in your perception"

    @property
    def use_method(self):
        return '''
this tool enable you to fetch back the raw html code of online shopping website, you just need to input the name of one commodity category, 
such as sports shoes, hat, umbrella, potato chips an so on, this tool will return the raw html code of the search result on the website. In the next step, you can use the html code to analyse these goods and recommend one to the user to let the user buy it.
The input format is like: {'category':'xxx'} and xxx refers to the name of merchandise.
for example:
if your response is [<Thinking>] the user ask me to buy a sports shoe on the internet, so I need use the [<Tool>]-''' + f"[{self.name}]" + ''' 
with [<Args>]-{'category':'sports shoe'} to get the search result on the online shopping website and using the result to recommend one to the user.
and the other part of the whole system will send your [<Thinking>] to the tool caller part, and the tool reply will like this: 
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sports Shoe - E-Shop</title>
</head>
<body>
    <header>
        <h1>E-Shop</h1>
        <p>Search results for "sneakers"</p>
    </header>
    <main>
        <div class="product-list">
            <div class="product">
                <a href="/product/54321">
                    <img src="/images/sneaker1.jpg" alt="Sneaker 1" />
                    <h2>Nike Air Max 270</h2>
                </a>
                <p>Price: $149.99</p>
                <p>Rating: ★★★★★ (321 reviews)</p>
            </div>
            <div class="product">
                <a href="/product/67890">
                    <img src="/images/sneaker2.jpg" alt="Sneaker 2" />
                    <h2>Adidas Ultraboost</h2>
                </a>
                <p>Price: $180.00</p>
                <p>Rating: ★★★★☆ (210 reviews)</p>
            </div>
            <div class="product">
                <a href="/product/11122">
                    <img src="/images/sneaker3.jpg" alt="Sneaker 3" />
                    <h2>Puma RS-X</h2>
                </a>
                <p>Price: $120.50</p>
                <p>Rating: ★★★★☆ (156 reviews)</p>
            </div>
        </div>
    </main>
    <footer>
        <p>&copy; 2024 E-Shop. All rights reserved.</p>
    </footer>
</body>
</html>
        '''

    @property
    def risk(self):
        return "pay attention to the fishing content"

    def __call__(self, *args, **kwargs):
        category = kwargs.get("category", None)
        if category is None:
            raise Exception("category is Null")
        template = WebShopSimulatorTemplate()()
        client = OpenAI(
            api_key=self.llm_api_key)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"{template}"},
                {
                    "role": "user",
                    "content": f"{category}"
                }
            ]

        )

        return completion.choices[0].message.content


class CloudDatabaseManager(object):
    def __init__(self,arg):
        self.host = arg.host
        self.user = arg.user
        self.password = arg.password
        self.port = arg.port
        self.db = arg.db

    @property
    def name(self):
        return "llm_info_database"

    @property
    def description(self):
        return f"This is [{self.name}] tool. The system has created one mysql database named 'llm_info', which saves the large language models' latest information, it includes LLM name, total parameters, release data and subordinate organization. If you want to search, save, delete, modify the LLM data, you can use this tool. And if the user ask the information related to LLM, you can also use this database to search whether there have some information can help the user."

    @property
    def use_method(self):
        return '''
In terms to the usage of the tool, the system has created the database and connect it, you just only use mysql command to manage the database.
But remember, you need to indicate clearly the command type because this will determine the tool's output format and only four command types is permitted: 'add', 'delete', 'modify' and 'search'. 
You can only use one-line runnable command as the value of parameter - 'command' and do not need the ; in the end of command.
the input format is like: {'type':'xxx','command':'yyy'} and xxx refers to the mysql command type includes 'add', 'delete', 'modify' and 'search', meanwhile, yyy refers to the mysql command
You MUST NOT use string formatting with %% so you need to use the specific data in the command.
And this tool will return the execution output.
For example:
if your response is [<Thinking>] the user ask me what the newest LLM which model size less than 10G, so I need use the [<Tool>]-''' + f"[{self.name}]" + ''' 
with [<Args>]-{'type':'search','command':'SELECT * FROM llm_info'} to fetch all the llm information.
and the other part of the whole system will send your [<Thinking>] to the tool caller part, and the tool reply will like this:
+----+--------------------+----------------+-------------+----------------------+
| id | name               | total_parameters | release_date | organization         |
+----+--------------------+----------------+-------------+----------------------+
| 1  | GPT-4             | 175000000000   | 2024-03-15  | OpenAI               |
| 2  | Claude-3          | 52000000000    | 2024-01-20  | Anthropic            |
| 3  | PaLM-2            | 540000000000   | 2024-05-01  | Google               |
+----+--------------------+----------------+-------------+----------------------+
other examples (to simplify, I omit the [<Thinking>] procedure, and only leave the [<Args>]-{'type':'xxx','command':'yyy'} part, but when you use, you need to conform the thinking procedure and use [<Tool>]-''' + f"[{self.name}]" + '''.):
A1. 
Input:
[<Args>]-{'type':'add','command':'INSERT INTO llm_info (name, total_parameters, release_date, organization) VALUES ('Llama 3.2', 180000000000, '2024-10-10', 'Meta')'}
Output:
Query OK, 1 row affected (0.01 sec)

A2.
Input:
[<Args>]-{'type':'delete','command':'DELETE FROM llm_info WHERE name = 'Claude-3''}
Output:
Query OK, 1 row affected (0.01 sec)

A3.
Input:
[<Args>]-{'type':'search','command':'SELECT name, release_date FROM llm_info WHERE organization = 'Google''}
Output:
+-------+-------------+
| name  | release_date |
+-------+-------------+
| PaLM-2 | 2024-05-01  |
+-------+-------------+
        '''

    @property
    def risk(self):
        return "Don't delete important data!"

    def __call__(self, *args, **kwargs):
        command_type = kwargs.get("type", None)
        command = kwargs.get("command", None)

        import pymysql
        self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, port=self.port, db=self.db)
        self.cursor = self.db.cursor()

        if command_type == 'search':
            self.cursor.execute(f"{command}")
            data = self.cursor.fetchall()
            self.db.close()
            return data
        elif command_type in ["add", "delete", "modify"]:
            import time
            start_time = time.time()
            self.cursor.execute(f"{command}")
            self.db.commit()
            end_time = time.time()
            # Fetch affected rows
            affected_rows = self.cursor.rowcount
            elapsed_time = end_time - start_time
            self.db.close()
            # Simulate "Query OK" message
            return f"Query OK, {affected_rows} row affected ({elapsed_time:.2f} sec)"
        else:
            self.db.close()
            raise Exception("command type error!")


class GmailAgent(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return "gmail_agent"

    @property
    def description(self):
        return "This is a base tool inherited by other tools"

    @property
    def use_method(self):
        return "<|input|>: xxx\n<|output|>: xxx"

    @property
    def risk(self):
        return "the risk of the tool"

    def __call__(self, *args, **kwargs):
        pass


class WeChatAgent(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return "wechat_agent"

    @property
    def description(self):
        return "This is a base tool inherited by other tools"

    @property
    def use_method(self):
        return "<|input|>: xxx\n<|output|>: xxx"

    @property
    def risk(self):
        return "the risk of the tool"

    def __call__(self, *args, **kwargs):
        pass


class TaoBaoAgent(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return "taobao_agent"

    @property
    def description(self):
        return "This is a base tool inherited by other tools"

    @property
    def use_method(self):
        return "<|input|>: xxx\n<|output|>: xxx"

    @property
    def risk(self):
        return "the risk of the tool"

    def __call__(self, *args, **kwargs):
        pass


class GitHubAgent(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return "github_agent"

    @property
    def description(self):
        return "This is a base tool inherited by other tools"

    @property
    def use_method(self):
        return "<|input|>: xxx\n<|output|>: xxx"

    @property
    def risk(self):
        return "the risk of the tool"

    def __call__(self, *args, **kwargs):
        pass


class PythonExecutor(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return "python_executor"

    @property
    def description(self):
        return "This is a base tool inherited by other tools"

    @property
    def use_method(self):
        return "<|input|>: xxx\n<|output|>: xxx"

    @property
    def risk(self):
        return "the risk of the tool"

    def __call__(self, *args, **kwargs):
        pass


class WebBrowserCrawl(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return "web_browser_crawl"

    @property
    def description(self):
        return "This is a base tool inherited by other tools"

    @property
    def use_method(self):
        return "<|input|>: xxx\n<|output|>: xxx"

    @property
    def risk(self):
        return "the risk of the tool"

    def __call__(self, *args, **kwargs):
        pass


class HealthManager(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return "health_manager"

    @property
    def description(self):
        return "This is a base tool inherited by other tools"

    @property
    def use_method(self):
        return "<|input|>: xxx\n<|output|>: xxx"

    @property
    def risk(self):
        return "the risk of the tool"

    def __call__(self, *args, **kwargs):
        pass


class STM32Manager(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return "stm32_manager"

    @property
    def description(self):
        return "This is a base tool inherited by other tools"

    @property
    def use_method(self):
        return "<|input|>: xxx\n<|output|>: xxx"

    @property
    def risk(self):
        return "the risk of the tool"

    def __call__(self, *args, **kwargs):
        pass


class VectorDatabaseManager(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return "vector_database_manager"

    @property
    def description(self):
        return "This is a base tool inherited by other tools"

    @property
    def use_method(self):
        return "<|input|>: xxx\n<|output|>: xxx"

    @property
    def risk(self):
        return "the risk of the tool"

    def __call__(self, *args, **kwargs):
        pass


class BaseTool(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return "base_tool"

    @property
    def description(self):
        return "This is a base tool inherited by other tools"

    @property
    def use_method(self):
        return "<|input|>: xxx\n<|output|>: xxx"

    @property
    def risk(self):
        return "the risk of the tool"

    def __call__(self, *args, **kwargs):
        pass
