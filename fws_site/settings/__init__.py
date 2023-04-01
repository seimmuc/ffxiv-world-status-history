import os

from .base import *

_FWSWEB_ENVIRONMENT_VAR_NAME = 'FWSWEB_ENVIRONMENT'

fwsweb_environment = os.getenv(_FWSWEB_ENVIRONMENT_VAR_NAME, default='production').lower()

if fwsweb_environment in ('dev', 'development'):
    from .dev import *
elif fwsweb_environment in ('prod', 'production'):
    from .prod import *
    try:
        from .prod_secrets import *
    except ImportError:
        pass
elif fwsweb_environment in ('test', 'testing'):
    from .test import *
else:
    raise RuntimeError(f'Unknown environment "{fwsweb_environment}", '
                       f'please change or set [{_FWSWEB_ENVIRONMENT_VAR_NAME}] environment variable')
