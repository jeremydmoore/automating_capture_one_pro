# ============ imports ============ #
import applescript
import argparse
import capture_one_pro_12 as co
from pathlib import Path

# ============ variables ============ #
directions = ['horizontal', 'vertical']
actions = ['expand', 'contract']

# ============ run script ============ #
if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-a", "--action", required=True, help="Expand or contract crop box")
    arg_parser.add_argument("-d", "--direction", required=True, help="Direction to change crop box size")
    arg_parser.add_argument("-p", "--pixels", required=True, help="Number of pixels to change the crop box size -- YAY!")
    args = vars(arg_parser.parse_args())

    # print(f'Shift crop box {args["pixels"]} pixels to the {args["direction"]}.')

    command = co.command_stub + [f'{co.tell_co12} to set primary_variant to (get primary variant)', 'return primary_variant']
    primary_variants_list = applescript.command_to_python_list(command)

    primary_variant = co.Variant(primary_variants_list[0])

    crop_box = co.get_crop_box(primary_variant.document, primary_variant.collection_id, primary_variant.id)
    center_x, center_y, width, height = crop_box

    print(f'Crop box of {primary_variant.id} is {center_x, center_y, width, height}')

    # set direction and action to lower case and get pixels as an integer
    action = args["action"].lower()
    direction = args["direction"].lower()
    pixels = int(args["pixels"])

    # total border is 2x the number of pixels
    pixels_to_add_to_crop_box = pixels * 2

    if action == 'contract':
        pixels_to_add_to_crop_box = -pixels_to_add_to_crop_box

    # expand = add pixels to both sides evenly
    # contract = subtract pixels from both sides evenly

    # only modify center_x and width for horizontal
    # only modify center_y and height for vertical

    # need width and height values as strings
    if direction == 'vertical':
        height = str(int(height) + pixels_to_add_to_crop_box)
    elif direction == 'horizontal':
        width = str(int(width) + pixels_to_add_to_crop_box)
    else:
        applescript.display_info(f'Direction given \"{args["direction"]}\" is not valid\nPlease choose between "Vertical" and "Horizontal"')

    new_crop_box = [center_x, center_y, width, height]
    applied_crop_box = co.set_crop_box(primary_variant.document, primary_variant.collection_id, primary_variant.id, new_crop_box)
