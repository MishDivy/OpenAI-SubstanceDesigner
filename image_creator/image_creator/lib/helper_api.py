from lib import utils
from pathlib import Path
import importlib

importlib.reload(utils)

UI_DIR = Path(__file__).parent.parent / 'ui'
ETC_DIR = Path(__file__).parent.parent / 'etc'
RESOURCES_DIR = Path(r'D:\FunToys\OpenAI-SD\images')


class API:
    def __init__(self, context) -> None:
        self._context = context
        self.setup()

        self.toolbar_ui_dir = UI_DIR
        self.toolbar_etc_dir = ETC_DIR
        self.resources_dir = RESOURCES_DIR

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context):
        self._context = context
        self.setup()

    def setup(self):
        self.application = self._context.getSDApplication()
        self.ui_mgr = self.application.getQtForPythonUIMgr()
        self.refresh_active_graph()
        self.main_window = self.ui_mgr.getMainWindow()

    def validate_graph(self) -> None:
        if self.graph is None:
            utils.logger.warning('No Active Graph Found!')
        else:
            utils.logger.info(
                f'Active graph found: {self.graph.getIdentifier()}')

    def refresh_active_graph(self) -> None:
        self.graph = self.ui_mgr.getCurrentGraph()
        self.validate_graph()
