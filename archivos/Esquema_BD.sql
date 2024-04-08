CREATE TABLE `corrida` (
  `id_corrida` varchar(30),
  `id_diseno` tinyint,
  `fecha` date,
  `created_at` timestamp,
  PRIMARY KEY (`id_corrida`, `id_diseno`)
);

CREATE TABLE `diseno` (
  `id_diseno` tinyint PRIMARY KEY AUTO_INCREMENT,
  `laboratorio` varchar(50),
  `empresa` varchar(25) NOT NULL,
  `anio` year NOT NULL,
  `tech_sec` varchar(20) NOT NULL,
  `tipo_sec` varchar(20) NOT NULL,
  `genes` LONGTEXT NOT NULL,
  `created_at` timestamp
);

CREATE TABLE `paciente` (
  `id_genomica` varchar(50) PRIMARY KEY,
  `sexo` varchar(1),
  `dx_presuntivo` varchar(255),
  `historia_clinica` varchar(25),
  `created_at` timestamp
);

CREATE TABLE `variantes` (
  `ref_build` varchar(10),
  `cromosoma` varchar(15),
  `posicion` int,
  `referencia` varchar(255),
  `alternativo` varchar(255),
  `tipo` varchar(50),
  `gen` varchar(20),
  `id_clinvar` varchar(50) NOT NULL,
  `created_at` timestamp,
  PRIMARY KEY (`ref_build`, `cromosoma`, `posicion`, `referencia`, `alternativo`)
);

CREATE TABLE `calidades` (
  `id_genomica` varchar(50),
  `id_corrida` varchar(30),
  `id_diseno` tinyint,
  `ref_build` varchar(10),
  `cromosoma` varchar(15),
  `posicion` int,
  `referencia` varchar(255),
  `alternativo` varchar(255),
  `GT` varchar(3) NOT NULL,
  `reads_ref` smallint NOT NULL,
  `reads_alt` smallint NOT NULL,
  `DP` int NOT NULL,
  `filter` varchar(255) NOT NULL,
  `haplotypecaller` tinyint(1),
  `freebayes` tinyint(1),
  `samtools` tinyint(1),
  `platypus` tinyint(1),
  `deepvariant` tinyint(1),
  `created_at` timestamp,
  PRIMARY KEY (`id_genomica`, `id_corrida`, `id_diseno`, `ref_build`, `cromosoma`, `posicion`, `referencia`, `alternativo`)
);

CREATE TABLE `clinvar` (
  `id_clinvar` varchar(50) PRIMARY KEY,
  `CLNSIG` varchar(255) NOT NULL,
  `CLNHGVS` varchar(255) NOT NULL,
  `clinvar_date` DATE,
  `last_update` timestamp
);

CREATE TABLE `reporte_clinvar` (
  `id_submission` varchar(100) PRIMARY KEY,
  `id_clinvar` varchar(50) NOT NULL,
  `created_at` timestamp
);

ALTER TABLE `calidades` ADD FOREIGN KEY (`id_genomica`) REFERENCES `paciente` (`id_genomica`);

ALTER TABLE `calidades` ADD FOREIGN KEY (`ref_build`, `cromosoma`, `posicion`, `referencia`, `alternativo`) REFERENCES `variantes` (`ref_build`, `cromosoma`, `posicion`, `referencia`, `alternativo`);

ALTER TABLE `calidades` ADD FOREIGN KEY (`id_corrida`, `id_diseno`) REFERENCES `corrida` (`id_corrida`, `id_diseno`);

ALTER TABLE `variantes` ADD FOREIGN KEY (`id_clinvar`) REFERENCES `clinvar` (`id_clinvar`);

ALTER TABLE `reporte_clinvar` ADD FOREIGN KEY (`id_clinvar`) REFERENCES `clinvar` (`id_clinvar`);

ALTER TABLE `corrida` ADD FOREIGN KEY (`id_diseno`) REFERENCES `diseno` (`id_diseno`);
