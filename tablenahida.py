import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QDialog, \
    QTextBrowser, QMessageBox, QComboBox
from PyQt5.QtGui import QMovie, QCursor, QPixmap
from PyQt5.QtCore import Qt, QRect
from llm import run_conversation


class MessageManager:
    def __init__(self, max_tokens=14000):
        self.messages = [{'role': 'system', 'content': 'I am your assistant'}]
        self.max_tokens = max_tokens
        self.current_model = "gpt-3.5-turbo"

    def add_message(self, message):
        self.messages.append(message)
        self.trim_messages()

    def trim_messages(self):
        total_tokens = sum(len(msg['content']) for msg in self.messages)
        while total_tokens > self.max_tokens:
            self.messages.pop(1)  # 删除从前往后第二条消息
            total_tokens = sum(len(msg['content']) for msg in self.messages)

    def get_messages(self):
        return self.messages

    def set_model(self, model):
        self.current_model = model

class Dialog(QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.setWindowTitle('Chat Dialog')

        self.layout = QVBoxLayout(self)

        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("Enter your message")
        self.input_text.returnPressed.connect(self.get_input)
        self.layout.addWidget(self.input_text)

        self.output_text = QTextBrowser()
        self.layout.addWidget(self.output_text)

        self.message_manager = MessageManager()

    def get_input(self):
        try:
            input_text = self.input_text.text().strip()
            self.message_manager.add_message({'role': 'user', 'content': input_text})

            # Add user input to the dialog box
            self.output_text.append("User: " + input_text)

            messages = self.message_manager.get_messages()
            print(f"Sending messages to run_conversation: {messages}")
            response = run_conversation(messages, model=self.message_manager.current_model)
            self.message_manager.add_message({'role': 'assistant', 'content': response})
            self.output_text.append("Assistant: " + response)
            print("Assistant response:", response)  # 打印模型返回的内容

            self.input_text.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

class SettingsDialog(QDialog):
    def __init__(self, message_manager, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle('Settings')

        self.layout = QVBoxLayout(self)

        self.model_selector = QComboBox()
        self.model_selector.addItems(["gpt-3.5-turbo", "gpt-4-0613", "claude-3-haiku-20240307", "gemini-pro"])
        self.model_selector.currentTextChanged.connect(self.update_model)
        self.layout.addWidget(self.model_selector)

        self.message_manager = message_manager

    def update_model(self, model):
        self.message_manager.set_model(model)

class PetWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Desktop Pet")
        self.setFixedSize(400, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.pet_label = QLabel(self)
        self.pet_label.setGeometry(QRect(0, 0, 400, 400))
        layout.addWidget(self.pet_label)

        self.chat_icon = QLabel(self)
        self.chat_icon.setGeometry(QRect(300, 280, 96, 96))
        self.chat_icon.setPixmap(QMessageBox.standardIcon(QMessageBox.Information))
        self.chat_icon.mousePressEvent = self.dialog_mousePressEvent

        self.settings_icon = QLabel(self)
        self.settings_icon.setGeometry(QRect(300, 180, 96, 96))
        self.settings_icon.setPixmap(QMessageBox.standardIcon(QMessageBox.Information))
        self.settings_icon.mousePressEvent = self.settings_mousePressEvent

        self.setCentralWidget(central_widget)

        self.gif_map = {
            "sad": "sad.gif",
            "happy": "happy.gif",
            "angry": "angry.gif",
            "normal": "normal.gif"
        }

        self.current_gif = "normal.gif"
        self.show_gif(os.path.join("./", self.current_gif))

        self.is_dragging = False
        self.drag_position = self.pos()

        self.dialog = Dialog(self)
        self.settings_dialog = SettingsDialog(self.dialog.message_manager, self)

    def dialog_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.dialog.isHidden():
                self.dialog.show()
            else:
                self.dialog.hide()

    def settings_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.settings_dialog.isHidden():
                self.settings_dialog.show()
            else:
                self.settings_dialog.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, event):
        if not self.is_dragging:
            return
        self.move(event.globalPos() - self.drag_position)
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.setCursor(QCursor(Qt.ArrowCursor))

    def show_gif(self, gif_path):
        self.movie = QMovie(gif_path)
        self.pet_label.setMovie(self.movie)
        self.movie.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PetWindow()
    window.show()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(window, "Error", f"An error occurred: {str(e)}")
        window.show()
