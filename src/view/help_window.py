import os
import json
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeWidgetItem,
    QTreeWidget,
    QTextBrowser,
    QSplitter,
)
from PyQt5.QtCore import Qt


class HelpWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Help")
        self.resize(700, 400)

        self.help_content: dict = {}

        self.create_ui()

    def create_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        self.navigation_tree_widget = QTreeWidget()
        self.navigation_tree_widget.setHeaderHidden(True)
        self.navigation_tree_widget.itemClicked.connect(
            lambda item, column: self.on_item_clicked(item)
        )
        splitter.addWidget(self.navigation_tree_widget)

        self.content_text_browser = QTextBrowser()
        self.content_text_browser.setReadOnly(True)
        # self.text_area.setOpenExternalLinks(True) # Allow links
        splitter.addWidget(self.content_text_browser)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        self.load_help_content()
        self.populate_navigation_tree_widget()

    def load_help_content(self):
        path = os.path.join(os.path.dirname(__file__), "help_content.json")

        with open(path, "r", encoding="utf-8") as f:
            self.help_content = json.load(f)

    def populate_navigation_tree_widget(self):
        for category, items in self.help_content.items():
            cat_item = QTreeWidgetItem([category])

            for sub_item in items:
                if sub_item != category:
                    cat_item.addChild(QTreeWidgetItem([sub_item]))

            self.navigation_tree_widget.addTopLevelItem(cat_item)

    def on_item_clicked(self, item):
        parent = item.parent()

        if parent:
            category = parent.text(0)
            sub_item = item.text(0)
            content = self.help_content.get(category, {}).get(sub_item, "")
            self.content_text_browser.setHtml(content)

        else:
            category = item.text(0)
            section_info = self.help_content.get(category, {})
            section_text = section_info.get(category, f"Section : {category}")
            self.content_text_browser.setHtml(section_text)
