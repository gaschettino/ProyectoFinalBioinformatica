#!/bin/bash

## Agregar el path al archivo local.jar de GATK
declare -A tools=(
  ["GATK"]="/mnt/c/Users/giovi/Ubuntu/tools/gatk-4.5.0.0/gatk-package-4.5.0.0-local.jar"
  )

echo -e -n "Seleccionar archivo que contiene path de los vcfs a convertir. \n * Si se quiere ingresar la lista por terminal, apretar enter. \n"
read LISTFILE

if [ -z "$LISTFILE" ] 
     then
     echo -e -n "Seleccionar listado de archivos a convertir separados por un espacio: \n"
     read FILES
     PASO="1"
elif [ ! -f "$LISTFILE" ] 
     then
     echo -e -n "Error: No se ingresó un path valido." $LISTFILE
     exit 
else
     PASO="2"
fi 

function trim {
    trimmed=$1
    trimmed=${trimmed%% }
    trimmed=${trimmed## }

    echo "$trimmed"
}

if [[ $PASO == '1' ]]
     then
     arr=( "${FILES}")
     for filepath in ${arr[@]}
     do
          echo "$filepath"
          filepath=$(trim ${filepath})
          if [ -z "$filepath" ] || [ ! -f "$filepath" ]
          then
               echo "##ERROR: El archivo $filepath es nulo o no existe."
               exit
          else
               INPUT=$filepath
               PATIENT=$(basename ${INPUT%_degvcf_intervar.vcf*})
               OUTPATH=$(dirname $INPUT)/VTT_OUT
               LOGPATH=$(dirname $INPUT)/VTT_LOG
               mkdir -p $LOGPATH $OUTPATH
               OUTPUT=$OUTPATH/$PATIENT\_VariantsToTable_final.txt
               LOG=$LOGPATH/$PATIENT\_VariantsToTable_final.log          
               echo "Generando archivo: $OUTPUT"
               java -Xmx20g -jar ${tools["GATK"]} VariantsToTable -V $INPUT -F CHROM -F POS -F ID -F REF -F ALT -F FILTER -GF AD -GF AO -GF DP -GF GQ -GF GT -GF NR -GF NV -GF PL -GF RO -F SNPEFF_GENE_ID -F VARTYPE -F CLNSIG -F CLNHGVS -F set --disable-tool-default-read-filters --show-filtered -O $OUTPUT > $LOG 2>&1        
          fi
     done
elif [[ $PASO == '2' ]]
     then 
     while read filepath; do
     if [ -z "$filepath" ] || [ ! -f "$filepath" ]
     then
          echo "##ERROR: El archivo $filepath es nulo o no existe."
          exit
     else
          echo "Entra al else"
          INPUT=$filepath
          PATIENT=$(basename ${INPUT%_degvcf_intervar.vcf*}) 
          OUTPATH=$(dirname $INPUT)/VTT_OUT
          LOGPATH=$(dirname $INPUT)/VTT_LOG
          mkdir -p $LOGPATH $OUTPATH
          OUTPUT=$OUTPATH/$PATIENT\_VariantsToTable_final.txt
          LOG=$LOGPATH/$PATIENT\_VariantsToTable_final.log
          echo "Generando archivo: $OUTPUT"
          java -Xmx20g -jar ${tools["GATK"]} VariantsToTable -V $INPUT -F CHROM -F POS -F ID -F REF -F ALT -F FILTER -GF AD -GF AO -GF DP -GF GQ -GF GT -GF NR -GF NV -GF PL -GF RO -F SNPEFF_GENE_ID -F VARTYPE -F CLNSIG -F CLNHGVS -F set --disable-tool-default-read-filters --show-filtered -O $OUTPUT > $LOG 2>&1
     fi
     done < $LISTFILE
else
     echo "##ERROR: Selección de paso incorrecta."
     exit
fi

echo "#################################################################################"
echo "#################################################################################"
echo "#################################################################################"
