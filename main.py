import random
import time
from datetime import datetime, timedelta,time as Dtime

# Configuración inicial
DATA = {
    "Norte-Sur": {
        "Lunes-Viernes": {"vehiculos": [["06:00", "09:00", 119], ["11:30", "13:00", 105], ["13:00", "19:30", 120]], "demora": 18},
        "Sabado-Domingo": {"vehiculos": [["13:00", "15:00", 107], ["06:00", "20:00", 80]], "demora": 8},
        "mantenimiento": 350
    },
    "Sur-Norte": {
        "Lunes-Viernes": {"vehiculos": [["06:00", "09:00", 117], ["11:30", "13:00", 98], ["17:00", "21:15", 76]], "demora": 6},
        "Sabado-Domingo": {"vehiculos": [["07:00", "09:00", 105], ["04:30", "22:00", 54]], "demora": 0},
        "mantenimiento": 197
    }
}

TOPE_FLUJO_VEHICULAR = 125  # vehículos/km
TOPE_FLUJO_VEHICULAR_REPARACION = round(TOPE_FLUJO_VEHICULAR * 0.77)
CANAL_EMERGENCIA = 1  # Canal reservado para emergencias
CANAL_NORMAL = 3  # Canales para tráfico normal


def main():
    sim = {"Norte-Sur":{}, "Sur-Norte":{}}
    random.seed(time.time())
    inicio = input("fecha inicio (dd/mm/aa hh:mm): ")
    fin = input("fecha fin (dd/mm/aa hh:mm): ")
    fecha_inicio = datetime.strptime(inicio,"%d/%m/%y %H:%M")
    fecha_fin = datetime.strptime(fin, "%d/%m/%y %H:%M")
    
    [sim["Norte-Sur"]["demora"],sim["Norte-Sur"]["autos"]] = simulacion("Norte-Sur",fecha_inicio,fecha_fin)
    [sim["Sur-Norte"]["demora"],sim["Sur-Norte"]["autos"]] = simulacion("Sur-Norte",fecha_inicio,fecha_fin)
    for via in ["Norte-Sur","Sur-Norte"] :
        [sim[via]["demora"],sim[via]["autos"]] = simulacion(via,fecha_inicio,fecha_fin)
    
    print(f"en el intervalo de {fecha_inicio} a {fecha_fin}")
    
    for k,v in sim.items():
        print(f"autos que recorrieron la via {k}: {v["autos"]}, demora de los autos en la via: {v["demora"]}")
        
def simulacion(sentido,fecha_inicio,fecha_fin):
    delta = fecha_inicio
    tiempo_consumido = 0
    cantidad_autos = 0
    while delta < fecha_fin:
        [tiempo_trafico,autos]= sim_trafico(delta,sentido)
        delta += timedelta(minutes=tiempo_trafico + 1)
        print(tiempo_trafico)
        tiempo_consumido += tiempo_trafico
        cantidad_autos += autos
    return [tiempo_consumido,cantidad_autos]
    
    
def autos_via(t_actual: datetime, vehiculos: list, flujo_vehicular):
    cantidad_vehiculos = 0
    for h in vehiculos:
        [inicio,fin,cantidad] = h
        hora_inicio = Dtime.fromisoformat(inicio)
        hora_fin = Dtime.fromisoformat(fin)
        
        if t_actual.time() > hora_inicio and t_actual.time() <= hora_fin:
            promedio_autos_intervalo = cantidad / (((hora_fin.hour - hora_inicio.hour) * 60) + hora_fin.minute)
            cantidad_vehiculos += random.randint(round(promedio_autos_intervalo * 0.9),round(promedio_autos_intervalo * 1.1))
            break
        else:
            cantidad_vehiculos = round(TOPE_FLUJO_VEHICULAR * 0.1)
        
    if cantidad_vehiculos > flujo_vehicular:
        cantidad_vehiculos = flujo_vehicular
        
    return cantidad_vehiculos

def sim_trafico(t_actual: datetime,sentido):
    dia = "Lunes-Viernes" if t_actual.weekday() < 5 else "Sabado-Domingo"
    info = DATA[sentido][dia]
    # demora = info["demora"]
    demora = 0
    flujo_vehicular = TOPE_FLUJO_VEHICULAR
    if random.random() < 0.01:
        [intr,duracion_intr]= interrupcion(sentido)
        print(f"ocurrio una interrupcion en el sentido {sentido}, causa: {intr}, demora: {duracion_intr}")
        demora += duracion_intr
        flujo_vehicular = TOPE_FLUJO_VEHICULAR_REPARACION
        
    autos = autos_via(t_actual,info["vehiculos"],flujo_vehicular)
    
    if autos == flujo_vehicular:
        demora += 1
    
    
    return [random.randint(round(demora* 0.9),round(demora* 1.1)),autos]
    
    

def interrupcion(sentido):
    interrupciones = [	"Mantenimiento Sistemas Eléctricos",
                        "Reparaciones menores en vía.",
	                    "Colisiones Varias.",
	                    "Cierres Preventivos.",
	                    "Manifestaciones Generales (Colectividad y sectores Particulares)"
                     ]
    
    int_actual = random.choice(interrupciones)
    duracion_max_intr = DATA[sentido]["mantenimiento"] 
    duracion_intr = random.randint(5,duracion_max_intr) if duracion_max_intr > 0 else 0
    DATA[sentido]["mantenimiento"] -= duracion_intr
    return [int_actual,duracion_intr]
    
    
if __name__=="__main__":
    main()

