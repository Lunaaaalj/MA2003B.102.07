# Log de agregación diaria (issue #51)


## 1. Entrada

- Horario limpio (#13): 574,343 filas × 38 columnas, 15 estaciones, 2021-01-01 → 2025-06-30.

## 2. Regla de completitud

- Referencia: el criterio del MDA8, 18 de 24 ventanas móviles válidas (docs/log_limpieza.md). Es el 75 % de la ventana, y esa proporción se traslada a las ventanas más cortas en vez de inventar un umbral por variable.
- Día completo (24 h): mínimo 18 horas válidas. Ventana de precursores 06-09 h (4 h): mínimo 3, medido SOBRE LA VENTANA y no sobre las 24 h. Ventana diurna 07-18 h (12 h): mínimo 9.
- Las filas que no llegan al mínimo quedan NaN. No se imputan: la regresión y el discriminante las descartan listwise, y con 22,529 días-estación de MDA8 válido hay margen de sobra.

## 3. Resúmenes diarios

- `TOUT_max` = max(TOUT) sobre el día (24 h), mínimo 18 h válidas en el día (24 h). Descarta 1,272 días-estación (5.3 %). Máximo, no media: el motor fotoquímico es el pico térmico del día, y además alinea la variable con el MDA8, que también es un máximo.
- `SR_acum` = sum(SR) sobre el día (24 h), mínimo 9 h válidas en 07-18 h (12 h). Descarta 1,018 días-estación (4.3 %). Acumulado de insolación (kWh/m² sobre el día), no promedio de 24 h: el promedio queda diluido por las horas de noche, que valen 0 por definición. Como esas horas aportan 0, la suma sobre el día ES el acumulado de horas con luz. La completitud sí se mide sobre la ventana diurna: un día al que le faltan seis horas de tarde pasaría el 18/24 habiendo perdido la mitad de la energía real.
- `NO_06_09` = mean(NO) sobre 06-09 h (4 h), mínimo 3 h válidas en 06-09 h (4 h). Descarta 1,598 días-estación (6.7 %). Media de la ventana matutina: la carga de precursores de 06-09 h es la que alimenta el pico vespertino de ozono; promediarla sobre 24 h la mezcla con el mínimo nocturno.
- `NO2_06_09` = mean(NO2) sobre 06-09 h (4 h), mínimo 3 h válidas en 06-09 h (4 h). Descarta 1,624 días-estación (6.8 %). Ídem NO_06_09.
- `NOX_06_09` = mean(NOX) sobre 06-09 h (4 h), mínimo 3 h válidas en 06-09 h (4 h). Descarta 1,584 días-estación (6.6 %). Ídem NO_06_09.
- `CO_06_09` = mean(CO) sobre 06-09 h (4 h), mínimo 3 h válidas en 06-09 h (4 h). Descarta 1,554 días-estación (6.5 %). Ídem NO_06_09. CO es además el proxy de COV disponible: el SIMA no mide compuestos orgánicos volátiles especiados.
- `WSR_media` = mean(WSR) sobre el día (24 h), mínimo 18 h válidas en el día (24 h). Descarta 959 días-estación (4.0 %). Capacidad de dispersión del día.
- `WSR_min` = min(WSR) sobre el día (24 h), mínimo 18 h válidas en el día (24 h). Descarta 959 días-estación (4.0 %). Estancamiento. Es una señal distinta de la media, no una redundancia: un día ventoso con una hora de calma acumula localmente igual que uno de viento flojo constante, y la media no lo distingue.
- `PRS_media` = mean(PRS) sobre el día (24 h), mínimo 18 h válidas en el día (24 h). Descarta 751 días-estación (3.1 %). La presión varía poco dentro del día; la media la resume sin pérdida y es el indicador de sistema anticiclónico (subsidencia, inversión).
- `RH_media` = mean(RH) sobre el día (24 h), mínimo 18 h válidas en el día (24 h). Descarta 2,067 días-estación (8.6 %). Contenido de humedad del día.
- `RH_min_diurna` = min(RH) sobre 07-18 h (12 h), mínimo 9 h válidas en 07-18 h (12 h). Descarta 1,995 días-estación (8.3 %). Mínimo DIURNO: marca el desarrollo de la capa de mezcla de la tarde, que es cuando se forma el ozono. Sobre 24 h el mínimo cae de madrugada y mide otro fenómeno.
- `viento_u_media` = mean(viento_u) sobre el día (24 h), mínimo 18 h válidas en el día (24 h). Descarta 1,387 días-estación (5.8 %). Media VECTORIAL del viento (componente este-oeste). Promediar WSR da magnitud sin transporte neto: un día de viento fuerte que rota 180° tiene media escalar alta y media vectorial cercana a cero, y es la segunda la que describe a dónde se fue la masa de aire.
- `viento_v_media` = mean(viento_v) sobre el día (24 h), mínimo 18 h válidas en el día (24 h). Descarta 1,387 días-estación (5.8 %). Ídem viento_u_media (componente norte-sur).
- `PM10_media` = mean(PM10) sobre el día (24 h), mínimo 18 h válidas en el día (24 h). Descarta 805 días-estación (3.4 %). Carga de partículas del día. Entra como covariable de fuente común, no como precursor de ozono.
- `PM2.5_media` = mean(PM2.5) sobre el día (24 h), mínimo 18 h válidas en el día (24 h). Descarta 5,229 días-estación (21.9 %). Ídem PM10_media.
- `SO2_media` = mean(SO2) sobre el día (24 h), mínimo 18 h válidas en el día (24 h). Descarta 1,720 días-estación (7.2 %). Trazador de fuente industrial fija, que distingue el origen de la carga del de las fuentes móviles que aportan NOx y CO.
- `llovio` = 1 si alguna hora del día tuvo RAINF > 0; 0 si no hubo ninguna y hay al menos 18 horas válidas; NaN en otro caso. Descarta 706 días-estación (3.0 %). Una hora con lluvia es evidencia definitiva; afirmar que no llovió exige haber observado el día casi completo.
- WDR no se resume: es circular y ya está representada por las componentes viento_u y viento_v, que sí se pueden promediar.

## 4. Variables de agrupación

- zona (7 niveles) y msnm, del catálogo oficial docs/Ubicación de las estaciones de monitoreo.docx. La agrupación se fija a priori sobre geografía: derivarla del comportamiento del ozono y luego usarla para explicar ozono sería circular.
- tipo_dia (laborable, sabado, domingo, festivo) y festivo, promovidos desde notebooks/04_eda_cualitativas.qmd. El calendario genera 81 fechas para 2021-2025 completos; dentro de la cobertura real del dataset (que termina el 2025-06-30) caen 71 días de asueto, o 1,041 filas día-estación.
- temporada con el mismo corte de src/limpieza.py, no una variante paralela. Se conservan también mes, anio y fin_de_semana.

## 5. Unión con la variable objetivo

- Left join contra sima_limpio_diario.csv por (estacion, fecha): 23,931 filas, las mismas del diario de #13. Trae MDA8, ventanas_validas, O3_max_1h y las cuatro indicadoras de excedencia.
- MDA8 válido en 22,529 filas (94.1 %). Excedencias del umbral de 51 ppb (escenario principal de modelado): 6,917 (30.7 % de los días válidos).
- Filas con MDA8 válido Y los 17 predictores completos: 14,376 (60.1 % del total). Es el tamaño efectivo de un modelo que descarte listwise.
- PM2.5_media es el cuello de botella: sin ella el conjunto listwise sube a 16,957 filas, 2,581 más (18 %). Es la única variable cuya exclusión cambia el tamaño de muestra de forma material, y la decisión de conservarla o no corresponde a #54/#55.

## 6. Salida

- Dataset día-estación de modelado: 23,931 filas × 34 columnas (17 predictores agregados, 8 de agrupación y calendario, 7 de la variable objetivo).
