import dotscience

import json
import datetime
import re
import io
import os
import sys
import shutil

from hypothesis import given, assume, note
from hypothesis.strategies import text, lists, sampled_from

###
### Test the Run class
###

def test_run_null():
    r = dotscience.Run("/workspace-root")
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]{
    "input": [],
    "labels": {},
    "output": [],
    "parameters": {},
    "summary": {},
    "version": "1"
}[[/DOTSCIENCE-RUN:%s]]""" % (r._id, r._id)

input_files=["test.csv","/workspace-root/test.csv","data/test.csv"]
output_files=["test.csv","/workspace-root/test.csv","data/test.csv"]
    
@given(text(),text())
def test_run_basics(error, description):
    r = dotscience.Run("/workspace-root")
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

def tidy_path(p):
    return os.path.normpath(p.replace("\x00"," "))

@given(sampled_from(input_files))
def test_run_input_1(x):
    r = dotscience.Run("/workspace-root")
    xpath = tidy_path("/workspace-root/" + x)
    assert r.input(xpath) == xpath
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "summary": {},
                        "parameters": {},
                        "output": [],
                        "input": [os.path.relpath(xpath,start="/workspace-root")],
                        "labels": {},
    }, sort_keys=True, indent=4), r._id)

def test_run_input_relative():
    orig_dir = os.getcwd()
    r = dotscience.Run(orig_dir)
    os.mkdir("test_run_input_relative.tmp")
    try:
        os.chdir("test_run_input_relative.tmp")
        assert r.input("../foo/test.csv") == "../foo/test.csv"
        assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
            (r._id, json.dumps({"version": "1",
                                "summary": {},
                                "parameters": {},
                                "output": [],
                                "input": ["foo/test.csv"],
                                "labels": {},
            }, sort_keys=True, indent=4), r._id)
    finally:
        os.chdir(orig_dir)
        os.rmdir("test_run_input_relative.tmp")

@given(lists(sampled_from(input_files), min_size=2, max_size=2, unique=True))
def test_run_input_2(x):
    r = dotscience.Run("/workspace-root")
    xp0 = tidy_path("/workspace-root/" + x[0])
    xp1 = tidy_path("/workspace-root/" + x[1])
    r.add_input(xp0)
    r.add_input(xp1)
    x = set([os.path.relpath(y,start="/workspace-root") for y in (xp0,xp1)])
    len(r._inputs) == len(x) and sorted(r._inputs) == sorted(x)

@given(lists(sampled_from(input_files), unique=True))
def test_run_input_n(x):
    x = set([tidy_path("/workspace-root/" + y) for y in x])
    r = dotscience.Run("/workspace-root")
    r.add_inputs(*x)
    len(r._inputs) == len(x) and sorted(r._inputs) == sorted([os.path.relpath(y,start="/workspace-root") for y in x])

def test_run_input_recursive():
    orig_dir = os.getcwd()
    try:
        os.mkdir("test_run_input_recursive.tmp")
        with open("test_run_input_recursive.tmp/file1", "w") as f:
            f.write("File 1")
        os.mkdir("test_run_input_recursive.tmp/a")
        with open("test_run_input_recursive.tmp/a/file2", "w") as f:
            f.write("File 2")
        with open("test_run_input_recursive.tmp/a/file3", "w") as f:
            f.write("File 3")
        os.mkdir("test_run_input_recursive.tmp/b")
        r = dotscience.Run(orig_dir)
        assert r.input("test_run_input_recursive.tmp") == "test_run_input_recursive.tmp"
        assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
            (r._id, json.dumps({"version": "1",
                                "summary": {},
                                "parameters": {},
                                "input": [
                                    "test_run_input_recursive.tmp/a/file2",
                                    "test_run_input_recursive.tmp/a/file3",
                                    "test_run_input_recursive.tmp/file1"
                                ],
                                "output": [],
                                "labels": {},
            }, sort_keys=True, indent=4), r._id)
    finally:
        shutil.rmtree("test_run_input_recursive.tmp")

@given(sampled_from(output_files))
def test_run_output_1(x):
    r = dotscience.Run("/workspace-root")
    xpath = tidy_path("/workspace-root/" + x)
    assert r.output(xpath) == xpath
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "summary": {},
                        "parameters": {},
                        "input": [],
                        "output": [os.path.relpath(xpath,start="/workspace-root")],
                        "labels": {},
    }, sort_keys=True, indent=4), r._id)

def test_run_output_relative():
    orig_dir = os.getcwd()
    r = dotscience.Run(orig_dir)
    os.mkdir("test_run_output_relative.tmp")
    try:
        os.chdir("test_run_output_relative.tmp")
        assert r.output("../foo/test.csv") == "../foo/test.csv"
        assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
            (r._id, json.dumps({"version": "1",
                                "summary": {},
                                "parameters": {},
                                "output": ["foo/test.csv"],
                                "input": [],
                                "labels": {},
            }, sort_keys=True, indent=4), r._id)
    finally:
        os.chdir(orig_dir)
        os.rmdir("test_run_output_relative.tmp")

@given(lists(sampled_from(output_files), min_size=2, max_size=2, unique=True))
def test_run_output_2(data):
    r = dotscience.Run("/workspace-root")
    xp0 = tidy_path("/workspace-root/" + data[0])
    xp1 = tidy_path("/workspace-root/" + data[1])
    r.add_output(xp0)
    r.add_output(xp1)
    data = set([os.path.relpath(x,start="/workspace-root") for x in (xp0,xp1)])
    len(r._outputs) == len(data) and sorted(r._outputs) == sorted(data)

@given(lists(sampled_from(output_files), unique=True))
def test_run_output_n(data):
    data = set([tidy_path("/workspace-root/" + x) for x in data])
    r = dotscience.Run("/workspace-root")
    r.add_outputs(*data)
    len(r._outputs) == len(data) and sorted(r._outputs) == sorted([os.path.relpath(y,start="/workspace-root") for y in data])

def test_run_output_recursive():
    orig_dir = os.getcwd()
    try:
        r = dotscience.Run(orig_dir)
        assert r.output("test_run_output_recursive.tmp") == "test_run_output_recursive.tmp"

        os.mkdir("test_run_output_recursive.tmp")
        with open("test_run_output_recursive.tmp/file1", "w") as f:
            f.write("File 1")
        os.mkdir("test_run_output_recursive.tmp/a")
        with open("test_run_output_recursive.tmp/a/file2", "w") as f:
            f.write("File 2")
        with open("test_run_output_recursive.tmp/a/file3", "w") as f:
            f.write("File 3")
        os.mkdir("test_run_output_recursive.tmp/b")

        assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
            (r._id, json.dumps({"version": "1",
                                "summary": {},
                                "parameters": {},
                                "input": [],
                                "output": [
                                    "test_run_output_recursive.tmp/a/file2",
                                    "test_run_output_recursive.tmp/a/file3",
                                    "test_run_output_recursive.tmp/file1"
                                ],
                                "labels": {},
            }, sort_keys=True, indent=4), r._id)
    finally:
        shutil.rmtree("test_run_output_recursive.tmp")

class MockTensorflow:
    def __init__(self):
        self.__name__ = "tensorflow"
        self.__version__ = "1.2.3.4"

@given(text(),sampled_from(output_files))
def test_run_tensorflow_model(name,x):
    r = dotscience.Run("/workspace-root")
    xpath = tidy_path("/workspace-root/" + x)
    relxpath = os.path.relpath(xpath,start="/workspace-root")
    assert r.model(MockTensorflow(), name, xpath) == xpath
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "summary": {},
                        "parameters": {},
                        "input": [],
                        "output": [relxpath],
                        "labels": {"artefact:"+name: "{\"files\":{\"model\":\"" + relxpath + "\"},\"type\":\"tensorflow-model\",\"version\":\"1.2.3.4\"}"},
    }, sort_keys=True, indent=4), r._id)

@given(text(),sampled_from(output_files),sampled_from(output_files))
def test_run_tensorflow_model_with_classes(name,x,c):
    assume(x != c)
    r = dotscience.Run("/workspace-root")
    xpath = tidy_path("/workspace-root/" + x)
    relxpath = os.path.relpath(xpath,start="/workspace-root")
    cpath = tidy_path("/workspace-root/" + c)
    relcpath = os.path.relpath(cpath,start="/workspace-root")

    assert r.model(MockTensorflow(), name, xpath, classes=cpath) == xpath
    assert str(r) == """[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]""" % \
    (r._id, json.dumps({"version": "1",
                        "summary": {},
                        "parameters": {},
                        "input": [],
                        "output": sorted([relxpath,relcpath]),
                        "labels": {"artefact:"+name: "{\"files\":{\"classes\":\"" + relcpath + "\",\"model\":\"" + relxpath + "\"},\"type\":\"tensorflow-model\",\"version\":\"1.2.3.4\"}"},
    }, sort_keys=True, indent=4), r._id)

@given(text())
def test_run_labels_1(x):
    r = dotscience.Run("/workspace-root")
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
    r = dotscience.Run("/workspace-root")
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
    r = dotscience.Run("/workspace-root")
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
    r = dotscience.Run("/workspace-root")
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
    r = dotscience.Run("/workspace-root")
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
    r = dotscience.Run("/workspace-root")
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
    r = dotscience.Run("/workspace-root")
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
    r = dotscience.Run("/workspace-root")
    r.start()
    try:
        r.start()
    except RuntimeError:
        return True
    else:
        assert 'Did not get a RuntimeError when attempting to start a run twice'

def test_run_end_1():
    r = dotscience.Run("/workspace-root")
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
    r = dotscience.Run("/workspace-root")
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

def test_notice_jupyter_mode():
    try:
        os.environ["DOTSCIENCE_WORKLOAD_TYPE"] = "jupyter"
        ds = dotscience.Dotscience()
        ds.publish()
        assert ds._mode == "interactive"
    finally:
        os.unsetenv("DOTSCIENCE_WORKLOAD_TYPE")

def test_notice_command_mode():
    try:
        os.environ["DOTSCIENCE_WORKLOAD_TYPE"] = "command"
        ds = dotscience.Dotscience()
        ds.publish()
        assert ds._mode == "script"
    finally:
        os.unsetenv("DOTSCIENCE_WORKLOAD_TYPE")

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
    assert m1["workload-file"].endswith("/usr/local/bin/pytest")

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

@given(sampled_from(input_files))
def test_input_1a(d):
    s=io.StringIO()
    dotscience.start()
    dp = tidy_path(os.getcwd() + "/" + d)
    dotscience.add_input(dp)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["input"] == [os.path.relpath(dp, start=os.getcwd())]
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(sampled_from(input_files))
def test_input_1b(d):
    s=io.StringIO()
    dotscience.start()
    dp = tidy_path(os.getcwd() + "/" + d)
    assert dotscience.input(dp) == dp
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["input"] == [os.path.relpath(dp, start=os.getcwd())]
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(lists(sampled_from(input_files), unique=True))
def test_input_n(d):
    d = set([tidy_path(os.getcwd() + "/" + x) for x in d])
    s=io.StringIO()
    dotscience.start()
    dotscience.add_inputs(*d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert len(m["input"]) == len(d) and sorted(m["input"]) == sorted([os.path.relpath(x, start=os.getcwd()) for x in d])
    assert m["output"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(sampled_from(output_files))
def test_output_1a(d):
    s=io.StringIO()
    dotscience.start()
    dp = tidy_path(os.getcwd() + "/" + d)
    dotscience.add_output(dp)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == [os.path.relpath(dp, start=os.getcwd())]
    assert m["input"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(sampled_from(output_files))
def test_output_1b(d):
    s=io.StringIO()
    dotscience.start()
    dp = tidy_path(os.getcwd() + "/" + d)
    assert dotscience.output(dp) == dp
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert m["output"] == [os.path.relpath(dp, start=os.getcwd())]
    assert m["input"] == []
    assert m["labels"] == {}
    assert m["parameters"] == {}
    assert m["summary"] == {}
    assert m["workload-file"] == TEST_WORKLOAD_FILE

@given(lists(sampled_from(output_files), unique=True))
def test_output_n(d):
    d = set([tidy_path(os.getcwd() + "/" + x) for x in d])
    s=io.StringIO()
    dotscience.start()
    dotscience.add_outputs(*d)
    dotscience.publish(stream=s)
    m = _parse(s.getvalue())
    assert len(m["output"]) == len(d) and sorted(m["output"]) == sorted([os.path.relpath(x, start=os.getcwd()) for x in d])
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
    assert m1["start"] != m2["start"]
    assert m1["end"] != m2["end"]

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
