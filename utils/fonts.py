"""
Matplotlib Chinese font configuration.
Import this before any matplotlib figure creation.
"""
import sys
import matplotlib
import matplotlib.pyplot as plt


def setup_matplotlib_fonts():
    """Configure matplotlib to display Chinese characters correctly."""
    if sys.platform == 'win32':
        font_list = [
            'Microsoft YaHei', 'SimHei', 'SimSun',
            'WenQuanYi Zen Hei', 'DejaVu Sans'
        ]
    elif sys.platform == 'darwin':
        font_list = [
            'PingFang SC', 'Heiti SC', 'STHeiti',
            'Microsoft YaHei', 'SimHei', 'DejaVu Sans'
        ]
    else:
        font_list = [
            'WenQuanYi Zen Hei', 'Noto Sans CJK SC', 'Noto Sans CJK JP',
            'SimHei', 'Microsoft YaHei', 'DejaVu Sans'
        ]

    matplotlib.rcParams['font.sans-serif'] = font_list
    matplotlib.rcParams['axes.unicode_minus'] = False
    matplotlib.rcParams['font.size'] = 10
    matplotlib.rcParams['figure.dpi'] = 100
    matplotlib.rcParams['savefig.dpi'] = 150


setup_matplotlib_fonts()
