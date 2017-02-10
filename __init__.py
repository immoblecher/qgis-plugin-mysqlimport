# -*- coding: utf-8 -*-
"""
/***************************************************************************
 mysqlimport
                                 A QGIS plugin
 Import spatial data into MySQL/MariaDB
                             -------------------
        begin                : 2016-10-17
        copyright            : (C) 2016 by Immo Blecher
        email                : immo@blecher.co.za
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load mysqlimport class from file mysqlimport.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .mysql_import import mysqlimport
    return mysqlimport(iface)
