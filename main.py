"""Entry point.
  python main.py          -> GUI
  python main.py --cli    -> terminal
"""

import sys


def main():
    if "--cli" in sys.argv:
        from cli import run_cli
        run_cli()
    else:
        from gui import App
        App().mainloop()


if __name__ == "__main__":
    main()