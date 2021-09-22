# FTP_XM
 
# XM_Pub_Checker
 
XM opera el Sistema Interconectado Nacional (SIN) y administramos el Mercado de Energía Mayorista (MEM), para lo cual realiza las funciones de Centro Nacional de Despacho -CND-, Administrador del Sistema de Intercambios Comerciales -ASIC- y Liquidador de Cuentas de Cuentas de cargos por Uso de las redes del Sistema Interconectado Nacional - LAC. Además, XM administra las Transacciones Internacionales de Electricidad de corto plazo -TIE- con Ecuador ([enlace](https://www.xm.com.co/corporativo/Paginas/Nuestra-empresa/que-hacemos.aspx) para mayor informacion sobre XM).

XM procesa y entrega grandes cantidaddes de informacion al manejar diferentes procesos del mercado energetico y regulacion en Colombia. Uno de los medio por los cuales XM entrega informacion a las empresas de energia, es por medio de un servidor FTP, en este se puede ingresar y descargar los archivos que fueron procesados previamente por XM, pero la mayoria de procesos que se realizan con estos archivos son monotomas, pueden llegar a ser tediosas y tomando varias horas de trabajo si se realizan manualmente.

Con el fin de generar un programo, eficiente y eficaz que pueda realizar tareas especificas y entregue informacion relevante de los archivos en el servidor FTP , se tiene en desarrollo este codigo el cual puede ser utilizado por cualquier empresa interesada en automatizar esta tarea.

## Librerias utilizadas

- **ftplib:** Para realizar la conexion al servidor FTP.
- **pandas:** Para el manejo de archivos de multiples fuentes.
- **io:** Utilizada para procesar archivos en el servidor FTP.
- **re:** Utilizado para filtrar nombres y/o extension de los archivos, con expresiones regulares.


## Modo de uso

(Esta es una primera version que puede ser actualizada a un encapsulamiento el cual no requiera abrir el codigo para modificar los valores de algunas variables)

Una vez instaladas las librerias necesarias, solo es necesario modificar tres variables que se encuentran en la parte principal de la ejecucion del codigo:

```Python
FTP_USER = "Usuario_XM" #Usuario
FTP_PASS = "password"  #Password
Siglas_comercializador="NNNN"
```

Estas variables son las que dan el acceso al servidor FTP y enrutan a la carpeta de la empresa que se quiere descargar la informacion. Cuando el codigo ya haya sido ejecutado el programa imprimira por consola las instrucciones que se deben seguir para acceder a los tres procesos que actualmente se tienen desarrollados:

- Descargar los consumos consolidados de las fronteras segun lo reportado en el AENC
- Visualizar un resumen general de todos los archivos dentro de la carpeta
- Descargar el consolidado de un archivo en concreto

En caso de querer utilizar este codigo en cualquier equipo, es posible generar una version ejecutable del codigo, para esto se utiliza la libreria de Pyinstaller la cual ya fue probada con la ultima version de este codigo, junto con la informacion de ingreso de la empresa CEDENAR SA ESP, para mas informacion de como realizar este proceso con Pyinstaller se pueden referir al tutorial del siguiente enlace : https://datatofish.com/executable-pyinstaller/.
