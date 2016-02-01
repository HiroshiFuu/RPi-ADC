"""
PygInputBox v0.1.0

PygInputBox (pronounced "pig inputbox") is a module that implements UI inputboxes for Pygame.
PygInputBox requires Pygame to be installed. Pygame can be downloaded from http://pygame.org
PygInputBox was developed by Feng Hao (fenghao@ntu.edu.sg)
https://github.com/HiroshiFuu/PygInputBox


Simplified BSD License:

Copyright 2015 Feng Hao. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY Al Sweigart ''AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Al Sweigart OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of Al Sweigart.
"""
import pygame
from pygame.locals import *

pygame.font.init()
PygInputBox_FONT = pygame.font.Font('freesansbold.ttf', 14)

BLACK     = (  0,   0,   0)
WHITE     = (255, 255, 255)
GREEN	  = (  0, 255,   0)
RED		  =	(255, 	0,	 0)

INPUTTEXT = []

class PygInputBox(object):
	def __init__(self, rect=None, prompt='', bgcolor=WHITE, fgcolor=BLACK, font=None, highlightcolor=GREEN):
		global INPUTTEXT
		
		"""Create a new inputbox object. Parameters:
			rect - The size and position of the inputbox as a pygame.Rect object
				or 4-tuple of integers.
			prompt - The prompt text on the inputbox (default is blank)
			bgcolor - The background color of the inputbox (default is a light
				gray color)
			fgcolor - The foreground color (i.e. the color of the text).
				Default is black.
			font - The pygame.font.Font object for the font of the text.
				Default is freesansbold in point 14.
			highlight - A pygame.Surface object for the inputbox's appearance
				when the mouse is over it.
		"""
		
		if rect is None:
			self._rect = pygame.Rect(0, 0, 100, 20)
		else:
			self._rect = pygame.Rect(rect)

		self._prompt = prompt
		self._bgcolor = bgcolor
		self._fgcolor = fgcolor
		self._highlightcolor = highlightcolor

		if font is None:
			self._font = PygInputBox_FONT
		else:
			self._font = font

		# tracks the state of the inputbox
		self._focused = False # is the inputbox currently been focused?
		self._visible = True # is the inputbox visible
		
		# create the surfaces for a text inputbox
		self.surface = pygame.Surface(self._rect.size)
		self._update() # draw the initial inputbox images

	def handleMouseEvent(self, eventObj):
		"""MOUSEBUTTONUP event objects created by Pygame should be passed to this method. 
		handleMouseEvent() will detect if the event is relevant to this inputbox and change its state.

		There are two ways that your code can respond to inputbox-events. One is to inherit the 
		PygInputBox class and override the mouse*() methods. The other is to have the caller 
		of handleMouseEvent() check the return value for the string 'click'."""
		
		global INPUTTEXT

		if eventObj.type != MOUSEBUTTONUP or not self._visible:
			# The inputbox only cares bout mouse-related events (or no events, if it is invisible)
			return []

		if eventObj.type == MOUSEBUTTONUP:
			if not self._focused and self._rect.collidepoint(eventObj.pos):
				# if a mouse click happened inside the inputbox:
				self._focused = True
				self._updateInputBox(''.join(INPUTTEXT), self.focused)
				self.mouseClick(eventObj)
				return 'click'
			elif self._focused and not self._rect.collidepoint(eventObj.pos):
				# if a mouse click happened outside the inputbox:
				self._focused = False
				self._updateInputBox(''.join(INPUTTEXT), self.focused)

		return []


	def handleKeyEvent(self, eventObj):
		global INPUTTEXT
		
		if not self._visible or not self.focused or eventObj.type != KEYUP:
			return None
			
		inkey = eventObj.key
		if inkey == K_RETURN:
			self._focused = False
		elif inkey == K_BACKSPACE:
			INPUTTEXT = INPUTTEXT[0:-1]
		elif inkey >= 40 and inkey <= 127:
			INPUTTEXT.append(chr(inkey))
		self._updateInputBox(''.join(INPUTTEXT), self._focused)


	def draw(self, surfaceObj):
		"""Blit the current inputbox's appearance to the surface object."""
		
		if self._visible:
			surfaceObj.blit(self.surface, self._rect)


	def _update(self):
		"""The default method to redraw the inputbox's Surface object. 
		Call this method to draw inputbox in default appearance"""

		# draw input box
		self._updateInputBox(self.prompt)
			
			
	def _updateInputBox(self, text, focused=False):
		"""Redraw the inputbox's Surface object. Call this method when the inputbox has changed appearance."""
		
		global INPUTTEXT
		
		# fill background color
		self.surface.fill(self.bgcolor)
		
		w = self._rect.width
		h = self._rect.height
		
		# if user didn't input anything, display the default prompt text when lost focus
		if INPUTTEXT == [] and not focused:
			text = self.prompt
		
		promptSurf = self._font.render(text, True, self.fgcolor, self.bgcolor)
		promptRect = promptSurf.get_rect()
		promptRect.center = promptRect.w / 2 + 2, int(h / 2)
		self.surface.blit(promptSurf, promptRect)
		
		pygame.draw.rect(self.surface, BLACK, pygame.Rect((0, 0, w, h)), 1) # black border around everything
		
		if not focused:
			# draw border for normal inputbox
			pygame.draw.line(self.surface, WHITE, (1, 1), (w - 2, 1))
			pygame.draw.line(self.surface, WHITE, (1, 1), (1, h - 2))
			pygame.draw.line(self.surface, WHITE, (1, h - 1), (w - 1, h - 1))
			pygame.draw.line(self.surface, WHITE, (w - 1, 1), (w - 1, h - 1))
			pygame.draw.line(self.surface, WHITE, (2, h - 2), (w - 2, h - 2))
			pygame.draw.line(self.surface, WHITE, (w - 2, 2), (w - 2, h - 2))
		else:
			# draw border for highlight inputbox
			pygame.draw.line(self.surface, self._highlightcolor, (1, 1), (w - 2, 1))
			pygame.draw.line(self.surface, self._highlightcolor, (1, 1), (1, h - 2))
			pygame.draw.line(self.surface, self._highlightcolor, (1, h - 1), (w - 1, h - 1))
			pygame.draw.line(self.surface, self._highlightcolor, (w - 1, 1), (w - 1, h - 1))
			pygame.draw.line(self.surface, self._highlightcolor, (2, h - 2), (w - 2, h - 2))
			pygame.draw.line(self.surface, self._highlightcolor, (w - 2, 2), (w - 2, h - 2))
			

	def mouseClick(self, event):
		pass # This class is meant to be overridden.


	def _propGetprompt(self):
		return self._prompt


	def _propSetprompt(self, promptText):
		self._prompt = promptText
		self._update()


	def _propGetRect(self):
		return self._rect


	def _propSetRect(self, newRect):
		# Note that changing the attributes of the Rect won't update the inputbox. You have to re-assign the rect member.
		self._rect = newRect
		self._update()


	def _propGetVisible(self):
		return self._visible


	def _propSetVisible(self, setting):
		self._visible = setting


	def _propGetFgColor(self):
		return self._fgcolor


	def _propSetFgColor(self, setting):
		self._fgcolor = setting
		self._update()


	def _propGetBgColor(self):
		return self._bgcolor


	def _propSetBgColor(self, setting):
		self._bgcolor = setting
		self._update()


	def _propGetFont(self):
		return self._font


	def _propSetFont(self, setting):
		self._font = setting
		self._update()

	def _propGetHightlightColor(self):
		return self._highlightcolor


	def _propSetHightlightColor(self, setting):
		self._highlightcolor = setting
		self._update()


	def _propGetFocused(self):
		return self._focused


	def _propSetFocused(self, setting):
		self._focused = setting
		self._update()


	prompt = property(_propGetprompt, _propSetprompt)
	rect = property(_propGetRect, _propSetRect)
	visible = property(_propGetVisible, _propSetVisible)
	fgcolor = property(_propGetFgColor, _propSetFgColor)
	bgcolor = property(_propGetBgColor, _propSetBgColor)
	font = property(_propGetFont, _propSetFont)
	highlightcolor = property(_propGetHightlightColor, _propGetHightlightColor)
	focused = property(_propGetFocused, _propGetFocused)
