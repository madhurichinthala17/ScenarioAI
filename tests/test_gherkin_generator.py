from src.agents.gherkin_generator import GherkinGeneratorAgent

agent = GherkinGeneratorAgent()

sample_parsed = {
    "actor": "User",
    "action": "Login",
    "preconditions": ["User has a valid email and password"],
    "expected_result": "Redirected to the dashboard",
    "edge_cases": [
        "Invalid email or password: Error message displayed",
        "Empty fields: Form shows validation error"
    ]
}

def test_output_contains_feature():
    result = agent.run(sample_parsed)
    assert "Feature:" in result

def test_output_contains_scenario():
    result = agent.run(sample_parsed)
    assert "Scenario:" in result

def test_output_contains_given_when_then():
    result = agent.run(sample_parsed)
    assert "Given" in result
    assert "When" in result
    assert "Then" in result

def test_happy_path_scenario_present():
    result = agent.run(sample_parsed)
    assert "dashboard" in result.lower()

def test_edge_cases_covered():
    result = agent.run(sample_parsed)
    assert "Invalid" in result or "invalid" in result