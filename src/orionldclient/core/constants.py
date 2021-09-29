from datetime import timedelta

from orionldclient import __version__

from enum import Enum, unique

Version = str


@unique
class Vendor(Enum):
    ORIONLD = "Orion-LD"
    SCORPIO = "Scorpio"
    STELLIO = "Stellio"
    UNKNOWN = None


@unique
class AttrsFormat(Enum):
    NORMALIZED = "normalized"
    KEYVALUES = "keyValues"
    VALUES = "values"


@unique
class LogLevel(Enum):
    NONE = "NONE"
    FATAL = "FATAL"
    ERROR = "ERROR"
    WARN = "WARN"
    INFO = "INFO"
    DEBUG = "DEBUG"


UA = f"python-orion-client v{__version__}"

NGSILD_PATH = "ngsi-ld"
NGSILD_VERSION = "v1"
NGSILD_BASEPATH = f"{NGSILD_PATH}/{NGSILD_VERSION}"

NGSILD_DEFAULT_PORT_ORIONLD = 1026
NGSILD_DEFAULT_PORT_SCORPIO = 9090
NGSILD_DEFAULT_PORT_STELLIO = 8080
NGSILD_DEFAULT_PORT = NGSILD_DEFAULT_PORT_ORIONLD

# endpoints MUST begin with a slash
# endpoints MUST NOT end with a slash
ENDPOINT_STATUS = "version"
ENDPOINT_ADMIN = "admin"
ENDPOINT_LOG = f"{ENDPOINT_ADMIN}/log"
ENDPOINT_ENTITIES = f"{NGSILD_BASEPATH}/entities"
ENDPOINT_SUBSCRIPTIONS = f"{NGSILD_BASEPATH}/subscriptions"


PAGINATION_LIMIT_MAX = 1000  # pagination (max. allowed by Orion-LD)

DEFAULT_ATTR_FORMAT = None  # Let Orion default value => AttrsFormat.NORMALIZED
DEFAULT_LOGLEVEL = LogLevel.WARN

WRITE_MODE_UPSERT = True
WRITE_MODE_IGNORE = False
DEFAULT_WRITE_MODE = WRITE_MODE_UPSERT

NOW = None
