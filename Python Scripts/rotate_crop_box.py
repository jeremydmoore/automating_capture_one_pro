# ============ imports ============ #
import applescript
import argparse
import capture_one_pro_20 as co
from pathlib import Path

# ============ variables ============ #
angles = ['clockwise', 'counter-clockwise']
# ============ run script ============ #
if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--angle", required=True, help="angle to rotate crop box")
    arg_parser.add_argument("--degrees", required=True, help="Number of degrees to rotate the crop box")
    arg_parser.add_argument("--concatenate", required=False, help="Put anything here to add the inputted degrees to the current rotation value")
    args = vars(arg_parser.parse_args())

    # set angle to lower case and get degrees as a float
    angle = args["angle"].lower()
    degrees = float(args["degrees"])

    if angle == 'counter-clockwise':
        # rotation should be negative
        degrees = -degrees


    # get list of selected variants to process
    selected_variants_list = co.get_selected_variants()
    number_of_selected_variants = len(selected_variants_list)
    #applescript.display_notification(f'Rotating {number_of_selected_variants} VARIANTS {degrees} {angle}')

    for index, selected_variant in enumerate(selected_variants_list):
        degrees_to_rotate = 0
        variant = co.Variant(selected_variant)
        pre_rotation_list = co.get_adjustment_values(variant.document, variant.collection_id, variant.id, 'rotation')
        degrees_pre_rotated = pre_rotation_list[0]



        if args["concatenate"]:
            degrees_to_rotate = float(degrees_pre_rotated) + degrees
        else:
            degrees_to_rotate = degrees

        post_rotation_list = co.set_adjustment_value(variant.document, variant.collection_id, variant.id, 'rotation', str(degrees_to_rotate))
        degrees_post_rotated = post_rotation_list[0]

    # applescript.display_notification(f'Rotated {number_of_selected_variants} VARIANTS {angle}')
