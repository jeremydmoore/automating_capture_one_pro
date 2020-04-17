# NOTE: this is unneeded if you can send a hotkey from a keyboard command instead

# ============ imports ============ #
import applescript
import capture_one_pro_20 as co
from pathlib import Path

# ============ run script ============ #
if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--rating", required=True, help="Number of stars to rate an image")
    args = vars(arg_parser.parse_args())

    command = co.command_stub + [f'{co.tell_co} to set primary_variant to (get primary variant)', 'return primary_variant']
    primary_variants_list = applescript.command_to_python_list(command)
    primary_variant = co.Variant(primary_variants_list[0])

    star_rating = int(args["rating"])

    if star_rating in [0, 1, 2, 3, 4, 5]:
        primary_variant.set_star_rating(star_rating)
