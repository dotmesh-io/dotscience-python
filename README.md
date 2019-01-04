# dotscience-python

Hi! Welcome to the python library for helping you instrument your
[Dotscience](https://www.dotscience.com/) workloads.

Instrumenting your workloads means making them output metadata about
what they're doing - which Dotscience can collect and use to make your
life easier!

## Installation

You can get the Dotscience python library in one of three ways.

### Use the ready-made Docker image

We've made a Docker image by taking the stock `python:3` image and pre-installing the Dotscience library like so:

```
$ docker run -ti quay.io/dotmesh/dotscience-python3:latest
Python 3.7.0 (default, Aug  4 2018, 02:33:39) 
[GCC 6.3.0 20170516] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import dotscience as ds
```

### Install it from PyPi

```
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

### Use the ready-made Jupyter image

The default Dotscience Jupyter images all have the latest version of the Dotscience python library bundled as standard, so you can just use it in your notebooks:

```python
import dotscience as ds
```

## Quick Start

The most basic usage is to record what data files you read and write, and maybe to declare some summary statistics about how well the job went.

```python
import dotscience as ds
import pandas as pd

ds.interactive()

# Wrap the names of files you read with ds.input() - it just returns the filename:
df = pd.read_csv(ds.input('input_file.csv'))

# Likewise with files you write to:
df.to_csv(ds.output('output_file.csv'))

# Record a summary statistic about how well your job went
ds.add_summary('f-score', f_score)

ds.publish('Did some awesome data science!')
```

Don't forget to call `ds.interactive()` at the top if you're using Jupyter, and `ds.publish()` at the end, or your results won't get published! (The run description string passed in is optional, so leave it out if you can't think of anything nice to say).

## Interactive vs. Script mode

The library has two modes - interactive and script. That call to `ds.interactive()` in the example above puts it in interactive mode, which tells it there isn't a script file that the code is coming from. But when you're writing code in a Python script file, you should call `ds.script()` instead.

This instructs the library to record the script filename (from `sys.argv[0]`) in the output runs, so they can be tracked back to the originating script. You don't need this in interactive mode, because Dotscience knows which Jupyter notebook you're using - and `sys.argv[0]` points to the Jupyter Python kernel in that case, which isn't useful to record in the run!

If `sys.argv[0]` isn't helpful in some other situation, you can call `ds.script('FILENAME')` to specify the script file, relative to the current working directory. In fact, in a Jupyter notebook, you could specify `ds.script('my-notebook.ipynb')` to manually specify the notebook file and override the automatic recording of the notebook file, but there wouldn't be any point!

## All the things you can record

There's a lot more than just data files and summary stats that Dotscience will keep track of for you - and there's a choice of convenient ways to specify each thing, so it can fit neatly into your code. Here's the full list:

### Start and end time

The library will try to guess when your job starts and ends, from when you load the `dotscience` module until you call `publish()` (although it gets a bit more complex with multiple runs; see below).

If you're running in Jupyter, that means it'll include the time you spend working on your notebook, thinking, and so on as well as the time actually spent running the steps, which probably isn't what you want. To get better tracking of the run times, to keep track of what operations are slow and to cross-reference the time periods against other stuff running on the same computers to see if the workloads are interfering, it's a good idea to explicitly tell Dotscience when your steps start and stop.

Even when running Python scripts through `ds run`, it still helps to declare start and end times - if your script does a lot of tedious setup and teardown, you probably don't want those included in the run times.

Just call `start()` and `end()` before and after the real work and the library will record the current time when those functions are called. If you miss the `end()` it'll assume that your run has finished when you call `publish()`; this is often a good assumption, so you can often just call `start()` at the start and `publish()` at the end and be done with it.

```python
import dotscience as ds

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

...
ds.set_error('The data wasn't correctly formatted')
...

ds.publish('Tried, in vain, to do some awesome data science!')
```

If you're assembling an error message to use for some other reason, the dotscience library can just grab a copy of it before you use it, with this convenience function that returns its argument:

```python
import dotscience as ds

...
raise DataFormatError(ds.error('The data wasn't correctly formatted'))
...

ds.publish('Tried, in vain, to do some awesome data science!')
```

### Describing the run

It's good to record a quick human-readable description of what your run did, which helps people who are viewing the provenance graph. We've already seen how to pass a description into `publish()`:

```python
import dotscience as ds

ds.publish('Did some awesome data science!')
```

But you can set up a description before then and just call `publish()` with no arguments:

```python
import dotscience as ds

...
ds.set_description('Did some awesome data science!')
...

ds.publish()
```

And if you're already making a descriptive string to send somewhere else, you can also use this function, that returns its argument:

```python
import dotscience as ds

...
log.write(ds.description('Did some awesome data science!'))
...

ds.publish()
```

### Input and Output files

In order to correctly track the provenance of data files, Dotscience needs you to correctly declare what data files your jobs read and write.

The most convenient way to do this is with `input()` and `output()`, which accept the name of a file to be used for input or output respectively, and return it:

```python
import dotscience as ds

df.from_csv(ds.input('input_file.csv'))

df.to_csv(ds.output('output_file.csv'))

ds.publish('Did some awesome data science!')
```

But you can also declare them explicitly with `add_input()` and `add_output()`:

```python
import dotscience as ds

ds.add_input('input_file.csv')

ds.add_output('output_file.csv')

ds.publish('Did some awesome data science!')
```

Or declare several at once with `add_inputs()` and `add_outputs()`:

```python
import dotscience as ds

ds.add_inputs('input_file_1.csv', 'input_file_2.csv')

ds.add_outputs('output_file_1.csv', 'output_file_2.csv')

ds.publish('Did some awesome data science!')
```

### Labels

You can attach arbitrary labels to your runs, which can be used to search for them in the Dotscience user interface. As usual, this can be done while returning the label value with `label()`, explicitly with `add_label()`, or en mass with `add_labels()`:

```python
import dotscience as ds

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

some_library.set_smoothing(ds.parameter("smoothing", 2.0))

ds.add_parameter("outlier_threshold",1.3)

ds.add_parameters(prefilter=True, smooth=True, smoothing_factor=12)

ds.publish('Did some awesome data science!')
```

## Multiple runs

There's nothing to stop you from doing more than one "run" in one go; just call `publish()` at the end of each.

This might look like this:

```python
import dotscience as ds

data = load_csv(ds.input('training.csv'))
model = train_model(data)
model.save(ds.output('model.mdl'))
ds.publish('Trained the model')

test_data = load_csv(ds.input('test.csv'))
accuracy = test_model(model, test_data)
ds.add_summary('accuracy', accuracy)
ds.publish('Tested the model')
```

Or it might look like this:

```python
import dotscience as ds

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

In that example, we've loaded the data into memory once and re-used it in each run - so we've put in an explicit call to `start()` to record when the actual run starts; we could have put a call to `end()` just before `publish()`, but `publish()` assumes the run is ended when you publish it anyway. If you don't call `start()` and `end()` at all when there's multiple calls to `publish()`, Dotscience will try to be smart about guessing what the start and end times are - the first run will go from when the `dotscience` module is imported until the first `publish()`; then subsequent runs will be timed from the last `publish()` to the next.
