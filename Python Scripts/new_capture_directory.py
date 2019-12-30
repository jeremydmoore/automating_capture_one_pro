# new capture directory

# ============ imports ============ #
import applescript
import capture_one_pro_12 as co
from pathlib import Path
import csv
import time


# ============ variables ============ #
begin_message = f'Begin - Python - {Path(__file__).name}'
end_message = f'End - Python - {Path(__file__).name}'


# ============ run script ============ #
if __name__ == '__main__':

    applescript.display_dialog(begin_message)

    new_capture_directory_name = applescript.get_user_input('New capture directory name', 'type here')
