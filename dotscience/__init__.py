name = "dotscience"
__version__ = '0.6.6'

import json
import datetime
import uuid
import sys
import os
import requests
import time
import platform
import random
import string

from dotmesh.client import DotmeshClient, DotName

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
        self._deployment = None
        self._deployer = None

    def connect(self, username, apikey, project, hostname):
        # TODO: Make this fail if we're in a mode other than 'remote' mode.
        # TODO: make publish etc fail if we're not connected in remote mode.
        if not project:
            raise Exception("Please specify a project name as the third argument to ds.connect()")
        self._dotmesh_client = DotmeshClient(
            cluster_url=hostname + "/v2/dotmesh/rpc",
            username=username,
            api_key=apikey
        )
        self._hostname = hostname
        self._mode = "remote"
        self._auth = (username, apikey)
        self._project_name = project
        print("Checking connection... ", end="")
        result = self._dotmesh_client.ping()
        print("connected!")

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

        ret = None
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
        print("\n=== Dotscience remote publish ===\n")
        # - Upload output files via S3 API in a tar stream
        # TODO: maybe don't upload all output files, only ones tagged as model?

        self._get_project_or_create(self._project_name, verbose=True)

        print("*  Uploading output/model files", end="")
        self._upload_output_files()
        # - Craft the commit metadata for the run and call the Commit() API
        #   directly on dotmesh on the hub
        run = self._commit_run_on_hub()
        ret["run"] = ret
        print(" done")
        print("   -> Dotscience run: %s\n" % (run,))

        # NB: deploy=True implies build=True
        if build or deploy:
            # - Build
            print("*  Building docker image...", end="")
            sys.stdout.flush()
            image = self._build_docker_image_on_hub()
            ret["image"] = image
            print(" done")
            print("   -> Docker image: %s\n" % (image,))
        if deploy:
            # - Deploy to Kubernetes
            print("*  Deploying to Kubernetes... ", end="")
            sys.stdout.flush()
            endpoint = self._deploy_to_kube()
            ret["endpoint"] = endpoint
            print("done")
            print("   -> Endpoint: %s\n" % (endpoint,))
            # - Set up Grafana dashboard
            print("*  Creating Grafana dashboard... ", end="")
            sys.stdout.flush()
            dashboard = self._setup_grafana()
            ret["dashboard"] = dashboard
            print("done")
            print("   -> Dashboard: %s\n" % (dashboard,))

            print("Waiting for model endpoint to become active", end="")
            sys.stdout.flush()
            self._wait_active()
            print(" done")

        print("=== Dotscience publish complete ===\n")
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
                    print("Found project %s.\n" % (project_name,))
                return project
        else:
            new = requests.post(self._hostname+"/v2/projects", auth=self._auth, json={"name": project_name})
            self._cached_project = new.json()
            if verbose:
                print("Created new project %s as it did not exist.\n" % (project_name,))
            return new.json()

    def _upload(self, filename):
        project = self._get_project_or_create(self._project_name)
        dotName = f"project-{project['id'][:8]}-default-workspace"
        attempt = 0
        while attempt < 10:
            attempt += 1
            with open(filename, 'rb') as f:
                # workaround https://github.com/psf/requests/issues/2422 - unable
                # to see response code when body isn't fully consumed due to error
                # (e.g. 423 Locked)
                import http
                from base64 import b64encode

                userAndPass = b64encode((f"{self._auth[0]}:{self._auth[1]}").encode("ascii")).decode("ascii")
                headers = { 'Authorization' : 'Basic %s' %  userAndPass }

                scheme, hostname = self._hostname.split("://")
                if scheme == "http":
                    conn = http.client.HTTPConnection(hostname)
                elif scheme == "https":
                    conn = http.client.HTTPSConnection(hostname)
                else:
                    raise Exception("Unsupported scheme %s", scheme)

                try:
                    R = conn.request(
                        "PUT",
                        self._hostname+f"/v2/dotmesh/s3/{self._auth[0]}:{dotName}/{filename}",
                        f,
                        headers, # {"Content-Type": "application/json", "Accept": "application/json"},
                    )
                    # Success, return - otherwise we'll retry
                    return
                except Exception as e:
                    print("Error uploading %s: %s" % (filename, e))
                    new_R = conn.getresponse()
                    print("Response code:", new_R.status)
                    if new_R.status == 423:
                        print("--> Try stopping Jupyter within Dotscience or wait "
                             "for the lock owner (e.g. task ID) listed below to finish, then try again")
                    print("Response body:", new_R.read())
                    print("Waiting a second and trying again...")
                    time.sleep(1.0)

                #upload = requests.put(
                #    self._hostname+f"/v2/dotmesh/s3/{self._auth[0]}:{dotName}/{filename}", auth=self._auth,
                #    data=f
                #)
        raise Exception("didn't succeed after retrying 10 times")

    def _commit_run_on_hub(self):
        """
        Set up commit metadata a bit like this:

        author: luke24sep
        exec.start: 20190924T112051.349340345
        exec.end: 20190924T112354.535838796
        exec.logs: ["4abc9799-3c45-4868-a669-d0e17e12e32b/agent-stdout.log","4abc9799-3c45-4868-a669-d0e17e12e32b/workload-stdout.log","4abc9799-3c45-4868-a669-d0e17e12e32b/workload-stderr.log","4abc9799-3c45-4868-a669-d0e17e12e32b/committer-stdout.log","4abc9799-3c45-4868-a669-d0e17e12e32b/committer-stderr.log"]
        message: Dotscience runs
        run.452521f7-c069-4271-b06e-dcd55635b871.authority: workload
        run.452521f7-c069-4271-b06e-dcd55635b871.description: trained linear regression model
        run.452521f7-c069-4271-b06e-dcd55635b871.end: 20190924T112352.941411
        run.452521f7-c069-4271-b06e-dcd55635b871.input-files: ["combined.csv@125f91d5-9d5d-4123-95f3-c97448bfcfb0"]
        run.452521f7-c069-4271-b06e-dcd55635b871.output-files: ["linear_regressor.pkl"]
        run.452521f7-c069-4271-b06e-dcd55635b871.parameters.features: finishedsqft
        run.452521f7-c069-4271-b06e-dcd55635b871.start: 20190924T112352.843016
        run.452521f7-c069-4271-b06e-dcd55635b871.summary.lin_rmse: 855408.5050370345
        run.452521f7-c069-4271-b06e-dcd55635b871.summary.regressor_score: 0.35677710327221
        run.452521f7-c069-4271-b06e-dcd55635b871.workload-file: hello-dotscience.ipynb
        runner.cpu: ["1x Intel(R) Xeon(R) CPU @ 2.30GHz"]
        runner.name: 6ddeae52-untitled
        runner.platform: linux
        runner.platform_version: Linux 096f216f707b 4.15.0-1037-gcp #39-Ubuntu SMP Wed Jul 3 06:28:59 UTC 2019 x86_64 Linux
        runner.ram: 3872563200
        runner.version: Runner=Dotscience Docker Executor rev. 0.8.4 Agent=0.11.1
        runs: ["452521f7-c069-4271-b06e-dcd55635b871"]
        timestamp: 1569324234537654474
        type: dotscience.run.v1
        workload.image.hash: 'quay.io/dotmesh/jupyterlab-tensorflow@sha256:7d5ab277b31d6a4024d61728ffedbf0ffc76ab7bb2fa6d4b0938ebc6c7f22a59'
        workload.image: quay.io/dotmesh/jupyterlab-tensorflow:0.2.11
        workload.type: jupyter
        """

        def flatten(d):
            # yield a sequence of (k, v) tuples where k is "a.b.c" for nested
            # dict {a: {b: c:{ ... }}}
            for k, v in d.items():
                if k == "input":
                    # XXX we can't add version strings to input files in this
                    # context, so ignore them
                    continue
                if k == "output":
                    k = "output-files"
                if k == "labels":
                    k = "label"
                if isinstance(v, dict):
                    for kk, vv in flatten(v):
                        yield k+"."+kk, vv
                elif isinstance(v, str):
                    yield k, v
                else:
                    # JSON encode e.g. lists or floats
                    yield k, json.dumps(v)

        commit = {}
        commit["author"] = self._auth[0]
        commit["exec.start"] = self.currentRun._start.strftime("%Y%m%dT%H%M%S.%f")
        commit["exec.end"] = self.currentRun._end.strftime("%Y%m%dT%H%M%S.%f")
        commit["exec.logs"] = json.dumps([])
        commit["runner.name"] = platform.node()
        commit["runner.platform"] = platform.system()
        commit["runner.platform_version"] = platform.version()
        # newID was called just before _publish_remote_run so this should be safe...
        commit["runs"] = json.dumps([self.currentRun._id])
        commit["workload.type"] = "remote"
        commit["type"] = "dotscience.run.v1"

        # TODO: insert run classes here
        run = self.currentRun.metadata()

        for k, v in flatten(run):
            commit[f"run.{self.currentRun._id}.{k}"] = v

        commit[f"run.{self.currentRun._id}.authority"] = "remote"
        # TODO the following might not work well from jupyter
        commit[f"run.{self.currentRun._id}.workload-file"] = sys.argv[0]
        # TODO add timestamp?

        project = self._get_project_or_create(self._project_name)
        dotName = f"project-{project['id'][:8]}-default-workspace"
        dot = self._dotmesh_client.getDot(dotname=dotName, ns=self._auth[0])
        branch = dot.getBranch("master")
        result = branch.commit("Remote dotscience run", commit)
        # construct URL
        runURL = f"{self._hostname}/project/{project['id']}/runs/summary/{self.currentRun._id}"
        return runURL

    def _find_model_id(self, run_id):
        attempt = 0
        while attempt < 10:
            attempt += 1
            # TODO: replace with a query arg in the backend to avoid iterating
            models = requests.get(self._hostname+"/v2/models", auth=self._auth).json()
            model_id = None
            for model in models:
                if model["run_id"] == self.currentRun._id:
                    # found it!
                    model_id = model["id"]
                    return model_id
            if model_id is None:
                print("Unable to find model with run id %r yet... (models=%s)" % (self.currentRun._id, models))
                print("Trying again in 1 second")
                time.sleep(1.0)

        raise Exception("Unable to find model with run id %s after 10 tries" % (run_id,))

    def _initiate_build(self, model_id):
        attempt = 0
        the_exc = None
        while attempt < 120:
            attempt += 1
            try:
                resp = requests.post(self._hostname+f"/v2/models/{model_id}/builds", auth=self._auth, json={})
                if resp.status_code != 201:
                    raise Exception(f"Error {resp.status_code} on POST to /v2/models/{model_id}/builds: {resp.content}")
                build = resp.json()
                return build
            except Exception as e:
                the_exc = e
                print(".", end="")
                sys.stdout.flush()
                time.sleep(1.0)
            if attempt == 60:
                print("\nSeems to be taking a long time, waiting one more minute")

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        print("Failed to start building model within 2 minutes, please let us know using the Intercom button bottom right, or email support@dotscience.com so that we can fix it with your help - thanks!\n")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if the_exc != None:
            raise the_exc
        else:
            raise Exception("Unable to load error")


    def _build_docker_image_on_hub(self):
        # find model id
        model_id = self._find_model_id(self.currentRun._id)
        build = self._initiate_build(model_id)
        self._docker_image = build["image_name"]
        attempt = 0
        the_exc = None
        while attempt < 120:
            attempt += 1
            try:
                resp = requests.get(self._hostname+f"/v2/models/{model_id}/builds/{build['id']}", auth=self._auth)
                if resp.status_code != 200:
                    raise Exception(f"Error {resp.status_code} on GET to /v2/models/{model_id}/builds/{build['id']}: {resp.content}")
                build = resp.json()
                if build["status"] != "completed":
                    raise Exception(f"build not complete: {build}")
                return self._docker_image
            except Exception as e:
                the_exc = e
                print(".", end="")
                sys.stdout.flush()
                time.sleep(1.0)
            if build is not None and build["status"] == "failed":
                raise Exception("Build failed: %s", build)
            if attempt == 60:
                print("\nSeems to be taking a long time, waiting one more minute")

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        print("Failed to build model within 2 minutes, please let us know using the Intercom button bottom right, or email support@dotscience.com so that we can fix it with your help - thanks!\n")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if the_exc != None:
            raise the_exc
        else:
            raise Exception("Unable to load error")

        return self._docker_image

    def _deploy_to_kube(self):
        # TODO: support specifying the deployer
        deployers = requests.get(self._hostname+"/v2/deployers", auth=self._auth).json()
        managed = [d for d in deployers if d["managed"]]
        if len(managed) == 0:
            raise Exception("Can't deploy - no managed deployers found")
        deployer = managed[0]
        self._deployer = deployer
        body = {
            # TODO fill this in
            "name": self._project_name.replace('-', ''),
            "namespace": "default",
            "image_name": self._docker_image,
            "container_port": 8501,
            "model_name": self._project_name.replace('-', ''), # XXX should this be the same as name?
            "replicas": 1
        }
        try:
            classes_file = json.loads(
                list(self.currentRun.metadata()["labels"].values())[0],
            )["files"]["classes"]
            # XXX what if it's changed in between model() and this point in publish()?
            import base64
            classes_data = open(classes_file, 'rb').read()
            classes_encoded = base64.b64encode(classes_data)
            body["model_classes"] = classes_encoded.decode('ascii')
        except Exception as e:
            print("Unable to extract classes file (error = %s), continuing regardless (try passing classes=\"classes.json\" to ds.model, where classes.json contains a single map from class ids (strings) to human readable classnames..." % (e,))
        deployment = requests.post(
            self._hostname+f"/v2/deployers/{deployer['id']}/deployments",
            json=body,
            auth=self._auth,
        )
        self._deployment = deployment.json()
        return "https://"+deployment.json()["host"]+"/v1/models/model:predict"

    def _wait_active(self):
        if self._deployment is None:
            raise Exception("tried to wait for model to become active when no self._deployment was set")
        attempt = 0
        the_exc = None
        while attempt < 120:
            attempt += 1
            try:
                resp = requests.get("https://"+self._deployment["host"]+"/v1/models/model")
                if resp.status_code != 200:
                    raise Exception("status code %s" % (resp.status_code,))
                return
            except Exception as e:
                the_exc = e
                print(".", end="")
                sys.stdout.flush()
                time.sleep(1.0)
            if attempt == 60:
                print("\nSeems to be taking a long time, waiting one more minute")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        print("Failed to contact model within 2 minutes, please let us know using the Intercom button bottom right, or email support@dotscience.com so that we can fix it with your help - thanks!\n")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if the_exc != None:
            raise the_exc
        else:
            raise Exception("Unable to load error")

    def _setup_grafana(self):
        if self._deployment is None:
            raise Exception("tried to set up dashboard when no self._deployment was set")
        if self._deployer is None:
            raise Exception("tried to set up dashboard when no self._deployer was set")
        deployer_id = self._deployer["id"]
        deployment_id = self._deployment["id"]
        grafana = requests.post(
            self._hostname+f"/v2/deployers/{deployer_id}/deployments/{deployment_id}/dashboard",
            json={},
            auth=self._auth,
        )
        # TODO check status code
        dashboard = grafana.json()
        return dashboard['dashboardURL']

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

    def model(self, kind, name, *args, **kwargs):
        self._check_started()
        return self.currentRun.model(kind, name, *args, **kwargs)

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

def model(kind, name, *args, **kwargs):
    return _defaultDS.model(kind, name, *args, **kwargs)

def add_parameter(label, value):
    _defaultDS.add_parameter(label, value)

def add_parameters(*args, **kwargs):
    _defaultDS.add_parameters(*args, **kwargs)

def parameter(label, value):
    return _defaultDS.parameter(label, value)

add_metric = add_summary
add_metrics = add_summaries
metric = summary
param = parameter

def debug():
    _defaultDS.debug()

def connect(username, apikey, project, hostname=""):
    # Allow defaulting on empty string e.g. from env
    if not hostname:
        hostname = "https://cloud.dotscience.com"
    _defaultDS.connect(
        username, apikey, project, hostname,
    )

