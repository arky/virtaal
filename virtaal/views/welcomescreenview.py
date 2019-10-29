#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008-2011 Zuza Software Foundation
# Copyright 2013 F Wolff
#
# This file is part of Virtaal.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import, print_function, unicode_literals

from gi.repository import Gtk
from gi.repository.GObject import idle_add

from virtaal.common.pan_app import get_abs_data_filename, ui_language
from virtaal.views.widgets.welcomescreen import WelcomeScreen
from .baseview import BaseView


class WelcomeScreenView(BaseView):
    """Manages the welcome screen widget."""

    PARENT_VBOX_POSITION = 2
    """Index of the welcome screen in the main VBox."""

    # INITIALIZERS #
    def __init__(self, controller):
        self.controller = controller
        gui = self.load_builder_file(["virtaal", "virtaal.ui"], root='WelcomeScreen', domain="virtaal")
        self.widget = WelcomeScreen(gui)
        self.parent_widget = self.controller.main_controller.view.gui.get_object('vbox_main')

        self.set_banner()
        self.widget.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.widget.connect('button-clicked', self._on_button_clicked)

    def set_banner(self):
        if ui_language == "ar":
            self.widget.set_banner_image(get_abs_data_filename(['virtaal', 'welcome_screen_banner_ar.png']))
            return
        if self.widget.get_direction() == Gtk.TextDirection.RTL:
            self.widget.set_banner_image(get_abs_data_filename(['virtaal', 'welcome_screen_banner_rtl.png']))
        else:
            self.widget.set_banner_image(get_abs_data_filename(['virtaal', 'welcome_screen_banner.png']))


    # METHODS #
    def hide(self):
        self.widget.hide()
        if self.widget.get_parent() is self.parent_widget:
            self.parent_widget.remove(self.widget)

    def show(self):
        if not self.widget.get_parent():
            self.parent_widget.add(self.widget)
        else:
            self.widget.reparent(self.parent_widget)
        self.parent_widget.child_set_property(self.widget, 'position', self.PARENT_VBOX_POSITION)
        self.parent_widget.child_set_property(self.widget, 'expand', True)

        self.widget.show()

        def calculate_width():
            txt = self.widget.widgets['txt_features']
            expander = txt.get_parent().get_parent()

            screenwidth = self.widget.get_allocation().width
            col1 = self.widget.widgets['buttons']['open'].get_parent()
            width_col1 = col1.get_allocation().width
            if width_col1 > 0.7 * screenwidth:
                width_col1 = int(0.7 * screenwidth)
                col1.set_size_request(width_col1, -1)
                
            maxwidth = 1.8 * width_col1
            # Preliminary width is the whole_screen - width_col1 - 30
            # The "50" above is just to make sure we don't go under the
            # vertical scroll bar (if it is showing).
            width = screenwidth - width_col1 - 50

            if width > maxwidth:
                width = int(maxwidth)

            txt.set_size_request(width, -1)
        idle_add(calculate_width)

    def update_recent_buttons(self, items):
        # if there are no items (maybe failure in xbel), hide the whole widget
        if not items:
            self.widget.gui.get_object("frame_recent").hide()
        else:
            self.widget.gui.get_object("frame_recent").show_all()

        buttons = [
            self.widget.widgets['buttons']['recent' + str(i)] for i in range(1, self.controller.MAX_RECENT+1)
        ]
        markup = '<span underline="single">%(name)s</span>'

        iconfile = get_abs_data_filename(['icons', 'hicolor', '24x24', 'mimetypes', 'x-translation.png'])
        for i in range(len(items)):
            buttons[i].get_child().get_children()[0].set_from_file(iconfile)
            name = items[i]['name']
            name = name.replace('&', '&amp;')
            name = name.replace('<', '&lt;')
            buttons[i].get_child().get_children()[1].set_markup(markup % {'name': name})
            buttons[i].set_tooltip_text(items[i]['uri'])
            buttons[i].props.visible = True
        for i in range(len(items), 5):
            buttons[i].props.visible = False


    # EVENT HANDLERS #
    def _on_button_clicked(self, button, name):
        """This method basically delegates button clicks to controller actions."""
        if name == 'open':
            self.controller.open_file()
        elif name.startswith('recent'):
            n = int(name[len('recent'):])
            self.controller.open_recent(n)
        elif name == 'tutorial':
            self.controller.open_tutorial()
        elif name == 'cheatsheet':
            self.controller.open_cheatsheat()
        else:
            self.controller.try_open_link(name)
