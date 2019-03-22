# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import datetime as dt
def int_simple(y, P, nd=365, na=365, F=1, inv=False, fi = (0,0,0), ff = (0,0,0)):
    print("y = Tasa de interés \nnd = numero de días de contrato \nna = número de días en el período de pag (ej: 360 ó 365 = 1 año) \nP = monto inicial")
    if y >= 1:
        y = y/100
    elif y < 0:
        print('la tasa de interés debe ser y > -1, y < 1')
    elif (nd <= 0 or na <= 0 or P <=0):
        print('nd, na o P deben ser todos mayores que 0')
    try:
        float(y), float(na), float(P), float(nd), float(F)
        (di,mi,ai) = fi; (df,mf,af) = ff
        datecond = (di > 31 or di < 0  or mi > 12 or mi < 0 or ai < 0 or df > 31 or df < 0 or mf > 12 or mf < 0 or af < 0 or fi > ff); 
        fi = np.abs(fi); ff = np.abs(ff)
        int(di), int(mi), int(ai)
        if datecond == True:
            raise ValueError
    except (ValueError, TypeError):
        print('los valores deben ser numéricos y en caso de fechas asegúrese que se encuentran bien introducidas')
        return
    datecond2 = (di > 0 and mi > 0 and ai > 0 and df > 0 and mf > 0 and af > 0)
    if datecond2 == False:
        if inv == False:
            F = P*(1 + y*(nd/na))
            return F
        elif inv == True:
            P = F*((1 + y*(nd/na))**(-1))
            return P
    if datecond2 == True:
        print('\n Fecha introducida: desde ({}/{}/{}) hasta ({}/{}/{}) \n'.format(fi[0],fi[1],fi[2],ff[0],ff[1],ff[2]))
        fi = dt.date(ai,mi,di); ff = dt.date(af,mf,df); nd = (ff-fi).days
        if inv == False:
            F = P*(1 + y*(nd/na))
            return F
        elif inv == True:
            P = F*((1 + y*(nd/na))**(-1))
            return P
    else:
        print('Error, inv no está correctamente introducido, asegúrese que sea True o False')

def int_compuesto_general(y, P, n, m=1, F=1, inv=False, fi = (0,0,0), ff = (0,0,0)):
    print("y = Tasa de interés \nn = numero de años de contrato \nm = cantidad de rentas por año (ej: 4 = trimestral) \nP = monto inicial, \nF = valor futuro (en caso inverso)")
    if y >= 1 and y < 100:
        y = y/100
    elif y < 0:
        print('la tasa de interés debe ser y > -1, y < 100')
    elif (n <= 0 or P <=0):
        print('n y P deben ser todos mayores que 0')
    else:
        print('Error de introducción de datos.')
    try:
        float(y), float(n), float(P), float(m), float(F)
        (di,mi,ai) = fi; (df,mf,af) = ff
        datecond = (di > 31 or di < 0  or mi > 12 or mi < 0 or ai < 0 or df > 31 or df < 0 or mf > 12 or mf < 0 or af < 0 or fi > ff); 
        fi = np.abs(fi); ff = np.abs(ff)
        int(di), int(mi), int(ai)
        if datecond == True:
            raise ValueError
    except (ValueError, TypeError):
        print('los valores deben ser numéricos y en caso de fechas asegúrese que se encuentran bien introducidas')
        return
    datecond2 = (di > 0 and mi > 0 and ai > 0 and df > 0 and mf > 0 and af > 0)
    if datecond2 == False:
        if inv == False:
            F = P*(1 + y/m)**(n*m)
            return F
        elif inv == True:
            P = F*((1 + y/m)**(-n*m))
            return P
    if datecond2 == True:
        print('\n Fecha introducida: desde ({}/{}/{}) hasta ({}/{}/{}) \n'.format(fi[0],fi[1],fi[2],ff[0],ff[1],ff[2]))
        fi = dt.date(ai,mi,di); ff = dt.date(af,mf,df); n = (int((ff-fi).days/365))*m
        if inv == False:
            F = P*(1 + y/m)**(n)
            return F
        elif inv == True:
            P = F*((1 + y/m)**(-n))
            return P
    else:
        print('Error, inv no está correctamente introducido, asegúrese que sea True o False')

def int_compuesto_variable(P, n=1, m=1, F=1, inv=False):
    i = 0; k = 1; tiempo = ['años', 'semestres', 'cuatrimestres', 'trimestres', 'meses (2)', 'meses', 'semanas', 'días', 'medios días', 'horas', 'minutos', 'segundos']
    val_m = [1,2,3,4,6,12,52,365,730,8760,525600,31536000]; dic_m = dict(zip(val_m,tiempo)); Tiempo = []; Acumulado = []; Tasa = []; interv = []; temp = []; tempsum = [0]; loopelement = 0; errcount = 0
    try:
        if m not in val_m:
            raise ValueError
        if inv == False:
            while i < n:
                try:
                    y = float(input('introduzca la tasa número {}: '.format(k)))
                    if y >= 1:
                        if y > 99.99:
                            raise ValueError
                        y = y/100 
                    elif y <= -1:
                        if y < -99.99:
                            raise ValueError
                        y = y/100
                    s = int(input('cantidad de {} utilizando la tasa {}: '.format(dic_m[m],y)))
                    if (s > n or s > (n - i)) :
                        raise ValueError
                    F = F*((1 + y/m)**(s*m))
                    i += s; k += 1
                    Tasa.append(y); interv.append(s); Acumulado.append(F*P)
                except ValueError:
                    print('Error de introducción de datos, inténtelo de nuevo')
                    errcount +=1; 
                    if errcount == 20:
                        return
            F = F*P
            for num in interv:
                if (loopelement == len(interv)):
                    break
                temp.append(num); tempsum.append(sum(temp))
                elem = str(tempsum[loopelement]) + ' - ' + str(tempsum[loopelement+1]) + ' {}'.format(dic_m[m])
                loopelement += 1; Tiempo.append(elem)
            print('\nValor presente: {} \nTasas introducidas: '.format(P))
            print(pd.DataFrame({'Tiempo': Tiempo, 'Tasa' : Tasa, 'Acumulado': Acumulado}))
            return F     
        if inv == True:
            P = 0; K = 1
            while i < n:
                try:
                    y = float(input('introduzca la tasa número {}: '.format(k)))
                    if y >= 1:
                        if y > 99.99:
                            raise ValueError
                        y = y/100 
                    elif y <= -1:
                        if y < -99.99:
                            raise ValueError
                        y = y/100
                    elif y > 99.99:
                        raise ValueError 
                    elif y <= 0:
                        raise ValueError
                    s = int(input('cantidad de {} utilizando la tasa {}: '.format(dic_m[m],y)))
                    if (s > n or s > (n - i)) :
                        raise ValueError
                    K = K*(1 + y/m)**(s)
                    i += s; k += 1
                    Tasa.append(y); interv.append(s);  Acumulado.append(F/K)
                except ValueError:
                    print('Error de introducción de datos, inténtelo de nuevo')
                    errcount +=1; 
                    if errcount == 20:
                        return
            P = F/K
            for num in interv:
                if (loopelement == len(interv)):
                    break
                temp.append(num); tempsum.append(sum(temp))
                elem = str(tempsum[loopelement]) + ' - ' + str(tempsum[loopelement+1]) + ' {}'.format(dic_m[m])
                loopelement += 1; Tiempo.append(elem)
            print('\nValor presente: {} \n\nTasas introducidas: '.format(P))
            print(pd.DataFrame({'Tiempo': Tiempo, 'Tasa' : Tasa, 'Acumulado': Acumulado}))
            print('\n Resultado: ')
            return P
    except (ValueError, KeyError):
        print('Error en la introducción de datos, asegúrese que los datos de todas las variables son numéricos y mayores que 0. \nAsegúrese en caso de no haberse dado cuenta, que su cantidad de años en un período determinado sea menor que "n", \nya que la duración de un período no puede ser mayor que la duración total ')
        print(' \n¿Desea intentar de nuevo con los mismos datos introducidos?  (Y/N) ')
        while True:
            resp = input('(Y/N) : ')
            if resp == 'N' or resp == 'n':
                print('\nOperación abortada\n')
                return; break
            elif resp == 'S' or resp == 's' or resp == 'Y' or resp == 'y':
                print('\nReintroduciendo datos\n')
                int_compuesto_variable(P, n, m=m, F=F, inv=inv)
                break
            else:
                print('Error, intente de nuevo')
                pass

def int_continuo(y, P, n, F=1, inv=False, fi = (0,0,0), ff = (0,0,0)):
    print("y = Tasa de interés \nn = numero de años de contrato \nP = monto inicial, \nF = valor futuro (en caso inverso)")
    if y >= 1:
        y = y/100
    elif y < 0:
        print('la tasa de interés debe ser y > -1, y < 1')
    elif (n <= 0 or P <= 0):
        print('n y P deben ser todos mayores que 0')
    try:
        float(y), float(n), float(P), float(F)
        (di,mi,ai) = fi; (df,mf,af) = ff
        datecond = (di > 31 or di < 0  or mi > 12 or mi < 0 or ai < 0 or df > 31 or df < 0 or mf > 12 or mf < 0 or af < 0 or fi > ff); 
        fi = np.abs(fi); ff = np.abs(ff)
        int(di), int(mi), int(ai)
        if datecond == True:
            raise ValueError
    except (ValueError, TypeError):
        print('los valores deben ser numéricos y en caso de fechas asegúrese que se encuentran bien introducidas')
        return
    datecond2 = (di > 0 and mi > 0 and ai > 0 and df > 0 and mf > 0 and af > 0)
    if datecond2 == False:
        if inv == False:
            F = P*np.exp(y*n)
            return F
        elif inv == True:
            P = F*np.exp(-y*n)
            return P
    if datecond2 == True:
        print('\n Fecha introducida: desde ({}/{}/{}) hasta ({}/{}/{}) \n'.format(fi[0],fi[1],fi[2],ff[0],ff[1],ff[2]))
        fi = dt.date(ai,mi,di); ff = dt.date(af,mf,df); n = (ff-fi).days/365; y = y/365
        if inv == False:
            F = P*np.exp(y*n)
            return F
        elif inv == True:
            P = F*np.exp(-y*n)
            return P
    else:
        print('Error, inv no está correctamente introducido, asegúrese que sea True o False')    
    
def TAE(y, n, m=1, tae=1, cont=False, inv=False, fi = (0,0,0), ff = (0,0,0)):
    print("y = Tasa de interés \nn = numero de años de contrato \nm = cantidad de rentas por año (ej: 4 = trimestral) \nP = monto inicial, \nF = valor futuro (en caso inverso)")
    if y >= 1 and y < 100:
        y = y/100
    elif y < 0:
        print('la tasa de interés debe ser y > -1, y < 100')
    elif (n <= 0 or m <= 0):
        print('n y m deben ser todos mayores que 0')
    else:
        print('Error de introducción de datos.')
    try:
        float(y), float(tae), float(m)
        (di,mi,ai) = fi; (df,mf,af) = ff
        datecond = (di > 31 or di < 0  or mi > 12 or mi < 0 or ai < 0 or df > 31 or df < 0 or mf > 12 or mf < 0 or af < 0 or fi > ff); 
        fi = np.abs(fi); ff = np.abs(ff)
        int(di), int(mi), int(ai)
        if datecond == True:
            raise ValueError
    except (ValueError, TypeError):
        print('los valores deben ser numéricos y en caso de fechas asegúrese que se encuentran bien introducidas')
        return
    datecond2 = (di > 0 and mi > 0 and ai > 0 and df > 0 and mf > 0 and af > 0)
    if datecond2 == False:
        if cont == False:
            if inv == False:
                tae = (1 + y/m)**(n*m) -1
                return tae
            elif inv == True:
                taeinv = (tae+1)*((1 + y/m)**(-n*m))
                return taeinv
        elif cont== True:
            if inv == False:
                tae = np.exp(y*n) - 1
                return tae
            elif inv == True:
                taeinv = (tae+1)*np.exp(-n*y)
                return taeinv
    if datecond2 == True:
        print('\n Fecha introducida: desde ({}/{}/{}) hasta ({}/{}/{}) \n'.format(fi[0],fi[1],fi[2],ff[0],ff[1],ff[2]))
        fi = dt.date(ai,mi,di); ff = dt.date(af,mf,df); n = (int((ff-fi).days/365))*m
        if cont == False:
            if inv == False:
                tae = (1 + y/m)**(n) - 1
                return tae
            elif inv == True:
                taeinv = (tae+1)*((1 + y/m)**(-n))
                return taeinv
        elif cont == True:
            if inv == False:
                tae = np.exp(n*y) - 1
                return tae
            elif inv == True:
                taeinv = (tae+1)*(np.exp(-n*y))
                return taeinv
    else:
        print('Error, inv no está correctamente introducido, asegúrese que sea True o False')    
    
def val_futuros(r, S_t, t, T, K, cant_r=0, R=0, d=0, renta=False):
    suma = 0;
    if r >= 1:
        r = r/100
    elif r < 0:
        print('la tasa de interés debe ser r > -1, r < 1')
    elif (T < 0 or t < 0 or K <= 0):
        print('Todos los valores (excepto t) deben ser todos mayores que 0')
    try:
        float(r), float(t), float(T), float(K), float(S_t)
    except (ValueError, TypeError):
        print('los valores deben ser numéricos y en caso de fechas asegúrese que se encuentran bien introducidas')
        return
    if renta == False:
        if d > 0:
            Ft = S_t*np.exp(-d*(T-t)) - K*np.exp(-r*(T-t))
            return Ft
        Ft = S_t - K*np.exp(r*(t-T))
        return Ft
    elif renta == True:
        k = 1
        while k <= cant_r:
            s = float(input('Tasa número {}: '.format(k))); s = s/100
            m = float(input('Tiempo con {}%: '.format(s*100))); m=m/12
            suma = suma + np.exp(-s*m); k += 1
        I_t = R*(suma); print()
        Ft = S_t - I_t - K*np.exp(r*(t-T))
        print(K*np.exp(r*(t-T)))
        return Ft
    
    
    
    
    
    
    
    
    
    
    

        