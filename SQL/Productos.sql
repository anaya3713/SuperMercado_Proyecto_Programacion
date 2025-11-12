CREATE TABLE public."productos"
(
    id_producto SERIAL PRIMARY KEY,
    nombre_producto VARCHAR(100) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(50) NOT NULL,
    marca VARCHAR(50),
    valor_unitario DECIMAL(10,2) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_actual INTEGER DEFAULT 0,
    codigo_barras VARCHAR(50) UNIQUE
);

ALTER TABLE IF EXISTS public."productos" OWNER to postgres;

-- Insertar más de 100 productos de comida inventados
INSERT INTO public."productos" 
(nombre_producto, descripcion, categoria, marca, valor_unitario, precio_venta, stock_actual, codigo_barras) VALUES
-- Lácteos (1-15)
('Leche Entera 1L', 'Leche entera pasteurizada', 'Lácteos', 'Lactosa', 2500, 3200, 50, '770123456001'),
('Queso Mozzarella 200g', 'Queso fresco mozzarella', 'Lácteos', 'Quesos Don Juan', 4500, 6800, 30, '770123456002'),
('Yogurt Natural 500g', 'Yogurt natural sin azúcar', 'Lácteos', 'Yogurísimo', 2800, 4200, 40, '770123456003'),
('Mantequilla 250g', 'Mantequilla sin sal', 'Lácteos', 'Mantequilla Real', 3500, 5200, 25, '770123456004'),
('Queso Cheddar 300g', 'Queso cheddar madurado', 'Lácteos', 'Quesos Selectos', 6200, 8900, 20, '770123456005'),
('Crema de Leche 200ml', 'Crema para cocinar', 'Lácteos', 'CremaFina', 2200, 3500, 35, '770123456006'),
('Leche Deslactosada 1L', 'Leche sin lactosa', 'Lácteos', 'LactoFree', 3000, 4500, 28, '770123456007'),
('Yogurt de Fresa 150g', 'Yogurt con sabor a fresa', 'Lácteos', 'Fruity', 1800, 2800, 60, '770123456008'),
('Queso Parmesano 150g', 'Queso parmesano rallado', 'Lácteos', 'Italiano', 5500, 7800, 18, '770123456009'),
('Leche Condensada 390g', 'Leche condensada azucarada', 'Lácteos', 'DulceLec', 4200, 6200, 22, '770123456010'),
('Queso Fresco 400g', 'Queso fresco campesino', 'Lácteos', 'Campo Verde', 3800, 5800, 26, '770123456011'),
('Yogurt Griego 200g', 'Yogurt griego natural', 'Lácteos', 'Greco', 3200, 4800, 32, '770123456012'),
('Mantequilla con Sal 200g', 'Mantequilla con sal', 'Lácteos', 'Sal y Mante', 3000, 4500, 24, '770123456013'),
('Leche en Polvo 400g', 'Leche entera en polvo', 'Lácteos', 'PolvoLac', 7500, 10500, 16, '770123456014'),
('Queso Gouda 250g', 'Queso gouda ahumado', 'Lácteos', 'Holandés', 5200, 7500, 19, '770123456015'),

-- Carnes y Embutidos (16-30)
('Pechuga de Pollo 1kg', 'Pechuga de pollo sin hueso', 'Carnes', 'Pollo Rey', 13500, 18500, 15, '770123456016'),
('Carne Molida Res 500g', 'Carne de res molida premium', 'Carnes', 'Carnes Selectas', 10500, 14500, 20, '770123456017'),
('Jamón de Pierna 200g', 'Jamón de pierna ahumado', 'Embutidos', 'Jamones Finos', 5400, 7800, 35, '770123456018'),
('Salchichas 500g', 'Salchichas tipo viena', 'Embutidos', 'SalchiMax', 6000, 8500, 28, '770123456019'),
('Tocino 250g', 'Tocino ahumado en rebanadas', 'Embutidos', 'Tocinero', 7500, 10500, 22, '770123456020'),
('Chorizo Parrillero 400g', 'Chorizo para parrilla', 'Embutidos', 'Choripan', 9000, 12500, 18, '770123456021'),
('Filete de Res 300g', 'Filete de res premium', 'Carnes', 'Carnes Prime', 15000, 21000, 12, '770123456022'),
('Pavo Ahumado 300g', 'Pavo ahumado en rebanadas', 'Embutidos', 'Pavo Real', 8400, 11800, 24, '770123456023'),
('Costillas de Cerdo 1kg', 'Costillas de cerdo para BBQ', 'Carnes', 'Cerdo Fresco', 18000, 24500, 10, '770123456024'),
('Salami 150g', 'Salami italiano', 'Embutidos', 'Italiano', 4500, 6800, 30, '770123456025'),
('Pechuga de Pavo 500g', 'Pechuga de pavo fresca', 'Carnes', 'Pavo Real', 11400, 15800, 14, '770123456026'),
('Mortadela 250g', 'Mortadela con pistachos', 'Embutidos', 'Embutidos Select', 3600, 5200, 32, '770123456027'),
('Chuleta de Cerdo 400g', 'Chuleta de cerdo', 'Carnes', 'Cerdo Fresco', 9600, 13200, 16, '770123456028'),
('Jamón Cocido 180g', 'Jamón cocido extra', 'Embutidos', 'Jamones Finos', 4800, 7200, 38, '770123456029'),
('Carne para Asar 800g', 'Carne de res para asar', 'Carnes', 'Carnes Selectas', 22500, 29800, 8, '770123456030'),

-- Frutas y Verduras (31-45)
('Manzana Roja 1kg', 'Manzanas rojas frescas', 'Frutas', 'Frutas Frescas', 3600, 5200, 40, '770123456031'),
('Banano 1kg', 'Banano maduro', 'Frutas', 'Tropical', 2400, 3800, 55, '770123456032'),
('Naranja 1kg', 'Naranjas jugosas', 'Frutas', 'Cítricos Select', 3000, 4500, 35, '770123456033'),
('Zanahoria 500g', 'Zanahorias frescas', 'Verduras', 'Verduras Campo', 1800, 2800, 45, '770123456034'),
('Tomate 1kg', 'Tomates rojos maduros', 'Verduras', 'Hortalizas Fres', 4500, 6500, 30, '770123456035'),
('Lechuga', 'Lechuga crespa fresca', 'Verduras', 'Verde Fresco', 2100, 3200, 25, '770123456036'),
('Papa 2kg', 'Papas para cocinar', 'Verduras', 'Papa Selecta', 5400, 7800, 28, '770123456037'),
('Cebolla 1kg', 'Cebolla blanca', 'Verduras', 'Cebolla Prime', 3000, 4500, 32, '770123456038'),
('Limón 500g', 'Limones verdes', 'Frutas', 'Cítricos Select', 2700, 4000, 38, '770123456039'),
('Aguacate', 'Aguacates hass', 'Frutas', 'Aguacate Premium', 2400, 3800, 22, '770123456040'),
('Pimiento Rojo 250g', 'Pimientos rojos frescos', 'Verduras', 'Pimientos Finos', 3600, 5200, 20, '770123456041'),
('Uvas 500g', 'Uvas rojas sin semilla', 'Frutas', 'Uvas Select', 6000, 8500, 18, '770123456042'),
('Brócoli', 'Brócoli fresco', 'Verduras', 'Verde Fresco', 3000, 4500, 24, '770123456043'),
('Fresas 250g', 'Fresas frescas', 'Frutas', 'Berry Fresh', 4500, 6500, 16, '770123456044'),
('Espinaca 200g', 'Espinacas frescas', 'Verduras', 'Hoja Verde', 2700, 4000, 30, '770123456045'),

-- Panadería y Pastelería (46-60)
('Pan Blanco 500g', 'Pan blanco fresco', 'Panadería', 'Panadería Don Carlos', 3000, 4500, 20, '770123456046'),
('Croissant', 'Croissant de mantequilla', 'Pastelería', 'Dulce Horno', 1500, 2500, 35, '770123456047'),
('Baguel de Ajonjolí', 'Baguel con ajonjolí', 'Panadería', 'Pan Artesanal', 1800, 2800, 28, '770123456048'),
('Torta de Chocolate', 'Torta de chocolate 500g', 'Pastelería', 'Dulce Tentación', 12000, 16800, 8, '770123456049'),
('Pan Integral 400g', 'Pan integral con semillas', 'Panadería', 'Saludable', 3600, 5200, 18, '770123456050'),
('Donas Glaseadas', 'Donas con glaseado blanco', 'Pastelería', 'Dulce Horno', 1200, 2000, 40, '770123456051'),
('Pan de Ajo', 'Pan de ajo horneado', 'Panadería', 'Sabroso Pan', 4500, 6500, 15, '770123456052'),
('Muffin de Arándanos', 'Muffin con arándanos', 'Pastelería', 'Muffin House', 2400, 3800, 25, '770123456053'),
('Pan de Centeno 350g', 'Pan de centeno alemán', 'Panadería', 'Alemán', 4200, 6200, 12, '770123456054'),
('Tarta de Manzana', 'Tarta de manzana individual', 'Pastelería', 'Tartas Finas', 3600, 5200, 20, '770123456055'),
('Pan de Hamburguesa', 'Pan para hamburguesas', 'Panadería', 'Panadería Don Carlos', 900, 1500, 50, '770123456056'),
('Brownie de Chocolate', 'Brownie con nueces', 'Pastelería', 'Choco Lovers', 2700, 4200, 30, '770123456057'),
('Pan de Molde Blanco', 'Pan de molde blanco', 'Panadería', 'Pan Soft', 3300, 4800, 22, '770123456058'),
('Galletas de Mantequilla', 'Galletas dulces de mantequilla', 'Pastelería', 'Galleta Fina', 600, 1000, 80, '770123456059'),
('Pan de Queso', 'Pan de queso brasileño', 'Panadería', 'Brasileiro', 2100, 3200, 32, '770123456060'),

-- Bebidas (61-75)
('Agua Mineral 500ml', 'Agua mineral sin gas', 'Bebidas', 'Agua Pura', 900, 1500, 60, '770123456061'),
('Jugo de Naranja 1L', 'Jugo de naranja natural', 'Bebidas', 'Frutal', 3600, 5200, 25, '770123456062'),
('Refresco Cola 355ml', 'Refresco de cola', 'Bebidas', 'Cola Fizz', 1500, 2500, 45, '770123456063'),
('Café Molido 500g', 'Café molido tostado', 'Bebidas', 'Café Selecto', 12000, 16800, 18, '770123456064'),
('Té Verde 20 bolsas', 'Té verde en bolsitas', 'Bebidas', 'Té Natural', 4500, 6500, 30, '770123456065'),
('Energética 250ml', 'Bebida energética', 'Bebidas', 'Energix', 2400, 3800, 35, '770123456066'),
('Jugo de Manzana 1L', 'Jugo de manzana natural', 'Bebidas', 'Manzana Fresh', 3300, 4800, 22, '770123456067'),
('Agua con Gas 500ml', 'Agua mineral con gas', 'Bebidas', 'Burbujas', 1200, 2000, 38, '770123456068'),
('Café en Grano 250g', 'Café en grano tostado', 'Bebidas', 'Café Premium', 9000, 12500, 15, '770123456069'),
('Té Negro 25 bolsas', 'Té negro clásico', 'Bebidas', 'Té Clásico', 3600, 5200, 28, '770123456070'),
('Bebida Deportiva 500ml', 'Bebida isotónica', 'Bebidas', 'SportDrink', 2100, 3200, 32, '770123456071'),
('Jugo de Uva 1L', 'Jugo de uva natural', 'Bebidas', 'Uva Select', 4200, 6200, 20, '770123456072'),
('Refresco Limón 355ml', 'Refresco sabor limón', 'Bebidas', 'Lima Fizz', 1350, 2200, 40, '770123456073'),
('Café Instantáneo 200g', 'Café instantáneo', 'Bebidas', 'Café Rápido', 7500, 10500, 24, '770123456074'),
('Infusión de Hierbas', 'Infusión de hierbas naturales', 'Bebidas', 'Hierbas Sanas', 3900, 5800, 26, '770123456075'),

-- Granos y Cereales (76-90)
('Arroz Blanco 1kg', 'Arroz blanco grano largo', 'Granos', 'Arroz Selecto', 3000, 4500, 40, '770123456076'),
('Frijoles Negros 500g', 'Frijoles negros secos', 'Granos', 'Frijol Natural', 3600, 5200, 35, '770123456077'),
('Avena en Hojuelas 500g', 'Avena en hojuelas', 'Cereales', 'Avena Salud', 2700, 4000, 30, '770123456078'),
('Lentejas 500g', 'Lentejas secas', 'Granos', 'Legumbres Finas', 3300, 4800, 28, '770123456079'),
('Harina de Trigo 1kg', 'Harina de trigo todo uso', 'Granos', 'Harina Pura', 2400, 3800, 25, '770123456080'),
('Pasta Spaghetti 500g', 'Pasta spaghetti italiana', 'Granos', 'Pasta Italiana', 2100, 3200, 38, '770123456081'),
('Quinoa 250g', 'Quinoa orgánica', 'Granos', 'Quinoa Natural', 6000, 8500, 20, '770123456082'),
('Garbanzos 500g', 'Garbanzos secos', 'Granos', 'Legumbres Finas', 3900, 5800, 22, '770123456083'),
('Cereal Maíz 500g', 'Cereal de maíz tostado', 'Cereales', 'Cereal Crunch', 4200, 6200, 26, '770123456084'),
('Arroz Integral 1kg', 'Arroz integral orgánico', 'Granos', 'Arroz Natural', 4500, 6500, 18, '770123456085'),
('Pasta Penne 500g', 'Pasta penne rigate', 'Granos', 'Pasta Italiana', 2250, 3500, 32, '770123456086'),
('Maíz Palomero 200g', 'Maíz para palomitas', 'Granos', 'Pop Corn', 1800, 2800, 35, '770123456087'),
('Harina de Maíz 1kg', 'Harina de maíz', 'Granos', 'Maíz Natural', 2700, 4000, 24, '770123456088'),
('Cereal Avena 400g', 'Cereal de avena integral', 'Cereales', 'Avena Crunch', 4800, 7200, 20, '770123456089'),
('Lentejas Rojas 400g', 'Lentejas rojas secas', 'Granos', 'Legumbres Finas', 4200, 6200, 19, '770123456090'),

-- Snacks y Dulces (91-105)
('Papas Fritas 150g', 'Papas fritas clásicas', 'Snacks', 'Chipy', 2400, 3800, 45, '770123456091'),
('Chocolate con Leche 100g', 'Chocolate con leche', 'Dulces', 'ChocoSweet', 3000, 4500, 38, '770123456092'),
('Galletas Saladas 200g', 'Galletas saladas crackers', 'Snacks', 'Cracker Fin', 2700, 4200, 32, '770123456093'),
('Caramelos Surtidos 150g', 'Caramelos surtidos', 'Dulces', 'Dulce Sabor', 1800, 2800, 50, '770123456094'),
('Nachos 200g', 'Nachos de maíz', 'Snacks', 'Nacho Max', 3600, 5200, 28, '770123456095'),
('Chocolate Amargo 80g', 'Chocolate 70% cacao', 'Dulces', 'ChocoDark', 4200, 6200, 25, '770123456096'),
('Mix de Frutos Secos 150g', 'Mix de nueces y frutos secos', 'Snacks', 'Nuts Mix', 6000, 8500, 22, '770123456097'),
('Gomitas de Fruta 100g', 'Gomitas de fruta', 'Dulces', 'Gomi Fruit', 1500, 2500, 40, '770123456098'),
('Palomitas de Maíz 100g', 'Palomitas para microondas', 'Snacks', 'Pop Quick', 2100, 3200, 35, '770123456099'),
('Barra de Cereal 40g', 'Barra de cereal con frutas', 'Snacks', 'Energy Bar', 1200, 2000, 60, '770123456100'),
('Cacahuates Tostados 150g', 'Cacahuates tostados con sal', 'Snacks', 'Nutty', 2700, 4200, 30, '770123456101'),
('Chocolate Blanco 90g', 'Chocolate blanco', 'Dulces', 'White Choco', 3300, 4800, 26, '770123456102'),
('Tortilla Chips 180g', 'Tortilla chips de maíz', 'Snacks', 'Torti Chip', 3900, 5800, 24, '770123456103'),
('Malvaviscos 200g', 'Malvaviscos blancos', 'Dulces', 'Marsh Soft', 2400, 3800, 32, '770123456104'),
('Pretzels 150g', 'Pretzels horneados', 'Snacks', 'Pretzel Crunch', 2850, 4500, 28, '770123456105'),

-- Productos adicionales para completar más de 100
('Aceite de Oliva 500ml', 'Aceite de oliva extra virgen', 'Aceites', 'Oliva Premium', 10500, 14500, 15, '770123456106'),
('Vinagre Balsámico 250ml', 'Vinagre balsámico de Módena', 'Condimentos', 'Balsámico Fino', 7500, 10500, 18, '770123456107'),
('Salsa de Tomate 400g', 'Salsa de tomate natural', 'Salsas', 'Salsa Casera', 3600, 5200, 25, '770123456108'),
('Mostaza 200g', 'Mostaza amarilla', 'Condimentos', 'Mostaza Fina', 2700, 4000, 30, '770123456109'),
('Miel de Abeja 500g', 'Miel pura de abeja', 'Endulzantes', 'Miel Natural', 8400, 11800, 12, '770123456110');

-- Crear índice para mejorar búsquedas por categoría
CREATE INDEX idx_productos_categoria ON public."productos" (categoria);
CREATE INDEX idx_productos_nombre ON public."productos" (nombre_producto);