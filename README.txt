MySQL/MariaDB Importer Plugin

This plugin was built with the Plugin Builder in QGIS.

Please make sure the MySQL Python extensions are installed! Otherwise the plugin
will give an error message about a missing "MySQLdb" module.

Once installed there will be a button with a seal (MariaDB icon) and a menu
item under Database to access the one-form plugin. Just enter the details
of the server, username, password and the database, which you should create
using any MySQL management tool beforehand as the plugin does not create the
database yet (I am woking on it).

Then choose the file to import and press OK. Depending on the size of the file
it can take a while, but no progress is shown, only the WAIT cursor. (I am
working on it). Shapefiles and OSM files work well but, really any file that
ogr2ogr can read can be imported. So make sure ogr2ogr is installed with
QGIS.

ENJOY!

Git location: https://github.com/immoblecher/qgis-plugin-mysqlimport

Git revision : $Format:%H$
