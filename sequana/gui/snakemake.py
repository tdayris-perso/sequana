# coding: utf-8
#
#  This file is part of Sequana software
#
#  Copyright (c) 2016 - Sequana Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#      Dimitri Desvillechabrol <dimitri.desvillechabrol@pasteur.fr>,
#          <d.desvillechabrol@gmail.com>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
"""Snakemake Dialog for the main GUI application"""
import multiprocessing

from sequana.gui.ui_snakemake import Ui_Snakemake
from PyQt5 import QtWidgets as QW
from PyQt5 import QtCore


class SnakemakeDialog(QW.QDialog):
    """ Widget to set up options of snakemake and launch pipeline. It provides
    a progress bar to know how your jobs work.
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.ui = Ui_Snakemake()
        self.ui.setupUi(self)
        self._application = "sequana_gui"
        self._section = "snakemake_dialog"
        self.read_settings()

        # Set maximum of local cores to be used
        cpu = multiprocessing.cpu_count()
        self.ui.snakemake_options_local_cores_value.setMaximum(cpu)

    def get_widgets(self, prefix):
        # identify names of the widget objects
        names = self._get_widget_names(prefix)

        # Get the objects themselves
        widgets = [getattr(self.ui, this) for this in names]

        # the double underescore __  is used i nplace or dash - in qt designer
        # because dash is not acceptable within the object name. so we must
        # replace it. We also strip the prefix and suffix (_value)
        names = [this.replace(prefix + "_", "") for this in names]
        names = [this.replace("__", "-") for this in names]
        names = [this.replace("_value", "") for this in names]

        options = []
        for name, widget in zip(names, widgets):
            options.append(SOptions(name, widget))
        return options

    def _get_options(self, prefix):
        options = []
        for widget in self.get_widgets(prefix):
            option = widget.get_option()
            if option:
                options.extend(option)
        return options

    def get_snakemake_local_options(self):
        """Return local snakemake parameters as list of strings"""
        return self._get_options("snakemake_options_local")

    def get_snakemake_cluster_options(self):
        """Return cluster-related snakemake parameters as list of strings"""
        return self._get_options("snakemake_options_cluster")

    def get_snakemake_general_options(self):
        """Return general snakemake parameters as list of strings"""
        return self._get_options("snakemake_options_general")

    def accept(self):
        self.write_settings()
        super().accept()

    def reject(self):
        self.read_settings()
        super().reject()

    def read_settings(self):
        settings = QtCore.QSettings(self._application, self._section)
        for key in settings.allKeys():
            value = settings.value(key)
            try:
                # This is required to skip the tab_position key/value
                this = getattr(self.ui, key)
            except:
                continue
            if isinstance(this, QW.QLineEdit):
                this.setText(value)
            elif isinstance(this, QW.QSpinBox):
                this.setValue(int(value))
            elif isinstance(this, QW.QCheckBox):
                if value in ['false']:
                    this.setChecked(False)
                else:
                    this.setChecked(True)
            else:
                print('could not handle : %s' % this)
        # The last tab position
        self._tab_pos = settings.value("tab_position", 0, type=int)
        self.ui.tabs.setCurrentIndex(self._tab_pos)

    def write_settings(self):
        settings = QtCore.QSettings(self._application, self._section)
        items = self.get_settings()
        for k,v in self.get_settings().items():
            settings.setValue(k, v)

    def _get_widget_names(self, prefix="snakemake_options"):
        names = [this for this in dir(self.ui) if this.startswith(prefix)]
        names = [this for this in names if this.endswith('_value')]
        return names

    def get_settings(self):
        # get all items to save in settings
        items = {}
        names = self._get_widget_names()
        for name in names:
            widget = getattr(self.ui, name)
            if isinstance(widget, QW.QLineEdit):
                value = widget.text()
            elif isinstance(widget, QW.QSpinBox):
                value = widget.value()
            elif isinstance(widget, QW.QCheckBox):
                value = widget.isChecked()
            else:
                raise NotImplementedError("for developers")
            items[name] = value
        items["tab_position"] = self.ui.tabs.currentIndex()
        return items


class SOptions(object):

    def __init__(self, name, widget):
        self.name = name
        self.widget = widget

    def _get_value(self):
        """Return a string"""
        if isinstance(self.widget, QW.QSpinBox):
            value = self.widget.text()
        elif isinstance(self.widget, QW.QLabel):
            value = self.widget.text()
        else:
            try:
                value = self.widget.text()
            except:
                print("unknown widget" + str(type(self.widget)))
                value = ""
        return value

    def get_option(self):
        """Return option and its value as a list

        An option may be without any value, but we still return a list

        e.G. ["--verbose"] or ["--cores", "2"]
        """
        if isinstance(self.widget, QW.QCheckBox):
            if self.widget.isChecked() is True:
                return ["--" + self.name]
        else:
            value = self._get_value()
            if value is None or value in ["", '', "''", '""']:
                return []
            else:
                return ["--" + self.name, value]

