# -*- coding: utf-8 -*-
from flet import *
from reader import DependencyReader
from resolver import DependencyResolver
from manager import InputManager
from clean import CleanRequirements
from logo import get_logo
from datetime import datetime
import json


class BaseScreen:
    def __init__(self, app):
        self._app = app
        self._page = None

    def render(self, page: Page):
        page.clean()
        self._page = page
        page.add(self.build())
        page.update()

    def build(self):
        return Column()

class HomeScreen(BaseScreen):
    def build(self):
        return Column(
            alignment="center",
            horizontal_alignment="center",
            spacing=20,
            controls=[
                get_logo(),
                Text("Zepix", size=80, weight=FontWeight.BOLD, color=self._app.accent),
                Text("Smart Dependency Manager", size=40, color=self._app.subtext),
                Row(
                    alignment="center",
                    spacing=20,
                    controls=[
                        FilledTonalButton("📁 Upload File",bgcolor=self._app.accent,color="white",on_click=lambda e: self._app.show("upload")
                        ),
                        OutlinedButton("🖊️ Manual Input",style=ButtonStyle(color=self._app.accent),on_click=lambda e: self._app.show("manual"))
                    ],
                ),
            ],
        )
class UploadScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.selected_path = {"value": ""}
        self.selected_file_name = Text("", size=20, color=app.subtext)
    def build(self):
            fp = self._app.file_picker
            fp.on_result = lambda e: (self.selected_file_name.__setattr__("value", e.files[0].name if e.files and 
              len(e.files) > 0 else "No file selected"),self.selected_path.update({
            "value": e.files[0].path if e.files and len(e.files) > 0 else ""
        }),
            self._page.update()
    )
            upload_box = Container(
             height=220,
             width=550,
             border=border.all(3, self._app.accent),
             border_radius=18,
             bgcolor="#F3EEFF",
             alignment=alignment.center,
             on_click=lambda e: fp.pick_files(allow_multiple=False,allowed_extensions=["txt", "json"]),
             content=Column(
                 alignment="center",
                 horizontal_alignment="center",
                 spacing=10,
                 controls=[
                     Icon(Icons.CLOUD_UPLOAD, size=70, color=self._app.accent),
                     Text("Click to upload your file", size=22, color=self._app.subtext),
                 ],
             ),
             )
            return Column(
                alignment="center",
                horizontal_alignment="center",
                spacing=30,
                controls=[
                    Text("Upload Your File", size=32, weight=FontWeight.BOLD, color=self._app.accent),
                    Row(                      
                        alignment="center",
                        controls=[upload_box]
                    ),
                    self.selected_file_name,
                    FilledButton(
                        "Process File",
                        bgcolor=self._app.accent,
                        color="white",
                        on_click=lambda e: self._app.process_file(self._page, self.selected_path["value"])),
                    OutlinedButton(
                        "Back",style=ButtonStyle(color=self._app.accent),on_click=lambda e: self._app.show("home")),
                ],
            )
class ManualScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.manual_input_text = ""
    def build(self):
        input_box = TextField(
            label="Enter dependencies",
            multiline=True, min_lines=8, max_lines=15, width=500,
            border_color=self._app.accent,
            focused_border_color=self._app.accent,
            on_change=lambda e: setattr(self, "manual_input_text", e.control.value))
        return Column(
            alignment="center",
            horizontal_alignment="center",
            spacing=25,
            controls=[
                Text("Manual Dependency Input", size=32, weight=FontWeight.BOLD, color=self._app.accent),
                Text(
                    "Enter one dependency per line\nExamples:\nrequests==2.31.0\npandas>=1.5\nnumpy\nFlask>=2.0.0",
                    size=14, color=self._app.subtext, text_align="center"),
                input_box,
                Row(
                    alignment="center", spacing=20,
                    controls=[
                        FilledButton(
                            "Process",bgcolor=self._app.accent,color="white",on_click=lambda e: self._app.process_manual(self._page, input_box.value)),
                        OutlinedButton(
                            "Clear",style=ButtonStyle(color="orange"),on_click=lambda e: self.clear_input(input_box)),
                        OutlinedButton("Back",style=ButtonStyle(color=self._app.accent),on_click=lambda e: self._app.show("home")),
                    ],
                ),
            ],
        )
    def clear_input(self, box):
        box.value = ""
        self._page.update()
class AnalysisScreen(BaseScreen):
    def build(self):
        deps = self._app.dependencies
       
        total = len(deps)
        ok = sum(1 for v in deps.values() if v.get("result") == "OK")
        warn = sum(1 for v in deps.values() if v.get("result") == "Warning")
        error = sum(1 for v in deps.values() if v.get("result") == "Error")
        stats_column = Column(
            alignment="center",
            horizontal_alignment="center",
            spacing=8,
            controls=[
                Text(f"Total: {total}", color=self._app.accent, size=18, weight=FontWeight.BOLD, selectable=True),
                Text(f"No Issues: {ok}", color="green", size=18, weight=FontWeight.BOLD, selectable=True),
                Text(f"Warnings: {warn}", color="orange", size=18, weight=FontWeight.BOLD, selectable=True),
                Text(f"Errors: {error}", color="red", size=18, weight=FontWeight.BOLD, selectable=True),
            ],
        )

        packages_list = Column(
            spacing=10,
            expand=True,
            controls=[
                Row(
                    spacing=20,
                    vertical_alignment="start",
                    expand=True,
                    controls=[
                        Text(pkg, size=18, weight=FontWeight.BOLD, selectable=True, expand=True),
                        Text(
                            status.get("result", "").upper(),
                            size=16,
                            weight=FontWeight.BOLD,
                            color=(
                                "#2ecc71" if status.get("result") == "OK" else
                                "#f39c12" if status.get("result") == "Warning" else
                                "#e74c3c"
                            ),
                            selectable=True,width=120
                        ),
                        Text(
                            status.get("details", ""),
                            size=14,color="#444444",selectable=True,expand=True)
                    ],
                )
                for pkg, status in deps.items()
            ],
        )

        return Column(
            scroll=ScrollMode.AUTO,  
            expand=True,
            alignment="center",
            horizontal_alignment="center",
            spacing=25,
            controls=[
                Text("Dependency Analysis", size=32, weight=FontWeight.BOLD,
                     color=self._app.accent, selectable=True),
                stats_column,
                Divider(height=1, color=self._app.subtext),
                Container(
                    content=packages_list,expand=True),
                FilledTonalButton(
                    "Download Clean File",bgcolor=self._app.accent,color="white",on_click=lambda e: self._app.save_clean(self._page)),
                FilledButton(
                    "Back",bgcolor=self._app.accent,color="white",on_click=lambda e: self._app.show("home"))
            ],
        )
class FixOptionsScreen(BaseScreen):
    def build(self):
        deps = self._app.dependencies
        total = len(deps)
        no_issues = sum(1 for v in deps.values() if v.get("result") == "OK")
        problem = total - no_issues
        return Column(scroll=ScrollMode.AUTO,
            alignment="center",
            horizontal_alignment="center",
            spacing=20,
            controls=[
                Text(f"Analysis finished: {total} packages", size=20, weight=FontWeight.BOLD),
                Text(f"No Issues: {no_issues}", size=16, color="green"),
                Text(f"Packages with problem: {problem}", size=16, color="red"),
                Row(
                    alignment="center",
                    spacing=20,
                    controls=[
                        FilledButton("Download Clean File",bgcolor=self._app.accent,on_click=lambda e: self._app.save_clean(self._page)),
                        OutlinedButton("View Report",style=ButtonStyle(color=self._app.accent),on_click=lambda e: self._app.show("analysis")),
                        OutlinedButton("Back",style=ButtonStyle(color=self._app.accent),on_click=lambda e: self._app.show("home"))
                    ]
                )
            ]
        )

class ZepixApp:
    def __init__(self):
        self.bg = "#F5F6FA"
        self.text = "#1f1f1f"
        self.subtext = "#696969"
        self.accent = "#6B3CF0"
        self.dependencies = {}
        self.raw_dependencies = {}
        self.clean_counter = 1
        self.screens = {
            "home": HomeScreen(self),
            "upload": UploadScreen(self),
            "manual": ManualScreen(self),
            "analysis": AnalysisScreen(self),
            "fix": FixOptionsScreen(self)
        }
    def show(self, name):
        self.screens[name].render(self._page)
    def start(self, page: Page):
        self._page = page
        page.title = "Zepix - Smart Dependency Manager"
        page.theme_mode = "light"
        page.bgcolor = self.bg
        self.file_picker = FilePicker()
        page.overlay.append(self.file_picker)
    
        self.show("home")
    def process_file(self, page: Page, filename):
        try:
            if not filename:
                page.snack_bar = SnackBar(Text("No file selected"), bgcolor="#ffa600")
                page.snack_bar.open = True
                page.update()
                return
            reader = DependencyReader(filename)
            deps = reader.read()
            if not isinstance(deps, dict) or not deps:
                page.snack_bar = SnackBar(Text("No dependencies found or file is empty"), bgcolor="#ffa600")
                page.snack_bar.open = True
                page.update()
                return
            self.raw_dependencies = deps
            resolver = DependencyResolver(deps)
            solutions = resolver.analyze()
            self.dependencies = solutions
            page.snack_bar = SnackBar(Text("Processed successfully"), bgcolor=self.accent)
            page.snack_bar.open = True
            page.update()
            self.show("fix")
        except Exception as e:
            page.snack_bar = SnackBar(Text(f"Error: {str(e)}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
    def process_manual(self, page: Page, text):
        if not text.strip():
            page.snack_bar = SnackBar(Text("Please enter some dependencies first!"), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
            return
        try:
            lines = [x.strip() for x in text.split("\n") if x.strip()]
            manager = InputManager()
            deps = manager.manual_input(lines)
            if not deps:
                page.snack_bar = SnackBar(Text("Invalid dependencies"), bgcolor="#ffa600")
                page.snack_bar.open = True
                page.update()
                return
            self.raw_dependencies = deps
            resolver = DependencyResolver(deps)
            self.dependencies = resolver.analyze()
            page.snack_bar = SnackBar(Text("Processed successfully"), bgcolor=self.accent)
            page.snack_bar.open = True
            page.update()
            self.show("fix")
        except Exception as e:
            page.snack_bar = SnackBar(Text(str(e)), bgcolor="red")
            page.snack_bar.open = True
            page.update()
    def save_clean(self, page: Page):
        cleaner = CleanRequirements(
            raw_deps=self.raw_dependencies,
            analyzed=self.dependencies,
            counter=self.clean_counter)
        txt_name, json_name = cleaner.save()
        self.clean_counter = cleaner.counter
        page.snack_bar = SnackBar(
            Text(f"Saved as {txt_name}"), 
            bgcolor=self.accent)
        page.snack_bar.open = True
        page.update()


def main(page: Page):
    app = ZepixApp()
    page.window_height = 700
    page.window_width = 900
    page.window_resizable = True
    app.start(page)


app(target=main)

