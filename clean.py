# -*- coding: utf-8 -*-


import json

class CleanRequirements:

    def __init__(self, raw_deps: dict, analyzed: dict, counter=1):
        self.raw = raw_deps             
        self.analyzed = analyzed        
        self.counter = counter         

    def save(self):
        cleaned = {}

        for pkg, raw_info in self.raw.items():
            result = self.analyzed.get(pkg, {})
            if result.get("result") == "OK":
                entry = dict(raw_info)
                if "specifier" in entry:
                    entry["specifier"] = str(entry["specifier"])

                cleaned[pkg] = entry
        txt_name = f"Clean_{self.counter}.txt"
        json_name = f"Clean_{self.counter}.json"
        with open(txt_name, "w", encoding="utf-8") as f:
            for pkg, info in cleaned.items():
                f.write(info.get("raw", pkg) + "\n")
        with open(json_name, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=4, ensure_ascii=False)

      
        self.counter += 1

        return txt_name, json_name
