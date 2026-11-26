import json
from collections import Counter
from google.genai import types

# 12 casos de triaje de siniestros: texto libre del asegurado -> JSON fijo
ejemplos_raw = [
    # denuncio (3)
    (
        "Me acaban de chocar por detrás en la autopista, el parachoques quedó hundido y necesito ingresar el siniestro.",
        {"tipo_gestion": "denuncio", "prioridad": "alta"},
    ),
    (
        "Ayer en la noche me rompieron el vidrio del copiloto para robar la radio, quiero hacer el denuncio.",
        {"tipo_gestion": "denuncio", "prioridad": "alta"},
    ),
    (
        "Tuve un raspón menor contra un pilar del estacionamiento hace un par de horas, ¿cómo lo reporto?",
        {"tipo_gestion": "denuncio", "prioridad": "media"},
    ),
    # documentacion (3)
    (
        "Adjunto mi licencia de conducir renovada y el padrón del auto para que puedan aprobar los daños.",
        {"tipo_gestion": "documentacion", "prioridad": "media"},
    ),
    (
        "Ya firmé el relato del choque, ¿dónde subo el archivo junto con las fotos del vehículo?",
        {"tipo_gestion": "documentacion", "prioridad": "media"},
    ),
    (
        "Me pidieron mandar de nuevo la copia del padrón porque salió borrosa en el primer correo.",
        {"tipo_gestion": "documentacion", "prioridad": "baja"},
    ),
    # reclamo_taller (3)
    (
        "Llevo tres semanas esperando el peritaje en el taller y nadie me da fecha de entrega.",
        {"tipo_gestion": "reclamo_taller", "prioridad": "alta"},
    ),
    (
        "El taller todavía no recibe los repuestos y el presupuesto sigue pegado en revisión.",
        {"tipo_gestion": "reclamo_taller", "prioridad": "alta"},
    ),
    (
        "Quiero dejar un reclamo porque me prometieron el auto listo el viernes y siguen retrasando la reparación.",
        {"tipo_gestion": "reclamo_taller", "prioridad": "alta"},
    ),
    # consulta_poliza (3)
    (
        "¿Cuánto me toca pagar de deducible si decido arreglar el golpe con el seguro?",
        {"tipo_gestion": "consulta_poliza", "prioridad": "baja"},
    ),
    (
        "Quiero confirmar si mi póliza actual incluye auto de reemplazo mientras está en el taller.",
        {"tipo_gestion": "consulta_poliza", "prioridad": "baja"},
    ),
    (
        "¿El deducible se paga al taller al retirar el vehículo o directo a la aseguradora?",
        {"tipo_gestion": "consulta_poliza", "prioridad": "baja"},
    ),
]

examples = [
    types.TuningExample(
        text_input=texto,
        output=json.dumps(salida, ensure_ascii=False),
    )
    for texto, salida in ejemplos_raw
]


def chequear_balance(ejemplos: list[tuple[str, dict]], clave: str) -> Counter:
    return Counter(salida[clave] for _, salida in ejemplos)


def validar_dataset(
    examples: list[types.TuningExample],
    claves_esperadas: tuple[str, ...],
) -> list[str]:
    problemas = []
    vistos = set()

    for i, ej in enumerate(examples):
        if not ej.text_input or not ej.text_input.strip():
            problemas.append(f"ejemplo {i}: text_input vacio")
        if not ej.output or not ej.output.strip():
            problemas.append(f"ejemplo {i}: output vacio")
            continue
        if ej.text_input in vistos:
            problemas.append(f"ejemplo {i}: text_input duplicado")
        vistos.add(ej.text_input)

        try:
            salida = json.loads(ej.output)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {i}: output no es JSON valido")
            continue

        for clave in claves_esperadas:
            if clave not in salida:
                problemas.append(f'ejemplo {i}: output no tiene la clave "{clave}"')

    return problemas


if __name__ == "__main__":
    print(f"{len(examples)} ejemplos construidos\n")

    # 1. Revisar balance entre categorias
    balance = chequear_balance(ejemplos_raw, "tipo_gestion")
    print("--- Balance por tipo_gestion ---")
    for categoria, cuenta in balance.most_common():
        print(f"  {categoria}: {cuenta}")

    # 2. Validar el dataset real
    claves = ("tipo_gestion", "prioridad")
    problemas = validar_dataset(examples, claves_esperadas=claves)
    print(f"\n--- Validacion dataset real ---")
    print(f"{len(examples)} ejemplos, {len(problemas)} problemas encontrados")
    for p in problemas:
        print(" -", p)

    # 3. Prueba con 2 ejemplos rotos a proposito para confirmar que el validador funciona
    examples_rotos = examples + [
        types.TuningExample(text_input="", output='{"tipo_gestion": "denuncio"}'),
        types.TuningExample(text_input=ejemplos_raw[0][0], output="{'no_es': 'json_valido'}"),
    ]
    problemas_prueba = validar_dataset(examples_rotos, claves_esperadas=claves)
    print(f"\n--- Prueba de deteccion de errores ---")
    print(f"{len(examples_rotos)} ejemplos, {len(problemas_prueba)} problemas detectados")
    for p in problemas_prueba:
        print(" -", p)