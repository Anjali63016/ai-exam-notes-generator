import google.generativeai as genai

genai.configure(
    api_key="AIzaSyB72B4ukFX67QVPjK6fbZpFv8uSKZixnpw"
)

models = genai.list_models()

for model in models:
    print(model.name)