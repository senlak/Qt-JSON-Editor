import sys
import json
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *


class JsonEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Editor")
        self.setWindowIcon(QIcon('Icons/icon.png'))
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setColumnCount(2)
        self.tree_widget.setHeaderLabels(["Key", "Value"])
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tree_widget.setSizePolicy(size_policy)
        self.modified = False
        self.tree_widget.itemChanged.connect(self.mark_modified)

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        
        new_file_action = QAction(
            QIcon("Icons/file_new.svg"), "New File", self)
        new_file_action.triggered.connect(self.new_file)
        file_menu.addAction(new_file_action)
        
        open_action = QAction(QIcon("Icons/file_open.svg"), "Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        self.save_action = QAction(QIcon("Icons/file_save.svg"), "Save", self)
        self.save_action.triggered.connect(self.save_file)
        file_menu.addAction(self.save_action)
        
        save_as_action = QAction(
            QIcon("Icons/file_saveas.svg"), "Save As", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        close_file_action = QAction(
            QIcon("Icons/file_close.svg"), "Close", self)
        close_file_action.triggered.connect(self.close_file)
        file_menu.addAction(close_file_action)
        
        edit_menu = menu_bar.addMenu("Edit")
        
        add_node_action = QAction(
            QIcon("Icons/node_add.svg"), "Add Node", self)
        add_node_action.triggered.connect(self.add_node)
        edit_menu.addAction(add_node_action)
        
        remove_node_action = QAction(
            QIcon("Icons/node_delete.svg"), "Remove Node", self)
        remove_node_action.triggered.connect(self.remove_node)
        edit_menu.addAction(remove_node_action)
        
        edit_node_action = QAction(
            QIcon("Icons/node_edit.svg"), "Edit Node", self)
        edit_node_action.triggered.connect(self.edit_node)
        edit_menu.addAction(edit_node_action)
        
        toolbar = QToolBar(self)
        
        self.addToolBar(toolbar)
        toolbar.addAction(new_file_action)
        toolbar.addAction(open_action)
        toolbar.addAction(self.save_action)
        toolbar.addAction(save_as_action)
        toolbar.addAction(close_file_action)
        toolbar.addSeparator()
        toolbar.addAction(add_node_action)
        toolbar.addAction(remove_node_action)
        toolbar.addAction(edit_node_action)
        
        layout = QVBoxLayout()
        layout.addWidget(self.tree_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        container = QWidget()
        container.setLayout(layout)
        
        self.setCentralWidget(container)
        self.save_action.setEnabled(False)
        self.current_file = None

    def mark_modified(self):
        self.modified = True
        self.save_action.setEnabled(True)

    def new_file(self):
        self.check_modified()
        self.tree_widget.clear()
        self.current_file = None
        self.json_data = {}
        self.modified = False
        self.save_action.setEnabled(False)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open JSON file", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            if not file_name.lower().endswith('.json'):
                QMessageBox.critical(
                    self, "Error", "Invalid file format. Please select a JSON file.")
                return
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    self.json_data = json.load(file)
            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "Error", f"Invalid JSON file: {e}")
                return
            except UnicodeDecodeError as e:
                QMessageBox.critical(
                    self, "Error", f"Unable to read file: {e}")
                return
            self.setWindowTitle(f"JSON Editor - {file_name}")
            self.current_file = file_name
            self.populate_tree()
            self.modified = False
            self.save_action.setEnabled(False)

    def save_file(self):
        if not self.modified:
            return
        if not self.current_file:
            self.save_file_as()
            return
        with open(self.current_file, "w") as file:
            json.dump(self.json_data, file, indent=2)
        self.modified = False
        self.save_action.setEnabled(False)

    def save_file_as(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save JSON file as", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            self.save_json_data(file_name)
            self.current_file = file_name
            self.setWindowTitle(f"JSON Editor - {file_name}")

    def close_file(self):
        if self.modified:
            save_msg = QMessageBox(self)
            save_msg.setWindowTitle("Save Changes")
            save_msg.setText("The current file has been modified.")
            save_msg.setInformativeText("Do you want to save your changes?")
            save_msg.setStandardButtons(
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            save_msg.setDefaultButton(QMessageBox.Save)
            response = save_msg.exec()
            if response == QMessageBox.Save:
                self.save_file()
            elif response == QMessageBox.Cancel:
                return
        self.tree_widget.clear()
        self.current_file = None
        self.json_data = {}

    def save_json_data(self, file_name):
        json_data = self.get_tree_data(self.tree_widget.invisibleRootItem())
        with open(file_name, 'w') as file:
            json.dump(json_data, file, indent=4)

    def populate_tree(self):
        self.tree_widget.clear()
        self.build_tree(self.json_data, self.tree_widget.invisibleRootItem())

    def build_tree(self, data, parent_item):
        if isinstance(data, dict):
            for key, value in data.items():
                item = QTreeWidgetItem(parent_item)
                item.setText(0, key)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                if isinstance(value, (list, dict)):
                    self.build_tree(value, item)
                else:
                    item.setText(1, str(value))
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                item = QTreeWidgetItem(parent_item)
                item.setText(0, str(index))
                if isinstance(value, (list, dict)):
                    self.build_tree(value, item)
                else:
                    item.setText(1, str(value))
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
            parent_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)

    def get_tree_data(self, item):
        child_count = item.childCount()
        if child_count == 0:
            return item.text(1)
        data = {}
        is_list = False
        for index in range(child_count):
            child_item = item.child(index)
            key = child_item.text(0)
            if key.isdigit():
                is_list = True
                key = int(key)
            data[key] = self.get_tree_data(child_item)
        if is_list:
            data = [data[key] for key in sorted(data.keys())]
        return data

    def add_node(self):
        selected_items = self.tree_widget.selectedItems()
        if not selected_items and self.tree_widget.topLevelItemCount() == 0:
            key, ok = QInputDialog.getText(self, "Add Node", "Enter the key:")
            if not ok:
                return
            new_item = QTreeWidgetItem([key, ""])
            new_item.setFlags(new_item.flags() | Qt.ItemIsEditable)
            self.tree_widget.addTopLevelItem(new_item)
            self.mark_modified()
            return
        if not selected_items:
            QMessageBox.warning(self, "No Node Selected",
                                "Please select a node to add a child.")
            return
        parent_item = selected_items[0]
        key, ok = QInputDialog.getText(self, "Add Node", "Enter the key:")
        if not ok:
            return
        new_item = QTreeWidgetItem([key, ""])
        parent_item.addChild(new_item)
        parent_item.setExpanded(True)
        self.mark_modified()

    def check_modified(self):
        if self.modified:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("The document has been modified.")
            msg_box.setInformativeText("Do you want to save your changes?")
            msg_box.setStandardButtons(
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Save)
            response = msg_box.exec()
            if response == QMessageBox.Save:
                self.save_file()
            elif response == QMessageBox.Discard:
                self.modified = False
                self.save_action.setEnabled(False)

    def remove_node(self):
        selected_items = self.tree_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Warning", "Please select a node in the tree before removing a node.")
            return
        item_to_remove = selected_items[0]
        parent_item = item_to_remove.parent()
        if parent_item is None:
            index = self.tree_widget.indexOfTopLevelItem(item_to_remove)
            self.tree_widget.takeTopLevelItem(index)
        else:
            index = parent_item.indexOfChild(item_to_remove)
            parent_item.takeChild(index)

    def edit_node(self):
        selected_items = self.tree_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Node Selected",
                                "Please select a node to edit.")
            return
        item = selected_items[0]
        self.tree_widget.editItem(item, 0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JsonEditor()
    window.show()
    sys.exit(app.exec())
