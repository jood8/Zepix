# -*- coding: utf-8 -*-


from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from pathlib import Path
import json


class DependencyReader:
    def __init__(self, f: str):
        self.file_path = f

    def read(self):

        file_path = Path(self.file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if file_path.stat().st_size == 0:
            return {}
        deps = {}

        
        if file_path.suffix.lower() == ".json":
            return self.read_json(file_path)

       
        with file_path.open("r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()

                if not line or line.startswith("#"):
                    continue

                if "#" in line:
                    line = line.split("#", 1)[0].strip()

                try:
                    req = Requirement(line)
                    deps[req.name] = {
                        "specifier": req.specifier,
                        "extras": list(req.extras) if req.extras else [],
                        "marker": str(req.marker) if req.marker else None,
                        "raw": line
                    }
                except Exception:
                    deps[line] = {
                        "specifier": SpecifierSet(),
                        "extras": [],
                        "marker": None,
                        "raw": line,
                        "note": "Could not parse with Requirement()"
                    }

        return deps

    def read_json(self, file_path: Path):
        deps = {}
        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            return {}
    
        if not isinstance(data, dict):
            return {}
    
        for name, info in data.items():
    
           
            if isinstance(info, str):
               
                if info.startswith(("==", ">=", "<=", ">", "<")):
                    raw_line = f"{name}{info}"
                else:
                    raw_line = info
    
            elif isinstance(info, dict):
                
                raw_line = (
                    info.get("raw")
                    or info.get("version")
                    or info.get("specifier")
                    or ""
                )
                if raw_line.startswith(("==", ">=", "<=", ">", "<")):
                    raw_line = f"{name}{raw_line}"
                if not raw_line:
                    raw_line = name  
    
            else:
                raw_line = name
    
           
            try:
                req = Requirement(raw_line)
                deps[req.name] = {
                    "specifier": req.specifier,
                    "extras": list(req.extras) if req.extras else [],
                    "marker": str(req.marker) if req.marker else None,
                    "raw": raw_line
                }
            except Exception:
                deps[name] = {
                    "specifier": SpecifierSet(),
                    "extras": [],
                    "marker": None,
                    "raw": raw_line,
                    "note": "Could not parse requirement"
                }
    
        return deps