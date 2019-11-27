# importing
from pathlib import Path
import capture_one_pro_12 as co
import applescript
import pandas as pd

from otsu_autocrop import autocrop as otsu_autocrop

## csv information
hot_folder_directory_path = co.scripts_dir_path.joinpath('Hot Folder')
athletics_csv_path = hot_folder_directory_path.joinpath('athletics_programs.csv')
fieldnames = ['image_name', 'image_path', 'variant', 'pixel_padding']

to_process_df = pd.read_csv(athletics_csv_path)

number_of_rows = len(to_process_df.index)
for index in range(number_of_rows):
    file_info_list = to_process_df.loc[index].tolist()
    image_name, image_path, variant, pixel_padding = file_info_list[:]
    applescript.display_notification(f'Cropping: {image_name}\n# {index+1}/{number_of_rows}')
    image_path = Path(image_path)
    if image_path.is_file():
        capture_one_crop_data = otsu_autocrop(image_path, pixel_padding=pixel_padding)
        # applescript.display_dialog(capture_one_crop_data)

        autocrop_rotation_angle = capture_one_crop_data[0]
        autocrop_box = capture_one_crop_data[1:]
        # applescript.display_dialog(f'angle: {autocrop_rotation_angle}\nbox: {autocrop_box}')

        # crop image
        variant = co.Variant(variant)
        new_crop_box = co.set_crop_box(variant.document, variant.collection_id, variant.id, autocrop_box)
        rotation_value = co.set_adjustment_value(variant.document, variant.collection_id, variant.id, 'rotation', autocrop_rotation_angle)[0]  # get first item in list
        # applescript.display_dialog(f'New crop: {new_crop_box}')

    #
    # # get capture one values for crop box from autocropResult
	# 		set autocrop_rotation_angle to item 1 in paragraphs of autocropResult
	# 		set autocrop_center_x to (item 2 in paragraphs of autocropResult as number)
	# 		set autocrop_center_y to (item 3 in paragraphs of autocropResult as number)
	# 		set autocrop_width to (item 4 in paragraphs of autocropResult as number)
	# 		set autocrop_height to (item 5 in paragraphs of autocropResult as number)
	# 		set autocrop_box to {autocrop_center_x, autocrop_center_y, autocrop_width, autocrop_height}

# if __name__ == "__main__":
#
#     # single autocrop
#     capture_one_data_as_str = autocrop(image_path, pixel_padding=pixel_padding)
#
#     print("\n".join(capture_one_data_as_str))
