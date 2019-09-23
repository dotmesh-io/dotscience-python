name = "dotscience"

import json
import datetime
import uuid
import sys
import os
import requests

from dotmesh.client import DotmeshClient

# Paths will be relative to root, not necessarily cwd
def _add_output_path(root, nameset, path):
    full_path = os.path.join(root, path)

    if os.path.isdir(full_path):
        ents = os.listdir(full_path)
        for ent in ents:
            fn = os.path.join(path, ent)
            _add_output_path(root, nameset, fn)
    else:
        nameset.add(path)

class Run:
    def __init__(self, root):
        self._id = None
        self._error = None
        self._description = None
        self._inputs = set()
        self._outputs = set()
        self._labels = {}
        self._summary = {}
        self._parameters = {}
        self._start = None
        self._end = None
        self._workload_file = None
        self._mode = None
        self._root = root

    def _set_workload_file(self, workload_file):
        self._workload_file = workload_file

    def start(self):
        if self._start == None:
            self._start = datetime.datetime.utcnow()
        else:
            raise RuntimeError('Run.start() has been called more than once')

    def lazy_start(self):
        if self._start == None:
            self._start = datetime.datetime.utcnow()

    def forget_times(self):
        self._end = None
        self._start = None

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

    def add_input_file(self, filename):
        filename_str = os.path.relpath(str(filename),start=self._root)
        self._inputs.add(filename_str)

    def add_input(self, filename):
        if os.path.isdir(filename):
            ents = os.listdir(filename)
            for ent in ents:
                fn = os.path.join(filename, ent)
                self.add_input(fn)
        else:
            self.add_input_file(filename)

    def add_inputs(self, *args):
        for filename in args:
            self.add_input(filename)

    def input(self, filename):
        self.add_input(filename)
        return filename

    # add_output does not recursively expand directories like
    # add_input because it's called BEFORE the output happens - the
    # files might not exist yet.  So expansion happens in metadata()
    # below!
    def add_output(self, filename):
        filename_str = os.path.relpath(str(filename),start=self._root)
        self._outputs.add(filename_str)

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

    def model(self, kind, name, *args, **kwargs):
        artefact_type = None
        try:
            if kind.__name__ == "tensorflow":
                artefact_type = "tensorflow-model"
        except:
            pass

        if artefact_type == None:
            raise RuntimeError('Unknown model type %r' % (kind,))

        aj = {"type": artefact_type}
        files = {}
        return_value = None
        if artefact_type == "tensorflow-model":
            aj["version"] = kind.__version__
            if len(args) != 1:
                raise RuntimeError('Tensorflow models require a path to the model as the third argument')
            files["model"] = args[0]
            return_value = args[0]
            if "classes" in kwargs:
                files["classes"] = kwargs["classes"]

        relative_files = {}
        for key in files:
            self.add_output(files[key])
            relative_files[key] = os.path.relpath(str(files[key]),start=self._root)
        aj["files"] = relative_files

        self.add_label("artefact:" + name, json.dumps(aj, sort_keys=True, separators=(',', ':')))

        return return_value

    def add_model(self, kind, name, *args, **kwargs):
        self.model(kind, name, *args, **kwards)
        return None

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
        # We expanded input directories on the way in, because we
        # expect the files to exist before add_input is called; but we
        # only expand output directories here at the end, because we
        # expect them to be created AFTER add_output is called.

        expanded_outputs = set()
        for o in self._outputs:
            _add_output_path(self._root, expanded_outputs, o)

        r = {
            "version": "1",
            "input": sorted(self._inputs),
            "output": sorted(expanded_outputs),
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

        if self._workload_file != None:
            r["workload-file"] = self._workload_file

        return r

    def newID(self):
        self._id = str(uuid.uuid4())

    def __str__(self):
        jsonMetadata = json.dumps(self.metadata(), sort_keys=True, indent=4)

        return "[[DOTSCIENCE-RUN:%s]]%s[[/DOTSCIENCE-RUN:%s]]" % (self._id, jsonMetadata, self._id)

    def debug(self):
        # FIXME: Do something a bit nicer
        print (json.dumps(self.metadata(), sort_keys=True, indent=4))

class Dotscience:
    currentRun = None

    def __init__(self):
        self._mode = None
        self._workload_file = None
        self._root = os.getenv('DOTSCIENCE_PROJECT_DOT_ROOT', default=os.getcwd())
        self._dotmesh_client = None
        self._hostname = None
        self._auth = None
        self._cached_project = None
        self._project_name = None

    def connect(self, username, apikey, project, hostname):
        # TODO: Make this fail if we're in a mode other than 'remote' mode.
        # TODO: make publish etc fail if we're not connected in remote mode.
        self._dotmesh_client = DotmeshClient(
            cluster_url=hostname + "/v2/dotmesh/rpc",
            username=username,
            api_key=apikey
        )
        self._hostname = hostname
        self._auth = (username, apikey)
        self._project_name = project
        print("Calling ping...")
        result = self._dotmesh_client.ping()
        print("result = %r", (result,))

    def interactive(self):
        if self._mode == None or self._mode == "interactive":
            self._mode = "interactive"
            self._workload_file = None
        else:
            raise RuntimeError('An attempt was mode to select interactive mode for the Dotscience Python Library when it was in %s mode' % (self._mode,))

    def remote(self):
        if self._mode == None or self._mode == "remote":
            self._mode = "remote"
            self._workload_file = None
        else:
            raise RuntimeError('An attempt was mode to select remote mode for the Dotscience Python Library when it was in %s mode' % (self._mode,))

    def script(self, script_path = None):
        if self._mode == None or self._mode == "script":
            self._mode = "script"
            if script_path == None:
                self._workload_file = os.path.relpath(str(sys.argv[0]),start=self._root)
            else:
                self._workload_file = os.path.relpath(str(script_path),start=self._root)
        else:
            raise RuntimeError('An attempt was mode to select script mode for the Dotscience Python Library when it was in %s mode' % (self._mode,))

    def _check_started(self):
        if self.currentRun == None:
            print("You have not called ds.start() yet, so I'm doing it for you!")
            self.start()
        # In case we got started implicitly after a publish, make sure we
        # record the start time of the first thing after the publish
        self.currentRun.lazy_start()

    def publish(self, description=None, stream=sys.stdout, build=False, deploy=False):
        if self._mode == None:
            runMode = os.getenv("DOTSCIENCE_WORKLOAD_TYPE", "")
            if runMode == "jupyter":
                self.interactive()
            elif runMode == "command":
                self.script()
            else:
                self.remote()
        self._check_started()

        # end() will set the end timestamp, if the user hasn't already
        # done so manually
        self.currentRun.end()

        if description != None:
            self.currentRun.set_description(description)

        self.currentRun._set_workload_file(self._workload_file)

        # Generate a new ID on every publish(), so you never get multiple runs
        # with the same id but potentially different parameters ending up in
        # metadata. That confuses the Dotscience UI very badly as it makes it
        # impossible to distinguish different runs by ID.
        self.currentRun.newID()

        if self._mode == "remote":
            # In remote mode, we need to push output files (i.e. models) to the
            # remote dotscience hub via the S3 api, then construct the run
            # metadata ourselves and create a dotmesh commit.
            #
            # TODO: in the future, we should call a runs API on the gateway to
            # decouple the run storage from dotmesh commit metadata (the
            # gateway will soon have a separate runs database which will
            # support streaming multi-epoch runs).
            ret = self._publish_remote_run(build, deploy)
        else:
            # In jupyter and command mode, we just write the current run out as
            # JSON (into a notebook or stdout, respectively) to get picked by
            # the agent's committer
            stream.write(str(self.currentRun) + "\n")

        # After publishing, reset the start and end time so that we don't end
        # up with multiple runs with the same times (calling end() twice has no
        # effect the second time otherwise). If the user doesn't explicitly
        # call start(), it will get implicitly called after the next
        # interaction with the python library anyway (e.g. ds.summary(), etc),
        # via _check_started which does a lazy_start to cover resetting the
        # start timer in this case.
        self.currentRun.forget_times()
        return ret

    def _publish_remote_run(self, build, deploy):
        ret = {}
        print("\n======== Dotscience publish ========\n")
        # - Upload output files via S3 API in a tar stream
        # TODO: maybe don't upload all output files, only ones tagged as model?
       
        self._get_project_or_create(self._project_name, verbose=True)
        
        print("Uploading output/model files", end="")
        self._upload_output_files()
        # - Craft the commit metadata for the run and call the Commit() API
        #   directly on dotmesh on the hub
        run = self._commit_run_on_hub()
        ret["run"] = ret
        print(" done")
        print("Dotscience run: %s\n" % (run,))

        # NB: deploy=True implies build=True
        if build or deploy:
            # - Build
            print("Building docker image... ", end="")
            image = self._build_docker_image_on_hub()
            ret["image"] = image
            print("done")
            print("Docker image: %s\n" % (image,))
        if deploy:
            # - Deploy to Kubernetes
            print("Deploying to Kubernetes... ", end="")
            endpoint = self._deploy_to_kube()
            ret["endpoint"] = endpoint
            print("done")
            print("Endpoint: %s\n" % (endpoint,))
            # - Set up Grafana dashboard
            print("Creating Grafana dashboard... ", end="")
            dashboard = self._setup_grafana()
            ret["dashboard"] = dashboard
            print("done")
            print("Dashboard: %s\n" % (dashboard,))
        print("=====================================")
        return ret

    def _upload_output_files(self):
        # TODO: upload them all in one go, using PUT tarball API, once
        # https://github.com/dotmesh-io/dotmesh/issues/754 is implemented
        for f in self.currentRun.metadata()["output"]:
            self._upload(f)
            print(".", end="")
            sys.stdout.flush()

    def _get_project_or_create(self, project_name, verbose=False):
        if self._cached_project:
            return self._cached_project
        
        projects = requests.get(self._hostname+"/v2/projects", auth=self._auth)
        for project in projects.json():
            if project["name"] == project_name:
                self._cached_project = project
                if verbose:
                    print("Found project %s." % (project_name,))
                return project
        else:
            new = requests.post(self._hostname+"/v2/projects", auth=self._auth, json={"name": project_name})
            self._cached_project = new.json()
            if verbose:
                print("Created new project %s as it did not exist." % (project_name,))
            return new.json()

    def _upload(self, filename):
        project = self._get_project_or_create(self._project_name)
        dotName = f"project-{project['id'][:8]}-default-workspace"
        upload = requests.put(
            self._hostname+f"/v2/dotmesh/s3/{self._auth[0]}:{dotName}/{filename}", auth=self._auth,
            data=open(filename, 'rb').read(),
        )
        #with open(filename, 'rb') as f:
        #    upload = requests.put(
        #        self._hostname+f"/v2/dotmesh/s3/{self._auth[0]}:{dotName}/{filename}", auth=self._auth,
        #        data=f
        #    )

    def _commit_run_on_hub(self):
        pass

    def _build_docker_image_on_hub(self):
        pass

    def _deploy_to_kube(self):
        pass

    def _setup_grafana(self):
        pass

    # Proxy things through to the current run
    def start(self, description = None):
        self.currentRun = Run(self._root)
        self.currentRun.start()
        if description != None:
            self.currentRun.set_description(description)

    def end(self):
        self._check_started()
        self.currentRun.end()

    def set_error(self, error):
        self._check_started()
        self.currentRun.set_error(error)

    def error(self, filename):
        self._check_started()
        return self.currentRun.error(filename)

    def set_description(self, description):
        self._check_started()
        self.currentRun.set_description(description)

    def description(self, filename):
        self._check_started()
        return self.currentRun.description(filename)

    def add_input(self, filename):
        self._check_started()
        self.currentRun.add_input(filename)

    def add_inputs(self, *args):
        self._check_started()
        self.currentRun.add_inputs(*args)

    def input(self, filename):
        self._check_started()
        return self.currentRun.input(filename)

    def add_output(self, filename):
        self._check_started()
        self.currentRun.add_output(filename)

    def add_outputs(self, *args):
        self._check_started()
        self.currentRun.add_outputs(*args)

    def output(self, filename):
        self._check_started()
        return self.currentRun.output(filename)

    def add_label(self, label, value):
        self._check_started()
        self.currentRun.add_label(label, value)

    def label(self, label, value):
        self._check_started()
        return self.currentRun.label(label, value)

    def add_labels(self, *args, **kwargs):
        self._check_started()
        self.currentRun.add_labels(*args, **kwargs)

    def add_summary(self, label, value):
        self._check_started()
        self.currentRun.add_summary(label, value)

    def add_summaries(self, *args, **kwargs):
        self._check_started()
        self.currentRun.add_summaries(*args, **kwargs)

    def summary(self, label, value):
        self._check_started()
        return self.currentRun.summary(label, value)

    def add_parameter(self, label, value):
        self._check_started()
        self.currentRun.add_parameter(label, value)

    def add_parameters(self, *args, **kwargs):
        self._check_started()
        self.currentRun.add_parameters(*args, **kwargs)

    def parameter(self, label, value):
        self._check_started()
        return self.currentRun.parameter(label, value)

    def debug(self):
        self._check_started()
        self.currentRun.debug()

# Default run start time is set HERE at module load time
_defaultDS = Dotscience()

# Proxy things through to the default Dotscience

def interactive():
    _defaultDS.interactive()

def script(workload_file = None):
    _defaultDS.script(workload_file)

def remote():
    _defaultDS.remote()

def publish(description=None, stream=sys.stdout, build=False, deploy=False):
    _defaultDS.publish(description, stream, build, deploy)

def start(description = None):
    _defaultDS.start(description)

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

add_metric = add_summary
add_metrics = add_summaries
metric = summary

def add_parameter(label, value):
    _defaultDS.add_parameter(label, value)

def add_parameters(*args, **kwargs):
    _defaultDS.add_parameters(*args, **kwargs)

def parameter(label, value):
    return _defaultDS.parameter(label, value)

def debug():
    _defaultDS.debug()

def connect(username, apikey, project, hostname="https://cloud.dotscience.com"):
    _defaultDS.connect(username, apikey, project, hostname)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
