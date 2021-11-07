import datetime
import sys
import logging

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QWidget, QTableView, QTableWidget, QTableWidgetItem, QHBoxLayout, QGridLayout, QLineEdit, QPushButton, \
    QVBoxLayout, QStyledItemDelegate
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QColor
from PyQt6.QtSql import QSqlDatabase, QSqlQueryModel

from dbconnection import openDbConnection

EXP_DATE_COL = 1


class DrugItemDelegate(QStyledItemDelegate):
    def __init__(self):
        QStyledItemDelegate.__init__(self)

    def paint(self, painter, option, index):
        if index.column() != EXP_DATE_COL:
            super().paint(painter, option, index)
        else:
            model = index.model()
            date = model.data(index, Qt.ItemDataRole.DisplayRole)
            painter.fillRect(option.rect, QColor(200, 0, 0))
            QApplication.style().drawItemText(painter, option.rect, option.displayAlignment,
                                              QApplication.palette(), True, date)


class ElixirUi(QMainWindow):
    table: QTableView

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
        model = QSqlQueryModel()
        model.setQuery("SELECT name, exp_date FROM drugs")
        self.table = QTableView()
        self.table.setModel(model)
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


class ElixirController:
    def __init__(self, view : ElixirUi):
        self._view = view
        self._connectSignals()

    def _connectSignals(self):
        self._view.addDrugBtn.clicked.connect(self.openAddDrugDialog)

    def openAddDrugDialog(self):
        pass



def main():
    logging.basicConfig(filename='elixir.log',
                        level=logging.DEBUG,
                        format='%(asctime)s | %(levelname)s | %(message)s')
    logging.debug(f"Elixir started")
    openDbConnection()
    app = QApplication(sys.argv)
    view = ElixirUi()
    view.show()
    ElixirController(view)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
