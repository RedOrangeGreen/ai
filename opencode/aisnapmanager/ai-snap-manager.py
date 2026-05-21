#!/usr/bin/env python3
import os
os.environ["GTK_MODULES"] = ""

import gi
import re
import subprocess
import signal
import threading
import shlex
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

SNAPS = [
    ("deepseek-r1",         "DeepSeek R1"),
    ("gemma3",              "Gemma 3 (default)"),
    ("gemma4",              "Gemma 4"),
    ("nemotron-3-nano",     "Nemotron 3 Nano"),
    ("nemotron-3-nano-omni","Nemotron 3 Nano Omni"),
    ("qwen-vl",             "Qwen VL"),
]


def idle(fn):
    GLib.idle_add(fn)


class LogPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.set_min_content_height(120)

        self.buffer = Gtk.TextBuffer()
        self.buffer.create_tag("prompt", foreground="#bbb")
        self.buffer.create_tag("stdout", foreground="#fff")
        self.buffer.create_tag("stderr", foreground="#f99")

        self.textview = Gtk.TextView(buffer=self.buffer)
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_data(b"""
            textview, textview text {
                background-color: #000000;
                color: #ffffff;
                font-family: monospace;
                font-size: 9pt;
            }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1
        )

        sw.add(self.textview)
        self.pack_start(sw, True, True, 0)

    def write(self, text, tag=None):
        end = self.buffer.get_end_iter()
        self.buffer.insert_with_tags_by_name(end, text, tag) if tag \
            else self.buffer.insert(end, text)
        m = self.buffer.get_mark("insert")
        if m:
            self.textview.scroll_to_mark(m, 0, False, 0, 0)


class Gemma3Manager(Gtk.Window):
    def __init__(self):
        super().__init__(title="Inference Snap Manager")
        self.set_default_size(600, 480)
        self.set_border_width(12)
        self.connect("destroy", Gtk.main_quit)

        self.snap = "gemma3"

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.add(vbox)

        mb = Gtk.MenuBar()
        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem(label="Help")
        help_item.set_submenu(help_menu)
        doc_item = Gtk.MenuItem(label="Documentation")
        doc_item.connect("activate", lambda _: (
            self.log.write("$ Opening https://documentation.ubuntu.com/inference-snaps/\n", "prompt"),
            __import__("webbrowser").open("https://documentation.ubuntu.com/inference-snaps/")))
        help_menu.append(doc_item)
        mb.append(help_item)
        vbox.pack_start(mb, False, False, 0)

        lbl = Gtk.Label()
        lbl.set_markup("<b>Inference Snap Manager</b>  —  Native AI for Ubuntu")
        lbl.set_halign(Gtk.Align.START)
        vbox.pack_start(lbl, False, False, 0)

        hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        slbl = Gtk.Label(label="Snap:")
        self.snap_combo = Gtk.ComboBoxText()
        for snap_id, snap_name in SNAPS:
            self.snap_combo.append(snap_id, snap_name)
        self.snap_combo.set_active(1)
        self.snap_combo.connect("changed", self.on_snap_changed)
        hb.pack_start(slbl, False, False, 0)
        hb.pack_start(self.snap_combo, True, True, 0)
        vbox.pack_start(hb, False, False, 0)

        self.buttons = {}
        for label, handler in [
            ("Install And Start",   self.on_install),
            ("Use Web UI",    self.on_web),
            ("Start",     self.on_start),
            ("Stop",      self.on_stop),
            ("Uninstall", self.on_uninstall),
        ]:
            btn = Gtk.Button(label=label)
            btn.connect("clicked", handler)
            btn.set_size_request(-1, 36)
            vbox.pack_start(btn, False, False, 0)
            self.buttons[label] = btn

        vbox.pack_start(Gtk.HSeparator(), False, False, 8)

        for label, handler in [
            ("Use CLI",       self.on_cli),
            ("How To Use API",       self.on_api),
        ]:
            btn = Gtk.Button(label=label)
            btn.connect("clicked", handler)
            btn.set_size_request(-1, 36)
            vbox.pack_start(btn, False, False, 0)
            self.buttons[label] = btn

        self.status_bar = Gtk.Statusbar()
        self.status_ctx = self.status_bar.get_context_id("status")
        vbox.pack_end(self.status_bar, False, False, 0)

        self.log = LogPanel()
        vbox.pack_end(self.log, True, True, 0)

        self.set_status("Ready")
        self.show_all()
        self.refresh_buttons()

    def set_status(self, msg):
        plain = re.sub(r"</?[^>]+>", "", msg)
        self.status_bar.push(self.status_ctx, plain)

    def refresh_buttons(self):
        installed = self.is_installed()
        running = self.service_status() == "active" if installed else False
        self.buttons["Install And Start"].set_sensitive(not installed)
        self.buttons["Uninstall"].set_sensitive(installed)
        self.buttons["Start"].set_sensitive(installed and not running)
        self.buttons["Stop"].set_sensitive(installed and running)
        self.buttons["Use Web UI"].set_sensitive(running)
        self.buttons["Use CLI"].set_sensitive(running)
        self.buttons["How To Use API"].set_sensitive(running)

    def on_snap_changed(self, combo):
        self.snap = combo.get_active_id()
        self.set_status(f"Switched to {self.snap}")
        self.refresh_buttons()

    def _dlg(self, msg, msg_type, buttons):
        d = Gtk.MessageDialog(transient_for=self, flags=0,
                              message_type=msg_type, buttons=buttons)
        d.set_markup(msg)
        return d

    def info_dialog(self, msg):
        d = self._dlg(msg, Gtk.MessageType.INFO, Gtk.ButtonsType.OK)
        d.run()
        d.destroy()

    def confirm_dialog(self, msg):
        d = self._dlg(msg, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO)
        resp = d.run()
        d.destroy()
        return resp == Gtk.ResponseType.YES

    def quick(self, cmd):
        return subprocess.run(cmd, capture_output=True, text=True, timeout=15)

    def is_installed(self):
        return self.quick(["snap", "list", self.snap]).returncode == 0

    def service_status(self):
        r = self.quick(["snap", "services", self.snap])
        for line in r.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 3 and self.snap in parts[0]:
                return parts[2]
        return "inactive"

    def stream_cmd(self, cmd, label=None):
        display = " ".join(shlex.quote(str(a)) for a in cmd)
        if label:
            display = f"{label}  ——  {display}"
        idle(lambda: self.log.write(f"$ {display}\n", "prompt"))

        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        def reader(pipe, tag, dest):
            for line in iter(pipe.readline, ""):
                idle(lambda l=line, t=tag: self.log.write(l, t))
                dest.append(line)
            pipe.close()

        stdout_lines = []
        stderr_lines = []
        t1 = threading.Thread(target=reader, args=(proc.stdout, "stdout", stdout_lines), daemon=True)
        t2 = threading.Thread(target=reader, args=(proc.stderr, "stderr", stderr_lines), daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        proc.wait()

        rc = proc.returncode
        idle(lambda: self.log.write(
            f"→ exit {rc}\n\n", "prompt"))
        return rc, "".join(stdout_lines), "".join(stderr_lines)

    def run_async(self, cmd, done_msg, fail_msg=None, label=None):
        self.set_status(label or "Running ...")
        def task():
            rc, *_ = self.stream_cmd(cmd, label=label)
            return rc
        def done(rc):
            if rc == 0:
                self.set_status(done_msg)
                self.info_dialog(done_msg)
            else:
                self.set_status(fail_msg or "Failed")
                self.info_dialog(fail_msg or "Command failed.")
            self.refresh_buttons()
        def wrapper():
            rc = task()
            idle(lambda: done(rc))
        threading.Thread(target=wrapper, daemon=True).start()

    def on_install(self, _btn):
        if self.is_installed():
            self.info_dialog(f"<b>{self.snap}</b> is already installed.")
            return
        def task():
            self.set_status("Installing ...")
            rc, *_ = self.stream_cmd(
                ["sudo", "snap", "install", self.snap, "--beta"],
                label="Install")
            if rc != 0:
                idle(lambda: self.set_status(f"Failed to install <b>{self.snap}</b>."))
                idle(lambda: self.info_dialog(f"Failed to install <b>{self.snap}</b>."))
                idle(lambda: self.refresh_buttons())
                return
            self.set_status("Starting ...")
            rc, *_ = self.stream_cmd(
                ["sudo", "snap", "start", self.snap],
                label="Start")
            if rc == 0:
                self.set_status("Checking status ...")
                self.stream_cmd([self.snap, "status"], label="Status")
                idle(lambda: self.set_status(f"<b>{self.snap}</b> installed and started."))
                idle(lambda: self.info_dialog(f"<b>{self.snap}</b> installed and started."))
            else:
                idle(lambda: self.set_status(f"Installed but failed to start <b>{self.snap}</b>."))
                idle(lambda: self.info_dialog(f"Installed but failed to start <b>{self.snap}</b>."))
            idle(lambda: self.refresh_buttons())
        threading.Thread(target=task, daemon=True).start()

    def on_uninstall(self, _btn):
        if not self.is_installed():
            self.info_dialog(f"<b>{self.snap}</b> is not installed.")
            return
        if not self.confirm_dialog(f"Remove <b>{self.snap}</b>?"):
            return
        self.run_async(
            ["sudo", "snap", "remove", self.snap],
            f"<b>{self.snap}</b> removed.",
            f"Failed to remove <b>{self.snap}</b>.")

    def on_start(self, _btn):
        if self.service_status() == "active":
            self.info_dialog(f"<b>{self.snap}</b> services are already active.")
            return
        self.run_async(
            ["sudo", "snap", "start", self.snap],
            f"<b>{self.snap}</b> services started.",
            f"Failed to start <b>{self.snap}</b>.")

    def on_stop(self, _btn):
        if self.service_status() != "active":
            self.info_dialog(f"<b>{self.snap}</b> services are not running.")
            return
        self.run_async(
            ["sudo", "snap", "stop", self.snap],
            f"<b>{self.snap}</b> services stopped.",
            f"Failed to stop <b>{self.snap}</b>.")

    def on_cli(self, _btn):
        import shutil
        cmd_str = f"{self.snap} chat; exec bash"
        terms = {
            "ptyxis":         ["ptyxis", "--", "bash", "-c", f"{self.snap} chat; exec bash"],
            "gnome-terminal": ["gnome-terminal", "--", "bash", "-c", cmd_str],
            "kgx":            ["kgx", "-e", "bash", "-c", cmd_str],
            "xfce4-terminal": ["xfce4-terminal", "-e", f"bash -c '{cmd_str}'"],
            "lxterminal":     ["lxterminal", "-e", f"bash -c '{cmd_str}'"],
            "x-terminal-emulator": ["x-terminal-emulator", "--", "bash", "-c", f"{self.snap} chat; exec bash"],
            "xterm":          ["xterm", "-e", f"bash -c '{cmd_str}'"],
        }
        for name, cmd in terms.items():
            if shutil.which(name):
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                return
        self.info_dialog("No terminal emulator found.")

    def on_api(self, _btn):
        r = self.quick([self.snap, "status"])
        url = "http://localhost:8328/v1"
        for line in r.stdout.splitlines():
            line = line.strip()
            if line.startswith("openai:"):
                url = line.split(":", 1)[1].strip()
                break

        code = f'''# python3 -m venv venv
# source venv/bin/activate
# pip install openai
# python3 api_example.py

from openai import OpenAI

client = OpenAI(
    base_url="{url}",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="{self.snap}",
    messages=[{{"role": "user", "content": "Why is the sky blue?"}}]
)

print(response.choices[0].message.content)'''

        d = Gtk.Dialog(title="OpenAI-Compatible API", transient_for=self, flags=0)
        d.add_button("Copy", 1)
        d.add_button("Close", Gtk.ResponseType.CLOSE)
        d.set_default_size(500, 360)

        box = d.get_content_area()
        box.set_spacing(8)

        lbl = Gtk.Label()
        lbl.set_markup(f"Endpoint: <tt>{url}</tt>")
        lbl.set_halign(Gtk.Align.START)
        box.pack_start(lbl, False, False, 0)

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.set_min_content_height(250)

        buf = Gtk.TextBuffer()
        buf.set_text(code)
        tv = Gtk.TextView(buffer=buf)
        tv.set_editable(False)
        tv.set_cursor_visible(True)
        tv.set_wrap_mode(Gtk.WrapMode.NONE)
        css = Gtk.CssProvider()
        css.load_from_data(b"""
            textview { font-family: monospace; font-size: 9pt; }
        """)
        tv.get_style_context().add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        sw.add(tv)
        box.pack_start(sw, True, True, 0)
        d.show_all()

        resp = d.run()
        if resp == 1:
            clip = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clip.set_text(code, -1)
        d.destroy()

    def on_web(self, _btn):
        import webbrowser
        r = self.quick([self.snap, "status"])
        for line in r.stdout.splitlines():
            line = line.strip()
            if line.startswith("webui:"):
                url = line.split(":", 1)[1].strip()
                self.log.write(f"$ Opening {url}\n", "prompt")
                webbrowser.open(url)
                return
        self.log.write("$ Web UI not found, trying localhost:8329\n", "prompt")
        webbrowser.open("http://localhost:8329")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gemma3Manager()
    Gtk.main()
