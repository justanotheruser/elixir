import logging

from PyQt6.QtSql import QSqlDatabase

DB_NAME = ".\\elixir_db.sqlite3"


def initTables(db: QSqlDatabase) -> None:
    logging.info("Creating tables")
    result = db.exec("CREATE TABLE drugs ("
                     "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "name TEXT NOT NULL,"
                     "exp_date CHAR(10));"
                     )
    if result.lastError().text():
        logging.error(result.lastError().text())
    result = db.exec("CREATE TABLE categories ("
                     "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "name TEXT NOT NULL,"
                     "description TEXT);"
                     )
    if result.lastError().text():
        logging.error(result.lastError().text())
    result = db.exec("CREATE TABLE drugs_categories ("
                     "drug_id INTEGER NOT NULL,"
                     "cat_id INTEGER NOT NULL,"
                     "CONSTRAINT fk_drug_id FOREIGN KEY (drug_id) REFERENCES drugs(id) ON DELETE CASCADE,"
                     "CONSTRAINT fk_cat_id FOREIGN KEY (cat_id) REFERENCES cat(id));")
    if result.lastError().text():
        logging.error(result.lastError().text())


def openDbConnection() -> None:
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(DB_NAME)
    logging.info(f'Opening SQLite DB at {DB_NAME}')
    if not db.open():
        logging.error("Failed to open DB")
    if not db.tables():
        initTables(db)
