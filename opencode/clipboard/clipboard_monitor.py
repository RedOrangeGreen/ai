#!/usr/bin/env python3
# Author: opencode (opencode.ai), Date: 2026-04-19, Version: big-pickle
# Usage: python3 ./clipboard_monitor.py (requires: apt install xclip python3-gi)

import subprocess
import threading
import time
import sys
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

def check_command(cmd):
  try:
    subprocess.run(cmd, capture_output=True, timeout=2)
    return True
  except FileNotFoundError:
    return False

def show_error(msg):
  try:
    err = Gtk.MessageDialog(
      None, 0,
      Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
      msg
    )
    for child in err.get_message_area().get_children():
      if isinstance(child, Gtk.Label):
        child.set_selectable(True)
    err.run()
  except NameError:
    print(f"Error: {msg}", file=sys.stderr)
  sys.exit(1)

try:
  import gi
  gi.require_version('Gtk', '3.0')
  from gi.repository import Gtk, GLib
except ImportError:
  show_error("python3-gi is required but could not be imported.")

if not check_command(['xclip', '-selection', 'clipboard', '-o']):
  show_error("xclip not found. Please install it with: sudo apt install xclip")

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
      self.label.set_markup("Clipboard is <b>empty</b>")
      self.clear_button.get_style_context().remove_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
      self.clear_button.set_sensitive(False)
    else:
      self.label.set_markup("<b><big>Clipboard has content</big></b>")
      self.clear_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
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
  win = ClipboardMonitor()
  win.show_all()
  Gtk.main()

if __name__ == "__main__":
  main()
