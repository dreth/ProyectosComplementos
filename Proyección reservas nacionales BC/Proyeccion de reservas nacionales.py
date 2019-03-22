# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 19:04:35 2019

@author: dreth
"""

""" INSTALACIÓN E IMPORTACIÓN DE LIBRERÍAS """

# Funcion para mostrar proceso en consola
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    if iteration == total: 
        print()


# Instalando librerías para que el usuario no tenga que instalarlas manualmente
import subprocess
import sys
def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

# Lista de librerias a instalar
used_non_default_libraries = ['warnings', 'itertools', 'pandas', 'matplotlib', 'numpy', 'sklearn', 'statsmodels', 'inspect', 'dateutil']

# Instalación de las librerías
for libreria in used_non_default_libraries:
    install(libreria)

import warnings
import itertools
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from os import path
from inspect import getframeinfo, currentframe
from sklearn import linear_model
from dateutil import relativedelta as rd
plt.style.use('seaborn')
plt.rcParams["figure.figsize"] = [16,9]

# Obteniendo localización en la pc del script para poder importar datos desde el mismo directorio donde se encuentra el script
filename = getframeinfo(currentframe()).filename
filepath = path.dirname(path.abspath(filename))

""" DEFINICIÓN DE FUNCIÓN ARIMA """

def ARIMA(dataset, printsummary=False, step = 48, s = [1,2,3,4,6,12,24]):
    
    # Definimos los parámetros p, d y q para que tengan valores entre 0 y 2
    p = d = q = range(0, 2)
    
    
    # Generate all different combinations of p, q and q triplets
    pdq = list(itertools.product(p, d, q))
    seasonal_pdq = []
    
    # Generamos todas las combinaciones posibles de pdq con s = [1, 2, 3, 4, 6, 12]
    for season in s:
        params = [(x[0], x[1], x[2], season) for x in pdq]
        for elem in params:
            seasonal_pdq.append(elem)
    
    # Ignorando advertencias para no llenar la consola de advertencias
    warnings.filterwarnings("ignore") 
    
    # Haciendo una lista vacía para agregar todos los modelos y luego elegir el mejor calculando cuál tiene mejor AIC
    model = []; i = 0
    for param in pdq:
        for param_seasonal in seasonal_pdq:
            if param_seasonal[3] == 48:
                length = 48
            else:
                length = 64
            try:
                mod = sm.tsa.statespace.SARIMAX(dataset, order=param, seasonal_order=param_seasonal, enforce_stationarity=False, enforce_invertibility=False)
                results = mod.fit()
                model.append((param, param_seasonal, results.aic))
            except:
                continue
            printProgressBar(i + 1, length*len(s), prefix = 'Calculando mejor modelo para {}:'.format(dataset.name), suffix = 'Al completar se mostrará un gráfico.', length=50)
            i+=1
    
    # Seleccionamos el mejor modelo
    best_model = [x for x in model if x[2] == min([x[2] for x in model])][0]
    
    # Aplicando la función al mejor modelo
    mod = sm.tsa.statespace.SARIMAX(dataset, order = best_model[0], seasonal_order = best_model[1], enforce_stationarity=False, enforce_invertibility=False)
    results = mod.fit()
    
    # Tabla con información estadística relevante
    if printsummary == True:
        print(results.summary().tables[1])
    else:
        print('\n Procesamiento de la variable {} completado, mostrando gráfico \n'.format(dataset.name))
    
    # Obteniendo predicción p pasos en el futuro
    pred_uc = results.get_forecast(steps=step)

    # Obteniendo intervalos de confianza para el gráfico
    pred_ic = pred_uc.conf_int()
    
    # creando una lista de fechas con la cantidad de meses requeridos para realizar la proyección
    next_date = dataset.index[len(dataset.index)-1]
    future_dates = []
    for i in range(0,step):
        next_date = next_date + rd.relativedelta(months=1)
        future_dates.append(next_date)
    
    # graficando la variable con información pasada e información de la proyección
    data_proy = pd.DataFrame(results.forecast(steps=step))
    data_proy.index = future_dates
    plt.plot(dataset)
    plt.plot(data_proy)
    plt.show()
    
    # devolviendo informacion futura
    return (future_dates, results.forecast(steps=step), best_model)

""" LIMPIEZA Y MODELACIÓN DE DATOS """

# asignando tiempo del modelo
tiempo = 60

# importando datos y limpiando
df = pd.read_csv(filepath+'\\datainflmens.csv')
tasa6m_e_inflacion = pd.read_csv(filepath+'\\tasaref6m.csv')

# Convirtiendo el índice del dataframe en un datetime index
df.index = pd.to_datetime(df.Fecha)
tasa6m_e_inflacion.index = pd.to_datetime(tasa6m_e_inflacion.Fecha)
tasa6m_e_inflacion.drop('Fecha',axis=1,inplace=True)
df.drop('Fecha', axis=1, inplace=True)

# Creando una lista con los nombres de las variables
colname = [x for x in df.columns[0:len(df.columns)-1]]

# Creando el modelo de regresión
reg = linear_model.LinearRegression()

# Creando el modelo para los datos que tenemos
reg.fit(df[colname],df.ResBrutas)

# creando un dataframe que no incluye las columnas de tasa de referencia e inflacion
# ya que estas dos variables no llevan el mismo proceso de modelación y requieren
# una mayor cantidad de datos para modelarse apropiadamente.
df_modif = pd.DataFrame(df)
df_modif.drop('Inflacion', axis=1, inplace=True)
df_modif.drop('TasaRef6', axis=1, inplace=True)
df_modif.drop('ResBrutas', axis=1, inplace=True)

# haciendo el modelo para las variables TasaRef6 e inflacion
temp_df= pd.DataFrame()
temp_df['TasaRef6'] = [x*100 for x in tasa6m_e_inflacion.tasaref6]
temp_df.index = tasa6m_e_inflacion.index
proy_tasaref6 = ARIMA(temp_df.TasaRef6, step=tiempo, s=[12])
temp_df = pd.DataFrame()
temp_df['Inflacion'] = [x*10000 for x in tasa6m_e_inflacion.inflacion]
temp_df.index = tasa6m_e_inflacion.index
proy_inflacion = ARIMA(temp_df.Inflacion, step=tiempo, s=[36])

# Prediciendo los datos futuros utilizando ARIMA
proyeccion_dict = {}; bm = []
for col in df_modif.columns:
    proy = ARIMA(df_modif[col], step=tiempo, s=[24])
    proyeccion_dict[col] = proy[1]
    bm.append(proy[2])
    if col == df_modif.columns[0]:
        fd = proy[0]

# Agregando mejores modelos de variables tasaref6 y inflacion
bm.append(proy_tasaref6[2])
bm.append(proy_inflacion[2])

# Agregando elementos tasaref6 y inflacion al diccionario con la proyección
proyeccion_dict['TasaRef6'] = [x/100 for x in proy_tasaref6[1]]
proyeccion_dict['Inflacion'] = [x/1000 for x in proy_inflacion[1]]
del(temp_df)

# convirtiendo el diccionario a un dataframe y asignando el indice de fechas con las fechas predecidas
proy_df = pd.DataFrame.from_dict(proyeccion_dict)
proy_df.index = fd

# Introduciendo los datos y haciendo un dataframe nuevo con la información de la proyección
regresult = []
for date in proy_df.index:
    array = np.reshape(np.array([x for x in proy_df[colname].loc[date]]),(1,7))
    res = reg.predict(array)
    regresult.append(res[0])

# creando un dataframe con valores de la reserva proyectada
ReservasBrutas = pd.DataFrame(regresult)
ReservasBrutas.index = proy_df.index

# graficando los datos
plt.plot(df.ResBrutas)
plt.plot(ReservasBrutas)
plt.show()
























