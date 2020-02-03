# ============ imports ============ #
import applescript
import capture_one_pro_12 as co
from pathlib import Path

# ============ variables ============ #
begin_message = f'Begin - Python - {Path(__file__).name}'
end_message = f'End - Python - {Path(__file__).name}'

all_variants = []
horizontal_variants = []
vertical_variants = []
widths = []
heights = []

# ============ run script ============ #
if __name__ == '__main__':

    applescript.display_dialog(begin_message)

    # get list of selected variants to process
    selected_variants_list = co.get_selected_variants()

    number_of_selected_variants = len(selected_variants_list)

    # process selected variants
    for index, selected_variant in enumerate(selected_variants_list):

        # instantiate co.Variant class with current selected variant
        variant = co.Variant(selected_variant)
        if variant.image_name not in all_variants:
            if variant.width not in widths:
                widths.append(variant.width)
            if variant.height not in heights:
                heights.append(variant.height)

            if variant.height != variant.width:
                if variant.orientation == 'horizontal':
                    horizontal_variants.append(variant.image_name)
                elif variant.orientation == 'vertical':
                    vertical_variants.append(variant.image_name)
            else:
                vertical_variants.append(variant.image_name)
            all_variants.append(variant.image_name)

        applescript.display_notification(f'Processed {variant.image_name}\nVariant {index+1} of {number_of_selected_variants}')

    number_of_horizontal_variants = len(horizontal_variants)
    number_of_vertical_variants = len(vertical_variants)
    if number_of_horizontal_variants > number_of_vertical_variants:
        book_orientation = 'horizontal'
    else:
        book_orientation = 'vertical'

    if len(widths) > 1:
        if len(widths) == 2:
            if widths[0] == heights[1]:  # then correct size, we just have both orientations
                pass
            else:  # too many widths!
                applescript.display_dialog(f'Too many widths: {widths}')
                raise ValueError()

        if len(heights) > 1:
            if len(heights) == 2:
                if heights[0] == widths[1]:  # then correct size, we just have both orientations
                    pass
                else:  # too many heights!
                    applescript.display_dialog(f'Too many heights: {heights}')
                    raise ValueError()

    if book_orientation == 'horizontal':  # then use longer width and shorter height
        width = max(widths)
        height = min(widths)
    else:
        width = min(widths)
        height = max(heights)

    applescript.display_dialog(f'Total images: {number_of_selected_variants}\n\tHorizontal images: {number_of_horizontal_variants}\n\tVertical images: {number_of_vertical_variants}\nBook orientation: {book_orientation}\n\tWidth: {width}\n\tHeight: {height}')
