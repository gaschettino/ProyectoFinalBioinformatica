# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 18:11:55 2024

@author: giovi
"""

import argparse
from datetime import datetime
import pandas as pd
import os
import mygene
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Script que genera los datos para importar en la base de datos la información del diseño elegido.', 
        usage='use "%(prog)s --help or -h" for more information', 
        formatter_class=argparse.RawTextHelpFormatter, 
        epilog=('\t \t ######################################################################### \n \n'))
parser.add_argument('-i', dest='inputfile', required=True, type=str, help='Requerido: Path del archivo tsv a utilizar. \n Debe tener las columnas: path al archivo bed, empresa, año de ingreso, tipo de secuenciación(opcional), tecnología de secuenciación(opcional).')
parser.add_argument('-o', dest='outpath', required=False, type=str, help='Opcional: Path de la carpeta donde se quiere guardar el archivo de salida. Si no se declara, será en la misma carpeta que el inputfile.\n')
args = parser.parse_args()

def generar_tabla_diseno (bed_file):
    print(bed_file)
    tmp=pd.read_table(bed_file, index_col=False, header=None, usecols=[3])
    tmp.dropna(subset=[3], inplace=True)
    genes=tmp[3].drop_duplicates(keep='first').to_list()  
    newlist = [x for x in genes if not x.startswith('chr')]
    newlist = [x for x in newlist if not x.isdigit()]
    newlist = [word for line in newlist for word in line.split(',')]    
    newlist.sort()
    lista=[]
    genes_ens = []
    otros_genes = []
    for gene_id in newlist:
        if gene_id.startswith('ENS'):
            genes_ens.append(gene_id)
        else:
            otros_genes.append(gene_id)  
    mg = mygene.MyGeneInfo()
    df=mg.getgenes(genes_ens, as_dataframe=True)
    if 'symbol' in df.columns:
        lista=df[~ df.symbol.isna()].symbol.to_list()
    lista= lista + otros_genes
    resultados = [elemento.replace("-", "_") for elemento in lista]
    print(f'termino {bed_file}')
    return '-'.join(set(resultados))



date_file=datetime.now().strftime("%Y%m%d_%H%M")

if not os.path.isfile(args.inputfile):
    print(f'##ERROR: No existe el archivo {args.inputfile}')
    exit()
if args.outpath and os.path.exists(args.outpath):
    filename=f"{args.outpath}/Tabla_Diseno-{date_file}.csv"
elif args.outpath:
    print (f"##ERROR: {args.outpath} no existe.")
    exit()
else:
    filename=f"{os.path.dirname(args.inputfile)}/Tabla_Diseno-{date_file}.csv"




tabla_diseno=pd.DataFrame(columns=['laboratorio', 'empresa', 'anio', 'tech_sec', 'tipo_sec', 'genes', 'created_at'])  

'''
Abro el archivo inicial para leer cada linea 
'''
archivos = pd.read_csv(args.inputfile, sep='\t')


'''
Leyendo linea por linea completo el dataframe output.
'''
    
for index, row in archivos.iterrows():
    genes = generar_tabla_diseno(row['path'])
    laboratorio = row['laboratorio']
    empresa = row['empresa']
    anio = row['año']
    tec = row['tecnologia']
    tipo = row['tipo']
    tabla_diseno.loc[len(tabla_diseno)] = [laboratorio, empresa, anio, tec, tipo, genes, '']

tabla_diseno.to_csv(filename, index=False)

