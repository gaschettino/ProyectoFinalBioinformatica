# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 14:18:31 2023

@author: Giovanna Aschettino
"""

import argparse
from datetime import datetime
import glob
import numpy as np
import pandas as pd
import os

parser = argparse.ArgumentParser(description='Script que genera, a partir de archivos VariantToTable 3 tablas diferentes para importar a la base de datos: \n   * Variantes \n   * Calidades \n   * ClinVar', 
        usage='use "%(prog)s --help or -h" for more information', 
        formatter_class=argparse.RawTextHelpFormatter, 
        epilog=('\t \t ######################################################################### \n \n'))
parser.add_argument('-i', dest='initialpath', required=True, type=str, help='Requerido: Carpeta inicial donde se encuentran los archivos a procesar. \n')
parser.add_argument('-clinvar', dest='clinvar', required=True, type=str, help='Requerido: Fecha de actualización del clinvar utilizado en formato YYYY-MM-DD. \n\n\n')
parser.add_argument('-dis', dest='dis', required=True, type=int, help='Requerido: Identificador del diseño de secuenciación elegido.')

parser.add_argument('-o1', dest='out1', required=False, action="store_true", help='Opcional: Indica que se quiere guardar el dataframe de la concatenación de archivos del paso 1 en la carpeta de trabajo.\n')

parser.add_argument('-p2', dest='paso2', required=False, action="store_true", help='Opcional: Booleano que indica que se quiere saltear el paso 1 y partir directamente desde un archivo con el dataframe de todos los pacientes incluidos.\n')
parser.add_argument('-f2', dest='file2', required=False, type=str, default="", help='Opcional: Path del archivo que contiene el dataframe de todas las variantes. Solo válido en caso de querer saltear el paso 1.\n')
parser.add_argument('-o2', dest='out2', required=False, action="store_true", help='Opcional: Indica que se quiere guardar el dataframe de la concatenación de archivos del paso 2 en la carpeta de trabajo.\n')

parser.add_argument('-p3', dest='paso3', required=False, action="store_true", help='Opcional: Booleano que indica que se quieren saltear los pasos 1 y 2 y partir directamente desde un archivo con el dataframe de todos los pacientes incluidos y limpio.\n')
parser.add_argument('-f3', dest='file3', required=False, type=str, default="", help='Opcional: Path del archivo que contiene el dataframe de todas las variantes limpias. Solo válido en caso de querer saltear el paso 1 y 2.\n')

parser.add_argument('-ref', dest='ref', required=False, default='hg38', help='Opcional: Genoma de referencia utilizado. Valor por default: hg38\n')

args = parser.parse_args()

# =============================================================================
# args = argparse.Namespace(
#     initialpath='/home/usuario/Downloads/BaseDeDatos2024/Exomas',
#     clinvar='2024-01-15',
#     dis='21',
#     out1=False,
#     paso2=False,
#     out2='',
#     paso3=False,
#     file3='',
#     ref='hg38'
# )
# 
# =============================================================================
def transformar_genotipo(gt, ref, alt):
    if '/' in gt:
        alelos=gt.split('/')
    elif '|' in gt:
        alelos=gt.split('|')
    if alelos[0] == ref: 
        if alelos[1] == ref:
            return '0/0'
        elif alelos[1] == alt:
            return '0/1'
    elif alelos[1] == ref: 
        if alelos[0] == alt:
            return '0/1'
    elif alelos[0] == alt and alelos[1] == alt :
        return '1/1'

    elif alelos[0] == '.':
        if alelos[1] == ref:
            return './0'
        elif alelos[1] == alt:
            return './1'
    elif alelos[1] == '.':
        if alelos[0] == ref:
            return './0'
        elif alelos[0] == alt:
            return './1'
    else:
        return './.'


dt_string = datetime.now().strftime("%Y%m%d_%H.%M.%S")

dirpath=f"{args.initialpath}/BD_{dt_string}"

if os.path.exists(args.initialpath):
    os.mkdir(dirpath)
    os.chdir(dirpath)
else:
    print (f"##ERROR: {args.initialpath} no existe.")
    exit()

if args.paso2 and not args.paso3:
    if not os.path.isfile(args.file2):
        print(f'##ERROR: Se decidió saltear el paso 1 pero no existe el archivo {args.file2}')
        exit()
elif args.paso3 and not args.paso2:
    if not os.path.isfile(args.file3):
        print(f'##ERROR: Se decidió saltear el paso 1 y 2 pero no existe el archivo {args.file3}')
        exit()

if not args.paso2 and not args.paso3:
    '''
    Se buscan todos los archivos que terminan en "_VariantsToTable_final.txt"
    Se genera un dataframe con todos los archivos encontrados
    Se eliminan las lineas duplicadas (variantes que pertenecen a un mismo paciente)
    '''
    print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S")} - Paso 1')    
    variants_list = glob.glob(f'{args.initialpath}/*/*/*_VariantsToTable_final.txt')
    
    list_df=[]
    for file in variants_list:
      samplename=file.replace("_degvcf_intervar_VariantsToTable_final.txt", "")
      samplename=samplename.replace("_Step9", "")      
      df = pd.read_table(file, sep="\t", header=0, dtype={'CHROM': str})

      # df.columns=["CHROM", "POS", "ID", "REF", "ALT", "FILTER", "SNPEFF_GENE_ID", "VARTYPE", "CLNSIG", "CLNHGVS", "set", "SNPEFF_EFF", "AD", "AO", "DP", "GQ", "GT", "NR", "NV", "PL", "RO"]
      df.columns=["CHROM", "POS", "ID", "REF", "ALT", "FILTER", "SNPEFF_GENE_ID", "VARTYPE", "CLNSIG", "CLNHGVS", "set", "AD", "AO", "DP", "GQ", "GT", "NR", "NV", "PL", "RO"]
            
      df["Patient"]=samplename
      df.drop_duplicates(subset=["CHROM", "POS", "ID", "REF", "ALT", "FILTER","Patient", "AD", "AO", "DP", "GQ", "GT", "NR", "NV", "PL", "RO"], keep='first', inplace=True)
      list_df.append(df)
      del(file, samplename, df)
    
    df_concat=pd.concat(list_df, axis=0, ignore_index=True)
    del list_df
    
    if args.out1:
        print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S")} - Se guarda el archivo del paso 1')    
        df_concat.to_csv(f"Paso1_todos_{dt_string}.csv",index=False)
elif args.paso2 and not args.paso3:   
    '''
    Si quiero pasar directamente por el paso 1
    '''    
    print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S")} - Leyendo el archivo salteando el paso 1')
    df_concat=pd.read_csv(args.file2)
elif args.paso3:
    print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S")} - Leyendo el archivo salteando el paso 1 y el paso 2')
    df_concat=pd.read_csv(args.file3)

'''
Campo Allele Depth

- Separación en dos:
  - Profundidad para el alelo de referencia 
  - Profundidad para el alelo alternativo.

HaplotypeCaller, DeepVariant y SamTools cumplen con estas características  
'''


if not args.paso3:
    print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S")} - Paso 2')
    
    df_concat[["Ref_depth", "Alt_depth"]] = pd.DataFrame(df_concat.AD.str.split(',', expand=True))
    
    
    '''
    Freebayes
    
    Desdobla el AD en AO y RO. Pero pone el DP. No siempre es exacta la suma de DP respecto de la suma de AO y RO, lo cual es posible, por alguna base que podría estar mal leída, se deja el valor de DP que calculó el programa.
    - Asigno los valores de RO y AD a las columnas desdobladas en el paso anterior.
    '''
    
    df_concat['Ref_depth'] = df_concat['RO'].fillna(df_concat['Ref_depth'])
    df_concat['Alt_depth'] = df_concat['AO'].fillna(df_concat['Alt_depth'])
    df_concat['Ref_depth'] = pd.to_numeric(df_concat['Ref_depth'], errors='coerce').astype('Int64')
    df_concat['Alt_depth'] = pd.to_numeric(df_concat['Alt_depth'], errors='coerce').astype('Int64')

    
    '''
    Platypus
    
    - NR profundidad de la referencia. 
    - NV profundidad del alternativo
    - Para DP, a falta de una alternativa, se suma los valores de NR y NV
    '''
    
    df_concat['Ref_depth'] = df_concat.apply(lambda row: pd.to_numeric(row['NR'], errors='coerce') if pd.notna(row['NR']) else row['Ref_depth'], axis=1)
    
    df_concat['Alt_depth'] = df_concat.apply(lambda row: pd.to_numeric(row['NV'], errors='coerce') if pd.notna(row['NV']) else row['Alt_depth'], axis=1)
    
    df_concat['DP'] = df_concat['DP'].fillna(df_concat['Alt_depth'].add(df_concat['Ref_depth'], fill_value=0))
    
    '''
    Si hubieran quedado valores de profundidades tanto total como de alternativo o referencia en blanco, se eliminan
    '''
    
    df_concat['Ref_depth'] = pd.to_numeric(df_concat['Ref_depth'], errors='coerce').astype('Int64')
    df_concat['Alt_depth'] = pd.to_numeric(df_concat['Alt_depth'], errors='coerce').astype('Int64')
    df_concat['DP'] = pd.to_numeric(df_concat['DP'], errors='coerce').astype('Int64')
    
    
    '''
    Si hubieran quedado valores con alternativo Y referencia de 0 se elimina la linea.
    '''
    df_concat[df_concat.ALT.str.contains(',')]
    df_eliminar=df_concat[(df_concat.Ref_depth == 0) & (df_concat.Alt_depth == 0)]
    
    df_concat.drop(df_eliminar.index, inplace=True)
    
    df_eliminar=df_concat[df_concat.ALT.str.contains(',')]
    df_concat.drop(df_eliminar.index, inplace=True)
    
    '''
    Si algun valor de profundidad es NaN los elimino.
    '''
    
    df_concat = df_concat.dropna(subset=['DP', 'Ref_depth', 'Alt_depth'], how='any')
    
    
    '''
    Chequeo valores de NR o NV que por error contengan una coma. 
    Los elimino.
    '''
    
    df_eliminar=df_concat[df_concat['NR'].astype('str').str.contains(',', na=False)]
    df_concat.drop(df_eliminar.index, inplace=True)
    
    
    df_eliminar=df_concat[df_concat['NV'].astype('str').str.contains(',', na=False)]
    df_concat.drop(df_eliminar.index, inplace=True)
    
    df_eliminar=df_concat[(df_concat.Ref_depth.isna() | df_concat.Alt_depth.isna())]
    df_concat.drop(df_eliminar.index, inplace=True)

    '''
    Armo una columna según el llamador que la detecta.
    '''
    
    df_tmp=df_concat.set.str.get_dummies(sep=',')
    df_concat=pd.concat([df_concat, df_tmp], axis=1, join="inner")
    columnas_a_sumar = ["DeepVariant", "FreeBayes", "HaplotypeCaller", "Platypus", "SamTools"]
    for columna in columnas_a_sumar:
        if columna not in df_concat.columns:
            df_concat[columna] = 0
    
    df_concat["cantidad"]=df_concat[["DeepVariant","FreeBayes","HaplotypeCaller","Platypus","SamTools"]].sum(axis=1)
    del(df_tmp)
    
    
    '''
    Asigno el nombre de corrida y el nombre del paciente
    '''
    
    df_concat['Corrida'] = df_concat['Patient'].str.split(r'[\\/]').str[-3]
    df_concat['Patient'] = df_concat['Patient'].str.split(r'[\\/]').str[-1]
    
    '''
    Elimino el chr del campro cromosoma
    '''
    df_concat.CHROM=df_concat.CHROM.str.replace('chr', '')
    '''
    Si quiero un archivo con todas las modificaciones.
    '''
    
    if args.out2:
        print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S")} - Se guarda el archivo del paso 2')    
        df_concat.to_csv(f"Paso2_pre_tablas_{dt_string}.csv",index=False)

print (f'{datetime.now().strftime("%Y%m%d %H:%M:%S")} - Paso 3')

'''
Agrego una carpeta para guardar las tablas comunes dentro de la carpeta output. 
'''

outputtablas=f"{dirpath}/Tablas_"+dt_string+"/"
os.mkdir(outputtablas)
print(len(df_concat))
df_concat=df_concat[df_concat['REF'].str.len()<256]
print(len(df_concat))
df_concat=df_concat[df_concat['ALT'].str.len()<256]
print(len(df_concat))

'''
Armado de la Tabla Clinvar

- Genero el dataframe
- Elimino duplicados
- Guardo en archivo csv

- Si es un archivo nuevo hay que agregar la linea para el valor del ClinVar de 0 y - para que asigne un valor Dummy y que ya quede. Sino todas las variantes que agregue van a generar problemas a la hora de importar.

'''

print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S")} - Tabla Clinvar')

tabla_clinvar=pd.DataFrame(columns=["id_clinvar", "CLNSIG", "CLNHGVS", "clinvar_date", "last_update"])

df_concat.ID=df_concat.ID.replace('\.+', np.nan, regex=True)
df_concat.ID=df_concat.ID.replace(';-', '', regex=True)
df_concat["id_Clinvar"]=df_concat.ID.str.replace('rs.+;', '', regex=True).replace('rs.+', np.nan, regex=True)

tabla_clinvar["id_clinvar"]=df_concat.id_Clinvar
tabla_clinvar["CLNSIG"]=df_concat.CLNSIG.str.replace(',', '|')
tabla_clinvar["CLNHGVS"]=df_concat.CLNHGVS
tabla_clinvar["clinvar_date"]=args.clinvar
tabla_clinvar["last_update"]=''

# =============================================================================
# ### SOLO si es la primera vez que armo la base de datos van estas líneas.
# tabla_clinvar.loc[len(tabla_clinvar.index)] = ['0', 'Dummy', 'Dummy',args.clinvar,"" ]
# tabla_clinvar.loc[tabla_clinvar['id_clinvar'] == '-', ['CLNSIG', 'CLNHGVS']] = ['Dummy', 'Dummy']
# 
# =============================================================================

tabla_clinvar.drop_duplicates(keep='first',inplace=True, ignore_index=True)

tabla_clinvar = tabla_clinvar[tabla_clinvar["id_clinvar"].notna()==True]

filename=outputtablas + 'tabla_clinvar-' + dt_string + '.csv'

tabla_clinvar.to_csv(filename, index=False)


''' 
Armado de la tabla Variantes

- Genero el dataframe.
- Para posicion_end se pone null si no hay nada automáticamente en la tabla. Es por si queremos agregar CNV alguna vez.
- Elimino duplicados si lo hubiera.  
'''

print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S")} - Tabla Variantes')


tabla_variantes=pd.DataFrame(columns=["ref_build","cromosoma","posicion","referencia","alternativo","tipo","gen","id_clinvar","created_at"])
tabla_variantes.cromosoma=df_concat.CHROM.astype(str)
tabla_variantes.posicion=df_concat.POS
tabla_variantes.ref_build=args.ref

tabla_variantes.referencia=df_concat.REF
tabla_variantes.alternativo=df_concat.ALT
tabla_variantes.tipo=df_concat.VARTYPE
tabla_variantes.gen=df_concat.SNPEFF_GENE_ID
tabla_variantes.id_clinvar=df_concat.id_Clinvar
tabla_variantes.id_clinvar=tabla_variantes.id_clinvar.fillna(0)
# tabla_variantes['efecto'] = df_concat['SNPEFF_EFF'].str.replace(r"(\s*\(.*?\)\s*)", " ").str.strip().str.replace(' ', '')
# tabla_variantes['efecto']=tabla_variantes['efecto'].str.split(',').apply(lambda x : ','.join(set(x)))

tabla_variantes.drop_duplicates(subset=["ref_build","cromosoma","posicion","referencia","alternativo"], keep='first',inplace=True, ignore_index=True)

tmp_var=tabla_variantes[tabla_variantes.id_clinvar == '-']


filename=outputtablas + 'tabla_variantes-' + dt_string + '.csv'

tabla_variantes.to_csv(filename, index=False)


''' 
Armado de la Tabla Calidades
'''

print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S")} - Tabla Calidades')

df_concat['GT_transformado'] = df_concat.apply(lambda row: transformar_genotipo(row['GT'], row['REF'], row['ALT']), axis=1)

tabla_calidades=pd.DataFrame(columns=["id_genomica","id_corrida","id_diseno","ref_build","cromosoma","posicion","referencia","alternativo","GT","reads_ref","reads_alt","DP","filter","haplotypecaller","freebayes","samtools","platypus","deepvariant","created_at"])

tabla_calidades.id_genomica=df_concat.Patient
tabla_calidades.id_corrida=df_concat.Corrida
tabla_calidades.id_diseno=args.dis
tabla_calidades.ref_build=args.ref
tabla_calidades.cromosoma=df_concat.CHROM
tabla_calidades.posicion=df_concat.POS
tabla_calidades.referencia=df_concat.REF
tabla_calidades.alternativo=df_concat.ALT

tabla_calidades.GT=df_concat.GT_transformado
tabla_calidades.reads_ref=df_concat.Ref_depth
tabla_calidades.reads_alt=df_concat.Alt_depth
tabla_calidades.DP=df_concat.DP
tabla_calidades["filter"]=df_concat.FILTER.str.replace(",","-")
tabla_calidades.haplotypecaller=df_concat.HaplotypeCaller
tabla_calidades.freebayes=df_concat.FreeBayes
tabla_calidades.samtools=df_concat.SamTools
tabla_calidades.platypus=df_concat.Platypus
tabla_calidades.deepvariant=df_concat.DeepVariant

filename=outputtablas + 'tabla_calidades-' + dt_string + '.csv'

tabla_calidades.to_csv(filename, index=False)


tmp=tabla_calidades.sample()
