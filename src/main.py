#!/usr/bin/env python3
"""DOVELA RIW - Terminal gráfica experimental para Linux."""

import os
import shutil
import subprocess
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")

from gi.repository import Gtk, Vte, GLib, Gdk, Pango


class RhynusTerminal(Gtk.Window):

    THEMES = {
        "Dovela Oscuro": ("#0B141B", "#E9E9D8", "#2EC889"),
        "Dovela Ámbar": ("#17140D", "#F1E4C6", "#F9A825"),
        "Dovela Azul": ("#0B1725", "#DCEEFF", "#38BDF8"),
        "Dovela Claro": ("#F7F9F6", "#1A2A2E", "#176F65"),
    }

    ANSI_PALETTES = {
        "Dovela Oscuro": [
            "#19242B", "#E67E80", "#72CFA0", "#E8C779",
            "#7DADE0", "#C59ADB", "#6ECFCB", "#D5DED9",
            "#53656E", "#FF9A9A", "#9AE6BB", "#F5DC96",
            "#A5C8F0", "#DBB6F0", "#95E5DF", "#FFFFFF",
        ],
        "Dovela Ámbar": [
            "#272119", "#D97967", "#9DBB79", "#E8B65C",
            "#8FAEC7", "#C6A0BD", "#86C1B5", "#E6D7BC",
            "#665744", "#F19B83", "#BED49A", "#FFD17C",
            "#B2C9DA", "#DFC1D5", "#A9D9CA", "#FFF4DF",
        ],
        "Dovela Azul": [
            "#172536", "#EF8190", "#77D3B4", "#E8C985",
            "#75B9F0", "#C4A4F0", "#70D0DF", "#D6E7F3",
            "#526A83", "#FFA3AE", "#9CE9CD", "#F5DFA5",
            "#A5D4FF", "#DCC4FF", "#9CEAF0", "#FFFFFF",
        ],
        "Dovela Claro": [
            "#28363A", "#B33F49", "#24795C", "#946200",
            "#2867A0", "#864B91", "#176F78", "#34454A",
            "#62757B", "#C4535B", "#31896A", "#A87916",
            "#397DB5", "#9A62A4", "#25828B", "#34454A",
        ],
    }


    def load_system_info(self):
        """Información real obtenida de Neofetch."""
        campos = {
            "Icons": "No disponible",
            "CPU": "No disponible",
            "GPU": "No disponible",
            "Memory": "No disponible",
        }

        try:
            resultado = subprocess.run(
                [
                    shutil.which("neofetch") or "neofetch",
                    "--stdout",
                    "--off",
                    "--color_blocks", "off",
                ],
                capture_output=True,
                text=True,
                timeout=8,
                check=False,
            )
            for linea in resultado.stdout.splitlines():
                linea = linea.strip()
                for clave in campos:
                    if linea.startswith(clave + ":"):
                        campos[clave] = linea.split(":", 1)[1].strip()
        except (OSError, subprocess.TimeoutExpired):
            pass

        return campos

    def apply_theme(self, name):
        background, foreground, accent = self.THEMES[name]

        def rgba(value):
            color = Gdk.RGBA()
            color.parse(value)
            return color

        bg_color = rgba(background)
        bg_color.alpha = 1.0 - (self.transparency_percent / 100.0)

        self.terminal.set_colors(
            rgba(foreground),
            bg_color,
            [rgba(value) for value in self.ANSI_PALETTES[name]]
        )
        self.terminal.set_color_cursor(rgba(accent))

        if hasattr(self, "glifo_imagen"):
            ruta_glifo = (
                self.glifo_claro
                if name == "Dovela Claro"
                else self.glifo_original
            )
            self.glifo_imagen.set_from_file(ruta_glifo)
        # Identidad visual GTK adaptada al tema seleccionado.
        css = """
        headerbar.dovela-header {
            background-image: none;
            background-color: %s;
            color: %s;
            border-color: %s;
        }

        headerbar.dovela-header label {
            color: %s;
        }

        box.dovela-toolbar {
            background-color: %s;
            color: %s;
        }

        box.dovela-toolbar label {
            color: %s;
        }

        box.dovela-toolbar combobox button {
            background-image: none;
            background-color: %s;
            color: %s;
            border-color: %s;
        }

        box.dovela-toolbar combobox button label {
            color: %s;
        }

        box.dovela-identity {
            background-color: %s;
            color: %s;
        }

        box.dovela-identity label {
            color: %s;
        }
        """ % (
            background, foreground, accent,
            foreground,
            background, foreground,
            foreground,
            background, foreground, accent,
            foreground,
            background, foreground, foreground
        )

        rgb = tuple(
            int(background[i:i + 2], 16)
            for i in (1, 3, 5)
        )
        opacidad = 1.0 - self.transparency_percent / 100.0
        fondo = "rgba(%d,%d,%d,%.2f)" % (*rgb, opacidad)

        css += """
        box.dovela-identity {
            background-color: %s;
        }
        frame.dovela-info {
            background-color: %s;
            border: 1px solid %s;
            border-radius: 8px;
        }
        frame.dovela-info label {
            color: %s;
        }
        """ % (fondo, fondo, accent, foreground)

        self.palette_label.set_markup(
            "".join(
                '<span background="%s">   </span>' % color
                for color in self.ANSI_PALETTES[name][:8]
            )
        )

        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode("utf-8"))

        if hasattr(self, "_theme_provider"):
            for widget in (self.header, self.toolbar, self.identity_panel, self.info_frame):
                widget.get_style_context().remove_provider(
                    self._theme_provider
                )

        for widget in (self.header, self.toolbar, self.identity_panel, self.info_frame):
            widget.get_style_context().add_provider(
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

        self._theme_provider = provider

        self.terminal.grab_focus()

    def on_theme_changed(self, combo):
        self.apply_theme(combo.get_active_text())

    def on_transparency_changed(self, scale):
        self.transparency_percent = int(scale.get_value())
        self.apply_theme(self.theme_selector.get_active_text())

    def __init__(self):
        super().__init__(title="DOVELA RIW · RTL v0.3 · Transparencia")

        self.set_default_size(950, 580)
        self.set_icon_from_file(
            str(Path(__file__).resolve().parent.parent / "assets/identity/v0.1/icons/dovela-256.png")
        )
        self.transparency_percent = 0

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is not None and screen.is_composited():
            self.set_visual(visual)

        # Cabecera corporativa nativa GTK3
        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.header.set_title("DOVELA RIW")
        self.header.set_subtitle("RTL v0.3 · Terminal LAB")
        self.header.get_style_context().add_class(
            "dovela-header"
        )
        self.set_titlebar(self.header)

        self.settings_button = Gtk.ToggleButton()
        self.settings_button.set_tooltip_text(
            "Mostrar u ocultar configuración (Ctrl+Shift+P)"
        )
        self.settings_button.add(
            Gtk.Image.new_from_icon_name(
                "preferences-system-symbolic",
                Gtk.IconSize.BUTTON
            )
        )
        self.settings_button.set_active(True)
        self.settings_button.connect(
            "toggled", self.on_settings_toggled
        )
        self.header.pack_end(self.settings_button)

        self.connect("destroy", Gtk.main_quit)

        terminal = Vte.Terminal()
        terminal.set_font(Pango.FontDescription("Ubuntu Mono 13"))
        terminal.set_scrollback_lines(10000)
        self.terminal = terminal
        self.connect("key-press-event", self.on_key_press)
        terminal.connect("button-press-event", self.on_button_press)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC
        )
        scroll.add(terminal)
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        toolbar = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )
        toolbar.set_border_width(8)
        toolbar.get_style_context().add_class(
            "dovela-toolbar"
        )
        self.toolbar = toolbar

        label = Gtk.Label(label="Tema:")
        toolbar.pack_start(label, False, False, 0)

        self.theme_selector = Gtk.ComboBoxText()
        for theme_name in self.THEMES:
            self.theme_selector.append_text(theme_name)

        self.theme_selector.set_active(0)
        self.theme_selector.connect(
            "changed", self.on_theme_changed
        )
        toolbar.pack_start(self.theme_selector, False, False, 0)

        transparency_label = Gtk.Label(label="Transparencia:")
        toolbar.pack_start(transparency_label, False, False, 0)

        self.transparency_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0, 70, 5
        )
        self.transparency_scale.set_size_request(150, -1)
        self.transparency_scale.set_value(0)
        self.transparency_scale.set_digits(0)
        self.transparency_scale.set_draw_value(True)
        self.transparency_scale.connect(
            "value-changed", self.on_transparency_changed
        )
        toolbar.pack_start(self.transparency_scale, True, True, 0)

        opaque_button = Gtk.Button(label="Opaco")
        opaque_button.connect(
            "clicked",
            lambda *_: self.transparency_scale.set_value(0)
        )
        toolbar.pack_start(opaque_button, False, False, 0)

        layout.pack_start(toolbar, False, False, 0)


        # Panel de identidad compacto sobre la terminal VTE.
        self.identity_panel = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12
        )
        self.identity_panel.get_style_context().add_class("dovela-identity")
        self.identity_panel.set_border_width(6)

        self.identity_image = Gtk.Image.new_from_file(
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..", "assets", "branding",
                    "dovela-rhino-transparente.png"
                )
            )
        )
        self.identity_panel.pack_start(
            self.identity_image, False, False, 0
        )

        # Cuadro Neofetch situado a la derecha del rinoceronte.
        self.info_frame = Gtk.Frame()
        self.info_frame.set_shadow_type(Gtk.ShadowType.IN)
        self.info_frame.get_style_context().add_class("dovela-info")

        contenido = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4
        )
        contenido.set_border_width(10)

        lema = Gtk.Label(label="Una pieza. Mil conexiones.")
        lema.set_xalign(0)
        contenido.pack_start(lema, False, False, 0)

        datos = self.load_system_info()

        for clave in ("Icons", "CPU", "GPU", "Memory"):
            etiqueta = Gtk.Label(
                label=f"{clave}: {datos[clave]}"
            )
            etiqueta.set_xalign(0)
            etiqueta.set_line_wrap(True)
            etiqueta.set_selectable(True)
            contenido.pack_start(etiqueta, False, False, 0)

        self.palette_label = Gtk.Label()
        self.palette_label.set_xalign(0)
        contenido.pack_start(
            self.palette_label, False, False, 4
        )

        # Glifo flotante sobre el cuadro de información.
        superposicion = Gtk.Overlay()
        superposicion.add(contenido)

        self.glifo_original = os.path.join(
            os.path.dirname(__file__),
            "..", "assets", "identity", "v0.1", "icons",
            "dovela-128.png"
        )
        self.glifo_claro = os.path.join(
            os.path.dirname(__file__),
            "..", "assets", "identity", "v0.1", "icons",
            "dovela-128-claro.png"
        )
        titulo = Gtk.Image.new_from_file(self.glifo_original)
        self.glifo_imagen = titulo
        titulo.set_pixel_size(96)
        titulo.set_halign(Gtk.Align.END)
        titulo.set_valign(Gtk.Align.START)
        titulo.set_margin_top(8)
        titulo.set_margin_end(8)

        superposicion.add_overlay(titulo)
        superposicion.set_overlay_pass_through(titulo, True)

        self.info_frame.add(superposicion)
        # Espacio flexible: empuja el cuadro al extremo derecho.
        separador = Gtk.Box()
        self.identity_panel.pack_start(
            separador, True, True, 0
        )

        self.info_frame.set_size_request(430, -1)
        self.info_frame.set_halign(Gtk.Align.END)

        self.identity_panel.pack_end(
            self.info_frame, False, False, 0
        )

        layout.pack_start(
            self.identity_panel, False, False, 0
        )
        layout.pack_start(scroll, True, True, 0)
        self.add(layout)

        self.identity_button = Gtk.ToggleButton()
        self.identity_button.set_tooltip_text(
            "Mostrar u ocultar identidad gráfica"
        )
        self.identity_button.add(
            Gtk.Image.new_from_icon_name(
                "image-x-generic-symbolic",
                Gtk.IconSize.BUTTON
            )
        )
        self.identity_button.set_active(True)
        self.identity_button.connect(
            "toggled", self.on_identity_toggled
        )
        self.header.pack_start(self.identity_button)

        self.apply_theme("Dovela Oscuro")

        terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            os.path.expanduser("~"),
            [
                "/bin/bash",
                "--rcfile",
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "dovela-bashrc.sh"
                    )
                ),
                "-i",
            ],
            [],
            GLib.SpawnFlags.DEFAULT,
            None,
            None,
            -1,
            None,
            None
        )

        terminal.connect(
            "child-exited",
            lambda *_: self.close()
        )




    def on_identity_toggled(self, button):
        self.identity_panel.set_visible(button.get_active())
        self.terminal.grab_focus()

    def on_settings_toggled(self, button):
        if button.get_active():
            self.toolbar.show()
        else:
            self.toolbar.hide()
        self.terminal.grab_focus()

    def on_key_press(self, widget, event):
        ctrl = bool(event.state & Gdk.ModifierType.CONTROL_MASK)
        shift = bool(event.state & Gdk.ModifierType.SHIFT_MASK)

        if ctrl and shift:
            key = Gdk.keyval_name(event.keyval).lower()

            if key == "p":
                self.settings_button.set_active(
                    not self.settings_button.get_active()
                )
                return True

            if key == "a":
                self.terminal.select_all()
                return True

            if key == "c":
                self.terminal.copy_clipboard_format(
                    Vte.Format.TEXT
                )
                return True

            if key == "v":
                self.terminal.paste_clipboard()
                return True

        return False

    def on_button_press(self, terminal, event):
        if event.button != 3:
            return False

        menu = Gtk.Menu()

        copy_item = Gtk.MenuItem(label="Copiar")
        copy_item.set_sensitive(terminal.get_has_selection())
        copy_item.connect(
            "activate",
            lambda *_: terminal.copy_clipboard_format(Vte.Format.TEXT)
        )

        paste_item = Gtk.MenuItem(label="Pegar")
        paste_item.connect(
            "activate",
            lambda *_: terminal.paste_clipboard()
        )

        menu.append(copy_item)
        menu.append(paste_item)
        menu.show_all()
        menu.popup_at_pointer(event)

        return True



if __name__ == "__main__":
    window = RhynusTerminal()
    window.show_all()
    Gtk.main()
