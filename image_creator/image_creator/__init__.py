import os
import sys
import sd
from PySide2 import QtGui

if not os.path.normpath(os.path.dirname(os.getcwd())) in sys.path:
    sys.path.append(os.path.normpath(os.path.dirname(os.getcwd())))

import importlib
from lib import open_ai_helper, utils, helper_api, toolbar_gui

importlib.reload(open_ai_helper)
importlib.reload(utils)
importlib.reload(helper_api)
importlib.reload(toolbar_gui)


# Global Objects
API = helper_api.API(sd.getContext())


def add_json_injector_to_toolbar(graph_view_id) -> None:
    API.ui_mgr.addToolbarToGraphView(
        graph_view_id,
        toolbar_gui.OpenAIToolbar(API),
        icon=QtGui.QIcon(str(API.toolbar_ui_dir / 'openai_logo.png')),
        tooltip='OpenAIToolbar'
    )


def initializeSDPlugin():
    API.on_graph_view_created_callback_id = API.ui_mgr.registerGraphViewCreatedCallback(
        add_json_injector_to_toolbar)


def uninitializeSDPlugin() -> None:
    API.ui_mgr.unregisterCallback(API.on_graph_view_created_callback_id)
