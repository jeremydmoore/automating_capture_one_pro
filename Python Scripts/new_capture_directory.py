# new capture directory

# ============ imports ============ #
import applescript
import capture_one_pro_12 as co
from pathlib import Path


# ============ variables ============ #
begin_message = f'Begin - Python - {Path(__file__).name}'
end_message = f'End - Python - {Path(__file__).name}'

# ============ functions ============ #
def input_capture_directory_name():
    collection = applescript.get_user_input('Capture directory collection', 'ex: lady-vols-basketball')
    # applescript.display_dialog(collection)
    volume = applescript.get_user_input(f'Capture directory volume', 'ex: 2001')
    # applescript.display_dialog(volume)
    capture_directory_name = f'{collection}_{volume}'
    # applescript.display_dialog(capture_directory_name)
    return capture_directory_name


def verify_capture_directory_name(capture_directory_name):
    keep_name = applescript.get_user_input(f"Is directory name below correct, Y or N?\n{capture_directory_name}", 'Y')
    if str(keep_name).lower().startswith('y'):
        return True
    else:
        return False


def get_capture_directory_name(attempts_left=5):
    capture_directory_name = input_capture_directory_name()
    verified = verify_capture_directory_name(capture_directory_name)

    if verified:
        return capture_directory_name
    else:
        if attempts_left > 0:
            attempts_left = attempts_left - 1
            applescript.display_notification(f'Attempts left: {attempts_left}')
            get_capture_directory_name(attempts_left=attempts_left)
        else:
            applescript.display_dialog('No more attempts left')
            return None


# ============ run script ============ #
if __name__ == '__main__':

    applescript.display_notification(begin_message)

    capture_directory_name = get_capture_directory_name()

    applescript.display_dialog(f'New directory name: {capture_directory_name}')

    # reset to primary variant after creating new directory before next image capture

    # get primary variant info
    primary_variant = co.get_primary_variant()
    # applescript.display_dialog(primary_variant)

    # get document from primary_variant info
    document = primary_variant.split('document ', 1)[1]
    # applescript.display_dialog(document)

    # use document to get path to session directory
    session_directory_path = co.get_session_directory_path(document)
    # applescript.display_dialog(session_directory_path)

    # set path inside session_directory_path/Capture/<new name> and create directory
    capture_directory_path = Path(session_directory_path).joinpath('Capture', capture_directory_name)
    capture_directory_path.mkdir()
    if capture_directory_path.is_dir():
        applescript.display_dialog(f'Directory successfully created at:\n{capture_directory_path}')

    applescript.display_notification(end_message)
