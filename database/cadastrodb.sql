-- Remover banco de dados se existir
DROP DATABASE IF EXISTS cadastrodb;

-- Criar novo banco de dados com codificação utf8mb4
CREATE DATABASE cadastrodb CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- Usar o banco de dados recém-criado
USE cadastrodb;

-- Criar tabela de proprietários (owner)
CREATE TABLE owner (
    ow_id INT PRIMARY KEY AUTO_INCREMENT,  -- Identificador único para cada proprietário
    ow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Data de registro do proprietário
    ow_birth DATE,  -- Data de nascimento do proprietário
    ow_name VARCHAR(127) NOT NULL,  -- Nome do proprietário
    ow_email VARCHAR(255) NOT NULL,  -- E-mail do proprietário
    ow_password VARCHAR(255) NOT NULL,  -- Senha do proprietário
    ow_status ENUM('on','off','del') DEFAULT 'on'  -- Status do proprietário
);

-- Criar tabela de itens (item)
CREATE TABLE item (
    it_id INT PRIMARY KEY AUTO_INCREMENT,  -- Identificador único para cada item
    it_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Data de registro do item
    it_image VARCHAR(255) NOT NULL,  -- URL da imagem do item
    it_name VARCHAR(127) NOT NULL,  -- Nome do item
    it_description VARCHAR(255) NOT NULL,  -- Descrição do item
    it_location VARCHAR(255) NOT NULL,  -- Localização do item
    it_owner INT NOT NULL,  -- ID do proprietário do item
    it_status ENUM('on','off','del') DEFAULT 'on',  -- Status do item
    FOREIGN KEY (it_owner) REFERENCES owner (ow_id)  -- Chave estrangeira referenciando a tabela owner
);

-- Inserir dados na tabela owner
INSERT INTO owner (ow_birth, ow_name, ow_email, ow_password, ow_status) VALUES
('1985-03-15', 'Alice Silva', 'alice@example.com', SHA1('senha123'), 'on'),  -- Proprietário 1
('1990-07-22', 'Bruno Costa', 'bruno@example.com', SHA1('senha456'), 'on'),  -- Proprietário 2
('1978-11-05', 'Carlos Oliveira', 'carlos@example.com', SHA1('senha789'), 'on'),  -- Proprietário 3
('2000-01-30', 'Diana Mendes', 'diana@example.com', SHA1('senha321'), 'on');  -- Proprietário 4

-- Inserir dados na tabela item
INSERT INTO item (it_image, it_name, it_description, it_location, it_owner, it_status) VALUES
('https://www.madeirado.com.br/cdn/shop/products/WhatsAppImage2020-10-14at14.41.26_1.jpg?v=1651605671', 'Mesa de Jantar', 'Mesa de jantar de madeira', 'Sala de Estar', 1, 'on'),  -- Item 1
('https://abracasa.vteximg.com.br/arquivos/ids/183850/sofa-cama-belize-casal-150cm-um.jpg?v=638171033620470000', 'Sofá', 'Sofá confortável', 'Sala de Estar', 1, 'on'),  -- Item 2
('https://m.media-amazon.com/images/I/61rAmh5BqrS._AC_SL1500_.jpg', 'Cadeira', 'Cadeira de escritório', 'Escritório', 2, 'on'),  -- Item 3
('https://m.media-amazon.com/images/I/41PtnqJC4dL._AC_SL1000_.jpg', 'Estante', 'Estante para livros', 'Quarto', 3, 'on'),  -- Item 4
('https://imgs.casasbahia.com.br/1547780703/1xg.jpg', 'Cama', 'Cama queen size', 'Quarto', 4, 'on');  -- Item 5


