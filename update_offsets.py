import requests

print("Updating offsets...")
with open("resources/offsets.json", "w") as f:
    f.write(requests.get("https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.json").text)

print("Done.")