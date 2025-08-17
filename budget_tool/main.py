import os
import sys

import ui

# Ensure the script's directory is in sys.path
tool_dir = os.path.dirname(os.path.abspath(__file__))
if tool_dir not in sys.path:
    sys.path.insert(0, tool_dir)


# Launch your tool
def main():
    ui.launch()

if __name__ == "__main__":
    main()
