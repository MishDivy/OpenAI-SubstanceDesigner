from lib import utils
from pathlib import Path
import importlib
import sd
from sd.tools import export

importlib.reload(utils)

UI_DIR = Path(__file__).parent.parent / 'ui'
ETC_DIR = Path(__file__).parent.parent / 'etc'
RESOURCES_DIR = Path(__file__).parent.parent / 'images'


class API:
    def __init__(self, context) -> None:
        self._context = context
        self.setup()

        self.toolbar_ui_dir = UI_DIR
        self.toolbar_etc_dir = ETC_DIR
        self.resources_dir = RESOURCES_DIR

        self.resource_folder = None

        self.__temp_out_nodes = []

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

    def check_unique_output_node_name(self, unique_name: str = 'ai_temp_internal_use_1') -> str:
        for out_node in self.graph.getOutputNodes():
            if out_node.getIdentifier() == unique_name:
                version = int(unique_name.split('_')[-1])
                unique_name = unique_name.replace(
                    str(version), str(version + 1))
                self.check_unique_output_node_name(unique_name)
        return unique_name

    @staticmethod
    def set_identifier(node, value: str) -> None:
        for prop in node.getProperties(sd.api.sdproperty.SDPropertyCategory.Input):
            if prop.getLabel() == 'Identifier':
                node.setPropertyValue(
                    prop, sd.api.sdvaluestring.SDValueString.sNew(value))

    def set_RGBA_on_output_node(self, node) -> None:
        for prop in node.getProperties(sd.api.sdproperty.SDPropertyCategory.Annotation):
            if prop.getLabel() == 'Format':
                node.setPropertyValue(
                    prop, sd.api.sdvalueint.SDValueInt.sNew(1))

    def create_output_node(self, node=None):
        self.refresh_active_graph()
        out_node = self.graph.newNode('sbs::compositing::output')
        self.__temp_out_nodes.append(out_node)
        self.set_RGBA_on_output_node(out_node)
        self.set_identifier(out_node, self.check_unique_output_node_name())
        if node is not None:
            out_prop = None
            for prop in node.getProperties(sd.api.sdproperty.SDPropertyCategory.Output):
                if prop.getLabel() == 'Output':
                    out_prop = prop
            if out_prop:
                node.newPropertyConnectionFromId(
                    out_prop.getId(), out_node, 'inputNodeOutput')
            else:
                utils.logger.error(
                    f'Cannot connect output node to {node.getDefinition().getLabel()}')
        return out_node

    def export_outputs(self, folder: Path = None) -> None:
        if folder is None:
            folder = self.resources_dir / 'temp'
        export.exportSDGraphOutputs(self.graph, str(folder))

    def get_last_exported_images(self, num: int, folder: Path = None) -> list[Path]:
        if folder is None:
            folder = self.resources_dir / 'temp'
        all_names = []
        for file in folder.iterdir():
            all_names.append(str(file))
        all_names.sort()
        string_paths = all_names[(len(all_names) - num):]
        selected_paths = [Path(i) for i in string_paths]
        return selected_paths

    def export_selected_nodes(self) -> list[Path]:
        nodes = self.ui_mgr.getCurrentGraphSelectedNodes()
        for node in nodes:
            self.create_output_node(node)
        self.export_outputs()
        files = self.get_last_exported_images(len(nodes))
        self.clean_output_nodes()
        return files

    def clean_output_nodes(self) -> None:
        for node in self.__temp_out_nodes:
            self.graph.deleteNode(node)
        self.__temp_out_nodes.clear()
