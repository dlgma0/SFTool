from simple_salesforce import Salesforce
from MyReadFile import read_file_to_array
from MyReadFile import is_blank_str
from datetime import datetime, timedelta, time
import pytz
import json

# create a Salesforce object
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

OwnerId = '005F0000004zlmwIAA'

def get_case_info(case_number):
    # Find out all available fields for Case
    table_metadata = sf.Case.describe()
    fields = table_metadata['fields']
    str1 = ""
    for field in fields:
        # print(field['name'])
        str1 = str1 + field['name'] + ","
    query_fields = str1[:-1]
    # print(query_fields)

    # Query case's all information, just like SELECT *
    # query = "SELECT " + query_fields + " FROM Case WHERE CaseNumber = '{}'".format(case_number)
    query = "SELECT " + "RecordTypeId" + " FROM Case WHERE CaseNumber = '{}'".format(case_number)
    result = sf.query(query)
    print(result['records'][0]['RecordTypeId'])
    # print the results
    # for record in result['records']:
    #     print(record)

# Not tested yet. do not use below function
def get_case_owner_recent_case(ownerName="Sam Li"):
    caseAssignedDate = datetime.now(pytz.timezone('Etc/GMT'))
    yesterday = caseAssignedDate - timedelta(days=1)
    print(ownerName, yesterday)

    # UTC time(GMT+0) : the case's date information is UTC time
    # print(datetime.now(pytz.timezone('Etc/GMT')))
    # GMT+8 time
    # new_timezone = pytz.timezone('Asia/Shanghai')
    # converted_date = datetime.now(pytz.timezone('Etc/GMT')).astimezone(new_timezone)

    query = "SELECT CaseNumber,Owner_Name__c,Assigned_On__c FROM Case WHERE Owner_Name__c = '{}'" \
            " AND Assigned_On__c<{} LIMIT 10".format(ownerName, yesterday)
    result = sf.query(query)
    # print the results
    print(result['records'])
# Specify case number
# case_number = '16781852'
# get_case_info(case_number)


def get_case_info2(sf, case_number):
    query = "SELECT Id,Assessment_Done__c,Issue_has_been_Clarified__c,Symptoms__c,Steps_to_Reproduce__c,Error_s__c," \
            "Resolution_Criteria__c,Business_Impact__c,Delivered_Solution__c,Status,OnHold_Reason__c," \
            "LongSubject__c " \
            "FROM Case WHERE CaseNumber = '{}'".format(case_number)
    result = sf.query(query)
    return result["records"][0]

# get_case_owner_recent_case()
result = get_case_info2(sf, '16830825')
print(type(result))
print(result["Id"], result["Symptoms__c"], result["Assessment_Done__c"])

