import pickle

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMessageBox, QApplication, QPushButton, QSizePolicy, QLabel, QLineEdit, QVBoxLayout
from PyQt5.QtCore import Qt
from Sockets import Client
from threading import Thread
import sys
import numpy as np


class Player(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.client = Client()
        self.server_ip = '127.0.0.1'
        self.marks = 0
        self.end = False
        self.final = False
        self.answers = []
        self.functions = [self.key0, self.key1]
        self.player_answers = []
        self.date = np.datetime64('today')
        self.fill_hello_page()

    def key0(self, message):
        self.stacked_widget.setCurrentIndex(2)
        self.game_var = message
        self.last_index = 1
        self.label.setText('Вопрос ' + str(self.last_index) + ' из ' + str(len(self.game_var)))
        self.text_browser.append(self.set_text(str(self.last_index)))
        self.last_index += 1

    def key1(self, message):
        if message:
            self.show_correct_btn.setHidden(False)

    def fill_hello_page(self):
        # Общие настройки
        self.setObjectName("MainWindow")
        self.setFixedSize(1200, 800)
        self.setStyleSheet('background-color: rgb(221, 188, 149); font: 10pt Tahoma')
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.stacked_widget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stacked_widget.setGeometry(QtCore.QRect(0, 0, 1200, 800))
        self.stacked_widget.setObjectName("stacked_widget")

        # Окна
        self.connection_page = QtWidgets.QWidget()
        self.connection_page.setObjectName("connection_page")

        # Надпись ФИО
        self.name_label = QLabel(self.connection_page)
        self.name_label.setGeometry(QtCore.QRect(450, 200, 300, 30))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setObjectName("name_label")
        self.name_label.setText("Введите ФИО:")

        # Поле ввода ФИО
        self.name_line_edit = QLineEdit(self.connection_page)
        self.name_line_edit.setStyleSheet('background-color: rgb(248, 218, 179)')
        self.name_line_edit.setGeometry(QtCore.QRect(450, 250, 300, 30))
        self.name_line_edit.setObjectName("name_line_edit")
        self.name_line_edit.setStyleSheet("background: white;")

        # Надпись ip сервера
        self.connection_label = QLabel(self.connection_page)
        self.connection_label.setGeometry(QtCore.QRect(450, 320, 300, 30))
        self.connection_label.setAlignment(Qt.AlignCenter)
        self.connection_label.setObjectName("connection_label")
        self.connection_label.setText("Введите ip сервера:")

        # Поле ввода ip
        self.connection_line_edit = QLineEdit(self.connection_page)
        self.connection_line_edit.setStyleSheet('background-color: rgb(248, 218, 179)')
        self.connection_line_edit.setGeometry(QtCore.QRect(450, 370, 300, 30))
        self.connection_line_edit.setObjectName("connection_line_edit")
        self.connection_line_edit.setStyleSheet("background: white;")

        # Кнопка подключиться
        self.connect_btn = QPushButton(self.connection_page)
        self.connect_btn.setGeometry(QtCore.QRect(500, 460, 200, 50))
        self.connect_btn.setObjectName("connect_btn")
        self.connect_btn.setText("Подключиться")
        self.connect_btn.clicked.connect(self.connect_btn_click)
        self.connect_btn.setStyleSheet(button_style())

        self.wait_page = QtWidgets.QWidget()
        self.wait_page.setObjectName("wait_page")

        self.wait_label = QtWidgets.QLabel(self.wait_page)
        self.wait_label.setText('Ожидайте')
        self.wait_label.setStyleSheet('font: 46pt Tahoma')
        self.wait_label.setAlignment(Qt.AlignCenter)
        self.wait_label.setGeometry(QtCore.QRect(350, 370, 500, 80))
        self.wait_label.setObjectName("wait_label")

        self.quest_page = QtWidgets.QWidget()
        self.quest_page.setObjectName("quest_page")

        self.label = QtWidgets.QLabel(self.quest_page)
        # self.label.setText('Вопрос 1 из ' + str(len(self.game_var)))
        self.label.setGeometry(QtCore.QRect(540, 70, 120, 30))
        self.label.setObjectName("label")

        self.text_browser = QtWidgets.QTextBrowser(self.quest_page)
        # self.text_browser.setText(self.set_text('1'))
        self.text_browser.setStyleSheet(text_style())
        self.text_browser.setGeometry(QtCore.QRect(50, 180, 500, 150))
        self.text_browser.setObjectName("text_browser")

        self.text_edit = QtWidgets.QTextEdit(self.quest_page)
        self.text_edit.setPlaceholderText('Введите ответ...')
        self.text_edit.setStyleSheet(text_style())
        self.text_edit.setGeometry(QtCore.QRect(650, 180, 500, 150))
        self.text_edit.setObjectName("text_edit")

        self.next_btn = QtWidgets.QPushButton(self.quest_page)
        self.next_btn.setStyleSheet(button_style(font_size=12))
        self.next_btn.clicked.connect(self.next_quest_func)
        self.next_btn.setText('Далее')
        self.next_btn.setGeometry(QtCore.QRect(530, 610, 140, 50))
        self.next_btn.setObjectName("next_btn")

        self.result_page = QtWidgets.QWidget()
        self.result_page.setObjectName("result_page")

        self.result_label = QtWidgets.QLabel(self.result_page)
        self.result_label.setStyleSheet('font: 32pt Tahoma')
        self.result_label.setAlignment(Qt.AlignCenter)
        # self.result_label.setText('{}, вы набрали {} баллов.'.format(self.name, self.marks))
        self.result_label.setGeometry(QtCore.QRect(200, 250, 800, 150))
        self.result_label.setObjectName("result_label")

        self.show_correct_btn = QtWidgets.QPushButton(self.result_page)
        self.show_correct_btn.setStyleSheet(button_style(font_size=12))
        self.show_correct_btn.clicked.connect(self.show_correct_func)
        self.show_correct_btn.setText('Посмотреть ответы')
        self.show_correct_btn.setGeometry(QtCore.QRect(470, 500, 260, 50))
        self.show_correct_btn.setHidden(True)

        self.show_correct_page = QtWidgets.QWidget()
        self.answers_frame = QtWidgets.QFrame(self.show_correct_page)

        self.stacked_widget.addWidget(self.connection_page)
        self.stacked_widget.addWidget(self.wait_page)
        self.stacked_widget.addWidget(self.quest_page)
        self.stacked_widget.addWidget(self.result_page)
        self.stacked_widget.addWidget(self.show_correct_page)
        self.setCentralWidget(self.centralwidget)
        self.stacked_widget.setCurrentIndex(0)

    def show_correct_func(self):
        height = min(len(self.game_var) * 40 + 70, 640)
        self.answers_frame.setGeometry(QtCore.QRect(10, 100, 1180, height))
        self.answers_frame.setStyleSheet(frame_style())
        self.table_answers = QtWidgets.QTableWidget(self.answers_frame)
        self.table_answers.setStyleSheet('background-color: white')
        height = min(len(self.game_var) * 40 + 30, 600)
        self.table_answers.setGeometry(QtCore.QRect(20, 20, 1140, height))
        self.table_answers.setColumnCount(7)
        self.table_answers.setRowCount(len(self.game_var))
        self.table_answers.setHorizontalHeaderLabels(
            ['Номер вопроса', 'Метод шифрования', 'Исходный текст', 'Ваш ответ', 'Правильный ответ', 'Ключ', 'Задание'])

        for i in range(7):
            self.table_answers.horizontalHeaderItem(i).setTextAlignment(Qt.AlignLeft)
            if i == 0:
                w = 60
            elif i == 1:
                w = 160
            elif i in [5, 6]:
                w = 150
            else:
                w = 200
            self.table_answers.setColumnWidth(i, w)
        for i in range(len(self.game_var)):
            info = self.game_var[str(i + 1)]
            if info[4] == 'зашифровать':
                text = info[1]
                correct = info[2]
            else:
                text = info[2]
                correct = info[1]
            self.table_answers.setItem(i, 0, QtWidgets.QTableWidgetItem(str(i + 1)))
            self.table_answers.setItem(i, 1, QtWidgets.QTableWidgetItem(info[0]))
            self.table_answers.setItem(i, 2, QtWidgets.QTableWidgetItem(text))
            self.table_answers.setItem(i, 3, QtWidgets.QTableWidgetItem(self.answers[i]))
            self.table_answers.setItem(i, 4, QtWidgets.QTableWidgetItem(correct))
            self.table_answers.setItem(i, 5, QtWidgets.QTableWidgetItem(info[3]))
            self.table_answers.setItem(i, 6, QtWidgets.QTableWidgetItem(info[4]))
        self.table_answers.resizeRowsToContents()
        self.stacked_widget.setCurrentIndex(4)

    def fill_game_page(self):
        pass

    def set_text(self, index):
        self.method = self.game_var[index][0]
        text = self.game_var[index][1]
        crypto_text = self.game_var[index][2]
        key = self.game_var[index][3]
        self.task = self.game_var[index][4]

        if self.task == 'зашифровать':
            result_text = 'Метод шифрования: {}.\nВам необходимо {} следующий текст:\n{}\nКлюч: {}'.format(self.method, self.task, text, key)
        else:
            result_text = 'Метод шифрования: {}.\nВам необходимо {} следующий текст:\n{}\nКлюч: {}'.format(self.method, self.task, crypto_text, key)
        return result_text

    def next_quest_func(self):
        self.send_server()
        if self.last_index - 1 == len(self.game_var):
            self.end = True
            self.send_server()
            self.result_label.setText('{}, \nВы набрали {} из {}.'.format(self.player_name, self.marks, len(self.game_var)))
            self.stacked_widget.setCurrentIndex(3)
        else:
            self.label.setText('Вопрос ' + str(self.last_index) + ' из ' + str(len(self.game_var)))
            self.text_edit.clear()
            self.text_browser.setText(self.set_text(str(self.last_index)))
            self.last_index += 1

    def listen_server(self):
        while True:
            data = self.client.socket.recv(2048)
            data = pickle.loads(data)
            self.functions[data['Key']](data['Message'])

    def send_server(self):
        if self.end:
            data = {'Key': 2, 'Message': [self.player_answers]}
        else:
            player_answer = self.text_edit.toPlainText()
            self.answers.append(player_answer)
            if self.task == 'зашифровать':
                correct = int(player_answer == self.game_var[str(self.last_index - 1)][2])
            else:
                correct = int(player_answer == self.game_var[str(self.last_index - 1)][1])
            self.marks += correct
            self.player_answers.append({'ФИО': self.player_name, 'Дата': self.date, 'Метод': self.method, 'Правильно': correct})
            data = {'Key': 1, 'Message': [self.player_name, correct]}
        data = pickle.dumps(data)
        self.client.socket.send(data)

    def connect_btn_click(self):
        try:
            self.server_ip = self.connection_line_edit.text()
            self.client.socket.connect((self.server_ip, 1234))
            self.client.socket.settimeout(None)
            self.player_name = self.name_line_edit.text()
            data = {'Key': 0, 'Message': self.player_name}
            data = pickle.dumps(data)
            self.client.socket.send(data)
            listen_thread = Thread(target=self.listen_server)
            listen_thread.start()
            self.stacked_widget.setCurrentIndex(1)
        except:
            alert = QMessageBox()
            alert.setText('Ошибка подключения к серверу!')
            alert.exec_()


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
    s = """border: 2px; border-radius: 8px; background-color: rgb(248, 218, 179); font: 12pt;"""
    return s


def frame_input_style():
    s = """background-color: rgb(239, 210, 172);"""
    return s


app = QtWidgets.QApplication(sys.argv)
player = Player()
player.show()
sys.exit(app.exec_())
