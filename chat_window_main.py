import sys

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QScrollArea, QFrame
from PyQt5.QtCore import pyqtSignal, QTimer, Qt, QRectF, QPoint
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QFont

class CodeWriterWindow(QWidget):
    button_press = pyqtSignal(str)
    return_press = pyqtSignal(str)

    def __init__(self):
        super(CodeWriterWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.main_color=QColor('#3b3b3e')
        self.backgroundColor =  self.main_color
        self.borderColor =  self.main_color
        self.window_size = (1120,1244)
        self.cornerRadius =  20
        self.borderWidth =  2
        self.window_title = ''
        self.initUI()
        print('- class init main window')
        self.input_box.setText('Hi! Please make a cool simple plot in python')
        self.input_box.setFocus()

    def initUI(self):
            self.init_style_sheets()
            self.setWindowTitle(self.window_title)
            self.setGeometry(200,120,*self.window_size)

            self.main_vbox = QVBoxLayout()
            self.main_vbox.setContentsMargins(16, 16, 16, 16)
            self.main_vbox.setSpacing(15)
     
            self.top_button_box = self.make_button_box(['code', 'chat', 'debug'])
            self.main_vbox.addLayout(self.top_button_box)
    
            self.scroll_area = self.create_scroll_area()
            self.main_vbox.addWidget(self.scroll_area)
                   
            self.input_box = self.make_input()
            self.main_vbox.addWidget(self.input_box)
                 
            self.bottom_button_box = self.make_button_box(['exit', 'stop'])
            self.main_vbox.addLayout(self.bottom_button_box)

            self.setLayout(self.main_vbox)

    def make_input(self):
        input_box = QLineEdit()
        input_box.setFont(self.main_font)
        input_box.setStyleSheet(self.input_style)
        input_box.returnPressed.connect(self.handle_return)
        return input_box

    def create_scroll_area(self):
        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        scroll_widget.setStyleSheet(self.background_style)
        self.scroll_layout.setAlignment(Qt.AlignBottom)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setWidget(scroll_widget)
        return scroll_area

    def make_button_box(self, buttons):
        button_box = QHBoxLayout()
        for label in buttons:
            button = self.make_button(label)
            button_box.addWidget(button)
        return button_box
     
    def make_button(self, text):
        button = QPushButton(text)
        button.setFont(self.main_font)
        button.setStyleSheet(self.button_style)
        button.clicked.connect(lambda: self.handle_button(text))
        return button
    
    def add_message(self, message, color):
        print(f"adding message box: {message}")
        message_box = QLabel()
        message_box.clear()
        message_box.setText(message)
        message_box.setWordWrap(True)
        message_box.setTextFormat(Qt.PlainText)
        message_box.setFont(self.main_font)
        self.current_message = message_box
        message_box.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.scroll_layout.addWidget(message_box)
        self.scrollbar = self.scroll_area.verticalScrollBar()
        message_box.setStyleSheet(self.message_style)
        message_box.setStyleSheet(f'background-color: {color};')
        timer = QTimer(self)
        timer.singleShot(20, lambda: self.scrollbar.setValue(self.scrollbar.maximum()+30))

    def set_message_text(self, text):
        self.current_message.setText(text)

    def reset_scrollbox(self):
        while self.scroll_layout.count():
            widget = self.scroll_layout.takeAt(0)
            if widget:
                widget.widget().deleteLater()

    def handle_button(self, text):
        self.button_press.emit(text)

    def handle_return(self):
        text = self.input_box.text()
        self.input_box.clear()
        self.return_press.emit(text)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()
        
    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.backgroundColor)

        rectPath = QPainterPath()
        rect = QRectF(0, 0, self.width(), self.height())
        rectPath.addRoundedRect(rect, self.cornerRadius, self.cornerRadius)
        painter.drawPath(rectPath)

        painter.setPen(self.borderColor)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(rectPath)
    
    def init_style_sheets(self):
        self.main_font = QFont("Cascadia Code Extralight", 15)
        self.input_style="color: white; background-color: #505052; border-radius: 10px; padding: 12px 10px;"
        self.message_style="color: white; background-color: #303034; border-radius: 10px; padding: 8px 12px;"
        self.background_style="color: white; background-color: #3b3b3b; border-radius: 10px; padding: 8px 10px;"
        self.button_style="QPushButton {background-color: #4e4e50; color: white; border-radius: 10px; padding: 5px 15px;} QPushButton:hover {background-color: #5b5b5e;}"

if __name__=="__main__":
    app = QApplication(sys.argv)
    obj = CodeWriterWindow()
    obj.show()
    sys.exit(app.exec_())
