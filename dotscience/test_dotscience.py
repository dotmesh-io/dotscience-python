import dotscience

import json
import datetime
import re
import io

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
    "version": "1"
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
                        "input": [x],
                        "labels": {}
    }, sort_keys=True, indent=4), r._id)

@given(text(), text())
def test_run_input_2(x, y):
    r = dotscience.Run()
    r.add_input(x)
    r.add_input(y)
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "summary": {},
                        "parameters": {},
                        "output": [],
                        "input": [x,y],
                        "labels": {}
    }, sort_keys=True, indent=4), r._id)

@given(lists(text()))
def test_run_input_n(x):
    r = dotscience.Run()
    r.add_inputs(*x)
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "summary": {},
                        "parameters": {},
                        "output": [],
                        "input": x,
                        "labels": {}
    }, sort_keys=True, indent=4), r._id)

@given(text())
def test_run_output_1(x):
    r = dotscience.Run()
    assert r.output(x) == x
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "summary": {},
                        "parameters": {},
                        "input": [],
                        "output": [x],
                        "labels": {}
    }, sort_keys=True, indent=4), r._id)

@given(text(), text())
def test_run_output_2(x, y):
    r = dotscience.Run()
    r.add_output(x)
    r.add_output(y)
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "summary": {},
                        "parameters": {},
                        "input": [],
                        "output": [x,y],
                        "labels": {}
    }, sort_keys=True, indent=4), r._id)

@given(lists(text()))
def test_run_output_n(x):
    r = dotscience.Run()
    r.add_outputs(*x)
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "summary": {},
                        "parameters": {},
                        "input": [],
                        "output": x,
                        "labels": {}
    }, sort_keys=True, indent=4), r._id)

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
                        "labels": {"food": x}
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
                        "labels": {"a": a, "b": b, "c": c, "d": d}
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
                        "summary": {"food": x}
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
                        "summary": {"a": a, "b": b, "c": c, "d": d}
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
                        "parameters": {"food": x}
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
                        "parameters": {"a": a, "b": b, "c": c, "d": d}
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
                        "start": r._start.strftime("%Y%m%dT%H%M%S.%f")
    }, sort_keys=True, indent=4), r._id)

def test_run_start_2():
    r = dotscience.Run()
    r.start()
    time1 = r._start
    r.start()
    # Assume clock has enough resolution that the two calls to start() don't get the same timestamp anyway
    assume(time1 != r._start)
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "labels": {},
                        "summary": {},
                        "input": [],
                        "output": [],
                        "parameters": {},
                        "start": r._start.strftime("%Y%m%dT%H%M%S.%f")
    }, sort_keys=True, indent=4), r._id)

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
                        "end": r._end.strftime("%Y%m%dT%H%M%S.%f")
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
                        "end": time1.strftime("%Y%m%dT%H%M%S.%f")
    }, sort_keys=True, indent=4), r._id)

###
### Test the module-level methods, indirectly testing the Dotscience class
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

def test_null():
    s=io.StringIO()
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}

def test_auto_start():
    s=io.StringIO()
    t = dotscience._defaultDS.currentRun._start
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["start"] == t.strftime("%Y%m%dT%H%M%S.%f")
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}

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

@given(text())
def test_description_a(d):
    s=io.StringIO()
    dotscience.publish(stream=s, description=d)
    m = _parse(s.getvalue())
    assert m["description"] == d
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(text())
def test_description_b(d):
    s=io.StringIO()
    dotscience.set_description(d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["description"] == d
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(text())
def test_description_c(d):
    s=io.StringIO()
    assert dotscience.description(d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["description"] == d
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(text())
def test_error_a(d):
    s=io.StringIO()
    assert dotscience.error(d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["error"] == d
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(text())
def test_error_b(d):
    s=io.StringIO()
    dotscience.set_error(d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["error"] == d
    assert m["input"] == []
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(text())
def test_input_1a(d):
    s=io.StringIO()
    dotscience.add_input(d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["input"] == [d]
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(text())
def test_input_1b(d):
    s=io.StringIO()
    assert dotscience.input(d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["input"] == [d]
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(lists(text()))
def test_input_n(d):
    s=io.StringIO()
    dotscience.add_inputs(*d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["input"] == d
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(text())
def test_output_1a(d):
    s=io.StringIO()
    dotscience.add_output(d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == [d]
    assert m["input"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(text())
def test_output_1b(d):
    s=io.StringIO()
    assert dotscience.output(d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == [d]
    assert m["input"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(lists(text()))
def test_output_n(d):
    s=io.StringIO()
    dotscience.add_outputs(*d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == d
    assert m["input"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(text())
def test_label_1a(d):
    s=io.StringIO()
    dotscience.add_label("test", d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["labels"] == {"test": d}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(text())
def test_label_1b(d):
    s=io.StringIO()
    assert dotscience.label("test", d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["labels"] == {"test": d}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(text(),text())
def test_label_n(a, b):
    s=io.StringIO()
    dotscience.add_labels("a", a)
    dotscience.add_labels(b=b)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["labels"] == {"a": a, "b": b}
    assert m["parameters"] == {}
    assert m["summary"] == {}

@given(text())
def test_summary_1a(d):
    s=io.StringIO()
    dotscience.add_summary("test", d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["summary"] == {"test": d}
    assert m["parameters"] == {}
    assert m["labels"] == {}

@given(text())
def test_summary_1b(d):
    s=io.StringIO()
    assert dotscience.summary("test", d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["summary"] == {"test": d}
    assert m["parameters"] == {}
    assert m["labels"] == {}

@given(text(),text())
def test_summary_n(a, b):
    s=io.StringIO()
    dotscience.add_summaries("a", a)
    dotscience.add_summaries(b=b)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["summary"] == {"a": a, "b": b}
    assert m["parameters"] == {}
    assert m["labels"] == {}

@given(text())
def test_parameter_1a(d):
    s=io.StringIO()
    dotscience.add_parameter("test", d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["parameters"] == {"test": d}
    assert m["labels"] == {}
    assert m["summary"] == {}

@given(text())
def test_parameter_1b(d):
    s=io.StringIO()
    assert dotscience.parameter("test", d) == d
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["parameters"] == {"test": d}
    assert m["labels"] == {}
    assert m["summary"] == {}

@given(text(),text())
def test_parameter_n(a, b):
    s=io.StringIO()
    dotscience.add_parameters("a", a)
    dotscience.add_parameters(b=b)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == []
    assert m["input"] == []
    assert m["parameters"] == {"a": a, "b": b}
    assert m["labels"] == {}
    assert m["summary"] == {}

def test_multi_publish():
    s1=io.StringIO()
    dotscience.publish("Hello", stream=s1)
    s2=io.StringIO()
    dotscience.publish("World", stream=s2)
    m1 = _parse(s1.getvalue())
    m2 = _parse(s2.getvalue())

    assert m1["description"] == "Hello"
    assert m2["description"] == "World"
    assert m1["__ID"] != m2["__ID"]
    assert m1["start"] != m2["start"]
    assert m1["end"] != m2["end"]
