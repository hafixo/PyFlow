from Settings import *
from PySide import QtGui
from PySide import QtCore
from Port import Port
from AbstractGraph import *


class NodeName(QtGui.QGraphicsTextItem):
    def __init__(self, name, parent, color=Colors.kNodeNameRect):
        QtGui.QGraphicsTextItem.__init__(self)
        self.object_type = AGObjectTypes.tNodeName
        self.name = name
        self.color = color
        self.setPlainText(self.name)
        self.setParentItem(parent)
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.setCursor(QtCore.Qt.IBeamCursor)
        self.options = self.parentItem().graph().get_settings()
        if self.options:
            self.opt_bg_color = QtGui.QColor(self.options.value('NODES/Nodes label bg color'))
            self.text_color = QtGui.QColor(self.options.value('NODES/Nodes label font color'))
            self.setDefaultTextColor(self.text_color)
            self.opt_font = QtGui.QFont(self.options.value('NODES/Nodes label font'))
            self.opt_font_size = int(self.options.value('NODES/Nodes label font size'))
            self.opt_font.setPointSize(self.opt_font_size)
            self.setFont(self.opt_font)
        self.setPos(0, -self.boundingRect().height())

    def keyPressEvent(self, event):
        key = event.key()
        if (key == QtCore.Qt.Key_Return) or (key == QtCore.Qt.Key_Escape):
            self.setEnabled(False)
            self.setEnabled(True)
            return
        else:
            QtGui.QGraphicsTextItem.keyPressEvent(self, event)

    def paint(self, painter, option, widget):
        if self.options:
            painter.fillRect(option.rect, QtGui.QColor(self.opt_bg_color))
        else:
            painter.fillRect(option.rect, QtGui.QColor(self.color))
        super(NodeName, self).paint(painter, option, widget)

    def focusInEvent(self, event):
        self.parentItem().graph.disable_sortcuts()

    def focusOutEvent(self, event):
        self.parentItem().graph.enable_sortcuts()

        if self.parentItem().name == self.toPlainText():
            super(NodeName, self).focusOutEvent(event)
            return
        new_name = self.parentItem().graph.get_uniq_node_name(self.toPlainText())
        self.name = new_name
        self.parentItem().label.setPlainText(new_name)

        for i in self.parentItem().get_input_edges().iterkeys():
            if self.name == i.connection['From'].split('.')[0]:
                i.connection['From'] = i.connection['From'].replace(self.name, new_name)
            if self.name == i.connection['To'].split('.')[0]:
                i.connection['To'] = i.connection['To'].replace(self.name, new_name)
        for i in self.parentItem().get_output_edges().iterkeys():
            if self.name == i.connection['From'].split('.')[0]:
                i.connection['From'] = i.connection['From'].replace(self.name, new_name)
            if self.name == i.connection['To'].split('.')[0]:
                i.connection['To'] = i.connection['To'].replace(self.name, new_name)
        new_name = new_name.replace(" ", "_")
        self.parentItem().set_name(new_name)
        super(NodeName, self).focusOutEvent(event)


class Node(QtGui.QGraphicsItem, AGNode):
    """
    Default node description
    """
    def __init__(self, name, graph, w=120, colors=Colors, spacings=Spacings, port_types=AGPortTypes, addHeader=True):
        AGNode.__init__(self, name, graph)
        QtGui.QGraphicsItem.__init__(self)
        self.options = self.graph().get_settings()
        if self.options:
            self.opt_node_base_color = QtGui.QColor(self.options.value('NODES/Nodes base color'))
            self.opt_selected_pen_color = QtGui.QColor(self.options.value('NODES/Nodes selected pen color'))
            self.opt_lyt_a_color = QtGui.QColor(self.options.value('NODES/Nodes lyt A color'))
            self.opt_lyt_b_color = QtGui.QColor(self.options.value('NODES/Nodes lyt B color'))
            opt_pen_selected_type_name = QtGui.QColor(self.options.value('NODES/Nodes selected pen type'))
            self.opt_pen_selected_type = get_line_type(opt_pen_selected_type_name)
        self.object_type = AGObjectTypes.tNode
        self._color_idx = 1
        self._left_stretch = 0
        self.colors = colors
        self.height_offset = 3
        self.spacings = spacings
        self.port_types = port_types
        self.nodeMainGWidget = QtGui.QGraphicsWidget()
        self.w = w
        self.h = 40
        self.sizes = [0, 0, self.w, self.h, 1, 1]
        self.setFlag(self.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.custom_widget_data = {}
        # node name
        self.label = NodeName(self.name, self)
        # set node layouts
        self.nodeMainGWidget.setParentItem(self)
        # main
        self.portsMainLayout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Horizontal)
        self.portsMainLayout.setContentsMargins(1, 1, 1, 1)
        self.nodeMainGWidget.setLayout(self.portsMainLayout)
        self.nodeMainGWidget.setX(self.nodeMainGWidget.x())
        # inputs layout
        self.inputsLayout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        self.inputsLayout.setContentsMargins(1, 1, 1, 1)
        self.portsMainLayout.addItem(self.inputsLayout)

        # outputs layout
        self.outputsLayout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        self.outputsLayout.setContentsMargins(1, 1, 1, 1)
        self.portsMainLayout.addItem(self.outputsLayout)

        self.setZValue(1)
        self.setCursor(QtCore.Qt.OpenHandCursor)
        if addHeader:
            self.head = self.add_layout(True)
        self.effect = QtGui.QGraphicsDropShadowEffect()
        self.effect.setColor(Colors.kSceneBackground.lighter(50))
        self.effect.setParent(self.graph())
        self.effect.setBlurRadius(20)
        self.effect.setOffset(5, 10)
        self.effect.setEnabled(False)
        self.setGraphicsEffect(self.effect)
        self.tweakPosition()

    def tweakPosition(self):
        value = self.scenePos()
        self.setX(roundup(value.x() - self.graph().grid_size, self.graph().grid_size))
        self.setY(roundup(value.y() - self.graph().grid_size, self.graph().grid_size))

    def boundingRect(self):
        return self.childrenBoundingRect()

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            # grid snapping
            value.setX(roundup(value.x() - self.graph().grid_size + self.graph().grid_size / 3.0, self.graph().grid_size))
            value.setY(roundup(value.y() - self.graph().grid_size + self.graph().grid_size / 3.0, self.graph().grid_size))
            return value
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    @staticmethod
    def description():
        return "Default node description"

    def post_create(self):
        self.w = self.childrenBoundingRect().width() + self.spacings.kPortSpacing
        self.nodeMainGWidget.setMaximumWidth(self.childrenBoundingRect().width() + self.spacings.kPortOffset)
        self.nodeMainGWidget.setGeometry(QtCore.QRectF(0, 0, self.w + self.spacings.kPortOffset, self.h))

    def save_command(self):
        return "createNode ~type {0} ~x {1} ~y {2} ~n {3}\n".format(self.__class__.__name__, self.scenePos().x(), self.scenePos().y(), self.name)

    def property_view(self):
        return self.graph().parent.dockWidgetNodeView

    def set_name(self, name):
        AGNode.set_name(self, name)
        self.label.setPlainText(self.name)

    def set_shadows_enabled(self, state):

        self.effect.setEnabled(state)

    def clone(self):
        x = 0.0
        y = 0.0
        if self.parentItem() is None:
            x = self.pos().x() + self.boundingRect().width()
            y = self.pos().y() + self.boundingRect().height()
            new_node = self.graph().create_node(self.__class__.__name__, x, y, self.get_name())
            return new_node
        else:
            x = self.pos().x() + self.boundingRect().width() + self.parentItem().scenePos().x()
            y = self.pos().y() + self.boundingRect().height() + self.parentItem().scenePos().y()
            new_node = self.graph().create_node(self.__class__.__name__, x, y, self.get_name())
            self.parentItem().add_node(new_node)
            self.parentItem().fit_content()
            return new_node

    def update_ports(self):
        [i.update() for i in self.inputs]
        [i.update() for i in self.outputs]

    def paint(self, painter, option, widget):

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.darkGray)

        if self.options:
            color = self.opt_node_base_color
        else:
            color = self.colors.kNodeBackgrounds
        if self.isSelected():
            color = color.lighter(150)

        linearGrad = QtGui.QRadialGradient(QtCore.QPointF(40, 40), 300)
        linearGrad.setColorAt(0, color)
        linearGrad.setColorAt(1, color.lighter(180))
        br = QtGui.QBrush(linearGrad)
        painter.setBrush(br)
        pen = QtGui.QPen(QtCore.Qt.black, 0.5)
        if option.state & QtGui.QStyle.State_Selected:
            if self.options:
                pen.setColor(self.opt_selected_pen_color)
                pen.setStyle(self.opt_pen_selected_type)
            else:
                pen.setColor(Colors.kWhite)
                pen.setStyle(QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawRoundedRect(self.sizes[0], self.sizes[1],
                                self.childrenBoundingRect().width(), self.nodeMainGWidget.boundingRect().height(),
                                self.sizes[4], self.sizes[5])

    def get_input_edges(self):
        out = {}
        for i in [i.edge_list for i in self.inputs]:
            if not i.__len__() == 0:
                out[i[0]] = [e.connection for e in i]
        return out

    def get_output_edges(self):
        out = {}
        for i in [i.edge_list for i in self.outputs]:
            if not i.__len__() == 0:
                out[i[0]] = [e.connection for e in i]
        return out

    def mousePressEvent(self, event):

        self.update()
        self.setCursor(QtCore.Qt.ClosedHandCursor)
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):

        self.update()
        self.setCursor(QtCore.Qt.OpenHandCursor)
        modifiers = event.modifiers()
        selected_nodes = [n for n in self.graph().nodes if n.isSelected()]
        groupers = [i for i in self.graph().groupers if i.object_type == AGObjectTypes.tGrouper]
        grouper = [g for g in groupers if self in g.collidingItems()]
        if len(grouper) == 1:
            if not modifiers == QtCore.Qt.ControlModifier:
                grouper[0].add_from_iterable(selected_nodes)
        else:
            parent = self.parentItem()
            if parent and parent.object_type == AGObjectTypes.tGrouper:
                if self in parent.nodes:
                    parent.remove_from_iterable(selected_nodes)
                    self.setZValue(1)
                    for n in selected_nodes:
                        if n.parentItem():
                            if hasattr(n.parentItem(), 'object_type'):
                                if n.parentItem().object_type == AGObjectTypes.tGrouper:
                                    n.parentItem().remove_node(n)
        p_item = self.parentItem()
        if p_item and hasattr(p_item, 'object_type'):
            if p_item.object_type == AGObjectTypes.tGrouper:
                if p_item.auto_fit_content:
                    p_item.fit_content()
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

    def add_input_port(self, port_name, data_type):

        p = self._add_port(AGPortTypes.kInput, data_type, port_name)
        return p

    @staticmethod
    def get_category():
        return "Default"

    def add_output_port(self, port_name, data_type):

        p = self._add_port(AGPortTypes.kOutput, data_type, port_name)
        return p

    def add_layout(self, portType, head=False):

        form = QtGui.QGraphicsWidget()
        lyt = QtGui.QGraphicsLinearLayout()
        lyt.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        lyt.setContentsMargins(1, 1, 1, 1)
        form.setLayout(lyt)
        form.setAutoFillBackground(True)
        form.setPalette(QtGui.QPalette(QtCore.Qt.gray))

        if portType == AGPortTypes.kInput:
            self.inputsLayout.addItem(form)
        else:
            self.outputsLayout.addItem(form)
        return lyt

    def kill(self, call_connection_functions=False):

        for i in self.inputs + self.outputs:
            if i.hasConnections():
                i.disconnect_all()

        self.setVisible(False)
        if self.parentItem() and hasattr(self.parentItem(), 'object_type'):
            if self.parentItem().object_type == AGObjectTypes.tGrouper:
                self.parentItem().remove_node(self)
        # AGNode.kill(self, call_connection_functions)
        self.graph().write_to_console("killNode {1}nl {0}".format(self.name, FLAG_SYMBOL))
        self.scene().removeItem(self)

    def set_pos(self, x, y):

        AGNode.set_pos(self, x, y)
        self.setPos(QtCore.QPointF(x, y))

    def _add_port(self, port_type, data_type, name, color=QtGui.QColor(0, 100, 0, 255)):

        newColor = color

        if data_type == AGPortDataTypes.tNumeric:
            # set colot for numeric ports
            newColor = QtGui.QColor(0, 100, 0, 255)
        elif data_type == AGPortDataTypes.tString:
            # set colot for string ports
            newColor = QtGui.QColor(50, 0, 50, 255)
        elif data_type == AGPortDataTypes.tBool:
            # set colot for bool ports
            newColor = QtGui.QColor(100, 0, 0, 255)
        elif data_type == AGPortDataTypes.tArray:
            # set colot for bool ports
            newColor = QtGui.QColor(0, 0, 0, 255)
        else:
            newColor = QtGui.QColor(255, 255, 30, 255)

        p = Port(name, self, data_type, 10, 10, newColor)
        p.type = port_type
        connector_name = QtGui.QGraphicsProxyWidget()
        lbl = QtGui.QLabel(p.name)
        lbl.setAlignment(QtCore.Qt.AlignVCenter)
        lbl.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        if self.options:
            font = QtGui.QFont(self.options.value('NODES/Port label font'))
            color = QtGui.QColor(self.options.value('NODES/Port label color'))
            font.setPointSize(int(self.options.value('NODES/Port label size')))
            lbl.setFont(font)
            style = 'color: rgb({0}, {1}, {2}, {3});'.format(
                color.red(),
                color.green(),
                color.blue(),
                color.alpha())
            lbl.setStyleSheet(style)
        connector_name.setWidget(lbl)
        if port_type == self.port_types.kInput:
            inPortLyt = self.add_layout(port_type)
            lbl.setAlignment(QtCore.Qt.AlignLeft)
            inPortLyt.addItem(p)
            inPortLyt.addItem(connector_name)
            self.inputs.append(p)
            self.inputsLayout.insertItem(1, inPortLyt)
        elif port_type == self.port_types.kOutput:
            outPortLyt = self.add_layout(port_type)
            lbl.setAlignment(QtCore.Qt.AlignRight)
            outPortLyt.addItem(connector_name)
            outPortLyt.addItem(p)
            self.outputs.append(p)
            self.outputsLayout.insertItem(1, outPortLyt)
        return p
