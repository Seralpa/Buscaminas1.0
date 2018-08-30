# -*- coding: UTF-8 -*-

from __future__ import print_function
from random import randint
import gtk

imgs=["data/cerrada.png","data/marcada.png","data/mina.png","data/malMarcada.png","data/menorDe0.png","data/boom.png"]
imgsNums=["data/0.png","data/1.png","data/2.png","data/3.png","data/4.png","data/5.png","data/6.png"]

def leerFichero(fich):
    tablero=list()
    i,j=0,0
    with open(fich,'r') as f:
        linea=f.readline()
        if int(linea[0])>30 or int(linea[2])>30:
            raise Exception("Error en el fichero, tablero demasiado grande")
        for linea in f:
            tablero.append(list())
            j=0
            for c in linea.strip('\n'):
                if c=='.':
                    tablero[i].append(Cell(j,i))
                elif c=='*':
                    tablero[i].append(Cell(j,i,True))
                else:
                    raise Exception("Error en el fichero")
                j+=1
            i+=1
        return tablero

def generarTablero(tamano,minas):
    tablero=list()
    for i in range(tamano[0]):
        tablero.append(list())
        for j in range(tamano[1]):
            tablero[i].append(Cell(j,i))
    for _ in range(minas):
        i=randint(0,tamano[0]-1)
        j=randint(0,tamano[1]-1)
        while tablero[i][j].has_mine:
            i=randint(0,tamano[0]-1)
            j=randint(0,tamano[1]-1)
        tablero[i][j].has_mine=True
    return tablero
    
def swapMine(Tablero,i,j):
#Cambia una mina de una posicion i j a la primera casilla sin mina del tablero
    for row in Tablero:
        for c in row:
            if not c.has_mine:
                c.has_mine=True
                Tablero[i][j].has_mine=False
                return None

def updateAll(tablero):
    for row in tablero:
        for c in row:
            c.update()

def setAllNumMinas(tablero):
    for row in tablero:
        for c in row:
            c.set_num_minas(tablero)

def openAll(tablero):
    for row in tablero:
        for c in row:
            c.is_open=True

def contarMinas(tablero):
    cont=0
    for row in tablero:
        for c in row:
            if c.has_mine:
                cont+=1
    return cont

def comprobarTablero(tablero):
    for row in tablero:
        for c in row:
            if (not c.is_open and not c.has_mine) or (c.has_mine and not c.is_checked):
                return False
    return True

class Cell:
    def __init__(self,x,y,mina=False,abierta=False,marcada=False,btn=None):
        self.is_open=abierta
        self.is_checked=marcada
        self.has_mine=mina
        self.x=x
        self.y=y
        self.btn=btn
        self.has_explded=False

    def set_num_minas(self,tablero):
        self.num_minas=0
        if self.y!=0:
            if tablero[self.y-1][self.x].has_mine:
                self.num_minas+=1
            if tablero[self.y-1][self.x].is_checked:
                self.num_minas-=1
        
        if self.x!=0:
            if tablero[self.y][self.x-1].has_mine:
                self.num_minas+=1
            if tablero[self.y][self.x-1].is_checked:
                self.num_minas-=1

        if self.x!=len(tablero[0])-1:
            if tablero[self.y][self.x+1].has_mine:
                self.num_minas+=1
            if tablero[self.y][self.x+1].is_checked:
                self.num_minas-=1

        if self.y!=len(tablero)-1:
            if tablero[self.y+1][self.x].has_mine:
                self.num_minas+=1
            if tablero[self.y+1][self.x].is_checked:
                self.num_minas-=1

        if self.y%2==0:
            if self.x!=len(tablero[0])-1 and self.y!=0:
                if tablero[self.y-1][self.x+1].has_mine:
                    self.num_minas+=1
                if tablero[self.y-1][self.x+1].is_checked:
                    self.num_minas-=1
            
            if self.y!=len(tablero)-1 and self.x!=len(tablero[0])-1:
                if tablero[self.y+1][self.x+1].has_mine:
                    self.num_minas+=1
                if tablero[self.y+1][self.x+1].is_checked:
                    self.num_minas-=1
        else:
            if self.x!=0 and self.y!=0:
                if tablero[self.y-1][self.x-1].has_mine:
                    self.num_minas+=1
                if tablero[self.y-1][self.x-1].is_checked:
                    self.num_minas-=1

            if self.y!=len(tablero)-1 and self.x!=0:
                if tablero[self.y+1][self.x-1].has_mine:
                    self.num_minas+=1
                if tablero[self.y+1][self.x-1].is_checked:
                    self.num_minas-=1
    
    def open_cell(self,tablero):
        if self.is_checked:
            return 0
        if self.has_mine:
            self.has_explded=True
            return -1
        else:
            self.is_open=True
            self.update()
            if self.num_minas<=0:   #abrir recursivamente
                if self.y!=0 and not tablero[self.y-1][self.x].is_open:
                    if tablero[self.y-1][self.x].open_cell(tablero)==-1:
                        return -1
        
                if self.x!=0 and not tablero[self.y][self.x-1].is_open:
                    if tablero[self.y][self.x-1].open_cell(tablero)==-1:
                        return -1

                if self.x!=len(tablero[0])-1 and not tablero[self.y][self.x+1].is_open:
                    if tablero[self.y][self.x+1].open_cell(tablero)==-1:
                        return -1

                if self.y!=len(tablero)-1 and not tablero[self.y+1][self.x].is_open:
                        if tablero[self.y+1][self.x].open_cell(tablero)==-1:
                            return -1
                if self.y%2==0:
                    if self.x!=len(tablero[0])-1 and self.y!=0 and not tablero[self.y-1][self.x+1].is_open:
                        if tablero[self.y-1][self.x+1].open_cell(tablero)==-1:
                            return -1

                    if self.y!=len(tablero)-1 and self.x!=len(tablero[0])-1 and not tablero[self.y+1][self.x+1].is_open:
                        if tablero[self.y+1][self.x+1].open_cell(tablero)==-1:
                            return -1
                else:
                    if self.x!=0 and self.y!=0 and not tablero[self.y-1][self.x-1].is_open:
                        if tablero[self.y-1][self.x-1].open_cell(tablero)==-1:
                            return -1

                    if self.y!=len(tablero)-1 and self.x!=0 and not tablero[self.y+1][self.x-1].is_open:
                        if tablero[self.y+1][self.x-1].open_cell(tablero)==-1:
                            return -1
    
    def update(self):
        imagen=gtk.Image()
        if self.is_checked and (not self.is_open or self.has_mine):
            imagen.set_from_file(imgs[1])
        elif not self.is_open and not self.is_checked:
            imagen.set_from_file(imgs[0])
        elif self.is_open and self.is_checked and not self.has_mine:
            imagen.set_from_file(imgs[3])
        elif self.is_open and not self.is_checked and self.has_mine:
            imagen.set_from_file(imgs[2])
        elif self.num_minas<0:
            imagen.set_from_file(imgs[4])
        else:
            imagen.set_from_file(imgsNums[self.num_minas])
        
        if self.has_explded:
            imagen.set_from_file(imgs[5])
        self.btn.set_image(imagen)    
            
            
            
            
            
            