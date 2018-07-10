# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SplitLine
                                 A QGIS plugin
 Split contour and river stream line based on elevation
                             -------------------
        begin                : 2018-07-08
        copyright            : (C) 2018 by Faizal
        email                : faizalprbw@gmail.com
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
    """Load SplitLine class from file SplitLine.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .split_line import SplitLine
    return SplitLine(iface)
