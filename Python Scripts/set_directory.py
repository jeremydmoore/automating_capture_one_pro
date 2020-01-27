# set - directory

# ============ imports ============ #
import applescript
import capture_one_pro_12 as co
from pathlib import Path


# ============ variables ============ #
begin_message = f'Begin - Python - {Path(__file__).name}'
end_message = f'End - Python - {Path(__file__).name}'
capture_one_pro_12_directory_names = ['Capture', 'Output', 'Selects', 'Trash']
data_directory_path = Path.home().joinpath('Library', 'Scripts', 'data')
last_value_path = data_directory_path.joinpath('set_directory_last_value.csv')

# ============ functions ============ #


def input_directory_name(directory):
    if directory not in capture_one_pro_12_directory_names:
        return None
    collection = applescript.get_user_input('Capture directory collection',
                                            'ex: lady-vols-basketball')
    # applescript.display_dialog(collection)
    volume = applescript.get_user_input(f'Capture directory volume',
                                        'ex: 2001')
    # applescript.display_dialog(volume)
    directory_name = f'{collection}_{volume}'
    # applescript.display_dialog(directory_name)
    return directory_name


def verify_directory_name(directory_name):
    question = f'Is this the correct directory name:\n{directory_name}'
    option_1 = 'Yes'
    option_2 = 'No'
    user_input = applescript.display_dialog_question(question,
                                                     option_1, option_2)
    if user_input == 'Yes':
        return True
    elif user_input == 'No':
        return False


def get_directory_name(attempts_left=5):
    directory_name = input_directory_name('Capture')
    verified = verify_directory_name(directory_name)

    if verified:
        return directory_name
    else:
        if attempts_left > 0:
            attempts_left = attempts_left - 1
            applescript.display_notification(f'Attempts left: {attempts_left}')
            get_directory_name(attempts_left=attempts_left)
        else:
            applescript.display_dialog('No more attempts left')
            return None


# ============ run script ============ #
if __name__ == '__main__':

    applescript.display_notification(begin_message)

    directory_name = get_directory_name()

    applescript.display_dialog(f'New directory name: {directory_name}')

    # reset to primary variant after creating new
    # directory before next image capture

    # get primary variant info
    primary_variant = co.get_primary_variant()
    # applescript.display_dialog(primary_variant)

    # get document from primary_variant info
    document = primary_variant.split('document ', 1)[1]
    # applescript.display_dialog(document)

    # use document to get path to session directory
    session_directory_path = co.get_session_directory_path(document)
    # applescript.display_dialog(session_directory_path)

    # set path inside session_directory_path/Capture/<new name>
    # and create directory
    directory_path = Path(session_directory_path).joinpath('Capture',
                                                           directory_name)
    directory_path.mkdir()
    if directory_path.is_dir():
        msg = f'Directory successfully created at:\n{directory_path}'
        applescript.display_dialog(msg)

    applescript.display_notification(end_message)
