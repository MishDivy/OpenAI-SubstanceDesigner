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

        action = self.addAction(QtGui.QIcon(
            str(self.api.toolbar_ui_dir / 'play_button.png')), '')
        action.setToolTip(
            'Set the prompt for image generation.')
        action.triggered.connect(self.on_clicked)

        self.entry_box = QtWidgets.QLineEdit()
        self.entry_box.setObjectName('prompt')
        self.entry_box.setText(
            'Orange british short hair cat with a pumpkin head')
        self.addWidget(self.entry_box)

    def on_clicked(self) -> None:
        utils.logger.info('Button Pressed!')
        url = open_ai_helper.generate_image(self.entry_box.text())
        file = self.api.resources_dir / 'ai.png'
        file = open_ai_helper.check_file_name(file)
        if file.is_file():
            file.unlink()
        if not url:
            return
        url.download_image(file)

        if (file.is_file):
            self.api.refresh_active_graph()
            bitmap_node = self.api.graph.newNode('sbs::compositing::bitmap')

            resource = sd.api.sdresourcebitmap.SDResourceBitmap.sNewFromFile(self.api.graph.getPackage(),
                                                                             str(file),
                                                                             sd.api.sdresource.EmbedMethod.Linked)
            resource_url = resource.getUrl()
            for prop in bitmap_node.getProperties(sd.api.sdproperty.SDPropertyCategory.Input):
                if prop.getLabel() == 'PKG Resource Path':
                    bitmap_node.setPropertyValue(
                        prop, sd.api.sdvaluestring.SDValueString.sNew(resource_url))

    def create_file_browser(self) -> None:
        file_name = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Select JSON File', '', 'JSON File (*.json)')
        if file_name:
            if file_name[0] is not None and file_name[0] != '':
                self.api.json_file = file_name[0]
                self.write_json_path_to_disk()
                self.set_json_file_path_from_disk()
                print(f'filename is : {file_name[0]}')
