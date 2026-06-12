from langgraph.graph import StateGraph, END
from src.models.state import ScenarioAIState
from src.agents.requirement_parser import RequirementParserAgent
from src.agents.gherkin_generator import GherkinGeneratorAgent
from src.agents.file_planner import FilePlannerAgent

parser = RequirementParserAgent()
gherkin_agent = GherkinGeneratorAgent()
file_planner_agent = FilePlannerAgent()


def requirement_parser_node(state: ScenarioAIState) -> dict:
    print("--- Requirement Parser ---")
    result = parser.run(state['requirement'])
    return {"parsed_requirement": result}


def gherkin_generator_node(state: ScenarioAIState) -> dict:
    print("--- Gherkin Generator ---")
    result = gherkin_agent.run(state['parsed_requirement'])
    return {"gherkin": result}


def file_planner_node(state: ScenarioAIState) -> dict:
    print("--- File Planner ---")
    result = file_planner_agent.run(state['gherkin'])
    return {"file_plan": result}


def build_graph():
    graph = StateGraph(ScenarioAIState)

    graph.add_node("requirement_parser", requirement_parser_node)
    graph.add_node("gherkin_generator", gherkin_generator_node)
    graph.add_node("file_planner", file_planner_node)
    graph.set_entry_point("requirement_parser")
    graph.add_edge("requirement_parser", "gherkin_generator")
    graph.add_edge("gherkin_generator", "file_planner")
    graph.add_edge("file_planner", END)

    return graph.compile()