from MyReadFile import read_file_to_array, read_file
from UpdateSFCaseClarificationAndClosureDetails import *
import json
import time


def get_case_recordtype(sf, case_number):
    query = "SELECT " + "RecordTypeId" + " FROM Case WHERE CaseNumber = '{}'".format(case_number)
    result = sf.query(query)
    record_type_id = result['records'][0]['RecordTypeId']
    return record_type_id


def create_fc(sf, case_number, fc_template):
    # If the fc.txt is blank:
    if is_blank_str(fc_template):
        fc_template='We received your question and will start to look into it, thank you.\n\nMedia: Email\n\nNext Step: I will search for the knowledge base.\n\nBusiness Impact: Not get this time.'
    # Get Case related info first, such as Id, AccountId,etc
    query = "SELECT Id,ContactId,Subject " \
            "FROM Case WHERE CaseNumber = '{}'".format(case_number)
    result = sf.query(query)
    case_id = result["records"][0]["Id"]
    contact_id = result["records"][0]["ContactId"]
    # Get the current date and time
    today = datetime.today()
    # Extract the date part only
    date_only = today.date()
    task = {
        'Subject': 'First Contact made for Case#'+case_number,
        'Description': fc_template,
        'Status': 'Completed',
        'Priority': 'Normal',
        'WhatId': case_id,  # Replace with the ID of the Case you want to create the Task for
        'WhoId': contact_id,  # Case Contact ID
        'TaskSubtype': 'Task',
        'Sub_Type__c': 'First Contact',
        'Time_Spent__c': 0.0,
        'Visible_To_Customer__c': True,
        'ActivityDate': str(date_only)
    }

    # Create the Task in Salesforce
    # try:
    sf.Task.create(task)
    print(f'Successfully Created First Contact Task for C{case_number}')
    # except Exception as e:
    #     print(f"An Error occurred while creating first contact task: {e}")


if __name__ == "__main__":
    # Open the JSON file for reading
    with open('config.json', 'r') as f:
        # Load the JSON data into a Python dictionary
        data = json.load(f)
    if len(data) == 0:
        raise ValueError('!!config.json is blank')
    # create a Salesforce object
    sf = Salesforce(username=data["username"],
                    password=data["password"],
                    security_token=data["security_token"])

    # Execute function
    fc_template = read_file('fc.txt')
    case_number_array = read_file_to_array("case.txt")
    if len(case_number_array) == 0:
        raise ValueError('!!Case # is blank, Add Case # to "case.txt" as xxxxxxxx without C prefix, E.g: 12345678')
    for case_number in case_number_array:
        #recordtypeid '012A0000000Vg0PIAS' is 'Technical Support'
        if get_case_recordtype(sf,case_number) == '012A0000000Vg0PIAS':
            try:
                # 1) get the case info for this case_number first
                case_info = get_case_info(sf, case_number)
                # 2) update assessment to True
                update_case_assessment(sf, case_number, case_info)
                time.sleep(0.5)
                # 3) Create FC
                create_fc(sf, case_number, fc_template)
                time.sleep(0.5)
                # 4) Update Clarification
                update_case_clarification(sf, case_number, case_info)
            except Exception as e:
                print(f"An Error occurred while creating first contact task or updating Case Clarification for C{case_number}: {e}")
        else:
            print(f"!!The case record type for C{case_number} is not Technical Support!! Update the Case Record Type to Technical Support for C{case_number} and try again")






