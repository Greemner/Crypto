from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMessageBox
from Cyphers import *
from Sockets import Server
import sys
import json
import pickle
from threading import Thread
import pandas as pd
import openpyxl


class PlayerTable:

    def __init__(self, root, max_players):

        self.l_quest = 100
        self.table = QtWidgets.QTableWidget(root)
        self.table.setGeometry(QtCore.QRect(30, 30, 750, 500))
        self.table.setStyleSheet('background-color: white')

        self.table.setColumnCount(3)
        self.table.setRowCount(max_players)
        self.table.setHorizontalHeaderLabels(['ФИО студента', 'Текущий вопрос', 'Количество баллов'])

        self.table.horizontalHeaderItem(0).setToolTip("Column 1")
        for i in range(3):
            self.table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignLeft)
            if i == 0:
                w = 380
            else:
                w = 160
            self.table.setColumnWidth(i, w)

        self.last_index = 0
        self.finder = {}

    def add(self, name):
        self.table.setItem(self.last_index, 0, QtWidgets.QTableWidgetItem(name))
        self.table.setItem(self.last_index, 1, QtWidgets.QTableWidgetItem('-'))
        self.table.setItem(self.last_index, 2, QtWidgets.QTableWidgetItem('0'))
        self.finder[name] = [self.last_index, 1, 0]
        self.last_index += 1

    def change(self, name, correct, end=False):
        index = self.finder[name][0]
        if end:
            self.table.setItem(index, 1, QtWidgets.QTableWidgetItem('Закончил'))
        else:
            self.finder[name][1] += 1
            quest_num = str(self.finder[name][1])
            if int(quest_num) > self.l_quest:
                self.table.setItem(index, 1, QtWidgets.QTableWidgetItem('Закончил'))
            else:
                self.table.setItem(index, 1, QtWidgets.QTableWidgetItem('Вопрос ' + quest_num))

        self.finder[name][2] += correct
        marks = str(self.finder[name][2])
        self.table.setItem(index, 2, QtWidgets.QTableWidgetItem(marks))


class App(QtWidgets.QMainWindow):

    def setup_ui(self):
        # Общие настройки
        self.setObjectName("MainWindow")
        self.setFixedSize(1200, 800)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setStyleSheet('background-color: rgb(221, 188, 149); font: 10pt Tahoma')
        # Главное окно переключения виджетов
        self.mainStackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.mainStackedWidget.setGeometry(QtCore.QRect(0, 0, 1200, 800))
        self.mainStackedWidget.setObjectName("mainStackedWidget")

        # Первая страница с тремя кнопками
        self.hello_page = QtWidgets.QWidget()
        self.hello_page.setObjectName("hello_page")
        # Кнопка запуска игры
        self.start_btn = QtWidgets.QPushButton(self.hello_page)
        self.start_btn.clicked.connect(self.start_func)
        self.start_btn.setText('Начать')
        self.start_btn.setStyleSheet(button_style())
        self.start_btn.setEnabled(True)
        self.start_btn.setGeometry(QtCore.QRect(450, 320, 300, 60))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.start_btn.sizePolicy().hasHeightForWidth())
        self.start_btn.setSizePolicy(sizePolicy)
        self.start_btn.setObjectName("start_btn")
        # Кнопка создания варианта
        self.create_var_btn = QtWidgets.QPushButton(self.hello_page)
        self.create_var_btn.clicked.connect(lambda x: self.mainStackedWidget.setCurrentIndex(1))
        self.create_var_btn.setText('Создать вариант')
        self.create_var_btn.setStyleSheet(button_style())
        self.create_var_btn.setEnabled(True)
        self.create_var_btn.setGeometry(QtCore.QRect(450, 420, 300, 60))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.create_var_btn.sizePolicy().hasHeightForWidth())
        self.create_var_btn.setSizePolicy(sizePolicy)
        self.create_var_btn.setObjectName("create_var_btn")

        # Добавление приветственной страницы на главный виджет
        self.mainStackedWidget.addWidget(self.hello_page)

        # Страница для создания варианта
        self.var_page = QtWidgets.QWidget()
        self.var_page.setObjectName("var_page")
        # Надпись про количество вопросов
        self.num_quest_label = QtWidgets.QLabel(self.var_page)
        self.num_quest_label.setText('Количество вопросов:')
        self.num_quest_label.setGeometry(QtCore.QRect(410, 20, 180, 30))
        self.num_quest_label.setObjectName("num_quest_label")
        # Поле ввода количества вопросов
        self.num_quest_edit = QtWidgets.QLineEdit(self.var_page)
        self.num_quest_edit.setStyleSheet(input_style())
        self.num_quest_edit.setGeometry(QtCore.QRect(590, 20, 40, 30))
        self.num_quest_edit.setObjectName("num_quest_edit")
        # Кнопка для начала редактирования вопросов в варианте
        self.create_quest_btn = QtWidgets.QPushButton(self.var_page)
        self.create_quest_btn.setText('Начать')
        self.create_quest_btn.setStyleSheet(button_style(font_size=12))
        self.create_quest_btn.clicked.connect(self.create_quest_func)
        self.create_quest_btn.setGeometry(QtCore.QRect(680, 10, 120, 50))
        self.create_quest_btn.setObjectName("create_quest_btn")
        # Виджеты для редактирования по количетсву вопросов
        self.questFrame = QtWidgets.QFrame(self.var_page)
        self.questFrame.setStyleSheet(frame_style())
        self.questFrame.setHidden(True)

        self.questFrame.setGeometry(QtCore.QRect(25, 70, 1150, 700))
        self.questFrame.setObjectName("questFrame")

        self.mainStackedWidget.addWidget(self.var_page)

        self.setCentralWidget(self.centralwidget)
        self.mainStackedWidget.setCurrentIndex(0)

    def start_func(self):
        self.fill_start_game_page()
        self.server = Server(self.table_players)
        self.server.socket.bind(('', 1234))
        # self.server.socket.bind(('172.18.7.101', 1234))
        self.server.socket.listen(3)
        self.server.socket.setblocking(False)
        self.server_thread = Thread(target=self.server.start)
        self.server_thread.start()
        print('Сервер запущен')
        self.mainStackedWidget.setCurrentIndex(2)

    def fill_start_game_page(self):
        self.game_page = QtWidgets.QWidget()
        self.game_page.setObjectName("game_page")
        # Надпись про выбор файла с вариантом
        self.num_quest_label = QtWidgets.QLabel(self.game_page)
        self.num_quest_label.setText('Файл с вариантом:')
        self.num_quest_label.setGeometry(QtCore.QRect(390, 20, 200, 30))
        self.num_quest_label.setObjectName("num_quest_label")
        # Frame с карточками игроков
        self.players_frame = QtWidgets.QFrame(self.game_page)
        self.players_frame.setHidden(True)
        self.players_frame.setStyleSheet('background-color: white')
        self.players_frame.setGeometry(QtCore.QRect(195, 100, 810, 560))
        self.players_frame.setStyleSheet(frame_style())
        self.players_frame.setObjectName("players_frame")

        self.table_players = PlayerTable(self.players_frame, 30)
        # Frame с предпросмотром варианта
        self.var_frame = QtWidgets.QFrame(self.game_page)
        self.var_frame.setHidden(True)
        self.var_frame.setGeometry(QtCore.QRect(0, 50, 1200, 720))
        self.var_frame.setObjectName("var_frame")
        # Кнопка выбора файла с вариантом
        self.choose_file_btn = QtWidgets.QPushButton(self.game_page)
        self.choose_file_btn.setText('Выбрать файл')
        self.choose_file_btn.setStyleSheet(button_style(font_size=12))
        self.choose_file_btn.clicked.connect(self.choose_file_func)
        self.choose_file_btn.setGeometry(QtCore.QRect(610, 10, 140, 50))
        self.choose_file_btn.setObjectName("choose_file_btn")
        # Кнопка для создания игровой комнаты
        self.create_room_btn = QtWidgets.QPushButton(self.game_page)
        self.create_room_btn.setStyleSheet(button_style(font_size=12))
        self.create_room_btn.setText('Создать комнату')
        self.create_room_btn.clicked.connect(self.create_room_func)
        self.create_room_btn.setGeometry(QtCore.QRect(470, 700, 260, 50))
        self.create_room_btn.setObjectName("create_room_btn")
        # Кнопка для завершения
        self.finish_btn = QtWidgets.QPushButton(self.game_page)
        self.finish_btn.setStyleSheet(button_style(font_size=12))
        self.finish_btn.setText('Завершить')
        self.finish_btn.clicked.connect(self.finish_func)
        self.finish_btn.setGeometry(QtCore.QRect(510, 700, 180, 50))
        self.finish_btn.setHidden(True)

        self.mainStackedWidget.addWidget(self.game_page)

    def finish_func(self):
        data = {'Key': 1, 'Message': True}
        data = pickle.dumps(data)
        for user in self.server.players:
            user.sendall(data)

        ans = self.server.answers
        try:
            df = pd.read_excel('Статистика.xlsx', engine='openpyxl')
            df.drop(columns=['Unnamed: 0'], inplace=True)
        except Exception as e:
            df = pd.DataFrame(data=ans[0])
            for i in range(1, len(ans)):
                df = df.append(ans[i], ignore_index=True)
            df.to_excel('Статистика.xlsx')
        else:
            for i in range(len(ans)):
                df = df.append(ans[i], ignore_index=True)
            df.to_excel('Статистика.xlsx')
        self.server.socket.shutdown(1)
        self.close()

    def start_game(self):
        self.create_room_btn.setHidden(True)
        self.finish_btn.setHidden(False)
        self.table_players.l_quest = len(self.game_var)
        data = {'Key': 0, 'Message': self.game_var}
        data = pickle.dumps(data)
        for user in self.server.players:
            user.sendall(data)

    def create_room_func(self):
        self.var_frame.setHidden(True)
        self.choose_file_btn.setHidden(True)
        self.num_quest_label.setHidden(True)
        self.players_frame.setHidden(False)
        self.create_room_btn.setText('Отправить задание')
        self.create_room_btn.clicked.connect(self.start_game)
        self.create_room_btn.setStyleSheet(button_style(font_size=12))

    def choose_file_func(self):
        name = QtWidgets.QFileDialog.getOpenFileName()
        name = name[0]
        with open(name, 'r') as fp:
            self.game_var = json.load(fp)
        height = min(len(self.game_var) * 40 + 70, 640)
        self.var_frame.setGeometry(QtCore.QRect(110, 100, 980, height))
        self.var_frame.setStyleSheet(frame_style())
        if self.table_var_flag:
            height = min(len(self.game_var) * 40 + 30, 600)
            self.table_var.setGeometry(QtCore.QRect(20, 20, 940, height))
            self.table_var.setRowCount(len(self.game_var))
            for i in range(len(self.game_var)):
                info = self.game_var[str(i + 1)]
                self.table_var.setItem(i, 0, QtWidgets.QTableWidgetItem(str(i + 1)))
                self.table_var.setItem(i, 1, QtWidgets.QTableWidgetItem(info[0]))
                self.table_var.setItem(i, 2, QtWidgets.QTableWidgetItem(info[1]))
                self.table_var.setItem(i, 3, QtWidgets.QTableWidgetItem(info[2]))
                self.table_var.setItem(i, 4, QtWidgets.QTableWidgetItem(info[3]))
                self.table_var.setItem(i, 5, QtWidgets.QTableWidgetItem(info[4]))
        else:
            self.table_var = QtWidgets.QTableWidget(self.var_frame)
            self.table_var.setStyleSheet('background-color: white')
            height = min(len(self.game_var) * 40 + 30, 600)
            self.table_var.setGeometry(QtCore.QRect(20, 20, 940, height))

            self.table_var.setColumnCount(6)
            self.table_var.setRowCount(len(self.game_var))
            self.table_var.setHorizontalHeaderLabels(['Номер вопроса', 'Метод шифрования', 'Исходный текст', 'Зашифрованный текст', 'Ключ', 'Задание'])

            for i in range(6):
                self.table_var.horizontalHeaderItem(i).setTextAlignment(Qt.AlignLeft)
                if i == 0:
                    w = 60
                elif i == 1:
                    w = 160
                elif i in [4, 5]:
                    w = 150
                else:
                    w = 200
                self.table_var.setColumnWidth(i, w)

            for i in range(len(self.game_var)):
                info = self.game_var[str(i + 1)]
                self.table_var.setItem(i, 0, QtWidgets.QTableWidgetItem(str(i + 1)))
                self.table_var.setItem(i, 1, QtWidgets.QTableWidgetItem(info[0]))
                self.table_var.setItem(i, 2, QtWidgets.QTableWidgetItem(info[1]))
                self.table_var.setItem(i, 3, QtWidgets.QTableWidgetItem(info[2]))
                self.table_var.setItem(i, 4, QtWidgets.QTableWidgetItem(info[3]))
                self.table_var.setItem(i, 5, QtWidgets.QTableWidgetItem(info[4]))

            self.table_var.resizeRowsToContents()
            self.var_frame.setHidden(False)
            self.table_var_flag = True

    def fill_quest_page(self):
        # Редактирование одного вопроса
        # Номер вопроса
        self.label = QtWidgets.QLabel(self.questFrame)
        self.label.setText('Вопрос 1 из ' + str(self.num_quest))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(QtCore.QRect(500, 20, 150, 30))
        self.label.setObjectName("label_2")
        # Выбор метода шифрования
        self.type_crypto_label = QtWidgets.QLabel(self.questFrame)
        self.type_crypto_label.setText('Метод шифрования:')
        self.type_crypto_label.setGeometry(QtCore.QRect(420, 70, 170, 30))
        self.type_crypto_label.setObjectName("type_crypto_label")
        # Combobox с вариантами методов
        self.comboBox = QtWidgets.QComboBox(self.questFrame)
        self.comboBox.setStyleSheet(frame_input_style())
        self.comboBox.setGeometry(QtCore.QRect(600, 70, 170, 30))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem(" ")
        self.comboBox.addItem("Гаммирование")
        self.comboBox.addItem("Перестановка")
        self.comboBox.addItem("Шифр Цезаря")
        self.comboBox.addItem("Шифр Виженера")
        self.comboBox.addItem("Шифр Плейфера")
        self.comboBox.addItem("Квадрат Полибия")
        self.comboBox.activated[str].connect(self.crypto_type)
        # Кнопка зашифровать
        self.cypher_btn = QtWidgets.QPushButton(self.questFrame)
        self.cypher_btn.clicked.connect(self.cypher_func)
        self.cypher_btn.setText('Зашифровать')
        self.cypher_btn.setStyleSheet(button_style(font_size=12))
        self.cypher_btn.setGeometry(QtCore.QRect(495, 610, 160, 50))
        self.cypher_btn.setObjectName("cypher_btn")
        self.cypher_btn.setHidden(True)
        # Кнопка далее
        self.next_quest_btn = QtWidgets.QPushButton(self.questFrame)
        self.next_quest_btn.clicked.connect(self.next_quest_func)
        self.next_quest_btn.setText('Далее')
        self.next_quest_btn.setStyleSheet(button_style(font_size=12))
        self.next_quest_btn.setGeometry(QtCore.QRect(960, 610, 160, 50))
        self.next_quest_btn.setObjectName("next_quest_btn")
        # Поле для ввода текста для шифрования
        self.text_edit = QtWidgets.QTextEdit(self.questFrame)
        self.text_edit.setPlaceholderText('Введите сообщение...')
        # self.text_edit.setAlignment(Qt.AlignCenter)
        self.text_edit.setStyleSheet(text_style())
        self.text_edit.setGeometry(QtCore.QRect(50, 180, 450, 150))
        self.text_edit.setObjectName("text_edit")
        self.text_edit.setHidden(True)
        # Поле для вывода зашифрованного текста
        self.text_browser = QtWidgets.QTextBrowser(self.questFrame)
        self.text_browser.setPlaceholderText('Здесь отобразится зашифрованное сообщение')
        self.text_browser.setAlignment(Qt.AlignCenter)
        self.text_browser.setStyleSheet(text_style())
        self.text_browser.setGeometry(QtCore.QRect(650, 180, 450, 150))
        self.text_browser.setObjectName("text_browser")
        self.text_browser.setHidden(True)
        # Ключ
        self.label_key = QtWidgets.QLabel(self.questFrame)
        self.label_key.setText('Ключ:')
        self.label_key.setGeometry(QtCore.QRect(50, 400, 80, 30))
        self.label_key.setObjectName("label_key")
        self.edit_key = QtWidgets.QLineEdit(self.questFrame)
        self.edit_key.setStyleSheet(frame_input_style())
        self.edit_key.setGeometry(QtCore.QRect(130, 400, 120, 30))
        self.edit_key.setObjectName("edit_key")
        self.label_key.setHidden(True)
        self.edit_key.setHidden(True)
        # Задание
        self.label_task = QtWidgets.QLabel(self.questFrame)
        self.label_task.setText('Студенту необходимо:')
        self.label_task.setGeometry(QtCore.QRect(50, 450, 190, 30))
        self.label_task.setHidden(True)
        self.task1 = QtWidgets.QRadioButton(self.questFrame)
        self.task1.setStyleSheet(frame_input_style())
        self.task1.setText("Зашифровать")
        self.task1.setGeometry(QtCore.QRect(250, 450, 140, 30))
        self.task1.setChecked(True)
        self.task1.choice = "зашифровать"
        self.task1.toggled.connect(self.onClicked)
        self.task1.setHidden(True)
        self.task2 = QtWidgets.QRadioButton(self.questFrame)
        self.task2.setStyleSheet(frame_input_style())
        self.task2.setText("Расшифровать")
        self.task2.setGeometry(QtCore.QRect(420, 450, 140, 30))
        self.task2.setChecked(True)
        self.task2.choice = "расшифровать"
        self.task2.toggled.connect(self.onClicked)
        self.task2.setHidden(True)

    def onClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            self.task_choice = radioButton.choice

    def crypto_type(self, type):
        self.crypto_method = type
        self.text_edit.setHidden(False)
        self.text_browser.setHidden(False)
        self.label_key.setHidden(False)
        self.edit_key.setHidden(False)
        self.cypher_btn.setHidden(False)
        self.label_task.setHidden(False)
        self.task1.setHidden(False)
        self.task2.setHidden(False)

    def cypher_func(self):
        try:
            text = self.text_edit.toPlainText().lower()
            text = ''.join(text.split())
            if self.crypto_method == 'Гаммирование':
                temp = self.edit_key.text().split(',')
                key = [temp[0], int(temp[1])]
                text_key = self.edit_key.text()
            elif self.crypto_method in ['Шифр Плейфера', 'Квадрат Полибия']:
                key = None
                text_key = '_'
            else:
                key = self.edit_key.text()
                text_key = key

            crypto_text = self.type_func[self.crypto_method](text, key)
            self.new_var[self.last_quest] = [self.crypto_method, text, crypto_text, text_key, self.task_choice]
            self.text_browser.setText(crypto_text)
            self.cypher_flag = True
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Ошибка!')
            msg.setInformativeText('Проверьте правильность введенных данных.')
            msg.exec_()

    def next_quest_func(self):
        if self.crypto_method == ' ':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Ошибка!')
            msg.setInformativeText('Выберете метод шифрования.')
            msg.exec_()
        else:
            if self.cypher_flag:
                self.last_quest += 1
                self.label.setText('Вопрос ' + str(self.last_quest) + ' из ' + str(self.num_quest))
                self.cypher_btn.setHidden(True)
                self.text_edit.setHidden(True)
                self.label_key.setHidden(True)
                self.edit_key.setHidden(True)
                self.label_task.setHidden(True)
                self.task1.setHidden(True)
                self.task2.setHidden(True)
                self.edit_key.clear()
                self.text_edit.clear()
                self.text_browser.setHidden(True)
                self.text_browser.clear()
                self.comboBox.setCurrentText(' ')
                self.crypto_method = ' '
                self.cypher_flag = False
                if self.last_quest == self.num_quest:
                    self.next_quest_btn.setText('Сохранить')
                    self.next_quest_btn.clicked.connect(self.save_var)
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText('Ошибка!')
                msg.setInformativeText('Нажмите "Зашифровать".')
                msg.exec_()

    def save_var(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
        name = name[0] + '.json'
        with open(name, 'w') as fp:
            json.dump(self.new_var, fp)

        self.mainStackedWidget.setCurrentIndex(0)

    def create_quest_func(self):
        self.num_quest = int(self.num_quest_edit.text())
        self.new_var = {}
        self.fill_quest_page()
        self.questFrame.setHidden(False)

    def __init__(self):
        super(App, self).__init__()
        self.button_style = """QPushButton {
                                                 border: 2px;
                                                 border-radius: 6px;
                                                 background-color: rgb(222, 196, 158);
                                                 min-width: 80px;
                                                padding: 18px 32px;
                                                font: 16pt "Tahoma";
                                             }
                                            
                                             QPushButton:hover {
                                                 background-color: rgb(204, 176, 135);
                                             }"""
        self.last_quest = 1
        self.setup_ui()
        self.type_func = {'Перестановка': permutation, 'Шифр Цезаря': ceasar, 'Шифр Виженера': new_encode_vijn,
                          'Гаммирование': gamma, 'Шифр Плейфера': pleifer, 'Квадрат Полибия': polybius_square}
        self.task_choice = 'расшифровать'
        self.table_var_flag = False
        self.crypto_method = ' '
        self.cypher_flag = False
        self.shutdown = False


def button_style(font_size=16):
    s = r"""QPushButton {
                             border: 2px;
                             border-radius: 6px;
                             background-color: rgb(120, 165, 163);
                             min-width: 80px;
                            font: """
    s += str(font_size) + """pt "Tahoma";
                         }
                        
                         QPushButton:hover {
                             background-color: rgb(104, 143, 141);
                         }"""
    return s


def frame_style():
    s = """QFrame {
                 border: 2px;
                 border-radius: 12px;
                 background-color: rgb(239, 210, 172);
             }"""

    return s


def text_style():
    s = """background-color: rgb(248, 218, 179); font: 12pt;"""
    return s


def frame_input_style():
    s = """background-color: rgb(239, 210, 172);"""
    return s


def input_style():
    s = """background-color: rgb(248, 218, 179);"""
    return s


app = QtWidgets.QApplication([])
application = App()
application.show()
# server_thread = Thread(target=application.server.start)
# server_thread.start()
sys.exit(app.exec())
