#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
import gobject
from Metodos import *

class App(gtk.Builder):
    def __init__(self):
        super(App,self).__init__()
        self.add_from_file("data/buscaminas.glade")
        
        self.connect_signals(self)

        self.menu_principal = self.get_object("Menu principal")
        self.juego=self.get_object("Juego")

        self.menu_principal.show_all()

        self.label_err=self.get_object("error")
        self.label_tpo=self.get_object("tiempo")
        self.tabla_niveles=self.get_object("tabla1").get_children()
        self.tabla_juego=self.get_object("table1")
        self.label_minas_restantes=self.get_object("minas restantes")
        
        self.timer=None

    def salir(self,widget,data=None):
        dialog = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION,buttons=gtk.BUTTONS_YES_NO,flags=gtk.DIALOG_MODAL,message_format="¿Estas seguro de que quieres salir?")
        response = dialog.run()
        if response == gtk.RESPONSE_YES:
            gtk.main_quit()
        else:
            dialog.destroy()
            return True
        
    def jugar(self,widget,data=None):   
        for i in range(len(self.tabla_niveles)):
            if self.tabla_niveles[i]==widget:
                self.nivel=i
      
        if(self.nivel==0):
            self.tablero=generarTablero((9,9),10)
        elif(self.nivel==1):
            self.tablero=generarTablero((16,16),40)
        elif(self.nivel==2):
            self.tablero=generarTablero((16,30),99)
        elif(self.nivel==3):
            self.filename=self.elegirFichero()
            if self.filename==None:
                return None
            self.tablero=leerFichero(self.filename)
        
        self.preparar_tablero()
        
        self.menu_principal.hide()
        self.juego.show_all()  
    
    def click(self):
        dt = int(time.time() - self.tpo0)
        self.label_tpo.set_label("{0:02}:{1:02}".format(dt/60,dt%60))
        return True
    
    def elegirFichero(self):
        dlg = gtk.FileChooserDialog(
            "Abrir fichero", None,
            gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
             gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        if dlg.run() == gtk.RESPONSE_OK:
            res = dlg.get_filename()
        else:
            res = None
        dlg.destroy()
        return res
    
    def preparar_tablero(self):
        self.total_minas=contarMinas(self.tablero)
        self.minas_marcadas=0
        self.first_move=True
        setAllNumMinas(self.tablero)
        
        self.label_minas_restantes.set_text(str(self.total_minas))
        self.label_tpo.set_text("00:00")
        
        # Quitar (y destruir) controles de la tabla
        for ctrl in self.tabla_juego:
            ctrl.destroy()
        # Redimensionar tabla
        self.tabla_juego.resize(len(self.tablero), 2*len(self.tablero[0])+1)
        for fil in range(len(self.tablero)):
            for col in range(len(self.tablero[0])):        
                btn = gtk.Button()
                btn.connect("button-release-event",self.celda_clicked)
                btn.set_relief(gtk.RELIEF_NONE)
                self.tablero[fil][col].btn=btn
                btn.show()
                if fil%2==0:
                    self.tabla_juego.attach(btn, 2*col+1, 2*col+3, fil, fil+1)
                else:
                    self.tabla_juego.attach(btn, 2*col, 2*col+2, fil, fil+1)
    
        for fil in self.tablero:
            for c in fil:
                c.update()
    def reiniciar(self,widget,data=None):
        if(self.nivel==0):
            self.tablero=generarTablero((9,9),10)
        elif(self.nivel==1):
            self.tablero=generarTablero((16,16),40)
        elif(self.nivel==2):
            self.tablero=generarTablero((16,30),99)
        elif(self.nivel==3):
            self.tablero=leerFichero(self.filename)
        
        if self.timer != None:
            gobject.source_remove(self.timer)
            self.timer = None
        
        self.preparar_tablero()
                
    def celda_clicked(self,widget,event,data=None):
        for fil in range(len(self.tablero)):
            for col in range(len(self.tablero[fil])):
                if widget==self.tablero[fil][col].btn:
                    pos=(fil,col)                
        
        if event.button == 1:
            # Boton izquierdo pulsado
            if self.tablero[pos[0]][pos[1]].is_checked:
                self.label_err.set_markup("<small>NO SE PUEDE ABRIR UNA CELDA MARCADA</small>")
            else:
                if self.tablero[pos[0]][pos[1]].is_open and self.tablero[pos[0]][pos[1]].num_minas>0:
                    self.label_err.set_markup("<small>CELDA YA ABIERTA. FALTAN MARCAS</small>")
                else:
                    if self.tablero[pos[0]][pos[1]].has_mine and self.first_move:
                        swapMine(self.tablero,pos[0],pos[1])
                    
                    if self.first_move:
                        self.tpo0 = time.time()
                        self.timer = gobject.timeout_add(1000, self.click)
                        self.first_move=False
                    
                    if self.tablero[pos[0]][pos[1]].open_cell(self.tablero)==-1:
                        openAll(self.tablero)
                        updateAll(self.tablero)
                        for fil in self.tablero:
                            for c in fil:
                                c.btn.set_sensitive(False)
                        if self.timer != None:
                            gobject.source_remove(self.timer)
                            self.timer = None
                        final = gtk.Dialog()
                        label_msj = gtk.Label('te comés un garrón de la gran flauta')
                        label_msj.show()
                        final.vbox.pack_start(label_msj)
                        final.show_all()
                    
        elif event.button == 3:
            # Boton derecho pulsado
            if self.tablero[pos[0]][pos[1]].is_open:
                self.label_err.set_markup("<small>NO SE PUEDE MARCAR UNA CELDA ABIERTA</small>")
                return None
                
            if self.minas_marcadas==self.total_minas and not self.tablero[pos[0]][pos[1]].is_checked:
                self.label_err.set_markup("<small>DEMASIADAS MARCAS</small>")
                return None
                
            if self.tablero[pos[0]][pos[1]].is_checked:
                self.minas_marcadas-=1
            else:
                self.minas_marcadas+=1
            self.tablero[pos[0]][pos[1]].is_checked=not self.tablero[pos[0]][pos[1]].is_checked
            self.label_minas_restantes.set_text(str(self.total_minas-self.minas_marcadas))
            setAllNumMinas(self.tablero)
            updateAll(self.tablero)
    
        if comprobarTablero(self.tablero):
            for fil in self.tablero:
                for c in fil:
                    c.btn.set_sensitive(False)
            if self.timer != None:
                gobject.source_remove(self.timer)
                self.timer = None
            final = gtk.Dialog()
            label_msj = gtk.Label('sos inimputable hermano!')
            final.vbox.pack_start(label_msj)
            final.show_all()
        
    def volver(self,widget,data=None):
        if self.timer != None:
            gobject.source_remove(self.timer)
            self.timer = None
        
        self.juego.hide()
        self.menu_principal.show_all()

    def abrir(self,widget,data=None):
        openAll(self.tablero)
        updateAll(self.tablero)
        for fil in self.tablero:
            for c in fil:
                c.btn.set_sensitive(False)
        if self.timer != None:
            gobject.source_remove(self.timer)
            self.timer = None
buscaminas=App()
gtk.main()








