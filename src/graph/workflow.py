from langgraph.graph import StateGraph, END
from src.models.state import ScenarioAIState
from src.agents.requirement_parser import RequirementParserAgent
from src.agents.gherkin_generator import GherkinGeneratorAgent
from src.agents.file_planner import FilePlannerAgent
from src.agents.pom_generator import POMGeneratorAgent
from src.agents.driver_generator import DriverGeneratorAgent

parser = RequirementParserAgent()
gherkin_agent = GherkinGeneratorAgent()
file_planner_agent = FilePlannerAgent()
pom_agent = POMGeneratorAgent()
driver_agent = DriverGeneratorAgent()


def requirement_parser_node(state: ScenarioAIState) -> dict:
    print("--- Requirement Parser ---")
    return {"parsed_requirement": parser.run(state['requirement'])}


def gherkin_generator_node(state: ScenarioAIState) -> dict:
    print("--- Gherkin Generator ---")
    return {"gherkin": gherkin_agent.run(state['parsed_requirement'])}


def file_planner_node(state: ScenarioAIState) -> dict:
    print("--- File Planner ---")
    return {"file_plan": file_planner_agent.run(state['gherkin'])}


def pom_generator_node(state: ScenarioAIState) -> dict:
    print("--- POM Generator ---")
    return {"pom_content": pom_agent.run(
        state['gherkin'],
        state['file_plan']['functionality']
    )}


def driver_generator_node(state: ScenarioAIState) -> dict:
    print("--- Driver Generator ---")
    return {"driver_content": driver_agent.run(
        state['gherkin'],
        state['file_plan']['functionality'],
        state['file_plan']['pages_file']
    )}


def build_graph():
    graph = StateGraph(ScenarioAIState)

    graph.add_node("requirement_parser", requirement_parser_node)
    graph.add_node("gherkin_generator", gherkin_generator_node)
    graph.add_node("file_planner", file_planner_node)
    graph.add_node("pom_generator", pom_generator_node)
    graph.add_node("driver_generator", driver_generator_node)

    graph.set_entry_point("requirement_parser")
    graph.add_edge("requirement_parser", "gherkin_generator")
    graph.add_edge("gherkin_generator", "file_planner")
    graph.add_edge("file_planner", "pom_generator")
    graph.add_edge("pom_generator", "driver_generator")
    graph.add_edge("driver_generator", END)

    return graph.compile()