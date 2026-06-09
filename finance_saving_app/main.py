import importlib

from finance_saving_app import ui

importlib.reload(ui)

def main():
    ui.launch()


if __name__ == "__main__":
    main()
