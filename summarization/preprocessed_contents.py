''' Class definition for Pre processed contents'''


class PreprocessedContents:
    def __init__(
            self,
            title_text,
            normal_text,
            media,
            embedded_content,
            quoted_content):
        self.title_text = title_text
        self.normal_text = normal_text
        self.media = media
        self.embedded_content = embedded_content
        self.quoted_content = quoted_content
