-- Tabla de Ventas
CREATE TABLE public."ventas"
(
    id_venta SERIAL PRIMARY KEY,
    fecha_venta DATE NOT NULL,
    hora_venta TIME NOT NULL,
    total_venta DECIMAL(10,2) NOT NULL,
    metodo_pago VARCHAR(20) NOT NULL,
    nombre_cliente VARCHAR(100) NOT NULL,
    cedula_cliente VARCHAR(20) NOT NULL
);

ALTER TABLE IF EXISTS public."ventas" OWNER to postgres;

-- Tabla de Detalle de Ventas (para los productos de cada venta)
CREATE TABLE public."detalle_ventas"
(
    id_detalle SERIAL PRIMARY KEY,
    id_venta INTEGER NOT NULL REFERENCES public."ventas"(id_venta),
    id_producto INTEGER NOT NULL REFERENCES public."productos"(id_producto),
    codigo_barras VARCHAR(50) NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

ALTER TABLE IF EXISTS public."detalle_ventas" OWNER to postgres;

-- Insertar ventas inventadas con datos de clientes
INSERT INTO public."ventas" (fecha_venta, hora_venta, total_venta, metodo_pago, nombre_cliente, cedula_cliente) VALUES
-- Enero 2025
('2025-01-05', '09:15:00', 45800, 'EFECTIVO', 'María González', '1234567890'),
('2025-01-08', '14:30:00', 32500, 'TARJETA', 'Carlos Rodríguez', '2345678901'),
('2025-01-12', '11:45:00', 28700, 'EFECTIVO', 'Ana Martínez', '3456789012'),
('2025-01-15', '16:20:00', 54200, 'TARJETA', 'José López', '4567890123'),
('2025-01-18', '10:10:00', 18900, 'EFECTIVO', 'Laura García', '5678901234'),
('2025-01-22', '15:45:00', 42300, 'TARJETA', 'Miguel Hernández', '6789012345'),
('2025-01-25', '12:30:00', 31500, 'EFECTIVO', 'Isabel Díaz', '7890123456'),
('2025-01-28', '17:15:00', 47800, 'TARJETA', 'Roberto Silva', '8901234567'),

-- Febrero 2025
('2025-02-02', '08:45:00', 39200, 'EFECTIVO', 'Carmen Vargas', '9012345678'),
('2025-02-05', '13:20:00', 26700, 'TARJETA', 'Fernando Castro', '1122334455'),
('2025-02-09', '10:35:00', 53400, 'EFECTIVO', 'Patricia Rojas', '2233445566'),
('2025-02-12', '15:50:00', 29800, 'TARJETA', 'Jorge Méndez', '3344556677'),
('2025-02-15', '11:25:00', 42100, 'EFECTIVO', 'Sandra Morales', '4455667788'),
('2025-02-18', '16:40:00', 35600, 'TARJETA', 'Ricardo Ortega', '5566778899'),
('2025-02-22', '09:55:00', 48900, 'EFECTIVO', 'Elena Castillo', '6677889900'),
('2025-02-25', '14:15:00', 31200, 'TARJETA', 'Daniel Pérez', '7788990011'),

-- Marzo 2025
('2025-03-03', '10:20:00', 44500, 'EFECTIVO', 'Gabriela Reyes', '8899001122'),
('2025-03-06', '15:35:00', 27800, 'TARJETA', 'Luis Ramírez', '9900112233'),
('2025-03-10', '12:45:00', 51200, 'EFECTIVO', 'Adriana Cruz', '1011121314'),
('2025-03-13', '17:10:00', 33400, 'TARJETA', 'Andrés Herrera', '1213141516'),
('2025-03-16', '09:30:00', 46700, 'EFECTIVO', 'Teresa Mendoza', '1314151617'),
('2025-03-19', '14:25:00', 28900, 'TARJETA', 'Raúl Guzmán', '1415161718'),
('2025-03-23', '11:40:00', 52300, 'EFECTIVO', 'Verónica Soto', '1516171819'),
('2025-03-26', '16:55:00', 37600, 'TARJETA', 'Oscar Núñez', '1617181920'),
('2025-03-29', '13:15:00', 49800, 'EFECTIVO', 'Claudia Vega', '1718192021'),

-- Abril 2025
('2025-04-02', '08:50:00', 41200, 'EFECTIVO', 'Mario Flores', '1819202122'),
('2025-04-05', '14:05:00', 29500, 'TARJETA', 'Lucía Campos', '1920212223'),
('2025-04-08', '11:20:00', 56700, 'EFECTIVO', 'Héctor Ríos', '2021222324'),
('2025-04-11', '16:35:00', 32300, 'TARJETA', 'Natalia Peña', '2122232425'),
('2025-04-14', '10:45:00', 47800, 'EFECTIVO', 'Francisco Mora', '2223242526'),
('2025-04-17', '15:20:00', 38900, 'TARJETA', 'Rosa Salazar', '2324252627'),
('2025-04-20', '12:30:00', 53400, 'EFECTIVO', 'Alberto Medina', '2425262728'),
('2025-04-23', '17:45:00', 26700, 'TARJETA', 'Silvia Romero', '2526272829'),
('2025-04-26', '09:55:00', 49100, 'EFECTIVO', 'Guillermo Torres', '2627282930'),
('2025-04-29', '14:10:00', 34500, 'TARJETA', 'Beatriz Navarro', '2728293031'),

-- Mayo 2025
('2025-05-03', '11:25:00', 52300, 'EFECTIVO', 'Santiago Jiménez', '2829303132'),
('2025-05-06', '16:40:00', 37800, 'TARJETA', 'Valeria Acosta', '2930313233'),
('2025-05-09', '13:15:00', 45600, 'EFECTIVO', 'Felipe Paredes', '3031323334'),
('2025-05-12', '08:30:00', 31200, 'TARJETA', 'Diana Cordero', '3132333435'),
('2025-05-15', '15:45:00', 58900, 'EFECTIVO', 'Gustavo León', '3233343536'),
('2025-05-18', '10:20:00', 42300, 'TARJETA', 'Paola Miranda', '3334353637'),
('2025-05-21', '17:35:00', 33400, 'EFECTIVO', 'René Espinoza', '3435363738'),
('2025-05-24', '12:50:00', 47800, 'TARJETA', 'Lorena Valdez', '3536373839'),
('2025-05-27', '09:05:00', 51200, 'EFECTIVO', 'Mauricio Ponce', '3637383940'),
('2025-05-30', '14:25:00', 36700, 'TARJETA', 'Alicia Rangel', '3738394041'),

-- Junio 2025
('2025-06-02', '11:40:00', 44500, 'EFECTIVO', 'Rodrigo Mejía', '3839404142'),
('2025-06-05', '16:55:00', 29800, 'TARJETA', 'Camila Bustos', '3940414243'),
('2025-06-08', '13:10:00', 52300, 'EFECTIVO', 'Esteban Lozano', '4041424344'),
('2025-06-11', '08:25:00', 41200, 'TARJETA', 'Jimena Orozco', '4142434445'),
('2025-06-14', '15:30:00', 35600, 'EFECTIVO', 'Hugo Franco', '4243444546'),
('2025-06-17', '10:45:00', 48900, 'TARJETA', 'Mariana Solís', '4344454647'),
('2025-06-20', '17:50:00', 26700, 'EFECTIVO', 'Alejandro Roa', '4445464748'),
('2025-06-23', '12:15:00', 53400, 'TARJETA', 'Daniela Montes', '4546474849'),
('2025-06-26', '09:20:00', 37800, 'EFECTIVO', 'Arturo Cervantes', '4647484950'),
('2025-06-29', '14:35:00', 45600, 'TARJETA', 'Vanessa Gallegos', '4748495051'),

-- Julio 2025
('2025-07-03', '11:50:00', 51200, 'EFECTIVO', 'César Velásquez', '4849505152'),
('2025-07-06', '16:05:00', 34500, 'TARJETA', 'Ximena Tapia', '4950515253'),
('2025-07-09', '13:20:00', 47800, 'EFECTIVO', 'Roberto Zúñiga', '5051525354'),
('2025-07-12', '08:35:00', 31200, 'TARJETA', 'Andrea Sepúlveda', '5152535455'),
('2025-07-15', '15:40:00', 58900, 'EFECTIVO', 'Gerardo Cárdenas', '5253545556'),
('2025-07-18', '10:55:00', 42300, 'TARJETA', 'Carolina Andrade', '5354555657'),
('2025-07-21', '17:10:00', 33400, 'EFECTIVO', 'Marcelo Salgado', '5455565758'),
('2025-07-24', '12:25:00', 52300, 'TARJETA', 'Paulina Rivas', '5556575859'),
('2025-07-27', '09:40:00', 45600, 'EFECTIVO', 'Federico Molina', '5657585960'),
('2025-07-30', '14:50:00', 37800, 'TARJETA', 'Rebeca Olivares', '5758596061'),

-- Agosto 2025
('2025-08-02', '11:15:00', 49800, 'EFECTIVO', 'Sergio Contreras', '5859606162'),
('2025-08-05', '16:30:00', 28900, 'TARJETA', 'Eugenia Fuentes', '5960616263'),
('2025-08-08', '13:45:00', 56700, 'EFECTIVO', 'Tomás Vergara', '6061626364'),
('2025-08-11', '08:55:00', 32300, 'TARJETA', 'Constanza Lagos', '6162636465'),
('2025-08-14', '15:20:00', 44500, 'EFECTIVO', 'Nicolás Bravo', '6263646566'),
('2025-08-17', '10:35:00', 37800, 'TARJETA', 'Antonia Vidal', '6364656667'),
('2025-08-20', '17:40:00', 51200, 'EFECTIVO', 'Fabián Sanhueza', '6465666768'),
('2025-08-23', '12:50:00', 26700, 'TARJETA', 'Pamela Correa', '6566676869'),
('2025-08-26', '09:05:00', 53400, 'EFECTIVO', 'Leonardo Pizarro', '6667686970'),
('2025-08-29', '14:15:00', 35600, 'TARJETA', 'Florencia Valenzuela', '6768697071'),

-- Septiembre 2025
('2025-09-02', '11:30:00', 48900, 'EFECTIVO', 'Matías Garrido', '6869707172'),
('2025-09-05', '16:45:00', 31200, 'TARJETA', 'Javiera Saavedra', '6970717273'),
('2025-09-08', '13:55:00', 52300, 'EFECTIVO', 'Boris Parra', '7071727374'),
('2025-09-11', '08:10:00', 41200, 'TARJETA', 'Trinidad Alarcón', '7172737475'),
('2025-09-14', '15:25:00', 35600, 'EFECTIVO', 'Yerko Barrera', '7273747576'),
('2025-09-17', '10:40:00', 47800, 'TARJETA', 'Amanda Escobar', '7374757677'),
('2025-09-20', '17:50:00', 28900, 'EFECTIVO', 'Cristóbal Duarte', '7475767778'),
('2025-09-23', '12:05:00', 53400, 'TARJETA', 'Francisca Carrasco', '7576777879'),
('2025-09-26', '09:20:00', 42300, 'EFECTIVO', 'Ignacio Troncoso', '7677787980'),
('2025-09-29', '14:35:00', 36700, 'TARJETA', 'Macarena Aguirre', '7778798081'),

-- Octubre 2025
('2025-10-03', '11:50:00', 51200, 'EFECTIVO', 'Benjamín Moya', '7879808182'),
('2025-10-06', '16:05:00', 33400, 'TARJETA', 'Antonella Leiva', '7980818283'),
('2025-10-09', '13:20:00', 58900, 'EFECTIVO', 'Vicente Godoy', '8081828384'),
('2025-10-12', '08:35:00', 29800, 'TARJETA', 'Emilia Bustamante', '8182838485'),
('2025-10-15', '15:40:00', 44500, 'EFECTIVO', 'Maximiliano Cáceres', '8283848586'),
('2025-10-18', '10:55:00', 37800, 'TARJETA', 'Sofía Venegas', '8384858687'),
('2025-10-21', '17:10:00', 52300, 'EFECTIVO', 'Kevin Aravena', '8485868788'),
('2025-10-24', '12:25:00', 26700, 'TARJETA', 'Martina Pacheco', '8586878889'),
('2025-10-27', '09:40:00', 55600, 'EFECTIVO', 'Bastián Soto', '8687888990'),
('2025-10-30', '14:50:00', 38900, 'TARJETA', 'Julieta Orellana', '8788899091'),

-- Noviembre 2025 (hasta el 20)
('2025-11-02', '11:15:00', 47800, 'EFECTIVO', 'Alonso Segura', '8889909192'),
('2025-11-05', '16:30:00', 31200, 'TARJETA', 'Isidora Palma', '8990919293'),
('2025-11-08', '13:45:00', 53400, 'EFECTIVO', 'Simón Farías', '9091929394'),
('2025-11-11', '08:55:00', 35600, 'TARJETA', 'Renata Gutiérrez', '9192939495'),
('2025-11-14', '15:20:00', 48900, 'EFECTIVO', 'Emilio Sandoval', '9293949596'),
('2025-11-17', '10:35:00', 26700, 'TARJETA', 'Maite Figueroa', '9394959697'),
('2025-11-20', '17:40:00', 51200, 'EFECTIVO', 'Joaquín Ruiz', '9495969798');

-- Insertar detalles de ventas con códigos de barras (los mismos detalles que antes)
INSERT INTO public."detalle_ventas" (id_venta, id_producto, codigo_barras, cantidad, precio_unitario, subtotal) VALUES
-- Ventas con múltiples productos y códigos de barras
(1, 16, '770123456016', 2, 18500, 37000), (1, 31, '770123456031', 1, 5200, 5200), (1, 46, '770123456046', 1, 4500, 4500),
(2, 5, '770123456005', 1, 8900, 8900), (2, 17, '770123456017', 1, 14500, 14500), (2, 61, '770123456061', 3, 1500, 4500),
(3, 2, '770123456002', 2, 6800, 13600), (3, 32, '770123456032', 1, 3800, 3800), (3, 76, '770123456076', 1, 4500, 4500),
(4, 22, '770123456022', 1, 21000, 21000), (4, 1, '770123456001', 3, 3200, 9600), (4, 62, '770123456062', 2, 5200, 10400),
(5, 91, '770123456091', 5, 3800, 19000), (5, 92, '770123456092', 1, 4500, 4500),
(6, 8, '770123456008', 4, 2800, 11200), (6, 35, '770123456035', 2, 6500, 13000), (6, 81, '770123456081', 3, 3200, 9600),
(7, 12, '770123456012', 2, 4800, 9600), (7, 25, '770123456025', 1, 6800, 6800), (7, 44, '770123456044', 1, 6500, 6500),
(8, 64, '770123456064', 1, 16800, 16800), (8, 69, '770123456069', 1, 12500, 12500), (8, 106, '770123456106', 1, 14500, 14500),

-- Continuar con más detalles de ventas... (los mismos que antes)
(9, 3, '770123456003', 3, 4200, 12600), (9, 18, '770123456018', 2, 7800, 15600), (9, 47, '770123456047', 4, 2500, 10000),
(10, 7, '770123456007', 2, 4500, 9000), (10, 33, '770123456033', 1, 4500, 4500), (10, 77, '770123456077', 1, 5200, 5200),
(11, 20, '770123456020', 3, 10500, 31500), (11, 36, '770123456036', 2, 3200, 6400), (11, 63, '770123456063', 4, 2500, 10000),
(12, 9, '770123456009', 1, 7800, 7800), (12, 28, '770123456028', 1, 13200, 13200), (12, 93, '770123456093', 2, 4200, 8400),
(13, 13, '770123456013', 3, 4500, 13500), (13, 37, '770123456037', 1, 7800, 7800), (13, 82, '770123456082', 1, 8500, 8500),
(14, 6, '770123456006', 2, 3500, 7000), (14, 23, '770123456023', 1, 11800, 11800), (14, 78, '770123456078', 2, 4000, 8000),
(15, 19, '770123456019', 4, 8500, 34000), (15, 34, '770123456034', 1, 2800, 2800), (15, 94, '770123456094', 3, 2800, 8400),
(16, 10, '770123456010', 2, 6200, 12400), (16, 29, '770123456029', 1, 7200, 7200), (16, 83, '770123456083', 1, 5800, 5800),

-- Continuar con el resto de detalles... (igual que antes)
(17, 4, '770123456004', 2, 5200, 10400), (17, 24, '770123456024', 1, 24500, 24500), (17, 95, '770123456095', 2, 5200, 10400),
(18, 11, '770123456011', 1, 5800, 5800), (18, 30, '770123456030', 1, 29800, 29800),
(19, 14, '770123456014', 1, 10500, 10500), (19, 38, '770123456038', 2, 4500, 9000), (19, 96, '770123456096', 1, 6200, 6200),
(20, 15, '770123456015', 2, 7500, 15000), (20, 39, '770123456039', 3, 4000, 12000), (20, 97, '770123456097', 1, 8500, 8500);

-- Crear índices para mejorar el rendimiento
CREATE INDEX idx_ventas_fecha ON public."ventas" (fecha_venta);
CREATE INDEX idx_ventas_cliente ON public."ventas" (cedula_cliente);
CREATE INDEX idx_detalle_venta ON public."detalle_ventas" (id_venta);
CREATE INDEX idx_detalle_producto ON public."detalle_ventas" (id_producto);
CREATE INDEX idx_detalle_codigo_barras ON public."detalle_ventas" (codigo_barras);