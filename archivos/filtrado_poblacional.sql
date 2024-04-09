## cambiar: ${database} ${empresa} ${anio} ${laboratorio}
USE '${database}';

SELECT V.ref_build, V.cromosoma, V.posicion, V.referencia, V.alternativo, V.tipo, V.gen, CL.id_clinvar, CL.CLNHGVS, 
  COUNT(DISTINCT Q.id_genomica) AS cantidad_pacientes, 
    CAST(ROUND(COUNT(DISTINCT Q.id_genomica) * 100 / ( SELECT COUNT(DISTINCT P.id_genomica) 
    FROM paciente AS P 
        INNER JOIN calidades AS Q ON P.id_genomica = Q.id_genomica 
        INNER JOIN corrida AS C ON Q.id_corrida = C.id_corrida 
        INNER JOIN diseno AS PA ON C.id_panel = PA.id_panel AND PA.empresa = '${empresa}' AND PA.anio = '${anio}' AND PA.laboratorio = '${laboratorio}' 
        WHERE PA.empresa = '${empresa}' AND PA.anio = '${anio}' AND PA.laboratorio = '${laboratorio}' ), 2) AS SIGNED) AS frecuencia 
FROM variantes AS V 
INNER JOIN calidades AS Q ON V.ref_build = Q.ref_build AND V.cromosoma = Q.cromosoma AND V.posicion = Q.posicion AND V.referencia = Q.referencia AND V.alternativo = Q.alternativo 
INNER JOIN clinvar AS CL ON CL.id_clinvar = V.id_clinvar 
INNER JOIN corrida AS C ON Q.id_corrida = C.id_corrida 
INNER JOIN diseno AS PA ON C.id_panel = PA.id_panel 
WHERE Q.DP >= 50 AND Q.reads_alt >= 25 AND Q.filter = 'PASS' AND PA.empresa = '${empresa}' AND PA.anio = '${anio}' AND PA.laboratorio = '${laboratorio}' 
GROUP BY V.ref_build, V.cromosoma, V.posicion, V.referencia, V.alternativo 
HAVING frecuencia >= 20 
ORDER BY cantidad_pacientes DESC;