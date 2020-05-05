#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys, os, numpy, PIL
from PySide2 import QtCore, QtGui, QtWidgets
from PIL import Image, ImagePalette

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setAcceptDrops(True)
        self.widget = Widget(self)
        self.setCentralWidget(self.widget)
        self.show()

class Widget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)
        self.setAcceptDrops(True)
        self.framelist = FrameListView()
        scroller = QtWidgets.QScrollArea()
        scroller.setWidget(self.framelist)
        scroller.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        layout = QtWidgets.QGridLayout()
        layout.addWidget(scroller, 0, 0)
        self.setLayout(layout)
#        self.resize(self.view.width(), self.view.height())
        self.setWindowTitle("QAction")
        self.show()

class FrameListView(QtWidgets.QListView):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
#        self.resizeContents(16, 16*16)
        self.model = FrameListModel()
        here = os.path.abspath(os.path.dirname(__file__))
        res = os.path.join(os.path.dirname(here), 'res')
        red = os.path.join(res, 'red.png')
        green = os.path.join(res, 'green.png')
        self.model.appendRow(red)
        self.model.appendRow(green)
        self.model.appendRow(red)
        self.model.appendRow(green)
        self.model.appendRow(red)
        self.model.appendRow(green)
        self.setModel(self.model)
#        self.resize(64, 16*16)
        self.show()
    def mousePressEvent(self, event):
        super(self.__class__, self).mousePressEvent(event)
        for idx in self.selectedIndexes():
            frame = idx.data(QtCore.Qt.UserRole)
            self.model.change_icon(idx)
#            print(frame)

class FrameListModel(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.frames = []
    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid(): return 0
        return len(self.frames)
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DecorationRole:
            return self.frames[index.row()].Icon
        elif  role == QtCore.Qt.UserRole:
            return self.frames[index.row()]
    def appendRow(self, file_path):
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        self.frames.append(Frame(file_path))
        self.endInsertRows()
    def change_icon(self, index):
        self.frames[index.row()].change_icon()

class Frame:
    def __init__(self, file_path=None):
        self.pixels = Pixels()
        self.icon = QtGui.QIcon(file_path)
        self.file_path = file_path
    @property
    def Pixels(self): return self.pixels
    @Pixels.setter
    def Pixels(self, value): self.pixels = value
    @property
    def Icon(self): return self.icon
    @Icon.setter
    def Icon(self, value): self.icon = value
    def change_icon(self):
        self.file_path = os.path.join(os.path.dirname(self.file_path), self.__get_file_name())
        self.icon = QtGui.QIcon(self.file_path)
#        print(self.file_path)
    def __get_file_name(self):
        if 'red.png' == os.path.basename(self.file_path): return 'green.png'
        else: return 'red.png'

class Pixels:
    def __init__(self):
        self.width = 16
        self.height = 16
        self.pixels = numpy.zeros(self.width*self.height, dtype=int).reshape(self.height, self.width)
    @property
    def Pixels(self): return self.pixels
    @property
    def Width(self): return self.width
    @property
    def Height(self): return self.height
    def save(self):
        print(os.getcwd())
        self.save_txt()
        for ext in ('gif', 'png', 'webp'):
            self.save_raster(ext)
    def load(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()[1:]
        if '' == ext: raise Exception('拡張子が必要です。png,gif,webp,txt形式のいずれかに対応しています。')
        elif 'txt' == ext: self.load_txt(file_path)
        elif 'gif' == ext: self.load_gif(file_path)
        elif 'png' == ext: self.load_png(file_path)
        elif 'webp' == ext: self.load_webp(file_path)
        else: raise Exception('拡張子が未対応です。png,gif,webp,txt形式のいずれかに対応しています。')
    def save_txt(self):
        with open(os.path.join(os.getcwd(), 'pixels.txt'), 'w') as f:
            f.write('\n'.join([''.join(map(str, self.pixels[y].tolist())) for y in range(self.height)]))
    def load_txt(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.read().split('\n')
            self.height = len(lines)
            self.width = len(lines[0])
            self.pixels = numpy.zeros(self.width*self.height, dtype=int).reshape(self.height, self.width)
            x = 0; y = 0;
            for line in lines:
                for c in line:
                    self.pixels[y][x] = int(c, 16)
                    x += 1
                y += 1
                x = 0

    def save_raster(self, ext):
        image = Image.new('1', (self.width, self.height))
        image.putdata(self.pixels.reshape(self.width * self.height).tolist())
        print(ext)
        image.save(os.path.join(os.getcwd(), 'pixels.' + ext), optimize=True, lossless=True)
#        image.save(os.path.join(os.getcwd(), 'pixels.' + ext), optimize=True, lossless=True, transparency=0)
    def load_png(self, file_path):
        image = Image.open(file_path, mode='r')
        image = image.convert('1')
        self.pixels = numpy.array(list(map(lambda x: 0 if 0 == x else 1, list(image.getdata())))).reshape(image.size[1], image.size[0])
        self.width, self.height = image.size
    def load_gif(self, file_path): # 値が0/255で出力されてしまうので0/1に変換する
        image = Image.open(file_path, mode='r')
        self.width, self.height = image.size
        self.pixels = numpy.array(list(map(lambda x: 0 if 0 == x else 1, list(image.getdata())))).reshape(self.height, self.width)
    def load_webp(self, file_path): # 値が[0,0,0]/[255,255,255]で出力されてしまうので0/1に変換する
        image = Image.open(file_path, mode='r')
        self.width, self.height = image.size
        self.pixels = numpy.array(list(map(lambda x: 0 if (0,0,0) == x else 1, list(image.getdata())))).reshape(self.height, self.width)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())

