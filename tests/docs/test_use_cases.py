import traceback
import json

from pytest import mark


@mark.docs
def test_single_value_string(project_result):
    assert project_result.exit_code == 0, "Command should complete successfully"
    assert 10 <= len(project_result.output.strip()) <= 12, "Length of string should be 8 - 10 chars long (plus quotes)"


@mark.docs
def test_single_value_integer(project_result):
    assert project_result.exit_code == 0, f"Command Errored: {project_result.exception}"
    gen_val = int(project_result.output)
    assert 5 <= gen_val <= 10, "Generated Integer should be between 5 and 10"


@mark.docs
def test_random_choice(project_result):
    assert project_result.exit_code == 0, "Command should complete successfully"
    assert project_result.output[:-1] in {'"red"', '"yellow"', '"blue"', '"orange"', '"green"', '"purple"'}, "Choice should be a colour"


@mark.docs
def test_single_value_object(project_result):
    if project_result.exit_code:
        traceback.print_tb(project_result.exc_info[2])
    assert project_result.exit_code == 0, f"Command Errored: {project_result.exception}\n{traceback.print_stack(project_result.exc_info)}"
    gen_obj = json.loads(project_result.output)
    assert (
        isinstance(gen_obj, dict), f"Expecting dict but got {type(gen_obj).__name__} instead",
    )
    assert len(gen_obj) == 4, "Each object should have 3 properties"
    assert "field_1" in gen_obj, "'field_1' should be an object in both sets"
    assert isinstance(gen_obj["field_1"], str)
    assert isinstance(gen_obj["field_2"], int)
    assert isinstance(gen_obj["field_3"], float)
    assert gen_obj["field_4"] in {"small", "medium", "large"}


@mark.docs
def test_multi_value_string(project_result):
    assert project_result.exit_code == 0, "Command should complete successfully"
    generated_lines = project_result.output[:-1].split("\n")
    assert len(generated_lines) == 5, "Should have generated 5 values"
    assert all([8 <= len(line) <= 22 for line in generated_lines])


@mark.docs
def test_static_ref_events(project_result):
    assert project_result.exit_code == 0, "Command should complete successfully"
    generated_lines = [
        json.loads(line) for line in project_result.output[:-1].split("\n")
    ]
    names = [ev["user_id"] for ev in generated_lines]
    timestamps = [ev["timestamp"] for ev in generated_lines]
    assert len(generated_lines) == 5, "Should have generated 5 values"
    assert all([name == "jdoe" for name in names])
    assert all([timestamps[a - 1] + 5 == timestamps[a] for a in range(1, len(timestamps))])


@mark.docs
def test_static_ref_random_start(project_result):
    assert project_result.exit_code == 0, "Command should complete successfully"
    generated_lines = [
        json.loads(line) for line in project_result.output[:-1].split("\n")
    ]
    names = [ev["user_id"] for ev in generated_lines]
    timestamps = [ev["timestamp"] for ev in generated_lines]
    assert len(generated_lines) == 5, "Should have generated 5 values"
    assert 3 <= len(names[0]) <= 6
    assert all([name == names[0] for name in names])
    assert all([timestamps[a - 1] + 5 == timestamps[a] for a in range(1, len(timestamps))])


@mark.docs
def test_seq_format_string(project_result):
    assert project_result.exit_code == 0, "Command should complete successfully"
    generated_lines = [
        json.loads(line) for line in project_result.output[:-1].split("\n")
    ]
    assert all([ev.endswith("-test") for ev in generated_lines])
    assert all([len(ev) == 10 for ev in generated_lines])


@mark.docs
def test_cond_status_change(project_result):
    assert project_result.exit_code == 0, "Command should complete successfully"
    generated_lines = [
        json.loads(line) for line in project_result.output[:-1].split("\n")
    ]
    assert all([ev["ref"] == "status" for ev in generated_lines])
    below, above = [], []
    ranges = (below, above)
    for ev in generated_lines:
        ranges[ev["sensor"] > 5].append(ev)
    assert len(below) > 1
    assert len(above) > 1
    assert all([
        ev["status"] == "below" for ev in below
    ]), "Status should report 'below' when Sensor value is less than 6"
    assert all([
        ev["status"] == "above" for ev in above
    ]), "Status should report 'above' when sensor value is greater than 5"
    print(generated_lines)
    # TODO: Fix Dependency Management
