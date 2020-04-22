r"""
Evennia settings file.

The available options are found in the default settings file found
here:

/home/mud/tidebreak-mud/evennia/evennia/settings_default.py

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "Barx"
GAME_SLOGAN = "Can someone tell me if this is a MUD or a MUSH?"
TELNET_PORTS = [32767]
START_LOCATION = "#21"
DEFAULT_HOME = "#21"
INLINEFUNC_ENABLED = True
WEBSERVER_ENABLED = False
AMP_PORT = 32766

GAME_INDEX_ENABLED = True
GAME_INDEX_LISTING = \
{   'game_name': 'Barx',
    'game_status': 'launched',
    'game_website': '',
    'listing_contact': 'sage@limitlessinteractive.com',
    'long_description': "It's ruff out there for a dog.",
    'short_description': 'A Shaggy Dog Story',
    'telnet_hostname': 'mud.invertedspectra.com',
    'telnet_port': '32767'
}

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")


try:
    # Created by the `evennia connections` wizard
    from .connection_settings import *
except ImportError:
    pass
