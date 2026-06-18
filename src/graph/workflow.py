from langgraph.graph import StateGraph, END

from src.models.state import ScenarioAIState
from src.agents.requirement_parser import RequirementParserAgent
from src.agents.gherkin_generator import GherkinGeneratorAgent
from src.agents.file_planner import FilePlannerAgent
from src.agents.pom_generator import POMGeneratorAgent
from src.agents.driver_generator import DriverGeneratorAgent
from src.agents.stepdefinition_generator import StepDefinitionGeneratorAgent
from src.agents.validator import ValidatorAgent
from src.agents.file_writer import FileWriterAgent
from src.config import settings
from src.core.logger import get_logger

log = get_logger(__name__)


def should_retry(state: ScenarioAIState) -> str:
    if state["validation_passed"]:
        return "file_writer"
    if state.get("retry_count", 0) >= settings.max_retries:
        log.warning("Max retries (%d) reached — ending with validation errors", settings.max_retries)
        return "end"
    failed = state.get("failed_agent")
    if failed:
        log.info("Retrying from node: %s", failed)
        return failed
    return "end"


def build_graph():
    parser            = RequirementParserAgent()
    gherkin_agent     = GherkinGeneratorAgent()
    file_planner_agent = FilePlannerAgent()
    pom_agent         = POMGeneratorAgent()
    driver_agent      = DriverGeneratorAgent()
    step_agent        = StepDefinitionGeneratorAgent()
    validator         = ValidatorAgent()
    file_writer       = FileWriterAgent()

    # ── Node functions (closures over the agents above) ───────────────────

    def requirement_parser_node(state: ScenarioAIState) -> dict:
        log.info("Node: requirement_parser")
        return {"parsed_requirement": parser.run(state["requirement"])}

    def gherkin_generator_node(state: ScenarioAIState) -> dict:
        log.info("Node: gherkin_generator")
        return {"gherkin": gherkin_agent.run(state["parsed_requirement"])}

    def file_planner_node(state: ScenarioAIState) -> dict:
        log.info("Node: file_planner")
        return {"file_plan": file_planner_agent.run(state["gherkin"])}

    def pom_generator_node(state: ScenarioAIState) -> dict:
        log.info("Node: pom_generator")
        return {"pom_content": pom_agent.run(
            state["gherkin"],
            state["file_plan"]["functionality"],
        )}

    def driver_generator_node(state: ScenarioAIState) -> dict:
        log.info("Node: driver_generator")
        return {"driver_content": driver_agent.run(
            state["gherkin"],
            state["file_plan"]["functionality"],
            state["file_plan"]["pages_file"],
        )}

    def step_definition_generator_node(state: ScenarioAIState) -> dict:
        log.info("Node: step_definition_generator")
        return {"steps_content": step_agent.run(
            state["gherkin"],
            state["pom_content"],
            state["driver_content"],
            state["file_plan"],
        )}

    def validator_node(state: ScenarioAIState) -> dict:
        log.info("Node: validator")
        result = validator.run(
            state["gherkin"],
            state["pom_content"],
            state["driver_content"],
            state["steps_content"],
        )

        failed_agent = None
        if not result["passed"]:
            errors = result["errors"]
            if any("POM" in e or "Method existence" in e for e in errors):
                failed_agent = "pom_generator"
            elif any("Driver existence" in e for e in errors):
                failed_agent = "driver_generator"
            elif any("Step coverage" in e or "Phase 2" in e for e in errors):
                failed_agent = "step_definition_generator"
            elif any("Gherkin" in e for e in errors):
                failed_agent = "gherkin_generator"

        return {
            "validation_passed": result["passed"],
            "validation_errors": result["errors"],
            "validation_phase": result.get("phase", 1),
            "failed_agent": failed_agent,
            "retry_count": 0 if result["passed"] else 1,
        }

    def file_writer_node(state: ScenarioAIState) -> dict:
        log.info("Node: file_writer")
        return file_writer.run(state)

    # ── Build and compile the graph ───────────────────────────────────────

    graph = StateGraph(ScenarioAIState)

    graph.add_node("requirement_parser",        requirement_parser_node)
    graph.add_node("gherkin_generator",          gherkin_generator_node)
    graph.add_node("file_planner",               file_planner_node)
    graph.add_node("pom_generator",              pom_generator_node)
    graph.add_node("driver_generator",           driver_generator_node)
    graph.add_node("step_definition_generator",  step_definition_generator_node)
    graph.add_node("validator",                  validator_node)
    graph.add_node("file_writer",                file_writer_node)

    graph.set_entry_point("requirement_parser")
    graph.add_edge("requirement_parser",       "gherkin_generator")
    graph.add_edge("gherkin_generator",         "file_planner")
    graph.add_edge("file_planner",              "pom_generator")
    graph.add_edge("pom_generator",             "driver_generator")
    graph.add_edge("driver_generator",          "step_definition_generator")
    graph.add_edge("step_definition_generator", "validator")
    graph.add_edge("file_writer",               END)

    graph.add_conditional_edges(
        "validator",
        should_retry,
        {
            "file_writer":               "file_writer",
            "end":                       END,
            "pom_generator":             "pom_generator",
            "driver_generator":          "driver_generator",
            "step_definition_generator": "step_definition_generator",
            "gherkin_generator":         "gherkin_generator",
        },
    )

    return graph.compile()
