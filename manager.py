# -*- coding: utf-8 -*-


import json
from reader import DependencyReader
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
import re


class InputManager:
    def __init__(self):
        self.dependencies = {}

    def load(self, filename: str):
        if filename.lower().endswith(".json"):
            return self.from_json(filename)
        elif filename.lower().endswith(".txt"):
            return self.from_txt(filename)
        else:
           
            with open(filename, "r", encoding="utf-8") as f:
                first = f.read(20).strip()
                if first.startswith("{"):
                    return self.from_json(filename)
                else:
                    return self.from_txt(filename)

    def from_txt(self, filename):
        reader = DependencyReader(filename)
        self.dependencies = reader.read()
        return self.dependencies

    def from_json(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        deps = {}

        for name, info in data.items():
            raw = info.get("raw", name)
            try:
                req = Requirement(raw)
                deps[req.name] = {
                    "specifier": req.specifier,
                    "extras": list(req.extras) if req.extras else [],
                    "marker": str(req.marker) if req.marker else None,
                    "raw": raw,
                    "note": info.get("note")
                }
            except:
                deps[name] = {
                    "specifier": SpecifierSet(),
                    "extras": [],
                    "marker": None,
                    "raw": raw,
                    "note": "Could not parse JSON requirement"
                }

        self.dependencies = deps
        return deps

    def manual_input(self, dep_list):
        self.dependencies = {}

        for line in dep_list:
            clean = line.strip()
            if not clean:
                continue

            normalized = self.normalize(clean)

            try:
                req = Requirement(normalized)
                self.dependencies[req.name] = {
                    "specifier": req.specifier,
                    "extras": list(req.extras) if req.extras else [],
                    "marker": str(req.marker) if req.marker else None,
                    "raw": normalized,
                    "note": None
                }

            except Exception as e:
                name = re.split(r"[<>=!]", clean)[0].strip()
                self.dependencies[name] = {
                    "specifier": SpecifierSet(),
                    "extras": [],
                    "marker": None,
                    "raw": clean,
                    "note": f"Could not parse: {str(e)}"
                }

        return self.dependencies

    
    def normalize(self, line: str) :
        line = line.replace(" ", "")     
        line = line.replace("===", "==") 
        line = line.replace("=>", ">=") 

       
        ops = ["==", ">=", "<=", "!=", ">", "<"]
        if not any(op in line for op in ops):
            return line   # raw name only

        return line

    
    def validate(self):
        problems = {}

        for name, info in self.dependencies.items():
            raw = info.get("raw", "")
            spec = str(info.get("specifier", ""))

            
            if not name or name.strip() == "":
                problems[name] = "Package name is empty"
                continue

            
            if any(c in name for c in ["@", "/", "\\", "{", "}"]):
                problems[name] = "Invalid characters in package name"
                continue

            
            if spec == "" and "note" not in info:
                problems[name] = "Version is missing"

            
            if info.get("note"):
                problems[name] = info["note"]

           
            if spec == "" and "==" in raw:
                problems[name] = "Malformed version specifier"

        return problems
