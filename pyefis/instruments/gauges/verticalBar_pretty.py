#  Copyright (c) 2013 Phil Birkelbach
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


from .abstract import AbstractGauge

class VerticalBarPretty(AbstractGauge):
    def __init__(self, parent=None):
        super(VerticalBarPretty, self).__init__(parent)
        self.setMinimumSize(80, 120)
        self.showValue = True
        self.showUnits = True
        self.showName = True
        self.barWidthPercent = 0.3
        self.lineWidthPercent = 0.5
        self.textGap = 12
        self.smallFontPercent = 0.20
        self.bigFontPercent = 0.25
        self.normalizePenColor = QColor(Qt.blue)
        self.normalizeRange = 0
        self.normalizeReference = 0
        self._normalizeMode = False
        self.peakValue = 0.0
        self._peakMode = False
        self.peakColor = QColor(Qt.magenta)
        self._oldpencolor = self.penGoodColor

    def getNormalizeMode(self):
        return self._normalizeMode

    def setNormalizeMode(self, x):
        if x:
            if self._normalizeMode: return
            self._normalizeMode = True
            self._oldpencolor = self.penGoodColor
            self.penGoodColor = self.normalizePenColor
            self.normalizeReference = self.value
        else:
            self._normalizeMode = False
            self.penGoodColor = self._oldpencolor
        self.setColors()
        self.update()

    normalizeMode = property(getNormalizeMode, setNormalizeMode)

    def getPeakMode(self):
        return self._peakMode

    def setPeakMode(self, x):
        if x:
            self._peakMode = True
        else:
            self._peakMode = False
        self.update()

    peakMode = property(getPeakMode, setPeakMode)

    def resizeEvent(self, event):
        self.barWidth = self.width() * self.barWidthPercent
        self.lineWidth = self.width() * self.lineWidthPercent
        self.bigFont = QFont()
        self.bigFont.setPixelSize(self.width() * self.bigFontPercent)
        self.smallFont = QFont()
        self.smallFont.setPixelSize(self.width() * self.smallFontPercent)
        #self.barHeight = self.height() / 6
        if self.showName:
            self.barTop = self.smallFont.pixelSize() + self.textGap
        else:
            self.barTop = 1
        self.barBottom = self.height()
        if self.showValue:
            self.barBottom -= (self.bigFont.pixelSize() + self.textGap)
        # if self.showUnits:
        #     self.barBottom -= (self.smallFont.pixelSize() + self.textGap)

        self.barLeft = (self.lineWidth - self.barWidth) / 2
        self.barRight = self.barLeft + self.barWidth
        self.lineLeft = 0
        self.lineRight = self.lineLeft + self.lineWidth
        self.barHeight = self.barBottom - self.barTop

        self.nameTextRect = QRectF(0, 0, self.width(), self.smallFont.pixelSize())
        self.valueTextRect = QRectF(0, self.height() - self.bigFont.pixelSize() - self.textGap, self.width()/2, self.bigFont.pixelSize())
        self.unitsTextRect = QRectF(self.width()/2, self.height() - self.bigFont.pixelSize() - self.textGap, self.width()/2, self.bigFont.pixelSize())
        self.ballRadius = self.barWidth * 0.40
        self.ballCenter = QPointF(self.barLeft + (self.barWidth / 2), self.barBottom - (self.barWidth/2))

    def drawValue(self, p, pen):
        pen.setColor(self.valueColor)
        p.setPen(pen)
        p.setFont(self.bigFont)
        p.drawText(self.valueTextRect, self.valueText, QTextOption(Qt.AlignCenter))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        pen = QPen()
        pen.setWidth(1)
        pen.setCapStyle(Qt.FlatCap)
        p.setPen(pen)
        opt = QTextOption(Qt.AlignCenter)
        if self.showName:
            pen.setColor(self.textColor)
            p.setPen(pen)
            p.setFont(self.smallFont)
            p.drawText(self.nameTextRect, self.name, opt)
        if self.showValue:
            # if self.peakMode:
            #     dv = self.value - self.peakValue
            #     if dv <= -10:
            #         pen.setColor(self.peakColor)
            #         p.setFont(self.bigFont)
            #         p.setPen(pen)
            #         p.drawText(self.valueTextRect, str(round(dv)), opt)
            #     else:
            #         self.drawValue(p, pen)
            # else:
                # Draw Value
                self.drawValue(p, pen)
        if self.showUnits:
            # Units
            pen.setColor(self.unitColor)
            p.setPen(pen)
            p.setFont(self.smallFont)
            p.drawText(self.unitsTextRect, self.units, opt)

        # Draw the scale
        # Calculate tick intervals from total range
        totalRange = self.highRange - self.lowRange
        minorTick = 2
        majorTick = 10
        labelDivisor = 1
        if totalRange >= 100:
            minorTick = 25
            majorTick = 50
            labelDivisor = 1
        elif totalRange >= 30:
            minorTick = 1
            majorTick = 5
            labelDivisor = 1
        
        labelTick = majorTick

        # Minor ticks
        pen.setColor(self.scaleColor)
        pen.setWidth(1)
        p.setPen(pen)
        length = self.barWidth * 0.5
        for tick in range(int(self.lowRange), int(self.highRange)+1, minorTick):
            y = self.barTop + self.barHeight - self.interpolate(tick, self.barHeight)
            x2 = self.barRight + length
            p.drawLine(self.barRight, y, x2, y)

        # # Major ticks
        pen.setColor(self.scaleColor)
        pen.setWidth(2)
        p.setPen(pen)
        length = self.barWidth * 0.75
        for tick in range(int(self.lowRange), int(self.highRange)+1, majorTick):
            y = self.barTop + self.barHeight - self.interpolate(tick, self.barHeight)
            x2 = self.barRight + length
            p.drawLine(self.barRight, y, x2, y)

        # Caution/warning ticks
        pen.setWidth(1)
        length = self.barWidth * 0.75
        if self.lowAlarm:
            pen.setColor(self.alarmColor)
            p.setPen(pen)
            y = self.barTop + self.barHeight - self.interpolate(self.lowAlarm, self.barHeight)
            x2 = self.barRight + length
            p.drawLine(self.barRight, y, x2, y)

        if self.lowWarn:
            pen.setColor(self.warnColor)
            p.setPen(pen)
            y = self.barTop + self.barHeight - self.interpolate(self.lowWarn, self.barHeight)
            x2 = self.barRight + length
            p.drawLine(self.barRight, y, x2, y)

        if self.highWarn:
            pen.setColor(self.warnColor)
            p.setPen(pen)
            y = self.barTop + self.barHeight - self.interpolate(self.highWarn, self.barHeight)
            x2 = self.barRight + length
            p.drawLine(self.barRight, y, x2, y)

        if self.highAlarm:
            pen.setColor(self.alarmColor)
            p.setPen(pen)
            y = self.barTop + self.barHeight - self.interpolate(self.highAlarm, self.barHeight)
            x2 = self.barRight + length
            p.drawLine(self.barRight, y, x2, y)

        # # Labels
        pen.setColor(self.scaleColor)
        pen.setWidth(1)
        p.setPen(pen)
        f = QFont()
        f.setPixelSize(self.height() / 10)
        p.setFont(f)
        opt = QTextOption(Qt.AlignLeft | Qt.AlignBottom)
        path = QPainterPath()
        brush = QBrush(self.scaleColor)
        p.setBrush(brush)

        x = self.barRight + (length * 1.5)
        for tick in range(int(self.lowRange), int(self.highRange)+1, labelTick):
            numString = str(int(tick / labelDivisor))
            fm = QFontMetrics(f)
            y = self.barTop + self.barHeight - self.interpolate(tick, self.barHeight)
            y += f.pixelSize() / 2
            x2 = self.barRight + length
            path = QPainterPath()
            path.addText(QPointF(x, y), f, numString)
            p.drawPath(path)

        # Select bar color
        if self.lowAlarm and self._value <= self.lowAlarm:
            color = self.alarmColor
        elif self.lowWarn and self._value <= self.lowWarn:
            color = self.warnColor
        elif self.highAlarm and self._value >= self.highAlarm:
            color = self.alarmColor
        elif self.highWarn and self._value >= self.highWarn:
            color = self.warnColor
        else:
            color = self.safeColor

        # Draw the bar
        p.setRenderHint(QPainter.Antialiasing, False)
        pen.setColor(color)
        brush = color
        p.setPen(pen)
        p.setBrush(brush)
        x = self.interpolate(self._value, self.barHeight)
        p.drawRect(self.barLeft, self.barTop + self.barHeight - x, self.barWidth, x)

        # Highlight Ball
        # if self.highlight:
        #     pen.setColor(Qt.black)
        #     pen.setWidth(1)
        #     p.setPen(pen)
        #     p.setBrush(self.highlightColor)
        #     p.drawEllipse(self.ballCenter, self.ballRadius, self.ballRadius)


        # Draw Peak Value Line and text
        # if self.peakMode:
        #     pen.setColor(QColor(Qt.white))
        #     brush = QBrush(self.peakColor)
        #     pen.setWidth(1)
        #     p.setPen(pen)
        #     p.setBrush(brush)
        #     if self.normalizeMode:
        #         nval = self.peakValue - self.normalizeReference
        #         start = self.barTop + self.barHeight / 2
        #         y = start - (nval * self.barHeight / self.normalizeRange)
        #     else:
        #         y = self.barTop + (self.barHeight - self.interpolate(self.peakValue, self.barHeight))
        #     if y < self.barTop: y = self.barTop
        #     if y > self.barBottom: y = self.barBottom
        #     p.drawRect(self.lineLeft, y-2, self.lineWidth, 4)
