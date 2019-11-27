# ============ imports ============ #
from subprocess import PIPE, run

# ============ functions ============ #
def convert_applescript_output_to_python_list(applescript_subprocess):
    return [x.strip('\n').strip(' ') for x in applescript_subprocess.stdout.split(',')]


def display_dialog(message):
    command = [f'Tell application \"System Events\" to display dialog \"{message}\"']
    dialog = process(command)
    return dialog

def display_notification(message):
    command = [f'Tell application \"System Events\" to display notification \"{message}\"']
    dialog = process(command)
    return dialog

def get_user_input_int(value_name, default_value, attempts_left=5):
    user_input = None
    # only process if the default value is of the expected input type
    if isinstance(default_value, int):

        command = [f'set value_name to text returned of (display dialog "Enter {value_name} (type: integer)\nAttempts left: {attempts_left}" default answer "{default_value}")', 'return value_name']
        user_input = command_to_python_list(command)

        if user_input:
            # returned value should be a single string in a list
            user_input = user_input[0]
            try:
                user_input = int(user_input)
            except ValueError:
                if attempts_left > 0:
                    attempts_left = attempts_left - 1
                    user_input = get_user_input_int(value_name, default_value, attempts_left=attempts_left)
                else:
                    user_input = None

    return user_input


def command_to_python_list(command):
    applescript_output = process(command)
    python_list = convert_applescript_output_to_python_list(applescript_output)
    return python_list


def process(command):
    osascript_run_command = ['osascript']
    if isinstance(command, list):
        for line in command:
            osascript_run_command.append('-e')
            osascript_run_command.append(line)
    else:
        osascript_run_command.append('-e')
        osascript_run_command.append(command)
    applescript_subprocess = run(osascript_run_command, encoding='utf-8', stdout=PIPE, stderr=PIPE)

    return applescript_subprocess


def process_script(script_path, args=None):
    shell_input = ['osascript', str(script_path)]
    if args:
        if isinstance(args, list):
            for arg in args:
                shell_input = shell_input + [arg]
        else:
            shell_input = shell_input + [args]
    applescript_subprocess = run(shell_input, encoding='utf-8', stdout=PIPE, stderr=PIPE)
    return applescript_subprocess


def script_to_python_list(script_path, args=None):
    applescript_subprocess = process_script(script_path, args)
    python_list = convert_applescript_output_to_python_list(applescript_subprocess)
    return python_list
