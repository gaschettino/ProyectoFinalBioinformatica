# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 20:43:12 2024

@author: giovi

"""
import argparse
from datetime import datetime
import pandas as pd
import os
parser = argparse.ArgumentParser(description='Generar archivos necesarios para la actualización de la base de datos luego del reporte de variantes a ClinVar (*_submitter_report_B.txt)', formatter_class=argparse.RawTextHelpFormatter, epilog = ' ')

parser.add_argument('-i1', dest='inputfile1', required=True, help='Requerido: Path del archivo devuelto por clinvar.')
parser.add_argument('-i2', dest='inputfile2', required=True, help='Requerido: Path del archivo con las variantes reportadas a clinvar.')
parser.add_argument('-outpath', dest='outpath', required=False, help='Opcional: Path de la carpeta output. Si no se indica será el mismo lugar donde está el archivo de corrida')

def abrir_archivo (path):
    lineafecha=''
    with open(path, 'r') as file:
        for line in file:
            if line.startswith('#'):
                ultimo_encabezado = line.strip('#').strip()
                if 'Date:' in ultimo_encabezado:
                    lineafecha=ultimo_encabezado.strip('Date:').strip()
        file.seek(0)
        dataframe = pd.read_csv(file, comment='#', delimiter='\t', names=ultimo_encabezado.split(), index_col=False)
    return dataframe, lineafecha

args = parser.parse_args()

date_file=datetime.now().strftime("%Y%m%d_%H%M")
date=datetime.now().strftime("%Y-%m-%d")

if not os.path.isfile(args.inputfile1) or not os.path.isfile(args.inputfile2):
    if not os.path.isfile(args.inputfile1):
        print(f'##ERROR: No existe el archivo {args.inputfile1}')
    else:
        print(f'##ERROR: No existe el archivo {args.inputfile2}')
    exit()

if args.outpath and os.path.exists(args.outpath):
    outputtablas=args.outpath
elif args.outpath:
    print (f"##ERROR: {args.outpath} no existe.")
    exit()
else:
    outputtablas=os.path.dirname(args.inputfile1)

archivo=args.inputfile1
SUB_ID=archivo.split('/')[-1].split('_')[0]

df, fecha=abrir_archivo(archivo)

# =============================================================================
# =============================================================================
#                           TABLA REPORTE CLINVAR
# =============================================================================
# =============================================================================

reporte_clinvar=pd.DataFrame(columns=['id_submission', 'id_clinvar'])
reporte_clinvar.id_submission=df.SCV
reporte_clinvar.id_clinvar=df.VariationID

filename=f"{outputtablas}/tabla_reporte_clinvar-{SUB_ID}-{date_file}.csv"
reporte_clinvar.to_csv(filename, index=False)

# =============================================================================
# =============================================================================
#                               TABLA CLINVAR
# =============================================================================
# =============================================================================
tabla_clinvar=pd.DataFrame(columns=["id_clinvar", "CLNSIG", "CLNHGVS", "clinvar_date", "last_update"])


tabla_clinvar.id_clinvar=df.VariationID
tabla_clinvar.CLNSIG=df.Clinical_significance
tabla_clinvar.CLNHGVS=df.Your_variant_description_HGVS
tabla_clinvar.clinvar_date=fecha

filename=f"{outputtablas}/tabla_clinvar-{SUB_ID}-{date_file}.csv"
tabla_clinvar.to_csv(filename, index=False)

# =============================================================================
# =============================================================================
#                               TABLA VARIANTES
# =============================================================================
# =============================================================================
archivo=args.inputfile2

variantes=pd.read_csv(archivo)
variantes=variantes[["ref_build","cromosoma","posicion","referencia","alternativo", 'HGVS']]
    
variantes.drop_duplicates(subset=["ref_build","cromosoma","posicion","referencia","alternativo"],keep='first', inplace=True)

clinvar=tabla_clinvar[["id_clinvar", 'CLNHGVS']]
resultado = pd.merge(variantes, clinvar, left_on='HGVS', right_on='CLNHGVS', how='inner')

filename=f"{outputtablas}/tabla_variantes2-{SUB_ID}-{date_file}.csv"
resultado.to_csv(filename, index=False)


print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - Script finalizado.')
