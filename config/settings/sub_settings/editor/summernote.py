import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from utils.os.file_path_name_gen import date_upload_to_for_summernote

from  config.settings.base import INSTALLED_APPS

INSTALLED_APPS += [
    "django_summernote",
]


#Summer note
#click jacking setting
X_FRAME_OPTIONS = "SAMEORIGIN"

SUMMERNOTE_CONFIG = {
    # Using SummernoteWidget - iframe mode, default
    'iframe': True,

    # Or, you can set it as False to use SummernoteInplaceWidget by default - no iframe mode
    # In this case, you have to load Bootstrap/jQuery stuff by manually.
    # Use this when you're already using Bootstraip/jQuery based themes.
    #'iframe': False,

    # You can put custom Summernote settings
    'summernote': {
        # As an example, using Summernote Air-mode
        'airMode': False,

        # Change editor size
        'width': '100%',
        'height': '480',

        # Use proper language setting automatically (default)
        'lang': None,

        # Or, set editor language/locale forcely
        'lang': 'ko-KR',

        # You can also add custom settings for external plugins
        #'print': { 'stylesheetUrl': '/some_static_folder/printable.css', },
    },

    # Need authentication while uploading attachments.
    'attachment_require_authentication': True,

    'attachment_filesize_limit': 5 * 1024 * 1024,
    # Set `upload_to` function for attachments.
    #'attachment_upload_to': my_custom_upload_to_func(),
    'attachment_upload_to': date_upload_to_for_summernote,

    # Set custom storage class for attachments.
    #'attachment_storage_class': 'my.custom.storage.class.name',

    # Set custom model for attachments (default: 'django_summernote.Attachment')
    #'attachment_model': 'my.custom.attachment.model', # must inherit 'django_summernote.AbstractAttachment'

    # You can disable attachment feature.
    #'disable_attachment': False,

    # Set `True` to return attachment paths in absolute URIs.
    #'attachment_absolute_uri': False,

    # You can add custom css/js for SummernoteWidget.
    'css': (
    ),
    'js': (
    ),

    # You can also add custom css/js for SummernoteInplaceWidget.
    # !!! Be sure to put {{ form.media }} in template before initiate summernote.
    'css_for_inplace': (
    ),
    'js_for_inplace': (
    ),

    # Codemirror as codeview
    # If any codemirror settings are defined, it will include codemirror files automatically.
    # 'css': (
    #     '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/theme/monokai.min.css',
    # ),
    # 'codemirror': {
    #     'mode': 'htmlmixed',
    #     'lineNumbers': 'true',

    #     # You have to include theme file in 'css' or 'css_for_inplace' before using it.
    #     'theme': 'monokai',
    # },

    # Lazy initialize
    # If you want to initialize summernote at the bottom of page, set this as True
    # and call `initSummernote()` on your page.
    'lazy': True,

    # To use external plugins,
    # Include them within `css` and `js`.
    # 'js': {
    #     '/some_static_folder/summernote-ext-print.js',
    #     '//somewhere_in_internet/summernote-plugin-name.js',
    # },
}