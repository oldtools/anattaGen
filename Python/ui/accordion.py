from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QScrollArea, QToolButton,
    QSizePolicy, QFrame, QLabel
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSlot


class AccordionSection(QWidget):
    def __init__(self, title: str, content: QWidget, animation_duration=200):
        super().__init__()

        self.toggle_button = QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("QToolButton { font-weight: bold; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.toggle_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggle_button.clicked.connect(self.toggle)

        self.content_area = QScrollArea()
        self.content_area.setStyleSheet("QScrollArea { background-color: transparent; }")
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.content_area.setFrameShape(QFrame.Shape.NoFrame)
        self.content_area.setWidgetResizable(True)
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)
        self.content_area.setWidget(content)

        self.animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.animation.setDuration(animation_duration)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)

        self.content_height = content.sizeHint().height()

    @pyqtSlot()
    def toggle(self):
        checked = self.toggle_button.isChecked()
        start_height = self.content_area.maximumHeight()
        end_height = self.content_height if checked else 0

        self.animation.stop()
        self.animation.setStartValue(start_height)
        self.animation.setEndValue(end_height)
        self.animation.start()


class AccordionMenu(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        for i in range(3):
            content_widget = self.create_section_content(i)
            section = AccordionSection(f"Section {i + 1}", content_widget)
            layout.addWidget(section)

        layout.addStretch(1)

    def create_section_content(self, index: int) -> QWidget:
        content = QWidget()
        content_layout = QVBoxLayout(content)
        for j in range(3):
            content_layout.addWidget(QLabel(f"Item {index + 1}.{j + 1}"))
        content_layout.addStretch(1)
        return content


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Animated Accordion Menu - Qt6")
    layout = QVBoxLayout(window)

    accordion = AccordionMenu()
    layout.addWidget(accordion)

    window.resize(300, 400)
    window.show()
    sys.exit(app.exec())