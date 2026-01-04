"""CLI to run the Deep Research Agent from the command line."""
import argparse
from agent_core import run_agent
from langchain_core.messages import HumanMessage


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("topic", type=str, help="Research topic to run")
    return p.parse_args()


def main():
    cfg = parse_args()
    inputs = {"messages": [HumanMessage(content=cfg.topic)]}
    final = run_agent(inputs)
    if "messages" in final:
        print(final["messages"][-1].content)
    else:
        print(final)


if __name__ == "__main__":
    main()
