from __future__ import annotations

import os
from typing import Dict, List, TYPE_CHECKING

import yaml
from agentverse.logging import logger

# BMTools support removed - not needed for your configuration

from agentverse.llms import llm_registry

from agentverse.agents import agent_registry
from agentverse.environments import BaseEnvironment, env_registry
from agentverse.memory import memory_registry
from agentverse.memory_manipulator import memory_manipulator_registry

from agentverse.output_parser import output_parser_registry

if TYPE_CHECKING:
    from agentverse.agents import BaseAgent


def load_llm(llm_config: Dict):
    llm_type = llm_config.pop("llm_type", "text-davinci-003")

    return llm_registry.build(llm_type, **llm_config)


def load_memory(memory_config: Dict):
    memory_type = memory_config.pop("memory_type", "chat_history")
    return memory_registry.build(memory_type, **memory_config)


def load_memory_manipulator(memory_manipulator_config: Dict):
    memory_manipulator_type = memory_manipulator_config.pop(
        "memory_manipulator_type", "basic"
    )
    return memory_manipulator_registry.build(
        memory_manipulator_type, **memory_manipulator_config
    )


def load_tools(tool_config: List[Dict]):
    """Load tools based on configuration. Simplified to only include tools used in config."""
    if len(tool_config) == 0:
        return []
    
    all_tools_list = []
    for tool_dict in tool_config:
        # Check if it's a custom tool function
        if "tool_url" not in tool_dict:
            tool_name = tool_dict["tool_name"]
            
            # Only include tools actually used in your configuration
            if tool_name == "semantic_scholar_search":
                from agentverse.tools.ai_researcher_tools import semantic_scholar_search
                from langchain.tools import tool
                
                @tool
                def semantic_scholar_search_tool(query: str, limit: int = 10) -> str:
                    """Direct Semantic Scholar API search for papers"""
                    return semantic_scholar_search(query, limit)
                
                semantic_scholar_search_tool.name = "semantic_scholar_search"
                semantic_scholar_search_tool.description = tool_dict.get("description", "Direct Semantic Scholar API search")
                all_tools_list.append(semantic_scholar_search_tool)
                
            elif tool_name == "get_paper_details":
                from agentverse.tools.ai_researcher_tools import GetPaperDetailsTool
                
                tool_instance = GetPaperDetailsTool()
                tool_instance.description = tool_dict.get("description", "Get comprehensive paper details")
                all_tools_list.append(tool_instance)
                
            else:
                # Log warning for unsupported tools
                logger.warning(f"Unsupported tool: {tool_name}. Only semantic_scholar_search and get_paper_details are supported.")
    
    return all_tools_list


def load_environment(env_config: Dict) -> BaseEnvironment:
    env_type = env_config.pop("env_type", "basic")
    return env_registry.build(env_type, **env_config)


def load_agent(agent_config: Dict) -> BaseAgent:
    agent_type = agent_config.pop("agent_type", "conversation")
    agent = agent_registry.build(agent_type, **agent_config)
    return agent


def prepare_task_config(task, tasks_dir):
    """Read the yaml config of the given task in `tasks` directory."""
    all_task_dir = tasks_dir
    task_path = os.path.join(all_task_dir, task)
    config_path = os.path.join(task_path, "config.yaml")
    if not os.path.exists(task_path):
        all_tasks = []
        for task in os.listdir(all_task_dir):
            if (
                os.path.isdir(os.path.join(all_task_dir, task))
                and task != "__pycache__"
            ):
                all_tasks.append(task)
                for subtask in os.listdir(os.path.join(all_task_dir, task)):
                    if (
                        os.path.isdir(os.path.join(all_task_dir, task, subtask))
                        and subtask != "__pycache__"
                    ):
                        all_tasks.append(f"{task}/{subtask}")
        raise ValueError(f"Task {task} not found. Available tasks: {all_tasks}")
    if not os.path.exists(config_path):
        raise ValueError(
            "You should include the config.yaml file in the task directory"
        )
    task_config = yaml.safe_load(open(config_path, encoding="utf-8"))

    for i, agent_configs in enumerate(task_config["agents"]):
        agent_configs["memory"] = load_memory(agent_configs.get("memory", {}))
        


        if agent_configs.get("tool_memory", None) is not None:
            agent_configs["tool_memory"] = load_memory(agent_configs["tool_memory"])
        llm = load_llm(agent_configs.get("llm", "text-davinci-003"))
        agent_configs["llm"] = llm

        memory_manipulator = load_memory_manipulator(
            agent_configs.get("memory_manipulator", {})
        )
        agent_configs["memory_manipulator"] = memory_manipulator

        agent_configs["tools"] = load_tools(agent_configs.get("tools", []))

        # Build the output parser
        output_parser_config = agent_configs.get("output_parser", {"type": "dummy"})
        output_parser_name = output_parser_config.pop("type", task)
        agent_configs["output_parser"] = output_parser_registry.build(
            output_parser_name, **output_parser_config
        )

    return task_config
