import re
import base64
import urllib.request
import urllib.parse
import easyocr

__author__ = 'kcastanedat'

# Global variables
URL = 'http://challenge01.root-me.org/programmation/ch8/'
PATH_IMAGES = r'images'
PATH_PAGES = r'pages'


class Captcha:
    """Class that contains the methods to cache the page"""

    def __init__(self):
        self.count = 0
        self.continue_loop = True
        self.reader = easyocr.Reader(['en'])

    def captchame(self):
        """Method that instantiates the other methods"""
        try:
            while self.continue_loop:
                self.count += 1
                self.response = self.get_url()
                # create str for search in page initial html
                self.image_captcha = r'data:image/png;base64,(.*)" /><br><br>'
                self.create_local_file(
                    'initial_request', self.response)
                # search str of image in html with regular expresions
                self.result = re.search(self.image_captcha, self.response)
                # result obtained from the process, decoding from base64 to utf-8
                self.result = self.result.group(1)
                self.result = base64.b64decode(self.result)
                # save image in local
                self.file_handle = open(f'{PATH_IMAGES}/captcha.png', 'wb')
                self.file_handle.write(self.result)
                self.file_handle.close
                # call image, extract text and clean
                self.file_handle = open(f'{PATH_IMAGES}/captcha.png', 'rb')
                self.result = self.reader.readtext(
                    f'{PATH_IMAGES}/captcha.png')
                self.file_handle.close
                self.result = self.clean_text(self.result)
                # build data for the form
                self.data = self.build_data_form(self.result)
                self.response = self.get_url(self.data)
                # save news requests to the page with text sent in the form
                self.create_local_file(
                    f'new_request_{self.count}', self.response)
                # stop the loop when the page's captcha has been successfully passed
                self.continue_loop = self.page_ok(self.response)
        except Exception as error:
            print(error)

    @classmethod
    def get_url(cls, custom_request=None):
        """
        Allow request in the URL
        @custom_request: object that retrieves form and header data with
                        referenced previous page
        """
        cls.html = urllib.request.urlopen(
            custom_request if custom_request else URL)
        cls.html = cls.html.read()
        return cls.html.decode('utf-8')

    @classmethod
    def create_local_file(cls, file_name, contents):
        """
        Allow create local file
        @file_name: str, parameter for the file name
        @contents: any, parameter for the contents to save
        """
        cls.file_handle = open(f'{PATH_PAGES}/{file_name}.html', 'w')
        cls.file_handle.write(contents)
        cls.file_handle.close

    @classmethod
    def clean_text(cls, text):
        """apply cleanup to text"""
        cls.clean = {
            '\n': '',
            ' ': '',
            ',': '',
            '\'': '',
            '“': '',
            '.': '',
            '-': '',
            ')': 'j',
            '‘': '',
            ':': '',
            '~': '',
            '°': '',
            '’': '',
            '¥': 'Y',
            ';': '',
            '>': '',
            '”': '',
            '"': '',
            '»': '',
            'é': '',
            '*': ''
        }
        cls.text = text
        cls.text = cls.text[0][1]
        for key, value in cls.clean.items():
            cls.text = cls.text.replace(key, value)
        return cls.text

    @classmethod
    def build_data_form(cls, text):
        """Allow build the data for the form"""
        cls.post_data = urllib.parse.urlencode({'cametu': text})
        return urllib.request.Request(URL, cls.post_data.encode('ascii'),
                                      {'Referer': URL}, method='POST')

    @classmethod
    def page_ok(cls, page):
        """Validate if the captcha passed successfully"""
        if 'Failed' in page or 'Too late' in page:
            return True
        else:
            return False
