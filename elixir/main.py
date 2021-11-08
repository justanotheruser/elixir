import datetime
import sys
import logging

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QWidget, QTableView, QHBoxLayout, QLineEdit, QPushButton, \
    QVBoxLayout, QStyledItemDelegate, QDialog, QLabel, QDateEdit
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QKeyEvent
from PyQt6.QtSql import QSqlQueryModel, QSqlQuery

from .dbconnection import openDbConnection

ID_COL = 0
EXP_DATE_COL = 2


class DrugItemDelegate(QStyledItemDelegate):
    def __init__(self):
        QStyledItemDelegate.__init__(self)

    def paint(self, painter, option, index):
        if index.column() != EXP_DATE_COL:
            super().paint(painter, option, index)
        else:
            model = index.model()
            dateStr = model.data(index, Qt.ItemDataRole.DisplayRole)
            date = datetime.datetime.strptime(dateStr, "%d.%m.%Y")
            if date < datetime.datetime.now():
                painter.fillRect(option.rect, QColor(200, 0, 0))
            QApplication.style().drawItemText(painter, option.rect, option.displayAlignment,
                                              QApplication.palette(), True, dateStr)


class ElixirUi(QMainWindow):
    table: QTableView
    model: QSqlQueryModel

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elixir")
        self.setGeometry(870, 20, 400, 400)

        # Set the central widget
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        self.createTable()
        self.createToolbar()

    def createTable(self):
        self.model = QSqlQueryModel()
        self.table = QTableView()
        self.table.setModel(self.model)
        self.refreshTable()
        self.table.setItemDelegate(DrugItemDelegate())
        self.generalLayout.addWidget(self.table)

    def createToolbar(self):
        layout = QHBoxLayout()
        self.drugSearchBox = QLineEdit("поиск по названию")
        layout.addWidget(self.drugSearchBox)
        self.categorySeachBox = QLineEdit("поиск по категории")
        layout.addWidget(self.categorySeachBox)
        self.addDrugBtn = QPushButton("Добавить")
        layout.addWidget(self.addDrugBtn)
        self.generalLayout.addLayout(layout)

    def refreshTable(self):
        self.model.setQuery("SELECT id, name, exp_date FROM drugs")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            row_ids = set()
            for index in self.table.selectedIndexes():
                if index.column() == ID_COL:
                    row_ids.add(index.data(Qt.ItemDataRole.DisplayRole))
            logging.info(f'Deleting rows {row_ids}')
            deleteQuery = QSqlQuery()
            deleteQuery.prepare("DELETE FROM drugs WHERE id=:id")
            for id in row_ids:
                deleteQuery.bindValue(":id", id)
                deleteQuery.exec()
            self.refreshTable()


class AddDrugDialog(QDialog):
    def __init__(self, parent: ElixirUi):
        super().__init__(parent)
        self.main_ui = parent
        self.setWindowTitle("Добавить препарат")
        self.drugName = QLineEdit()
        nowDateStr = str(datetime.datetime.now().date())
        nowDate = QDate.fromString(nowDateStr, 'yyyy-MM-dd')
        self.expDateEdit = QDateEdit(nowDate)
        self.saveBtn = QPushButton("Добавить")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Название"))
        layout.addWidget(self.drugName)
        layout.addWidget(QLabel("Срок годности истечёт"))
        layout.addWidget(self.expDateEdit)
        layout.addWidget(self.saveBtn)
        self.setLayout(layout)
        self.saveBtn.clicked.connect(self.save)

    def save(self):
        if not self.drugName.text():
            return

        insertQuery = QSqlQuery()
        insertQuery.prepare("""
            INSERT INTO drugs (name, exp_date)
            VALUES (:name, :exp_date)""")
        insertQuery.bindValue(":name", self.drugName.text())
        insertQuery.bindValue(":exp_date", self.expDateEdit.text())
        insertQuery.exec()
        if insertQuery.lastError().text():
            logging.error(insertQuery.lastError().text())
        self.main_ui.refreshTable()
        self.close()


class ElixirController:
    def __init__(self, view: ElixirUi):
        self._view = view
        self._connectSignals()

    def _connectSignals(self):
        self._view.addDrugBtn.clicked.connect(self.openAddDrugDialog)

    def openAddDrugDialog(self):
        logging.info("Open AddDrugDialog")
        dialog = AddDrugDialog(self._view)
        dialog.show()


def main():
    logging.basicConfig(filename='../elixir.log',
                        level=logging.DEBUG,
                        format='%(asctime)s | %(levelname)s | %(message)s')
    logging.debug(f"Elixir started")
    openDbConnection()
    app = QApplication(sys.argv)
    view = ElixirUi()
    view.show()
    controller = ElixirController(view)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
