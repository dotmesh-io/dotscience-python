name = "dotscience"

import json
import datetime
import uuid
import sys

class Run:
    def __init__(self):
        self._id = None
        self._error = None
        self._description = None
        self._inputs = []
        self._outputs = []
        self._labels = {}
        self._summary = {}
        self._parameters = {}
        self._start = None
        self._end = None

    def start(self):
        # Subsequent start()s overwrite, as the system does one at the
        # start by default and users should be able to override it.
        self._start = datetime.datetime.utcnow()

    def end(self):
        # Only the first end() is kept, as the system does one at the
        # end, but that shouldn't override one the user has done.
        if self._end == None:
            self._end = datetime.datetime.utcnow()

    def set_error(self, error):
        self._error = str(error)

    def error(self, error):
        self.set_error(error)
        return error

    def set_description(self, description):
        self._description = str(description)

    def description(self, description):
        self.set_description(description)
        return description

    def add_input(self, filename):
        ## FIXME: Canonicalise filename
        self._inputs.append(str(filename))

    def add_inputs(self, *args):
        for filename in args:
            self.add_input(filename)

    def input(self, filename):
        self.add_input(filename)
        return filename

    def add_output(self, filename):
        ## FIXME: Canonicalise filename
        self._outputs.append(str(filename))

    def add_outputs(self, *args):
        for filename in args:
            self.add_output(filename)

    def output(self, filename):
        self.add_output(filename)
        return filename

    def add_label(self, label, value):
        self._labels[str(label)] = str(value)

    # Supports any combination of ("a", "val of a", "b", "val of b") and (c="val of c")
    def add_labels(self, *args, **kwargs):
        if kwargs is not None:
            for key, value in kwargs.items():
                self.add_label(key, value)
        for key, value in [args[i:i+2] for i  in range(0, len(args), 2)]:
            self.add_label(key, value)

    # Binds a single value, but returns it unchanged
    def label(self, label, value):
        self.add_label(label, value)
        return value

    def add_summary(self, label, value):
        self._summary[str(label)] = str(value)

    # Supports any combination of ("a", "val of a", "b", "val of b") and (c="val of c")
    def add_summaries(self, *args, **kwargs):
        if kwargs is not None:
            for key, value in kwargs.items():
                self.add_summary(key, value)
        for key, value in [args[i:i+2] for i  in range(0, len(args), 2)]:
            self.add_summary(key, value)

    # Binds a single value, but returns it unchanged
    def summary(self, label, value):
        self.add_summary(label, value)
        return value

    def add_parameter(self, label, value):
        self._parameters[str(label)] = str(value)

    # Supports any combination of ("a", "val of a", "b", "val of b") and (c="val of c")
    def add_parameters(self, *args, **kwargs):
        if kwargs is not None:
            for key, value in kwargs.items():
                self.add_parameter(key, value)
        for key, value in [args[i:i+2] for i  in range(0, len(args), 2)]:
            self.add_parameter(key, value)

    # Binds a single value, but returns it unchanged
    def parameter(self, label, value):
        self.add_parameter(label, value)
        return value

    def metadata(self):
        r = {
            "version": "1",
            "input": self._inputs,
            "output": self._outputs,
            "labels": self._labels,
            "summary": self._summary,
            "parameters": self._parameters
        }

        if self._error != None:
            r["error"] = self._error

        if self._description != None:
            r["description"] = self._description

        if self._start != None:
            r["start"] = self._start.strftime("%Y%m%dT%H%M%S.%f")

        if self._end != None:
            r["end"] = self._end.strftime("%Y%m%dT%H%M%S.%f")

        return r

    def __str__(self):
        jsonMetadata = json.dumps(self.metadata(), sort_keys=True, indent=4)

        while self._id == None or jsonMetadata.find(self._id) != -1:
            self._id = str(uuid.uuid4())

        return "[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]" % (self._id, jsonMetadata, self._id)

    def debug(self):
        # FIXME: Do something a bit nicer
        print (json.dumps(self.metadata(), sort_keys=True, indent=4))

class Dotscience:
    currentRun = None

    def __init__(self):
        self._startRun()

    def _startRun(self):
        self.currentRun = Run()
        self.currentRun.start()

    def publish(self, description = None, stream = sys.stdout):
        # end() will set the end timestamp, if the user hasn't already
        # done so manually
        self.currentRun.end()
        if description != None:
            self.currentRun.set_description(description)

        stream.write(str(self.currentRun) + "\n")
        self._startRun()

    # Proxy things through to the current run

    def start(self):
        self.currentRun.start()

    def end(self):
        self.currentRun.end()

    def set_error(self, error):
        self.currentRun.set_error(error)

    def error(self, filename):
        return self.currentRun.error(filename)

    def set_description(self, description):
        self.currentRun.set_description(description)

    def description(self, filename):
        return self.currentRun.description(filename)

    def add_input(self, filename):
        self.currentRun.add_input(filename)

    def add_inputs(self, *args):
        self.currentRun.add_inputs(*args)

    def input(self, filename):
        return self.currentRun.input(filename)

    def add_output(self, filename):
        self.currentRun.add_output(filename)

    def add_outputs(self, *args):
        self.currentRun.add_outputs(*args)

    def output(self, filename):
        return self.currentRun.output(filename)

    def add_label(self, label, value):
        self.currentRun.add_label(label, value)

    def label(self, label, value):
        return self.currentRun.label(label, value)

    def add_labels(self, *args, **kwargs):
        self.currentRun.add_labels(*args, **kwargs)

    def add_summary(self, label, value):
        self.currentRun.add_summary(label, value)

    def add_summaries(self, *args, **kwargs):
        self.currentRun.add_summaries(*args, **kwargs)

    def summary(self, label, value):
        return self.currentRun.summary(label, value)

    def add_parameter(self, label, value):
        self.currentRun.add_parameter(label, value)

    def add_parameters(self, *args, **kwargs):
        self.currentRun.add_parameters(*args, **kwargs)

    def parameter(self, label, value):
        return self.currentRun.parameter(label, value)

    def debug(self):
        self.currentRun.debug()

# Default run start time is set HERE at module load time
_defaultDS = Dotscience()

# Proxy things through to the default Dotscience

def publish(description = None, stream = sys.stdout):
    _defaultDS.publish(description, stream)

def start():
    _defaultDS.start()

def end():
    _defaultDS.end()

def set_error(error):
    _defaultDS.set_error(error)

def error(error):
    return _defaultDS.error(error)

def set_description(description):
    _defaultDS.set_description(description)

def description(description):
    return _defaultDS.description(description)

def add_input(filename):
    _defaultDS.add_input(filename)

def add_inputs(*filenames):
    _defaultDS.add_inputs(*filenames)

def input(filename):
    return _defaultDS.input(filename)

def add_output(filename):
    _defaultDS.add_output(filename)

def add_outputs(*filenames):
    _defaultDS.add_outputs(*filenames)

def output(filename):
    return _defaultDS.output(filename)

def add_label(label, value):
    _defaultDS.add_label(label, value)

def add_labels(*args, **kwargs):
    _defaultDS.add_labels(*args, **kwargs)

def label(label, value):
    return _defaultDS.label(label, value)

def add_summary(label, value):
    _defaultDS.add_summary(label, value)

def add_summaries(*args, **kwargs):
    _defaultDS.add_summaries(*args, **kwargs)

def summary(label, value):
    return _defaultDS.summary(label, value)

def add_parameter(label, value):
    _defaultDS.add_parameter(label, value)

def add_parameters(*args, **kwargs):
    _defaultDS.add_parameters(*args, **kwargs)

def parameter(label, value):
    return _defaultDS.parameter(label, value)

def debug():
    _defaultDS.debug()

