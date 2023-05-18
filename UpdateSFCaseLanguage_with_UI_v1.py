from simple_salesforce import Salesforce
from MyReadFile import read_file_to_array
from UpdateSFCaseClarificationAndClosureDetails import get_case_info
import json

# # Open the JSON file for reading
# with open('config.json', 'r') as f:
#     # Load the JSON data into a Python dictionary
#     data = json.load(f)
#
# # create a Salesforce object
# sf = Salesforce(username=data["username"],
#                 password=data["password"],
#                 security_token=data["security_token"])


#
# Update Case Language v1 change log: added case_info parameter
#
def update_case_lang(sf, case_number, case_info, case_record_target_lang):
    # case_number = '16781852'
    case_id = case_info["Id"]
    case_language_orig = case_info["Language__c"]
    print(case_number, case_id, case_language_orig)

    # Update Particular Case Language:
    # Available Language__c value:
    # English, Simplified Chinese, Traditional Chinese, Korean, Japanese, French, German, Italian, Portuguese, Spanish
    case_record_lang = {'Language__c': case_record_target_lang}
    try:
        sf.Case.update(case_id, case_record_lang)
        print(f'Successfully updated C{case_number} Language from {case_language_orig} to {case_record_target_lang}')
    except Exception as e:
        print(f"An Error occurred while updating Case Language: {e}")
        raise


if __name__ == '__main__':
    case_number_array = read_file_to_array("case.txt")
    # print(case_number_array)
    for case_number in case_number_array:
        case_info = get_case_info(sf, case_number)
        update_case_lang(sf, case_number, case_info, 'Korean')
