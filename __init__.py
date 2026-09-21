from .nanobanana_pro_node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = './js'

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

# Bundled independent API tasks; install() is idempotent across both plugins.
from .api_immediate import install as _install_immediate
_install_immediate()
