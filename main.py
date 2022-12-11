import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from functions.getData import distancia_curso

semana = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]

cursos_df = pd.read_csv('./data/cursos.csv', encoding='utf8')
salas_df = pd.read_csv('./data/salas.csv', encoding='utf8')
secciones_df = pd.read_csv('./data/secciones.csv', encoding='utf8')
distancia_cursos_df = pd.read_csv('./data/distancia_cursos.csv', encoding='utf8')

salas = salas_df.set_index('ID SALA').T.to_dict()
cursos = cursos_df.set_index('ID CURSO').T.to_dict()
secciones = secciones_df.set_index('ID SECCION').T.to_dict()

def separa_info_genetica(informacion):
    return [informacion[0:6], informacion[6:11], informacion[11:14], informacion[14:16], informacion[16:]]

def fitness_function(cromosoma):
    score = 0
    informacion = []
    informacion_decimal = []
    calendario_split = [cromosoma[i:i+21] for i in range(0, len(cromosoma), 21)]

    for i, asignacion in enumerate(calendario_split):
        # 0 - ID CURSO, 1 - ID SECCION, 2 - DIA, 3 - BLOQUE Y 4 - SALA
        informacion = separa_info_genetica(asignacion)
        informacion_decimal = [int(gen, 2) for gen in informacion]
        
        # SI EL ID DEL CURSO NO SE ENCUENTRA DENTRO DE CURSOS.KEYS
        if(informacion_decimal[0] not in cursos.keys()):
            score += -1000
        
        # SI LA SECCION NO EXISTE
        if(informacion_decimal[1] not in secciones.keys()):
            score += -1000

        # SI EL DÍA ES MAYOR A 5 ENTONCES SE CASTIGA
        if(informacion_decimal[2] > 5):
            score += -1000

        # CUENTA LAS REPETICIONES DEL DIA/BLOQUE/SALA
        repite_dbs = 0
        norepite_db = 0
        repite_cs = 0
        distancia = 0
        dbs = '{}{}{}'.format(informacion[2], informacion[3], informacion[4])
        db = '{}{}'.format(informacion[2], informacion[3])
        cs = '{}{}'.format(informacion[0], informacion[1])
        
        for asignacion_aux in calendario_split:
            informacion_aux = separa_info_genetica(asignacion_aux)
            if dbs == '{}{}{}'.format(informacion_aux[2], informacion_aux[3], informacion_aux[4]):
                repite_dbs += 1
            if informacion[0] == informacion_aux[0] and db != '{}{}'.format(informacion_aux[2], informacion_aux[3]):
                norepite_db += 1
            if cs == '{}{}'.format(informacion_aux[0], informacion_aux[1]):
                repite_cs += 1
            if informacion[2] == informacion_aux[2] and informacion[0] != informacion_aux[0]:
                distancia = distancia_curso(distancia_cursos_df, int(informacion[0],2), int(informacion_aux[0],2))
                score += 1000*distancia

        if repite_dbs > 1:
            score += -1000*(repite_dbs-1)
        if norepite_db > 1:
            score += -1000*(norepite_db-1)
        if repite_cs > 1:
            score += -1000*(repite_cs-1)
        
    return score

def generar_cromosoma():
    return ''.join(random.choice('10') for _ in range(1260))

def crossover(cromosoma1, cromosoma2):
    newcromosoma1 = ''
    newcromosoma2 = ''
    for i in range(len(cromosoma1)):
        if random.uniform(0.0, 1.0) < 0.5:
            newcromosoma1 += cromosoma1[i]
            newcromosoma2 += cromosoma2[i]
        else:
            newcromosoma1 += cromosoma2[i]
            newcromosoma2 += cromosoma1[i]
    return newcromosoma1,newcromosoma2

def mutacion(cromosoma, mp):
    newcromosoma = ''
    for i in range(len(cromosoma)):
        if random.uniform(0.0, 1.0) < mp:
            if cromosoma[i] == '1':
                newcromosoma += '0'
            else:
                newcromosoma += '1'
        else:
            newcromosoma += cromosoma[i]
    return newcromosoma

def decodificar(cromosoma):
    file = open('./output/calendario.csv', 'w', encoding='utf8')
    file.write('Curso,Seccion,Semestre,Dia,Bloque,Sala\n')
    calendario_split = [cromosoma[i:i+21] for i in range(0, len(cromosoma), 21)]

    for curso in calendario_split:
        informacion = separa_info_genetica(curso)
        informacion_decimal = [int(gen, 2) for gen in informacion]
        row = ''
        try:
            section = secciones[informacion_decimal[1]]['SECCION']
            course = cursos[secciones[informacion_decimal[1]]['ID CURSO']]['TITULO']
            semester = cursos[secciones[informacion_decimal[1]]['ID CURSO']]['SEMESTRE']
        except:
            semester = course = section = 'No existe'

        try:
            room = salas[informacion_decimal[4]]['NOMBRE']
        except:
            room = 'No existe'

        day = int((informacion_decimal[2]+1)/5)
        bloque = informacion_decimal[3]
        
        file.write('{},{},{},{},{},{}\n'.format(course, section, semester, semana[day], bloque+1, room))

if __name__ == "__main__":
    poblacion_total = 100
    probabilidad_mutacion = 0.025
    porcentaje_crossover = 0.8
    porcentaje_mutacion = 0.2
    generaciones = 200

    poblacion = [generar_cromosoma() for _ in range(poblacion_total)]
    top_generaciones = []
    top_calendario = [0,""]
    for generacion in range(generaciones):
        fitness = [fitness_function(individuo) for individuo in poblacion]
        problacion_nueva_generacion = []
        for i in range(int(poblacion_total*porcentaje_crossover/2)):
            torneo = sorted([fitness[random.randint(0, poblacion_total-1)] for _ in range(int(poblacion_total/25))])[::-1][:2]
            c1, c2 = crossover(poblacion[fitness.index(torneo[0])], poblacion[fitness.index(torneo[1])])
            problacion_nueva_generacion.append(c1)
            problacion_nueva_generacion.append(c2)
        
        for i in range(int(poblacion_total*porcentaje_mutacion)):
            individuo = random.randint(0, poblacion_total-1)
            muta = mutacion(poblacion[individuo], probabilidad_mutacion)
            problacion_nueva_generacion.append(muta)

        mejor_puntaje = max(fitness)
        mejorCromosoma = poblacion[np.argmax(fitness)]

        print('Generacion {}'.format(generacion+1))
        print("Mejor puntaje :", mejor_puntaje)
        print(mejorCromosoma)

        if top_calendario[0] < mejor_puntaje:
            top_calendario[0] = mejor_puntaje
            top_calendario[1] = mejorCromosoma

        top_generaciones.append(mejor_puntaje)
        poblacion = problacion_nueva_generacion

    decodificar(top_calendario[1])

    plt.plot(top_generaciones, color='orange')
    plt.title("Progreso de Puntajes")
    plt.xlabel("Generaciones")
    plt.xlabel("Puntaje Top")
    plt.grid()
    plt.show()