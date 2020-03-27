# ============ imports ============ #
import applescript
import capture_one_pro_12 as co
from pathlib import Path
import csv
import time

from otsu_autocrop import autocrop as otsu_autocrop

# ============ variables ============ #
begin_message = f'Begin - Python - {Path(__file__).name}'
end_message = f'End - Python - {Path(__file__).name}'
autocrop_recipe_name = 'autocrop_jpg'

# csv information
hot_folder_directory_path = co.scripts_dir_path.joinpath('Hot Folder')

fieldnames = ['image_name', 'image_path', 'variant', 'pixel_padding', 'autocrop_box', 'autocrop_rotation_angle', 'time_to_autocrop']


# ============ run script ============ #
if __name__ == '__main__':

    applescript.display_dialog(begin_message)

    # get list of selected variants to process
    selected_variants_list = co.get_selected_variants()

    # applescript.display_dialog(selected_variants_list)

    # get pixel padding input
    pixel_padding = applescript.get_user_input_int('pixel_padding', 35)
    camera = applescript.get_user_input_int('fuji = 1 or sony = 2', 1)
    if camera == 1:  # fuji 50s
        camera_height = 6192
        camera_width = 8256
    elif camera == 2:  # sony a7r2
        camera_height = 5304
        camera_width = 7952
    # applescript.display_dialog(f'Pixel padding: {pixel_padding}')

    number_of_selected_variants = len(selected_variants_list)

    # reset crop/rotation on selected image
    for index, selected_variant in enumerate(selected_variants_list):
        time_autocrop_start = time.perf_counter()
        if index > 0 and index % 5 == 0:
            stop_script_path = hot_folder_directory_path.joinpath('ERROR.ERROR')
            if stop_script_path.exists():
                applescript.display_dialog(f'Error file exists: {stop_script_path}\nEnding Script')
                break
        variant = co.Variant(selected_variant)
        applescript.display_notification(f'Processing {variant.image_name}\nVariant # {index+1}/{number_of_selected_variants}')
        # applescript.display_dialog(f'document: {variant.document}\nvariant id: {variant.id}')

        rotation_value = co.get_adjustment_values(variant.document, variant.collection_id, variant.id, 'rotation')
        flip_value = co.get_adjustment_values(variant.document, variant.collection_id, variant.id, 'flip')
        crop_box = co.get_crop_box(variant.document, variant.collection_id, variant.id)
        pre_crop_orientation_value = co.get_adjustment_values(variant.document, variant.collection_id, variant.id, 'orientation')[0]  # get first item in list
        # applescript.display_dialog(f'rotation before: {rotation_value}\nflip before: {flip_value}\ncrop before: {crop_box}')

        # reset orientation, flip, rotation, and crop
        orientation_value = co.set_adjustment_value(variant.document, variant.collection_id, variant.id, 'orientation', '0')[0]  # get first item in list
        flip_value = variant.reset_flip()
        rotation_value = variant.reset_rotation()
        crop_box = variant.reset_crop()  # is this an incorrect method?
        # applescript.display_dialog(f'rotation after reset: {rotation_value}\nflip after: {flip_value}\ncrop after reset: {crop_box}')

        # for right now . . . just output and crop single image then we'll work on faster batching later
        output_location = variant.output_with_recipe(autocrop_recipe_name)
        # applescript.display_dialog(output_location)
        output_path = Path(output_location)

        selected_variant_dict = {}

        # add data to dictionary file
        selected_variant_dict.update({'image_path': str(output_path)})
        selected_variant_dict.update({'image_name': variant.image_name})
        selected_variant_dict.update({'variant': selected_variant})
        selected_variant_dict.update({'pixel_padding': pixel_padding})
        # applescript.display_dialog(selected_variant_dict)

        # give image 5 seconds before skipping
        count = 0
        while count < 5 and not output_path.is_file():
            time.sleep(0.25)
            count += 0.25
        if output_path.is_file():  # autocrop
            applescript.display_notification(f'{variant.image_name} is file and took {count} seconds')
            applescript.display_notification(f'Auto Cropping: {variant.image_name}\n# {index+1}/{number_of_selected_variants}')

            # autocrop with Otsu
            capture_one_crop_data = otsu_autocrop(output_path, pixel_padding=pixel_padding, camera_height, camera_width)


            # ## AutoCrop with KMeans
            # # instantiate image
            # scan = NegativeScan(output_path)
            #
            # # set autocrop_height
            # autocrop_height = scan.image_cv2.shape[0]  # numpy arrays: height, width, channels
            #
            # # get binarized image
            # threshold = scan.threshold_kmeans()
            #
            # # get contours
            # contours = find_contours(threshold)
            #
            # # get rect, x, y, angle
            # rect, angle = find_external_rectangle(contours)
            # capture_one_crop_data = get_capture_one_coordinates(rect, angle, autocrop_height, pixel_padding=pixel_padding)

            if capture_one_crop_data is not None:

                # set crop data for Capture one
                autocrop_rotation_angle = capture_one_crop_data[0]
                autocrop_box = capture_one_crop_data[1:]

                # crop image
                autocrop_box = co.set_crop_box(variant.document, variant.collection_id, variant.id, autocrop_box)
                rotation_value = co.set_adjustment_value(variant.document, variant.collection_id, variant.id, 'rotation', autocrop_rotation_angle)[0]  # get first item in list

            elif capture_one_crop_data is None:
                autocrop_rotation_angle = capture_one_crop_data
                autocrop_box = capture_one_crop_data

            # reset orientation to orignal value
            if pre_crop_orientation_value != orientation_value:
                post_crop_orientation_value = co.set_adjustment_value(variant.document, variant.collection_id, variant.id, 'orientation', pre_crop_orientation_value)[0]  # get first item in list

            # applescript.display_dialog(f'pre: {pre_crop_orientation_value}\nduring: {orientation_value}\nafter: {post_crop_orientation_value}')
            # set orientation of item to 90 to rotate
            # applescript.display_dialog(f'New crop: {new_crop_box}')

            # stop autocrop stopclock for this variant
            time_autocrop_stop = time.perf_counter()
            time_to_autocrop = time_autocrop_stop - time_autocrop_start

            # update dictionary
            selected_variant_dict.update({'autocrop_rotation_angle': rotation_value})
            selected_variant_dict.update({'autocrop_box': autocrop_box})
            selected_variant_dict.update({'time_to_autocrop': time_to_autocrop})

            # assume the image is correctly named with <identifier>_<index #>
            # the index # is 3 digits long plus an underscore get all data before last underscore
            volume_name = variant.image_name.rsplit('_', 1)[0]
            # applescript.display_dialog(volume_name)
            volume_csv_path = hot_folder_directory_path.joinpath(f'{volume_name}.csv')
            # open CSV and write selected_variant_dict
            with open(volume_csv_path, 'a') as csv_file:
                 writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                 writer.writerow(selected_variant_dict)

        else:  # no output file to autocrop
            applescript.display_dialog('No outputfile to AutoCrop')
            break

    applescript.display_dialog(end_message)
