from PyQt5 import QtGui
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from simple_salesforce import SalesforceAuthenticationFailed
from MyReadFile import read_string_to_array
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from CreateFCAndClarification import *
from Utilities import *
from UpdateSFCaseLanguage_with_UI_v1 import *
from MyReadFile import get_config

# v2.2 change log:
    # Removed Save Assessment as it causes the case owner change to Admin Queue

# v2.1 change log:
    # Removed Change Case Status logic(It won't change to Working status anymore), we see change case status under some conditions would casue the case to be reassigned to Admin Queue. So removed it and now the case status will remain unchanged after running the Execute

# v2.0 change log:
# Major changes:
    # Combined FC page and Language page into one UI
    # Added update_assessment, the FC script now would 1) Save assessment 2) Create FC 3) Update Clarification, case status, closure details
    # script now skips the case if the case already have FC task created
    # script now start in separate thread so the main UI does not get freeze
    # the FC Execute button is disabled when user click and re-enabled when task is completed to avoid user click multi times

# Minor changes:
    # Log print format added timestamp
    # When wrong credentials provided in config.json, then error is captured and shown

# Load the GUI from the .ui file
Ui_MainWindow, QMainWindow = loadUiType("sfgui_v2.ui")


class Worker(QObject):
    # define signals:
    finished = pyqtSignal()
    finished_update_lang = pyqtSignal()
    console_updated = pyqtSignal(str, str)
    console_lang_updated = pyqtSignal(str, str)

    def __init__(self, sf, fctemplate=None, caselist=None, target_lang=None, caselist_lang=None, parent=None):
        super(Worker, self).__init__(parent)
        self.fctemplate = fctemplate
        self.caselist = caselist
        self.target_lang = target_lang
        self.caselist_lang = caselist_lang
        self.sf = sf

    # Do FC and update Clarification
    def run_script(self):
        def execute_script():
            # recordtypeid '012A0000000Vg0PIAS' is 'Technical Support'
            if get_case_recordtype(sf, case_number) == '012A0000000Vg0PIAS':
                try:
                    # 1) get the case info for this case_number first
                    case_info = get_case_info(sf, case_number)
                    # 2) update assessment to True
                    # Adding assessment causing the New case to be reassigned to Admin Queue, remove this to see if issue resolves
                    # update_case_assessment(sf, case_number, case_info)
                    # self.console_updated.emit('log',
                    #                           f'[{get_time_for_logging()}] Successfully updated assessment for C{case_number}')
                    # time.sleep(0.5)
                    # 3) Create FC
                    create_fc(sf, case_number, fc_template)
                    self.console_updated.emit('log',
                                              f'[{get_time_for_logging()}] Successfully Created First Contact Task for C{case_number}')
                    time.sleep(0.5)
                    # 4) Update Clarification
                    update_case_clarification(sf, case_number, case_info)
                    self.console_updated.emit('log',
                                              f'[{get_time_for_logging()}] Successfully updated Clarification for C{case_number}')
                except Exception as e:
                    print(
                        f"[{get_time_for_logging()}] An Error occurred while creating first contact task or updating Case Clarification for C{case_number}: {e}")
                    self.console_updated.emit('log',
                                              f'[{get_time_for_logging()}] An Error occurred while creating first contact task or updating Case Clarification for C{case_number}: {e}')
            else:
                print(
                    f"[{get_time_for_logging()}] !!The case record type for C{case_number} is not Technical Support!! Update the Case Record Type to Technical Support for C{case_number} and try again")
                self.console_updated.emit('log',
                                          f'[{get_time_for_logging()}] !!The case record type for C{case_number} is not Technical Support!! Update the Case Record Type to Technical Support for C{case_number} and try again')

        # Open the JSON file for reading
        with open('config.json', 'r') as f:
            # Load the JSON data into a Python dictionary
            data = json.load(f)
        if len(data) == 0:
            self.console_updated.emit('log', f'[{get_time_for_logging()}] !!config.json is blank')
            raise ValueError('!!config.json is blank')
        sf = self.sf
        # Execute function
        fc_template = self.fctemplate.toPlainText()
        case_number_array = read_string_to_array(self.caselist.toPlainText())
        if len(case_number_array) == 0:
            self.console_updated.emit('log',
                '!!Case # is blank, Add Case # under case: as xxxxxxxx without C prefix, E.g: 12345678')
            # raise ValueError(
            #     '!!Case # is blank, Add Case # under case: as xxxxxxxx without C prefix, E.g: 12345678')
        else:
            for case_number in case_number_array:
                # 1) get the case info for this case_number first
                case_info = get_case_info(sf, case_number)
                # if enableMultiFC is 1 in config.json, means if allow multi fc for a case
                enableMultiFC = get_config("config.json", "enableMultiFC")
                if enableMultiFC == 1:
                    # if allow multi fc
                    execute_script()
                # if not allow multi fc
                else:
                    # if fc is not made yet:
                    if not is_fc_made(sf, case_info):
                        execute_script()
                    # if fc is already made
                    else:
                        self.console_updated.emit('log',
                                                  f'[{get_time_for_logging()}] First Contact is already made for C{case_number}, skip this case...')
        # Emit a signal to indicate that the function has finished
        self.finished.emit()

    def update_case_lang_script(self):
        # Open the JSON file for reading
        with open('config.json', 'r') as f:
            # Load the JSON data into a Python dictionary
            data = json.load(f)
        if len(data) == 0:
            self.console_lang_updated.emit('log_lang', f'[{get_time_for_logging()}] !!config.json is blank')
            raise ValueError('!!config.json is blank')
        # create a Salesforce object
        sf = Salesforce(username=data["username"],
                        password=data["password"],
                        security_token=data["security_token"])

        # Execute update language function
        target_lang = self.target_lang.currentText()
        # if the target_lang is not blank
        if not is_blank_str(target_lang):
            case_number_array = read_string_to_array(self.caselist_lang.toPlainText())
            if len(case_number_array) == 0:
                self.console_lang_updated.emit('log_lang',
                    '!!Case # is blank, Add Case # under case: as xxxxxxxx without C prefix, E.g: 12345678')
                # raise ValueError(
                #     '!!Case # is blank, Add Case # under "case:" as xxxxxxxx without C prefix, E.g: 12345678')
            else:
                for case_number in case_number_array:
                    try:
                        # 1) get the case info for this case_number first
                        case_info = get_case_info(sf, case_number)
                        case_language_orig = case_info["Language__c"]
                        # 2) update case language
                        update_case_lang(sf, case_number, case_info, target_lang)
                        self.console_lang_updated.emit('log_lang',
                            f'[{get_time_for_logging()}] Successfully updated C{case_number} Language from "{case_language_orig}" to "{target_lang}"')
                    except Exception as e:
                        print(
                            f"[{get_time_for_logging()}] An Error occurred while updating Case Language for C{case_number}: {e}")
                        self.console_lang_updated.emit('log_lang',
                            f'[{get_time_for_logging()}] An Error occurred while updating Case Language for C{case_number}: {e}')
        else:
            print("!!Please select a Target Language!!")
            self.console_lang_updated.emit('log_lang',
                f'[{get_time_for_logging()}] !!Please select a Target Language!!')
        # Emit a signal to indicate that the function has finished
        self.finished_update_lang.emit()


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, sf):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.sf = sf

        # define console prop as the UI log
        self.console = self.log
        self.console_lang = self.log_lang
        # set template value to fctemplate widget
        self.fctemplate.setPlainText(
            "We received your question and will start to look into it, thank you.\n\nMedia: Email\n\nNext Step: I will search for the knowledge base.\n\nBusiness Impact: Not get this time.")
        # Pages
        # Page 1 - fc
        self.btn_fc.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_fc))
        # Connect the executeButton to the start_script method
        self.executeButton.clicked.connect(self.start_script)
        # Page 2 - language update
        self.btn_lang.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_lang))
        self.btn_update_lang.clicked.connect(self.start_update_case_lang_script)

    # Write log to UI
    def write_console(self, ui_logger, text):
        text = "\n" + text
        cursor = getattr(self, ui_logger).textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        getattr(self, ui_logger).setTextCursor(cursor)
        getattr(self, ui_logger).ensureCursorVisible()

    # Write log to UI
    def write_console_orig(self, text):
        text = "\n" + text
        cursor = self.console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()

    # start script in a new thread
    def start_script(self):
        # Disable the execute button before starting the script to avoid multi-click by mistake
        self.executeButton.setEnabled(False)

        # Create a worker instance and move it to a new thread
        self.worker = Worker(sf=self.sf, fctemplate=self.fctemplate, caselist=self.caselist)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        # Connect signals to slots
        self.worker.finished.connect(self.thread.quit)
        # self.worker.console_updated.connect(lambda text: self.write_console(text))
        self.worker.console_updated.connect(lambda ui_logger, text: self.write_console(ui_logger, text))
        self.thread.started.connect(self.worker.run_script)

        # Start the thread
        self.thread.start()

        # Define callback function for message box
        def show_message_box():
            QMessageBox.information(self, "Success", "Execution successful!")
            # Enable the executeButton after the message box is closed
            self.executeButton.setEnabled(True)

        # Call the show_message_box function after the thread has finished executing
        self.thread.finished.connect(show_message_box)

    # start update language script in a new thread
    def start_update_case_lang_script(self):
        # Disable the execute button before starting the script to avoid multi-click by mistake
        self.btn_update_lang.setEnabled(False)

        # Create a worker instance and move it to a new thread
        self.worker_lang = Worker(sf=self.sf, target_lang=self.combo_target_lang, caselist_lang=self.caselist_lang)
        self.thread_lang = QThread()
        self.worker_lang.moveToThread(self.thread_lang)

        # Connect signals to slots
        self.worker_lang.finished_update_lang.connect(self.thread_lang.quit)
        self.worker_lang.console_lang_updated.connect(lambda ui_logger, text: self.write_console(ui_logger, text))
        self.thread_lang.started.connect(self.worker_lang.update_case_lang_script)

        # Start the thread
        self.thread_lang.start()

        # Define callback function for message box
        def show_message_box():
            QMessageBox.information(self, "Success", "Execution successful!")
            # Enable the executeButton after the message box is closed
            self.btn_update_lang.setEnabled(True)

        # Call the show_message_box function after the thread has finished executing
        self.thread_lang.finished.connect(show_message_box)


if __name__ == '__main__':
    try:
        # Open the JSON file for reading
        with open('config.json', 'r') as f:
            # Load the JSON data into a Python dictionary
            data = json.load(f)
        if len(data) == 0:
            raise ValueError('!!config.json is blank')
        sf = Salesforce(username=data["username"],
                        password=data["password"],
                        security_token=data["security_token"])
    except SalesforceAuthenticationFailed as e1:
        print(f'Authentication failed. Please check your credentials in config.json file!!\n'
              f'If you have changed your salesforce password, please reset your Security Token also and update the config.json file.\n'
              f'exception: {e1}')
        raise
    except Exception as e:
        print(f'Unkown error occurred while login sf, if your credentials are correct, then try again to resolve... {e}')
        raise
    app = QApplication([])
    window = MyWindow(sf)
    window.show()
    app.exec_()
