import joblib


def predict(model, query):
    """
    Default implementation of model prediction.

    Accepts an already-loaded model object and a decoded-from-JSON query, must
    return a response that can be encoded as JSON.

    If you want to change the prediction logic, just modify this function.
    """
    # The default implementation takes a JSON object whose "instances" key has a
    # value that is a list that can be converted to a NumPy array.
    instances = query["instances"]
    try:
        inputs = np.array(instances)
    except Exception as e:
        raise Exception(
            "Failed to initialize NumPy array from inputs: %s, %s" % (e, instances)
        )

    # The default implementation returns a JSON object with "predictions" key
    # whose value is the result of predict_proba():
    result = model.predict_proba(inputs).tolist()
    return {"predictions": result}


def load_model(path):
    """Load an sklearn model."""
    return joblib.load(path)


def save_model(model, path):
    """Save a model to disk."""
    joblib.dump(model, path)


# You should customize this with inputs to the predict() function and their
# expected output, and then test() below will test your predict() function using
# them.
#
# Specifically, this should be a list of tuples, each of the form (input,
# output) where input will be passed to predict() and output should match
# predict()'s result.
TEST_PAIRS = []


def test():
    """
    Test infrastructure.

    You should fill some values in once your model is implemented, so you can
    ensure your prediction logic works as expected.

    This expects you have a "model.joblib" file on disk already in same
    directory as this file.
    """
    import os, json
    model = load_model(os.path.join(os.path.dirname(__file__), "model.joblib"))

    for input_query, expected_output in TEST_PAIRS:
        output = predict(model, input_query)
        assert output == expected_output
        # Make sure the output is JSON serializable:
        json.dumps(output)


if __name__ == '__main__':
    test()
