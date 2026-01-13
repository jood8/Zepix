# -*- coding: utf-8 -*-

from reader import DependencyReader
import re
from packaging.specifiers import SpecifierSet
from packaging.version import Version, InvalidVersion



class DependencyResolver:
    def __init__(self, dep):
        self.dependencies = dep
        self.solutions = {}

    def analyze(self):
        for name, info in self.dependencies.items():
            raw = info.get("raw", name)
            spec = info.get("specifier", None)
            note = info.get("note")
            if note:
                self.solutions[name] = {
                    "result": "Error",
                    "details": f"Problem detected: {note}. Suggested fix: check version."
                }
                continue
            if not spec or str(spec) == "":
                self.solutions[name] = {
                    "result": "Warning",
                    "details": "No version specified. Suggested fix: pin a version (e.g., pkg==1.2.3)."
                }
                continue
            try:
                _ = SpecifierSet(str(spec))
            except:
                self.solutions[name] = {
                    "result": "Error",
                    "details": f"Malformed specifier: {spec}. Suggested fix: correct the operator."
                }
                continue
            conflict = self._check_conflicts(specifier=str(spec))
            if conflict:
                self.solutions[name] = {
                    "result": "Error",
                    "details": f"Version conflict detected: {conflict}"
                }
                continue
            else:
                self.solutions[name] = {
                    "result": "OK",
                    "details": "No issues detected."
                }

        return self.solutions
    def _check_conflicts(self, specifier: str):
       
        try:
            spec = SpecifierSet(specifier)
        except:
            return "Invalid specifier."

        test_versions = ["0.1", "1.0", "2.0", "5.0", "10.0"]

        valid = False
        for v in test_versions:
            try:
                if Version(v) in spec:
                    valid = True
                    break
            except InvalidVersion:
                pass

        if not valid:
            return "Constraints do not allow any valid version."

        return None