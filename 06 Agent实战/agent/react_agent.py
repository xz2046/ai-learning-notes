"""业务运维排查助手的 ReAct Agent — 集成工具调用与流式输出"""

from collections.abc import Generator

from langchain.agents import create_agent

from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools import get_all_tools
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch


class ReactAgent():
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=get_all_tools(),
            middleware=[monitor_tool, log_before_model, report_prompt_switch]
        )

    def execute_stream(self, query: str) -> Generator[str, None, None]:
        input_dict = {
            "messages": [
                {"role": "user", "content": query}
            ]
        }

        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            if latest_message:
                yield latest_message.content.strip() + "\n"

