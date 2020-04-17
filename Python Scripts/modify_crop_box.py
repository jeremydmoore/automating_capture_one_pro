# ============ imports ============ #
import applescript
import argparse
import capture_one_pro_20 as co
from pathlib import Path

# ============ variables ============ #
horizontal_directions = ['left', 'west', 'right', 'east']
left_directions = ['left', 'west']
right_directions = ['right', 'east']
vertical_directions = ['up', 'north', 'down', 'south']
up_directions = ['up', 'north']
down_directions = ['down', 'south']

# ============ run script ============ #
if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-d", "--direction", required=True, help="Direction to shift crop box towards")
    arg_parser.add_argument("-p", "--pixels", required=True, help="Number of pixels to shift the crop box")
    args = vars(arg_parser.parse_args())

    print(f'Shift crop box {args["pixels"]} pixels to the {args["direction"]}.')

    command = co.command_stub + [f'{co.tell_co} to set primary_variant to (get primary variant)', 'return primary_variant']
    primary_variants_list = applescript.command_to_python_list(command)

    primary_variant = co.Variant(primary_variants_list[0])

    crop_box = co.get_crop_box(primary_variant.document, primary_variant.collection_id, primary_variant.id)
    center_x, center_y, width, height = crop_box

    print(f'Crop box of {primary_variant.id} is {center_x, center_y, width, height}')

    # set direction to lower case and get pixels as an integer
    direction = args["direction"].lower()
    pixels = int(args["pixels"])

    if direction in left_directions or direction in down_directions:
        # movement should be negative
        pixels = -pixels

    if direction in horizontal_directions:
        center_x = str(int(center_x) + pixels)
    elif direction in vertical_directions:
        center_y = str(int(center_y) + pixels)

    else:
        applescript.display_info(f'Direction given \"{args["direction"]}\" is not valid\nPlease choose from "left, right, up, down, or the cardinal directions"')

    new_crop_box = [center_x, center_y, width, height]
    applied_crop_box = co.set_crop_box(primary_variant.document, primary_variant.collection_id, primary_variant.id, new_crop_box)
