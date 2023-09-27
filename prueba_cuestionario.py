import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QRadioButton, QPushButton, QButtonGroup

class QuestionnaireApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cuestionario')
        self.current_question = 0
        self.questions = [
            {
                "question": "Pregunta 1: ¿Pregunta 1?",
                "options": ["Opción 1", "Opción 2", "Opción 3"]
            },
            {
                "question": "Pregunta 2: ¿Pregunta 2?",
                "options": ["Opción A", "Opción B", "Opción C"]
            },
            {
                "question": "Pregunta 3: ¿Pregunta 3?",
                "options": ["Sí", "No"]
            }
        ]
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.question_label = QLabel()
        self.layout.addWidget(self.question_label)

        self.option_group = QButtonGroup()

        self.option_buttons = []
        for option in self.questions[self.current_question]["options"]:
            button = QRadioButton(option)
            self.layout.addWidget(button)
            self.option_group.addButton(button)
            self.option_buttons.append(button)

        self.next_button = QPushButton("Siguiente")
        self.next_button.clicked.connect(self.show_next_question)
        self.layout.addWidget(self.next_button)

        self.setLayout(self.layout)
        self.update_question()

    def update_question(self):
        question_data = self.questions[self.current_question]
        self.question_label.setText(question_data["question"])

        options = question_data["options"]
        for i in range(len(options)):
            self.option_buttons[i].setText(options[i])
            self.option_buttons[i].setChecked(False)

    def show_next_question(self):
        self.current_question += 1
        if self.current_question < len(self.questions):
            self.update_question()
        else:
            self.question_label.setText("Cuestionario completado.")
            self.next_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QuestionnaireApp()
    window.show()
    sys.exit(app.exec_())
