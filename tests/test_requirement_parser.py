from src.agents.requirement_parser import RequirementParserAgent

agent = RequirementParserAgent()

def test_output_has_required_fields():
    result = agent.run("User logs in with valid credentials and sees the dashboard")
    assert "actor" in result
    assert "action" in result
    assert "preconditions" in result
    assert "expected_result" in result
    assert "edge_cases" in result

def test_output_types_are_correct():
    result = agent.run("User logs in with valid credentials and sees the dashboard")
    assert isinstance(result["actor"], str)
    assert isinstance(result["action"], str)
    assert isinstance(result["preconditions"], list)
    assert isinstance(result["expected_result"], str)
    assert isinstance(result["edge_cases"], list)

def test_actor_is_not_empty():
    result = agent.run("User logs in with valid credentials and sees the dashboard")
    assert len(result["actor"]) > 0