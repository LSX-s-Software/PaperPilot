from server.config import data

gpt = data["gpt"]

url = gpt.get("url", "https://api.openai.com/v1/engines/davinci/completions")
proxy = gpt.get("proxy", None)
