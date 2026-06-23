import os
import json
import sys

def main():
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))
    html_content = inp.get("html_content")
    filename = inp.get("filename", "weather_report.html")

    if not html_content:
        print(json.dumps({"error": "html_content is required"}))
        return

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Sandbox convention to surface the file to the user/workspace
        print(f"A2ABASEAI_FILE: {os.path.abspath(filename)}")
        print(json.dumps({"ok": True, "file_path": filename}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()