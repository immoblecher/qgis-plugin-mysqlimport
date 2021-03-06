# -*- coding: utf-8 -*-
"""
/***************************************************************************
 mysqlimport
                                 A QGIS plugin
 Import data into MySQL/MariaDB
                              -------------------
        begin                : 2016-10-17
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Immo Blecher
        email                : immo@blecher.co.za
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from mysql_import_dialog import mysqlimportDialog
import os.path, subprocess, MySQLdb
from qgis.gui import QgsMessageBar
from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsProjectionSelectionWidget

class mysqlimport:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
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
            'mysqlimport_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&MySQL Importer')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'mysqlimport')
        self.toolbar.setObjectName(u'mysqlimport')
        

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
        return QCoreApplication.translate('mysqlimport', message)


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
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = mysqlimportDialog()

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
            self.iface.addPluginToDatabaseMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/mysqlimport/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Import data into MySQL/MariaDB'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.dlg.toolButton.clicked.connect(self.selectFile)
        self.dlg.testButton.clicked.connect(self.testConnection)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&MySQL Importer'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    # Define Openfile Dialog
    def selectFile(self):
        self.dlg.button_box.button(QDialogButtonBox.Ok).setEnabled(False)          
        self.dlg.lineEditFile.setText(QFileDialog.getOpenFileName(self.dlg, 'Open file', '', "All files (*.*)"))
        if self.dlg.lineEditFile.text() > '':
            self.dlg.button_box.button(QDialogButtonBox.Ok).setEnabled(True)

    # Define Test Connection button function
    def testConnection(self):
        dbhost = self.dlg.lineEditHost.text()
        dbuser = self.dlg.lineEditUsername.text()
        dbpasswd = self.dlg.lineEditPassword.text()
        dbport = int(self.dlg.lineEditPort.text())
        dbschema = self.dlg.lineEditDB.text()
        try:
            testdb = MySQLdb.connect(host=dbhost, port=dbport, user=dbuser, passwd=dbpasswd, db=dbschema)
            testdb.close();
            self.iface.messageBar().pushMessage("Information:", "Connection to database successful.")
        except MySQLdb.Error:
            self.iface.messageBar().pushMessage("Error:", "Could not connect to database with these parameters! Please check your settings and try again.", level=QgsMessageBar.CRITICAL)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.dlg.mQgsProjectionSelectionWidget.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            cursor = QCursor()
            cursor.setShape(Qt.WaitCursor)
            QApplication.instance().setOverrideCursor(cursor)
            dbhost = self.dlg.lineEditHost.text()
            dbuser = self.dlg.lineEditUsername.text()
            dbpasswd = self.dlg.lineEditPassword.text()
            dbport = int(self.dlg.lineEditPort.text())
            dbschema = self.dlg.lineEditDB.text()
            loadfile = self.dlg.lineEditFile.text()
            crs = QgsCoordinateReferenceSystem.authid(self.dlg.mQgsProjectionSelectionWidget.crs())
            os.chdir(os.path.dirname(os.path.abspath(loadfile)))
            fname = os.path.basename(loadfile) 
            try:
                thisdb = MySQLdb.connect(host=dbhost, port=dbport, user=dbuser, passwd=dbpasswd, db=dbschema)
                command = 'ogr2ogr -f "MySQL" MYSQL:"' + dbschema + ',host=' + dbhost + ',user=' + dbuser + ',password=' + dbpasswd + ',port=' + str(dbport) + '" -a_srs "' + crs + '" -lco engine=MYISAM "' + fname + '"'
                subprocess.check_call(command, shell=True)
            except MySQLdb.Error:
                QApplication.instance().restoreOverrideCursor()
                self.iface.messageBar().pushMessage("Error:", "Could not connect to database with these parameters! Please check your settings and try again. Nothing has been imported.", level=QgsMessageBar.CRITICAL)
            finally:
                thisdb.close()
                self.dlg.lineEditFile.clear()
                QApplication.instance().restoreOverrideCursor()
                QMessageBox.information(self.iface.mainWindow(), "MySQL/MariaDB Import", "The file " + fname + " has been imported successfully.")

