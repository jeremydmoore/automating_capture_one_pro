# ============ imports ============ #
import applescript
import capture_one_pro_20 as co
from pathlib import Path

# ============ variables ============ #
begin_message = f'Begin - Python - {Path(__file__).name}'
end_message = f'End - Python - {Path(__file__).name}'

# hot folder location for errors
hot_folder_directory_path = co.scripts_dir_path.joinpath('Hot Folder')

# ============ run script ============ #
if __name__ == '__main__':

    # applescript.display_dialog(begin_message)

    # get primary variant
    command = co.command_stub + [f'{co.tell_co} to set primary_variant to (get primary variant)', 'return primary_variant']
    primary_variants_list = applescript.command_to_python_list(command)  # TODO: refactor and remove list if only 1 item
    primary_variant = co.Variant(primary_variants_list[0])
    # applescript.display_dialog(f'Primary variant image: {primary_variant.image_name}\nOrientation: {primary_variant.orientation}\nHeight: {primary_variant.height}')

    # get list of selected variants to process
    selected_variants_list = co.get_selected_variants()

    number_of_selected_variants = len(selected_variants_list)

    # process selected variants
    for index, selected_variant in enumerate(selected_variants_list):

        # horribly primitive error handling
        if index > 0 and index % 5 == 0:
            stop_script_path = hot_folder_directory_path.joinpath('ERROR.ERROR')
            if stop_script_path.exists():
                applescript.display_dialog(f'Error file exists: {stop_script_path}\nEnding Script')
                break
        # if the selected_variant is the primary variant then SKIP IT
        elif selected_variant == primary_variants_list[0]:
            applescript.display_notification(f'Skip processing Primary Variant:\n{primary_variant.image_name}\nVariant {index+1} of {number_of_selected_variants}')
            continue

        # instantiate co.Variant class with current selected variant
        variant = co.Variant(selected_variant)

        if variant.orientation == primary_variant.orientation:
             new_width, new_height = primary_variant.width, primary_variant.height
        else:  # new_height == primary_variant.width
            new_height, new_width = primary_variant.width, primary_variant.height

        new_crop_box = [variant.center_x, variant.center_y, new_width, new_height]

        variant.set_crop_box(new_crop_box)

        if variant.width != primary_variant.width or variant.height != primary_variant.height:
            applescript.display_dialog(f'Width or Height not set correctly for {variant.image_name}')
        else:
            applescript.display_notification(f'Crop set for {variant.image_name}\nVariant {index+1} of {number_of_selected_variants}')

    # applescript.display_dialog(end_message)
