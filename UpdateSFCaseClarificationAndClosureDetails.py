from simple_salesforce import Salesforce
from MyReadFile import read_file_to_array, is_blank_str
from datetime import datetime
import json


# Check whether
# case_info type: OrderedDict
def is_fc_made(sf, case_info):
    case_id = case_info['Id']
    tasks = sf.query_all("SELECT Id, Sub_Type__c FROM Task WHERE WhatId = '{}'".format(case_id))
    task_type = 'First Contact'
    task_exists = False
    for task in tasks['records']:
        if task['Sub_Type__c'] == task_type:
            task_exists = True
    return task_exists


def get_case_info(sf, case_number):
    query = "SELECT Id,Assessment_Done__c,Issue_has_been_Clarified__c,Symptoms__c,Steps_to_Reproduce__c,Error_s__c," \
            "Resolution_Criteria__c,Business_Impact__c,Delivered_Solution__c,Status,OnHold_Reason__c," \
            "LongSubject__c,Language__c " \
            "FROM Case WHERE CaseNumber = '{}'".format(case_number)
    result = sf.query(query)
    return result["records"][0]
# update_case_clarification v2:
# 1) removed parameter case_number
# 2) added case_info
def update_case_clarification(sf, case_number, case_info):
    case_id = case_info["Id"]
    # Original values for Clarification fields
    case_isClarified = case_info["Issue_has_been_Clarified__c"]
    case_symptom_orig = case_info["Symptoms__c"]
    case_steps_orig = case_info["Steps_to_Reproduce__c"]
    case_errors_orig = case_info["Error_s__c"]
    case_resolution_orig = case_info["Resolution_Criteria__c"]
    case_impact_orig = case_info["Business_Impact__c"]
    case_closure_details = case_info["Delivered_Solution__c"]



    # Format the content for Closure Details
    orig_str = case_closure_details
    working_str = " Working on it\n"
    # need_more_info = " Asked for more detail info\n"
    # current_date = datetime.today().strftime('%Y-%m-%d')
    current_date = datetime.today().strftime('%Y-%b-%d')
    formatted_date = "[" + current_date + "]"
    closure_working = formatted_date + working_str if(is_blank_str(orig_str)) else formatted_date + working_str + orig_str

    # Target values for Clarification fields
    target_isClarified = True
    target_symptom = case_info["LongSubject__c"] if is_blank_str(case_symptom_orig) else case_symptom_orig
    target_steps = 'N/A' if is_blank_str(case_steps_orig) else case_steps_orig
    target_errors = 'N/A' if is_blank_str(case_errors_orig) else case_errors_orig
    target_resolution = 'Provide Resolution' if is_blank_str(case_resolution_orig) else case_resolution_orig
    target_impact = 'N/A' if is_blank_str(case_impact_orig) else case_impact_orig
    target_closure_details = closure_working
    target_status = 'Working'
    target_sub_status = None

    # Print to see the original and target values
    # print(result)
    # print(case_number, case_id)
    # print("Original Values:", case_isClarified, case_symptom_orig, case_steps_orig, case_errors_orig,
    #       case_resolution_orig, case_impact_orig)
    # print("Target Values:", target_isClarified, target_symptom, target_steps, target_errors, target_resolution, target_impact)

    #
    # Update the Clarification of the case record
    # case_id 不是case number, 是Case里面的Id字段值，18位字符串
    # case_id = '5006e00001vQwHpAAK'

    # case_record = sf.Case.get(case_id)
    case_record_clarification = {'Issue_has_been_Clarified__c': target_isClarified,
                                 'Symptoms__c': target_symptom,
                                 'Steps_to_Reproduce__c': target_steps,
                                 'Error_s__c': target_errors,
                                 'Resolution_Criteria__c': target_resolution,
                                 'Business_Impact__c': target_impact,
                                 'Delivered_Solution__c': target_closure_details
                                 # 发现修改状态的话Case Owner会被改为Admin Queue，就算改OwnerId也没用，所以还是不改下面的内容了
                                 # 'Status': target_status,
                                 # 'OnHold_Reason__c': target_sub_status,
                                 # 'OwnerId': '005F0000004zlmwIAA'
                                 }
    try:
        sf.Case.update(case_id, case_record_clarification)
        print(f'Successfully updated Clarification for C{case_number}')
    except Exception as e:
        print(f"An Error occurred while updating: {e}")


def update_case_clarification_v1(sf, case_number):
    query = "SELECT Id,Issue_has_been_Clarified__c,Symptoms__c,Steps_to_Reproduce__c,Error_s__c," \
            "Resolution_Criteria__c,Business_Impact__c,Delivered_Solution__c,Status,OnHold_Reason__c," \
            "LongSubject__c " \
            "FROM Case WHERE CaseNumber = '{}'".format(case_number)
    result = sf.query(query)
    case_id = result["records"][0]["Id"]

    # Original values for Clarification fields
    case_isClarified = result["records"][0]["Issue_has_been_Clarified__c"]
    case_symptom_orig = result["records"][0]["Symptoms__c"]
    case_steps_orig = result["records"][0]["Steps_to_Reproduce__c"]
    case_errors_orig = result["records"][0]["Error_s__c"]
    case_resolution_orig = result["records"][0]["Resolution_Criteria__c"]
    case_impact_orig = result["records"][0]["Business_Impact__c"]
    case_closure_details = result["records"][0]["Delivered_Solution__c"]



    # Format the content for Closure Details
    orig_str = case_closure_details
    working_str = " Working on it\n"
    # need_more_info = " Asked for more detail info\n"
    # current_date = datetime.today().strftime('%Y-%m-%d')
    current_date = datetime.today().strftime('%Y-%b-%d')
    formatted_date = "[" + current_date + "]"
    closure_working = formatted_date + working_str if(is_blank_str(orig_str)) else formatted_date + working_str + orig_str

    # Target values for Clarification fields
    target_isClarified = True
    target_symptom = result["records"][0]["LongSubject__c"] if is_blank_str(case_symptom_orig) else case_symptom_orig
    target_steps = 'N/A' if is_blank_str(case_steps_orig) else case_steps_orig
    target_errors = 'N/A' if is_blank_str(case_errors_orig) else case_errors_orig
    target_resolution = 'Provide Resolution' if is_blank_str(case_resolution_orig) else case_resolution_orig
    target_impact = 'N/A' if is_blank_str(case_impact_orig) else case_impact_orig
    target_closure_details = closure_working
    target_status = 'Working'
    target_sub_status = None

    # Print to see the original and target values
    # print(result)
    # print(case_number, case_id)
    # print("Original Values:", case_isClarified, case_symptom_orig, case_steps_orig, case_errors_orig,
    #       case_resolution_orig, case_impact_orig)
    # print("Target Values:", target_isClarified, target_symptom, target_steps, target_errors, target_resolution, target_impact)

    #
    # Update the Clarification of the case record
    # case_id 不是case number, 是Case里面的Id字段值，18位字符串
    # case_id = '5006e00001vQwHpAAK'

    case_record = sf.Case.get(case_id)
    case_record_clarification = {'Issue_has_been_Clarified__c': target_isClarified,
                                 'Symptoms__c': target_symptom,
                                 'Steps_to_Reproduce__c': target_steps,
                                 'Error_s__c': target_errors,
                                 'Resolution_Criteria__c': target_resolution,
                                 'Business_Impact__c': target_impact,
                                 'Delivered_Solution__c': target_closure_details,
                                 # 发现修改状态的话Case Owner会被改为Admin Queue，就算改OwnerId也没用，所以还是不改下面的内容了
                                 'Status': target_status,
                                 'OnHold_Reason__c': target_sub_status
                                 # 'OwnerId': '005F0000004zlmwIAA'
                                 }
    try:
        sf.Case.update(case_id, case_record_clarification)
        print(f'Successfully updated Clarification for C{case_number}')
    except Exception as e:
        print(f"An Error occurred while updating: {e}")


def update_case_assessment(sf, case_number, case_info):
    case_id = case_info["Id"]
    case_assessment = {'Assessment_Done__c': True}
    try:
        sf.Case.update(case_id, case_assessment)
        print(f'Successfully updated assessment for C{case_number}')
    except Exception as e:
        print(f"An Error occurred while updating assessment: {e}")


if __name__ == "__main__":
    # This code block only runs when .py is executed as a script
    # Open the JSON file for reading
    with open('config.json', 'r') as f:
        # Load the JSON data into a Python dictionary
        data = json.load(f)

    # create a Salesforce object
    sf = Salesforce(username=data["username"],
                    password=data["password"],
                    security_token=data["security_token"])
    #
    # Query Case Id from Case Number
    #
    # case_number = '16781852'
    case_number_array = read_file_to_array("case.txt")
    # print(case_number_array)
    for case_number in case_number_array:
        # 1) get the case info for this case_number first
        case_info = get_case_info(sf, case_number)
        # 2) update assessment to True
        update_case_assessment(sf, case_number, case_info)
        # 3) update clarification
        update_case_clarification(sf, case_number, case_info)






