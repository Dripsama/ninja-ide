# -*- coding: utf-8 -*-
#
# This file is part of NINJA-IDE (http://ninja-ide.org).
#
# NINJA-IDE is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NINJA-IDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NINJA-IDE; If not, see <http://www.gnu.org/licenses/>.


from __future__ import absolute_import

from sys import builtin_module_names
from pkgutil import iter_modules

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QSpinBox
from PyQt4.QtGui import QGroupBox
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide.tools import introspection


LIST_OF_PY_CHECKERS_COMMENTS = (
    'flake8:noqa', 'isort:skip', 'isort:skip_file', 'lint:disable',
    'lint:enable', 'lint:ok', 'noqa', 'pyflakes:ignore', 'pylint:disable',
    'pylint:enable', 'pragma: no cover', 'silence pyflakes')


class FromImportDialog(QDialog):
    """From Import dialog class."""

    def __init__(self, editorWidget, parent=None):
        QDialog.__init__(self, parent, Qt.Dialog)
        self.setWindowTitle('from ... import ...')
        self._editorWidget = editorWidget
        self.setMinimumSize(606, 90)

        source = self._editorWidget.get_text()
        source = source.encode(self._editorWidget.encoding)
        self._imports = introspection.obtain_imports(source)

        self._imports_names = list(self._imports["imports"].keys())
        self._imports_names += [imp for imp in self._imports['fromImports']]
        self._froms = [self._imports['fromImports'][imp]['module']
                       for imp in self._imports['fromImports']]
        self._froms += builtin_module_names
        self._froms += [module_name[1] for module_name in iter_modules()]
        self._froms = tuple(sorted(set(self._froms)))

        group = QGroupBox(self)
        hbox = QGridLayout(group)
        hbox.addWidget(QLabel('from'), 0, 0)
        self._lineFrom, self._insertAt = QLineEdit(self), QSpinBox(self)
        self._completer = QCompleter(self._froms)
        self._lineFrom.setCompleter(self._completer)
        self._lineFrom.setPlaceholderText("module")
        self._insertAt.setRange(0, 999)
        self._insertAt.setValue(
            self._editorWidget.textCursor().blockNumber() + 1)
        hbox.addWidget(self._lineFrom, 0, 1)
        hbox.addWidget(QLabel('import'), 0, 2)
        self._lineImport, self._asImport = QLineEdit(self), QLineEdit(self)
        self._completerImport = QCompleter(self._imports_names)
        self._lineImport.setCompleter(self._completerImport)
        self._lineImport.setPlaceholderText("object")
        self._asImport.setPlaceholderText("object_name")
        self._lineComment = QLineEdit(self)
        self._lineComment.setPlaceholderText("lint:ok")
        self._lineComment.setCompleter(QCompleter(LIST_OF_PY_CHECKERS_COMMENTS))
        hbox.addWidget(self._lineImport, 0, 3)
        hbox.addWidget(QLabel('as'), 0, 4)
        hbox.addWidget(self._asImport, 0, 5)
        hbox.addWidget(QLabel(translations.TR_INSERT_AT_LINE), 1, 0)
        hbox.addWidget(self._insertAt, 1, 1)
        hbox.addWidget(QLabel(translations.TR_WITH_COMMENT), 1, 2)
        hbox.addWidget(self._lineComment, 1, 3)
        self._btnAdd = QPushButton(translations.TR_ADD, self)
        hbox.addWidget(self._btnAdd, 1, 5)

        self.connect(self._lineImport, SIGNAL("returnPressed()"),
                     self._add_import)
        self.connect(self._btnAdd, SIGNAL("clicked()"),
                     self._add_import)

    def _add_import(self):
        """Get From item and Import item and add the import on the code."""
        fromItem = self._lineFrom.text().strip()  # from FOO
        importItem = self._lineImport.text().strip()  # import BAR
        asItem = self._asImport.text().strip()  # as FOO_BAR
        importComment = self._lineComment.text().strip()  # lint:ok or something
        cursor = self._editorWidget.textCursor()
        cursor.movePosition(abs(self._insertAt.value() - 2))
        cursor.movePosition(QTextCursor.EndOfLine)
        if fromItem:
            importLine = '\nfrom {0} import {1}'.format(fromItem, importItem)
        else:
            importLine = '\nimport {0}'.format(importItem)
        if asItem:
            importLine += " as " + asItem
        if importComment:
            importLine += "  # " + importComment
        cursor.insertText(importLine)
        self.close()
