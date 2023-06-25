# v2.2 change log:
    # Removed Save Assessment as it causes the case owner change to Admin Queue

# v2.1 change log:
    # Removed Change Case Status logic(It won't change to Working status anymore), we see change case status under some conditions would casue the case to be reassigned to Admin Queue. So removed it and now the case status will remain unchanged after running the Execute

# v2.0 change log:
# Major changes:
    # Combined FC page and Language page into one UI
    # Added update_asessment, the FC script now would 1) Save assessment 2) Create FC 3) Update Clarification, case status, closure details
    # script now skips the case if the case already have FC task created
    # script now start in separate thread so the main UI does not get freeze
    # the FC Execute button is disabled when user click and re-enabled when task is completed to avoid user click multi times
    # The UI changed to responsive UI, previous it is static UI

# Minor changes:
    # Log print format added timestamp
    # When wrong credentials provided in config.json, then error is captured and shown
    # Removed the console window when executing .exe tool

# Known limitation:
    # When the case status is On Hold status, then running the script
    # would reassign the case to Admin Queue, not sure why
    # it's a rare situation that we would do FC for case that is On Hold status, so not big impact