import applescript
import capture_one_pro_12 as co


class CaptureOneVariant():
    """
    This is my docstring
    """
    def __init__(self, selected_variant):
        self.info = selected_variant

        # self.info in form of 'variant id {self.id} of collection id
        # {self.collection_id} of document {self.document}'
        # assumes collection id and document do NOT have spaces in them!
        info_list = self.info.split(' ')
        self.id = info_list[2]
        self.collection_id = info_list[6]
        self.document = info_list[-1]
        # get name of image to be processed
        command = command_stub + [f'{tell_co12} to tell its document "{self.document}" to tell its collection id "{self.collection_id}" to set image_name to name of variant id "{self.id}"', 'return image_name']
        self.image_name = applescript.command_to_python_list(command)[0]  # get first item in list
