# v3.0 change log:
    # New Features:
        # 1. Article Prompt for AAA feature implemented
        How to use it:
        1) Provide a case number with XXXXXXXX or CXXXXXXXX
        2) Click Execute button
        3) Copy the Generated Prompt for AAA and paste to AAA tool for article creation
        Note: If Include Case Comment is checked, the generated prompt will also include the Case Comment
    # Bug Fixes:
        # 1. Logging exceptions instead of crashing the program when:
            1) Provided config.json file is invalid
            2) Provided Case number is invalid or doesn't exist
    # Improvements:
        # 1. Added Reset button on each page to reset the contents
        # 2. The error message will show in a popup message in addition to the log
        # 3. Format the closure detail date format to align with the SF "Add Status" format
            # After: [2 Jan 25] for 2025/1/2
            # Before: [02 Jan 25] for 2025/1/2

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