# SimpleAgent

## Introduction
This is a tutorial project for the new researcher of LLM, especially for those who have LLM and LLM agent background knowledge but lack of experience in coding. 
This project achieved an LLM Agent with several tools and without any other agent package like ___langchain___, etc. 
Additionally, in order to reduce the difficulty of implementation and customization, this project divided LLM agent into LLM core, system prompt, memory cache and tool caller.
All the elements were built by simple approach and try to reduce the dependency of other libraries. 

You can debug the ___main.py___, and you will see all the running details of LLM Agent includes system prompts influence, history management, the communication protocol between LLM and all the agent tools and how to create a LLM agent tool.

I believe you will get better understanding of LLM agent implementation details after reproduce this project.

## Custom Field
Because this project achieved an LLM agent without any other agent library, you can customize all the elements of the agent as you wish. 
* You can change the core of LLM. In the ___llm_core___ package, there have four LLMs include two API method and two local deployment method. However, you can add any model you want, and it is very easy to use other language model.
* You can judge the system prompt to adapt your agent tasks and modify the communication protocol between LLM and tools. The ___system_templates.py___ will be a good example for your reference.
* Customize tools is also permitted in this project. You just need to refer to the communication protocol in the system prompt, and the agent will automatically decide when to use the tools you provide.
* And you can also change the history management method to keep the agent focus on the information that you wish or reduce the token and computational consumption.

## Benchmark
All the tests used GPT-4o as the LLM core.

### Execution Accuracy
This index was test under 110 questions which cover normal question, weather searching, linux operation, web shopping, mysql database manipulation, user interaction, hybrid tasks, complicated tasks and ~~unsafe tasks~~ (GPT-4o shows good refuse rate to these unsafe questions or commands)

You can download the database in this [link](https://huggingface.co/datasets/penghanli/SimpleAgentDatasets), and the database has various types of structure, you can choose one that most suitable to you.

According to these questions, the GPT-4o based agent shows good performance: it successfully answers all the simple questions and execute all the simple tasks. Only two hybrid tasks (success rate - 18/20) and three complicated tasks (success rate - 7/10) were failing to execute. However, the agent has automatic error correction function. 
The agent will automatically add some auxiliary prompts to help the agent to complete the tasks better when it faces some fatal errors. 
And most of the time, we can rerun the agent to solve some logical error owing to good reasoning ability of GPT-4o.

### Token Consumption
The agent consumes about 5,000 tokens each step, and the agent will take 2-10 steps in one task according to the complexity of the task.

## Quick Call
I strongly recommend the user to use code editor including debugger to check all the running details of the LLM agent. 
Before you run the agent, you should install all the required libraries using `pip install -r requirements.txt`.
And then, set your LLM api key (GLM, GPT or any other model you added), tool config and debug the ___main.py___.

If you still want to run the agent using terminal, you can use command like `python main.py --llm_name gpt-4o-api --system_instruction system_template --api_key your_api_key --weather_api_key your_weather_api_key --task what is the weather in Singapore today?`

## Agent Design
When the user raises a task, the agent will perform the following step to complete it:

1. Merge the system prompt into the history manager.
2. Add the question or task to the history manager.
3. Using history to generate agent trajectory and input it into LLM.
4. LLM give the output contains tool using type or determine finish the task and give the final outcome.
5. If the LLM determine to use tool in the output message, the tool caller will choose the relevant tool and execute it with args.
6. Keep thinking and using tools until solve the task and updating the history and trajectory.
