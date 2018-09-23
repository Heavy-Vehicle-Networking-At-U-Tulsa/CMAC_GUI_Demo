
#from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMessageBox,
                             QFileDialog,
                             QLabel,
                             QGridLayout,
                             QPushButton,
                             QGroupBox,
                             QDialog,
                             QWidget,
                             QTableWidget,
                             QTableWidgetItem,
                             QAbstractItemView,
                             QHeaderView,
                             QCheckBox,
                             QVBoxLayout)
#from matplotlib.backends import qt_compat
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
#import matplotlib.pyplot as plt
import matplotlib.figure as mpl
import os
import csv


from matplotlib import rcParams
rcParams.update({'figure.autolayout': True}) #Depends on matplotlib from graphing
markers = [ "D", "o", "v", "*", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "h", "H", "+", "x", "X", "d", "|"]
 
class GraphWidget(QWidget):
    def __init__(self, parent=None):
        super(GraphWidget, self).__init__(parent)
        


        self.figure = mpl.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.data = {}

        self.ax = self.figure.add_subplot(111)
        self.ymin = None
        self.ymax = None
        self.x_label = ""
        self.y_label = ""
        self.title = ""

        # Set up the table
        # See http://doc.qt.io/qt-5/qtablewidget.html
        self.data_table = QTableWidget()
        # set row count
        self.data_table.setRowCount(2)
        self.data_table.setVerticalHeaderItem(0, QTableWidgetItem("Row 1 Label"))
        self.data_table.setVerticalHeaderItem(1, QTableWidgetItem("Row 2 Label"))
        # set column count
        self.data_table.setColumnCount(2)
        self.data_table.setHorizontalHeaderItem(0, QTableWidgetItem("Column 1 Label"))
        self.data_table.setHorizontalHeaderItem(1, QTableWidgetItem("Column 2 Label"))
        header = self.data_table.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.data_table)
        layout.addWidget(self.toolbar)
        self.setLayout(layout)
        self.show()
         
    def plot(self):
        ''' plot data '''
        self.ax.cla()
        for key, value in self.data.items():
            self.ax.plot(value["X"], value["Y"], value["Marker"],label=key)
        self.ax.grid(True)
        self.ax.legend()
        [xmin, xmax, ymin, ymax] = self.ax.axis()
        try:
            self.ax.axis([xmin, xmax, self.ymin, self.ymax])
        except:
            pass
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.set_title(self.title)
        if self.update_button.isChecked():
            self.canvas.draw()
    
    def add_data(self, data, marker='*-', label="DEFAULT LABEL"):
        x, y = zip(*data) #unpacks a list of tuples
        self.data[label] = {"X": [float(val) for val in x], 
                            "Y": [float(val) for val in y], 
                            "Marker": marker}

    def set_yrange(self,min_y, max_y):
        self.ymax = max_y
        self.ymin = min_y        
    
    def set_xlabel(self,label):
        self.x_label = label
    
    def set_ylabel(self,label):
        self.y_label = label
    
    def set_title(self,label):
        self.title = label
