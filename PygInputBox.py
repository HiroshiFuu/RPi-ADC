"""
PygInputBox v0.1.0

PygInputBox (pronounced "pig inputbox") is a module that implements non-pooling inputbox UI for Pygame.
PygInputBox requires Pygame to be installed. Pygame can be downloaded from http://pygame.org.
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

THIS SOFTWARE IS PROVIDED BY Feng Hao ''AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Feng Hao OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of Feng Hao.
"""

import pygame
from pygame.locals import *

pygame.font.init()

BLACK     = (  0,   0,   0)
WHITE     = (255, 255, 255)
GREEN	  = (  0, 255,   0)
RED		  =	(255, 	0,	 0)

class PygInputBox(object):
	def __init__(self, rect=None, prompt='', inputtext=[], bgcolor=WHITE, fgcolor=BLACK, font=None, highlightcolor=GREEN):
		"""Create a new inputbox object. Parameters:
			rect - The size and position of the inputbox as a pygame. Rect object or 4-tuple of integers.
			prompt - The prompt text on the inputbox (default is blank)
			bgcolor - The background color of the inputbox. Default is black.
			fgcolor - The foreground color (i.e. the color of the text). Default is white.
			font - The pygame.font.Font object for the font of the text. Default is freesansbold in point 14.
			highlight - A pygame.Surface object for the inputbox's appearance when the it is been focused.
		"""
		
		if rect is None:
			self._rect = pygame.Rect(0, 0, 100, 20)
		else:
			self._rect = pygame.Rect(rect)

		self._prompt = prompt
		self._inputtext = inputtext
		self._bgcolor = bgcolor
		self._fgcolor = fgcolor
		self._highlightcolor = highlightcolor

		if font is None:
			self._font = pygame.font.Font('freesansbold.ttf', 14)
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
		handleMouseEvent() will detect if the event is relevant to this inputbox and change its state."""

		if eventObj.type != MOUSEBUTTONUP or not self._visible:
			# The inputbox only cares about mouse-related events (or no events, if it is invisible)
			return []

		if eventObj.type == MOUSEBUTTONUP:
			if not self._focused and self._rect.collidepoint(eventObj.pos):
				# if a mouse click happened inside the inputbox:
				self._focused = True
				self._updateInputBox(''.join(self.inputtext), self.focused)
				return 'click'
			elif self._focused and not self._rect.collidepoint(eventObj.pos):
				# if a mouse click happened outside the inputbox:
				self._focused = False
				self._updateInputBox(''.join(self.inputtext), self.focused)

		return []


	def handleKeyEvent(self, eventObj):
		"""KEYUP event objects created by Pygame should be passed to this method. 
		handleKeyEvent() will detect if the event is relevant to this inputbox and change its input text."""
		
		if not self._visible or not self.focused or eventObj.type != KEYUP:
			# The inputbox only cares about key-related events (or no events, if it is invisible)
			# and the inputbox is currently activated.
			return None
		
		entered = False	# whether the return key is pressed
		
		inkey = eventObj.key
		if inkey == K_RETURN:
			self._focused = False
			entered = True
		elif inkey == K_BACKSPACE:
			self._inputtext = self.inputtext[0:-1]
		elif inkey >= 32 and inkey <= 127:
			# if SHIFT key is held or CAPS key is on, append the uppercased or lowercased key
			mods = pygame.key.get_mods()
			if mods & KMOD_CAPS:
				inkey -= 32
			if mods & KMOD_SHIFT:
				inkey -= 32
			if mods & KMOD_SHIFT and mods & KMOD_CAPS:
				inkey += 32 + 32
			self._inputtext.append(chr(inkey))
		self._updateInputBox(''.join(self.inputtext), self._focused)
		if entered:
			return True
		return False


	def draw(self, surfaceObj):
		"""Blit the current inputbox's appearance to the surface object."""
		
		if self._visible:
			surfaceObj.blit(self.surface, self._rect)


	def _update(self):
		"""The default method to redraw the inputbox's Surface object. 
		Call this method to draw inputbox in default appearance"""

		# draw input box
		if self.inputtext == []:
			self._updateInputBox(self.prompt)
		else:
			self._updateInputBox(''.join(self.inputtext))
			
			
	def _updateInputBox(self, text, focused=False):
		"""Redraw the inputbox's Surface object. Call this method when the inputbox has changed appearance or input text."""
		
		# fill background color
		self.surface.fill(self.bgcolor)
		
		w = self._rect.width
		h = self._rect.height
		
		# if user didn't input anything, display the default prompt text when lost focus
		if self.inputtext == [] and not focused:
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


	def _propGetprompt(self):
		return self._prompt


	def _propSetprompt(self, promptText):
		self._prompt = promptText
		self._update()


	def _propGetinputtext(self):
		return self._inputtext


	def _propSetinputtext(self, inputtext):
		self._inputtext = inputtext
		self._update()



	def _propGetRect(self):
		return self._rect


	def _propSetRect(self, newRect):
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
	inputtext = property(_propGetinputtext, _propSetinputtext)
	rect = property(_propGetRect, _propSetRect)
	visible = property(_propGetVisible, _propSetVisible)
	fgcolor = property(_propGetFgColor, _propSetFgColor)
	bgcolor = property(_propGetBgColor, _propSetBgColor)
	font = property(_propGetFont, _propSetFont)
	highlightcolor = property(_propGetHightlightColor, _propGetHightlightColor)
	focused = property(_propGetFocused, _propGetFocused)
