import dotscience

import json
import datetime
import re
import io
import os
import sys

from hypothesis import given, assume, note
from hypothesis.strategies import text, lists

###
### Test the Run class
###

def test_run_null():
    r = dotscience.Run()
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]{
    "input": [],
    "labels": {},
    "output": [],
    "parameters": {},
    "summary": {},
    "version": "1"
}[[/DOTSCIENCE-RUN:%s]]""" % (r._id, r._id)

@given(text(),text())
def test_run_basics(error, description):
    r = dotscience.Run()
    r._set_workload_file('nonsense.py')
    assert r.error(error) == error
    assert r.description(description) == description
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]{
    "description": %s,
    "error": %s,
    "input": [],
    "labels": {},
    "output": [],
    "parameters": {},
    "summary": {},
    "version": "1",
    "workload-file": "nonsense.py"
}[[/DOTSCIENCE-RUN:%s]]""" % (r._id, json.dumps(description), json.dumps(error), r._id)

@given(text())
def test_run_input_1(x):
    r = dotscience.Run()
    assert r.input(x) == x
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "summary": {},
                        "parameters": {},
                        "output": [],
                        "input": [os.path.normpath(x)],
                        "labels": {},
    }, sort_keys=True, indent=4), r._id)

@given(lists(text(min_size=1), min_size=2, max_size=2, unique=True))
def test_run_input_2(x):
    r = dotscience.Run()
    r.add_input(x[0])
    r.add_input(x[1])
    x = set([os.path.normpath(y) for y in x])
    len(r._inputs) == len(x) and sorted(r._inputs) == sorted(x)

@given(lists(text(min_size=1), unique=True))
def test_run_input_n(x):
    x = set([os.path.normpath(y) for y in x])
    r = dotscience.Run()
    r.add_inputs(*x)
    len(r._inputs) == len(x) and sorted(r._inputs) == sorted(x)

@given(text())
def test_run_output_1(x):
    r = dotscience.Run()
    assert r.output(x) == x
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "summary": {},
                        "parameters": {},
                        "input": [],
                        "output": [os.path.normpath(x)],
                        "labels": {},
    }, sort_keys=True, indent=4), r._id)

@given(lists(text(min_size=1), min_size=2, max_size=2, unique=True))
def test_run_output_2(data):
    r = dotscience.Run()
    r.add_output(data[0])
    r.add_output(data[1])
    data = set([os.path.normpath(x) for x in data])
    len(r._outputs) == len(data) and sorted(r._outputs) == sorted(data)

@given(lists(text(min_size=1), unique=True))
def test_run_output_n(data):
    data = set([os.path.normpath(x) for x in data])
    r = dotscience.Run()
    r.add_outputs(*data)
    len(r._outputs) == len(data) and sorted(r._outputs) == sorted(data)

@given(text())
def test_run_labels_1(x):
    r = dotscience.Run()
    assert r.label("food", x) == x
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "summary": {},
                        "parameters": {},
                        "input": [],
                        "output": [],
                        "labels": {"food": x},
    }, sort_keys=True, indent=4), r._id)

@given(text(),text(),text(),text())
def test_run_labels_multi(a,b,c,d):
    r = dotscience.Run()
    r.add_labels("a", a)
    r.add_labels(b=b)
    r.add_labels("c", c, d=d)
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "summary": {},
                        "parameters": {},
                        "input": [],
                        "output": [],
                        "labels": {"a": a, "b": b, "c": c, "d": d},
    }, sort_keys=True, indent=4), r._id)

@given(text())
def test_run_summary_1(x):
    r = dotscience.Run()
    assert r.summary("food", x) == x
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "labels": {},
                        "parameters": {},
                        "input": [],
                        "output": [],
                        "summary": {"food": x},
    }, sort_keys=True, indent=4), r._id)

@given(text(),text(),text(),text())
def test_run_summary_multi(a,b,c,d):
    r = dotscience.Run()
    r.add_summaries("a", a)
    r.add_summaries(b=b)
    r.add_summaries("c", c, d=d)
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "labels": {},
                        "parameters": {},
                        "input": [],
                        "output": [],
                        "summary": {"a": a, "b": b, "c": c, "d": d},
    }, sort_keys=True, indent=4), r._id)

@given(text())
def test_run_parameter_1(x):
    r = dotscience.Run()
    assert r.parameter("food", x) == x
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "labels": {},
                        "summary": {},
                        "input": [],
                        "output": [],
                        "parameters": {"food": x},
    }, sort_keys=True, indent=4), r._id)

@given(text(),text(),text(),text())
def test_run_parameter_multi(a,b,c,d):
    r = dotscience.Run()
    r.add_parameters("a", a)
    r.add_parameters(b=b)
    r.add_parameters("c", c, d=d)
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "labels": {},
                        "summary": {},
                        "input": [],
                        "output": [],
                        "parameters": {"a": a, "b": b, "c": c, "d": d},
    }, sort_keys=True, indent=4), r._id)

def test_run_start_1():
    r = dotscience.Run()
    r.start()
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "labels": {},
                        "summary": {},
                        "input": [],
                        "output": [],
                        "parameters": {},
                        "start": r._start.strftime("%Y%m%dT%H%M%S.%f"),
    }, sort_keys=True, indent=4), r._id)

def test_run_start_2():
    r = dotscience.Run()
    r.start()
    try:
        r.start()
    except RuntimeError:
        return True
    else:
        assert 'Did not get a RuntimeError when attempting to start a run twice'

def test_run_end_1():
    r = dotscience.Run()
    r.end()
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "labels": {},
                        "summary": {},
                        "input": [],
                        "output": [],
                        "parameters": {},
                        "end": r._end.strftime("%Y%m%dT%H%M%S.%f"),
    }, sort_keys=True, indent=4), r._id)

def test_run_end_2():
    r = dotscience.Run()
    r.end()
    time1 = r._end
    # Assume clock has enough resolution to not return the same timestamp for a second call to r.end()
    assume(time1 != datetime.datetime.utcnow())
    r.end()
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "labels": {},
                        "summary": {},
                        "input": [],
                        "output": [],
                        "parameters": {},
                        "end": time1.strftime("%Y%m%dT%H%M%S.%f"),
    }, sort_keys=True, indent=4), r._id)

###
### Utils for testing output JSON
###

METADATA_RE = re.compile(r"\[\[DOTSCIENCE-RUN:(.+)\]\](.*)\[\[/DOTSCIENCE-RUN:\1\]\]", re.MULTILINE + re.DOTALL)
def _parse(metadata):
    m = METADATA_RE.match(metadata)
    if not m:
        note("Regexp didn't match %r" % (metadata,))
        assert False
    meta = json.loads(m.group(2))
    assert meta["version"] == "1"
    # Capture the run ID
    meta["__ID"] = m.group(1)
    return meta

TEST_WORKLOAD_FILE = "made_up_test_script.py"

###
### Test the interactive/script mode switching in the Dotscience class
###

def test_no_mode():
    ds = dotscience.Dotscience()
    try:
        ds.publish()
    except RuntimeError:
        return True
    else:
        assert 'Did not get a RuntimeError when attempting to publish without choosing a mode'

def test_conflicting_mode_1():
    ds = dotscience.Dotscience()
    try:
        ds.interactive()
        ds.script()
    except RuntimeError:
        return True
    else:
        assert 'Did not get a RuntimeError when attempting to conflict modes'

def test_conflicting_mode_2():
    ds = dotscience.Dotscience()
    try:
        ds.script()
        ds.interactive()
    except RuntimeError:
        return True
    else:
        assert 'Did not get a RuntimeError when attempting to conflict modes'

def test_non_conflicting_mode_1():
    ds = dotscience.Dotscience()
    ds.script()
    ds.script()
    ds.publish()

def test_non_conflicting_mode_2():
    ds = dotscience.Dotscience()
    ds.interactive()
    ds.interactive()
    ds.publish()

def test_no_script_name_when_interactive():
    ds = dotscience.Dotscience()
    ds.interactive()
    s1=io.StringIO()
    ds.publish("Hello", stream=s1)
    m1 = _parse(s1.getvalue())

    assert "workload-file" not in m1

def test_default_script_name():
    ds = dotscience.Dotscience()
    ds.script()
    s1=io.StringIO()
    ds.publish("Hello", stream=s1)
    m1 = _parse(s1.getvalue())

    # This might be a fragile assertion...
    assert m1["workload-file"] == "/usr/local/bin/pytest"

def test_explicit_script_name():
    ds = dotscience.Dotscience()
    ds.script(TEST_WORKLOAD_FILE)
    s1=io.StringIO()
    ds.publish("Hello", stream=s1)
    m1 = _parse(s1.getvalue())

    assert m1["workload-file"] == TEST_WORKLOAD_FILE

###
### Test the module-level methods, indirectly testing the Dotscience class
###

# All these tests assume script mode

dotscience.script(TEST_WORKLOAD_FILE)

def test_null():
    s=io.StringIO()
    dotscience.start()
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

# How to test auto_end? The currentRun object is reset by publish() so we have no way to get the value. Parse it back and confirm it's between a saved dotscience._defaultDS.currentRun._start and now?

def test_start_end():
    s=io.StringIO()
    dotscience.start()
    t1 = dotscience._defaultDS.currentRun._start
    dotscience.end()
    t2 = dotscience._defaultDS.currentRun._end
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["start"] == t1.strftime("%Y%m%dT%H%M%S.%f")
    assert m["end"] == t2.strftime("%Y%m%dT%H%M%S.%f")
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_description_a(d):
    s=io.StringIO()
    dotscience.start()
    dotscience.publish(stream=s, description=d)
    m = _parse(s.getvalue())
    assert m["description"] == d
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_description_b(d):
    s=io.StringIO()
    dotscience.start()
    dotscience.set_description(d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["description"] == d
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_description_c(d):
    s=io.StringIO()
    dotscience.start()
    assert dotscience.description(d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["description"] == d
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_error_a(d):
    s=io.StringIO()
    dotscience.start()
    assert dotscience.error(d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["error"] == d
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_error_b(d):
    s=io.StringIO()
    dotscience.start()
    dotscience.set_error(d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["error"] == d
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_input_1a(d):
    s=io.StringIO()
    dotscience.start()
    dotscience.add_input(d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["input"] == [os.path.normpath(d)]
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_input_1b(d):
    s=io.StringIO()
    dotscience.start()
    assert dotscience.input(d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["input"] == [os.path.normpath(d)]
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(lists(text(min_size=1), unique=True))
def test_input_n(d):
    d = set([os.path.normpath(x) for x in d])
    s=io.StringIO()
    dotscience.start()
    dotscience.add_inputs(*d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert len(m["input"]) == len(d) and sorted(m["input"]) == sorted(d)
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_output_1a(d):
    s=io.StringIO()
    dotscience.start()
    dotscience.add_output(d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == [os.path.normpath(d)]
    assert m["input"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_output_1b(d):
    s=io.StringIO()
    dotscience.start()
    assert dotscience.output(d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == [os.path.normpath(d)]
    assert m["input"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(lists(text(min_size=1), unique=True))
def test_output_n(d):
    d = set([os.path.normpath(x) for x in d])
    s=io.StringIO()
    dotscience.start()
    dotscience.add_outputs(*d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert len(m["output"]) == len(d) and sorted(m["output"]) == sorted(d)
    assert m["input"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_label_1a(d):
    s=io.StringIO()
    dotscience.start()
    dotscience.add_label("test", d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["labels"] == {"test": d}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_label_1b(d):
    s=io.StringIO()
    dotscience.start()
    assert dotscience.label("test", d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["labels"] == {"test": d}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text(),text())
def test_label_n(a, b):
    s=io.StringIO()
    dotscience.start()
    dotscience.add_labels("a", a)
    dotscience.add_labels(b=b)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["labels"] == {"a": a, "b": b}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_summary_1a(d):
    s=io.StringIO()
    dotscience.start()
    dotscience.add_summary("test", d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["summary"] == {"test": d}
    assert m["parameters"] == {}
    assert m["labels"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_summary_1b(d):
    s=io.StringIO()
    dotscience.start()
    assert dotscience.summary("test", d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["summary"] == {"test": d}
    assert m["parameters"] == {}
    assert m["labels"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text(),text())
def test_summary_n(a, b):
    s=io.StringIO()
    dotscience.start()
    dotscience.add_summaries("a", a)
    dotscience.add_summaries(b=b)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["summary"] == {"a": a, "b": b}
    assert m["parameters"] == {}
    assert m["labels"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_parameter_1a(d):
    s=io.StringIO()
    dotscience.start()
    dotscience.add_parameter("test", d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["parameters"] == {"test": d}
    assert m["labels"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text())
def test_parameter_1b(d):
    s=io.StringIO()
    dotscience.start()
    assert dotscience.parameter("test", d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["parameters"] == {"test": d}
    assert m["labels"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(text(),text())
def test_parameter_n(a, b):
    s=io.StringIO()
    dotscience.start()
    dotscience.add_parameters("a", a)
    dotscience.add_parameters(b=b)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["parameters"] == {"a": a, "b": b}
    assert m["labels"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

def test_multi_publish_1():
    s1=io.StringIO()
    dotscience.start()
    dotscience.publish("Hello", stream=s1)
    s2=io.StringIO()
    dotscience.publish("World", stream=s2)
    m1 = _parse(s1.getvalue())
    m2 = _parse(s2.getvalue())

    assert m1["description"] == "Hello"
    assert m2["description"] == "World"
    assert m1["__ID"] != m2["__ID"]
    assert m1["start"] == m2["start"]
    assert m1["end"] == m2["end"]

def test_multi_publish_2():
    s1=io.StringIO()
    dotscience.start()
    dotscience.publish("Hello", stream=s1)
    s2=io.StringIO()
    dotscience.start()
    dotscience.publish("World", stream=s2)
    m1 = _parse(s1.getvalue())
    m2 = _parse(s2.getvalue())

    assert m1["description"] == "Hello"
    assert m2["description"] == "World"
    assert m1["__ID"] != m2["__ID"]
    assert m1["start"] != m2["start"]
    assert m1["end"] != m2["end"]
