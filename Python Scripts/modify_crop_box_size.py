# ============ imports ============ #
import applescript
import argparse
import capture_one_pro_12 as co
from pathlib import Path

# ============ variables ============ #
directions = ['horizontal', 'vertical']
actions = ['expand', 'contract']

hot_folder_directory_path = co.scripts_dir_path.joinpath('Hot Folder')

# ============ run script ============ #
if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-a", "--action", required=True, help="Expand or contract crop box")
    arg_parser.add_argument("-d", "--direction", required=True, help="Direction to change crop box size")
    arg_parser.add_argument("-p", "--pixels", required=True, help="Number of pixels to change the crop box size -- YAY!")
    args = vars(arg_parser.parse_args())

    # get list of selected variants to process
    selected_variants_list = co.get_selected_variants()

    # set direction and action to lower case and get pixels as an integer
    action = args["action"].lower()
    direction = args["direction"].lower()
    pixels = int(args["pixels"])

    # total border is 2x the number of pixels
    pixels_to_add_to_crop_box = pixels * 2

    # expand = add pixels to both sides evenly
    # contract = subtract pixels from both sides evenly
    if action == 'contract':
        pixels_to_add_to_crop_box = -pixels_to_add_to_crop_box

    # get list of selected variants to process
    selected_variants_list = co.get_selected_variants()
    number_of_selected_variants = len(selected_variants_list)

    # reset crop/rotation on selected image
    for index, selected_variant in enumerate(selected_variants_list):

        # stop batch running if ERROR.ERROR file is used
        if index > 0 and index % 3 == 0:
            stop_script_path = hot_folder_directory_path.joinpath('ERROR.ERROR')
            if stop_script_path.exists():
                applescript.display_dialog(f'Error file exists: {stop_script_path}\nEnding Script')
                break
        variant = co.Variant(selected_variant)
        applescript.display_notification(f'Processing {variant.image_name}\nVariant # {index+1}/{number_of_selected_variants}')

        crop_box = co.get_crop_box(variant.document, variant.collection_id, variant.id)
        center_x, center_y, width, height = crop_box

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
        applied_crop_box = co.set_crop_box(variant.document, variant.collection_id, variant.id, new_crop_box)

        check_crop_box = co.get_crop_box(variant.document, variant.collection_id, variant.id)
        if new_crop_box != check_crop_box:
            applescript.display_info(f'expected crop_box {new_crop_box} is not equal to actual crop_box {check_crop_box}')
            # TODO: attempt to reset to old crop value
