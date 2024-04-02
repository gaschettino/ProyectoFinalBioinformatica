# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 21:54:59 2023

@author: Giovanna
"""

import argparse
from datetime import datetime
from openpyxl import load_workbook
import os
import pandas as pd
import shutil

parser = argparse.ArgumentParser(description='Script que arma el Templado de ClinVar para la carga.', 
        usage='use "%(prog)s --help or -h" for more information', 
        formatter_class=argparse.RawTextHelpFormatter, 
        epilog=('\t \t ######################################################################### \n \n'))
parser.add_argument('-i', dest='inputfile', required=True, type=str, help='Requerido: Con las variantes a cargar. Es la salida del script NormalizacionNomenclatura. \n')
parser.add_argument('-t', dest='template', required=False, type=str, default="/home/usuario/OneDrive/Materias/ProyectoFinal/Templados/SubmissionTemplateLite.xlsx", help='Opcional: Path del archivo templado LITE de ClinVar. Se va a acceder al almacenado en la carpeta bundle, a menos que se espeficique lo contrario.\n')
parser.add_argument('-o', dest='outpath', required=False, type=str, help='Opcional: Path de la carpeta donde se quiere guardar el archivo. Si no se declara, será en la misma carpeta que el inputfile.\n')
args = parser.parse_args()


date_file=datetime.now().strftime("%Y%m%d_%H%M")




if not os.path.isfile(args.inputfile):
    print(f'##ERROR: No existe el archivo {args.inputfile}')
    exit()

if args.outpath and os.path.exists(args.outpath):
    filename=f"{args.outpath}/Template_Lite_{date_file}.xlsx"
    rejectedfile=f"{args.outpath}/Rejected_{date_file}.csv"    
elif args.outpath:
    print (f"##ERROR: {args.outpath} no existe.")
    exit()
else:
    filename=f"{os.path.dirname(args.inputfile)}/Template_Lite_{date_file}.xlsx"
    rejectedfile=f"{args.outpath}/Rejected_{date_file}.csv"
    
def limpiar_gen(valor):
    if '-' in valor:
        return ''
    elif '.' in valor:
        return valor.split('.')[0]
    else:
        return valor

'''
Leo el inputfile
'''
df = pd.read_csv(args.inputfile)

'''
Armo un archivo de variantes rechazadas que no podrán ser cargadas a ClinVar a pesar de cumplir condiciones porque falta el HGVS. Son para revisión manual.
'''

df_fail=df[df.HGVS.isna()]
df_fail.to_csv(rejectedfile, index=False)    

'''
Preparación del dataframe para cargar en el Templado
'''
df=df[df.HGVS.notna()]
df.reset_index(drop=True, inplace=True)
df.drop_duplicates("HGVS", keep="first", inplace=True)   
df.reset_index(drop=True, inplace=True)    


df.gen = df.gen.apply(lambda x: limpiar_gen(x))
df.gen=df.gen.replace("DDX58",'RIGI')

'''
Preparación de las dos solapas que se utilizan para cargar a ClinVar
'''
df_Variant=pd.DataFrame(columns = ["HGVS","ConditionID_type","Condition_ID_value","Preferred_condition_name","Explanation_MC","Clinical_significance","Date_last_evaluated","CS_citations","URL_CS","Comment_CS","Explanation_CS","DR","Functional_consequence","Local_ID","URL","Variation_identifiers","Gene_symbol","Location","Alternate_designations_","Official_allele_name","Comment","Private_comment","ClinVarAccession","Novel_or_Update","Replaces_ClinVarAccessions"])

df_ExpEvidence=pd.DataFrame(columns = ["HGVS","ConditionID_type","Condition_ID_value","Preferred_condition_name","Collection_method","Allele_origin","Affected_status","Sex","Age_range","Population_Group","Geographic_origin","N_individuals","Private_comment","Testing_laboratory","Date_variant_was_reported_to_submitter"])


df_Variant.HGVS=df.HGVS
df_Variant.Preferred_condition_name="not specified"
df_Variant.Clinical_significance="Benign"
df_Variant.Date_last_evaluated=datetime.now().strftime("%Y-%m-%d")
for row in range(0,len(df)):
    df_Variant.Comment_CS[row]=f"This variant is classified as Benign based on local population frequency. This variant was detected in {df.frecuencia[row]}% of patients studied by a panel of primary immunodeficiencies. Number of patients: {df.n_pacientes[row]}. Only high quality variants are reported."
df_Variant.Gene_symbol=df.gen
df_Variant.CS_citations=""
df_ExpEvidence.HGVS=df.HGVS
df_ExpEvidence.Preferred_condition_name="not specified"
df_ExpEvidence.Allele_origin='germline'
df_ExpEvidence.Affected_status='no'
df_ExpEvidence.Sex='mixed'
df_ExpEvidence.Age_range='<18'
df_ExpEvidence.N_individuals=df.n_pacientes
df_ExpEvidence.Collection_method='clinical testing'



'''
Cargo el templado y lo copio al output que voy a usar
'''
book = load_workbook(args.template)
shutil.copy(args.template, filename)

'''
A la copia le agrego los dataframes preparados.
Cuidado que está appendeado el número de linea a utilizar.
'''
with pd.ExcelWriter(filename, mode="a",engine="openpyxl",if_sheet_exists="overlay") as writer:
    df_Variant.to_excel(writer, sheet_name="Variant",header=None, startrow=9,index=False)
    df_ExpEvidence.to_excel(writer, sheet_name="ExpEvidence",header=None, startrow=11,index=False)    
    
print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - Script finalizado.')
