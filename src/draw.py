#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011~2013 Deepin, Inc.
#               2011~2013 Kaisheng Ye
#
# Author:     Kaisheng Ye <kaisheng.ye@gmail.com>
# Maintainer: Kaisheng Ye <kaisheng.ye@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cairo
import pango
import pangocairo

from dtk.ui.constant import DEFAULT_FONT_SIZE, DEFAULT_FONT
import dtk_cairo_blur
from dtk.ui.utils import cairo_state, color_hex_to_cairo

TEXT_ALIGN_TOP = 1
TEXT_ALIGN_MIDDLE = 2
TEXT_ALIGN_BOTTOM = 3
        
def draw_text(cr, markup, 
              x, y, w, h, 
              text_size=DEFAULT_FONT_SIZE, 
              text_color="#000000", 
              text_font=DEFAULT_FONT, 
              alignment=pango.ALIGN_LEFT,
              gaussian_radious=None, 
              gaussian_color=None,
              border_radious=None, 
              border_color=None, 
              wrap_width=None, 
              underline=False,
              vertical_alignment=TEXT_ALIGN_MIDDLE,
              clip_line_count=None,
              ellipsize=pango.ELLIPSIZE_END,
              ):
    '''
    Standard function for draw text.
    
    @param cr: Cairo context.
    @param markup: Pango markup string.
    @param x: X coordinate of draw area.
    @param y: Y coordinate of draw area.
    @param w: Width of draw area.
    @param h: Height of draw area.
    @param text_size: Text size, default is DEFAULT_FONT_SIZE.
    @param text_color: Text color, default is \"#000000\".
    @param text_font: Text font, default is DEFAULT_FONT.
    @param alignment: Font alignment option, default is pango.ALIGN_LEFT. You can set pango.ALIGN_MIDDLE or pango.ALIGN_RIGHT.
    @param gaussian_radious: Gaussian radious, default is None.
    @param gaussian_color: Gaussian color, default is None.
    @param border_radious: Border radious, default is None.
    @param border_color: Border color, default is None.
    @param wrap_width: Wrap width of text, default is None.
    @param underline: Whether draw underline for text, default is False.
    @param vertical_alignment: Vertical alignment value, default is TEXT_ALIGN_MIDDLE, can use below value:
     - TEXT_ALIGN_TOP
     - TEXT_ALIGN_MIDDLE
     - TEXT_ALIGN_BOTTOM
    @param clip_line_count: The line number to clip text area, if set 2, all lines that above 2 will clip out, default is None.
    @param ellipsize: Ellipsize style of text when text width longer than draw area, it can use below value:
     - pango.ELLIPSIZE_START
     - pango.ELLIPSIZE_CENTER
     - pango.ELLIPSIZE_END
    '''
    if border_radious == None and border_color == None and gaussian_radious == None and gaussian_color == None:
        render_text(cr, markup, x, y, w, h, text_size, text_color, text_font, alignment,
                    wrap_width=wrap_width,
                    underline=underline,
                    vertical_alignment=vertical_alignment,
                    clip_line_count=clip_line_count,
                    ellipsize=ellipsize,
                    )
    elif (border_radious != None and border_color != None) or (gaussian_radious != None and gaussian_color != None):
        # Create text cairo context.
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        text_cr = cairo.Context(surface)
        
        # Draw gaussian light.
        if gaussian_radious != None and gaussian_color != None:
            text_cr.save()
            render_text(text_cr, markup, gaussian_radious, 
                        gaussian_radious, w - gaussian_radious * 2, h - gaussian_radious * 2, 
                        text_size, gaussian_color, alignment=alignment,
                        wrap_width=wrap_width,
                        underline=underline,
                        vertical_alignment=vertical_alignment,
                        clip_line_count=clip_line_count,
                        ellipsize=ellipsize,
                        )
            dtk_cairo_blur.gaussian_blur(surface, gaussian_radious)
            text_cr.restore()
        
        # Make sure border can render correctly.
        if gaussian_radious == None:
            gaussian_radious = 0
            
        # Draw gaussian border.
        if border_radious != None and border_radious != 0 and border_color != None:
            render_text(text_cr, markup, gaussian_radious, gaussian_radious, w - gaussian_radious * 2, 
                        h - gaussian_radious * 2, text_size, border_color, alignment=alignment,
                        wrap_width=wrap_width,
                        underline=underline,
                        vertical_alignment=vertical_alignment,
                        clip_line_count=clip_line_count,
                        ellipsize=ellipsize,
                        )
            dtk_cairo_blur.gaussian_blur(surface, border_radious)
        
        # Draw font.
        render_text(text_cr, markup, gaussian_radious, gaussian_radious, w - gaussian_radious * 2, 
                    h - gaussian_radious * 2, text_size, text_color, alignment=alignment,
                    wrap_width=wrap_width,
                    underline=underline,
                    vertical_alignment=vertical_alignment,
                    clip_line_count=clip_line_count,
                    ellipsize=ellipsize,
                    )
        
        # Render gaussian text to target cairo context.
        cr.set_source_surface(surface, x, y)
        cr.paint()
    
def render_text(cr, markup, 
                x, y, w, h, 
                text_size=DEFAULT_FONT_SIZE, 
                text_color="#000000", 
                text_font=DEFAULT_FONT, 
                alignment=pango.ALIGN_LEFT,
                wrap_width=None, 
                underline=False,
                vertical_alignment=TEXT_ALIGN_MIDDLE,
                clip_line_count=None,
                ellipsize=pango.ELLIPSIZE_END,
                ):
    '''
    Render text for function L{ I{draw_text} <draw_text>}, you can use this function individually.
    
    @param cr: Cairo context.
    @param markup: Pango markup string.
    @param x: X coordinate of draw area.
    @param y: Y coordinate of draw area.
    @param w: Width of draw area.
    @param h: Height of draw area.
    @param text_size: Text size, default is DEFAULT_FONT_SIZE.
    @param text_color: Text color, default is \"#000000\".
    @param text_font: Text font, default is DEFAULT_FONT.
    @param alignment: Font alignment option, default is pango.ALIGN_LEFT. You can set pango.ALIGN_MIDDLE or pango.ALIGN_RIGHT.
    @param wrap_width: Wrap width of text, default is None.
    @param underline: Whether draw underline for text, default is False.
    @param vertical_alignment: Vertical alignment value, default is TEXT_ALIGN_MIDDLE, can use below value:
     - TEXT_ALIGN_TOP
     - TEXT_ALIGN_MIDDLE
     - TEXT_ALIGN_BOTTOM
    @param clip_line_count: The line number to clip text area, if set 2, all lines that above 2 will clip out, default is None.
    @param ellipsize: Ellipsize style of text when text width longer than draw area, it can use below value:
     - pango.ELLIPSIZE_START
     - pango.ELLIPSIZE_CENTER
     - pango.ELLIPSIZE_END
    '''
    with cairo_state(cr):
        # Set color.
        cr.set_source_rgb(*color_hex_to_cairo(text_color))
        
        # Create pangocairo context.
        context = pangocairo.CairoContext(cr)
        
        # Set layout.
        layout = context.create_layout()
        layout.set_font_description(pango.FontDescription("%s %s" % (text_font, text_size)))
        layout.set_markup(markup)
        layout.set_alignment(alignment)
        if wrap_width == None:
            layout.set_single_paragraph_mode(True)
            layout.set_width(w * pango.SCALE)
            layout.set_ellipsize(ellipsize)
        else:
            layout.set_width(wrap_width * pango.SCALE)
            layout.set_wrap(pango.WRAP_WORD)
            
        (text_width, text_height) = layout.get_pixel_size()
        
        if underline:
            if alignment == pango.ALIGN_LEFT:
                cr.rectangle(x, y + text_height + (h - text_height) / 2, text_width, 1)
            elif alignment == pango.ALIGN_CENTER:
                cr.rectangle(x + (w - text_width) / 2, y + text_height + (h - text_height) / 2, text_width, 1)
            else:
                cr.rectangle(x + w - text_width, y + text_height + (h - text_height) / 2, text_width, 1)
            cr.fill()
            
        # Set render y coordinate.
        if vertical_alignment == TEXT_ALIGN_TOP:
            render_y = y
        elif vertical_alignment == TEXT_ALIGN_MIDDLE:
            render_y = y + max(0, (h - text_height) / 2)
        else:
            render_y = y + max(0, h - text_height)
            
        # Clip area.
        if clip_line_count:
            line_count = layout.get_line_count()
            if line_count > 0:
                line_height = text_height / line_count
                cr.rectangle(x, render_y, text_width, line_height * clip_line_count)
                cr.clip()
            
        # Draw text.
        cr.move_to(x, render_y)
        context.update_layout(layout)
        context.show_layout(layout)

