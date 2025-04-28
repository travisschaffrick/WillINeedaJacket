from PyQt6.QtWidgets import QApplication
import ui

if __name__ == '__main__':
    app = QApplication([])
    myApp = ui.MyApp()
    app.exec()
    output = myApp.controller.get_output()
    print(output)
    file = open('logs.txt', 'w')
    file.writelines(output)
    file.close()
