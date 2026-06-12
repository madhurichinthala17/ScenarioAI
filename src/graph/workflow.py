from langgraph.graph import StateGraph, END
from src.models.state import ScenarioAIState
from src.agents.requirement_parser import RequirementParserAgent
from src.agents.gherkin_generator import GherkinGeneratorAgent

parser = RequirementParserAgent()
gherkin_agent = GherkinGeneratorAgent()


def requirement_parser_node(state: ScenarioAIState) -> dict:
    print("--- Requirement Parser ---")
    result = parser.run(state['requirement'])
    return {"parsed_requirement": result}


def gherkin_generator_node(state: ScenarioAIState) -> dict:
    print("--- Gherkin Generator ---")
    result = gherkin_agent.run(state['parsed_requirement'])
    return {"gherkin": result}


def build_graph():
    graph = StateGraph(ScenarioAIState)
    graph.add_node("requirement_parser", requirement_parser_node)
    graph.add_node("gherkin_generator", gherkin_generator_node)
    graph.set_entry_point("requirement_parser")
    graph.add_edge("requirement_parser", "gherkin_generator")
    graph.add_edge("gherkin_generator", END)
    return graph.compile()