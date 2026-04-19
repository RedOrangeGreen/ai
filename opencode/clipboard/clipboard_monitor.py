#!/usr/bin/env python3
# Author: opencode (opencode.ai), Date: 2026-04-19, Version: big-pickle
# Usage: Run with: python3 ./clipboard_monitor.py (requires: sudo apt install xclip python3-gi)

import subprocess
import threading
import time
import sys
import warnings
import os

warnings.filterwarnings('ignore', category=DeprecationWarning)

def check_command(cmd):
  try:
    subprocess.run(cmd, capture_output=True, timeout=2)
    return True
  except FileNotFoundError:
    return False
  except Exception:
    return True

def install_package(pkg):
  try:
    result = subprocess.run(
      ['pkexec', 'apt', 'install', '-y', pkg],
      capture_output=True, text=True, timeout=120
    )
    return result.returncode == 0
  except Exception:
    return False

def show_error(msg):
  err = Gtk.MessageDialog(
    None, 0,
    Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
    msg
  )
  err.run()
  sys.exit(1)

try:
  import gi
  gi.require_version('Gtk', '3.0')
  from gi.repository import Gtk, GLib
except ImportError:
  show_error("python3-gi is required but could not be imported.")

missing = []
if not check_command(['xclip', '-selection', 'clipboard', '-o']):
  missing.append('xclip')
if not check_command(['python3', '-c', 'import gi']):
  missing.append('python3-gi')

if missing:
  class InstallDialog(Gtk.Window):
    def __init__(self, pkgs):
      super().__init__(title="Missing Dependencies")
      self.set_resizable(False)
      self.set_default_size(350, 150)
      self.connect("destroy", Gtk.main_quit)

      box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
      box.set_margin_start(20)
      box.set_margin_end(20)
      box.set_margin_top(20)
      box.set_margin_bottom(20)
      self.add(box)

      msg = "The following packages are required but not installed:"
      box.pack_start(Gtk.Label(label=msg), True, True, 0)

      pkg_label = ", ".join(pkgs)
      box.pack_start(Gtk.Label(label=pkg_label), True, True, 0)

      btn_box = Gtk.Box(spacing=10)
      btn_box.set_halign(Gtk.Align.CENTER)
      box.pack_start(btn_box, True, True, 0)

      install_btn = Gtk.Button(label="Install Now")
      install_btn.connect("clicked", self.on_install, pkgs)
      btn_box.pack_start(install_btn, True, True, 0)

      exit_btn = Gtk.Button(label="Exit")
      exit_btn.connect("clicked", self.on_exit)
      btn_box.pack_start(exit_btn, True, True, 0)

    def on_install(self, widget, pkgs):
      for pkg in pkgs:
        if not install_package(pkg):
          err = Gtk.MessageDialog(
            self, Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
            f"Failed to install {pkg}. Please install manually:\n  sudo apt install {pkg}"
          )
          err.run()
          err.destroy()
          sys.exit(1)
      self.destroy()
      os.execv(sys.executable, [sys.executable, sys.argv[0]])

    def on_exit(self, widget):
      sys.exit(0)

  InstallDialog(missing).show_all()
  Gtk.main()
  sys.exit(0)

class ClipboardMonitor(Gtk.Window):
  def __init__(self):
    super().__init__(title="Clipboard Monitor")
    self.set_default_size(300, 150)
    self.connect("destroy", Gtk.main_quit)

    self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    self.box.set_halign(Gtk.Align.CENTER)
    self.box.set_valign(Gtk.Align.CENTER)
    self.box.set_margin_start(20)
    self.box.set_margin_end(20)
    self.box.set_margin_top(20)
    self.box.set_margin_bottom(20)
    self.add(self.box)

    self.label = Gtk.Label(label="Checking clipboard...")
    self.box.pack_start(self.label, True, True, 0)

    self.clear_button = Gtk.Button(label="Clear clipboard")
    self.clear_button.connect("clicked", self.on_clear_clicked)
    self.box.pack_start(self.clear_button, True, True, 0)

    self.status_thread = threading.Thread(target=self.check_clipboard_loop, daemon=True)
    self.status_thread.start()

    self.prev_state = None
    self.check_clipboard()

  def check_clipboard(self):
    try:
      result = subprocess.run(
        ['xclip', '-selection', 'clipboard', '-o'],
        capture_output=True, text=True, timeout=2
      )
      has_content = result.returncode == 0 and bool(result.stdout.strip())
    except Exception:
      has_content = False

    state = "non-empty" if has_content else "empty"

    if state != self.prev_state:
      self.prev_state = state
      GLib.idle_add(self.update_ui, state)

  def update_ui(self, state):
    if state == "empty":
      self.label.set_text("Clipboard is empty")
      self.clear_button.set_sensitive(False)
    else:
      self.label.set_text("Clipboard has content")
      self.clear_button.set_sensitive(True)

  def on_clear_clicked(self, widget):
    try:
      result = subprocess.run(['xclip', '-selection', 'clipboard'], input='', encoding='utf-8')
      if result.returncode == 0:
        self.prev_state = "empty"
        self.update_ui("empty")
    except Exception as e:
      err = Gtk.MessageDialog(
        self, Gtk.DialogFlags.DESTROY_WITH_PARENT,
        Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
        f"Error clearing clipboard: {e}"
      )
      err.run()
      err.destroy()

  def check_clipboard_loop(self):
    while True:
      time.sleep(1)
      self.check_clipboard()

def main():
  try:
    subprocess.run(['xclip', '-selection', 'clipboard', '-o'],
                 capture_output=True, timeout=2)
  except FileNotFoundError:
    show_error("xclip not found. Please install it with: sudo apt install xclip")

  win = ClipboardMonitor()
  win.show_all()
  Gtk.main()

if __name__ == "__main__":
  main()
