import sublime
import threading
import socket, os
import re

sProjectToManagerMap = { }

def GetWindow(project_name):
    for w in sublime.windows():
        window_project_name = w.project_file_name()

        if (not window_project_name):
            for folder in w.folders():
                if project_name == folder:
                    return w

            continue

        if (window_project_name and window_project_name.startswith(project_name)):
            return w

    return None


class ProjectIssueManager():
    def __init__(self, window, project):
        self.window = window
        self.issueCount = 0
        self.groupCount = 0
        self.lines = [ ];
        self.issueMap = { };
        self.project = project

        panel = self.window.create_output_panel("TinySpork")
        panel.settings().set("result_file_regex", "^([^:]*):([0-9]+):?([0-9]+)?:? (.*)$")
        panel.settings().set("result_line_regex", "")
        panel.settings().set("result_base_dir", project)
        panel.settings().set("word_wrap", True)
        panel.settings().set("line_numbers", False)
        panel.settings().set("gutter", False)
        panel.settings().set("scroll_past_end", False)
        panel.assign_syntax("Packages/Text/Plain text.tmLanguage")

        self.panel = panel

    def _append(self, lines):
        self.panel.set_read_only(False)
        self.panel.run_command("append", { "characters": "\n".join(lines) + "\n", "scroll_to_end": True })
        self.panel.set_read_only(True)


    def _flush(self):
        for line in self.lines:
            m = re.match("^([^:]*):([0-9]+):?([0-9]+)?:? (.*)$", line)
            if m:
                file = m.group(1).strip()
                lineNumber = int(m.group(2))

                if file in self.issueMap:
                    self.issueMap[file].append(lineNumber)
                else:
                    self.issueMap[file] = [ lineNumber ]

        self._append(self.lines);

        if (self.issueCount > 0):
            self.window.run_command("show_panel", { "panel": "output.TinySpork" })

        self.lines = [ ]

    def handleBegin(self):
        self.issueCount = 0
        self.panel.set_read_only(False)
        self.panel.run_command("select_all")
        self.panel.run_command("right_delete")
        self.panel.set_read_only(True)

    def handleEnd(self):
        for view in self.window.views():
            view.erase_regions("TinySpork")

        if (self.issueCount == 0):
            self.window.run_command("hide_panel", { "panel": "output.TinySpork" })
        else:
            for key in self.issueMap:
                view = self.window.find_open_file(self.project + "/" + key)
                if view:
                    icon  = view.settings().get("tiny_spork_icon", "dot")
                    scope = view.settings().get("tiny_spork_scope", "invalid")

                    regions = [ ]
                    for lineNumber in self.issueMap[key]:
                        regions.append(sublime.Region(
                            view.text_point(lineNumber - 1, 0),
                            view.text_point(lineNumber, 0) - 1
                        ))

                    view.add_regions("TinySpork", regions, scope, icon, sublime.DRAW_NO_OUTLINE | sublime.DRAW_NO_FILL | sublime.DRAW_STIPPLED_UNDERLINE)

        self.issueMap = { }

    def handleStartLines(self):
        self.groupCount = self.groupCount + 1

    def handleEndLines(self):
        self.groupCount = self.groupCount - 1

        if (self.groupCount == 0):
            self._flush();

    def handleErrorLine(self, line):
        self.lines.append(line)
        self.issueCount = self.issueCount + 1

        if (self.groupCount == 0):
            self._flush();

    def handleInfoLine(self, string):
        self._append([ string ])
        self.window.run_command("show_panel", { "panel": "output.TinySpork" })



def serve_forever():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        os.remove("/tmp/TinySpork.sock")
    except OSError:
        pass

    s.bind("/tmp/TinySpork.sock")
    s.listen(5)

    while (1):
        conn, addr = s.accept()
        manager = None

        sublime.status_message("Building");

        f = conn.makefile() 

        for l in f:
            try:
                line = l.strip()
                m = re.match('(\[[-\w]+?\])\s*(.*)', line)

                if m:
                    command = m.group(1)
                    rest    = m.group(2)

                    if (command == "[begin]"):
                        project = rest.strip()
                        manager = sProjectToManagerMap.get(project, None)

                        if (not manager):
                            w = GetWindow(project)

                            if (w):
                                manager = ProjectIssueManager(w, project)
                                sProjectToManagerMap[project] = manager

                        if manager: manager.handleBegin()

                    elif (command == "[start-lines]"):
                        if manager: manager.handleStartLines();

                    elif (command == "[end-lines]"):
                        if manager: manager.handleEndLines();

                    elif (command == "[info]"):
                        if manager: manager.handleInfoLine(rest.strip())

                    elif (command == "[end]"):
                        if manager: manager.handleEnd()
                        break
                else:
                    if manager: manager.handleErrorLine(line)

                if (len(line) == 0): break

            except Exception as e:
                print(e);
                break

        sublime.status_message("");

        conn.close()


thread = threading.Thread(target=serve_forever)
thread.start()
