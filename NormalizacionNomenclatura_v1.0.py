# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 17:51:21 2023

@author: Giovanna
"""

import argparse
from datetime import datetime
import os
import pandas as pd
import re
import requests
from tqdm import tqdm


parser = argparse.ArgumentParser(description='Script para corregir la nomenclatura de las variantes a la versión HGVS más actualizada utilizando la API de mutalyzer.',  formatter_class=argparse.RawTextHelpFormatter, epilog = ' ')

parser.add_argument('-i', dest='inputfile', required=True, help='Requerido: Path del archivo exportado desde la base de datos con las variantes que cumplen con el criterio de selección.')
parser.add_argument('-outpath', dest='outpath', required=False, help='Opcional: Path de la carpeta output. Si no se indica será el mismo lugar donde está el archivo input')

args = parser.parse_args()


def corregir_clnhgvs(clnhgvs):
    return re.sub(r'(\d+)([A-Z]+)(\d+)', r'\1\2[\3]', clnhgvs)

def clinvar_NC(valor):
    valor=valor.split('(')[1].replace(')', '')
    return valor

def busqueda_API(variante):
        response = requests.get("https://mutalyzer.nl/api/normalize/{}?only_variants=false".format(variante), headers={"accept": "application/json"})
        value=''
        if 'normalized_description' in response.json():
            value = response.json()['normalized_description']
        elif 'equivalent_descriptions' in response.json():
            response_c = response.json()["equivalent_descriptions"]["c"]
            mane_select_description = next((desc for desc in response_c if desc.get('tag', {}).get('details') == 'MANE Select'), None)
            if mane_select_description:
                value = clinvar_NC(mane_select_description['description'])
            else:
                value = clinvar_NC(response_c[0])
        return value


date_file=datetime.now().strftime("%Y%m%d_%H%M")

if not os.path.isfile(args.inputfile):
    print(f'##ERROR: No existe el archivo {args.inputfile}')
    exit()
else:
    panel=args.inputfile.split('resultado_')[1].split('.')[0]

if args.outpath and os.path.exists(args.outpath):
    filename=f"{args.outpath}/Resultado_{panel}_{date_file}.csv"
    
elif args.outpath:
    print (f"##ERROR: {args.outpath} no existe.")
    exit()
else:
    filename=f"{os.path.dirname(args.inputfile)}/Resultado_{panel}_{date_file}.csv"

variants = pd.read_csv(args.inputfile, sep='\t')
variants["variante"] = 'GRCh38(chr' + variants['cromosoma'].astype(str) + '):g.' + variants['posicion_start'].astype(str) + variants['referencia'] + '>' + variants['alternativo']
variants["HGVS"]=''  
variants['CLNHGVS'] = variants['CLNHGVS'].apply(corregir_clnhgvs)

for i in tqdm(range(len(variants))):
    HGVS_desc=busqueda_API(variants.iloc[i].variante)
    if len(HGVS_desc) > 0:
        variants.at[i, "HGVS"] = HGVS_desc
    elif variants.iloc[i].CLNHGVS != 'Dummy':
        res=busqueda_API(variants.iloc[i].CLNHGVS)
        if res:
            variants.at[i, "HGVS"]=res


variants.to_csv(filename, index=False)

print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - Script finalizado.')
