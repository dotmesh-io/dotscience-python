name = "dotscience"

import json
import datetime
import uuid

class Run:
    _id = None
    _error = None
    _description = None
    _inputs = []
    _outputs = []
    _labels = {}
    _summary = {}
    _parameters = {}
    _start = None
    _end = None

    def start(self):
        # Subsequent start()s overwrite, as the system does one at the
        # start by default and users should be able to override it.
        self._start = datetime.datetime.utcnow()

    def end(self):
        # Only the first end() is kept, as the system does one at the
        # end, but that shouldn't override one the user has done.
        if self._end != None:
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
        self._inputs.append(str(filename))

    def input(self, filename):
        self.add_input(filename)
        return filename

    def add_output(self, filename):
        self._outputs.append(str(filename))

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
            "input": json.dumps(self._inputs),
            "output": json.dumps(self._outputs),
            "labels": json.dumps(self._labels),
            "summary": json.dumps(self._summary),
            "parameters": json.dumps(self._parameters)
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

    def str(self):
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
        currentRun = Run()
        currentRun.start()

    def publish(self, description = None):
        # end() will set the end timestamp, if the user hasn't already
        # done so manually
        self.currentRun.end()
        if description != None:
            self.currentRun.set_description(description)

        print self.currentRun.str()
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

    def input(self, filename):
        return self.currentRun.input(filename)

    def add_output(self, filename):
        self.currentRun.add_output(filename)

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

_defaultDS = Dotscience()


# Proxy things through to the default Dotscience

def publish(description = None):
    _defaultDS.publish(description)

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

def input(filename)
    return _defaultDS.input(filename)

def add_output(filename):
    _defaultDS.add_output(filename)

def output(filename)
    return _defaultDS.output(filename)

def add_label(label, value):
    _defaultDS.add_label(label, value)

def add_labels(self, *args, **kwargs):
    _defaultDS.add_labels(*args, **kwargs)

def label(label, value)
    return _defaultDS.label(label, value)

def add_summary(label, value):
    _defaultDS.add_summary(label, value)

def add_summaries(self, *args, **kwargs):
    _defaultDS.add_summaries(*args, **kwargs)

def summary(label, value)
    return _defaultDS.summary(label, value)

def add_parameter(label, value):
    _defaultDS.add_parameter(label, value)

def add_parameters(self, *args, **kwargs):
    _defaultDS.add_parameters(*args, **kwargs)

def parameter(label, value)
    return _defaultDS.parameter(label, value)

def debug():
    _defaultDS.debug()
