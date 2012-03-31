import sublime
import sublime_plugin
import threading
import subprocess

stdout = ""
stderr = ""


def show_panel():
    view = sublime.active_window().active_view()
    if len(stderr) > 0:
        if stderr.count("\n") == 1:
            sublime.status_message("CGC: %s" % stderr)
            return
        v = view.window().get_output_panel("cgc")
        v.settings().set("result_file_regex", "^(.+)\((\d+)\)")
        view.window().get_output_panel("cgc")
        v.set_read_only(False)
        v.set_scratch(True)
        e = v.begin_edit()
        v.insert(e, 0, stderr)
        v.end_edit(e)
        v.set_read_only(True)
        view.window().run_command("show_panel", {"panel": "output.cgc"})


def compile(cmd):
    global stdout
    global stderr

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    sublime.set_timeout(show_panel, 0)

fragmentExtensions = [".glslf", ".frag", ".fs"]
vertexExtensions = [".glslv", ".vert", ".vs"]


class CGCCompile(sublime_plugin.EventListener):
    def on_post_save(self, view):
        fn = view.file_name()
        idx = fn.rfind(".")
        if idx != -1:
            ext = fn[idx:]
            cmd = None
            if ext in fragmentExtensions:
                cmd = "cgc -nocode -ogles -profile fp40 %s" % fn
                cmd = cmd.split()
            elif ext in vertexExtensions:
                cmd = "cgc -nocode -ogles -profile vp40 %s" % fn
                cmd = cmd.split()

            if not cmd is None:
                t = threading.Thread(target=compile, args=(cmd,))
                t.start()
