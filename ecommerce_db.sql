CREATE DATABASE  IF NOT EXISTS `ecommerce_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `ecommerce_db`;
-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: ecommerce_db
-- ------------------------------------------------------
-- Server version	8.0.34

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `id` int NOT NULL,
  `email` varchar(45) NOT NULL,
  `pass` varchar(500) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `base_shipping_rates`
--

DROP TABLE IF EXISTS `base_shipping_rates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `base_shipping_rates` (
  `shipping_rate_id` int NOT NULL AUTO_INCREMENT,
  `city_id` int NOT NULL,
  `products_id` varchar(45) NOT NULL,
  `base_charge` decimal(12,2) NOT NULL,
  PRIMARY KEY (`shipping_rate_id`),
  KEY `city_id_idx` (`city_id`),
  KEY `product_id_idx` (`products_id`) /*!80000 INVISIBLE */,
  CONSTRAINT `city_id_fk_bsr` FOREIGN KEY (`city_id`) REFERENCES `cities` (`city_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `products_id_fk_bsr` FOREIGN KEY (`products_id`) REFERENCES `products` (`products_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `base_shipping_rates`
--

LOCK TABLES `base_shipping_rates` WRITE;
/*!40000 ALTER TABLE `base_shipping_rates` DISABLE KEYS */;
/*!40000 ALTER TABLE `base_shipping_rates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `brand_seq`
--

DROP TABLE IF EXISTS `brand_seq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `brand_seq` (
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brand_seq`
--

LOCK TABLES `brand_seq` WRITE;
/*!40000 ALTER TABLE `brand_seq` DISABLE KEYS */;
/*!40000 ALTER TABLE `brand_seq` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `brands`
--

DROP TABLE IF EXISTS `brands`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `brands` (
  `brands_id` varchar(45) NOT NULL,
  `value` varchar(45) NOT NULL,
  PRIMARY KEY (`brands_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brands`
--

LOCK TABLES `brands` WRITE;
/*!40000 ALTER TABLE `brands` DISABLE KEYS */;
/*!40000 ALTER TABLE `brands` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `brands_id_trigger` BEFORE INSERT ON `brands` FOR EACH ROW BEGIN
  INSERT INTO brand_seq VALUES (NULL);
  SET NEW.brands_id = CONCAT('BR', LPAD(LAST_INSERT_ID(), 3, '0'));
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `categories_id` varchar(45) NOT NULL,
  `value` varchar(45) NOT NULL,
  PRIMARY KEY (`categories_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `categories_id_trigger` BEFORE INSERT ON `categories` FOR EACH ROW BEGIN
  INSERT INTO category_seq VALUES (NULL);
  SET NEW.categories_id = CONCAT('CA', LPAD(LAST_INSERT_ID(), 3, '0'));
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `category_seq`
--

DROP TABLE IF EXISTS `category_seq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category_seq` (
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category_seq`
--

LOCK TABLES `category_seq` WRITE;
/*!40000 ALTER TABLE `category_seq` DISABLE KEYS */;
/*!40000 ALTER TABLE `category_seq` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cities`
--

DROP TABLE IF EXISTS `cities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cities` (
  `city_id` int NOT NULL AUTO_INCREMENT,
  `city` char(45) NOT NULL,
  `ram_address_1` varchar(45) NOT NULL,
  `ram_address_2` varchar(45) NOT NULL,
  `region` char(45) NOT NULL,
  `postal_code` varchar(45) NOT NULL,
  PRIMARY KEY (`city_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cities`
--

LOCK TABLES `cities` WRITE;
/*!40000 ALTER TABLE `cities` DISABLE KEYS */;
/*!40000 ALTER TABLE `cities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoice_items`
--

DROP TABLE IF EXISTS `invoice_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice_items` (
  `invoice_item_id` int NOT NULL AUTO_INCREMENT,
  `invoice_id` varchar(45) NOT NULL,
  `order_item_id` int NOT NULL,
  PRIMARY KEY (`invoice_item_id`),
  KEY `invoice_id_idx` (`invoice_id`),
  KEY `order_item_id_idx` (`order_item_id`),
  CONSTRAINT `invoice_id_fk_ii` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`invoice_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `order_item_id_fk_ii` FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`order_item_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice_items`
--

LOCK TABLES `invoice_items` WRITE;
/*!40000 ALTER TABLE `invoice_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoice_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoice_seq`
--

DROP TABLE IF EXISTS `invoice_seq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice_seq` (
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice_seq`
--

LOCK TABLES `invoice_seq` WRITE;
/*!40000 ALTER TABLE `invoice_seq` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoice_seq` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoices`
--

DROP TABLE IF EXISTS `invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoices` (
  `invoice_id` varchar(45) NOT NULL,
  `user_id` int NOT NULL,
  `order_id` varchar(45) NOT NULL,
  `download_link` varchar(500) DEFAULT NULL,
  `is_synced` tinyint NOT NULL,
  `sage_id` int DEFAULT NULL,
  `sage_doc_no` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`invoice_id`),
  UNIQUE KEY `invoice_id_UNIQUE` (`invoice_id`),
  UNIQUE KEY `sage_id_UNIQUE` (`sage_id`),
  UNIQUE KEY `sage_doc_no_UNIQUE` (`sage_doc_no`),
  KEY `order_id_idx` (`order_id`),
  KEY `user_id_idx` (`user_id`),
  CONSTRAINT `order_id_fk_i` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `user_id_fk_i` FOREIGN KEY (`user_id`) REFERENCES `user_login` (`user_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoices`
--

LOCK TABLES `invoices` WRITE;
/*!40000 ALTER TABLE `invoices` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoices` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `invoice_id_trigger` BEFORE INSERT ON `invoices` FOR EACH ROW BEGIN
  INSERT INTO invoice_seq VALUES (NULL);
  SET NEW.invoice_id = CONCAT('INV', LPAD(LAST_INSERT_ID(), 3, '0'));
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `order_communication_history`
--

DROP TABLE IF EXISTS `order_communication_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_communication_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `order_id` varchar(45) NOT NULL,
  `comm_method` char(45) NOT NULL,
  `comm_type` char(45) NOT NULL,
  `comm_recipient` varchar(45) NOT NULL,
  `comm_date` datetime NOT NULL,
  `comm_subject` mediumtext NOT NULL,
  `comm_comment` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `order_id_fk_och_idx` (`order_id`),
  KEY `user_id_fk_och_idx` (`user_id`),
  CONSTRAINT `order_id_fk_och` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `user_id_fk_och` FOREIGN KEY (`user_id`) REFERENCES `user_login` (`user_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_communication_history`
--

LOCK TABLES `order_communication_history` WRITE;
/*!40000 ALTER TABLE `order_communication_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_communication_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_history`
--

DROP TABLE IF EXISTS `order_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` varchar(45) NOT NULL,
  `status_id` int NOT NULL,
  `status_date` datetime NOT NULL,
  `status_comment` mediumtext,
  PRIMARY KEY (`id`),
  KEY `order_id_fk_oh_idx` (`order_id`),
  KEY `status_id_fk_oh_idx` (`status_id`),
  CONSTRAINT `order_id_fk_oh` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `status_id_fk_oh` FOREIGN KEY (`status_id`) REFERENCES `statuses` (`id_status`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_history`
--

LOCK TABLES `order_history` WRITE;
/*!40000 ALTER TABLE `order_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `order_item_id` int NOT NULL AUTO_INCREMENT,
  `order_id` varchar(45) NOT NULL,
  `sku_no` varchar(45) NOT NULL,
  `order_item_price` decimal(12,2) NOT NULL,
  PRIMARY KEY (`order_item_id`),
  UNIQUE KEY `sku_no_UNIQUE` (`sku_no`),
  KEY `order_id_idx` (`order_id`),
  CONSTRAINT `order_id_fk_oi` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sku_no_fk_oi` FOREIGN KEY (`sku_no`) REFERENCES `product_stock` (`sku_no`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_seq`
--

DROP TABLE IF EXISTS `order_seq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_seq` (
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_seq`
--

LOCK TABLES `order_seq` WRITE;
/*!40000 ALTER TABLE `order_seq` DISABLE KEYS */;
INSERT INTO `order_seq` VALUES (3),(4),(24);
/*!40000 ALTER TABLE `order_seq` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_id` varchar(45) NOT NULL,
  `user_id` int NOT NULL,
  `order_date` datetime NOT NULL,
  `shipping_address_id` int DEFAULT NULL,
  `shipping_method_id` int NOT NULL,
  `shipping_tracking_id` varchar(45) DEFAULT NULL,
  `shipping_price` decimal(12,2) DEFAULT NULL,
  `order_subtotal` decimal(12,2) NOT NULL,
  `order_tax` decimal(12,2) NOT NULL,
  `order_total` decimal(12,2) NOT NULL,
  `order_total_dim_h` decimal(12,4) NOT NULL,
  `order_total_dim_l` decimal(12,4) NOT NULL,
  `order_total_dim_w` decimal(12,4) NOT NULL,
  `order_total_weight` decimal(12,4) NOT NULL,
  `contains_exchange_unit` tinyint NOT NULL,
  `exchange_unit_img` json DEFAULT NULL,
  `is_cancelled` tinyint NOT NULL,
  `is_completed` tinyint NOT NULL,
  `current_status_id` int NOT NULL,
  `current_status_date` datetime NOT NULL,
  `current_status_comment` mediumtext,
  PRIMARY KEY (`order_id`),
  KEY `shipping_method_id_idx` (`shipping_method_id`),
  KEY `shipping_address_id_idx` (`shipping_address_id`),
  KEY `user_id_idx` (`user_id`),
  KEY `current_status_id_fk_o_idx` (`current_status_id`),
  CONSTRAINT `current_status_id_fk_o` FOREIGN KEY (`current_status_id`) REFERENCES `statuses` (`id_status`) ON UPDATE CASCADE,
  CONSTRAINT `shipping_address_id_fk_o` FOREIGN KEY (`shipping_address_id`) REFERENCES `user_addresses` (`address_id`) ON DELETE SET NULL ON UPDATE SET NULL,
  CONSTRAINT `shipping_method_id_fk_o` FOREIGN KEY (`shipping_method_id`) REFERENCES `shipping_method` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `user_id_fk_o` FOREIGN KEY (`user_id`) REFERENCES `user_login` (`user_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `order_id_trigger` BEFORE INSERT ON `orders` FOR EACH ROW BEGIN
  INSERT INTO order_seq VALUES (NULL);
  SET NEW.order_id = CONCAT('OR', LPAD(LAST_INSERT_ID(), 3, '0'));
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `current_status_from_orders_insert_trigger` AFTER INSERT ON `orders` FOR EACH ROW BEGIN
	INSERT INTO order_history (order_id, status_id, status_date, status_comment)
    SELECT order_id, current_status_id, current_status_date, current_status_comment FROM orders;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `current_status_from_orders_update_trigger` AFTER UPDATE ON `orders` FOR EACH ROW BEGIN
	IF NEW.current_status_id <> OLD.current_status_id OR NEW.current_status_date <> OLD.current_status_date
    THEN
		INSERT INTO order_history (order_id, status_id, status_date, status_comment)
		SELECT order_id, current_status_id, current_status_date, current_status_comment FROM orders;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `product_config`
--

DROP TABLE IF EXISTS `product_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_config` (
  `product_config_id` int NOT NULL AUTO_INCREMENT,
  `products_id` varchar(45) NOT NULL,
  `variation_id` int NOT NULL,
  `price` decimal(12,2) NOT NULL,
  `is_synced` tinyint NOT NULL,
  `sage_id` int DEFAULT NULL,
  `sage_item_code` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`product_config_id`),
  UNIQUE KEY `sage_item_code_UNIQUE` (`sage_item_code`),
  UNIQUE KEY `sage_id_UNIQUE` (`sage_id`),
  KEY `product_id_idx` (`products_id`),
  KEY `variation_id_idx` (`variation_id`),
  CONSTRAINT `products_id_fk_pc` FOREIGN KEY (`products_id`) REFERENCES `products` (`products_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `variation_id_fk_pc` FOREIGN KEY (`variation_id`) REFERENCES `variations` (`variation_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_config`
--

LOCK TABLES `product_config` WRITE;
/*!40000 ALTER TABLE `product_config` DISABLE KEYS */;
/*!40000 ALTER TABLE `product_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_models`
--

DROP TABLE IF EXISTS `product_models`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_models` (
  `model_number` varchar(45) NOT NULL,
  `products_id` varchar(45) NOT NULL,
  PRIMARY KEY (`model_number`),
  KEY `product_id_idx` (`products_id`),
  CONSTRAINT `products_id_fk_pm` FOREIGN KEY (`products_id`) REFERENCES `products` (`products_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_models`
--

LOCK TABLES `product_models` WRITE;
/*!40000 ALTER TABLE `product_models` DISABLE KEYS */;
/*!40000 ALTER TABLE `product_models` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_stock`
--

DROP TABLE IF EXISTS `product_stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_stock` (
  `sku_no` varchar(45) NOT NULL,
  `product_config_id` int NOT NULL,
  `is_purchased` tinyint NOT NULL,
  PRIMARY KEY (`sku_no`),
  KEY `product_config_id_fk_ps_idx` (`product_config_id`),
  CONSTRAINT `product_config_id_fk_ps` FOREIGN KEY (`product_config_id`) REFERENCES `product_config` (`product_config_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_stock`
--

LOCK TABLES `product_stock` WRITE;
/*!40000 ALTER TABLE `product_stock` DISABLE KEYS */;
/*!40000 ALTER TABLE `product_stock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `products_id` varchar(45) NOT NULL,
  `name` varchar(45) NOT NULL,
  `weight` decimal(12,4) NOT NULL,
  `dimension_h` decimal(12,4) NOT NULL,
  `dimension_l` decimal(12,4) NOT NULL,
  `dimension_w` decimal(12,4) NOT NULL,
  `brands_id` varchar(20) NOT NULL,
  `categories_id` varchar(20) NOT NULL,
  `product_img` varchar(500) NOT NULL,
  `product_img_thumb` varchar(500) NOT NULL,
  `warranty` varchar(20) NOT NULL,
  `is_repairable` tinyint NOT NULL,
  `stock_available` int NOT NULL,
  `is_active` tinyint NOT NULL,
  PRIMARY KEY (`products_id`),
  KEY `brand_id_idx` (`brands_id`),
  KEY `category_id_idx` (`categories_id`),
  CONSTRAINT `brands_id_fk_p` FOREIGN KEY (`brands_id`) REFERENCES `brands` (`brands_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `categories_id_fk_p` FOREIGN KEY (`categories_id`) REFERENCES `categories` (`categories_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repair_communication_history`
--

DROP TABLE IF EXISTS `repair_communication_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `repair_communication_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `repair_id` varchar(45) NOT NULL,
  `comm_method` char(45) NOT NULL,
  `comm_type` char(45) NOT NULL,
  `comm_recipient` varchar(45) NOT NULL,
  `comm_date` datetime NOT NULL,
  `comm_subject` mediumtext NOT NULL,
  `comm_comment` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `repair_id_fk_rech_idx` (`repair_id`),
  KEY `user_id_fk_rech_idx` (`user_id`),
  CONSTRAINT `repair_id_fk_rech` FOREIGN KEY (`repair_id`) REFERENCES `repairs` (`repair_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `user_id_fk_rech` FOREIGN KEY (`user_id`) REFERENCES `user_login` (`user_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repair_communication_history`
--

LOCK TABLES `repair_communication_history` WRITE;
/*!40000 ALTER TABLE `repair_communication_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `repair_communication_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repair_history`
--

DROP TABLE IF EXISTS `repair_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `repair_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `repair_id` varchar(45) NOT NULL,
  `status_id` int NOT NULL,
  `status_date` datetime NOT NULL,
  `status_comment` mediumtext,
  PRIMARY KEY (`id`),
  KEY `repair_id_fk_reh_idx` (`repair_id`),
  KEY `status_id_fk_reh_idx` (`status_id`),
  CONSTRAINT `repair_id_fk_reh` FOREIGN KEY (`repair_id`) REFERENCES `repairs` (`repair_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `status_id_fk_reh` FOREIGN KEY (`status_id`) REFERENCES `statuses` (`id_status`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repair_history`
--

LOCK TABLES `repair_history` WRITE;
/*!40000 ALTER TABLE `repair_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `repair_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repair_seq`
--

DROP TABLE IF EXISTS `repair_seq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `repair_seq` (
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repair_seq`
--

LOCK TABLES `repair_seq` WRITE;
/*!40000 ALTER TABLE `repair_seq` DISABLE KEYS */;
/*!40000 ALTER TABLE `repair_seq` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repairs`
--

DROP TABLE IF EXISTS `repairs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `repairs` (
  `repair_id` varchar(45) NOT NULL,
  `user_id` int NOT NULL,
  `repair_date` datetime NOT NULL,
  `product_id` varchar(45) NOT NULL,
  `reason_repair` longtext NOT NULL,
  `error_codes` mediumtext,
  `shipping_address_id` int DEFAULT NULL,
  `shipping_method_id` int NOT NULL,
  `shipping_tracking_id` varchar(45) DEFAULT NULL,
  `shipping_price_excl` decimal(12,2) DEFAULT NULL,
  `shipping_price_incl` decimal(12,2) DEFAULT NULL,
  `shipping_price_tax` decimal(12,2) DEFAULT NULL,
  `is_cancelled` tinyint NOT NULL,
  `is_completed` tinyint NOT NULL,
  `current_status_id` int NOT NULL,
  `current_status_date` datetime NOT NULL,
  `current_status_comment` mediumtext,
  PRIMARY KEY (`repair_id`),
  KEY `user_id_rp_idx` (`user_id`),
  KEY `product_id_rp_idx` (`product_id`),
  KEY `current_status_id_fk_rp_idx` (`current_status_id`),
  CONSTRAINT `current_status_id_fk_re` FOREIGN KEY (`current_status_id`) REFERENCES `statuses` (`id_status`) ON UPDATE CASCADE,
  CONSTRAINT `product_id_fk_re` FOREIGN KEY (`product_id`) REFERENCES `products` (`products_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `user_id_fk_re` FOREIGN KEY (`user_id`) REFERENCES `user_login` (`user_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repairs`
--

LOCK TABLES `repairs` WRITE;
/*!40000 ALTER TABLE `repairs` DISABLE KEYS */;
/*!40000 ALTER TABLE `repairs` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `repair_id_trigger` BEFORE INSERT ON `repairs` FOR EACH ROW BEGIN
  INSERT INTO repair_seq VALUES (NULL);
  SET NEW.repair_id = CONCAT('RE', LPAD(LAST_INSERT_ID(), 3, '0'));
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `current_status_from_repairs_insert_trigger` AFTER INSERT ON `repairs` FOR EACH ROW BEGIN
	INSERT INTO repair_history (repair_id, status_id, status_date, status_comment)
    SELECT repair_id, current_status_id, current_status_date, current_status_comment FROM repairs;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `current_status_from_repairs_update_trigger` AFTER UPDATE ON `repairs` FOR EACH ROW BEGIN
	IF NEW.current_status_id <> OLD.current_status_id OR NEW.current_status_date <> OLD.current_status_date
    THEN
		INSERT INTO repair_history (repair_id, status_id, status_date, status_comment)
		SELECT repair_id, current_status_id, current_status_date, current_status_comment FROM repairs;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `return_communication_history`
--

DROP TABLE IF EXISTS `return_communication_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `return_communication_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `return_id` varchar(45) NOT NULL,
  `comm_method` char(45) NOT NULL,
  `comm_type` char(45) NOT NULL,
  `comm_recipient` varchar(45) NOT NULL,
  `comm_date` datetime NOT NULL,
  `comm_subject` mediumtext NOT NULL,
  `comm_comment` longtext CHARACTER SET armscii8 COLLATE armscii8_general_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `return_id_fk_rtch_idx` (`return_id`),
  KEY `user_id_fk_rtch_idx` (`user_id`),
  CONSTRAINT `return_id_fk_rtch` FOREIGN KEY (`return_id`) REFERENCES `returns` (`return_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `user_id_fk_rtch` FOREIGN KEY (`user_id`) REFERENCES `user_login` (`user_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `return_communication_history`
--

LOCK TABLES `return_communication_history` WRITE;
/*!40000 ALTER TABLE `return_communication_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `return_communication_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `return_history`
--

DROP TABLE IF EXISTS `return_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `return_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `return_id` varchar(45) NOT NULL,
  `status_id` int NOT NULL,
  `status_date` datetime NOT NULL,
  `status_comment` mediumtext,
  PRIMARY KEY (`id`),
  KEY `return_id_fk_rh_idx` (`return_id`),
  KEY `status_id_fk_rh_idx` (`status_id`),
  CONSTRAINT `return_id_fk_rth` FOREIGN KEY (`return_id`) REFERENCES `returns` (`return_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `status_id_fk_rth` FOREIGN KEY (`status_id`) REFERENCES `statuses` (`id_status`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `return_history`
--

LOCK TABLES `return_history` WRITE;
/*!40000 ALTER TABLE `return_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `return_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `returns`
--

DROP TABLE IF EXISTS `returns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `returns` (
  `return_id` varchar(45) NOT NULL,
  `user_id` int NOT NULL,
  `order_id` varchar(45) NOT NULL,
  `order_item_id` int NOT NULL,
  `reason_return` longtext NOT NULL,
  `product_problem` mediumtext NOT NULL,
  `is_completed` tinyint NOT NULL,
  `preferred_outcome` mediumtext NOT NULL,
  `current_status_id` int NOT NULL,
  `current_status_date` datetime NOT NULL,
  `current_status_comment` mediumtext,
  PRIMARY KEY (`return_id`),
  KEY `user_id_idx` (`user_id`),
  KEY `order_id_idx` (`order_id`),
  KEY `order_item_id_fk_rt_idx` (`order_item_id`),
  KEY `current_status_id_fk_rt_idx` (`current_status_id`),
  CONSTRAINT `current_status_id_fk_rt` FOREIGN KEY (`current_status_id`) REFERENCES `statuses` (`id_status`) ON UPDATE CASCADE,
  CONSTRAINT `order_id_fk_rt` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `order_item_id_fk_rt` FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`order_item_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `user_id_fk_rt` FOREIGN KEY (`user_id`) REFERENCES `user_login` (`user_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `returns`
--

LOCK TABLES `returns` WRITE;
/*!40000 ALTER TABLE `returns` DISABLE KEYS */;
/*!40000 ALTER TABLE `returns` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `return_id_trigger` BEFORE INSERT ON `returns` FOR EACH ROW BEGIN
  INSERT INTO returns_seq VALUES (NULL);
  SET NEW.return_id = CONCAT('RN', LPAD(LAST_INSERT_ID(), 3, '0'));
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `current_status_from_returns_insert_trigger` AFTER INSERT ON `returns` FOR EACH ROW BEGIN
	INSERT INTO return_history (return_id, status_id, status_date, status_comment)
    SELECT return_id, current_status_id, current_status_date, current_status_comment FROM `returns`;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `current_status_from_returns_update_trigger` AFTER UPDATE ON `returns` FOR EACH ROW BEGIN
	IF NEW.current_status_id <> OLD.current_status_id OR NEW.current_status_date <> OLD.current_status_date
    THEN
		INSERT INTO return_history (return_id, status_id, status_date, status_comment)
		SELECT return_id, current_status_id, current_status_date, current_status_comment FROM `returns`;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `returns_seq`
--

DROP TABLE IF EXISTS `returns_seq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `returns_seq` (
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `returns_seq`
--

LOCK TABLES `returns_seq` WRITE;
/*!40000 ALTER TABLE `returns_seq` DISABLE KEYS */;
/*!40000 ALTER TABLE `returns_seq` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shipping_method`
--

DROP TABLE IF EXISTS `shipping_method`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shipping_method` (
  `id` int NOT NULL AUTO_INCREMENT,
  `value` char(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shipping_method`
--

LOCK TABLES `shipping_method` WRITE;
/*!40000 ALTER TABLE `shipping_method` DISABLE KEYS */;
INSERT INTO `shipping_method` VALUES (1,'courier');
/*!40000 ALTER TABLE `shipping_method` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shopping_cart`
--

DROP TABLE IF EXISTS `shopping_cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shopping_cart` (
  `shopping_cart_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `subtotal` decimal(12,2) NOT NULL,
  `vat` decimal(12,2) NOT NULL,
  `total` decimal(12,2) NOT NULL,
  PRIMARY KEY (`shopping_cart_id`),
  KEY `user_id_idx` (`user_id`),
  CONSTRAINT `user_id_fk_sc` FOREIGN KEY (`user_id`) REFERENCES `user_login` (`user_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shopping_cart`
--

LOCK TABLES `shopping_cart` WRITE;
/*!40000 ALTER TABLE `shopping_cart` DISABLE KEYS */;
/*!40000 ALTER TABLE `shopping_cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shopping_cart_items`
--

DROP TABLE IF EXISTS `shopping_cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shopping_cart_items` (
  `shopping_cart_items_id` int NOT NULL AUTO_INCREMENT,
  `shopping_cart_id` int NOT NULL,
  `product_config_id` int NOT NULL,
  `quantity` int NOT NULL,
  `total_price` decimal(12,2) NOT NULL,
  PRIMARY KEY (`shopping_cart_items_id`),
  KEY `shopping_cart_id_idx` (`shopping_cart_id`),
  KEY `products_id_fk_sci_idx` (`product_config_id`),
  CONSTRAINT `products_config_fk_sci` FOREIGN KEY (`product_config_id`) REFERENCES `product_config` (`product_config_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `shopping_cart_id_fk_sci` FOREIGN KEY (`shopping_cart_id`) REFERENCES `shopping_cart` (`shopping_cart_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shopping_cart_items`
--

LOCK TABLES `shopping_cart_items` WRITE;
/*!40000 ALTER TABLE `shopping_cart_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `shopping_cart_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `statuses`
--

DROP TABLE IF EXISTS `statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `statuses` (
  `id_status` int NOT NULL AUTO_INCREMENT,
  `type` char(45) NOT NULL,
  `value` char(45) NOT NULL,
  `is_active` tinyint NOT NULL,
  PRIMARY KEY (`id_status`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statuses`
--

LOCK TABLES `statuses` WRITE;
/*!40000 ALTER TABLE `statuses` DISABLE KEYS */;
INSERT INTO `statuses` VALUES (1,'exchange_unit','requested_order',1);
/*!40000 ALTER TABLE `statuses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_addresses`
--

DROP TABLE IF EXISTS `user_addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_addresses` (
  `address_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `name` char(45) NOT NULL,
  `unit_number` varchar(45) DEFAULT NULL,
  `address_line_1` varchar(45) NOT NULL,
  `address_line_2` varchar(45) DEFAULT NULL,
  `city` char(45) NOT NULL,
  `region` char(45) NOT NULL,
  `postal_code` varchar(45) NOT NULL,
  `contact_number` varchar(45) NOT NULL,
  `is_regional` tinyint NOT NULL,
  `is_active` tinyint NOT NULL,
  PRIMARY KEY (`address_id`),
  KEY `user_id_idx` (`user_id`),
  CONSTRAINT `user_id_fk_ua` FOREIGN KEY (`user_id`) REFERENCES `user_login` (`user_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_addresses`
--

LOCK TABLES `user_addresses` WRITE;
/*!40000 ALTER TABLE `user_addresses` DISABLE KEYS */;
INSERT INTO `user_addresses` VALUES (1,1,'jason','unit 4','crompton','winchester','miami','surmer','5009','1',0,1);
/*!40000 ALTER TABLE `user_addresses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_details`
--

DROP TABLE IF EXISTS `user_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_details` (
  `user_id` int NOT NULL,
  `name` char(45) NOT NULL,
  `surname` char(45) DEFAULT NULL,
  `company` varchar(45) DEFAULT NULL,
  `default_address_id` int DEFAULT NULL,
  `shop_city_id` int DEFAULT NULL,
  `company_reg_no` varchar(45) DEFAULT NULL,
  `vat_no` int DEFAULT NULL,
  `is_synced` tinyint NOT NULL,
  `sage_id` int DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `sage_id_UNIQUE` (`sage_id`),
  KEY `shop_city_id_idx` (`shop_city_id`),
  KEY `default_address_id_fk_ud` (`default_address_id`),
  CONSTRAINT `default_address_id_fk_ud` FOREIGN KEY (`default_address_id`) REFERENCES `user_addresses` (`address_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `shop_city_id_fk_ud` FOREIGN KEY (`shop_city_id`) REFERENCES `cities` (`city_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `user_id_fk_ud` FOREIGN KEY (`user_id`) REFERENCES `user_login` (`user_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_details`
--

LOCK TABLES `user_details` WRITE;
/*!40000 ALTER TABLE `user_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_login`
--

DROP TABLE IF EXISTS `user_login`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_login` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password` varchar(500) NOT NULL,
  `mobile_no` varchar(45) NOT NULL,
  `created_at` datetime NOT NULL,
  `is_blacklisted` tinyint NOT NULL,
  `is_verified` tinyint NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_login`
--

LOCK TABLES `user_login` WRITE;
/*!40000 ALTER TABLE `user_login` DISABLE KEYS */;
INSERT INTO `user_login` VALUES (1,'1','1','','0000-00-00 00:00:00',0,0);
/*!40000 ALTER TABLE `user_login` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `variations`
--

DROP TABLE IF EXISTS `variations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `variations` (
  `variation_id` int NOT NULL AUTO_INCREMENT,
  `value` varchar(45) NOT NULL,
  PRIMARY KEY (`variation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `variations`
--

LOCK TABLES `variations` WRITE;
/*!40000 ALTER TABLE `variations` DISABLE KEYS */;
/*!40000 ALTER TABLE `variations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'ecommerce_db'
--

--
-- Dumping routines for database 'ecommerce_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-03-05 15:24:14
