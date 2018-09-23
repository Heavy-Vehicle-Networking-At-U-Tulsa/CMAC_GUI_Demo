from PyQt5.QtWidgets import (QMainWindow,
                             QWidget,
                             QTreeView,
                             QMessageBox,
                             QFileDialog,
                             QLabel,
                             QSlider,
                             QCheckBox,
                             QLineEdit,
                             QVBoxLayout,
                             QApplication,
                             QPushButton,
                             QTableWidget,
                             QTableView,
                             QTableWidgetItem,
                             QScrollArea,
                             QAbstractScrollArea,
                             QAbstractItemView,
                             QSizePolicy,
                             QGridLayout,
                             QGroupBox,
                             QComboBox,
                             QAction,
                             QDockWidget,
                             QDialog,
                             QFrame,
                             QDialogButtonBox,
                             QInputDialog,
                             QProgressDialog,
                             QTabWidget)
from PyQt5.QtCore import Qt, QTimer, QAbstractTableModel, QCoreApplication, QSize
from PyQt5.QtGui import QIcon

import sys
import threading
import queue
import time
import serial

from Graphing.graphing import *

class ReadSerialMessageThread(threading.Thread):
    def __init__(self, rx_queue):
        threading.Thread.__init__(self)
        self.rx_queue = rx_queue
        self.ser = serial.Serial(port="COM8", baudrate=9600) # <-- Change thisserial_port
        self.runSignal = True
        self.message_count = 0
        print("Started ReadSerialMessageThread")

    def run(self):
        while self.runSignal:
            serial_data = self.ser.readline().decode('ascii','ignore')
            serial_data = serial_data.strip() #remove leading and trailing whitespace
            print(serial_data)
            serial_data_items = serial_data.split("*") #Converts to a list delimited by a character
            self.rx_queue.put(serial_data_items)
            self.message_count += 1
        self.ser.close()
        self.ser.__del__()
        print("Exiting ReadSerialMessageThread")
        

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        
        self.setWindowTitle("S32K Demo")
        self.statusBar().showMessage("Welcome!")

        self.grid_layout = QGridLayout()
        
        self.setup_threads()

        # Build common menu options
        menubar = self.menuBar()
        # Serial Menu Items
        COM_menu = menubar.addMenu('&COM')
        
        stop_comms = QAction( '&Quit Serial', self)
        stop_comms.setShortcut('Ctrl+Q')
        stop_comms.setStatusTip('Stop the serial communications.')
        stop_comms.triggered.connect(self.stop_comms)
        COM_menu.addAction(stop_comms)
        

        self.high_res_graph = GraphWidget(self)
        self.high_res_graph.set_yrange(9, 15)
        self.high_res_graph.set_xlabel("Time")
        self.high_res_graph.set_ylabel("Voltage")
        self.high_res_graph.set_title("Battery Voltage Measurements from Vehicle Electronic Control Units")
        self.high_res_graph.show()

        self.grid_layout.addWidget(self.high_res_graph)

        main_widget = QWidget()
        main_widget.setLayout(self.grid_layout)
        self.setCentralWidget(main_widget)
        

        self.show()

        read_timer = QTimer(self)
        read_timer.timeout.connect(self.read_serial_thread)
        read_timer.start(250) #milliseconds
    
    def stop_comms(self):
        self.read_message_thread.runSignal = False
        print("Sent serial message thread a stop signal.")   

    def setup_threads(self):
        #setup a Receive queue. This keeps the GUI responsive and enables messages to be received.
        self.rx_queue = queue.Queue(10000)
        self.read_message_thread = ReadSerialMessageThread(self.rx_queue)
        self.read_message_thread.setDaemon(True) #needed to close the thread when the application closes.
        self.read_message_thread.start()
                    
    def read_serial_thread(self):
        self.statusBar().showMessage("Serial Message Count: {}".format(self.read_message_thread.message_count))
        new_data = False
        while self.rx_queue.qsize():
            #Get a message from the queue. These are raw bytes
            #if not protocol == "J1708":
            rxmessage = self.rx_queue.get()
            # Remove this if needed.
            self.high_res_graph.data_table.setItem(0, 1, QTableWidgetItem("{}".format(rxmessage)))
            
            #Resize things to fill in the gaps.
            #self.high_res_graph.data_table.resizeColumnsToContents()
            #self.high_res_graph.data_table.horizontalHeader().setStretchLastSection(True)

            try:
                X = rxmessage[0]
                Y = rxmessage[1]
                #Add the data to the cells in the table widget
                self.high_res_graph.data_table.setItem(1, 0, QTableWidgetItem("{}".format(X)))
                self.high_res_graph.data_table.setItem(1, 1, QTableWidgetItem("{}".format(Y)))

                # Add the data to the plotter
                self.high_res_graph.add_data( (X,Y), marker = 'o-', label="Label for Y" )
                new_data = True
            except IndexError:
                print("Needs a list with X and Y. Received: {}".format(rxmessage))
        # after finishing unloading the queue, we can plot the data.
        if new_data:
            self.high_res_graph.plot()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    execute = MainWindow()
    sys.exit(app.exec_())