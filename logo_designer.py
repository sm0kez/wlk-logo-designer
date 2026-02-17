#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sm0kez Logo Designer v0.8.0
Ontwikkeld door: sm0kez
Licentie: MIT License

Copyright (c) 2024 sm0kez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
... (SEE MIT LICENSE) ...
"""

from __future__ import annotations

import html as html_mod
import math
import os
import json
import random
import re
import sys
import tempfile
import traceback
import webbrowser
import urllib.request  # Toegevoegd voor updater
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from tkinter import (
    BOTH, BOTTOM, DISABLED, END, FLAT, HORIZONTAL, LEFT, NONE, NORMAL,
    RIGHT, RIDGE, SUNKEN, TOP, VERTICAL, W, E, X, Y, NW, SE,
    BooleanVar, Canvas, Event, Frame, Label, Menu, Scrollbar,
    StringVar, IntVar, Tk, Toplevel, Text,
    filedialog, messagebox, colorchooser,
)
from tkinter import ttk
from typing import Callable

# --- UPDATER CONFIGURATIE ---
UPDATE_URL = "https://raw.githubusercontent.com/sm0kez/wlk-logo-designer/main/logo_designer.py"
APP_VERSION = "0.8.2"
# ----------------------------

GOOGLE_FONT_NAME = "Black Ops One"
GOOGLE_FONT_IMPORT = '@import url("https://fonts.googleapis.com/css2?family=Black+Ops+One&amp;display=swap");'
FONT_STACK = '"Black Ops One", Impact, "Arial Black", Arial, sans-serif'
CONFIG_FILE = "wlk_config.json"


@dataclass
class BrandConfig:
    left: str = "LEFT"
    right: str = "RIGHT"
    tld: str = ".COM"
    tagline: str = "YOUR TAGLINE APPEARS HERE"
    color_dark: str = "#1b1b1b"
    color_red: str = "#e30613"
    color_gold: str = "#ffce00"
    color_white: str = "#ffffff"
    color_grey: str = "#666666"
    bg_dark: str = "#111111"
    font_stack: str = FONT_STACK
    tld_scale: float = 0.44
    word_gap: int = 0
    tld_gap: int = 0
    letter_spacing: float = 0
    icon_offset_x: int = 0
    icon_offset_y: int = 0
    icon_scale: float = 1.0
    out_width: int = 1200
    out_height: int = 140
    fs_main: int = 96


def _esc(s):
    return html_mod.escape(s, quote=False)


def _wrap(cfg, w, h, body, extra_defs=""):
    ls = cfg.letter_spacing
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<svg xmlns="http://www.w3.org/2000/svg"')
    lines.append('  viewBox="0 0 ' + str(w) + ' ' + str(h) + '"')
    lines.append('  width="' + str(w) + '" height="' + str(h) + '">')
    lines.append('  <defs>')
    lines.append('    <style>')
    lines.append('      ' + GOOGLE_FONT_IMPORT)
    lines.append('      .w {')
    lines.append('        font-family: ' + cfg.font_stack + ';')
    lines.append('        font-weight: 400;')
    if ls != 0:
        lines.append('        letter-spacing: ' + str(ls) + 'px;')
    lines.append('      }')
    lines.append('      .tag {')
    lines.append('        font-family: Arial, Helvetica, sans-serif;')
    lines.append('        font-weight: 600;')
    lines.append('      }')
    lines.append('    </style>')
    if extra_defs:
        lines.append(extra_defs)
    lines.append('  </defs>')
    lines.append(body)
    lines.append('</svg>')
    return '\n'.join(lines)


def _main_text(cfg, x, baseline_y, extra_attrs=""):
    fs = cfg.fs_main
    ft = int(fs * cfg.tld_scale)
    wg = cfg.word_gap
    tg = cfg.tld_gap
    parts = []
    parts.append('  <text x="' + str(x) + '" y="' + str(baseline_y) + '"')
    parts.append('    class="w" font-size="' + str(fs) + '"' + extra_attrs + '>')
    parts.append('    <tspan fill="' + cfg.color_dark + '">' + _esc(cfg.left) + '</tspan>')
    dx_right = ' dx="' + str(wg) + '"' if wg != 0 else ''
    parts.append('    <tspan fill="' + cfg.color_red + '"' + dx_right + '>' + _esc(cfg.right) + '</tspan>')
    dx_tld = ' dx="' + str(tg) + '"' if tg != 0 else ''
    parts.append('    <tspan fill="' + cfg.color_dark + '" font-size="' + str(ft) + '"' + dx_tld + '>' + _esc(cfg.tld) + '</tspan>')
    parts.append('  </text>')
    return '\n'.join(parts)


def _main_text_colors(cfg, x, baseline_y, left_color, right_color, tld_color, extra_attrs=""):
    fs = cfg.fs_main
    ft = int(fs * cfg.tld_scale)
    wg = cfg.word_gap
    tg = cfg.tld_gap
    parts = []
    parts.append('  <text x="' + str(x) + '" y="' + str(baseline_y) + '"')
    parts.append('    class="w" font-size="' + str(fs) + '"' + extra_attrs + '>')
    parts.append('    <tspan fill="' + left_color + '">' + _esc(cfg.left) + '</tspan>')
    dx_right = ' dx="' + str(wg) + '"' if wg != 0 else ''
    parts.append('    <tspan fill="' + right_color + '"' + dx_right + '>' + _esc(cfg.right) + '</tspan>')
    dx_tld = ' dx="' + str(tg) + '"' if tg != 0 else ''
    parts.append('    <tspan fill="' + tld_color + '" font-size="' + str(ft) + '"' + dx_tld + '>' + _esc(cfg.tld) + '</tspan>')
    parts.append('  </text>')
    return '\n'.join(parts)


def _baseline(cfg):
    return int(cfg.out_height * 0.5 + cfg.fs_main * 0.35)


# ─── SVG ICON HELPERS ───────────────────────────────────

def _crown_svg(fill, size=108):
    s = size / 108.0
    parts = []
    parts.append('<g fill="' + fill + '">')
    parts.append('  <polygon points="' +
        str(int(0*s)) + ',' + str(int(70*s)) + ' ' +
        str(int(18*s)) + ',' + str(int(30*s)) + ' ' +
        str(int(36*s)) + ',' + str(int(70*s)) + ' ' +
        str(int(54*s)) + ',' + str(int(20*s)) + ' ' +
        str(int(72*s)) + ',' + str(int(70*s)) + ' ' +
        str(int(90*s)) + ',' + str(int(30*s)) + ' ' +
        str(int(108*s)) + ',' + str(int(70*s)) + ' ' +
        str(int(108*s)) + ',' + str(int(92*s)) + ' ' +
        str(int(0*s)) + ',' + str(int(92*s)) + '"/>')
    parts.append('  <circle cx="' + str(int(18*s)) + '" cy="' + str(int(30*s)) + '" r="' + str(int(6*s)) + '"/>')
    parts.append('  <circle cx="' + str(int(54*s)) + '" cy="' + str(int(20*s)) + '" r="' + str(int(6*s)) + '"/>')
    parts.append('  <circle cx="' + str(int(90*s)) + '" cy="' + str(int(30*s)) + '" r="' + str(int(6*s)) + '"/>')
    parts.append('</g>')
    return '\n'.join(parts)


def _bearing_svg(stroke, accent):
    parts = []
    parts.append('<g>')
    parts.append('  <circle r="52" fill="none" stroke="' + stroke + '" stroke-width="10"/>')
    parts.append('  <circle r="24" fill="none" stroke="' + stroke + '" stroke-width="10"/>')
    parts.append('  <g fill="' + accent + '">')
    for cx, cy in [(36,0),(25.5,25.5),(0,36),(-25.5,25.5),(-36,0),(-25.5,-25.5),(0,-36),(25.5,-25.5)]:
        parts.append('    <circle cx="' + str(cx) + '" cy="' + str(cy) + '" r="6"/>')
    parts.append('  </g>')
    parts.append('</g>')
    return '\n'.join(parts)


def _star_svg(cx, cy, r_out, r_in, points_n, fill, opacity="1"):
    pts = []
    for i in range(points_n * 2):
        angle = math.pi * i / points_n - math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        pts.append(str(round(px, 1)) + "," + str(round(py, 1)))
    return '<polygon points="' + ' '.join(pts) + '" fill="' + fill + '" opacity="' + opacity + '"/>'


def _snowflake_svg(cx, cy, size, fill="#ffffff", opacity="0.8"):
    s = size
    parts = []
    parts.append('<g transform="translate(' + str(cx) + ' ' + str(cy) + ')" fill="' + fill + '" opacity="' + opacity + '">')
    for angle in [0, 60, 120]:
        parts.append('  <rect x="' + str(-s//16) + '" y="' + str(-s//2) + '" width="' + str(max(1,s//8)) + '" height="' + str(s) + '"')
        parts.append('    rx="1" transform="rotate(' + str(angle) + ')"/>')
    parts.append('  <circle r="' + str(max(1,s//6)) + '"/>')
    parts.append('</g>')
    return '\n'.join(parts)


def _heart_svg(cx, cy, size, fill="#e30613", opacity="1"):
    s = size / 30.0
    return ('<path d="M' + str(cx) + ' ' + str(cy + int(8*s)) +
            ' C' + str(cx) + ' ' + str(cy + int(3*s)) +
            ' ' + str(cx - int(15*s)) + ' ' + str(cy - int(8*s)) +
            ' ' + str(cx) + ' ' + str(cy - int(15*s)) +
            ' C' + str(cx + int(15*s)) + ' ' + str(cy - int(8*s)) +
            ' ' + str(cx) + ' ' + str(cy + int(3*s)) +
            ' ' + str(cx) + ' ' + str(cy + int(8*s)) +
            'Z" fill="' + fill + '" opacity="' + opacity + '"/>')


def _firework_svg(cx, cy, r, fill, n=12):
    parts = []
    parts.append('<g stroke="' + fill + '" stroke-width="2" opacity="0.9">')
    for i in range(n):
        angle = 2 * math.pi * i / n
        x1 = cx + int(r * 0.3 * math.cos(angle))
        y1 = cy + int(r * 0.3 * math.sin(angle))
        x2 = cx + int(r * math.cos(angle))
        y2 = cy + int(r * math.sin(angle))
        parts.append('  <line x1="' + str(x1) + '" y1="' + str(y1) + '" x2="' + str(x2) + '" y2="' + str(y2) + '"/>')
    parts.append('</g>')
    parts.append('<circle cx="' + str(cx) + '" cy="' + str(cy) + '" r="3" fill="' + fill + '"/>')
    return '\n'.join(parts)


def _mijter_svg(size=60):
    s = size
    w = int(s * 0.8)
    h = s
    parts = []
    parts.append('<g>')
    parts.append('  <path d="M0,' + str(h) + ' L' + str(w//2) + ',0 L' + str(w) + ',' + str(h) + ' Z" fill="#e30613"/>')
    bh = max(4, int(h * 0.18))
    parts.append('  <rect x="0" y="' + str(h - bh) + '" width="' + str(w) + '" height="' + str(bh) + '" fill="#ffce00"/>')
    cx = w // 2
    parts.append('  <line x1="' + str(cx) + '" y1="' + str(int(h*0.15)) + '" x2="' + str(cx) + '" y2="' + str(h - bh) + '" stroke="#ffce00" stroke-width="3"/>')
    parts.append('  <line x1="' + str(int(cx - w*0.2)) + '" y1="' + str(int(h*0.45)) + '" x2="' + str(int(cx + w*0.2)) + '" y2="' + str(int(h*0.45)) + '" stroke="#ffce00" stroke-width="3"/>')
    parts.append('</g>')
    return '\n'.join(parts)


def _pumpkin_svg(size=50):
    r = size // 2
    parts = []
    parts.append('<g>')
    parts.append('  <ellipse cx="0" cy="0" rx="' + str(r) + '" ry="' + str(int(r*0.8)) + '" fill="#FF6600"/>')
    parts.append('  <ellipse cx="0" cy="0" rx="' + str(int(r*0.6)) + '" ry="' + str(int(r*0.8)) + '" fill="none" stroke="#E55500" stroke-width="2"/>')
    parts.append('  <rect x="-3" y="' + str(int(-r*0.8 - 10)) + '" width="6" height="12" rx="2" fill="#2d8a4e"/>')
    ey = int(-r * 0.2)
    parts.append('  <polygon points="' + str(-r//3) + ',' + str(ey) + ' ' + str(-r//3 + 5) + ',' + str(ey - 10) + ' ' + str(-r//3 + 10) + ',' + str(ey) + '" fill="#1a0a2e"/>')
    parts.append('  <polygon points="' + str(r//3 - 10) + ',' + str(ey) + ' ' + str(r//3 - 5) + ',' + str(ey - 10) + ' ' + str(r//3) + ',' + str(ey) + '" fill="#1a0a2e"/>')
    my = int(r * 0.2)
    parts.append('  <path d="M' + str(-r//3) + ' ' + str(my) + ' Q0 ' + str(my + 12) + ' ' + str(r//3) + ' ' + str(my) + '" fill="#1a0a2e"/>')
    parts.append('</g>')
    return '\n'.join(parts)


def _christmas_tree_svg(size=80):
    s = size
    parts = []
    parts.append('<g>')
    for i, (yw, yh, xw) in enumerate([(0.0, 0.35, 0.3), (0.2, 0.55, 0.45), (0.4, 0.75, 0.6)]):
        y_top = int(-s * (1.0 - yw))
        y_bot = int(-s * (1.0 - yh))
        half_w = int(s * xw * 0.5)
        parts.append('  <polygon points="0,' + str(y_top) + ' ' + str(-half_w) + ',' + str(y_bot) + ' ' + str(half_w) + ',' + str(y_bot) + '" fill="#2d8a4e"/>')
    tw = max(4, int(s * 0.12))
    th = max(6, int(s * 0.15))
    parts.append('  <rect x="' + str(-tw//2) + '" y="' + str(int(-s*0.25)) + '" width="' + str(tw) + '" height="' + str(th) + '" fill="#8B4513"/>')
    parts.append('  ' + _star_svg(0, int(-s), max(4, int(s*0.12)), max(2, int(s*0.05)), 5, "#ffce00"))
    for bx, by in [(-8, int(-s*0.5)), (10, int(-s*0.35)), (-5, int(-s*0.65))]:
        parts.append('  <circle cx="' + str(bx) + '" cy="' + str(by) + '" r="3" fill="#e30613"/>')
    parts.append('</g>')
    return '\n'.join(parts)


def _egg_svg(w_r, h_r, fill, stripe_color="#ffffff"):
    parts = []
    parts.append('<g>')
    parts.append('  <ellipse cx="0" cy="0" rx="' + str(w_r) + '" ry="' + str(h_r) + '" fill="' + fill + '"/>')
    parts.append('  <line x1="' + str(-w_r+2) + '" y1="0" x2="' + str(w_r-2) + '" y2="0" stroke="' + stripe_color + '" stroke-width="2"/>')
    parts.append('  <line x1="' + str(-w_r+4) + '" y1="' + str(-h_r//3) + '" x2="' + str(w_r-4) + '" y2="' + str(-h_r//3) + '" stroke="' + stripe_color + '" stroke-width="1.5" opacity="0.6"/>')
    parts.append('</g>')
    return '\n'.join(parts)


# ─── VARIANTS 01-19 ─────────────────────────────────────

def v01_basic(c):
    m = 24
    by = _baseline(c)
    body = _main_text(c, m, by)
    return ("01 - Basis", _wrap(c, c.out_width, c.out_height, body))


def v02_flag(c):
    m = 24
    h = c.out_height + 30
    by = _baseline(c)
    uw = c.out_width - 2 * m
    y0 = by + 20
    parts = []
    parts.append(_main_text(c, m, by))
    parts.append('  <rect x="' + str(m) + '" y="' + str(y0) + '" width="' + str(uw) + '" height="5" fill="#000"/>')
    parts.append('  <rect x="' + str(m) + '" y="' + str(y0+6) + '" width="' + str(uw) + '" height="5" fill="#dd0000"/>')
    parts.append('  <rect x="' + str(m) + '" y="' + str(y0+12) + '" width="' + str(uw) + '" height="5" fill="' + c.color_gold + '"/>')
    body = '\n'.join(parts)
    return ("02 - Duitse vlag-underline", _wrap(c, c.out_width, h, body))


def v04_crown(c):
    m = 24
    icon_h = int(70 * c.icon_scale)
    gap = 10
    extra_top = icon_h + gap
    h = c.out_height + extra_top
    by = extra_top + _baseline(c)
    crown_w = int(108 * c.icon_scale)
    cx = c.out_width // 2 - crown_w // 2 + c.icon_offset_x
    cy = 5 + c.icon_offset_y
    parts = []
    parts.append('  <g transform="translate(' + str(cx) + ' ' + str(cy) + ') scale(' + str(c.icon_scale) + ')">')
    parts.append('    ' + _crown_svg(c.color_red))
    parts.append('  </g>')
    parts.append(_main_text(c, m, by))
    body = '\n'.join(parts)
    return ("03 - Met kroon", _wrap(c, c.out_width, h, body))


def v05_bearing(c):
    m = 24
    icon_r = int(55 * c.icon_scale)
    icon_cx = m + icon_r + 10 + c.icon_offset_x
    icon_cy = c.out_height // 2 + c.icon_offset_y
    shift = icon_r * 2 + 30
    by = _baseline(c)
    w = c.out_width + shift
    parts = []
    parts.append('  <g transform="translate(' + str(icon_cx) + ' ' + str(icon_cy) + ') scale(' + str(c.icon_scale) + ')">')
    parts.append('    ' + _bearing_svg(c.color_dark, c.color_red))
    parts.append('  </g>')
    parts.append(_main_text(c, m + shift, by))
    body = '\n'.join(parts)
    return ("04 - Met lager-icoon", _wrap(c, w, c.out_height, body))


def v08_mono(c):
    m = 24
    by = _baseline(c)
    bw = int(c.out_height * 0.85)
    bh = bw
    mono = (c.left[:1] + c.right[:1]).upper()
    shift = bw + 20
    box_y = (c.out_height - bh) // 2
    w = c.out_width + shift
    parts = []
    parts.append('  <g transform="translate(' + str(m) + ' ' + str(box_y) + ')">')
    parts.append('    <rect width="' + str(bw) + '" height="' + str(bh) + '" rx="12" fill="' + c.color_red + '"/>')
    parts.append('    <text x="' + str(bw//2) + '" y="' + str(int(bh*0.72)) + '"')
    parts.append('      text-anchor="middle" class="w" font-size="' + str(int(bh*0.55)) + '"')
    parts.append('      fill="' + c.color_white + '">' + _esc(mono) + '</text>')
    parts.append('  </g>')
    parts.append(_main_text(c, m + shift, by))
    body = '\n'.join(parts)
    return ("05 - Monogram", _wrap(c, w, c.out_height, body))


def v09_invert(c):
    m = 24
    by = _baseline(c)
    parts = []
    parts.append('  <rect width="' + str(c.out_width) + '" height="' + str(c.out_height) + '" fill="' + c.bg_dark + '"/>')
    parts.append(_main_text_colors(c, m, by, c.color_white, c.color_red, c.color_white))
    body = '\n'.join(parts)
    return ("06 - Inverted (donker)", _wrap(c, c.out_width, c.out_height, body))


def v10_diagonal(c):
    m = 24
    by = _baseline(c)
    sk = 35
    ps = int(c.out_width * 0.50)
    pe = c.out_width
    h = c.out_height
    points = str(ps) + ",0 " + str(pe) + ",0 " + str(pe) + "," + str(h) + " " + str(ps-sk) + "," + str(h)
    parts = []
    parts.append('  <polygon points="' + points + '" fill="' + c.color_red + '"/>')
    parts.append(_main_text_colors(c, m, by, c.color_dark, c.color_white, c.color_white))
    body = '\n'.join(parts)
    return ("07 - Diagonaal paneel", _wrap(c, c.out_width, c.out_height, body))


def v11_christmas(c):
    m = 24
    icon_zone = int(90 * c.icon_scale)
    h = c.out_height + icon_zone
    by = icon_zone + int(c.out_height * 0.5 + c.fs_main * 0.35)
    w = c.out_width
    parts = []
    parts.append('  <rect width="' + str(w) + '" height="' + str(h) + '" fill="#1a3a1a"/>')
    for sx, sy, ss in [(80,20,18),(250,40,12),(450,15,20),(650,35,14),(850,10,16),(1050,25,10)]:
        if sx < w:
            parts.append('  ' + _snowflake_svg(sx, sy, ss, "#ffffff", "0.4"))
    tree_x = w // 2 + c.icon_offset_x
    tree_y = icon_zone - 5 + c.icon_offset_y
    parts.append('  <g transform="translate(' + str(tree_x) + ' ' + str(tree_y) + ') scale(' + str(c.icon_scale) + ')">')
    parts.append('    ' + _christmas_tree_svg(70))
    parts.append('  </g>')
    parts.append('  ' + _star_svg(w - 80, 25, 14, 6, 5, "#ffce00", "0.9"))
    parts.append('  ' + _star_svg(w - 40, 50, 8, 3, 5, "#ffce00", "0.6"))
    parts.append('  ' + _star_svg(100, 35, 10, 4, 5, "#ffce00", "0.7"))
    parts.append(_main_text_colors(c, m, by, "#ffffff", "#e30613", "#ffce00"))
    parts.append('  <rect x="' + str(m) + '" y="' + str(h - 6) + '" width="' + str(w - 2*m) + '" height="4" fill="#ffce00" rx="2"/>')
    body = '\n'.join(parts)
    return ("08 - \U0001f384 Kerst / Weihnachten", _wrap(c, w, h, body))


def v12_sinterklaas(c):
    m = 24
    icon_zone = int(80 * c.icon_scale)
    h = c.out_height + icon_zone + 20
    by = icon_zone + int(c.out_height * 0.5 + c.fs_main * 0.35)
    w = c.out_width
    parts = []
    parts.append('  <rect width="' + str(w) + '" height="' + str(h) + '" fill="#8B0000"/>')
    mijter_x = w // 2 - int(24 * c.icon_scale) + c.icon_offset_x
    mijter_y = 8 + c.icon_offset_y
    parts.append('  <g transform="translate(' + str(mijter_x) + ' ' + str(mijter_y) + ') scale(' + str(c.icon_scale) + ')">')
    parts.append('    ' + _mijter_svg(60))
    parts.append('  </g>')
    rng = random.Random(55)
    for _ in range(8):
        px = rng.randint(m, w - m)
        py = rng.randint(5, icon_zone - 5)
        parts.append('  <circle cx="' + str(px) + '" cy="' + str(py) + '" r="6" fill="#D2691E" opacity="0.6"/>')
    parts.append(_main_text_colors(c, m, by, "#ffffff", "#ffce00", "#ffffff"))
    parts.append('  <rect x="0" y="' + str(h-6) + '" width="' + str(w) + '" height="6" fill="#ffce00"/>')
    body = '\n'.join(parts)
    return ("09 - \U0001f385 Sinterklaas (NL)", _wrap(c, w, h, body))


def v13_koningsdag(c):
    m = 24
    icon_zone = int(75 * c.icon_scale)
    h = c.out_height + icon_zone
    by = icon_zone + int(c.out_height * 0.5 + c.fs_main * 0.35)
    w = c.out_width
    parts = []
    parts.append('  <rect width="' + str(w) + '" height="' + str(h) + '" fill="#FF6600"/>')
    crown_w = int(108 * c.icon_scale)
    cx = w // 2 - crown_w // 2 + c.icon_offset_x
    cy = 5 + c.icon_offset_y
    parts.append('  <g transform="translate(' + str(cx) + ' ' + str(cy) + ') scale(' + str(c.icon_scale * 0.7) + ')">')
    parts.append('    ' + _crown_svg("#ffffff"))
    parts.append('  </g>')
    parts.append(_main_text_colors(c, m, by, "#ffffff", c.color_dark, "#ffffff"))
    parts.append('  <rect x="0" y="' + str(h-9) + '" width="' + str(w) + '" height="3" fill="#AE1C28"/>')
    parts.append('  <rect x="0" y="' + str(h-6) + '" width="' + str(w) + '" height="3" fill="#FFFFFF"/>')
    parts.append('  <rect x="0" y="' + str(h-3) + '" width="' + str(w) + '" height="3" fill="#21468B"/>')
    body = '\n'.join(parts)
    return ("10 - \U0001f451 Koningsdag (NL)", _wrap(c, w, h, body))


def v14_easter(c):
    m = 24
    icon_zone = int(60 * c.icon_scale)
    h = c.out_height + icon_zone
    by = icon_zone + int(c.out_height * 0.5 + c.fs_main * 0.35)
    w = c.out_width
    parts = []
    parts.append('  <rect width="' + str(w) + '" height="' + str(h) + '" fill="#f0f8e8"/>')
    egg_colors = ["#e30613", "#ffce00", "#4CAF50", "#2196F3", "#FF9800", "#9C27B0"]
    egg_spacing = w // 8
    for i in range(6):
        ex = egg_spacing + i * egg_spacing + c.icon_offset_x
        ey = icon_zone // 2 + ((-1)**i * 8) + c.icon_offset_y
        col = egg_colors[i]
        sc = c.icon_scale * 0.8
        parts.append('  <g transform="translate(' + str(ex) + ' ' + str(ey) + ') scale(' + str(sc) + ')">')
        parts.append('    ' + _egg_svg(12, 16, col))
        parts.append('  </g>')
    for fx, fy in [(100, icon_zone - 10), (400, icon_zone - 8), (700, icon_zone - 12), (1000, icon_zone - 9)]:
        if fx < w:
            parts.append('  <circle cx="' + str(fx) + '" cy="' + str(fy) + '" r="5" fill="#FFD700"/>')
            parts.append('  <circle cx="' + str(fx) + '" cy="' + str(fy) + '" r="2.5" fill="#FF6347"/>')
    parts.append('  <rect x="0" y="' + str(icon_zone - 4) + '" width="' + str(w) + '" height="4" fill="#4CAF50" opacity="0.5" rx="2"/>')
    parts.append(_main_text(c, m, by))
    body = '\n'.join(parts)
    return ("11 - \U0001f423 Pasen / Ostern", _wrap(c, w, h, body))


def v15_valentine(c):
    m = 24
    h = c.out_height + 10
    by = _baseline(c) + 5
    w = c.out_width
    parts = []
    parts.append('  <rect width="' + str(w) + '" height="' + str(h) + '" fill="#fff0f3"/>')
    rng = random.Random(14)
    for _ in range(15):
        hx = rng.randint(10, w - 10)
        hy = rng.randint(5, h - 5)
        hs = rng.randint(10, 22)
        op = str(round(rng.uniform(0.15, 0.4), 2))
        parts.append('  ' + _heart_svg(hx, hy, hs, "#e30613", op))
    parts.append(_main_text_colors(c, m, by, c.color_dark, "#e30613", c.color_dark))
    body = '\n'.join(parts)
    return ("12 - \u2764\ufe0f Valentijnsdag", _wrap(c, w, h, body))


def v16_newyear(c):
    m = 24
    icon_zone = int(60 * c.icon_scale)
    h = c.out_height + icon_zone
    by = icon_zone + int(c.out_height * 0.5 + c.fs_main * 0.35)
    w = c.out_width
    parts = []
    parts.append('  <rect width="' + str(w) + '" height="' + str(h) + '" fill="#0a0a2e"/>')
    fw_data = [(120, 25, 30, "#ffce00"), (350, 35, 35, "#e30613"),
               (600, 20, 28, "#4fc3f7"), (850, 30, 32, "#ff9800"),
               (1050, 25, 25, "#ab47bc")]
    for fx, fy, fr, fc in fw_data:
        if fx < w:
            parts.append('  ' + _firework_svg(fx + c.icon_offset_x, fy + c.icon_offset_y, int(fr * c.icon_scale), fc))
    for sx, sy in [(50,15),(250,8),(450,18),(700,5),(900,12),(1100,20)]:
        if sx < w:
            parts.append('  ' + _star_svg(sx, sy, 3, 1.5, 4, "#ffffff", "0.6"))
    parts.append(_main_text_colors(c, m, by, "#ffffff", "#ffce00", "#ffffff"))
    parts.append('  <rect x="' + str(m) + '" y="' + str(h-4) + '" width="' + str(w-2*m) + '" height="3" fill="#ffce00" rx="1"/>')
    body = '\n'.join(parts)
    return ("13 - \U0001f386 Oud & Nieuw / Silvester", _wrap(c, w, h, body))


def v17_einheit(c):
    m = 24
    flag_h = 24
    flag_total = flag_h * 3
    gap = 10
    h = c.out_height + flag_total + gap + 40
    by = flag_total + gap + int(c.out_height * 0.5 + c.fs_main * 0.35)
    w = c.out_width
    parts = []
    parts.append('  <rect x="0" y="0" width="' + str(w) + '" height="' + str(flag_h) + '" fill="#000000"/>')
    parts.append('  <rect x="0" y="' + str(flag_h) + '" width="' + str(w) + '" height="' + str(flag_h) + '" fill="#DD0000"/>')
    parts.append('  <rect x="0" y="' + str(flag_h*2) + '" width="' + str(w) + '" height="' + str(flag_h) + '" fill="#FFCE00"/>')
    parts.append(_main_text(c, m, by))
    tag_y = by + 35
    parts.append('  <text x="' + str(m) + '" y="' + str(tag_y) + '"')
    parts.append('    class="tag" font-size="22" fill="' + c.color_grey + '">')
    parts.append('    Tag der Deutschen Einheit - 3. Oktober</text>')
    body = '\n'.join(parts)
    return ("14 - \U0001f1e9\U0001f1ea Tag der Deutschen Einheit", _wrap(c, w, h, body))


def v18_oktoberfest(c):
    m = 24
    h = c.out_height + 20
    by = _baseline(c) + 10
    w = c.out_width
    parts = []
    parts.append('  <rect width="' + str(w) + '" height="' + str(h) + '" fill="#0066B3"/>')
    ds = 16
    for dx in range(0, w + ds, ds * 2):
        for row in range(3):
            offset = ds if row % 2 == 1 else 0
            px = dx + offset
            py = row * ds
            if px < w + ds:
                parts.append('  <polygon points="' +
                    str(px) + ',' + str(py) + ' ' +
                    str(px + ds) + ',' + str(py + ds) + ' ' +
                    str(px) + ',' + str(py + ds * 2) + ' ' +
                    str(px - ds) + ',' + str(py + ds) +
                    '" fill="#ffffff" opacity="0.2"/>')
    parts.append(_main_text_colors(c, m, by, "#ffffff", "#ffce00", "#ffffff"))
    body = '\n'.join(parts)
    return ("15 - \U0001f37a Oktoberfest (DE)", _wrap(c, w, h, body))


def v19_bevrijding(c):
    m = 24
    flag_h = 20
    flag_total = flag_h * 3
    gap = 10
    h = c.out_height + flag_total + gap + 40
    by = flag_total + gap + int(c.out_height * 0.5 + c.fs_main * 0.35)
    w = c.out_width
    parts = []
    parts.append('  <rect x="0" y="0" width="' + str(w) + '" height="' + str(flag_h) + '" fill="#AE1C28"/>')
    parts.append('  <rect x="0" y="' + str(flag_h) + '" width="' + str(w) + '" height="' + str(flag_h) + '" fill="#FFFFFF"/>')
    parts.append('  <rect x="0" y="' + str(flag_h*2) + '" width="' + str(w) + '" height="' + str(flag_h) + '" fill="#21468B"/>')
    parts.append(_main_text(c, m, by))
    tag_y = by + 35
    parts.append('  <text x="' + str(m) + '" y="' + str(tag_y) + '"')
    parts.append('    class="tag" font-size="22" fill="#21468B">')
    parts.append('    Bevrijdingsdag - 5 mei</text>')
    body = '\n'.join(parts)
    return ("16 - \U0001f54a\ufe0f Bevrijdingsdag (NL) 5 mei", _wrap(c, w, h, body))


def v20_carnival(c):
    m = 24
    h = c.out_height + 10
    by = _baseline(c) + 5
    w = c.out_width
    parts = []
    parts.append('  <rect width="' + str(w) + '" height="' + str(h) + '" fill="#ffffff"/>')
    stripe_colors = ["#e30613", "#ffce00", "#2d8a4e", "#2196F3", "#FF9800", "#9C27B0"]
    sw = w // len(stripe_colors) + 1
    for i, col in enumerate(stripe_colors):
        parts.append('  <rect x="' + str(i * sw) + '" y="0" width="' + str(sw) + '" height="' + str(h) + '" fill="' + col + '" opacity="0.12"/>')
    rng = random.Random(42)
    for _ in range(25):
        cx_c = rng.randint(10, w - 10)
        cy_c = rng.randint(5, h - 5)
        cr = rng.randint(3, 7)
        col = rng.choice(stripe_colors)
        parts.append('  <circle cx="' + str(cx_c) + '" cy="' + str(cy_c) + '" r="' + str(cr) + '" fill="' + col + '" opacity="0.35"/>')
    parts.append(_main_text(c, m, by))
    body = '\n'.join(parts)
    return ("17 - \U0001f3ad Karneval / Carnaval", _wrap(c, w, h, body))


def v21_halloween(c):
    m = 24
    icon_zone = int(70 * c.icon_scale)
    h = c.out_height + icon_zone
    by = icon_zone + int(c.out_height * 0.5 + c.fs_main * 0.35)
    w = c.out_width
    parts = []
    parts.append('  <rect width="' + str(w) + '" height="' + str(h) + '" fill="#1a0a2e"/>')
    parts.append('  <circle cx="' + str(w - 60) + '" cy="35" r="25" fill="#ffce00" opacity="0.9"/>')
    parts.append('  <circle cx="' + str(w - 48) + '" cy="30" r="23" fill="#1a0a2e"/>')
    pk_x = w // 2 + c.icon_offset_x
    pk_y = icon_zone // 2 + 5 + c.icon_offset_y
    parts.append('  <g transform="translate(' + str(pk_x) + ' ' + str(pk_y) + ') scale(' + str(c.icon_scale) + ')">')
    parts.append('    ' + _pumpkin_svg(50))
    parts.append('  </g>')
    for spx in [int(w * 0.15), int(w * 0.85)]:
        parts.append('  <g transform="translate(' + str(spx) + ' ' + str(icon_zone // 2) + ') scale(0.5)">')
        parts.append('    ' + _pumpkin_svg(40))
        parts.append('  </g>')
    for sx, sy in [(50,12),(200,8),(400,18),(700,5),(900,15)]:
        if sx < w:
            parts.append('  ' + _star_svg(sx, sy, 3, 1.5, 4, "#ffffff", "0.5"))
    parts.append(_main_text_colors(c, m, by, "#FF6600", "#e30613", "#ffce00"))
    body = '\n'.join(parts)
    return ("18 - \U0001f383 Halloween", _wrap(c, w, h, body))


def v22_blackfriday(c):
    m = 24
    h = c.out_height + 40
    by = _baseline(c) + 5
    w = c.out_width
    parts = []
    parts.append('  <rect width="' + str(w) + '" height="' + str(h) + '" fill="#000000"/>')
    parts.append('  <rect x="0" y="0" width="' + str(w) + '" height="3" fill="#ffce00"/>')
    parts.append('  <rect x="0" y="' + str(h-3) + '" width="' + str(w) + '" height="3" fill="#ffce00"/>')
    parts.append(_main_text_colors(c, m, by, "#ffffff", "#ffce00", "#ffffff"))
    bf_y = by + 35
    parts.append('  <text x="' + str(m) + '" y="' + str(bf_y) + '"')
    parts.append('    class="w" font-size="28" fill="#ffce00">')
    parts.append('    BLACK FRIDAY DEALS</text>')
    body = '\n'.join(parts)
    return ("19 - \U0001f3f7\ufe0f Black Friday", _wrap(c, w, h, body))


ALL_VARIANTS = [
    v01_basic, v02_flag, v04_crown, v05_bearing, 
    v08_mono, v09_invert, v10_diagonal,
    v11_christmas, v12_sinterklaas, v13_koningsdag, v14_easter,
    v15_valentine, v16_newyear, v17_einheit, v18_oktoberfest,
    v19_bevrijding, v20_carnival, v21_halloween, v22_blackfriday,
]


# ─── HTML BUILDERS ──────────────────────────────────────

def _build_all_preview_html(svgs, selected=None):
    cards = []
    for i, (label, svg_code) in enumerate(svgs):
        border = "3px solid #e30613" if i == selected else "1px solid #ddd"
        card = '<div style="background:#fff;border:' + border + ';border-radius:12px;padding:16px;margin-bottom:12px;">\n'
        card += '<div style="font:bold 14px Arial;color:#444;margin-bottom:8px;">' + html_mod.escape(label) + '</div>\n'
        card += svg_code + '\n</div>'
        cards.append(card)
    html_out = '<!doctype html><html><head><meta charset="utf-8">\n'
    html_out += '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    html_out += '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    html_out += '<link href="https://fonts.googleapis.com/css2?family=Black+Ops+One&display=swap" rel="stylesheet">\n'
    html_out += '<style>body{font-family:Arial,sans-serif;margin:16px;background:#f4f4f4}svg{width:100%;height:auto;display:block}</style></head><body>\n'
    html_out += '<h2 style="margin:0 0 16px">Logo Preview v3.7 (' + str(len(svgs)) + ' varianten)</h2>\n'
    html_out += '\n'.join(cards) + '\n</body></html>'
    return html_out


def _build_single_preview_html(label, svg_code):
    html_out = '<!doctype html><html><head><meta charset="utf-8">\n'
    html_out += '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    html_out += '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    html_out += '<link href="https://fonts.googleapis.com/css2?family=Black+Ops+One&display=swap" rel="stylesheet">\n'
    html_out += '<style>body{font-family:Arial,sans-serif;margin:24px;background:#f4f4f4}svg{width:100%;max-width:1400px;height:auto;display:block}.box{background:#fff;border:1px solid #ddd;border-radius:12px;padding:20px}</style></head><body>\n'
    html_out += '<h2>' + html_mod.escape(label) + '</h2>\n'
    html_out += '<div class="box">' + svg_code + '</div>\n</body></html>'
    return html_out


# ─── DEBUG CONSOLE ──────────────────────────────────────

class DebugConsole(Frame):
    TAG_COLORS = {
        "INFO":    {"fg": "#cccccc", "prefix": "[INFO] "},
        "SUCCESS": {"fg": "#4ec94e", "prefix": "[OK] "},
        "WARNING": {"fg": "#f0a030", "prefix": "[WARN] "},
        "ERROR":   {"fg": "#ff4444", "prefix": "[ERROR] "},
        "DEBUG":   {"fg": "#888888", "prefix": "[DEBUG] "},
        "ACTION":  {"fg": "#66bbff", "prefix": "[ACTIE] "},
    }

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._is_visible = True
        self._log_count = 0
        self._build()

    def _build(self):
        self.header = Frame(self, bg="#2a2a2a", height=32)
        self.header.pack(fill=X)
        self.header.pack_propagate(False)
        self.toggle_btn = ttk.Button(self.header, text="Debug Console (verbergen)", command=self.toggle, width=28)
        self.toggle_btn.pack(side=LEFT, padx=4, pady=3)
        self.count_label = Label(self.header, text="(0)", bg="#2a2a2a", fg="#888888", font=("Arial", 9))
        self.count_label.pack(side=LEFT, padx=8)
        ttk.Button(self.header, text="Kopieer", command=self._copy_log, width=8).pack(side=RIGHT, padx=4, pady=3)
        ttk.Button(self.header, text="Wis", command=self._clear_log, width=6).pack(side=RIGHT, padx=4, pady=3)

        self.log_frame = Frame(self)
        self.log_frame.pack(fill=BOTH, expand=True)
        scrollbar_y = Scrollbar(self.log_frame, orient=VERTICAL)
        self.log_text = Text(self.log_frame, wrap=NONE, font=("Consolas", 9), bg="#1a1a1a", fg="#cccccc",
                            insertbackground="#fff", state=DISABLED, height=6, yscrollcommand=scrollbar_y.set)
        scrollbar_y.config(command=self.log_text.yview)
        scrollbar_y.pack(side=RIGHT, fill=Y)
        self.log_text.pack(fill=BOTH, expand=True)
        for tag_name, props in self.TAG_COLORS.items():
            self.log_text.tag_configure(tag_name, foreground=props["fg"])
        self.log_text.tag_configure("TIMESTAMP", foreground="#666666")
        self.log_text.tag_configure("SEPARATOR", foreground="#444444")

    def log(self, message, level="INFO"):
        level = level.upper()
        if level not in self.TAG_COLORS:
            level = "INFO"
        props = self.TAG_COLORS[level]
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, "[" + ts + "] ", "TIMESTAMP")
        self.log_text.insert(END, props["prefix"] + message + "\n", level)
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)
        self._log_count += 1
        self.count_label.config(text="(" + str(self._log_count) + ")")

    def log_separator(self, title=""):
        self.log_text.config(state=NORMAL)
        line = ("--- " + title + " " + "-" * max(0, 50 - len(title))) if title else ("-" * 60)
        self.log_text.insert(END, line + "\n", "SEPARATOR")
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)

    def log_exception(self, context=""):
        tb = traceback.format_exc()
        self.log("EXCEPTION in " + context + ":" if context else "EXCEPTION:", "ERROR")
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, tb + "\n", "ERROR")
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)

    def toggle(self):
        if self._is_visible:
            self.log_frame.pack_forget()
            self.toggle_btn.config(text="Debug Console (tonen)")
        else:
            self.log_frame.pack(fill=BOTH, expand=True)
            self.toggle_btn.config(text="Debug Console (verbergen)")
        self._is_visible = not self._is_visible

    def _copy_log(self):
        self.winfo_toplevel().clipboard_clear()
        self.winfo_toplevel().clipboard_append(self.log_text.get("1.0", END))
        self.log("Log gekopieerd", "SUCCESS")

    def _clear_log(self):
        self.log_text.config(state=NORMAL)
        self.log_text.delete("1.0", END)
        self.log_text.config(state=DISABLED)
        self._log_count = 0
        self.count_label.config(text="(0)")


# ─── UPDATER LOGICA ─────────────────────────────────────

def check_for_updates(debug_console=None, quiet=False):
    """Controleert op updates via de Raw GitHub link."""
    try:
        if debug_console: debug_console.log("Controleren op updates...", "INFO")
        
        # Download de code van internet
        with urllib.request.urlopen(UPDATE_URL, timeout=5) as response:
            content = response.read().decode('utf-8')
        
        # Zoek naar APP_VERSION in de gedownloade code
        match = re.search(r'APP_VERSION = "([\d\.]+)"', content)
        if not match:
            if not quiet: messagebox.showerror("Update", "Kon versienummer online niet vinden.")
            return

        new_version = match.group(1)

        if new_version > APP_VERSION:
            if debug_console: debug_console.log(f"Nieuwe versie gevonden: {new_version}", "ACTION")
            if messagebox.askyesno("Update beschikbaar", 
                                   f"Er is een nieuwe versie ({new_version}) beschikbaar.\nHuidige versie: {APP_VERSION}\n\nWil je de update nu installeren?"):
                # Overschrijf huidig script
                script_path = os.path.realpath(sys.argv[0])
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                messagebox.showinfo("Klaar", "Update succesvol geïnstalleerd. Het programma wordt herstart.")
                # Herstart script
                os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            if debug_console: debug_console.log("Programma is up-to-date.", "SUCCESS")
            if not quiet: messagebox.showinfo("Update", f"Je gebruikt de nieuwste versie ({APP_VERSION}).")
            
    except Exception as e:
        if debug_console: debug_console.log(f"Updater fout: {str(e)}", "ERROR")
        if not quiet: messagebox.showerror("Update Fout", f"Kon niet controleren op updates:\n{str(e)}")


# ─── MAIN APP ───────────────────────────────────────────

class LogoDesignerApp:
    DIMENSION_PRESETS = [
        ("Website header (lagerkoning.nl)", 400, 80, 62),
        ("Website header groot", 800, 120, 96),
        ("Walzlagerkoenig.de (breed)", 1200, 140, 96),
        ("Social media banner", 1500, 200, 140),
        ("Favicon / icoon", 200, 200, 60),
        ("Visitekaartje", 600, 100, 78),
        ("Groot / print", 2400, 350, 220),
    ]

    def __init__(self):
        self.root = Tk()
        self.root.title("sm0kez Logo Designer v" + APP_VERSION)
        self.root.geometry("1300x1000")
        self.root.minsize(1100, 800)

        self.cfg = BrandConfig()
        self._load_settings()

        self.svgs = []
        self.selected_idx = 0
        self._tmp_dir = Path(tempfile.mkdtemp(prefix="wlk_logos_"))

        self.var_left = StringVar(value=self.cfg.left)
        self.var_right = StringVar(value=self.cfg.right)
        self.var_tld = StringVar(value=self.cfg.tld)
        self.var_tagline = StringVar(value=self.cfg.tagline)
        self.var_tld_scale = StringVar(value=str(self.cfg.tld_scale))
        self.var_word_gap = StringVar(value=str(self.cfg.word_gap))
        self.var_tld_gap = StringVar(value=str(self.cfg.tld_gap))
        self.var_letter_spacing = StringVar(value=str(self.cfg.letter_spacing))
        self.var_icon_offset_x = StringVar(value=str(self.cfg.icon_offset_x))
        self.var_icon_offset_y = StringVar(value=str(self.cfg.icon_offset_y))
        self.var_icon_scale = StringVar(value=str(self.cfg.icon_scale))
        self.var_width = StringVar(value=str(self.cfg.out_width))
        self.var_height = StringVar(value=str(self.cfg.out_height))
        self.var_fs_main = StringVar(value=str(self.cfg.fs_main))
        self.var_c_dark = StringVar(value=self.cfg.color_dark)
        self.var_c_red = StringVar(value=self.cfg.color_red)
        self.var_c_gold = StringVar(value=self.cfg.color_gold)
        self.var_c_white = StringVar(value=self.cfg.color_white)
        self.var_c_grey = StringVar(value=self.cfg.color_grey)
        self.var_c_bgdark = StringVar(value=self.cfg.bg_dark)
        self.var_status = StringVar(value="Klaar")

        self._build_ui()
        self.debug.log_separator("APPLICATIE GESTART")
        self.debug.log("v" + APP_VERSION + " | Updater geactiveerd", "INFO")
        self._generate()

    def _load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    d = json.load(f)
                    for k, v in d.items(): 
                        if hasattr(self.cfg, k): setattr(self.cfg, k, v)
            except: pass

    def _save_settings(self):
        try:
            with open(CONFIG_FILE, "w") as f: json.dump(asdict(self.cfg), f)
        except: pass

    def _build_ui(self):
        root = self.root
        menubar = Menu(root)
        
        # Bestand Menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exporteer geselecteerde SVG...", command=lambda: self._safe("export_sel", self._export_selected))
        file_menu.add_command(label="Exporteer alle SVG's...", command=lambda: self._safe("export_all", self._export_all))
        file_menu.add_separator()
        file_menu.add_command(label="Afsluiten", command=self._quit)
        menubar.add_cascade(label="Bestand", menu=file_menu)
        
        # Beeld Menu
        view_menu = Menu(menubar, tearoff=0)
        view_menu.add_command(label="Preview alle (browser)", command=lambda: self._safe("preview_all", self._open_all_browser))
        view_menu.add_command(label="Preview geselecteerd (browser)", command=lambda: self._safe("preview_sel", self._open_selected_browser))
        view_menu.add_separator()
        view_menu.add_command(label="Toggle debug console", command=lambda: self.debug.toggle())
        menubar.add_cascade(label="Beeld", menu=view_menu)

        # Help Menu (Nieuw voor updater)
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Zoek naar updates...", command=lambda: check_for_updates(self.debug, False))
        help_menu.add_separator()
        help_menu.add_command(label="Over...", command=lambda: messagebox.showinfo("Over", f"sm0kez Logo Designer v{APP_VERSION}\nOntwikkeld door sm0kez\nLicentie: MIT"))
        menubar.add_cascade(label="Help", menu=help_menu)

        root.config(menu=menubar)

        main_container = Frame(root)
        main_container.pack(fill=BOTH, expand=True)

        settings_frame = ttk.LabelFrame(main_container, text=" Instellingen ", padding=8)
        settings_frame.pack(fill=X, padx=10, pady=(8, 4))

        row1 = Frame(settings_frame)
        row1.pack(fill=X, pady=(0, 3))
        ttk.Label(row1, text="Links:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row1, textvariable=self.var_left, width=14).pack(side=LEFT, padx=(0, 8))
        ttk.Label(row1, text="Rechts:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row1, textvariable=self.var_right, width=12).pack(side=LEFT, padx=(0, 8))
        ttk.Label(row1, text="TLD:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row1, textvariable=self.var_tld, width=5).pack(side=LEFT, padx=(0, 8))
        ttk.Label(row1, text="TLD schaal:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row1, textvariable=self.var_tld_scale, width=5).pack(side=LEFT)

        row2 = Frame(settings_frame)
        row2.pack(fill=X, pady=(0, 3))
        ttk.Label(row2, text="Woord gap:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row2, textvariable=self.var_word_gap, width=5).pack(side=LEFT, padx=(0, 8))
        ttk.Label(row2, text="TLD gap:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row2, textvariable=self.var_tld_gap, width=5).pack(side=LEFT, padx=(0, 8))
        ttk.Label(row2, text="Letter-spacing:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row2, textvariable=self.var_letter_spacing, width=5).pack(side=LEFT, padx=(0, 16))
        ttk.Separator(row2, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=8)
        ttk.Label(row2, text="Icoon X:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row2, textvariable=self.var_icon_offset_x, width=5).pack(side=LEFT, padx=(0, 8))
        ttk.Label(row2, text="Icoon Y:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row2, textvariable=self.var_icon_offset_y, width=5).pack(side=LEFT, padx=(0, 8))
        ttk.Label(row2, text="Icoon schaal:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row2, textvariable=self.var_icon_scale, width=5).pack(side=LEFT)

        row3 = Frame(settings_frame)
        row3.pack(fill=X, pady=(0, 3))
        ttk.Label(row3, text="Breedte:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row3, textvariable=self.var_width, width=6).pack(side=LEFT, padx=(0, 8))
        ttk.Label(row3, text="Hoogte:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row3, textvariable=self.var_height, width=6).pack(side=LEFT, padx=(0, 8))
        ttk.Label(row3, text="Font size:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row3, textvariable=self.var_fs_main, width=5).pack(side=LEFT, padx=(0, 12))
        ttk.Label(row3, text="Preset:").pack(side=LEFT, padx=(0, 3))
        self.preset_combo = ttk.Combobox(row3, width=32, state="readonly", values=[p[0] for p in self.DIMENSION_PRESETS])
        self.preset_combo.pack(side=LEFT, padx=(0, 4))
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_select)

        row4 = Frame(settings_frame)
        row4.pack(fill=X, pady=(0, 3))
        ttk.Label(row4, text="Tagline:").pack(side=LEFT, padx=(0, 3))
        ttk.Entry(row4, textvariable=self.var_tagline, width=55).pack(side=LEFT, fill=X, expand=True, padx=(0, 8))

        row5 = Frame(settings_frame)
        row5.pack(fill=X, pady=(0, 3))
        self._color_buttons = {}
        for label_text, var in [("Donker", self.var_c_dark), ("Rood", self.var_c_red), ("Goud", self.var_c_gold),
                                 ("Wit", self.var_c_white), ("Grijs", self.var_c_grey), ("Achtergr.", self.var_c_bgdark)]:
            f = Frame(row5)
            f.pack(side=LEFT, padx=(0, 6))
            ttk.Label(f, text=label_text + ":").pack(side=LEFT, padx=(0, 2))
            btn = ttk.Button(f, text=var.get(), width=9,
                            command=lambda v=var, lt=label_text: self._safe("kleur:" + lt, lambda: self._pick_color(v, lt)))
            btn.pack(side=LEFT)
            self._color_buttons[id(var)] = btn

        row6 = Frame(settings_frame)
        row6.pack(fill=X, pady=(4, 0))
        for text, cmd in [("Genereer logo's", lambda: self._safe("genereer", self._generate)),
                          ("Alle in browser", lambda: self._safe("browser_all", self._open_all_browser)),
                          ("Preview geselecteerd", lambda: self._safe("browser_sel", self._open_selected_browser)),
                          ("Kopieer SVG", lambda: self._safe("copy_svg", self._copy_svg)),
                          ("Exporteer 1...", lambda: self._safe("export_sel", self._export_selected)),
                          ("Exporteer alle...", lambda: self._safe("export_all", self._export_all))]:
            ttk.Button(row6, text=text, command=cmd).pack(side=LEFT, padx=(0, 6))

        mid_frame = Frame(main_container)
        mid_frame.pack(fill=BOTH, expand=True, padx=10, pady=4)

        list_frame = ttk.LabelFrame(mid_frame, text=" Varianten (" + str(len(ALL_VARIANTS)) + ") ", padding=4)
        list_frame.pack(side=LEFT, fill=Y, padx=(0, 6))
        self.variant_listbox = ttk.Treeview(list_frame, columns=("name",), show="tree", height=18, selectmode="browse")
        self.variant_listbox.column("#0", width=0, stretch=False)
        self.variant_listbox.column("name", width=300)
        list_scroll = Scrollbar(list_frame, orient=VERTICAL, command=self.variant_listbox.yview)
        self.variant_listbox.config(yscrollcommand=list_scroll.set)
        list_scroll.pack(side=RIGHT, fill=Y)
        self.variant_listbox.pack(fill=Y, expand=True)
        self.variant_listbox.bind("<<TreeviewSelect>>", self._on_variant_select)

        right_frame = ttk.LabelFrame(mid_frame, text=" SVG Code ", padding=4)
        right_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.info_label = ttk.Label(right_frame, text="", wraplength=700, justify=LEFT)
        self.info_label.pack(fill=X, pady=(0, 4))
        code_frame = Frame(right_frame)
        code_frame.pack(fill=BOTH, expand=True)
        scrollbar = Scrollbar(code_frame, orient=VERTICAL)
        self.code_text = Text(code_frame, wrap=NONE, font=("Consolas", 9), yscrollcommand=scrollbar.set,
                             state=DISABLED, bg="#1e1e1e", fg="#d4d4d4", insertbackground="#fff")
        scrollbar.config(command=self.code_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.code_text.pack(fill=BOTH, expand=True)

        ttk.Label(main_container, textvariable=self.var_status, relief=SUNKEN, anchor=W, padding=4).pack(
            fill=X, side=BOTTOM, padx=10, pady=(0, 2))

        self.debug = DebugConsole(root)
        self.debug.pack(fill=X, side=BOTTOM, padx=10, pady=(0, 6))

    def _on_preset_select(self, event=None):
        idx = self.preset_combo.current()
        if idx < 0: return
        name, w, h, fs = self.DIMENSION_PRESETS[idx]
        self.var_width.set(str(w)); self.var_height.set(str(h)); self.var_fs_main.set(str(fs))

    def _safe(self, name, func):
        try: func()
        except Exception: self.debug.log_exception(name)

    def _pick_color(self, var, label):
        result = colorchooser.askcolor(color=var.get(), title="Kleur: " + label)
        if result and result[1]:
            var.set(result[1])
            btn = self._color_buttons.get(id(var))
            if btn: btn.config(text=result[1])

    def _int_safe(self, var, default):
        try: return int(var.get())
        except ValueError: return default

    def _float_safe(self, var, default):
        try: return float(var.get())
        except ValueError: return default

    def _sync_config(self):
        c = self.cfg
        c.left = self.var_left.get().strip() or "W\u00c4LZLAGER"
        c.right = self.var_right.get().strip() or "K\u00d6NIG"
        c.tld = self.var_tld.get().strip() or ".DE"
        c.tagline = self.var_tagline.get().strip()
        c.tld_scale = self._float_safe(self.var_tld_scale, 0.44)
        c.word_gap = self._int_safe(self.var_word_gap, 0)
        c.tld_gap = self._int_safe(self.var_tld_gap, 0)
        c.letter_spacing = self._float_safe(self.var_letter_spacing, 0)
        c.icon_offset_x = self._int_safe(self.var_icon_offset_x, 0)
        c.icon_offset_y = self._int_safe(self.var_icon_offset_y, 0)
        c.icon_scale = max(0.1, self._float_safe(self.var_icon_scale, 1.0))
        c.out_width = max(100, self._int_safe(self.var_width, 1200))
        c.out_height = max(50, self._int_safe(self.var_height, 140))
        c.fs_main = max(10, self._int_safe(self.var_fs_main, 96))
        c.color_dark = self.var_c_dark.get().strip()
        c.color_red = self.var_c_red.get().strip()
        c.color_gold = self.var_c_gold.get().strip()
        c.color_white = self.var_c_white.get().strip()
        c.color_grey = self.var_c_grey.get().strip()
        c.bg_dark = self.var_c_bgdark.get().strip()

    def _generate(self):
        self._sync_config()
        self._save_settings()
        self.svgs = []
        for fn in ALL_VARIANTS:
            try: self.svgs.append(fn(self.cfg))
            except Exception: self.svgs.append(("FOUT", "<svg></svg>"))
        self.variant_listbox.delete(*self.variant_listbox.get_children())
        for i, (label, _) in enumerate(self.svgs):
            iid = self.variant_listbox.insert("", END, values=(label,))
            if i == 0: self.variant_listbox.selection_set(iid)
        self.selected_idx = 0
        self._update_detail()
        self.var_status.set(str(len(self.svgs)) + " varianten OK")

    def _on_variant_select(self, event=None):
        sel = self.variant_listbox.selection()
        if not sel: return
        self.selected_idx = list(self.variant_listbox.get_children()).index(sel[0])
        self._update_detail()

    def _update_detail(self):
        if not self.svgs: return
        label, svg_code = self.svgs[self.selected_idx]
        self.info_label.config(text=label)
        self.code_text.config(state=NORMAL); self.code_text.delete("1.0", END)
        self.code_text.insert("1.0", svg_code); self.code_text.config(state=DISABLED)

    def _write_tmp(self, name, content):
        p = self._tmp_dir / name
        p.write_text(content, encoding="utf-8")
        return p

    def _open_all_browser(self):
        if not self.svgs: return
        p = self._write_tmp("preview_all.html", _build_all_preview_html(self.svgs, self.selected_idx))
        webbrowser.open(p.as_uri())

    def _open_selected_browser(self):
        if not self.svgs: return
        label, svg = self.svgs[self.selected_idx]
        p = self._write_tmp("preview_" + str(self.selected_idx + 1).zfill(2) + ".html", _build_single_preview_html(label, svg))
        webbrowser.open(p.as_uri())

    def _copy_svg(self):
        if not self.svgs: return
        self.root.clipboard_clear(); self.root.clipboard_append(self.svgs[self.selected_idx][1])
        self.var_status.set("SVG gekopieerd")

    def _export_selected(self):
        if not self.svgs: return
        label, svg = self.svgs[self.selected_idx]
        path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG", "*.svg")],
                                            initialfile=re.sub(r"[^a-zA-Z0-9_-]", "_", label) + ".svg")
        if path: Path(path).write_text(svg, encoding="utf-8")

    def _export_all(self):
        if not self.svgs: return
        folder = filedialog.askdirectory(title="Kies map")
        if not folder: return
        out = Path(folder); out.mkdir(parents=True, exist_ok=True)
        for i, (label, svg) in enumerate(self.svgs):
            fn = str(i + 1).zfill(2) + "_" + re.sub(r"[^a-zA-Z0-9_-]", "_", label) + ".svg"
            (out / fn).write_text(svg, encoding="utf-8")
        (out / "preview.html").write_text(_build_all_preview_html(self.svgs), encoding="utf-8")
        messagebox.showinfo("Export klaar", "Bestanden opgeslagen.")

    def _quit(self): self.root.quit()

    def run(self): self.root.mainloop()


if __name__ == "__main__":
    try:
        app = LogoDesignerApp()
        # Automatische check bij opstarten (stil op achtergrond)
        # check_for_updates(app.debug, quiet=True)
        app.run()
    except Exception:
        traceback.print_exc()
        input("\nDruk op Enter...")
