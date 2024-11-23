import random
import time
from datetime import datetime, timedelta, time as Dtime
import sys
import matplotlib.pyplot as plt

# Configuración inicial
DATA = {
    "Norte-Sur": {
        "Lunes-Viernes": {"vehiculos": [["06:00", "09:00", 119], ["11:30", "13:00", 105], ["13:00", "19:30", 120]], "demora": 18},
        "Sabado-Domingo": {"vehiculos": [["13:00", "15:00", 107], ["06:00", "20:00", 80]], "demora": 8},
        "mantenimiento": 350,
        "vias": 3
    },
    "Sur-Norte": {
        "Lunes-Viernes": {"vehiculos": [["06:00", "09:00", 117], ["11:30", "13:00", 98], ["17:00", "21:15", 76]], "demora": 6},
        "Sabado-Domingo": {"vehiculos": [["07:00", "09:00", 105], ["04:30", "22:00", 54]], "demora": 0},
        "mantenimiento": 197,
        "vias": 3
    }
}

TOPE_FLUJO_VEHICULAR = 125  # vehículos/km
TOPE_FLUJO_VEHICULAR_REPARACION = round(TOPE_FLUJO_VEHICULAR * 0.77)
CANAL_EMERGENCIA = 1  # Canal reservado para emergencias
CANAL_NORMAL = 3  # Canales para tráfico normal


def interfas():
    sim = {"Norte-Sur": {}, "Sur-Norte": {}}
    random.seed(time.time())
    inicio,fin = "",""
    while True:
        inicio = input("fecha inicio (dd/mm/aa hh:mm): ")
        fin = input("fecha fin (dd/mm/aa hh:mm): ")
        try:
            
            fecha_inicio = datetime.strptime(inicio, "%d/%m/%y %H:%M")
            fecha_fin = datetime.strptime(fin, "%d/%m/%y %H:%M")
            if fecha_inicio < fecha_fin:
                break
            print("colocar una rango valido ej: 15/11/24 11:00 a 16/11/24 11:00")
        except:
            print(f"ocurrio un error al parsear la info")
    fecha_inicio = datetime.strptime(inicio, "%d/%m/%y %H:%M")
    fecha_fin = datetime.strptime(fin, "%d/%m/%y %H:%M")
    print(f"intervalo de {fecha_inicio} a {fecha_fin}")

    for via in ["Norte-Sur", "Sur-Norte"]:
        sim[via]["demora"], sim[via]["autos"] = simulacion(
            via, fecha_inicio, fecha_fin)
    return sim


def main():
    sim = interfas()
    for k, v in sim.items():
        print(f"autos que recorrieron la via {k}: {
              v["autos"]}, demora de los autos en la via: {v["demora"]}")

    args = sys.argv

    if len(args) > 1 and args[1] == "-g":
        graficar_resultados(sim)


def simulacion(sentido, fecha_inicio, fecha_fin):
    delta = fecha_inicio
    tiempo_consumido = 0
    cantidad_autos = 0
    disponibilidad = 1
    otro_sentido = "Norte-Sur" if sentido == "Sur-norte" else "Sur-Norte"
    via_auxiliar_habilitada = False
    duracion_acumulativa_intr = fecha_inicio
    duracion_via_aux = fecha_inicio
    while delta < fecha_fin:
        [tiempo_trafico, autos,disponibilidad,tope_flujo_vehicular,duracion_intr] = sim_trafico(delta, sentido,disponibilidad,duracion_acumulativa_intr,via_auxiliar_habilitada)
        if duracion_intr > 0:
            duracion_acumulativa_intr = delta + timedelta(minutes=duracion_intr)
            
        if (disponibilidad <= 0.67 or autos/tope_flujo_vehicular >=0.95) and not via_auxiliar_habilitada :
            [_,autos_os,_,tope_flujo_vehicular_os,_] = sim_trafico(delta,otro_sentido,1,delta)
            if autos_os/ tope_flujo_vehicular_os <= 0.15:
                via_auxiliar_habilitada = True
                tiempo_trafico += 120
                disponibilidad += 0.33
                duracion_via_aux = delta + timedelta(minutes=60)
                #colocar una forma de finalizar la via auxiliar
                print(f"se habilito una via auxiliar para el sentido {sentido}")
        
        if via_auxiliar_habilitada and delta > duracion_via_aux:
            print(f"cerrando via auxiliar en {sentido}")
            disponibilidad -= 0.33
            via_auxiliar_habilitada = False
            

        delta += timedelta(minutes=tiempo_trafico + 1)
        tiempo_consumido += tiempo_trafico
        cantidad_autos += autos
    
    return [tiempo_consumido, cantidad_autos]


def autos_via(t_actual: datetime, vehiculos: list, flujo_vehicular):
    cantidad_vehiculos = 0
    for h in vehiculos:
        [inicio, fin, cantidad] = h
        hora_inicio = Dtime.fromisoformat(inicio)
        hora_fin = Dtime.fromisoformat(fin)

        if t_actual.time() > hora_inicio and t_actual.time() <= hora_fin:
            promedio_autos_intervalo = cantidad / \
                (((hora_fin.hour - hora_inicio.hour) * 60) + hora_fin.minute)
            cantidad_vehiculos += random.randint(
                round(promedio_autos_intervalo * 0.95), round(promedio_autos_intervalo * 1.05))
            break
        else:
            cantidad_vehiculos = random.randint(round(TOPE_FLUJO_VEHICULAR * 0.05),round(TOPE_FLUJO_VEHICULAR * 0.1))

    if cantidad_vehiculos > flujo_vehicular:
        cantidad_vehiculos = flujo_vehicular

    return cantidad_vehiculos


def sim_trafico(t_actual: datetime, sentido,disponibilidad, duracion_intr_acc,via_auxiliar_habilitada = False):
    dia = "Lunes-Viernes" if t_actual.weekday() < 5 else "Sabado-Domingo"
    info = DATA[sentido][dia]
    demora = 0
    duracion_intr = 0
    if t_actual > duracion_intr_acc and via_auxiliar_habilitada:
        disponibilidad += 0.33
    if random.random() < 0.000025:
        [intr, duracion_intr] = interrupcion(sentido)
        if duracion_intr > 0:
            print(f"ocurrio una interrupcion en el sentido {sentido}, causa: {intr}, demora: {duracion_intr} minutos")
            demora += duracion_intr
            disponibilidad -= 0.33

    flujo_vehicular = round(TOPE_FLUJO_VEHICULAR * disponibilidad)
    autos = autos_via(t_actual, info["vehiculos"], flujo_vehicular)
    if autos/flujo_vehicular >= 0.1:
        demora += 60 * (autos/flujo_vehicular)

    

    return [random.randint(round(demora * 0.95), round(demora * 1.05)), autos, disponibilidad,flujo_vehicular,duracion_intr]


def interrupcion(sentido):
    interrupciones = ["Mantenimiento Sistemas Eléctricos",
                      "Reparaciones menores en vía.",
                      "Colisiones Varias.",
                      "Cierres Preventivos.",
                      "Manifestaciones Generales (Colectividad y sectores Particulares)"
                      ]

    int_actual = random.choice(interrupciones)
    duracion_max_intr = DATA[sentido]["mantenimiento"]
    duracion_intr = random.randint(
        5, duracion_max_intr) if duracion_max_intr > 4 else 0
    DATA[sentido]["mantenimiento"] -= duracion_intr
    return [int_actual, duracion_intr]


def graficar_resultados(sim):
    vias = list(sim.keys())

    # Datos para la gráfica de barras (cantidad de autos)
    autos_totales = [sim[via]["autos"] for via in vias]

    # Datos para la gráfica de líneas (demoras)
    demoras_totales = [sim[via]["demora"] for via in vias]

    # Crear una figura con dos ejes
    fig, ax1 = plt.subplots()

    # Gráfico de barras para la cantidad de autos
    color = 'tab:red'
    ax1.set_xlabel('Vías')
    ax1.set_ylabel('Cantidad de Autos', color=color)
    ax1.bar(vias, autos_totales, color=color, alpha=0.6, label='Autos')

    # Crear un segundo eje para las demoras
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Demora (min)', color=color)
    ax2.plot(vias, demoras_totales, color=color, marker='o', label='Demora')

    fig.tight_layout()
    plt.title('Cantidad de Autos y Demora en las Vías')

    # Mostrar gráficos
    plt.show()

if __name__ == "__main__":
    main()
