from PySide2 import QtWidgets, QtGui
import sd
from pathlib import Path
import importlib
from lib import helper_api, utils, open_ai_helper

importlib.reload(helper_api)
importlib.reload(utils)
importlib.reload(open_ai_helper)


class OpenAIToolbar(QtWidgets.QToolBar):
    def __init__(self, api: helper_api.API) -> None:
        super(OpenAIToolbar, self).__init__(parent=api.main_window)

        self.setObjectName('OpenAI.Toolbar')
        self.api = api

        # Generate Image from Prompt
        action = self.addAction(QtGui.QIcon(
            str(self.api.toolbar_ui_dir / 'play_button.png')), '')
        action.setToolTip(
            'Set the prompt for image generation.')
        action.triggered.connect(self.on_clicked)

        # Generate Image from node
        variations_action = self.addAction(QtGui.QIcon(
            str(self.api.toolbar_ui_dir / 'variations_button.png')), '')
        variations_action.setToolTip(
            'Create variations of the selected node.')
        variations_action.triggered.connect(self.create_variations)

        # Generate Image from mask and node
        mask_action = self.addAction(QtGui.QIcon(
            str(self.api.toolbar_ui_dir / 'mask_button.png')), '')
        mask_action.setToolTip(
            'Create variations using selected node with a mask node.')
        mask_action.triggered.connect(self.create_variations_using_mask)

        self.entry_box = QtWidgets.QLineEdit()
        self.entry_box.setObjectName('prompt')
        self.entry_box.setText(
            'Orange british short hair cat with a pumpkin head')
        self.addWidget(self.entry_box)

    def create_bitmap_from_file(self, file: Path) -> None:

        utils.wait_for_substance_engine(
            lambda file: file.is_file(), '', f'File: {file} not found!', file=file)

        self.api.refresh_active_graph()
        bitmap_node = self.api.graph.newNode('sbs::compositing::bitmap')
        if self.api.resource_folder is None:
            self.api.resource_folder = sd.api.sdresourcefolder.SDResourceFolder.sNew(
                self.api.graph.getPackage())
            self.api.resource_folder.setIdentifier('AI_Images')
        resource = sd.api.sdresourcebitmap.SDResourceBitmap.sNewFromFile(self.api.resource_folder,
                                                                         str(file),
                                                                         sd.api.sdresource.EmbedMethod.Linked)
        resource_url = resource.getUrl()
        for prop in bitmap_node.getProperties(sd.api.sdproperty.SDPropertyCategory.Input):
            if prop.getLabel() == 'PKG Resource Path':
                bitmap_node.setPropertyValue(
                    prop, sd.api.sdvaluestring.SDValueString.sNew(resource_url))

    def on_clicked(self) -> None:
        utils.logger.info('Button Pressed!')
        url = open_ai_helper.generate_image(self.get_text_prompt())
        file = self.api.resources_dir / 'ai.png'
        file = open_ai_helper.check_file_name(file)
        if file.is_file():
            file.unlink()
        if not url:
            return
        url.download_image(file)
        self.create_bitmap_from_file(file)

    def get_text_prompt(self) -> str:
        return self.entry_box.text()

    def create_file_browser(self) -> None:
        file_name = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Select JSON File', '', 'JSON File (*.json)')
        if file_name:
            if file_name[0] is not None and file_name[0] != '':
                self.api.json_file = file_name[0]
                self.write_json_path_to_disk()
                self.set_json_file_path_from_disk()
                print(f'filename is : {file_name[0]}')

    def create_variations(self) -> None:
        images = self.api.export_selected_nodes()
        for image in images:
            utils.wait_for_substance_engine(
                lambda image: image.is_file(), '', 'Cannot export the node to image.', image=image)
            urls = open_ai_helper.generate_variations(image)
            file = self.api.resources_dir / 'ai.png'
            file = open_ai_helper.check_file_name(file)
            if file.is_file():
                file.unlink()
            if not urls:
                return
            urls[0].download_image(file)
            self.create_bitmap_from_file(file)

    def create_variations_using_mask(self) -> None:
        images = self.api.export_selected_nodes()
        main_image = images[0]
        mask = images[1]

        for count, image in enumerate(images):
            if count > 1:
                break
            utils.wait_for_substance_engine(
                lambda image: image.is_file(), '', 'Cannot export the node to image.', image=image)

        urls = open_ai_helper.edit_image(main_image, mask, self.get_text_prompt())
        file = self.api.resources_dir / 'ai.png'
        file = open_ai_helper.check_file_name(file)
        if file.is_file():
            file.unlink()
        if not urls:
            return
        urls[0].download_image(file)
        self.create_bitmap_from_file(file)
