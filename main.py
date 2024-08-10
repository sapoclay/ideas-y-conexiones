"""
Este módulo proporciona una aplicación gráfica basada en PyQt5 para crear y visualizar ideas conectadas mediante un 
mapa mental. Permite a los usuarios crear ideas representadas como rectángulos, conectarlas con flechas y editar el 
texto de las ideas y las conexiones.

Clases:
--------
- EditableTextItem(QGraphicsTextItem): Representa un texto editable en la escena gráfica.
- IdeaItem(QGraphicsRectItem): Representa una idea como un rectángulo con texto en la escena gráfica.
- ConnectionItem(QGraphicsPathItem): Representa una conexión entre dos IdeaItems con una flecha y texto editable.
- HelpWindow(QWidget): Muestra una ventana con las instrucciones de uso del programa.
- MainWindow(QMainWindow): Ventana principal de la aplicación que gestiona la interfaz de usuario y la lógica de las ideas y conexiones.

Uso:
-----
Para ejecutar el programa, simplemente ejecute el archivo. Se abrirá una ventana que permite al usuario añadir, 
conectar, editar, eliminar ideas y conexiones, y guardar o cargar el trabajo realizado. El programa también permite 
exportar el mapa mental a un archivo PDF.

Ejemplo de uso:
-----------------
    python main.py

Métodos:
---------
- EditableTextItem.mouseDoubleClickEvent(event): Permite editar el texto al hacer doble clic.
- EditableTextItem.focusOutEvent(event): Desactiva la edición cuando el texto pierde el foco.
- IdeaItem.update_size(event=None): Ajusta el tamaño del rectángulo basado en el texto contenido.
- IdeaItem.keyPressEvent(event): Maneja teclas específicas para actualizar el tamaño del rectángulo o eliminarlo.
- IdeaItem.mouseDoubleClickEvent(event): Permite editar el texto al hacer doble clic.
- IdeaItem.mouseReleaseEvent(event): Actualiza las posiciones de las conexiones al soltar el ratón.
- IdeaItem.set_color(color): Cambia el color del rectángulo.
- IdeaItem.to_dict(): Serializa el objeto IdeaItem en un diccionario.
- IdeaItem.from_dict(cls, data, window): Deserializa un objeto IdeaItem desde un diccionario.
- ConnectionItem.update_position(): Actualiza la posición de la conexión según las posiciones de los rectángulos conectados.
- ConnectionItem.draw_straight_connection(start_point, end_point): Dibuja una conexión recta entre dos rectángulos.
- ConnectionItem.draw_loop_connection(rect_center): Dibuja una conexión en bucle para conectar un rectángulo consigo mismo.
- ConnectionItem.update_arrow_and_text(end_point, angle, midpoint=None): Actualiza la posición de la flecha y del texto.
- ConnectionItem.keyPressEvent(event): Maneja la eliminación de la conexión al presionar la tecla de suprimir.
- ConnectionItem.to_dict(): Serializa el objeto ConnectionItem en un diccionario.
- ConnectionItem.from_dict(cls, data, scene, item_dict): Deserializa un objeto ConnectionItem desde un diccionario.
- HelpWindow.__init__(): Inicializa la ventana de ayuda con instrucciones de uso.
- MainWindow.__init__(): Inicializa la ventana principal con la interfaz de usuario.
- MainWindow.initUI(): Configura los menús y la barra de herramientas.
- MainWindow.create_toolbar(): Crea y configura la barra de herramientas de la aplicación.
- MainWindow.add_idea(): Añade una nueva idea a la escena gráfica.
- MainWindow.find_free_position(width, height): Encuentra una posición libre en la escena gráfica para colocar una nueva idea.
- MainWindow.add_connection(): Añade una conexión entre dos ideas en la escena gráfica.
- MainWindow.change_color(): Cambia el color de la idea seleccionada.
- MainWindow.update_connections(): Actualiza todas las conexiones en la escena gráfica.
- MainWindow.remove_idea(idea_item): Elimina una idea y sus conexiones asociadas de la escena gráfica.
- MainWindow.remove_connection(connection_item): Elimina una conexión de la escena gráfica.
- MainWindow.clear_all(): Elimina todas las ideas y conexiones de la escena gráfica.
- MainWindow.save_file(): Guarda el mapa de ideas en un archivo JSON.
- MainWindow.load_file(): Carga un mapa de ideas desde un archivo JSON.
- MainWindow.show_about(): Muestra una ventana con información sobre el programa.
- MainWindow.export_to_pdf(): Exporta el mapa de ideas a un archivo PDF.
- MainWindow.closeEvent(event): Pregunta al usuario si desea salir de la aplicación y maneja la salida.

Ejecutando la aplicación:
--------------------------
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
"""

import sys
import math
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, 
                             QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPathItem, 
                             QGraphicsTextItem, QLabel, QColorDialog, QAction, 
                             QMessageBox, QFileDialog, QHBoxLayout, QSpacerItem, QSizePolicy, QToolBar, QTextEdit, QSystemTrayIcon, QMenu)
from PyQt5.QtGui import QPen, QBrush, QFontMetrics, QPolygonF, QColor, QIntValidator, QPainterPath, QPainter, QPixmap, QIcon
from PyQt5.QtCore import Qt, QRect, QRectF, QPointF
from PyQt5.QtPrintSupport import QPrinter
from pathlib import Path

# Clase EditableTextItem
class EditableTextItem(QGraphicsTextItem):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setDefaultTextColor(Qt.blue)
        self.setFlag(QGraphicsTextItem.ItemIsMovable)
        self.setFlag(QGraphicsTextItem.ItemIsSelectable)
        self.setTextInteractionFlags(Qt.NoTextInteraction)

    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus()
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().focusOutEvent(event)

# Clase IdeaItem
class IdeaItem(QGraphicsRectItem):
    def __init__(self, number, text, x, y, window):
        super().__init__(0, 0, 100, 50)
        self.window = window
        self.number = number
        self.setPos(x, y)
        self.setBrush(QBrush(Qt.yellow))
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemIsFocusable)

        self.text_item = QGraphicsTextItem(f"{number}: {text}", self)
        self.text_item.setPos(10, 15)
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text_item.focusOutEvent = self.update_size

        self.update_size()

    def update_size(self, event=None):
        text = self.text_item.toPlainText()
        metrics = QFontMetrics(self.text_item.font())

        current_width = self.rect().width()
        lines = text.split('\n')
        max_line_width = max(metrics.horizontalAdvance(line) for line in lines) + 10
        new_width = max(current_width, max(100, max_line_width))
        self.text_item.setTextWidth(new_width - 20)

        text_rect = metrics.boundingRect(QRect(0, 0, int(new_width - 40), 0), Qt.TextWordWrap, text)
        new_height = max(50, text_rect.height() + 40)
        self.setRect(0, 0, new_width, new_height)
        self.text_item.setPos(10, 15)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.update_size()
            self.text_item.setTextInteractionFlags(Qt.NoTextInteraction)
            self.clearFocus()
        elif event.key() == Qt.Key_Delete:
            self.window.remove_idea(self)
        else:
            super().keyPressEvent(event)
            self.update_size()

    def mouseDoubleClickEvent(self, event):
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text_item.setFocus()
        super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.window.update_connections()

    def set_color(self, color):
        self.setBrush(QBrush(color))

    def to_dict(self):
        return {
            "number": self.number,
            "text": self.text_item.toPlainText(),
            "x": self.pos().x(),
            "y": self.pos().y(),
            "color": self.brush().color().name()
        }

    @classmethod
    def from_dict(cls, data, window):
        idea_item = cls(data['number'], data['text'], data['x'], data['y'], window)
        idea_item.set_color(QColor(data['color']))
        return idea_item

# Clase ConnectionItem
class ConnectionItem(QGraphicsPathItem):
    def __init__(self, start_item, end_item, scene, text="[Editar]"):
        super().__init__()
        self.start_item = start_item
        self.end_item = end_item
        self.arrow = None
        self.text_item = None
        self.connection_text = text

        self.setFlag(QGraphicsPathItem.ItemIsSelectable)
        self.setFlag(QGraphicsPathItem.ItemIsFocusable)

        scene.addItem(self)
        self.update_position()

    def update_position(self):
        start_point = self.start_item.pos() + self.start_item.rect().center()
        end_point = self.end_item.pos() + self.end_item.rect().center()

        if self.start_item == self.end_item:
            self.draw_loop_connection(start_point)
        else:
            self.draw_straight_connection(start_point, end_point)

        self.setPen(QPen(Qt.black, 2))
        
    def draw_straight_connection(self, start_point, end_point):
        path = QPainterPath()

        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        angle = math.atan2(dy, dx)

        edge_offset = min(self.start_item.rect().width(), self.start_item.rect().height()) / 2
        adjusted_start_point = start_point + QPointF(edge_offset * math.cos(angle), edge_offset * math.sin(angle))

        edge_offset = min(self.end_item.rect().width(), self.end_item.rect().height()) / 2
        adjusted_end_point = end_point - QPointF(edge_offset * math.cos(angle), edge_offset * math.sin(angle))

        path.moveTo(adjusted_start_point)
        path.lineTo(adjusted_end_point)

        self.setPath(path)
        self.update_arrow_and_text(adjusted_end_point, angle)

    def draw_loop_connection(self, rect_center):
        rect = self.start_item.rect()
        path = QPainterPath()

        start_offset = QPointF(rect.width() / 2, rect.height() / 2)
        end_offset = QPointF(-rect.width() / 2, rect.height() / 2)

        start_point = rect_center + start_offset
        end_point = rect_center + end_offset

        loop_size = rect.width() * 0.75

        path.moveTo(start_point)

        path.lineTo(start_point.x(), start_point.y() + loop_size) 
        path.lineTo(end_point.x(), start_point.y() + loop_size)
        path.lineTo(end_point.x(), end_point.y())

        self.setPath(path)

        midpoint = path.pointAtPercent(0.5)
        self.update_arrow_and_text(end_point, -math.pi / 2, midpoint)

    def update_arrow_and_text(self, end_point, angle, midpoint=None):
        if self.text_item is None:
            self.text_item = EditableTextItem(self.connection_text)
            self.scene().addItem(self.text_item)

        arrow_size = 10
        arrow_p1 = end_point
        arrow_p2 = arrow_p1 - QPointF(arrow_size * math.cos(angle - math.pi / 6), arrow_size * math.sin(angle - math.pi / 6))
        arrow_p3 = arrow_p1 - QPointF(arrow_size * math.cos(angle + math.pi / 6), arrow_size * math.sin(angle + math.pi / 6))

        arrow_head = QPolygonF([arrow_p1, arrow_p2, arrow_p3])
        if self.arrow:
            self.scene().removeItem(self.arrow)
        self.arrow = self.scene().addPolygon(arrow_head, QPen(Qt.black), QBrush(Qt.black))

        if midpoint is None:
            midpoint = self.path().pointAtPercent(0.5)

        offset = 10
        if -math.pi / 2 < angle < math.pi / 2:
            text_position = midpoint + QPointF(0, -offset)
        else:
            text_position = midpoint + QPointF(0, offset)

        self.text_item.setPos(text_position)
        self.text_item.setTextInteractionFlags(Qt.NoTextInteraction)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.window.remove_connection(self)
        else:
            super().keyPressEvent(event)

    def to_dict(self):
        return {
            "start_item": self.start_item.number,
            "end_item": self.end_item.number,
            "text": self.text_item.toPlainText()
        }

    @classmethod
    def from_dict(cls, data, scene, item_dict):
        start_item = item_dict[data['start_item']]
        end_item = item_dict[data['end_item']]
        connection_item = cls(start_item, end_item, scene, data['text'])
        return connection_item

# Clase HelpWindow para mostrar las instrucciones
class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cómo utilizar el programa")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout(self)

        instructions = QTextEdit(self)
        instructions.setReadOnly(True)  # Para que el texto sea solo de lectura

        # Texto de instrucciones
        help_text = """
        <h2>Instrucciones de Uso</h2>
        <p>Este programa permite crear ideas y conectarlas visualmente.</p>

        <h3>Añadir Ideas</h3>
        <ul>
            <li>Para añadir una idea, escribe el texto en el campo "Idea" en la barra de herramientas y haz clic en "Añadir Idea".</li>
            <li>Las ideas aparecerán como cuadros amarillos en la pantalla, que se pueden mover y editar.</li>
        </ul>

        <h3>Conectar Ideas</h3>
        <ul>
            <li>Para conectar dos ideas, introduce los números correspondientes a las ideas en los campos "Conectar de (número)" y "a (número)", y haz clic en "Añadir Conexión".</li>
            <li>Las conexiones se dibujarán como líneas entre las ideas, y puedes añadir texto a las conexiones haciendo doble clic en el texto "[Editar]".</li>
            <li>Los botones de las conexiones pueden verse utilizando en el botón desplegable del lado derecho. Este botón se muestra cuando no utilicemos la ventana a tamaño completo</li>
        </ul>

        <h3>Modificar Ideas y Conexiones</h3>
        <ul>
            <li>Puedes cambiar el color de una idea seleccionándola y haciendo clic en "Cambiar Color".</li>
            <li>Para eliminar una idea o conexión, selecciónala y presiona la tecla "Suprimir" en tu teclado.</li>
        </ul>

        <h3>Guardar y Cargar</h3>
        <ul>
            <li>Puedes guardar tu trabajo seleccionando "Guardar" en el menú "Archivo" de formato Json.</li>
            <li>También nos va a permitir "Guardar" nuestro proyecto como PDF.
            <li>Para cargar un archivo guardado previamente como archivo .json, selecciona "Cargar" en el menú "Archivo".</li>
        </ul>
        

        <h3>Otras Funciones</h3>
        <ul>
            <li>Puedes empezar un nuevo proyecto seleccionando "Nuevo" en el menú "Archivo".</li>
            <li>Para salir del programa, selecciona "Salir" en el menú "Archivo".</li>
        </ul>
        """

        instructions.setHtml(help_text)  # Configurar el texto HTML
        layout.addWidget(instructions)

# Clase MainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ideas y Conexiones")
        self.setGeometry(100, 100, 800, 600)
        
                 # Directorio del script actual
        current_directory = Path(__file__).parent

        # Establecer un icono personalizado
        icon_path = current_directory / 'icono.ico'
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
            self.tray_icon = QSystemTrayIcon(QIcon(str(icon_path)), self)
            self.tray_icon.setToolTip("Mapa de Ideas - Organiza y conecta tus ideas visualmente")

            # Crear un menú para el icono de la bandeja del sistema
            tray_menu = QMenu()
            restore_action = QAction("Restaurar", self)
            restore_action.triggered.connect(self.restore)
            tray_menu.addAction(restore_action)
            
            # Acción para abrir la ventana Acerca de
            about_action = QAction("Acerca de", self)
            about_action.triggered.connect(self.show_about)
            tray_menu.addAction(about_action)
            
            # Acción para mostrar la ayuda
            help_action = QAction("Cómo usar el programa", self)
            help_action.triggered.connect(self.show_instructions)
            tray_menu.addAction(help_action)
            

            exit_action = QAction("Salir", self)
            exit_action.triggered.connect(self.close)
            tray_menu.addAction(exit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()

        self.view = QGraphicsView()
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)

        self.idea_counter = 1
        self.ideas = []
        self.connections = []

        self.initUI()

    def initUI(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Archivo")
        
        export_action = QAction("Exportar a PDF", self)
        export_action.triggered.connect(self.export_to_pdf)
        file_menu.addAction(export_action)

        save_action = QAction("Guardar", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        load_action = QAction("Cargar", self)
        load_action.triggered.connect(self.load_file)
        file_menu.addAction(load_action)

        clear_action = QAction("Nuevo", self)
        clear_action.triggered.connect(self.clear_all)
        file_menu.addAction(clear_action)

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Ayuda")

        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Añadir la nueva opción "Cómo usar el programa" en el menú Ayuda
        instructions_action = QAction("Cómo usar el programa", self)
        instructions_action.triggered.connect(self.show_instructions)
        help_menu.addAction(instructions_action)

        self.create_toolbar()
    
    # Restaurar el foco sobre la ventana del programa
    def restore(self):
        if self.isMinimized():
            self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
        self.showNormal()
        self.activateWindow()
        
    # Método para mostrar la ventana de instrucciones
    def show_instructions(self):
        self.help_window = HelpWindow()
        self.help_window.show()

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # Primera línea
        first_line_widget = QWidget()
        first_line_layout = QHBoxLayout(first_line_widget)
        
        idea_label = QLabel("Idea:")
        first_line_layout.addWidget(idea_label)

        self.idea_input = QLineEdit(self)
        first_line_layout.addWidget(self.idea_input)

        add_idea_btn = QPushButton("Añadir Idea", self)
        add_idea_btn.clicked.connect(self.add_idea)
        first_line_layout.addWidget(add_idea_btn)

        color_btn = QPushButton("Cambiar Color", self)
        color_btn.clicked.connect(self.change_color)
        first_line_layout.addWidget(color_btn)

        first_line_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        toolbar.addWidget(first_line_widget)

        # Segunda línea
        second_line_widget = QWidget()
        second_line_layout = QHBoxLayout(second_line_widget)

        connection_label = QLabel("Conectar de (número):")
        second_line_layout.addWidget(connection_label)

        self.start_idea_input = QLineEdit(self)
        self.start_idea_input.setValidator(QIntValidator())
        self.start_idea_input.setMaximumWidth(50)
        second_line_layout.addWidget(self.start_idea_input)

        to_label = QLabel("a (número):")
        second_line_layout.addWidget(to_label)

        self.end_idea_input = QLineEdit(self)
        self.end_idea_input.setValidator(QIntValidator())
        self.end_idea_input.setMaximumWidth(50)
        second_line_layout.addWidget(self.end_idea_input)

        add_connection_btn = QPushButton("Añadir Conexión", self)
        add_connection_btn.clicked.connect(self.add_connection)
        second_line_layout.addWidget(add_connection_btn)

        second_line_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        toolbar.addWidget(second_line_widget)

    def add_idea(self):
        text = self.idea_input.text()
        if text:
            x, y = self.find_free_position(100, 50)
            idea_item = IdeaItem(self.idea_counter, text, x, y, self)
            self.ideas.append(idea_item)
            self.scene.addItem(idea_item)
            self.idea_counter += 1
            self.idea_input.clear()

    def find_free_position(self, width, height):
        padding = 20  # Espacio adicional alrededor de cada idea
        x, y = 100, 100  # Posición inicial tentativa
        while True:
            collision = False
            for idea in self.ideas:
                idea_rect = idea.sceneBoundingRect()
                new_rect = QRectF(x, y, width + padding, height + padding)
                if idea_rect.intersects(new_rect):
                    collision = True
                    break
            if collision:
                x += width + padding  # Mueve a la derecha si hay colisión
                if x + width > self.scene.width():  # Si se sale del borde derecho
                    x = 100  # Reinicia la x
                    y += height + padding  # Baja una línea
            else:
                return x, y

    def add_connection(self):
        try:
            start_num = int(self.start_idea_input.text())
            end_num = int(self.end_idea_input.text())

            start_item = next(item for item in self.ideas if item.number == start_num)
            end_item = next(item for item in self.ideas if item.number == end_num)

            connection_item = ConnectionItem(start_item, end_item, self.scene)
            self.connections.append(connection_item)

        except StopIteration:
            QMessageBox.warning(self, "Error", "Idea no encontrada.")
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor, ingrese números válidos.")

    def change_color(self):
        selected_items = self.scene.selectedItems()
        if selected_items:
            color = QColorDialog.getColor()
            if color.isValid():
                for item in selected_items:
                    if isinstance(item, IdeaItem):
                        item.set_color(color)

    def update_connections(self):
        for connection in self.connections:
            connection.update_position()

    def remove_idea(self, idea_item):
        self.scene.removeItem(idea_item)
        self.ideas.remove(idea_item)
        connections_to_remove = [conn for conn in self.connections if conn.start_item == idea_item or conn.end_item == idea_item]
        for conn in connections_to_remove:
            self.remove_connection(conn)

    def remove_connection(self, connection_item):
        self.scene.removeItem(connection_item)
        self.scene.removeItem(connection_item.arrow)
        self.scene.removeItem(connection_item.text_item)
        self.connections.remove(connection_item)

    def clear_all(self):
        self.scene.clear()
        self.idea_counter = 1
        self.ideas = []
        self.connections = []

    def save_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar Mapa de Ideas", "", "Archivos JSON (*.json)", options=options)
        if file_name:
            if not file_name.endswith(".json"):
                file_name += ".json"
            data = {
                "ideas": [idea.to_dict() for idea in self.ideas],
                "connections": [connection.to_dict() for connection in self.connections]
            }
            with open(file_name, 'w') as file:
                json.dump(data, file)

    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Cargar Mapa de Ideas", "", "Archivos JSON (*.json)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                data = json.load(file)
                self.clear_all()
                item_dict = {}
                for idea_data in data["ideas"]:
                    idea_item = IdeaItem.from_dict(idea_data, self)
                    self.ideas.append(idea_item)
                    self.scene.addItem(idea_item)
                    item_dict[idea_item.number] = idea_item
                    self.idea_counter = max(self.idea_counter, idea_item.number + 1)
                for connection_data in data["connections"]:
                    connection_item = ConnectionItem.from_dict(connection_data, self.scene, item_dict)
                    self.connections.append(connection_item)

    def show_about(self):
        about_message_box = QMessageBox(self)
        about_message_box.setWindowTitle("Sobre el programa")
        about_message_box.setIconPixmap(QPixmap("logo.png"))

        about_message_box.setText(
            "<br/>"
            "<h2>Ideas y Conexiones</h2>"
            "<p>Versión 0.5</p>"
            "<p>Una aplicación para crear y conectar ideas entre si.</p>"
            "<p><a href='https://github.com/sapoclay/ideas-y-conexiones'>Visita el repositorio en GitHub</a></p>"
        )

        about_message_box.setStandardButtons(QMessageBox.Ok)
        about_message_box.exec_()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Confirmar Salida', '¿Estás seguro de que quieres salir?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            
    def export_to_pdf(self):
        # Abrir un cuadro de diálogo para seleccionar la ubicación del archivo PDF
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar como PDF", "", "PDF Files (*.pdf)", options=options)
        
        if file_path:
            # Asegurarse de que la extensión sea .pdf
            if not file_path.endswith('.pdf'):
                file_path += '.pdf'
            
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)

            painter = QPainter(printer)
            # Escalar la vista a la página del PDF
            self.view.render(painter)
            painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())