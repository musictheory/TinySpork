import sublime
import codecs
import subprocess
import threading
import socketserver
import re

HOST, PORT = "localhost", 9666

sProjectToManagerMap = { }

def GetWindow(project_name):
    for w in sublime.windows():
        window_project_name = w.project_file_name()

        if (not window_project_name):
            for folder in w.folders():
                if project_name == folder:
                    return w

            continue

        if (window_project_name.startswith(project_name)):
            return w

    return None


class ProjectIssueManager():
    def __init__(self, window, project):
        self.window = window
        self.issueCount = 0
        
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

    def handleBegin(self):
        self.issueCount = 0
        self.panel.run_command("select_all")
        self.panel.run_command("right_delete")

    def handleEnd(self):
        if (self.issueCount == 0):
            self.window.run_command("hide_panel", { "panel": "output.TinySpork" })

    def handleInfoLine(self, string):
        self.panel.run_command("append", { "characters": string + "\n" })
        self.window.run_command("show_panel", { "panel": "output.TinySpork" })

    def handleErrorLine(self, string):
        self.panel.run_command("append", { "characters": string + "\n" })

        self.issueCount = self.issueCount + 1
        if (self.issueCount > 0):
            self.window.run_command("show_panel", { "panel": "output.TinySpork" })


class SporkTCPHandler(socketserver.ThreadingMixIn, socketserver.StreamRequestHandler):
    def handle(self):
        while 1:
            try:
                line = self.rfile.readline().strip().decode()
                m = re.match('(\[\w+?\])\s*(.*)', line)

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

                    elif (command == "[info]"):
                        if manager: manager.handleInfoLine(rest.strip())

                    elif (command == "[end]"):
                        if manager: manager.handleEnd()
                        break
                else:
                    if manager: manager.handleErrorLine(line)

                if (len(line) == 0): break

            except:
                break

server = None

def serve_forever():
    server.serve_forever()

socketserver.TCPServer.allow_reuse_address = True

server = socketserver.TCPServer((HOST, PORT), SporkTCPHandler)
thread = threading.Thread(target=serve_forever)
thread.start()

def plugin_unloaded():
    print("Unloading", server)
    server.shutdown()
