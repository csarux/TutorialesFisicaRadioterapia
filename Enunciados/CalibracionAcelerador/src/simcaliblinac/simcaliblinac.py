'''
Física de la Radioterapia. Máster de Física Biomédica. Universidad Complutense de Madrid

César Rodríguez

Módulo: simcaliblinac

Funciones para simular medidas de calibracicón en un acelerador lineal
'''
# Dependencias
import numpy as np

# Constantes

## Electrómetro
### Resolución
_resolucion_electrometro = 3
### Fugas
_fugas_mean = 0.078 # nC por minuto
_fugas_std = 0.009

## Condiciones ambientales
_presion_mean_Fuenlabrada = 946.6
_presion_std_Fuenlabrada = 11
_temperatura_mean_Fuenlabrada = 22
_temperatura_std_Fuenlabrada = 1.1
### Resolucion termómetro
_resolucion_termometro = 1
### Resolución. barómetro
_resolucion_barometro = 1

## Situación del acelerador
### Output
_D_actual = 1.016
### Tasa de medida
_UM_tasa = 600
### Reproducibilidad del acelerador [unidades relativas]
_acelerador_rel_std = 0.001


## Incertidumbres en la determinación de las condiciones ambientales
_presion_unc = 0.6
_temperatura_unc = 0.8

## Constantes de la cámara Farmer
_NDwQ0 = 0.05396
_rel_unc_NDwQ0 = 0.0055 # k=1
_kQ = 0.9886

# Generador 
_rng = np.random.default_rng()


# Funciones
def _presion_temperatura_actual():
    presion = _rng.normal(_presion_mean_Fuenlabrada, _presion_std_Fuenlabrada)
    temperatura = _rng.normal(_temperatura_mean_Fuenlabrada, _temperatura_std_Fuenlabrada)
    return presion, temperatura

## Establecer las condiones ambientales actuales
_presion_actual, _temperatura_actual = _presion_temperatura_actual()

def presion_temperatura_medida(trials=1):
    presion = _rng.normal(_presion_actual, _presion_unc, trials).round(decimals=_resolucion_barometro)
    temperatura = _rng.normal(_temperatura_actual, _temperatura_unc, trials).round(decimals=_resolucion_termometro)
    return presion, temperatura

# Corrección de las condiciones ambientales
def ϕpTf(p, T):
    ϕpT = 1013/p*(273.25+T)/293.25
    return ϕpT

# Factor de caorrección por las condiciones acctuales
_ϕpT_actual = ϕpTf(_presion_actual, _temperatura_actual)

# Fugas
def fugas(minutos=1, n=1, trials=1):
    return _rng.normal(_fugas_mean*minutos, _fugas_std*minutos, (trials, n)).round(decimals=_resolucion_electrometro)

## Establecer el valor medio actual de las fugas
_fugas_act = fugas()

# Situación actual del acelerador
def _lectura_actual_f(UM, D_actual=_D_actual, NDwQ0=_NDwQ0, kQ=_kQ, ϕpT=_ϕpT_actual):
    lectura_actual = D_actual * UM / 100 / NDwQ0 / kQ / ϕpT
    lectura_actual = np.round(lectura_actual, decimals=_resolucion_electrometro)
    return lectura_actual

def _dosis_actual_f(lectura_actual, UM, ϕpT=_ϕpT_actual, fugas=_fugas_act, NDwQ0=_NDwQ0, kQ=_kQ):
    D_actual = (lectura_actual - fugas * UM/_UM_tasa) * ϕpT * NDwQ0 * kQ 
    return D_actual

def _output_actual_f(UM, D_actual=_D_actual, NDwQ0=_NDwQ0, kQ=_kQ, ϕpT=_ϕpT_actual):
    lectura_actual = D_actual * UM / 100 / NDwQ0 / kQ / ϕpT
    output = D / UM * 100
    return output_actual

# Simulación de las medidas
def lectura_medida_f(UM, n=1, trials=1, D_actual=_D_actual, NDwQ0=_NDwQ0, kQ=_kQ, ϕpT=_ϕpT_actual):
    UMs = np.array(UM)
    try:
        lectura_medida = np.array([D_actual * UM / 100 / NDwQ0 / kQ / ϕpT * _rng.normal(1, _acelerador_rel_std, (trials, n)) for UM in UMs])
    except TypeError:
        lectura_medida = D_actual * UM / 100 / NDwQ0 / kQ / ϕpT * _rng.normal(1, _acelerador_rel_std, (trials, n))
    lectura_medida = lectura_medida.round(decimals=_resolucion_electrometro)
    return lectura_medida

def dosis_f(lecturas, UM, ϕpT, fugas, NDwQ0=_NDwQ0, kQ=_kQ):
    D = (lecturas - fugas * UM/_UM_tasa) * ϕpT * NDwQ0 * kQ 
    return D

def output_f(lecturas, UM, ϕpT, fugas, NDwQ0=_NDwQ0, kQ=_kQ):
    D = (lecturas - fugas * UM/_UM_tasa) * ϕpT * NDwQ0 * kQ 
    output = D / UM * 100
    return output