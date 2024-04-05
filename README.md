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
  * **Ejemplo para ingresar el path del archivo desde la terminal**
      ```
      bash VariantsToTable_v1.0.bash
              Precionar Enter
      archivos/HG00405_degvcf_intervar.vcf
      ```

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


____


* TablaVariantesCalidadClinVar
  * **Objetivo** 
    * Generar, a partir de los archivos separados por tab generados con el script VariantsToTable, 3 tablas para importar en la base de datos Variantes, Calidades y ClinVar.
  * **Input**                          _Correr el script con la opción --help para más detalles_
    * Dependiendo el modo de corrida pueden variar. 
      * Generación a partir de los archivos _VariantsToTable_final.txt
        * path donde se encuentran los archivos txt. 
        * versión de ClinVar utilizada
        * identificador del diseño utilizado en la base de datos
      * Generación a partir de un archivo que ya contiene los datos del archivo .txt unidos
        * path del archivo desde el cual se va a partir
        * versión de ClinVar utilizada  
        * identificador del diseño utilizado en la base de datos
      * Generación a partir de un archivo que ya contiene los datos del archivo .txt unidos y limpios
        * path del archivo desde el cual se va a partir
        * versión de ClinVar utilizada
        * identificador del diseño utilizado en la base de datos
  * **Output**
    * Archivos de cada una de las tablas generadas
      * tabla_clinvar-\<fecha\>.csv
      * tabla_variantes-\<fecha\>.csv
      * tabla_calidades-\<fecha\>.csv
    * Archivos opcionales
      * Dataframe de salida del paso de concatenación de los archivos VariantsToTable_final
      * Dataframe de salida del archivo concatenado, posterior limpieza 
  * **Requerimientos**
    * python versión 3.8 o superior
    * Paquetes: argparse, datetime, glob, numpy, pandas y os
      * Para instalarlos ```pip install <Nombre del Paquete>```
  * **Ejemplo**
      ```
      python3 TablaVariantesCalidadClinVar_v1.0.py -i /home/user/foo -clinvar 240404 -dis 1
      ```


____


* TablaActualizacion
  * **Objetivo**
    * Generar tres archivos para la carga de las tablas: ClinVar, Variantes y ReporteVariantes 
  * **Input**                     _Correr el script con la opción --help para más detalles_
    * Submitter Report generado por ClinVar
    * Reporte enviado a ClinVar.
  * **Output**
    * Archivos de cada una de las tablas generadas
      * tabla_clinvar-\<submissionID\>-\<fecha\>.csv
      * tabla_variantes-\<submissionID\>-\<fecha\>.csv
      * tabla_calidades-\<submissionID\>-\<fecha\>.csv
  * **Requerimientos**
    * Paquetes: argparse, datetime, pandas, os
    * Para instalarlos ```pip install <Nombre del Paquete>```
  * **Ejemplo**
      ```
      python3 TablaActualizacion_v1.0.py -i archivos/listado_beds.tsv
      ```

____


* NormalizacionNomenclatura
  * **Objetivo**
    * A partir del archivo exportado de la base de datos con las variantes filtradas para reportar, se actualiza y/o corrige la nomenclatura del transcripto para ser reportada a ClinVar 
  * **Input**                     _Correr el script con la opción --help para más detalles_
    * Archivo exportado desde la base de datos con las variantes que cumplen con el criterio de selección
  * **Output**
    * Resultado_{panel}_{date_file}.csv
  * **Requerimientos**
    * Paquetes: argparse, datetime, os, pandas, re, requests, tqdm
    * Para instalarlos ```pip install <Nombre del Paquete>```
  * **Ejemplo**
      ```
      python3 NormalizacionNomenclatura_v1.0.py -i archivos/listado_beds.tsv
      ```

____


* CargaTemplate
  * **Objetivo**
    * Completar el Templado de ClinVar con las variantes seleccionadas.
  * **Input**                     _Correr el script con la opción --help para más detalles_
    * Archivo con las variantes a reportar y su nomenclatura actualizada\
    * Templado versión Lite de ClinVar
  * **Output**
    * Templado completo con las variantes a reportar y la información obligatoria
  * **Requerimientos**
    * Paquetes: argparse, datetime, openpyxl, os, pandas, shutil
    * Para instalarlos ```pip install <Nombre del Paquete>```
  * **Ejemplo**
      ```
      python3 CargaTemplate_v1.0.py -i archivos/listado_beds.tsv
      ```

      
____


