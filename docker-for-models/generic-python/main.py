from flask import Flask, request, jsonify
import joblib
import pickle
import numpy as np
import os
import http
import sys
import tarfile
import tempfile
from subprocess import check_call

import user_predict

app = Flask(__name__)

@app.route("/v1/healthcheck")
def healthcheck():
    return "OK"

# TF Serving here returns a bigger response with available models
# {
#   "model_version_status": [
#     {
#       "version": "1",
#       "state": "AVAILABLE",
#       "status": {
#         "error_code": "OK",
#         "error_message": ""
#       }
#     }
#   ]
# }
# We might want to return something similar
@app.route("/v1/models/model", methods=["GET"])
def models():
    return "AVAILABLE"


@app.route("/v1/models/model:predict", methods=["POST"])
def http_predict():
    data = request.get_json(force=True)
    try:
        model = app.config["MODEL"]
        return jsonify(user_predict.predict(model, data))
    except Exception as e:
        logging.exception("Failed to predict")
        raise Exception("Failed to predict %s" % e)


if __name__ == "__main__":
    app.config["MODEL"] = user_predict.load_model()
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = os.environ.get("FLASK_PORT", "8501")
    app.run(host=host, port=port)
