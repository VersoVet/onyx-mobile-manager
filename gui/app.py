"""Point d'entree de l'application GUI PyQt6."""

import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main() -> None:
    """Lance l'application Onyx Mobile Manager."""
    app = QApplication(sys.argv)
    app.setApplicationName("Onyx Mobile Manager")
    app.setOrganizationName("Onyx")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
