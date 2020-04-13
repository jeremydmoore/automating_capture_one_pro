# ============ imports ============ #
import applescript
import capture_one_pro_20 as co
from pathlib import Path
import csv
import time

from otsu_autocrop import autocrop as otsu_autocrop

from kmeans_autocrop import NegativeScan, find_contours, find_external_rectangle, get_capture_one_coordinates

# ============ variables ============ #
begin_message = f'Begin - Python - {Path(__file__).name}'
end_message = f'End - Python - {Path(__file__).name}'
autocrop_recipe_name = 'autocrop_jpg'

## csv information
hot_folder_directory_path = co.scripts_dir_path.joinpath('Hot Folder')

fieldnames = ['image_name', 'image_path', 'variant', 'pixel_padding', 'autocrop_box', 'autocrop_rotation_angle', 'time_to_autocrop']


# ============ run script ============ #
if __name__ == '__main__':

    applescript.display_dialog(begin_message)

    # get list of selected variants to process
    selected_variants_list = co.get_selected_variants()

    # applescript.display_dialog(selected_variants_list)

    command = co.command_stub + [f'{co.tell_co20} to set primary_variant to (get primary variant)', 'return primary_variant']
    primary_variants_list = applescript.command_to_python_list(command)

    primary_variant = co.Variant(primary_variants_list[0])
    # applescript.display_dialog(primary_variant)

    # get pre_crop_orientation_value then reset orientation
    pre_crop_orientation_value = co.get_adjustment_values(primary_variant.document, primary_variant.collection_id, primary_variant.id, 'orientation')[0]  # get first item in list
    orientation_value = co.set_adjustment_value(primary_variant.document, primary_variant.collection_id, primary_variant.id, 'orientation', '0')[0]  # set first item in list

    # crop_box data in form of [center_x, center_y, width, height]
    crop_box_from_primary_variant = co.get_crop_box(primary_variant.document, primary_variant.collection_id, primary_variant.id)
    width, height = float(crop_box_from_primary_variant[2]), float(crop_box_from_primary_variant[3])
    # applescript.display_dialog(f'width: {width}\nheight: {height}')

    # reset orientation to orignal value
    if pre_crop_orientation_value != orientation_value:
        post_crop_orientation_value = co.set_adjustment_value(primary_variant.document, primary_variant.collection_id, primary_variant.id, 'orientation', pre_crop_orientation_value)[0]  # get first item in list

    # # set height and width first variant in selected variants list
    # variant = co.Variant(selected_variants_list[0])
    # command = co.command_stub + [f'{co.tell_co20} to tell its document "{variant.document}" to tell its collection id "{variant.collection_id}" to set crop_box to crop of variant id "{variant.id}"', 'return image_dimensions']
    # crop_box = applescript.command_to_python_list(command)
    # applescript.display_dialog(image_dimensions)
    # width, height = float(image_dimensions[0]), float(image_dimensions[1])

    number_of_selected_variants = len(selected_variants_list)

    # reset crop/rotation on selected image starting with the 2nd image
    for index, selected_variant in enumerate(selected_variants_list):
        if index > 0 and index % 3 == 0:
            stop_script_path = hot_folder_directory_path.joinpath('ERROR.ERROR')
            if stop_script_path.exists():
                applescript.display_dialog(f'Error file exists: {stop_script_path}\nEnding Script')
                break
        # if the selected_variant is the primary variant then SKIP IT
        elif selected_variant == primary_variants_list[0]:
            continue
        time_autocrop_start = time.perf_counter()
        variant = co.Variant(selected_variant)
        applescript.display_notification(f'Processing {variant.image_name}\nVariant # {index+1}/{number_of_selected_variants}')
        # applescript.display_dialog(f'document: {variant.document}\nvariant id: {variant.id}')

        rotation_value = co.get_adjustment_values(variant.document, variant.collection_id, variant.id, 'rotation')[0]  # get first item in list
        flip_value = co.get_adjustment_values(variant.document, variant.collection_id, variant.id, 'flip')
        crop_box = co.get_crop_box(variant.document, variant.collection_id, variant.id)
        pre_crop_orientation_value = co.get_adjustment_values(variant.document, variant.collection_id, variant.id, 'orientation')[0]  # get first item in list
        # applescript.display_dialog(f'rotation before: {rotation_value}\nflip before: {flip_value}\ncrop before: {crop_box}')

        # reset orientation, flip, rotation, and crop
        orientation_value = co.set_adjustment_value(variant.document, variant.collection_id, variant.id, 'orientation', '0')[0]  # set first item in list
        flip_value = variant.reset_flip()
        rotation_value = variant.reset_rotation()
        crop_box = variant.reset_crop()  # is this an incorrect method?

        # applescript.display_dialog(f'rotation after reset: {rotation_value}\nflip after: {flip_value}\ncrop after reset: {crop_box}')

        # for right now . . . just output and crop single image then we'll work on faster batching later
        output_location = variant.output_with_recipe(autocrop_recipe_name)
        # applescript.display_dialog(output_location)
        output_path = Path(output_location)

        selected_variant_dict = {}

        # add variant info and output_path to dictionary to add to dataframe_rows_list
        # for row in input_rows:
        #
        #         dict1 = {}
        #         # get input row in dictionary format
        #         # key = col_name
        #         dict1.update(blah..)
        #
        #         rows_list.append(dict1)
        #
        # df = pd.DataFrame(dataframe_rows_list)

        # add data to dictionary file
        selected_variant_dict.update({'image_path': str(output_path)})
        selected_variant_dict.update({'image_name': variant.image_name})
        selected_variant_dict.update({'variant': selected_variant})
        selected_variant_dict.update({'pixel_padding': 0})
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
            capture_one_crop_data = otsu_autocrop(output_path, pixel_padding=0)


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

                # set crop data for Capture One; crop_box data in form of [center_x, center_y, width, height]
                autocrop_box = capture_one_crop_data[1:]
                autocrop_center_x, autocrop_center_y = autocrop_box[:2]
                autocrop_box = [autocrop_center_x, autocrop_center_y, width, height]

                # set rotation angle
                autocrop_rotation_angle = capture_one_crop_data[0]

                # crop image
                autocrop_box = co.set_crop_box(variant.document, variant.collection_id, variant.id, autocrop_box)
                rotation_value = co.set_adjustment_value(variant.document, variant.collection_id, variant.id, 'rotation', autocrop_rotation_angle)[0]  # get first item in list

                # if width and height of new crop box are correct then set star rating to 3 as assumed successful
                width_after_cropping, height_after_cropping = autocrop_box[2:4]
                # applescript.display_dialog(f'width type: {type(width)}\nwidth after cropping: {type(width_after_cropping)}')
                # applescript.display_dialog(f'width: {width}\nwidth after cropping: {width_after_cropping}')
                # applescript.display_dialog(f'height: {height}\nheight after cropping: {height_after_cropping}')
                if float(width_after_cropping) == width and float(height_after_cropping) == height:
                    # set image rating to 3 in Capture One
                    variant.set_star_rating(3)

            elif capture_one_crop_data is None:
                autocrop_rotation_angle = capture_one_crop_data
                autocrop_box = capture_one_crop_data

            # reset orientation to original value
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



        # add dictionary to dataframe rows list
        # dataframe_rows_list.append(selected_variant_dict)



        # if output_path.is_file():
        #
        #     # kmeans AutoCrop
        #     # instantiate image
        #     scan = NegativeScan(output_path)
        #
        #     # set autocrop_height
        #     autocrop_height = scan.image_cv2.shape[0]  # numpy arrays: height, width, channels
        #
        #     # get binarized image
        #     threshold = scan.threshold_kmeans()
        #
        #     # get contours
        #     contours = find_contours(threshold)
        #
        #     # get rect, x, y, angle
        #     rect, angle = find_external_rectangle(contours)
        #
        #     capture_one_crop_data = get_capture_one_coordinates(rect, angle, autocrop_height)
        #
        #     # AppleScript needs list as single string
        #     applescript.display_dialog(f'crop data: {capture_one_crop_data}')
        # else:
        #     applescript.display_dialog('No image to process')

    # use applescript process with list or text file of variants to output with autocrop recipe
    # which also means it doesn't matter what recipe is selected so delect those actions above

    # create dataframe
    # to_process_dataframe = pd.DataFrame(dataframe_rows_list, columns=['image_name', 'image_path','variant', 'pixel_padding'])

    # write processed_dictionary to text to autocrop using WatchDog?
    # hot_file_name = 'autocrop_jpg'
    # count = 1
    # hot_file_output_path = hot_folder_directory_path.joinpath(f'{hot_file_name}_{str(count).zfill(8)}.csv')
    # while hot_file_output_path.is_file():
    #     count += 1
    #     hot_file_output_path = hot_folder_directory_path.joinpath(f'{hot_file_name}_{str(count).zfill(8)}.csv')
    # to_process_dataframe.to_csv(hot_file_output_path, index=False)

    # add all
    applescript.display_dialog(end_message)
