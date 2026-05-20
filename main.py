from fastapi import FastAPI, HTTPException
from datetime import datetime
from models.tarea import TareaEntrada, TareaActualizacion, TareaSalida

app = FastAPI(title="API de Tareas de Kilian")

# Simulación de Base de Datos en memoria
db_tareas = []
id_contador = 1

@app.post("/tareas", response_model=TareaSalida, status_code=201)
def crear_tarea(tarea: TareaEntrada):
    global id_contador
    
    # 1. Transformamos los datos que entran en un diccionario de Python
    datos_tarea = tarea.model_dump()
    
    # 2. Le añadimos los campos automáticos que no vienen en la entrada (id, completada, etc.)
    nueva_tarea = {
        "id": id_contador,
        "titulo": datos_tarea["titulo"],
        "descripcion": datos_tarea["descripcion"],
        "prioridad": datos_tarea["prioridad"],
        "completada": False,
        "creada_en": datetime.now(),
        "completada_en": None,
        "fecha_limite": datos_tarea["fecha_limite"]
    }
    
    # 3. Guardamos en nuestra "base de datos" y subimos el contador del ID
    db_tareas.append(nueva_tarea)
    id_contador += 1
    
    # 4. Devolvemos la tarea. FastAPI la validará automáticamente con TareaSalida
    return nueva_tarea

@app.get("/tareas", response_model=list[TareaSalida])
def obtener_tareas():
    return db_tareas

@app.get("/tareas/{tarea_id}", response_model=TareaSalida)
def obtener_tarea(tarea_id: int):
    for tarea in db_tareas:
        if tarea["id"] == tarea_id:
            return tarea
        
@app.put("/tareas/{tarea_id}", response_model=TareaSalida)
def actualizar_tarea(tarea_id: int, tarea: TareaActualizacion):
    for tarea_db in db_tareas:
        if tarea_db["id"] == tarea_id:
            if tarea.titulo:
                tarea_db["titulo"] = tarea.titulo
                #...

@app.delete("/tareas/{tarea_id}")
def eliminar_tarea(tarea_id: int):
    for tarea in db_tareas:
        if tarea["id"] == tarea_id:
            db_tareas.remove(tarea)
            return {"mensaje": "Tarea eliminada"}
    raise HTTPException(status_code=404, detail="Tarea no encontrada")

@app.post("/tareas/{tarea_id}/completar")
def completar_tarea(tarea_id: int):
    for tarea in db_tareas:
        if tarea["id"] == tarea_id:
            tarea["completada"] = True
            tarea["completada_en"] = datetime.now()
            return
@app.get("/tareas/estadisticas")
def obtener_estadisticas():
    # 1. Totales y completadas usando len()
    total = len(db_tareas)
    completadas = len([t for t in db_tareas if t["completada"] is True])
    
    # 2. Pendientes (las que tienen completada en False)
    pendientes = [t for t in db_tareas if t["completada"] is False]
    
    # 3. Agrupamos las pendientes por su prioridad sobre la marcha
    pendientes_baja = len([t for t in pendientes if t["prioridad"] == "baja"])
    pendientes_media = len([t for t in pendientes if t["prioridad"] == "media"])
    pendientes_alta = len([t for t in pendientes if t["prioridad"] == "alta"])
    
    # 4. Escupimos el JSON ordenado tal y como pide el enunciado
    return {
        "total_tareas": total,
        "completadas": completadas,
        "pendientes_por_prioridad": {
            "baja": pendientes_baja,
            "media": pendientes_media,
            "alta": pendientes_alta
        }
    }