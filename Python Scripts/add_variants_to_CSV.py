# ============ imports ============ #
import applescript
import capture_one_pro_20 as co
from pathlib import Path
import csv

# ============ variables ============ #
begin_message = f'Begin - Python - {Path(__file__).name}'
end_message = f'End - Python - {Path(__file__).name}'
autocrop_recipe_name = 'autocrop_jpg'

## csv information
hot_folder_directory_path = co.scripts_dir_path.joinpath('Hot Folder')
athletics_csv_path = hot_folder_directory_path.joinpath('athletics_programs.csv')
fieldnames = ['image_name', 'image_path', 'variant', 'pixel_padding']


# ============ run script ============ #
if __name__ == '__main__':

    # dataframe_rows_list = []
    if not athletics_csv_path.is_file():
        with open(athletics_csv_path, 'a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

    applescript.display_dialog(begin_message)

    # get list of selected variants to process
    selected_variants_list = co.get_selected_variants()

    # applescript.display_dialog(selected_variants_list)

    # get pixel padding input
    pixel_padding = applescript.get_user_input_int('pixel_padding', 25)
    # applescript.display_dialog(f'Pixel padding: {pixel_padding}')

    number_of_selected_variants = len(selected_variants_list)

    # reset crop/rotation on selected image
    for index, selected_variant in enumerate(selected_variants_list, start=1):
        variant = co.Variant(selected_variant)
        applescript.display_notification(f'Processing {variant.image_name}\nVariant # {index}/{number_of_selected_variants}')
        # applescript.display_dialog(f'document: {variant.document}\nvariant id: {variant.id}')

        rotation_value = co.get_adjustment_values(variant.document, variant.collection_id, variant.id, 'rotation')
        flip_value = co.get_adjustment_values(variant.document, variant.collection_id, variant.id, 'flip')
        crop_box = co.get_crop_box(variant.document, variant.collection_id, variant.id)
        # applescript.display_dialog(f'rotation before: {rotation_value}\nflip before: {flip_value}\ncrop before: {crop_box}')



        # reset flip, rotation, and crop
        rotation_value = variant.reset_rotation()
        flip_value = variant.reset_flip()
        crop_box = variant.reset_crop()  # this is probably incorrect and should just call some sort of AppleScript reset?
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
        selected_variant_dict.update({'pixel_padding': pixel_padding})
        # applescript.display_dialog(selected_variant_dict)

        # add dictionary to dataframe rows list
        # dataframe_rows_list.append(selected_variant_dict)
        with open(athletics_csv_path, 'a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow(selected_variant_dict)

        # if output_path.is_file():
        #
        #     # kmeans AutoCrop
        #     # instantiate image
        #     negative_scan = NegativeScan(output_path)
        #
        #     # set autocrop_height
        #     autocrop_height = negative_scan.image_cv2.shape[0]  # numpy arrays: height, width, channels
        #
        #     # get binarized image
        #     threshold = negative_scan.threshold_kmeans()
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
