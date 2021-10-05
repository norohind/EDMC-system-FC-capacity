# -*- coding: utf-8 -*-
import os
import logging

from config import appname
import tkinter as tk

from typing import Optional, Tuple, Dict, Any

mainUI_widget: Optional[tk.Label]

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f'{appname}.{plugin_name}')


def plugin_app(parent: tk.Frame) -> Tuple[tk.Label, tk.Label]:
    global mainUI_widget
    label = tk.Label(parent, text="System FC capacity:")
    mainUI_widget = tk.Label(parent, text="Waiting for data\n(scan, FC signals)")
    return label, mainUI_widget


def plugin_start3(plugin_dir) -> str:
    global fcs_counter
    fcs_counter = FCS_counter()
    return 'System FC capacity'


class FCS_counter:
    def __init__(self):
        self.count: int = 0

    def add_signal(self, signal_entry) -> None:
        if signal_entry.get('SignalName')[-4] == '-' and signal_entry.get('IsStation', False):  # It's FC, probably
            self.count += 1
            return

        # logger.debug(f"Don't considering {signal_entry.get('SignalName')} as FC")

    def len(self) -> int:
        return self.count

    def reset(self) -> None:
        self.count = 0


fcs_counter: FCS_counter
body_count: int = 0


def update_display_widget() -> None:
    if body_count == 0 and fcs_counter.len() == 0:
        mainUI_widget["text"] = "Waiting for data\n(scan, FC signals)"
        return

    elif body_count == 0:
        mainUI_widget["text"] = "Waiting for data\n(scan)"
        return

    elif fcs_counter.len() == 0:
        mainUI_widget["text"] = "Waiting for data\n(FC signals)"
        return

    else:
        mainUI_widget["text"] = f"{fcs_counter.len()}/{body_count * 16}"  # 16 FCs per body


def journal_entry(
    cmdr: str, is_beta: bool, system: str, station: str, entry: Dict[str, Any], state: Dict[str, Any]
) -> None:
    event = entry["event"]

    if event == 'StartJump':  # It triggers by both entering to cruise and jumping in a system
        global body_count  # TODO: reset body_count and fcs_counter only on leaving system
        body_count = 0
        fcs_counter.reset()
        update_display_widget()
        return

    if event == 'FSSSignalDiscovered':
        fcs_counter.add_signal(entry)
        update_display_widget()
        return

    if event == 'FSSDiscoveryScan':
        body_count = entry['BodyCount']
        update_display_widget()
        return
