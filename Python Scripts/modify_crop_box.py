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

    # set direction to lower case and get pixels as an integer
    direction = args["direction"].lower()
    pixels = int(args["pixels"])

    if direction in left_directions or direction in down_directions:
        # movement should be negative
        pixels = -pixels

    # print(f'Shift crop box {args["pixels"]} pixels to the {args["direction"]}.')

    # get list of selected variants to process
    selected_variants_list = co.get_selected_variants()
    number_of_selected_variants = len(selected_variants_list)
    applescript.display_notification(f'Processing {number_of_selected_variants} VARIANTS')
    for index, selected_variant in enumerate(selected_variants_list):
        # if index > 0 and index % 3 == 0:
        #     stop_script_path = hot_folder_directory_path.joinpath('ERROR.ERROR')
        #     if stop_script_path.exists():
        #         applescript.display_dialog(f'Error file exists: {stop_script_path}\nEnding Script')
        #         break
        # otherwise we're going to process the variant
        variant = co.Variant(selected_variant)


        crop_box = co.get_crop_box(variant.document, variant.collection_id, variant.id)
        center_x, center_y, width, height = crop_box

        if direction in horizontal_directions:
            center_x = str(int(center_x) + pixels)
        elif direction in vertical_directions:
            center_y = str(int(center_y) + pixels)

        else:
            applescript.display_info(f'Direction given \"{args["direction"]}\" is not valid\nPlease choose from "left, right, up, down, or the cardinal directions"')

        new_crop_box = [center_x, center_y, width, height]
        applied_crop_box = co.set_crop_box(variant.document, variant.collection_id, variant.id, new_crop_box)
    applescript.display_notification(f'{number_of_selected_variants} VARIANTS Processed')
