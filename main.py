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


# v2.3 change log:
    # Format the closure detail date format to align with the SF "Add Status" format
      # After: [23 Jan 25] for 2025/01/23
      # Before: [2025-Jan-23] for 2025/01/23
    # rewrite the function read_string_to_array to handle when the case number starts with C or c

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
Ui_MainWindow, QMainWindow = loadUiType("sfgui_v3.ui")

# This class defines the actual logic to run the tasks
class Worker(QObject):
    # define signals:
    # signal emitted when FC task is completed
    finished = pyqtSignal()
    # signal emitted when language update task is completed
    finished_update_lang = pyqtSignal()
    # v3.0 added signal for "Article Prompt for AAA" page
    # signal when article prompt generation task is completed
    finished_prompt = pyqtSignal()

    # signals for logging
    # signal for FC logging
    console_updated = pyqtSignal(str, str)
    # signal for Case Language logging
    console_lang_updated = pyqtSignal(str, str)
    # V3.0 Added:
    # signal for poping up error window when provided case is invalid
    # e.g., didn't provide any case, provided invalid case or provided more than 1 case a time
    # In prompt generation feature, we only support to provide 1 case a time
    error_prompt = pyqtSignal(str)
    # signal for generating output prompt
    output_prompt = pyqtSignal(str)

    def __init__(self, sf, fctemplate=None, caselist=None, target_lang=None, caselist_lang=None, caselist_prompt=None, parent=None):
        super(Worker, self).__init__(parent)
        self.fctemplate = fctemplate
        self.caselist = caselist
        self.target_lang = target_lang
        self.caselist_lang = caselist_lang
        self.sf = sf
        # V3.0 Initialize Case List in Prompt window
        self.caselist_prompt = caselist_prompt

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

        # V3.0 No need to open the file here as it is already opened outside, try delete later and test
        # Open the JSON file for reading
        # with open('config.json', 'r') as f:
        #     # Load the JSON data into a Python dictionary
        #     data = json.load(f)
        # if len(data) == 0:
        #     self.console_updated.emit('log', f'[{get_time_for_logging()}] !!config.json is blank')
        #     raise ValueError('!!config.json is blank')
        sf = self.sf
        # Execute function
        fc_template = self.fctemplate.toPlainText()
        case_number_array = read_string_to_array(self.caselist.toPlainText())
        if len(case_number_array) == 0:
            self.console_updated.emit('log',
                f'[{get_time_for_logging()}] !!Case # is blank, Add Case # under Case: as xxxxxxxx, E.g: 12345678 or C12345678')
            self.error_prompt.emit(f"!!Case # is blank, Add Case # under Case: as xxxxxxxx, E.g: 12345678 or C12345678")
        else:
            for case_number in case_number_array:
                # V3.0 try catch to handle situation that user provide a non-existing case number
                try:
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
                # Wrong case number provided
                except ValueError as e1:
                    print(f"Exception while executing the task: {e1}")
                    self.console_updated.emit('log',
                                              f'[{get_time_for_logging()}] Exception while executing the task for C{case_number}: {e1}')
                    self.error_prompt.emit(f"Exception while executing the task for C{case_number}: {e1}")
                # Other exceptions
                except Exception as e:
                    print(f"Exception while executing the task: {e}")
                    self.console_updated.emit('log',
                                              f'[{get_time_for_logging()}] Exception while executing the task for C{case_number}: {e}')
                    self.error_prompt.emit(
                        f"Exception while executing the task for C{case_number}: {e}")

        # Emit a signal to indicate that the function has finished
        self.finished.emit()

    # Do Case Language Update
    def update_case_lang_script(self):
        # V3.0 No need to open the file here as it is already opened outside, try delete later and test
        # Open the JSON file for reading
        # with open('config.json', 'r') as f:
        #     # Load the JSON data into a Python dictionary
        #     data = json.load(f)
        # if len(data) == 0:
        #     self.console_lang_updated.emit('log_lang', f'[{get_time_for_logging()}] !!config.json is blank')
        #     raise ValueError('!!config.json is blank')
        sf = self.sf

        # Execute update language function
        target_lang = self.target_lang.currentText()
        # if the target_lang is not blank
        if not is_blank_str(target_lang):
            case_number_array = read_string_to_array(self.caselist_lang.toPlainText())
            if len(case_number_array) == 0:
                self.console_lang_updated.emit('log_lang',
                    f'[{get_time_for_logging()}] !!Case # is blank, Add Case # under Case: as xxxxxxxx or Cxxxxxxxx, E.g: 12345678')
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
                    # V3.0 Wrong case number provided
                    except ValueError as e1:
                        print(f"Exception while executing the task: {e1}")
                        self.console_lang_updated.emit('log_lang',
                                                  f'[{get_time_for_logging()}] Exception while updating Case Language for C{case_number}: {e1}')
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

    # v3.0 Add function to support Article Prompt Generation feature
    # Do Article Prompt Generation
    def generate_article_prompt(self, b_include_case_comment=False):
        # salesforce object
        sf = self.sf
        # Execute generate article prompt function
        case_number_array = read_string_to_array(self.caselist_prompt.toPlainText())
        # Length of Case Number List
        case_num_length = len(case_number_array)
        # Run the logic to generate prompt
        if case_num_length == 1:
            case_number = case_number_array[0]
            try:
                # 1) get the case info for this case_number first
                case_info = get_case_info(sf, case_number)
                # 2） extract the required fields from the case_info
                # Get Case subject, clarification, closure details
                case_subject = case_info["LongSubject__c"] or "N/A"
                case_clarification_symptom = case_info["Symptoms__c"] or "N/A"
                case_clarification_steps_to_reproduce = case_info["Steps_to_Reproduce__c"] or "N/A"
                case_clarification_error = case_info["Error_s__c"] or "N/A"
                case_closure_details = case_info["Delivered_Solution__c"] or "N/A"
                # Get Case Product, Release, Date Code and the Last Email Communication
                product_info = get_product_info(sf, case_info["Product__c"])
                release_info = get_release_info(sf, case_info["Release__c"])
                date_code_info = get_date_code_info(sf, case_info["Date_Code__c"])
                last_email = get_last_email_content(sf, case_info["Id"])
                # 3) Build the prompt template
                # Example prompt:
                # Description:
                # Subject:
                # XXX in ThingWorx Platform 9.4 SP7
                # Symptom:
                # XXX
                # Error Message:
                # XXX
                # Steps to Reproduce:
                # XXX
                # Status Summarize:
                # XXX
                # (Optionally:) Case Comments:
                # XXX
                # Cause:
                # Email Communication History:
                # XXX
                prompt = f"Description:\n"
                prompt += (f"Subject:\n{case_subject} in {product_info} {release_info} {date_code_info}\n\n"
                          f"Symptom:\n{case_clarification_symptom}\n\n"
                          f"Error Message:\n{case_clarification_error}\n\n"
                          f"Steps to Reproduce:\n{case_clarification_steps_to_reproduce}\n\n"
                          f"Status Summarize:\n{case_closure_details}")
                # User selected Include Case Comment checkbox
                if b_include_case_comment:
                    case_comment = get_case_comments(sf, case_info["Id"])
                    # No Case Comment found
                    if case_comment == "N/A":
                        prompt += f"\n\nCase Comments:\n{case_comment}"
                    # There is Case Comments
                    else:
                        prompt += f"\n\nCase Comments:\n"
                        for record in case_comment:
                            prompt += f'{record["CreatedDate"]}: {record["CommentBody"]}\n'
                prompt += f"\n\nCause:"
                prompt += f"\n\nResolution:\n"
                prompt += f"Email Communication History:\n{last_email}"
                # Emit signal to generate output prompt
                self.output_prompt.emit(prompt)
            # Wrong case number provided
            except ValueError as e1:
                self.error_prompt.emit(f"Exception while executing the task: {e1}")
                print(f"Exception while executing the task: {e1}")
            except Exception as e:
                self.error_prompt.emit(f"An Error occurred while generating the article prompt for C{case_number}: {e}")
                print(
                    f"[{get_time_for_logging()}] An Error occurred while generating the article prompt for C{case_number}: {e}")
        # Didn't provide a case number
        elif case_num_length == 0:
            # Emit signal to popup error window
            self.error_prompt.emit("Case # is blank, Add Case # under Case: as xxxxxxxx E.g: 12345678 or C12345678")
            print('!!Case # is blank, Add Case # under Case: as xxxxxxxx E.g: 12345678 or C12345678')
        # Only support to handle 1 case a time
        else:
            # Emit signal to popup error window
            self.error_prompt.emit("!!Provide only 1 case a time")
            print('!!Provide only 1 case a time')
        # Emit a signal to indicate that the function has finished
        self.finished_prompt.emit()


# This class represents the UI, controls the workflow
# E.g., When clicking on a UI button, what occurs, etc
# It will create separate threads to run the actual code in the Worker class
class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, sf):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.sf = sf

        # V3.0 When display_error is called, skip the show_message_box, so defined a signal for that
        self.had_error = False
        # define console prop as the UI log widget
        self.console = self.log
        self.console_lang = self.log_lang
        # set template value to fctemplate widget
        self.fctemplate.setPlainText(
            "We received your question and will start to look into it, thank you.\n\nMedia: Email\n\nNext Step: I will search for the knowledge base.\n\nBusiness Impact: Not get this time.")
        # V3.0 define console prop for UI output_prompt widget
        self.console_output_prompt = self.output_prompt

        # Pages
        # Page 1 - fc
        self.btn_fc.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_fc))
        self.btn_fc_reset.clicked.connect(lambda: self.reset_window("fc"))
        # Connect the executeButton to the start_script method
        self.executeButton.clicked.connect(self.start_script)
        # Page 2 - language update
        self.btn_lang.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_lang))
        self.btn_update_lang.clicked.connect(self.start_update_case_lang_script)
        self.btn_lang_reset.clicked.connect(lambda: self.reset_window("lang"))
        # V3.0 Prompt Generation Feature
        # Page 3 - Prompt Generation
        self.btn_prompt.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_article_promp_generation))
        self.executeButton_prompt.clicked.connect(self.start_generate_article_prompt_script)
        self.btn_prompt_reset.clicked.connect(lambda: self.reset_window("prompt"))


    # Write log to UI - flexible via varabile ui_logger,  can log to any log section
    def write_console(self, ui_logger, text):
        text = "\n" + text
        cursor = getattr(self, ui_logger).textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        getattr(self, ui_logger).setTextCursor(cursor)
        getattr(self, ui_logger).ensureCursorVisible()

    # Deprecated
    # Write log to UI - fixed to fc log section
    def write_console_orig(self, text):
        text = "\n" + text
        cursor = self.console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()

    # V3.0 write prompt to the output_prompt UI widget
    def write_prompt(self, text):
        # self.console_output_prompt.clear()  # Clear all previous content
        # text = "\n" + text
        # cursor = self.console_output_prompt.textCursor()
        # cursor.movePosition(QtGui.QTextCursor.End)
        # cursor.insertText(text)
        # self.console_output_prompt.setTextCursor(cursor)
        # self.console_output_prompt.ensureCursorVisible()
        # Possibly just wt this line is sufficient? Test later
        self.console_output_prompt.setPlainText(text)


    # V3.0 reset the prompt output window
    def reset_window(self, page):
        if page == "prompt":
            self.console_output_prompt.clear()  # Clear previously generated prompt
            self.caselist_prompt.clear()  # Clear Previous Case
        elif page == "fc":
            self.caselist.clear() # Clear Previous Case
            self.fctemplate.setPlainText(
                "We received your question and will start to look into it, thank you.\n\nMedia: Email\n\nNext Step: I will search for the knowledge base.\n\nBusiness Impact: Not get this time.")
        elif page == "lang":
            self.caselist_lang.clear()  # Clear Previous Case

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
        self.worker.error_prompt.connect(self.display_error)

        # Start the thread
        self.thread.start()

        # Define callback function for message box
        def show_message_box():
            if not self.had_error:
                QMessageBox.information(self, "Completed", "Execution Completed!")
            # Enable the executeButton after the message box is closed
            self.executeButton.setEnabled(True)
            # Explicitly delete the thread and worker to avoid memory leak.
            # Need to add to the other two script functions later after testing
            try:
                self.worker.deleteLater()  # clean up the worker
                self.thread.deleteLater()  # clean up the thread
                self.worker = None  # De-reference worker so that the object get garbage collected immediately
                self.thread = None  # De-reference thread so that the object get garbage collected immediately
            except Exception as e:
                print(f"Exception while clearing the worker and thread {e}")
            # Reset the flag for next run
            self.had_error = False

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

    # start script in a new thread
    def start_generate_article_prompt_script(self):
        # Disable the execute button before starting the script to avoid multi-click by mistake
        self.executeButton_prompt.setEnabled(False)

        # Create a worker instance and move it to a new thread
        self.worker_prompt = Worker(sf=self.sf,caselist_prompt=self.caselist_prompt)
        self.thread_prompt = QThread()
        self.worker_prompt.moveToThread(self.thread_prompt)

        # Connect signals to slots
        # stop the thread once the worker is finished, otherwise the thread will continue in Running status
        self.worker_prompt.finished_prompt.connect(self.thread_prompt.quit)
        self.thread_prompt.started.connect(lambda: self.worker_prompt.generate_article_prompt(self.b_include_case_comment.isChecked()))
        self.worker_prompt.error_prompt.connect(self.display_error)
        self.worker_prompt.output_prompt.connect(self.write_prompt)

        # Start the thread
        self.thread_prompt.start()

        # Define callback function for message box
        def show_message_box():
            if not self.had_error:
                QMessageBox.information(self, "Completed", "Execution Completed!")

            # Enable the executeButton after the message box is closed
            self.executeButton_prompt.setEnabled(True)

            # Explicitly delete the thread and worker to avoid memory leak.
            # Need to add to the other two script functions later after testing
            try:
                self.worker_prompt.deleteLater()  # clean up the worker
                self.thread_prompt.deleteLater()  # clean up the thread
                self.worker_prompt = None  # De-reference worker so that the object get garbage collected immediately
                self.thread_prompt = None  # De-reference thread so that the object get garbage collected immediately
            except Exception as e:
                print(f"Exception while clearing the worker and thread {e}")
            # Reset the flag for next run
            self.had_error = False

        # Call the show_message_box function after the thread has finished executing
        self.thread_prompt.finished.connect(show_message_box)

    # V3.0 Show Error message box in UI
    def display_error(self, message):
        self.had_error = True  # Set error flag
        QMessageBox.critical(self, "Input Error", message)


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
              f'If you have changed your salesforce password, please update the config.json file with your new password.\n'
              f'exception: {e1}')
        raise
    # V3.0 handle invalid config.json exception
    except json.JSONDecodeError as e2:
        print(f"Exception in the config.json file \n make sure the json file has valid format and data: {e2}")
        raise
    except Exception as e:
        print(f'Unkown error occurred while login sf, if your credentials are correct, then try again to resolve... {e}')
        raise
    app = QApplication([])
    window = MyWindow(sf)
    window.show()
    app.exec_()
