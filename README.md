# dotscience-python [![Build Status](https://drone.app.cloud.dotscience.net/api/badges/dotmesh-io/dotscience-python/status.svg)](https://drone.app.cloud.dotscience.net/dotmesh-io/dotscience-python)
## Releasing
To release this project, we're using `bump2version`.
Install it using: `pip install bump2version`, then when you have a new tag to release, run `bump2version --new-version <sem-ver> <major|minor|patch> && git push --tags`

It's recommended you also add release notes to the tag using [github releases](https://github.com/dotmesh-io/dotscience-python/releases) - you can add new release notes to old tags by just entering it when you click "draft new release".

## Installation

You can get the Dotscience Python library in one of three ways.


### Use the Dotscience Jupyterlab environment

If you are using Dotscience in a Jupyter notebook via the Dotscience web interface, the Python library is already installed (it's installed in the container that you are executing in, on your runner). In this case, there is no need to install anything: just `import dotscience as ds` in your notebook.

If you are using Dotscience to track a model whose source code is a script other than a Jupyter notebook, use one of the following installation methods:

### Use the ready-made Docker image

We've made a Docker image by taking the stock `python:3` image and pre-installing the Dotscience library like so:

```bash
$ docker run -ti quay.io/dotmesh/dotscience-python3:latest
Python 3.7.0 (default, Aug  4 2018, 02:33:39) 
[GCC 6.3.0 20170516] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import dotscience as ds
```

### Install it from PyPi

```bash
$ pip install dotscience
Collecting dotscience
  Downloading https://files.pythonhosted.org/packages/b2/e9/81db25b03e4c2b0115a7cd9078f0811b709a159493bb1b30e96f0906e1a1/dotscience-0.0.1-py3-none-any.whl
Installing collected packages: dotscience
Successfully installed dotscience-0.0.1
$ python
Python 3.7.0 (default, Sep  5 2018, 03:25:31) 
[GCC 6.3.0 20170516] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import dotscience as ds
```

## Quick Start

The most basic usage is to record what data files you read and write, and maybe to declare some summary statistics about how well the job went.

```python
import dotscience as ds
import pandas as pd

ds.interactive()

ds.start()

# Wrap the names of files you read with ds.input() - it just returns the filename:
df = pd.read_csv(ds.input('input_file.csv'))

# Likewise with files you write to:
df.to_csv(ds.output('output_file.csv'))

# Record a summary statistic about how well your job went
ds.add_summary('f-score', f_score)

ds.publish('Did some awesome data science!')
```

Don't forget to call `ds.interactive()` and `ds.start()` at the top if you're using Jupyter, and `ds.publish()` at the end, or your results won't get published! (The run description string passed in is optional, so leave it out if you can't think of anything nice to say).

## Interactive vs. Script mode

The library has two modes - interactive and script. That call to `ds.interactive()` in the example above puts it in interactive mode, which tells it there isn't a script file that the code is coming from. But when you're writing code in a Python script file, you should call `ds.script()` instead.

This instructs the library to record the script filename (from `sys.argv[0]`) in the output runs, so they can be tracked back to the originating script. You don't need this in interactive mode, because Dotscience knows which Jupyter notebook you're using - and `sys.argv[0]` points to the Jupyter Python kernel in that case, which isn't useful to record in the run!

If `sys.argv[0]` isn't helpful in some other situation, you can call `ds.script('FILENAME')` to specify the script file, relative to the current working directory. In fact, in a Jupyter notebook, you could specify `ds.script('my-notebook.ipynb')` to manually specify the notebook file and override the automatic recording of the notebook file, but there wouldn't be any point!

If you don't call either `ds.interactive()` or `ds.script()`, the library will try and guess by examining its environment. This should work in most cases, except if you call a script from inside JupyterLab (either through a terminal, or by calling `system()` or similar from your notebook), whereupon it will think it's in interactive mode - so it's best to include `ds.script()` in your scripts, just in case!

## Dotscience Anywhere - Remote mode
If you want to use own IDE or scripts, you can connect to Dotscience with `ds.connect()`, and use all of the dotscience library functions, like `ds.model()` and `ds.publish()`. This is particularly useful when you are interested in deploying your models into production without run tracking and provenance. Refer section on [Script based development with Dotscience Anywhere](/tutorials/script-based-development/) for a tutorial on this.

### Connect

You can use `ds.connect(..)` in your scripts in any environment to connect to the Dotscience Hub with your username and API key.

```python

ds.connect(
    "DOTSCIENCE_USERNAME", 
    "DOTSCIENCE_APIKEY", 
    "DOTSCIENCE_PROJECT_NAME",
    "DOTSCIENCE_HOSTNAME"
)
```

If the `"DOTSCIENCE_HOSTNAME"` is not specified, it defaults to `"https://cloud.dotscience.com"`

The quickest way to deploy models into production is by doing 

```python
ds.connect(
    os.getenv("DOTSCIENCE_USERNAME"), 
    os.getenv("DOTSCIENCE_APIKEY"), 
    os.getenv("DOTSCIENCE_PROJECT_NAME"),
    os.getenv("DOTSCIENCE_HOSTNAME")
)

import tensorflow as tf
model = Sequential()
# build and train model

ds.model(tf, "mnist", "model", classes="model/classes.json")
ds.publish("trained mnist model", deploy=True)
```

## All the things you can record

There's a lot more than just data files and summary stats that Dotscience will keep track of for you - and there's a choice of convenient ways to specify each thing, so it can fit neatly into your code. Here's the full list:

### Start and end time

The library will try to guess when your job starts and ends, from when you call `start()` until you call `publish()` (although it gets a bit more complex with multiple runs; see below).

If you're running in Jupyter, that means it'll include the time you spend working on your notebook, thinking, and so on as well as the time actually spent running the steps, which probably isn't what you want. To get better tracking of the run times, to keep track of what operations are slow and to cross-reference the time periods against other stuff running on the same computers to see if the workloads are interfering, it's a good idea to explicitly tell Dotscience when your steps start and stop.

Even when running Python scripts through `ds run`, it still helps to declare start and end times - if your script does a lot of tedious setup and teardown, you probably don't want those included in the run times.

Just call `start()` and `end()` before and after the real work and the library will record the current time when those functions are called. If you miss the `end()` it'll assume that your run has finished when you call `publish()`; this is often a good assumption, so you can often just call `start()` at the start and `publish()` at the end and be done with it.

```python
import dotscience as ds

ds.script()

...setup code...

ds.start()

...the real work...

ds.end()

...cleanup code...

ds.publish('Did some awesome data science!')
```

or:

```python
import dotscience as ds

ds.script()

...setup code...

ds.start()

...the real work...

ds.publish('Did some awesome data science!')
```

Dotscience will still record the start and end times of the actual execution of your workload (which is the entire script for a command workload, or the time between saves for a Jupyter workload) as well, but that's kept separately.

### Errors

Sometimes, a run fails, but you still want to record that it happened (perhaps so you know not to do the same thing again...). You can declare a run as failed like so:

```python
import dotscience as ds

ds.script()
ds.start()

...
ds.set_error('The data wasn't correctly formatted')
...

ds.publish('Tried, in vain, to do some awesome data science!')
```

If you're assembling an error message to use for some other reason, the dotscience library can just grab a copy of it before you use it, with this convenience function that returns its argument:

```python
import dotscience as ds

ds.script()
ds.start()

...
raise DataFormatError(ds.error('The data wasn't correctly formatted'))
...

ds.publish('Tried, in vain, to do some awesome data science!')
```

### Models

If your run has generated a Tensorflow model, you can declare it as such. This will load the model into the Model Library on the Dotscience Hub, and will enable automated deployment and model tracking features.

This can be done with `model()` or `add_model()`:

```python
import dotscience as ds
import tensorflow as tf

ds.script()
ds.start()

...

tf.saved_model.simple_save(
    tf.keras.backend.get_session(),
    ds.model(tf, "potatoes", "./model"),        # <---
    inputs={'input_image_bytes': model.input},
    outputs={t.name:t for t in model.outputs})

...or...

tf.saved_model.simple_save(
    tf.keras.backend.get_session(),
    "./model",
    inputs={'input_image_bytes': model.input},
    outputs={t.name:t for t in model.outputs})

ds.add_model(tf, "potatoes", "./model")         # <---

ds.publish('Trained the potato classifier')
```

The first argument to `model` or `add_model` should be the Tensorflow module itself, as imported by `import tensorflow as tf` in our example. This is used to identify it as a Tensorflow model (other types of model will be used in future), and to record the Tensorflow version used to generate it.

The second argument is the model name for the Model Library. In this case, we called it `potatoes`, as our model is a potato classifier.

The third argument is the path to the directory we're saving the Tensorflow model in, in this case `./model`. If called as `model()` rather than `add_model()`, this path is returned, so that it can be used to wrap the output path argument to `simple_save` in our example.

For classifier models, an optional keyword argument is supported in both `model()` and `add_model()`: `classes` can be provided as a path to a JSON file listing your classes, to enable automatic model metric tracking in deployment. Note that the classes file must be a path within the model directory.

```python
ds.model(tf, "mnist", "model", classes="model/classes.json")
```

Note that we don't need to call `output()` for the paths passed to `model()` and `add_model()`; they automatically declare the files as outputs from this run.

### Describing the run

It's good to record a quick human-readable description of what your run did, which helps people who are viewing the provenance graph. We've already seen how to pass a description into `publish()`:

```python
import dotscience as ds

ds.script()
ds.start()

ds.publish('Did some awesome data science!')
```

But you can set up a description before then and just call `publish()` with no arguments:

```python
import dotscience as ds

ds.script()
ds.start()

...
ds.set_description('Did some awesome data science!')
...

ds.publish()
```

If you're already making a descriptive string to send somewhere else, you can also use this function, that returns its argument:

```python
import dotscience as ds

ds.script()
ds.start()

...
log.write(ds.description('Did some awesome data science!'))
...

ds.publish()
```

And if you wish, you can also pass the description to `start()`, although it can feel weird using the past tense for something you're about to do:

```python
import dotscience as ds

ds.script()
ds.start('Did some awesome data science!')

...

ds.publish()
```

### Input and Output files

In order to correctly track the provenance of data files, Dotscience needs you to correctly declare what data files your jobs read and write.

The most convenient way to do this is with `input()` and `output()`, which accept the name of a file to be used for input or output respectively, and return it:

```python
import dotscience as ds

ds.script()
ds.start()

df.from_csv(ds.input('input_file.csv'))

df.to_csv(ds.output('output_file.csv'))

ds.publish('Did some awesome data science!')
```

But you can also declare them explicitly with `add_input()` and `add_output()`:

```python
import dotscience as ds

ds.script()
ds.start()

ds.add_input('input_file.csv')

ds.add_output('output_file.csv')

ds.publish('Did some awesome data science!')
```

Or declare several at once with `add_inputs()` and `add_outputs()`:

```python
import dotscience as ds

ds.script()
ds.start()

ds.add_inputs('input_file_1.csv', 'input_file_2.csv')

ds.add_outputs('output_file_1.csv', 'output_file_2.csv')

ds.publish('Did some awesome data science!')
```
You can also name directories as inputs and outputs.

In the case of a directory as an input, the directory will be scanned and all the files in that directory (or its subdirectories) will be recorded as inputs at the time when `ds.input()`, `ds.add_input()` or `ds.add_inputs()` is called; any new files that crop up later will NOT be included, as it's assumed you'll read the files right after the call, so any subsequently-added files were the result of later processing steps.

In the case of a directory marked as an output, the directory will only be scanned when the run is published. This is because you will most like call `ds.output()` or similar on an empty directory, then a subsequent step will fill that directory with files. The directory name is stored, and when the run is published, that directory (and all its subdirectories) will be scanned for files to record as outputs.

Note that in either case, relative pathnames are interpreted relative to the current working directory; the library will handle converting them into paths relative to the workspace root, as required by the run metadata format.

### Labels

You can attach arbitrary labels to your runs, which can be used to search for them in the Dotscience user interface. As usual, this can be done while returning the label value with `label()`, explicitly with `add_label()`, or en mass with `add_labels()`:

```python
import dotscience as ds

ds.script()
ds.start()

some_library.set_mode(ds.label("some_library_mode", foo))

ds.add_label("algorithm_version","1.3")

ds.add_labels(experimental=True, mode="test")

ds.publish('Did some awesome data science!')
```

### Summary statistics

Often, your job will be able to measure its own performance in some way - perhaps testing how well a model trained on some training data works when tested on some test data. If you declare those summary statistics to Dotscience, it can help you keep track of which runs produced the best results.

As usual, this can be done while returning the summary value with `summary()`, explicitly with `add_summary()`, or en mass with `add_summaries()`:

```python
import dotscience as ds

ds.script()
ds.start()

print('Fit: %f%%' % (ds.summary('fit%', fit),))

ds.add_summary('fit%', fit)

ds.add_summaries(fit=computeFit(), error=computeMeanError())

ds.publish('Did some awesome data science!')
```

### Parameters

Often, the work of a data scientist involves running the same algorithm while tweaking some input parameters to see what settings work best. If you declare your input parameters to Dotscience, it can keep track of them and help you find the best ones!

As usual, this can be done while returning the parameter value with `parameter()`, explicitly with `add_parameter()`, or en mass with `add_parameters()`:

```python
import dotscience as ds

ds.script()
ds.start()

some_library.set_smoothing(ds.parameter("smoothing", 2.0))

ds.add_parameter("outlier_threshold",1.3)

ds.add_parameters(prefilter=True, smooth=True, smoothing_factor=12)

ds.publish('Did some awesome data science!')
```

## Multiple runs

There's nothing to stop you from doing more than one "run" in one go; just call `start()` at the beginning and `publish()` at the end of each.

This might look like this:

```python
import dotscience as ds

ds.script()

ds.start()
data = load_csv(ds.input('training.csv'))
model = train_model(data)
model.save(ds.output('model.mdl'))
ds.publish('Trained the model')

ds.start()
test_data = load_csv(ds.input('test.csv'))
accuracy = test_model(model, test_data)
ds.add_summary('accuracy', accuracy)
ds.publish('Tested the model')
```

Or it might look like this:

```python
import dotscience as ds

ds.script()

# Load the data, but don't report it to Dotscience (yet)
data = load_csv('training.csv')
test_data = load_csv('test.csv')

for smoothing in [1.0, 1.5, 2.0]:
    ds.start()
    # Report that we use the already-loaded data
    ds.add_input('training.csv')
    ds.add_input('test.csv')

    # Train model with the configured smoothing level (informing Dotscience of the input parameter)
    model = train_model(data, smoothing=ds.parameter('smoothing', smoothing))

    # Test model
    accuracy = test_model(model, test_data)

    # Inform Dotscience of the accuracy
    ds.add_summary('accuracy', accuracy)

    # Publish this run
    ds.publish('Tested the model with smoothing %s' % (smoothing,))
```

In that example, we've loaded the data into memory once and re-used it in each run - so we've done that before the call to `start()` to record when the actual run starts; we could have put a call to `end()` just before `publish()`, but `publish()` assumes the run is ended when you publish it anyway.

### Build and deploy models into production

`ds.publish` can, optionally, build and deploy any [registered models](/references/dotscience-python-library/#models) into production.

The default behavior of `ds.publish` is
```python
 ds.publish("description", build=False, deploy=False)
```

Setting `build=True` instructs Dotscience to look for registered model directories in the run, and if present, Dotscience builds docker images for the model. All builds for your account, along with their logs, and status can be found on https://cloud.dotscience.com/models/builds

Setting `deploy=True` instructs Dotscience to build docker images of registered models, and in addition to that, it triggers a model deployment into a default Kubernetes cluster managed by Dotscience. This looks for an available managed deployer (creates one if none exist), and creates a deployment. You can look at the model deployments, their status, versions and logs at https://cloud.dotscience.com/models/deployments.
