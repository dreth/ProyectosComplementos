# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 10:57:51 2018
@author: dreth
"""
# Instalando librerías para que el usuario no tenga que instalarlas manualmente
import subprocess
import sys
def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

# Lista de librerias a instalar
used_non_default_libraries = ['alpha_vantage', 'pandas', 'numpy', 'matplotlib', 'scipy']

# Instalación de las librerías
for libreria in used_non_default_libraries:
    install(libreria)

# Importando librerías a utilizar
from alpha_vantage.timeseries import TimeSeries as ts
import datetime as dt
import pandas as pd
import numpy as np
import random as rd
from scipy.stats import norm
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Arreglando el layout de los gráficos para que los labels del eje x (que tienen gran longitud)
# queden propiamente puestos en la ventana de figura.
rcParams.update({'figure.autolayout': True})

# Seed para luego utilizar rand()
rd.seed(a=15)

# API key para utilizar alpha_vantage
ts = ts(key='ZN5W0AUQ2LWX8JTD', output_format='pandas'); data = []

# Utilización:
# symbol: es un string, debe ser introducido entre comillas y es el símbolo en la bolsa de 
# la compañía cuyos precios de acciones se desea modelar, por ejemplo: 'MSFT' para microsoft
# o 'GOOGL' para Alphabet. En caso de introducir un símbolo incorrectamente, la función retornará
# un error.
#
# it : número de iteraciones con las que se desea modelar, es un int, así que debe ser menor que 2^31 - 1
# y no debe tener parte decimal, en caso de introducir el dato incorrecto, la función retornará un error
#
# n : número de clases en las cuales se subdividirán las secciones de precios al final de la proyección
# es decir, al final de la proyeccion tendremos *it* precios a la fecha introducida por el usuario
# luego de realizar la proyección, se calculará la probabilidad de obtener cada precio. Los precios posibles
# se dividirán en n secciones. Debe ser un int, es decir n < 2^31 - 1. La función retornará error en caso
# de no ser un int. Por default, lo establecemos en 20, pero puede ser modificado introduciendo n=<ValorDeseado>
# sin corchetes, ej: n=35
#
# v : cantidad de días anteriores a la fecha mas reciente desde la cual se proyecta que se desean visualizar en
# el gráfico, por default lo tenemos a 180 días
def get_data(symbol, it, n=20, v=40):
    
    # Chequeo para determinar si el usuario introdujo correctamente el símbolo de la compañía
    try:
        # Probando convertir el símbolo a string
        symbol = str(symbol)
        
        # Adquisición de datos
        data, meta_data = ts.get_daily_adjusted(symbol = symbol, outputsize = 'full')
        
        # Extrayendo la fecha de inicio para luego referenciarla en los cálculos
        k = list(data.index); k = str(k[len(data)-1]); ai,mi,di = map(int, k.split('-')); 
        start_date = dt.date(ai,mi,di)
    
    # Agarre de errores con mensaje de error para símbolos incorrectos
    except (ValueError,KeyError):
        print('ℹ️ Símbolo introducido incorrectamente, error.')
        return
    
    # Ciclo por si el usuario introduce la fecha hasta la cual desea 
    # proyectar incorrectamente, este pueda repetir la introducción de datos
    while True:
        try:
            
            # Si el número de iteraciones introducido como parámetro 
            # no es un número entero, el programa retorna error
            if (type(it) != int or type(n) != int or type(v) != int):
                print('El número de iteraciones, subdivisiones o cantidad de fechas anteriores a proyectar no es entero o no es un valor numérico, error')
                return
            
            # Input del usuario de la fecha de finalización
            end_date = input('¿Hasta donde desea proyectar a partir de los datos? (DD/MM/AAAA): '); df,mf,af = map(int, end_date.split('/'))
            
            # Si el usuario introduce 'c' en la fecha de proyección, el programa cierra, 
            # como un botón de emergencia para cancelar la operación, el uso tiene realmente 
            # propósitos de debugging en caso de querer modificar el código
            if end_date == 'c':
                return
            
            # Estableciendo la fecha de finalización como tipo fecha
            end_date = dt.date(af,mf,df)
            
            # Si la fecha de finalización está antes que la fecha de inicio 
            # (que usualmente es el día laborable más próximo en el cual el usuario hace la proyección)
            # el programa retorna error y reinicia el ciclo
            if start_date > end_date:
                print('La fecha de inicio no puede ser mayor a la fecha de finalización')
                raise ValueError
        except (ValueError, KeyError):
            print('\nℹ️ Error de introducción de datos, introduzca la fecha de nuevo. \n')
            continue
        
        # Finalizando el ciclo, si se llega este lugar del flujo, el usuario introdujo los datos correctamente
        break
    
    # Con PDR se hace la proyección, aqui creamos una lista con los valores del PDR
    PDR = [0]; d = 0
    for i in data['4. close']:
        if d+1 == len(data):
            break
        PDR.append(np.log(data['4. close'].iloc[d]/data['4. close'].iloc[d+1]))
        d+=1
        
    # En esta tabla se encuentran los datos de precio por fecha y el PDR calculado anteriormente
    data_used = pd.DataFrame({'Close':data['4. close'], 'PDR':PDR})
    
    # Calculamos media, varianza, desviación estándar y drift del PDR
    average = np.average(PDR); stdev = np.std(PDR, dtype=np.float64, ddof=1);
    var = stdev**2; drift = average - var/2; d = 0;
    
    # Definimos una lista para las fechas proyectadas que luego adjuntaremos a un dataframe con las proyecciones
    # La variable SDP comienza siendo el día después de la fecha de inicio y adjuntamos las fechas
    # día por día al dataframe con el formato DD/MM/AAAA, ya que el formato de la librería datetime
    # que es yyyy-MM-dd no es muy favorable o cómodo de leer
    fechas_proyectadas = []; d = []; sdp = start_date + dt.timedelta(1)
    while sdp <= end_date:
        fechas_proyectadas.append('{}/{}/{}'.format(sdp.day,sdp.month,sdp.year))
        sdp += dt.timedelta(1)
    
    # Agregando una serie de fechas con precios pasados que datan hasta v=180 días anteriores a start_date
    # para propósitos de graficación
    fechas_pasadas = []; precios_pasados = []; i = 0
    while i < v+1:
        precios_pasados.append(data_used['Close'][len(data_used)-1-v+i])
        av,mv,dv = map(int, data_used.index[len(data_used)-1-v+i].split('-')); fecha_previa = dt.date(av,mv,dv)
        fechas_pasadas.append('{}/{}/{}'.format(fecha_previa.day,fecha_previa.month,fecha_previa.year))
        i+=1

    # Aquí creamos la lista con las proyecciones
    i = 0; average_per_row = []; list_of_elem = []; all_data = {}; last_day = []; avgplus1std = []; avgminus1std = []
    for b in range(it):
        d.append([data['4. close'][len(data)-1]*np.exp(drift + stdev*(norm.ppf(rd.random())))])
    for elem in d:
        while i < int((end_date-start_date).days-1):
            elem.append(elem[i]*np.exp(drift + stdev*(norm.ppf(rd.random()))))
            i +=1
        i=0
    
    # agregamos el último día de la proyección a last_day para luego
    # utilizar esta lista para cálculos probabilísticos
    for elem in d:
        last_day.append(elem[len(elem)-1])    
    
    # reiniciamos la variable de ciclo i y creamos un diccionario donde adjuntamos los rangos
    # de precio para calcular su probabilidad y su respectiva probabilidad
    ancho = (max(last_day) - min(last_day))/n; i = min(last_day);
    rango_de_precio = []; frecuencia = []; 
    list.sort(last_day)
    while i < max(last_day):
        rango_de_precio.append('{0:.2f} a {1:.2f} USD'.format(i, i+ancho))
        if i+ancho == max(last_day):
            frecuencia.append(sum(1 for x in last_day if x >= i and x <= i+ancho))
            break
        frecuencia.append(sum(1 for x in last_day if x >= i and x < i+ancho))
        i += ancho
    
    # Calculando la probabilidad y agregándola al diccionario para convertir a dataframe
    global probabilidad
    probabilidad = [100*(x/sum(frecuencia)) for x in frecuencia]
    subdivisiones = {'Rango de Precio': rango_de_precio, 'Probabilidad (en %)': probabilidad};
    Probabilidades = pd.DataFrame(subdivisiones)
    Probabilidades.set_index('Rango de Precio')
    
    # Calculamos la media por fila y adjuntamos todas las iteraciones a una tabla para utilizar como referencia
    i = 0
    while i < len(d[1]):
        for elem in d:
            if i == len(d[1]):
                break
            list_of_elem.append(elem[i])
            if len(list_of_elem) == len(d):
                average_per_row.append(np.average(list_of_elem))
                avgplus1std.append(average_per_row[i] + np.std(list_of_elem, ddof=1))
                avgminus1std.append(average_per_row[i] - np.std(list_of_elem, ddof=1))
                list_of_elem = []; i+=1
    
    # Adjuntamos las fechas
    i = 1; all_data['Fechas Proyectadas'] = fechas_proyectadas
    
    # Nombramos las columnas de las iteraciones con el número apropiado 
    ultimo_dia = []
    for elem in d:
        all_data['Iteración #{}'.format(i)] = elem
        i+=1
        ultimo_dia.append(elem[len(elem)-1])
    
    # Nombrando la columna de la media
    all_data['Media+1std'] = avgplus1std
    all_data['Media-1std'] = avgminus1std
    all_data['Media'] = average_per_row
    
    # Creando un dataframe con todas las columnas3333
    proyeccion = pd.DataFrame(all_data)
    
    # establecemos las fechas como indice en la tabla de información proyectada
    proyeccion.set_index('Fechas Proyectadas')
    print(proyeccion); i = 1
    
    # Graficando el pasado
    plt.subplot(2,1,1)
    plt.plot(fechas_pasadas, precios_pasados, linewidth=1.5, color='maroon')
    
    # Graficando las proyecciones (todas las iteraciones)
    while i < it:
        if i == 1000:
            break
        color = ['xkcd:green','xkcd:blue','xkcd:red','xkcd:violet','xkcd:orange']
        plt.plot(proyeccion['Fechas Proyectadas'], proyeccion['Iteración #{}'.format(i)],linewidth=1, color=rd.choice(color))
        i += 1 
    
    # Graficando la media y estableciendo los parámetros del gráfico
    todas_las_fechas = fechas_pasadas+list(proyeccion['Fechas Proyectadas'])
    todos_los_precios = precios_pasados+list(proyeccion['Media'])
    plt.plot(todas_las_fechas, todos_los_precios, linewidth=2, color='black')
    plt.plot(proyeccion['Fechas Proyectadas'], all_data['Media+1std'], linewidth=2, color='black')
    plt.plot(proyeccion['Fechas Proyectadas'], all_data['Media-1std'], linewidth=2, color='black')
    if v <= 50:
        plt.xticks(rotation=70, ha='right')
    else:
        plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
    if v > 0:
        plt.xlim([fechas_pasadas[0], proyeccion['Fechas Proyectadas'][len(proyeccion)-1]])
    else:
        plt.xlim([proyeccion['Fechas Proyectadas'][0], proyeccion['Fechas Proyectadas'][len(proyeccion)-1]])
    plt.xlabel('Fecha proyectada'); plt.ylabel('Precio (USD)')
    
    # Imprimiendo tabla de probabilidades en consola
    print(Probabilidades)    
    
    # Agregando los rangos en float a partir de los rangos de precio
    rangos_en_float = [float(x.split(' ')[2]) for x in rango_de_precio]
    probabilidad = [float("%.2f"%x) for x in probabilidad]
    
    # Graficando probabilidades y customizando el gráfico
    plt.subplot(2,1,2)
    if n < 40:
        plt.bar(rangos_en_float, probabilidad, width=1)
    elif n >= 40 and n < 60:
        plt.bar(rangos_en_float, probabilidad, width=0.8)
    elif n >= 60 and n < 80:
        plt.bar(rangos_en_float, probabilidad, width=0.5)
    else:
        plt.bar(rangos_en_float, probabilidad, width=0.35)
    plt.xlabel('Precio (USD)'); plt.ylabel('Probabilidad (%)')
    plt.xticks(rangos_en_float, [x.replace('USD','') for x in rango_de_precio], rotation=70, ha='right')
    plt.subplots_adjust(hspace=1.5)
    plt.tight_layout()
    
    # Mostrando los gráficos
    plt.show(block=False)
    
    # Guardando valores necesarios en una tupla para utilizar en la función para 
    # calcular la probabilidad de que de que el precio sea mayor a X precio, 
    # menor a X precio o entre X e Y precios introducidos por el usuario
    global saved_information
    saved_information = (end_date, ultimo_dia, data)
    
    
    
def calc_prob_precio(fecha_final, ultimo_dia):
    # Pregunta al usuario si desea calcular la probabilidad de que el precio sea mayor a X precio, 
    # menor a X precio o entre X e Y precios introducidos por el usuario
    print('\n--------------------------')
    print('A la fecha {}/{}/{}, el máximo y mínimo son: '.format(fecha_final.day,fecha_final.month,fecha_final.year))
    precio_max = np.max(ultimo_dia); precio_min = np.min(ultimo_dia)
    print('\nPrecio mínimo: ' + str(precio_min))
    print('Precio máximo: ' + str(precio_max))
    while True:
        try:
            print('\nElija una opción: \n')
            print('Escriba 1,2 o 3 para elegir una opción, calcular probabilidad de:\n')
            print('1 - Obtener precio mayor o igual a X \n2 - Obtener precio entre X e Y \n3 - Obtener precio menor o igual a X \nc - Cancelar')
            entrada = input('(1, 2, 3 o c) : ')
            if entrada == '1' or entrada == '2' or entrada == '3':
                entrada = int(entrada)
            elif entrada == 'c' or entrada == 'C':
                break
            else:
                raise ValueError
        except ValueError:
            print('\nℹ️ Error de introducción de datos, intente de nuevo')
            continue
        if (entrada == 1 or entrada == 2 or entrada == 3):
            
            # Calculando la probabilidad para cada caso
            while True:
                suma = 0
                try:
                    
                    # Precio mayor o igual a X
                    if entrada == 1:
                        valor_de_precio = float(input('Introduzca el precio (X): '))
                        if valor_de_precio > precio_max or valor_de_precio < precio_min:
                            raise ValueError
                        for elem in ultimo_dia:
                            if elem >= valor_de_precio:
                                suma += 1
                        prob_para_X_precio = (suma/len(ultimo_dia))*100
                        print('\n--------------------------')
                        print('⭐ La probabilidad de que el precio sea mayor a {} es de: '.format(valor_de_precio) + '{0:.2f}%'.format(prob_para_X_precio))
                        print('--------------------------')
                    
                    # Precio entre X e Y
                    if entrada == 2:
                        valor_de_precio_X = float(input('Introduzca el precio (X): '))
                        valor_de_precio_Y = float(input('Introduzca el precio (Y): '))
                        valor_de_precio = [valor_de_precio_X, valor_de_precio_Y]
                        if valor_de_precio_X > precio_max or valor_de_precio_X < precio_min or valor_de_precio_Y > precio_max or valor_de_precio_Y < precio_min:
                            raise ValueError
                        for elem in ultimo_dia:
                            if elem >= np.min(valor_de_precio) and elem <= np.max(valor_de_precio):
                                suma += 1
                        prob_para_X_precio = (suma/len(ultimo_dia))*100
                        print('\n--------------------------')
                        print('⭐ La probabilidad de que el precio esté entre {} y {} es de: '.format(np.min(valor_de_precio), np.max(valor_de_precio)) + '{0:.2f}%'.format(prob_para_X_precio))
                        print('--------------------------')
                        
                    # Precio menor a X
                    if entrada == 3:
                        valor_de_precio = float(input('Introduzca el precio (X): '))
                        if valor_de_precio > precio_max or valor_de_precio < precio_min:
                            raise ValueError
                        for elem in ultimo_dia:
                            if elem <= valor_de_precio:
                                suma += 1
                        prob_para_X_precio = (suma/len(ultimo_dia))*100
                        print('\n--------------------------')
                        print('⭐ La probabilidad de que el precio sea menor a {} es de: '.format(valor_de_precio) + '{0:.2f}%'.format(prob_para_X_precio))
                        print('--------------------------')
            
                except ValueError:
                    print('\nℹ️ Error de introducción de datos, intente de nuevo. \nLos valores introducidos deben ser numéricos, menores al máximo y mayores al mínimo.\n')
                
                while True:
                        try:
                            print('\n🔁 Introduzca "Y" o "y" para continuar con las mismas opciones')
                            print('↩️ Introduzca "N" o "n" para continuar y cambiar las opciones')
                            print('❌ Introduzca "C" o "c" para cancelar la operación')
                            print('(No tiene que introducir las comillas)\n')
                            continuar = input('¿Desea continuar calculando con las mismas opciones? (y, n, c): ')
                            if (continuar != 'y' and continuar != 'Y' and continuar != 'n' and continuar != 'N' and continuar != 'c' and continuar != 'C'):
                                raise ValueError
                        except ValueError:
                            print('ℹ️ Error, escriba "y" (si) o "n" (no)')
                        if continuar == 'y' or continuar == 'Y' or continuar == 'N' or continuar == 'n':
                            break
                        elif continuar == 'c' or continuar == 'C':
                            print('Operación cancelada ❌')
                            return
                if continuar == 'y' or continuar == 'Y':
                    continue
                elif continuar == 'N' or continuar == 'n':
                    break
                if prob_para_X_precio > -1:
                    break
            else:
                continue
            
            # Cancelar
        elif entrada == 'c' or entrada == 'C':
            print('Operación cancelada ❌')
            return
    print('\n\n')

# menu principal para ease-of-use
def main():
    Instruccion = """Utilización: \n\nsymbol : es un string, debe ser introducido entre comillas y es el símbolo en la bolsa de  la compañía cuyos precios de acciones se desea modelar, por ejemplo: 'MSFT' para microsoft o 'GOOGL' para Alphabet. En caso de introducir un símbolo incorrectamente, la función retornará un error.\n\nit : número de iteraciones con las que se desea modelar, es un int, así que debe ser menor que 2^31 - 1 y no debe tener parte decimal, en caso de introducir el dato incorrecto, la función retornará un error\n\nn : número de clases en las cuales se subdividirán las secciones de precios al final de la proyección es decir, al final de la proyeccion tendremos *it* precios a la fecha introducida por el usuario luego de realizar la proyección, se calculará la probabilidad de obtener cada precio. Los precios posibles se dividirán en n secciones. Debe ser un int, es decir n < 2^31 - 1. La función retornará error en caso de no ser un int. Por default, lo establecemos en 20, pero puede ser modificado introduciendo n=<ValorDeseado> sin corchetes, ej: n=35\n\nv : cantidad de días anteriores a la fecha mas reciente desde la cual se proyecta que se desean visualizar en el gráfico, por default lo tenemos a 180 días"""
    print(Instruccion + '\n')
    while True:
        try:
            symbol = str(input('(symbol) Introduzca el símbolo que desea modelar: '))
            data, meta_data = ts.get_daily_adjusted(symbol = symbol, outputsize = 'compact')
        except (ValueError, KeyError):
            print('ℹ️ Error, asegúrese de introducir el símbolo, y los valores deben ser letras (Ej: MSFT, GOOGL, TSLA)')
            continue
        break
    while True:
        try:
            it = int(input('(it) Introduzca la cantidad de iteraciones que se harán de la proyección: '))
            if it > 10000 or it < 1:
                raise ValueError
        except ValueError:
            print('ℹ️ Error, introduzca un número válido de iteraciones, para fines de eficiencia deben ser menos de 10,000 iteraciones y debe ser un número entero positivo')
            continue
        break
    while True:
        try:
            n = int(input('(n) Introduzca la cantidad de clases en las cuales se subdividirán las probabilidades de obtener el precio a la fecha para el símbolo seleccionado: '))
            if n < 1 or n > 100:
                raise ValueError
        except ValueError:
            print('Los valores deben ser positivos y menores que 100')
            continue
        break
    while True:
        try:
            v = input('(v) Introduzca la cantidad de días pasados a graficar (deje vacío o escriba 0 para sólo graficar la proyección): ')
            if v == '':
                v = 0
            else:
                v = int(v)
        except ValueError:
            print('El valor debe ser positivo y entero')
            continue
        break
    global values
    values = (symbol, it, n, v)
    return

main()
get_data(values[0], values[1], n = values[2], v = values[3])
calc_prob_precio(saved_information[0], saved_information[1])
        
    
    
    
    
    
        
    
    