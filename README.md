## Cómo ejecutar

```bash
pip install -r requirements.txt
python main.py
```

## Controles

- Clic izquierdo: seleccionar / continuar
- F11: pantalla completa
- ESC: salir

## Flujo del juego

1. Intro
2. Objetivo
3. Reglas
4. Víctima del caso aleatorio
5. Hub de investigación
6. 5 acciones para investigar habitaciones, armas o sospechosos
7. Acusación final
8. Si falla en la primera ronda, recibe retroalimentación y obtiene 5 acciones más
9. Si falla en la segunda ronda, pierde
10. Si acierta, gana con la pantalla correspondiente al culpable

## Casos programados

1. Hijo / Veneno / Cava / víctima: Abuelo
2. Abogado / Cuchillo / Estudio / víctima: Hijo
3. Tío / Cuerda / Invernadero / víctima: Nuera
4. Nieta / Pistola / Biblioteca / víctima: Tío
5. Nuera / Copa / Cocina / víctima: Abogado

## Nota

El juego usa las imágenes ya generadas. Los botones son imágenes clicables; el código no escribe encima de ellos. Solo se escribe encima de `009_nota_blanca.png` para mostrar acciones restantes.
