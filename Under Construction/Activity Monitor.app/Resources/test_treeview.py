import sys
from collections import deque
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import psutil

from utility import bytes2human
from collections import namedtuple

class view(QWidget):
    def __init__(self):
        super(view, self).__init__()
        self.tree_view_model = None
        self.process_tree = None

        self.setupUi()

        tree_list = self.transverse_tree()
        print('tree_list saved from QTreeview:')
        for row in tree_list:
            print(row)

    def setupUi(self):
        self.process_tree = QTreeView(self)
        self.process_tree.setUniformRowHeights(True)
        self.process_tree.setAlternatingRowColors(True)

        # self.process_tree.header().setDefaultSectionSize(180)

        layout = QVBoxLayout(self)
        layout.addWidget(self.process_tree)

        self.importData()



    # Function to save populate treeview with a dictionary
    def importData(self):
        self.tree_view_model = QStandardItemModel()
        self.tree_view_model.setRowCount(0)

        data = []
        for p in psutil.process_iter():
            data.append(
                {
                    'unique_id': p.pid,
                    'parent_id': p.ppid(),
                    'process': p

                }, )

        seen = {}   # List of  QStandardItem
        values = deque(data)
        while values:
            value = values.popleft()
            if value['parent_id'] == 0:
                parent = self.tree_view_model.invisibleRootItem()
            else:
                pid = value['parent_id']
                if value['parent_id'] not in seen:
                    values.append(value)
                    continue
                try:
                    parent = seen[pid]
                except KeyError as e:
                    print(e)
                    pass

            unique_id = value['unique_id']

            p = value['process']

            row = []
            # PID can't be disabled because it is use for selection tracking
            item = QStandardItem(f"{p.pid}")
            item.setData(p.pid, Qt.UserRole)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.append(item)

            item = QStandardItem(p.name())
            item.setData(p.name(), Qt.UserRole)
            row.append(item)

            item = QStandardItem(p.username())
            item.setData(p.username(), Qt.UserRole)
            row.append(item)

            data = p.cpu_percent()
            item = QStandardItem(f"{data}")
            item.setData(data, Qt.UserRole)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.append(item)

            item = QStandardItem(f"{p.num_threads()}")
            item.setData(p.num_threads(), Qt.UserRole)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.append(item)

            item = QStandardItem(bytes2human(p.memory_info().rss))
            item.setData(p.memory_info().rss, Qt.UserRole)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.append(item)

            item = QStandardItem(bytes2human(p.memory_info().vms))
            item.setData(p.memory_info().vms, Qt.UserRole)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.append(item)

            parent.appendRow(row)

            seen[unique_id] = parent.child(parent.rowCount() - 1)

        self.set_treeview_headers()

        # Impose the Model to TreeView Processes
        self.tree_view_model.setSortRole(Qt.UserRole)
        self.process_tree.setSortingEnabled(False)
        self.process_tree.setModel(self.tree_view_model)
        self.process_tree.setSortingEnabled(True)
        self.process_tree.expandAll()

    # Function to transverse treeview and derive tree_list
    def transverse_tree(self):
        tree_list = []
        for i in range(self.tree_view_model.rowCount()):
            item = self.tree_view_model.item(i)
            level = 0
            self.GetItem(item, level, tree_list)
        return tree_list

    def GetItem(self, item, level, tree_list):
        if item != None:
            if item.hasChildren():
                level = level + 1
                id = 0

                pid = ' '
                name = " "
                username = " "
                cpu_percent = " "
                num_threads = " "
                rms = " "
                vms = " "

                for i in range(item.rowCount()):
                    id = id + 1
                    for j in range(6, -1, -1):
                        childitem = item.child(i, j)
                        if childitem != None:
                            if j == 0:
                                pid = childitem.data(0)
                            else:
                                pid = pid
                            if j == 1:
                                name = childitem.data(0)
                            else:
                                name = name
                            if j == 2:
                                username = childitem.data(0)
                            else:
                                username = username
                            if j == 3:
                                cpu_percent = childitem.data(0)
                            else:
                                cpu_percent = cpu_percent
                            if j == 4:
                                num_threads = childitem.data(0)
                            else:
                                num_threads = num_threads
                            if j == 5:
                                rms = childitem.data(0)
                            else:
                                rms = rms
                            if j == 6:
                                vms = childitem.data(0)

                            else:
                                vms = vms
                            if j == 0:
                                Process = namedtuple(
                                    "Process",
                                    "level id pid name username cpu_percent num_threads rms vms"
                                )
                                process = Process(
                                    level,
                                    id,
                                    pid,
                                    name,
                                    username,
                                    cpu_percent,
                                    num_threads,
                                    rms,
                                    vms
                                )
                                # dic = {}
                                # dic['level'] = level
                                # dic['id'] = id
                                # dic['pid'] = pid
                                # dic['name'] = name
                                # dic['username'] = username
                                # dic['cpu_percent'] = cpu_percent
                                # dic['num_threads'] = num_threads
                                # dic['rms'] = rms
                                # dic['vms'] = vms
                                # tree_list.append(dic)
                                tree_list.append(process)
                            self.GetItem(childitem, level, tree_list)
                return tree_list

    def set_treeview_headers(self):
        self.tree_view_model.setHorizontalHeaderLabels(
            ['PID', 'Process Name', 'User', "% CPU", "# Threads", "Real Memory", "Virtual Memory"]
        )


if __name__ == '__main__':

    app = QApplication(sys.argv)
    view = view()
    view.setGeometry(300, 100, 600, 300)
    view.setWindowTitle('QTreeview Example')
    view.show()
    sys.exit(app.exec_())