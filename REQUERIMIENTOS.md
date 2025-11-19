# Requerimientos del Proyecto SuperMercado

Para ejecutar todo el ecosistema (servidor Java + interfaz Python) es necesario contar con los siguientes componentes instalados y configurados.

## 1. Requisitos del sistema
- **Sistema operativo**: Windows 10/11 (probado en entorno Windows, puede adaptarse a Linux/macOS).
- **Conexión a internet** para descargar dependencias Maven y paquetes Python la primera vez.
- **PostgreSQL 14+** en ejecución con acceso local.

## 2. Base de datos
- Servidor PostgreSQL accesible en `localhost:5432`.
- Base de datos llamada `bd_productos_supermercado`.
- Usuario: `supermercado`, contraseña: `Super123`.
- Permisos: crear tablas, insertar, actualizar y eliminar registros.

> **Nota:** si cambias nombre de BD, usuario o contraseña, ajusta las constantes dentro de `ConexionBaseDatos.java`.

## 3. Servidor Java
- **Java Development Kit (JDK) 21** o superior.
- **Apache Maven 3.9+** para compilar el módulo Java (`Java/`):
  ```bash
  cd Java
  mvn clean package
  ```
- Dependencias gestionadas por Maven:
  - `org.postgresql:postgresql:42.7.1`
  - `com.google.code.gson:gson:2.10.1`

La compilación genera `Java\target\conexion-server-1.0-jar-with-dependencies.jar`, utilizado por `scripts\iniciar.bat`.

## 4. Interfaz Python
- **Python 3.10+** (probado con 3.10/3.11).
- Librerías recomendadas (instalar vía `pip`):
  ```bash
  pip install pillow reportlab qrcode opencv-python pyzbar matplotlib
  ```
  - `pillow`: carga del logo.
  - `reportlab`: generación de facturas en PDF.
  - `qrcode`: códigos QR en la factura.
  - `opencv-python` + `pyzbar`: escaneo de códigos de barras con cámara.
  - `matplotlib`: gráficos en el módulo de contabilidad.

> Si alguna librería no está instalada, las funciones relacionadas mostrarán avisos y continuarán sin esa característica.

## 5. Script de inicio
- El archivo `scripts\iniciar.bat` asume que:
  1. Se ejecutó `mvn clean package` y el jar existe en `Java\target`.
  2. Python se encuentra en el PATH del sistema.
  3. El script se lanza desde `scripts\` (lo hace automáticamente).

## 6. Resumen rápido de instalación
1. Instalar **PostgreSQL**, crear la BD y usuario indicados.
2. Instalar **JDK 21** y **Maven** → compilar el módulo Java.
3. Instalar **Python 3.10+** y los paquetes listados.
4. Ejecutar `scripts\iniciar.bat` para iniciar servidor Java y la interfaz gráfica.

Con estos requisitos cumplidos el proyecto puede ejecutarse sin problemas en un entorno de desarrollo estándar.

