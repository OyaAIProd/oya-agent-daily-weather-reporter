import os
import sys
import json
import urllib.request
import urllib.parse

def get_weather():
    input_str = os.environ.get("INPUT_JSON", "{}")
    try:
        inputs = json.loads(input_str)
    except Exception:
        inputs = {}
        
    location = inputs.get("location", "")
    if not location:
        print(json.dumps({"error": "Location is required"}))
        sys.exit(1)
        
    safe_loc = urllib.parse.quote(location)
    url = f"https://wttr.in/{safe_loc}?format=j1"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        current = data.get("current_condition", [{}])[0]
        weather = {
            "location": location,
            "current_temp_C": current.get("temp_C"),
            "current_temp_F": current.get("temp_F"),
            "condition": current.get("weatherDesc", [{}])[0].get("value"),
            "forecast": []
        }
        
        for day in data.get("weather", [])[:3]:
            weather["forecast"].append({
                "date": day.get("date"),
                "max_temp_C": day.get("maxtempC"),
                "min_temp_C": day.get("mintempC"),
                "max_temp_F": day.get("maxtempF"),
                "min_temp_F": day.get("mintempF"),
                "condition": day.get("hourly", [{}])[4].get("weatherDesc", [{}])[0].get("value", "Unknown")
            })
            
        print(json.dumps(weather))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    get_weather()