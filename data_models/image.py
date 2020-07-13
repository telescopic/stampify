"""This class creates the object structure for Image content"""

from data_models.contents import ContentType, _Content


class Image(_Content):
    """This class creates Image object"""

    def __init__(self,
                 img_url,
                 img_height,
                 img_width,
                 is_gif,
                 img_caption=None,
                 img_title=None,
                 img_type=''):
        super(Image, self).__init__(ContentType.IMAGE)
        self.img_url = img_url
        self.img_caption = img_caption
        self.img_title = img_title
        self.img_type = img_type
        self.img_height = img_height
        self.img_width = img_width
        self.img_description_embedding = None
        self.img_attribute_embedding = None
        self.has_text_on_image = False
        self.image_colors = None
        self.is_gif = is_gif
