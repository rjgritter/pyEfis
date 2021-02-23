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

import math
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .abstract import AbstractGauge, drawCircle

class ThreeQuarterGauge(AbstractGauge):
    def __init__(self, parent=None):
        super(ThreeQuarterGauge, self).__init__(parent)
        self.setMinimumSize(100, 100)
        self.startAngle = -90
        self.sweepAngle = 270
        self.arcWidth = self.height() / 6.66

    def resizeEvent(self, event):
        self.arcCenter = QPoint(self.width() / 2, self.height() / 2)
        self.arcWidth = self.height() / 6.66
        self.arcRadius = (self.height() / 2) - (self.arcWidth / 2)

    def paintEvent(self, e):
        startAngle = self.startAngle
        totalSweep = self.sweepAngle
        r = self.arcRadius - self.arcWidth

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pen = QPen()
        pen.setWidth(self.arcWidth)
        pen.setCapStyle(Qt.FlatCap)

        valAngle = self.interpolate(self._value, totalSweep)

        color = QColor(Qt.white)

        if self.lowAlarm and self._value <= self.lowAlarm:
            color = self.alarmColor
        elif self.lowWarn and self._value <= self.lowWarn:
            color = self.warnColor
        elif self.highWarn and self._value < self.highWarn:
            color = self.safeColor
        elif self.highAlarm and self._value < self.highAlarm:
            color = self.warnColor
        else:
            color = self.alarmColor

        pen.setColor(color)
        p.setPen(pen)
        # Angle arguments are start angle from 3 o'clock, then sweep angle counterclockwise
        drawCircle(p, self.arcCenter.x(), self.arcCenter.y(), r,
                    startAngle, -valAngle)

        # Calculate tick intervals from total range
        totalRange = self.highRange - self.lowRange
        minorTick = 2
        majorTick = 10
        labelDivisor = 1
        if totalRange >= 3000:
            minorTick = 100
            majorTick = 500
            labelDivisor = 100
        elif totalRange >= 300:
            minorTick = 10
            majorTick = 50
            labelDivisor = 10
        elif totalRange >= 30:
            minorTick = 1
            majorTick = 5
            labelDivisor = 1
        
        labelTick = majorTick

        # Draw scale
        pen.setColor(self.scaleColor)
        pen.setWidth(1)
        p.setPen(pen)
        rInner = r + (self.arcWidth / 2)
        rOuter = rInner + (self.arcRadius / 10)
        for tick in range(int(self.lowRange), int(self.highRange)+1, minorTick):
            angle = self.startAngle - self.interpolate(tick, totalSweep)
            x1 = self.arcCenter.x() + rInner*math.cos(math.radians(angle))
            y1 = self.arcCenter.y() - rInner*math.sin(math.radians(angle))  # Reversed since y is positive down
            x2 = self.arcCenter.x() + rOuter*math.cos(math.radians(angle))
            y2 = self.arcCenter.y() - rOuter*math.sin(math.radians(angle))  # Reversed since y is positive down
            p.drawLine(x1, y1, x2, y2)

        pen.setWidth(2)
        p.setPen(pen)
        rInner = r + (self.arcWidth / 2)
        rOuter = rInner + (self.arcRadius / 8)
        for tick in range(int(self.lowRange), int(self.highRange)+1, majorTick):
            angle = self.startAngle - self.interpolate(tick, totalSweep)
            x1 = self.arcCenter.x() + rInner*math.cos(math.radians(angle))
            y1 = self.arcCenter.y() - rInner*math.sin(math.radians(angle))  # Reversed since y is positive down
            x2 = self.arcCenter.x() + rOuter*math.cos(math.radians(angle))
            y2 = self.arcCenter.y() - rOuter*math.sin(math.radians(angle))  # Reversed since y is positive down
            p.drawLine(x1, y1, x2, y2)

        # Labels
        pen.setColor(self.scaleColor)
        pen.setWidth(1)
        p.setPen(pen)
        f = QFont()
        f.setPixelSize(self.height() / 13)
        p.setFont(f)
        opt = QTextOption(Qt.AlignLeft | Qt.AlignBottom)
        path = QPainterPath()
        brush = QBrush(self.scaleColor)
        p.setBrush(brush)

        rOuter += f.pixelSize() * 0.6    # TODO: Parameterize this
        for tick in range(int(self.lowRange), int(self.highRange)+1, labelTick):
            numString = str(int(tick / labelDivisor))
            angle = self.startAngle - self.interpolate(tick, totalSweep)
            x = self.arcCenter.x() + rOuter*math.cos(math.radians(angle))
            y = self.arcCenter.y() - rOuter*math.sin(math.radians(angle))  # Reversed since y is positive down
            fm = QFontMetrics(f)
            x -= fm.width(numString) / 2
            y += f.pixelSize() / 2
            path = QPainterPath()
            # path.addText(QPointF(x, y), f, QString::number(int(num)))
            path.addText(QPointF(x, y), f, numString)
            p.drawPath(path)


        # Main value text
        pen.setColor(color)
        p.setPen(pen)
        f = QFont()
        f.setPixelSize(self.height() / 6)
        p.setFont(f)
        opt = QTextOption(Qt.AlignLeft | Qt.AlignBottom)
        path = QPainterPath()
        brush = QBrush(color)
        p.setBrush(brush)
        
        f.setPixelSize(self.height() / 5)
        fm = QFontMetrics(f)
        valueTextWidth = fm.width(self.valueText)
        yPos = (self.height() / 2) + f.pixelSize() + (self.height() / 20)
        path.addText(QPointF(self.width()-valueTextWidth, yPos), f, self.valueText)
        p.drawPath(path)

        # Label Text
        pen.setColor(self.unitColor)
        pen.setWidth(1)
        p.setPen(pen)
        f.setPixelSize(self.height() / 12)
        p.setFont(f)
        fm = QFontMetrics(f)
        nameTextWidth = fm.width(self.name)
        xPos = self.width() - (nameTextWidth / 2) - (1.5 * f.pixelSize())
        yPos += f.pixelSize() + (self.height() / 20)
        #p.drawText(QPoint(centerX - (r - 40), centerY - (r - 40)), self.name)
        p.drawText(QPoint(xPos, yPos), self.name)
