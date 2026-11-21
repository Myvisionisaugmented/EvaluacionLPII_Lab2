from flask import Flask, jsonify, request, render_template
import json
import time
import random

app = Flask(__name__)

# Algoritmo Quicksort modular
def quicksort(items, clave, reverse=False):
    if len(items) <= 1: 
        return items
    pivote = items[len(items) // 2][clave]
    izq = [x for x in items if (x[clave] > pivote if reverse else x[clave] < pivote)]
    centro = [x for x in items if x[clave] == pivote]
    der = [x for x in items if (x[clave] < pivote if reverse else x[clave] > pivote)]
    return quicksort(izq, clave, reverse) + centro + quicksort(der, clave, reverse)

def bubble_sort(items, clave):
    arr = items.copy()
    n = len(arr)
    for i in range(n):
        intercambio = False
        for j in range(0, n - i - 1):
            if arr[j][clave] > arr[j + 1][clave]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                intercambio = True
        if not intercambio:
            break
    return arr

def busqueda_binaria(items_ordenados, objetivo_id):
    izquierda = 0
    derecha = len(items_ordenados) - 1
    pasos = 0

    while izquierda <= derecha:
        pasos += 1
        medio = (izquierda + derecha) // 2
        id_actual = items_ordenados[medio]['id']

        if id_actual == objetivo_id:
            return items_ordenados[medio], pasos
        elif id_actual < objetivo_id:
            izquierda = medio + 1
        else:
            derecha = medio - 1

    return None, pasos

def leer_productos():
    with open('productos.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/productos')
def get_productos():
    with open('productos.json') as f: productos = json.load(f)
    sort_by = request.args.get('sort_by', 'precio')
    order = request.args.get('order', 'asc') == 'desc'
    ordenados = quicksort(productos, sort_by, reverse=order)
    return jsonify(ordenados)

@app.route('/api/productos/buscar', methods=['GET'])
def buscar_productos():
    id_param = request.args.get('id', type=int)
    if id_param is None:
        return jsonify({'error': 'Debe proporcionar un parámetro numérico ?id=X'}), 400

    productos = leer_productos()

    productos_ordenados = quicksort(productos, 'id', reverse=False)

    resultado, pasos = busqueda_binaria(productos_ordenados, id_param)

    if resultado:
        return jsonify({
            'encontrado':True,
            'producto':resultado,
            'pasos_busqueda':pasos
        })
    else:
        return jsonify({
            'encontrado':False,
            'mensaje':f'No existe ningún producto con ID {id_param}',
            'pasos_busqueda':pasos
        }), 404

@app.route('/api/benchmark', methods=['GET'])
def benchmark():
    productos = leer_productos()  
    total = len(productos)

    
    inicio_qs = time.perf_counter()
    quicksort(productos.copy(), 'precio')
    fin_qs = time.perf_counter()
    tiempo_qs_ms = round((fin_qs - inicio_qs) * 1000, 4)

    inicio_bs = time.perf_counter()
    bubble_sort(productos.copy(), 'precio')
    fin_bs = time.perf_counter()
    tiempo_bs_ms = round((fin_bs - inicio_bs) * 1000, 4)

    mejora = round(tiempo_bs_ms / tiempo_qs_ms, 1) if tiempo_qs_ms > 0 else 0

    return jsonify({
        'elementos': total,
        'quicksort_ms': tiempo_qs_ms,
        'burbuja_ms': tiempo_bs_ms,
        'factor_mejora': f'{mejora}x más rápido'
    })

if __name__ == '__main__':
    app.run(debug=True)
