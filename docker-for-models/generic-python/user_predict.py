"""API for predictions.

This will get overwritten by the user's custom prediction logic.
"""

MODEL = object()

def predict(model, query):
    return {"query": query}
