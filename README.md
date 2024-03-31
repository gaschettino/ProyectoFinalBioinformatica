# Proyecto Final de Bioinformatica
## Desarrollo de una base de datos de variantes genéticas obtenidas a partir de ensayos de next generation sequencing en el Hospital Garrahan

___


* VariantsToTable
  * **Objetivo**
    * Filtrar campos de uno o varios archivos vcf y transformarlos a tsv.
  * **Input**
    * archivo txt con un listado de path de archivos vcf
    * listado de archivos vcf separados por espacio
  * **Output**
    * Archivo transformado \<NombreArchivo\>_VariantsToTable_final.txt
    * Archivo log \<NombreArchivo\>_VariantsToTable_final.log
  * **Requerimientos**
    * Herramienta GATK4. 
    * Se debe agregar el path del archivo local.jar en el array tools del script.




____


* TablaDiseno
  * **Objetivo** 
    * Generar, a partir de un archivo tsv un archivo para importar en la base de datos la tabla Diseno.
  * **Input**                          _Correr el script con la opción --help para más detalles_
    * Archivo tsv con: 
      * path al archivo bed
      * laboratorio encargado del diseño de las sondas
      * empresa encargada de la síntesis
      * año de ingreso del diseño
      * tecnologia de secuenciación, amplicones o captura
      * tipo de diseño, panel, exoma 
  * **Output**
    * Archivos con la tabla generada
      * tabla_diseno-\<fecha\>.csv
  * **Requerimientos**
    * python versión 3.8 o superior
    * Paquetes: argparse, datetime, pandas, os y mygene
      * Para instalarlos ```pip install <Nombre del Paquete>```
  * **Ejemplo**
      ```
      python3 TablaDiseno_v1.0.py -i archivos/listado_beds.tsv
      ```
