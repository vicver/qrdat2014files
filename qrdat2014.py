#!/usr/bin/env python
# coding=utf-8

import sys, os, stat
import pygtk, gtk
import zbarpygtk
import pycurl
from time import strftime, localtime
import pango

class qrdat:

    def __init__(self):

        """ VARIABLES DE CONFIGURACION """
		# Prefijo para el nombre de los archivos de registros 
        prefijo = 'Registro'
		
        # Lugar de almacenamiento de archivos de registros
		# Por defecto se guarda en la carpeta personal del usuario
        directorio = os.getenv('HOME')

        # Descomentar la siguiente linea y digitar la ruta de la carpeta
        # donde se guardaran los archivos

        #directorio = '/home/olpc/Escritorio'
	
	
        # Modo de reproduccion de sonido:
        # 1 : sonido enviado directamente a la tarjeta de sonido
        # 2 : sonido de alerta del sistema

        self.beep_mode = 1

        # No modificar abajo
        self.open_file = None
        self.video_device = '/dev/video0'
        self.fecha = strftime("%Y-%m-%d",localtime())
        self.filename = directorio+'/'+prefijo+'-'+self.fecha+'.csv'

        if len(sys.argv) > 1:
            self.video_device = sys.argv[1]

    def decoded(self, zbar, data):
        """funcion invocada cuando un codigo es decodificado por el
		control zbar. 
        """
        datos = data.split(':')
        qrdata = datos[1]

        # guardar datos
        self.save(qrdata)        
        
        # sonido de recepcion
        self.beep(self.beep_mode)
        
        # mostrar datos
        buf = self.results.props.buffer
        end = buf.get_end_iter()
        buf.insert(end, self.hora()+' - '+qrdata+"\n")
        self.results.scroll_to_iter(end, 0)

    def show(self):
        """Funcion que crea muestra la ventana principal """
		
        # threads *must* be properly initialized to use zbarpygtk
        gtk.gdk.threads_init()
        gtk.gdk.threads_enter()

        window = gtk.Window()
        window.set_title("Control de Asistencia QR")
        window.set_border_width(8)
        window.connect("destroy", gtk.main_quit)

        # zbar
        self.zbar = zbarpygtk.Gtk()
        self.zbar.connect("decoded-text", self.decoded)

        self.video_device = '/dev/video0'

        self.zbar.connect("notify::video-enabled", self.video_enabled)
        self.zbar.connect("notify::video-opened", self.video_opened)

        self.zbar.set_video_device(self.video_device)

        # combine combo box and buttons horizontally
        hbox = gtk.HBox(spacing=8)

        # text box for holding results
        self.results = gtk.TextView()
        self.results.set_size_request(320, 128)
        self.results.props.editable = self.results.props.cursor_visible = False
        self.results.modify_font(pango.FontDescription("monospace 12"))
        self.results.set_left_margin(4)

        # combine inputs, scanner, and results vertically
        vbox = gtk.VBox(spacing=8)
        vbox.pack_start(hbox, expand=False)
        vbox.pack_start(self.zbar)
        vbox.pack_start(self.results, expand=False)
    
        window.add(vbox)
        window.set_geometry_hints(self.zbar, min_width=320, min_height=240)
        window.show_all()


    def run(self):
        """Funcion que inicia el funcionamiento de la ventana"""
        gtk.main()
        gtk.gdk.threads_leave()
  
    def save(self,data):
        """ Funcion que guarda el archivo de registro """
        f = open(self.filename,'a')
        f.write(self.fecha+','+self.hora()+','+data+'\n')
        f.close()

    def hora(self):
        """ Funcion que obtiene la hora local """
        return strftime("%H:%M:%S",localtime())

    def beep(self, beep_mode):

        if os.access('/dev/audio', os.W_OK ) and beep_mode == 1:
            """ Genera un sonido enviado a la tarjeta de sonido"""
            frequency = 100
            amplitude = 200
            duration = 2
            sample = 8000
            half_period = int(sample/frequency/2)
            beep = chr(amplitude)*half_period+chr(0)*half_period
            beep *= int(duration*frequency)
            audio = file('/dev/audio', 'wb')
            audio.write(beep)
            audio.close()

        else:
            """ Reproduce sonido del propio sistema """
            f=open('/dev/tty','w')
            f.write(chr(7))
            f.close()


    def video_enabled(self, zbar, param):
        """callback invoked when the zbar widget enables or disables
        video streaming.  updates the status button state to reflect the
        current video state
        """
        enabled = zbar.get_video_enabled()


    def video_opened(self, zbar, param):
        """callback invoked when the zbar widget opens or closes a video
        device.  also called when a device is closed due to error.
        updates the status button state to reflect the current video state
        """
        opened = zbar.get_video_opened()

    def video_changed(self, widget):
        """callback invoked when a new video device is selected from the
        drop-down list.  sets the new device for the zbar widget,
        which will eventually cause it to be opened and enabled
        """
        dev = self.video_list.get_active_text()
        if dev[0] == '<':
            dev = ''
        self.zbar.set_video_device(dev)

if __name__ == "__main__":

    qr = qrdat()
    qr.show()
    qr.run()
