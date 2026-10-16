import config


PKG = config.APP_PACKAGE


class ImageFlipLocators:
    """画面翻转页面定位器"""

    # 页面标题与返回
    TITLE = ('xpath', "//*[@text='画面翻转']")
    BTN_BACK = ('id', f'{PKG}:id/left_img')

    # 选项行与选中状态
    OPTION_UNFLIPPED = ('id', f'{PKG}:id/imageUnFlipRel')
    CHECKBOX_UNFLIPPED = ('id', f'{PKG}:id/imageUnFlipCB')
    OPTION_FLIPPED = ('id', f'{PKG}:id/imageFlipRel')
    CHECKBOX_FLIPPED = ('id', f'{PKG}:id/imageFlipCB')