from agent_core import run_agent
from langchain_core.messages import HumanMessage


def test_agent_run_returns_state():
    inputs = {"messages": [HumanMessage(content="Test topic for agent") ]}
    final = run_agent(inputs)
    # final should be a dict and contain either messages or state
    assert isinstance(final, dict)
