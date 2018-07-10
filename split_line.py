# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SplitLine
                                 A QGIS plugin
 Split contour and river stream line based on elevation
                              -------------------
        begin                : 2018-07-08
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Faizal
        email                : faizalprbw@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from split_line_dialog import SplitLineDialog
import os.path
from qgis.gui import QgsMessageBar
from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsFields,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsMapLayerRegistry,
    QGis,
    QgsProject,
    QgsLayerTreeLayer
)
import processing
from osgeo import ogr, osr


class SplitLine:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SplitLine_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Split Line')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SplitLine')
        self.toolbar.setObjectName(u'SplitLine')

        # Declare custom variable
        self.layers_dict = {-1 : None}

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SplitLine', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        # Create the dialog (after translation) and keep reference
        self.dlg = SplitLineDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        # Declare Custom Action
        # Get all contour layer fields
        self.dlg.Contour_Layer.currentIndexChanged.connect(
            self.contour_combobox_onchange
        )
        # Set output directory path
        self.dlg.Browse_Output.clicked.connect(
            self.setup_output_path
        )

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SplitLine/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Split Line'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Split Line'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def contour_combobox_onchange(self):
        """Contour combobox onchange"""
        self.dlg.Contour_Elev_Field.clear()
        contour_layer = self.layers_dict[self.dlg.Contour_Layer.currentIndex()]
        field_names = [field.name() for field in contour_layer.pendingFields() if field.typeName() != 'String']
        self.dlg.Contour_Elev_Field.addItems(field_names)


    def setup_output_path(self):
        """Setup output directory path"""
        output_folder = QFileDialog.getExistingDirectory(
            self.dlg,
            ""
        )
        self.dlg.Output_Directory.setText(output_folder)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Clear all input line
        self.dlg.Contour_Layer.clear()
        self.dlg.River_Layer.clear()
        self.dlg.Contour_Elev_Field.clear()
        self.dlg.Output_Directory.clear()
        # Load all active layers
        layers = self.iface.legendInterface().layers()
        idx = 0
        for layer in layers:
            try:
                layer.wkbType()
                if layer.wkbType() == 2:
                    self.layers_dict.update({idx: layer})
                    self.dlg.Contour_Layer.addItem(layer.name(), layer)
                    self.dlg.River_Layer.addItem(layer.name(), layer)
                idx += 1
            except:
                pass
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # pass
            # Initial Input Parameter
            contour_layer = self.layers_dict[self.dlg.Contour_Layer.currentIndex()]
            contour_elev_field = self.dlg.Contour_Elev_Field.currentText()
            river_layer = self.layers_dict[self.dlg.River_Layer.currentIndex()]
            output_directory = self.dlg.Output_Directory.text()
            # Get data CRS
            contour_crs = contour_layer.crs().authid()
            river_crs = river_layer.crs().authid()
            if contour_crs == river_crs:
                shpdriver = ogr.GetDriverByName('ESRI Shapefile')
                # Intersect line
                output_point = os.path.join(output_directory, "point_of_intersect.shp")
                if os.path.exists(output_point):
                    shpdriver.DeleteDataSource(output_point)
                processing.runandload("qgis:lineintersections", contour_layer, river_layer, str(contour_elev_field), '', output_point)
                intersect_points_layer = QgsVectorLayer(output_point, 'point_of_intersect', 'ogr')
                # Split lines with lines
                output_split_lines = os.path.join(output_directory, "splited_lines.shp")
                if os.path.exists(output_split_lines):
                    shpdriver.DeleteDataSource(output_split_lines)
                processing.runalg('saga:splitlineswithlines', river_layer, contour_layer, 1, output_split_lines)
                splited_lines_layer = QgsVectorLayer(output_split_lines, 'splited_lines', 'ogr')
                # Join Attributes
                output_joint_lines = os.path.join(output_directory, "joint_lines.shp")
                if os.path.exists(output_joint_lines):
                    shpdriver.DeleteDataSource(output_joint_lines)
                processing.runalg("qgis:joinattributesbylocation", splited_lines_layer, intersect_points_layer, u'intersects', 0, 1, 'max,min', 0, output_joint_lines)
                joint_lines_layer = QgsVectorLayer(output_joint_lines, 'joint_lines', 'ogr')
                # Dissolve contour layers
                contour_dissolved = os.path.join(output_directory, "dissolved_contour.shp")
                processing.runalg("qgis:dissolve", contour_layer, "false", str(contour_elev_field), contour_dissolved)
                contour_dissolved_layer = QgsVectorLayer(contour_dissolved, 'contour_dissolved', 'ogr')
                # Dissolve river layers
                river_dissolved = os.path.join(output_directory, "dissolved_river.shp")
                processing.runalg("qgis:dissolve", joint_lines_layer, "false", 'min' + str(contour_elev_field), river_dissolved)
                river_dissolved_layer = QgsVectorLayer(river_dissolved, 'river_dissolved', 'ogr')
                # Generate Poliylines Vector for every features
                root = QgsProject.instance().layerTreeRoot()
                contourGroup = root.addGroup("Contour Group")
                riverGroup = root.addGroup("River Group")
                # Contour
                dataSource_contour = ogr.Open(contour_dissolved_layer.dataProvider().dataSourceUri().split("|")[0], 0)
                layerContour = dataSource_contour.GetLayer()
                n = 0
                for feature in layerContour:
                    n += 1
                    geom = feature.GetGeometryRef()
                    contour_directory = os.path.join(output_directory, 'contour')
                    if not os.path.exists(contour_directory):
                        os.mkdir(contour_directory)
                    output_vector_contour = os.path.join(contour_directory, str(int(feature.GetField(contour_elev_field))) + 'b.shp')
                    output_prj_contour = os.path.join(contour_directory, str(int(feature.GetField(contour_elev_field))) + 'b.prj')
                    data_source_contour = shpdriver.CreateDataSource(output_vector_contour)
                    srs = osr.SpatialReference()
                    srs.ImportFromEPSG(int(contour_dissolved_layer.crs().authid().split(":")[1]))
                    srs.MorphToESRI()
                    prj_file = open(output_prj_contour, 'w')
                    prj_file.write(srs.ExportToWkt())
                    prj_file.close()
                    output_vector_contour = output_vector_contour.encode('utf-8')
                    layer_contour = data_source_contour.CreateLayer(output_vector_contour, srs, ogr.wkbLineString)
                    layer_contour.CreateField(ogr.FieldDefn("ELEV", ogr.OFTReal))
                    fet = ogr.Feature(layer_contour.GetLayerDefn())
                    fet.SetField("ELEV", feature.GetField(contour_elev_field))
                    fet.SetGeometry(geom)
                    layer_contour.CreateFeature(fet)
                    data_source_contour.Destroy()
                    if self.dlg.autoAdd.isChecked():
                        vectorLyr = QgsVectorLayer(output_vector_contour, str(int(feature.GetField(contour_elev_field))) + 'b' , "ogr")
                        contourGroup.insertChildNode(1,QgsLayerTreeLayer(vectorLyr))
                        QgsMapLayerRegistry.instance().addMapLayer(vectorLyr, False)
                dataSource_contour.Destroy()
                # River
                dataSource_river = ogr.Open(river_dissolved_layer.dataProvider().dataSourceUri().split("|")[0], 0)
                layerRiver = dataSource_river.GetLayer()
                n = 0
                for feature in layerRiver:
                    n += 1
                    geom = feature.GetGeometryRef()
                    river_directory = os.path.join(output_directory, 'river')
                    if not os.path.exists(river_directory):
                        os.mkdir(river_directory)
                    output_vector_river = os.path.join(river_directory, str(int(feature.GetField('min'+ contour_elev_field))) + 'a.shp')
                    output_prj_river = os.path.join(river_directory, str(int(feature.GetField('min'+ contour_elev_field))) + 'a.prj')
                    data_source_river = shpdriver.CreateDataSource(output_vector_river)
                    srs = osr.SpatialReference()
                    srs.ImportFromEPSG(int(river_dissolved_layer.crs().authid().split(":")[1]))
                    srs.MorphToESRI()
                    prj_file = open(output_prj_river, 'w')
                    prj_file.write(srs.ExportToWkt())
                    prj_file.close()
                    output_vector_river = output_vector_river.encode('utf-8')
                    layer_river = data_source_river.CreateLayer(output_vector_river, srs, ogr.wkbLineString)
                    layer_river.CreateField(ogr.FieldDefn("ELEV", ogr.OFTReal))
                    fet = ogr.Feature(layer_river.GetLayerDefn())
                    fet.SetField("ELEV", feature.GetField('min'+ contour_elev_field))
                    fet.SetGeometry(geom)
                    layer_river.CreateFeature(fet)
                    data_source_river.Destroy()
                    if self.dlg.autoAdd.isChecked():
                        vectorLyr = QgsVectorLayer(output_vector_river, str(int(feature.GetField('min'+ contour_elev_field))) + 'a' , "ogr")
                        riverGroup.insertChildNode(1,QgsLayerTreeLayer(vectorLyr))
                        QgsMapLayerRegistry.instance().addMapLayer(vectorLyr, False)
                dataSource_river.Destroy()
            else:
                raise Exception('Contour and river are not in the same Coordinate Reference System.')
