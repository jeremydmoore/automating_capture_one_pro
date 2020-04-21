# ============ imports ============ #
# standard library
import argparse
from pathlib import Path

# 3rd party libraries
import pandas as pd

# my modules
import applescript
import capture_one_pro_20 as co

# ============ variables ============= #
begin_message = f'Begin - Python - {Path(__file__).name}'
end_message = f'End - Python - {Path(__file__).name}'

fieldnames = ['image_name',
              'image_path',
              'variant',
              'orientation',
              'width',
              'height',
              ]

# moved these variables into check_sizes() function
# variant_list = []
# horizontal_variant_list = []
# vertical_variant_list = []
# width_list = []
# height_list = []

# ============ functions ============= #
def get_image_dict(selected_variant, cover=False):
    variant = co.Variant(selected_variant)
    image_dict = {'image_name' : variant.image_name,
                  'variant' : selected_variant,
                  'orientation' : variant.orientation,
                  'width' : variant.width,
                  'height' : variant.height,
                  'cover' : cover
                  }
    return image_dict

def get_cover_list(selected_variant_list):

    # get possible covers: first 2 and last 2 images
    front_cover = selected_variant_list[0]
    front_inside_cover = selected_variant_list[1]
    back_inside_cover = selected_variant_list[-2]
    back_cover = selected_variant_list[-1]

    # create list of covers and return
    cover_list = [front_cover, front_inside_cover, back_inside_cover, back_cover]
    return cover_list

def get_selected_variant_dataframe(selected_variant_list):
    '''
    Return a DataFrame containing the information necessary to process variants
    by size

    NOTE: by default reports information on first/last leafs as possible covers
    '''
    # list of the image dictionaries we'll return as a DataFrame
    image_dict_list = []

    cover_list = get_cover_list(selected_variant_list)
    number_of_selected_variants = len(selected_variant_list)

    for index, selected_variant in enumerate(selected_variant_list):

        # get info from
        if selected_variant in cover_list:
            image_dict = get_image_dict(selected_variant, cover=True)
        else:
            image_dict = get_image_dict(selected_variant, cover=False)

        image_dict_list.append(image_dict)

        applescript.display_notification(f'Processed {image_dict["image_name"]}\nVariant {index+1} of {number_of_selected_variants}')

    # create DataFrame from list of dictionaries and return
    selected_variant_df = pd.DataFrame(image_dict_list)
    return selected_variant_df

def validate_dimension_lists(width_list, height_list):
    number_of_widths = len(width_list)
    number_of_heights = len(height_list)

    if number_of_widths > 1:  # we have too many widths
        if number_of_widths == 2:  # may have vertical and horizontal images
            if width_list[0] == height_list[1] and width_list[1] == height_list[0]:
                # odds are we have horizontal & vertical images
                pass
        # too many widths!

    # if len(width_list) > 1:
    #     if len(width_list) == 2:
    #         if width_list[0] == height_list[1]:  # then correct size, we just have both orientations
    #             pass
    #         else:  # too many width_list!
    #             applescript.display_dialog(f'Too many in width_list: {width_list}')
    #             raise ValueError()
    #
    #     if len(height_list) > 1:
    #         if len(height_list) == 2:
    #             if height_list[0] == width_list[1]:  # then correct size, we just have both orientations
    #                 pass
    #             else:  # too many height_list!
    #                 applescript.display_dialog(f'Too many height_list: {height_list}')
    #                 raise ValueError()


# ============ run script ============ #
if __name__ == '__main__':

    # construct the argument parser and parse the arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-c", "--covers", required=False, help="Assume the first 2 and last 2 images are covers and process separately")
    args = vars(arg_parser.parse_args())

    applescript.display_dialog(begin_message)

    # get list of selected variants to process, then get our DataFrame
    selected_variant_list = co.get_selected_variants()
    applescript.display_notification('Starting to get DataFrame')
    selected_variant_df = get_selected_variant_dataframe(selected_variant_list)
    applescript.display_notification('Got DataFrame')

    # asssumes first 2 images and last 2 images are covers
    cover_width_list = selected_variant_df[selected_variant_df['cover'] == True].width.unique()
    cover_height_list = selected_variant_df[selected_variant_df['cover'] == True].height.unique()

    # assume all other interior images are pages
    page_width_list = selected_variant_df[selected_variant_df['cover'] == False].width.unique()
    page_height_list = selected_variant_df[selected_variant_df['cover'] == False].height.unique()

    # get a list of all of our dimension lists
    dimension_list_list = [cover_width_list, cover_height_list, page_width_list, page_height_list]
    error_list = [x for x in dimension_list_list if len(x) > 1]

    applescript.display_dialog(f'cover_width_list: {cover_width_list}\ncover_height_list: {cover_height_list}')
    applescript.display_dialog(f'page_width_list: {page_width_list}\npage_height_list: {page_height_list}')

    # # process selected variants
    # for index, selected_variant in enumerate(selected_variant_list):
    #
    #     # instantiate co.Variant class with current selected variant
    #     variant = co.Variant(selected_variant)
    #     if variant.image_name not in variant_list:
    #         if variant.width not in width_list:
    #             width_list.append(variant.width)
    #         if variant.height not in height_list:
    #             height_list.append(variant.height)
    #
    #         if variant.height != variant.width:
    #             if variant.orientation == 'horizontal':
    #                 horizontal_variant_list.append(variant.image_name)
    #             elif variant.orientation == 'vertical':
    #                 vertical_variant_list.append(variant.image_name)
    #         else:
    #             vertical_variant_list.append(variant.image_name)
    #         variant_list.append(variant.image_name)
    #
    #     applescript.display_notification(f'Processed {variant.image_name}\nVariant {index+1} of {number_of_selected_variants}')
    #
    # number_of_horizontal_variant_list = len(horizontal_variant_list)
    # number_of_vertical_variant_list = len(vertical_variant_list)
    # if number_of_horizontal_variant_list > number_of_vertical_variant_list:
    #     book_orientation = 'horizontal'
    # else:
    #     book_orientation = 'vertical'
    #
    # if len(width_list) > 1:
    #     if len(width_list) == 2:
    #         if width_list[0] == height_list[1]:  # then correct size, we just have both orientations
    #             pass
    #         else:  # too many width_list!
    #             applescript.display_dialog(f'Too many in width_list: {width_list}')
    #             raise ValueError()
    #
    #     if len(height_list) > 1:
    #         if len(height_list) == 2:
    #             if height_list[0] == width_list[1]:  # then correct size, we just have both orientations
    #                 pass
    #             else:  # too many height_list!
    #                 applescript.display_dialog(f'Too many height_list: {height_list}')
    #                 raise ValueError()
    #
    # if book_orientation == 'horizontal':  # then use longer width and shorter height
    #     width = max(width_list)
    #     height = min(width_list)
    # else:
    #     width = min(width_list)
    #     height = max(height_list)
    #
    # applescript.display_dialog(f'Total images: {number_of_selected_variants}\n\tHorizontal images: {number_of_horizontal_variant_list}\n\tVertical images: {number_of_vertical_variant_list}\nBook orientation: {book_orientation}\n\tWidth: {width}\n\tHeight: {height}')
