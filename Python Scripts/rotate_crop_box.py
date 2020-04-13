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

    print(f'Rotate crop box {args["degrees"]} degrees {args["angle"]}.')

    command = co.command_stub + [f'{co.tell_co20} to set primary_variant to (get primary variant)', 'return primary_variant']
    primary_variants_list = applescript.command_to_python_list(command)

    primary_variant = co.Variant(primary_variants_list[0])

    pre_rotation_list = co.get_adjustment_values(primary_variant.document, primary_variant.collection_id, primary_variant.id, 'rotation')
    degrees_pre_rotated = pre_rotation_list[0]

    print(f'Pre-rotation of {primary_variant.id}: {degrees_pre_rotated}')

    # set angle to lower case and get degrees as a float
    angle = args["angle"].lower()
    degrees = float(args["degrees"])

    if angle == 'counter-clockwise':
        # rotation should be negative
        degrees = -degrees

    if args["concatenate"]:
        degrees = float(degrees_pre_rotated) + degrees

    post_rotation_list = co.set_adjustment_value(primary_variant.document, primary_variant.collection_id, primary_variant.id, 'rotation', str(degrees))
    degrees_post_rotated = post_rotation_list[0]

    print(f'Post-rotation of {primary_variant.id}: {degrees_post_rotated}')
