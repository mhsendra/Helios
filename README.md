# HELIOS

**HELIOS** es una aplicación de escritorio para el análisis del consumo energético de viviendas y la evaluación, optimización y simulación de instalaciones fotovoltaicas y sistemas de almacenamiento energético.

La aplicación permite partir de datos históricos de consumo eléctrico, generar un año representativo de 8.760 horas, estimar la producción fotovoltaica, dimensionar una instalación, evaluar distintas configuraciones de baterías, analizar el balance energético horario y estudiar sus resultados técnicos y económicos.

## Estado del proyecto

**Versión: 1.0.0**

HELIOS se encuentra en su primera versión funcional estable.

La versión 1.0 incluye:

- análisis y validación de datos históricos de consumo;
- estadísticas y perfiles horarios;
- generación de un año representativo de 8.760 horas;
- análisis de tarifas eléctricas;
- configuración y optimización de instalaciones fotovoltaicas;
- estimación de producción mediante PVGIS;
- cálculo del balance energético horario;
- estadísticas de producción y autoconsumo;
- evaluación y optimización de sistemas de almacenamiento mediante baterías;
- análisis económico de la instalación;
- análisis económico de configuraciones de batería;
- diagnóstico energético;
- generación de recomendaciones técnicas y económicas;
- generación de informes PDF;
- interfaz gráfica de escritorio basada en PySide6.

## Funcionalidades

### Análisis del consumo

HELIOS permite cargar datos históricos de consumo eléctrico y realizar:

- validación y control de calidad;
- estadísticas de consumo;
- perfiles horarios;
- comparativas;
- indicadores energéticos;
- análisis de tarifas;
- generación de un año representativo para las simulaciones.

El año representativo contiene **8.760 horas**, lo que permite utilizar el mismo período horario para comparar consumo y producción fotovoltaica.

### Simulación fotovoltaica

La aplicación permite configurar una instalación fotovoltaica mediante parámetros como:

- ubicación geográfica;
- inclinación;
- orientación;
- año de referencia;
- pérdidas;
- tecnología fotovoltaica;
- tipo de montaje;
- potencia de los módulos;
- número de módulos;
- superficie disponible;
- restricciones de instalación.

La producción solar se obtiene a partir de datos de **PVGIS**.

### Optimización de la instalación

HELIOS analiza la configuración disponible y permite obtener una recomendación de instalación teniendo en cuenta el consumo representativo y las restricciones introducidas.

La optimización y la simulación están separadas de la configuración básica del sistema, permitiendo modificar los parámetros y volver a calcular los resultados cuando sea necesario.

### Balance energético

El balance se calcula a nivel horario y permite obtener:

- consumo;
- producción fotovoltaica;
- autoconsumo;
- energía importada de la red;
- energía excedentaria vertida a la red.

El cálculo conserva las relaciones energéticas entre estas magnitudes y utiliza perfiles horarios de 8.760 horas.

### Almacenamiento energético

HELIOS permite evaluar sistemas de almacenamiento mediante baterías y comparar distintas capacidades de almacenamiento.

El análisis permite estudiar el efecto de la batería sobre el balance energético y cuantificar el ahorro adicional asociado al almacenamiento.

La optimización técnica de la batería y su evaluación económica son procesos independientes. De este modo, la configuración técnicamente más favorable puede analizarse posteriormente desde una perspectiva económica sin modificar los resultados de la optimización energética.

### Diagnóstico y recomendaciones

HELIOS analiza los resultados del balance energético para identificar situaciones relevantes como:

- elevado excedente fotovoltaico;
- elevada dependencia de la red;
- desajuste temporal entre producción y consumo.

Estos diagnósticos permiten interpretar el comportamiento energético del sistema y sirven de base para generar recomendaciones técnicas y económicas.

Las recomendaciones pueden incorporar información sobre sistemas de almacenamiento cuando los resultados del balance indican que pueden ser una solución adecuada.

### Análisis económico

HELIOS permite evaluar económicamente la instalación mediante diferentes escenarios y calcular, entre otros:

- coste sin instalación fotovoltaica;
- ahorro energético;
- ingresos por excedentes;
- costes de mantenimiento;
- flujo de caja;
- período de retorno;
- valor actual neto (NPV);
- tasa interna de retorno (IRR).

Los cálculos económicos utilizan el año representativo de consumo y producción para mantener la coherencia con la simulación energética.

Además, HELIOS permite evaluar económicamente distintas capacidades de almacenamiento, considerando el ahorro adicional generado por la batería y métricas como NPV, IRR y período de retorno.

La evaluación económica de baterías se utiliza para identificar la configuración económicamente más favorable sin sustituir la optimización técnica del sistema.

### Informes

La aplicación puede generar un **informe solar en PDF** con los principales resultados de la instalación y de su simulación energética.

Los informes pueden incluir información sobre:

- configuración de la instalación;
- producción fotovoltaica;
- balance energético;
- autoconsumo y dependencia de la red;
- análisis económico;
- almacenamiento energético;
- diagnósticos y recomendaciones.

## Flujo de trabajo

El flujo principal de HELIOS es:

1. **Configuración solar**
2. **Carga de datos**
3. **Análisis del consumo**
4. **Optimización solar**
5. **Simulación de producción**
6. **Balance y estadísticas solares**
7. **Evaluación de almacenamiento**
8. **Diagnóstico energético**
9. **Análisis económico**
10. **Recomendaciones**
11. **Generación de informes**

La aplicación controla las dependencias entre estas etapas. Las funciones que necesitan resultados previos permanecen desactivadas hasta que dichos resultados están disponibles.

Si se modifica la configuración solar, los resultados derivados de la configuración anterior se invalidan y deben volver a calcularse.

Los cambios en la configuración de almacenamiento invalidan los resultados del balance energético y las estadísticas que dependen de dicha configuración, manteniendo intacta la producción fotovoltaica calculada cuando esta no se ve afectada.

## Requisitos

- Python 3.11 o compatible con las dependencias del proyecto.
- Sistema operativo con soporte para PySide6.
- Conexión a Internet para consultar PVGIS cuando sea necesario.
- Archivo de datos de consumo en formato Excel (`.xlsx`).

Las dependencias de Python se encuentran en:

```text
requirements.txt
```

## Instalación

Se recomienda utilizar un entorno virtual:

```powershell
python -m venv .venv
```

Activar el entorno virtual en Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```powershell
python -m pip install -r requirements.txt
```

## Datos de consumo

HELIOS trabaja con datos históricos de consumo eléctrico almacenados en archivos Excel.

El archivo debe contener los datos necesarios para construir el perfil horario de consumo. La aplicación realiza un proceso de validación antes de utilizar los datos en los cálculos.

Los datos históricos se utilizan para construir el año representativo empleado posteriormente en la simulación energética y económica.

## PVGIS

La estimación de producción fotovoltaica utiliza **PVGIS** como fuente de datos de radiación y producción.

Los parámetros de configuración de la instalación determinan la consulta utilizada para obtener el perfil de producción.

Los datos obtenidos se transforman en un perfil horario de 8.760 horas para integrarlo con el año representativo de consumo.

## Informes PDF

Los informes solares contienen los principales resultados de la configuración, producción, balance energético y análisis económico de la instalación.

Cuando corresponde, los informes también pueden incorporar los resultados del almacenamiento, los diagnósticos energéticos y las recomendaciones obtenidas a partir de la simulación.

Los informes se generan desde la aplicación y pueden utilizarse para documentar los resultados de una simulación.

## Tests

El proyecto dispone de una batería de tests automatizados que cubre los principales componentes de análisis, simulación solar, balance energético, estadísticas, economía, almacenamiento, diagnóstico, recomendaciones e interfaz gráfica.

Para ejecutar todos los tests:

```powershell
python -m pytest -v
```

La versión 1.0 se ha validado mediante una regresión completa de la suite del proyecto.

## Estructura del proyecto

La arquitectura separa la lógica de negocio de la interfaz gráfica.

De forma simplificada:

```text
helios/
├── core/          # Modelos y lógica principal
├── solar/         # Producción, balance y estadísticas solares
├── gui/           # Interfaz gráfica
├── reports/       # Generación de informes
└── ...
tests/             # Tests automatizados
data/              # Datos del proyecto
requirements.txt   # Dependencias Python
pyproject.toml     # Configuración del proyecto
```

## Principios de diseño

HELIOS utiliza una arquitectura orientada a separar:

- adquisición y validación de datos;
- análisis del consumo;
- generación del año representativo;
- configuración solar;
- optimización;
- producción fotovoltaica;
- almacenamiento energético;
- balance energético;
- estadísticas;
- diagnóstico;
- economía;
- recomendaciones;
- presentación gráfica;
- generación de informes.

Esta separación permite modificar o ampliar cada área sin acoplarla directamente al resto de la aplicación y facilita mantener la coherencia entre los cálculos técnicos, económicos y las capas de presentación.

## Licencia

HELIOS se distribuye bajo la licencia MIT.

Consulta el archivo [LICENSE](LICENSE) para ver el texto completo de la licencia.

---

**HELIOS 1.0.0**
