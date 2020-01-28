# ============ imports ============ #
import applescript
from pathlib import Path

# ============ variables ============ #
tell_co12 = 'Tell application "Capture One 12"'
command_stub = ['use AppleScript version "2.4"', 'use scripting additions']
scripts_dir_path = Path.home().joinpath('LIbrary', 'Scripts')
python_scripts_dir_path = scripts_dir_path.joinpath('Python Scripts')
applescript_scripts_dir_path = scripts_dir_path.joinpath('AppleScript Scripts')


# ============ functions ============ #
def run_applescript_script(script_name, args=None):
    script_path = applescript_scripts_dir_path.joinpath(script_name)
    python_list = applescript.script_to_python_list(script_path, args)
    return python_list


def disable_all_recipes():
    script_name = 'disable_all_recipes.scpt'
    script_path = applescript_scripts_dir_path.joinpath(script_name)
    all_recipes_list = applescript.script_to_python_list(script_path)
    return all_recipes_list


def enable_recipe(recipe_name):
    """
    Input (str): recipe_name to activate and set as current recipe

    Returns (list): info for processed variants in capture_one_pro_12
        [recipe_name, output_folder_path, output_extension]
    """
    script_name = 'enable_recipe.scpt'
    # if isinstance(recipe_names, list):  # there are multiple recipes to enable
        # for recipe_name in recipe_names:
    script_path = applescript_scripts_dir_path.joinpath(script_name)
    output_info_list = applescript.script_to_python_list(script_path, args=recipe_name)
    return output_info_list




def get_selected_variants():

    command = command_stub + [f'{tell_co12} to set selected_variants to (get selected variants)', 'return selected_variants']
    selected_variants_list = applescript.command_to_python_list(command)

    # if there are less than 2 items in the list and the first item is empty
    if len(selected_variants_list) < 2 and selected_variants_list[0] == '':
        applescript.display_dialog('No images selected, select at least 1 image and run again')
        selected_variants_list = None

    return selected_variants_list


# adjustment values
def set_adjustment_value(document, collection_id, variant_id, adjustment, value, value_is_quoted=True):

    # set adjustment to new value
    if value_is_quoted:
        value = f'"{value}"'
    command = command_stub + [f'{tell_co12} to tell its document "{document}" to tell its collection id "{collection_id}" to set {adjustment} of adjustments of variant id "{variant_id}" to {value}']
    applescript.process(command)

    # get adjustment values list and return
    adjustment_values = get_adjustment_values(document, collection_id, variant_id, adjustment)

    return adjustment_values

def get_adjustment_values(document, collection_id, variant_id, adjustment):

    command = command_stub + [f'{tell_co12} to tell its document "{document}" to tell its collection id "{collection_id}" to set adjustment_values to {adjustment} of adjustments of variant id "{variant_id}"', 'return adjustment_values']
    adjustment_values = applescript.command_to_python_list(command)

    return adjustment_values


# crop box -- crop isn't under adjustments
def get_crop_box(document, collection_id, variant_id):


    command = command_stub + [f'{tell_co12} to tell its document "{document}" to tell its collection id "{collection_id}" to set crop_box to crop of variant id "{variant_id}"', 'return crop_box']
    crop_box = applescript.command_to_python_list(command)

    return crop_box

def set_crop_box(document, collection_id, variant_id, crop_box):

    # crop_box is list in form [center_x, center_y, width, height]
    command = command_stub + [f'set center_x to ({crop_box[0]} as number)',
                              f'set center_y to ({crop_box[1]} as number)',
                              f'set width to ({crop_box[2]} as number)',
                              f'set height to ({crop_box[3]} as number)',
                              'set crop_box to {center_x, center_y, width, height}',
                              f'{tell_co12} to tell its document "{document}" to tell its collection id "{collection_id}" to set crop of variant id "{variant_id}" to crop_box'
                             ]
    applescript.process(command)
    crop_box = get_crop_box(document, collection_id, variant_id)

    return crop_box

# can be used for all non-adjustment values
# TODO: could do an if/then to identify where a value might be so the user doesn't have to specify
def get_value(document, collection_id, variant_id, value):
    command = command_stub + [f'{tell_co12} to tell its document "{document}" to tell its collection id "{collection_id}" to set current_value to {value} of variant id "{variant_id}"', 'return current_value']
    current_value = applescript.command_to_python_list(command)

    if isinstance(current_value, list) and len(current_value) == 1:
        current_value = current_value[0]  # just return the first and only item in the list

    return current_value

# document functions
def get_session_directory_path(document, posix=True):
    if posix:
        path_format = 'POSIX path of (get folder)'
    else:
        path_format = '(get folder)'
    command = command_stub + [f'{tell_co12} to tell its document "{document}" to set document_path to {path_format}', 'return document_path']
    session_directory_path = applescript.command_to_python_list(command)[0]
    return session_directory_path

# primary variant functions
def get_primary_variant():
    command = command_stub + [f'{tell_co12} to set primary_variant to (get primary variant)', 'return primary_variant']
    primary_variant = applescript.command_to_python_list(command)[0]
    return primary_variant

# primary variant functions
def get_primary_variant_id():
    command = command_stub + [f'{tell_co12} to set primary_variant_id to id of primary variant', 'return primary_variant_id']
    primary_variant_id = applescript.command_to_python_list(command)[0]
    return primary_variant_id

def get_primary_variant_document():
    command = command_stub + [f'{tell_co12} to set primary_variant_document to document of primary variant', 'return primary_variant_document']
    primary_variant_document = applescript.command_to_python_list(command)[0]
    return get_primary_variant_document

def get_primary_variant_collection_id():
    command = command_stub + [f'{tell_co12} to set primary_variant_collection_id to document of primary variant', 'return primary_variant_document']
    primary_variant_collection_id = applescript.command_to_python_list(command)[0]
    return primary_variant_collection_id

def set_variant_as_primary(document, collection_id, variant_id):
    command = command_stub + [f'{tell_co12} to set primary variant to variant {variant_id} of collection {collection_id} of document {document}']
    applescript.process(command)
    new_primary_variant_id = get_primary_variant_id()
    if variant_id != new_primary_variant_id:
        applescript.display_dialog(f'ERROR: new id {new_primary_variant_id} != wanted value {variant_id}')
    return

def do_i_have_to_reset_the_primary_variant(document, collection_id, variant_id):

    old_primary_variant_collection_id = get_primary_variant_collection_id()
    old_primary_variant_document = get_primary_variant_document()
    old_primary_variant_id = get_primary_variant_id()

    reset_variant_list = [False, old_primary_variant_document, old_primary_variant_collection_id, old_primary_variant_id]

    # check if we need to change the variant or not
    if old_primary_variant_collection_id != collection_id or old_primary_variant_document != document or old_primary_variant_id != variant_id:
        set_variant_as_primary(document, collection_id, variant_id)
        reset_variant_list[0] = True

    return reset_variant_list


class Variant():

    def __init__(self, selected_variant):
        self.info = selected_variant

        # self.info in form of 'variant id {self.id} of collection id {self.collection_id} of document {self.document}'
        # assumes collection id and document do NOT have spaces in them!
        info_list = self.info.split(' ')
        self.id = info_list[2]
        self.collection_id = info_list[6]
        self.document = info_list[-1]
        # get name of image to be processed
        command = command_stub + [f'{tell_co12} to tell its document "{self.document}" to tell its collection id "{self.collection_id}" to set image_name to name of variant id "{self.id}"', 'return image_name']
        self.image_name = applescript.command_to_python_list(command)[0]  # get first item in list

        # reset_variant_list in form of [Boolean, old_primary_variant_document, old_primary_variant_id]
        # self.reset_variant_list = do_i_have_to_reset_the_primary_variant(self.document, self.collection_id, self.id)

    def display_info(self):
        applescript.display_dialog(self.info)
        applescript.display_dialog(f'self.variant_id: {self.id}\nself.collection_id: {self.collection_id}\nself.document: {self.document}')
        applescript.display_dialog(f'')

    def reset_flip(self):
        flip_values_list = set_adjustment_value(self.document, self.collection_id, self.id, 'flip', 'none', value_is_quoted=False)
        flip_value = flip_values_list[0]
        return flip_value

    def reset_rotation(self):
        rotation_values_list = set_adjustment_value(self.document, self.collection_id, self.id, 'rotation', '0.0')
        rotation_value = rotation_values_list[0]
        return rotation_value

    def reset_crop(self):

        # get image dimensions of the parent image to reset the crop
        command = command_stub + [f'{tell_co12} to tell its document "{self.document}" to tell its collection id "{self.collection_id}" to set image_dimensions to dimensions of parent image of variant id "{self.id}"']
        image_dimensions = applescript.command_to_python_list(command)

        width, height = int(image_dimensions[0]), int(image_dimensions[1])
        center_x = width / 2
        center_y = height / 2
        crop_box = [center_x, center_y, width, height]
        crop_box = set_crop_box(self.document, self.collection_id, self.id, crop_box)
        return crop_box

    def reset_primary_variant(self):
        # reset_variant_list in form of [Boolean, old_primary_variant_collection_id, old_primary_variant_document, old_primary_variant_id]
        if self.reset_variant_list is True:
            set_variant_as_primary(self.reset_variant_list[1], self.reset_variant_list[2], self.reset_variant_list[3])

    def set_star_rating(self, rating):
        """
        Set star rating of image to value {rating}

        {rating} can be an int with a value of 0 - 5 (inclusive)
        """
        # verify rating is a valid number, current number scale is 0 up through 5 stars
        valid_ratings = [0, 1, 2, 3, 4, 5]
        if rating not in valid_ratings:
            applescript.display_dialog(f'Rating of {rating} is not valid. Rating must be an integer from 0 - 5')
            raise ValueError

        # set AppleScript command & run it
        command = command_stub + [f'{tell_co12} to tell its document "{self.document}" to tell its collection id "{self.collection_id}" to set rating of variant id "{self.id}" to "{rating}"']
        applescript.process(command)

        # get rating value -- grab 1st item in returned list and get
        current_rating = get_value(self.document, self.collection_id, self.id, value='rating')
        self.rating = int(current_rating)

        if self.rating != rating:  # then the value wasn't updated correctly
            applescript.display_dialog(f'ERROR! self.rating "{self.rating}" is NOT equal to rating requested "{rating}"')
            raise ValueError

        return self.rating




    def output_with_recipe(self, process_recipe):
        # applescript.display_dialog(self.image_name)

        # get process_recipe's output location
        command = command_stub + [f'{tell_co12} to tell its document "{self.document}" to set recipe_output_folder to ((root folder location of current recipe as text) & (output sub folder of recipe "{process_recipe}"))',
                                  'set output_folder_posix to (quoted form of the POSIX path of recipe_output_folder)',
                                  'return output_folder_posix']
        output_folder_posix = applescript.command_to_python_list(command)[0]  # get first item in list
        # applescript.display_dialog(f'output_folder_posix: {output_folder_posix}')

        # get process recipe's file type
        ## TO DO

        # find all images that start with image_name in output_folder_path
        process_recipe_output_directory_path = Path(output_folder_posix.strip("'"))
        images_with_same_name_paths_list = list(process_recipe_output_directory_path.glob(f'{self.image_name}*'))
        # applescript.display_dialog(images_with_same_name_paths_list)

        if len(images_with_same_name_paths_list) > 1:
            applescript.display_dialog(f'More than 1 image named {self.image_name} at {process_recipe_output_directory_path}')
            return None
        else:  # delete image
            for image_path in images_with_same_name_paths_list:
                image_path.unlink()
        # set expected output file location
        ## NOTE: CURRENTLY HARD-CODED AS .jpg FILE!
        self.expected_output_path = Path(process_recipe_output_directory_path).joinpath(f'{self.image_name}.jpg')
        # applescript.display_dialog(f'expected_output_path: {expected_output_path}')

        if self.expected_output_path.is_file():
            applescript.display_dialog(f'ERROR image exists before output: {expected_output_path}')
        else:
            # process image with process_recipe
            command = command_stub + [f'{tell_co12} to tell its document "{self.document}" to tell its collection id "{self.collection_id}" to process variant id "{self.id}" recipe "{process_recipe}"']
            applescript.process(command)

            return self.expected_output_path

        # return path of processed image
        #command = command_stub + [f'{tell_co12}'
