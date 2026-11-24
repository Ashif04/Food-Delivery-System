CREATE DATABASE  IF NOT EXISTS `food_delivery` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `food_delivery`;
-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: food_delivery
-- ------------------------------------------------------
-- Server version	8.0.46

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
-- Table structure for table `addon_groups`
--

DROP TABLE IF EXISTS `addon_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `addon_groups` (
  `addon_group_id` bigint NOT NULL AUTO_INCREMENT,
  `restaurant_id` bigint NOT NULL,
  `group_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_required` tinyint(1) DEFAULT '0',
  `min_selection` int DEFAULT '0',
  `max_selection` int DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`addon_group_id`),
  KEY `fk_addon_groups_restaurant_id` (`restaurant_id`),
  KEY `fk_addon_groups_created_by` (`created_by`),
  KEY `fk_addon_groups_updated_by` (`updated_by`),
  CONSTRAINT `fk_addon_groups_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_addon_groups_restaurant_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`),
  CONSTRAINT `fk_addon_groups_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `addon_groups`
--

LOCK TABLES `addon_groups` WRITE;
/*!40000 ALTER TABLE `addon_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `addon_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `addons`
--

DROP TABLE IF EXISTS `addons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `addons` (
  `addon_id` bigint NOT NULL AUTO_INCREMENT,
  `addon_group_id` bigint NOT NULL,
  `addon_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `additional_price` decimal(10,2) DEFAULT '0.00',
  `is_available` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`addon_id`),
  KEY `fk_addons_addon_group_id` (`addon_group_id`),
  KEY `fk_addons_created_by` (`created_by`),
  KEY `fk_addons_updated_by` (`updated_by`),
  CONSTRAINT `fk_addons_addon_group_id` FOREIGN KEY (`addon_group_id`) REFERENCES `addon_groups` (`addon_group_id`),
  CONSTRAINT `fk_addons_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_addons_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `addons`
--

LOCK TABLES `addons` WRITE;
/*!40000 ALTER TABLE `addons` DISABLE KEYS */;
/*!40000 ALTER TABLE `addons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `addresses`
--

DROP TABLE IF EXISTS `addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `addresses` (
  `address_id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `address_type` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `house_number` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `street` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `area` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pincode` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `landmark` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `latitude` decimal(10,7) DEFAULT NULL,
  `longitude` decimal(10,7) DEFAULT NULL,
  `is_default` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`address_id`),
  KEY `fk_addresses_user_id` (`user_id`),
  KEY `fk_addresses_created_by` (`created_by`),
  KEY `fk_addresses_updated_by` (`updated_by`),
  CONSTRAINT `fk_addresses_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_addresses_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_addresses_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `addresses`
--

LOCK TABLES `addresses` WRITE;
/*!40000 ALTER TABLE `addresses` DISABLE KEYS */;
/*!40000 ALTER TABLE `addresses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('baseline_0001');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_item_addons`
--

DROP TABLE IF EXISTS `cart_item_addons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_item_addons` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `cart_item_id` bigint NOT NULL,
  `addon_id` bigint NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `fk_cart_item_addons_cart_item_id` (`cart_item_id`),
  KEY `fk_cart_item_addons_addon_id` (`addon_id`),
  KEY `fk_cart_item_addons_created_by` (`created_by`),
  KEY `fk_cart_item_addons_updated_by` (`updated_by`),
  CONSTRAINT `fk_cart_item_addons_addon_id` FOREIGN KEY (`addon_id`) REFERENCES `addons` (`addon_id`),
  CONSTRAINT `fk_cart_item_addons_cart_item_id` FOREIGN KEY (`cart_item_id`) REFERENCES `cart_items` (`cart_item_id`),
  CONSTRAINT `fk_cart_item_addons_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_cart_item_addons_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_item_addons`
--

LOCK TABLES `cart_item_addons` WRITE;
/*!40000 ALTER TABLE `cart_item_addons` DISABLE KEYS */;
/*!40000 ALTER TABLE `cart_item_addons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_items`
--

DROP TABLE IF EXISTS `cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_items` (
  `cart_item_id` bigint NOT NULL AUTO_INCREMENT,
  `cart_id` bigint NOT NULL,
  `item_id` bigint NOT NULL,
  `variant_id` bigint DEFAULT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  `special_instructions` text COLLATE utf8mb4_unicode_ci,
  `added_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`cart_item_id`),
  KEY `fk_cart_items_cart_id` (`cart_id`),
  KEY `fk_cart_items_item_id` (`item_id`),
  KEY `fk_cart_items_variant_id` (`variant_id`),
  KEY `fk_cart_items_created_by` (`created_by`),
  KEY `fk_cart_items_updated_by` (`updated_by`),
  CONSTRAINT `fk_cart_items_cart_id` FOREIGN KEY (`cart_id`) REFERENCES `carts` (`cart_id`),
  CONSTRAINT `fk_cart_items_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_cart_items_item_id` FOREIGN KEY (`item_id`) REFERENCES `menu_items` (`item_id`),
  CONSTRAINT `fk_cart_items_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_cart_items_variant_id` FOREIGN KEY (`variant_id`) REFERENCES `item_variants` (`variant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `cart_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `carts`
--

DROP TABLE IF EXISTS `carts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `carts` (
  `cart_id` bigint NOT NULL AUTO_INCREMENT,
  `customer_id` bigint NOT NULL,
  `restaurant_id` bigint NOT NULL,
  `cart_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT 'ACTIVE',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`cart_id`),
  KEY `fk_carts_customer_id` (`customer_id`),
  KEY `fk_carts_restaurant_id` (`restaurant_id`),
  KEY `fk_carts_created_by` (`created_by`),
  KEY `fk_carts_updated_by` (`updated_by`),
  CONSTRAINT `fk_carts_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_carts_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `fk_carts_restaurant_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`),
  CONSTRAINT `fk_carts_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carts`
--

LOCK TABLES `carts` WRITE;
/*!40000 ALTER TABLE `carts` DISABLE KEYS */;
/*!40000 ALTER TABLE `carts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coupons`
--

DROP TABLE IF EXISTS `coupons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coupons` (
  `coupon_id` bigint NOT NULL AUTO_INCREMENT,
  `coupon_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `discount_type` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `discount_value` decimal(10,2) NOT NULL,
  `maximum_discount` decimal(10,2) DEFAULT NULL,
  `minimum_order_amount` decimal(10,2) DEFAULT '0.00',
  `usage_limit` int DEFAULT NULL,
  `per_user_limit` int DEFAULT NULL,
  `valid_from` timestamp NULL DEFAULT NULL,
  `valid_until` timestamp NULL DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`coupon_id`),
  UNIQUE KEY `uq_coupons_code` (`coupon_code`),
  KEY `fk_coupons_created_by` (`created_by`),
  KEY `fk_coupons_updated_by` (`updated_by`),
  CONSTRAINT `fk_coupons_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_coupons_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coupons`
--

LOCK TABLES `coupons` WRITE;
/*!40000 ALTER TABLE `coupons` DISABLE KEYS */;
/*!40000 ALTER TABLE `coupons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cuisines`
--

DROP TABLE IF EXISTS `cuisines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cuisines` (
  `cuisine_id` bigint NOT NULL AUTO_INCREMENT,
  `cuisine_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`cuisine_id`),
  UNIQUE KEY `uq_cuisines_name` (`cuisine_name`),
  KEY `fk_cuisines_created_by` (`created_by`),
  KEY `fk_cuisines_updated_by` (`updated_by`),
  CONSTRAINT `fk_cuisines_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_cuisines_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cuisines`
--

LOCK TABLES `cuisines` WRITE;
/*!40000 ALTER TABLE `cuisines` DISABLE KEYS */;
/*!40000 ALTER TABLE `cuisines` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `customer_id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `gender` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`customer_id`),
  UNIQUE KEY `uq_customers_user_id` (`user_id`),
  KEY `fk_customers_created_by` (`created_by`),
  KEY `fk_customers_updated_by` (`updated_by`),
  CONSTRAINT `fk_customers_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_customers_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_customers_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `delivery_assignments`
--

DROP TABLE IF EXISTS `delivery_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_assignments` (
  `assignment_id` bigint NOT NULL AUTO_INCREMENT,
  `order_id` bigint NOT NULL,
  `partner_id` bigint NOT NULL,
  `assignment_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT 'ASSIGNED',
  `assigned_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `accepted_at` timestamp NULL DEFAULT NULL,
  `rejected_at` timestamp NULL DEFAULT NULL,
  `picked_up_at` timestamp NULL DEFAULT NULL,
  `completed_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`assignment_id`),
  KEY `fk_delivery_assignments_order_id` (`order_id`),
  KEY `fk_delivery_assignments_partner_id` (`partner_id`),
  KEY `fk_delivery_assignments_created_by` (`created_by`),
  KEY `fk_delivery_assignments_updated_by` (`updated_by`),
  CONSTRAINT `fk_delivery_assignments_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_delivery_assignments_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  CONSTRAINT `fk_delivery_assignments_partner_id` FOREIGN KEY (`partner_id`) REFERENCES `delivery_partners` (`partner_id`),
  CONSTRAINT `fk_delivery_assignments_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_assignments`
--

LOCK TABLES `delivery_assignments` WRITE;
/*!40000 ALTER TABLE `delivery_assignments` DISABLE KEYS */;
/*!40000 ALTER TABLE `delivery_assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `delivery_partners`
--

DROP TABLE IF EXISTS `delivery_partners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_partners` (
  `partner_id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `vehicle_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `vehicle_number` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `driving_license_number` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `verification_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT 'PENDING',
  `availability_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT 'AVAILABLE',
  `current_latitude` decimal(10,7) DEFAULT NULL,
  `current_longitude` decimal(10,7) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`partner_id`),
  UNIQUE KEY `uq_delivery_partners_user_id` (`user_id`),
  UNIQUE KEY `uq_delivery_partners_vehicle_number` (`vehicle_number`),
  UNIQUE KEY `uq_delivery_partners_license` (`driving_license_number`),
  KEY `fk_delivery_partners_created_by` (`created_by`),
  KEY `fk_delivery_partners_updated_by` (`updated_by`),
  CONSTRAINT `fk_delivery_partners_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_delivery_partners_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_delivery_partners_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_partners`
--

LOCK TABLES `delivery_partners` WRITE;
/*!40000 ALTER TABLE `delivery_partners` DISABLE KEYS */;
/*!40000 ALTER TABLE `delivery_partners` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `delivery_tracking`
--

DROP TABLE IF EXISTS `delivery_tracking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_tracking` (
  `tracking_id` bigint NOT NULL AUTO_INCREMENT,
  `assignment_id` bigint NOT NULL,
  `latitude` decimal(10,7) NOT NULL,
  `longitude` decimal(10,7) NOT NULL,
  `recorded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`tracking_id`),
  KEY `fk_delivery_tracking_assignment_id` (`assignment_id`),
  KEY `fk_delivery_tracking_created_by` (`created_by`),
  KEY `fk_delivery_tracking_updated_by` (`updated_by`),
  CONSTRAINT `fk_delivery_tracking_assignment_id` FOREIGN KEY (`assignment_id`) REFERENCES `delivery_assignments` (`assignment_id`),
  CONSTRAINT `fk_delivery_tracking_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_delivery_tracking_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_tracking`
--

LOCK TABLES `delivery_tracking` WRITE;
/*!40000 ALTER TABLE `delivery_tracking` DISABLE KEYS */;
/*!40000 ALTER TABLE `delivery_tracking` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `food_categories`
--

DROP TABLE IF EXISTS `food_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `food_categories` (
  `category_id` bigint NOT NULL AUTO_INCREMENT,
  `category_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `image_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `uq_food_categories_name` (`category_name`),
  KEY `fk_food_categories_created_by` (`created_by`),
  KEY `fk_food_categories_updated_by` (`updated_by`),
  CONSTRAINT `fk_food_categories_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_food_categories_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `food_categories`
--

LOCK TABLES `food_categories` WRITE;
/*!40000 ALTER TABLE `food_categories` DISABLE KEYS */;
INSERT INTO `food_categories` VALUES (1,'Demo Mains 20261119083121909910','Sample main dishes.',NULL,'2026-11-19 08:31:21',NULL,NULL,NULL,1),(2,'Demo Sides 20261119083121909910','Sample side dishes.',NULL,'2026-11-19 08:31:21',NULL,NULL,NULL,1);
/*!40000 ALTER TABLE `food_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `food_item_reviews`
--

DROP TABLE IF EXISTS `food_item_reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `food_item_reviews` (
  `review_id` bigint NOT NULL AUTO_INCREMENT,
  `order_item_id` bigint NOT NULL,
  `item_id` bigint NOT NULL,
  `customer_id` bigint NOT NULL,
  `rating` int NOT NULL,
  `review_text` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`review_id`),
  UNIQUE KEY `uq_food_item_reviews` (`order_item_id`,`customer_id`),
  KEY `fk_food_item_reviews_item_id` (`item_id`),
  KEY `fk_food_item_reviews_customer_id` (`customer_id`),
  KEY `fk_food_item_reviews_created_by` (`created_by`),
  KEY `fk_food_item_reviews_updated_by` (`updated_by`),
  CONSTRAINT `fk_food_item_reviews_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_food_item_reviews_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `fk_food_item_reviews_item_id` FOREIGN KEY (`item_id`) REFERENCES `menu_items` (`item_id`),
  CONSTRAINT `fk_food_item_reviews_order_item_id` FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`order_item_id`),
  CONSTRAINT `fk_food_item_reviews_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `food_item_reviews`
--

LOCK TABLES `food_item_reviews` WRITE;
/*!40000 ALTER TABLE `food_item_reviews` DISABLE KEYS */;
/*!40000 ALTER TABLE `food_item_reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item_variants`
--

DROP TABLE IF EXISTS `item_variants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_variants` (
  `variant_id` bigint NOT NULL AUTO_INCREMENT,
  `item_id` bigint NOT NULL,
  `variant_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `is_available` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`variant_id`),
  KEY `fk_item_variants_item_id` (`item_id`),
  KEY `fk_item_variants_created_by` (`created_by`),
  KEY `fk_item_variants_updated_by` (`updated_by`),
  CONSTRAINT `fk_item_variants_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_item_variants_item_id` FOREIGN KEY (`item_id`) REFERENCES `menu_items` (`item_id`),
  CONSTRAINT `fk_item_variants_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item_variants`
--

LOCK TABLES `item_variants` WRITE;
/*!40000 ALTER TABLE `item_variants` DISABLE KEYS */;
/*!40000 ALTER TABLE `item_variants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_item_addon_groups`
--

DROP TABLE IF EXISTS `menu_item_addon_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_item_addon_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `item_id` bigint NOT NULL,
  `addon_group_id` bigint NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_menu_item_addon_groups` (`item_id`,`addon_group_id`),
  KEY `fk_menu_item_addon_groups_addon_group_id` (`addon_group_id`),
  KEY `fk_menu_item_addon_groups_created_by` (`created_by`),
  KEY `fk_menu_item_addon_groups_updated_by` (`updated_by`),
  CONSTRAINT `fk_menu_item_addon_groups_addon_group_id` FOREIGN KEY (`addon_group_id`) REFERENCES `addon_groups` (`addon_group_id`),
  CONSTRAINT `fk_menu_item_addon_groups_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_menu_item_addon_groups_item_id` FOREIGN KEY (`item_id`) REFERENCES `menu_items` (`item_id`),
  CONSTRAINT `fk_menu_item_addon_groups_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_item_addon_groups`
--

LOCK TABLES `menu_item_addon_groups` WRITE;
/*!40000 ALTER TABLE `menu_item_addon_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `menu_item_addon_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_item_images`
--

DROP TABLE IF EXISTS `menu_item_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_item_images` (
  `image_id` bigint NOT NULL AUTO_INCREMENT,
  `item_id` bigint NOT NULL,
  `image_url` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_primary` tinyint(1) DEFAULT '0',
  `display_order` int DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`image_id`),
  KEY `fk_menu_item_images_item_id` (`item_id`),
  KEY `fk_menu_item_images_created_by` (`created_by`),
  KEY `fk_menu_item_images_updated_by` (`updated_by`),
  CONSTRAINT `fk_menu_item_images_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_menu_item_images_item_id` FOREIGN KEY (`item_id`) REFERENCES `menu_items` (`item_id`),
  CONSTRAINT `fk_menu_item_images_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_item_images`
--

LOCK TABLES `menu_item_images` WRITE;
/*!40000 ALTER TABLE `menu_item_images` DISABLE KEYS */;
/*!40000 ALTER TABLE `menu_item_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_items`
--

DROP TABLE IF EXISTS `menu_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_items` (
  `item_id` bigint NOT NULL AUTO_INCREMENT,
  `restaurant_id` bigint NOT NULL,
  `category_id` bigint NOT NULL,
  `item_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `food_type` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `base_price` decimal(10,2) NOT NULL,
  `is_available` tinyint(1) DEFAULT '1',
  `preparation_time` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`item_id`),
  KEY `fk_menu_items_restaurant_id` (`restaurant_id`),
  KEY `fk_menu_items_category_id` (`category_id`),
  KEY `fk_menu_items_created_by` (`created_by`),
  KEY `fk_menu_items_updated_by` (`updated_by`),
  CONSTRAINT `fk_menu_items_category_id` FOREIGN KEY (`category_id`) REFERENCES `food_categories` (`category_id`),
  CONSTRAINT `fk_menu_items_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_menu_items_restaurant_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`),
  CONSTRAINT `fk_menu_items_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_items`
--

LOCK TABLES `menu_items` WRITE;
/*!40000 ALTER TABLE `menu_items` DISABLE KEYS */;
INSERT INTO `menu_items` VALUES (1,1,1,'Paneer Tikka','Grilled paneer with spices.','VEG',249.00,1,20,'2026-11-19 08:31:21',NULL,NULL,NULL,1),(2,1,1,'Chicken Biryani','Basmati rice with spiced chicken.','NON_VEG',329.00,1,30,'2026-11-19 08:31:22',NULL,NULL,NULL,1),(3,1,2,'Masala Dosa','Crisp dosa with potato masala.','VEG',159.00,1,18,'2026-11-19 08:31:22',NULL,NULL,NULL,1);
/*!40000 ALTER TABLE `menu_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_coupons`
--

DROP TABLE IF EXISTS `order_coupons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_coupons` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order_id` bigint NOT NULL,
  `coupon_id` bigint NOT NULL,
  `discount_amount` decimal(10,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_order_coupons_order` (`order_id`),
  KEY `fk_order_coupons_coupon_id` (`coupon_id`),
  KEY `fk_order_coupons_created_by` (`created_by`),
  KEY `fk_order_coupons_updated_by` (`updated_by`),
  CONSTRAINT `fk_order_coupons_coupon_id` FOREIGN KEY (`coupon_id`) REFERENCES `coupons` (`coupon_id`),
  CONSTRAINT `fk_order_coupons_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_order_coupons_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  CONSTRAINT `fk_order_coupons_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_coupons`
--

LOCK TABLES `order_coupons` WRITE;
/*!40000 ALTER TABLE `order_coupons` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_coupons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_item_addons`
--

DROP TABLE IF EXISTS `order_item_addons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_item_addons` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order_item_id` bigint NOT NULL,
  `addon_id` bigint DEFAULT NULL,
  `addon_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `fk_order_item_addons_order_item_id` (`order_item_id`),
  KEY `fk_order_item_addons_addon_id` (`addon_id`),
  KEY `fk_order_item_addons_created_by` (`created_by`),
  KEY `fk_order_item_addons_updated_by` (`updated_by`),
  CONSTRAINT `fk_order_item_addons_addon_id` FOREIGN KEY (`addon_id`) REFERENCES `addons` (`addon_id`),
  CONSTRAINT `fk_order_item_addons_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_order_item_addons_order_item_id` FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`order_item_id`),
  CONSTRAINT `fk_order_item_addons_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_item_addons`
--

LOCK TABLES `order_item_addons` WRITE;
/*!40000 ALTER TABLE `order_item_addons` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_item_addons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `order_item_id` bigint NOT NULL AUTO_INCREMENT,
  `order_id` bigint NOT NULL,
  `item_id` bigint DEFAULT NULL,
  `variant_id` bigint DEFAULT NULL,
  `item_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `variant_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `quantity` int NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `special_instructions` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`order_item_id`),
  KEY `fk_order_items_order_id` (`order_id`),
  KEY `fk_order_items_item_id` (`item_id`),
  KEY `fk_order_items_variant_id` (`variant_id`),
  KEY `fk_order_items_created_by` (`created_by`),
  KEY `fk_order_items_updated_by` (`updated_by`),
  CONSTRAINT `fk_order_items_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_order_items_item_id` FOREIGN KEY (`item_id`) REFERENCES `menu_items` (`item_id`),
  CONSTRAINT `fk_order_items_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  CONSTRAINT `fk_order_items_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_order_items_variant_id` FOREIGN KEY (`variant_id`) REFERENCES `item_variants` (`variant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_status_history`
--

DROP TABLE IF EXISTS `order_status_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_status_history` (
  `history_id` bigint NOT NULL AUTO_INCREMENT,
  `order_id` bigint NOT NULL,
  `old_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `new_status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `changed_by` bigint DEFAULT NULL,
  `remarks` text COLLATE utf8mb4_unicode_ci,
  `changed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`history_id`),
  KEY `fk_order_status_history_order_id` (`order_id`),
  KEY `fk_order_status_history_changed_by` (`changed_by`),
  KEY `fk_order_status_history_created_by` (`created_by`),
  KEY `fk_order_status_history_updated_by` (`updated_by`),
  CONSTRAINT `fk_order_status_history_changed_by` FOREIGN KEY (`changed_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_order_status_history_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_order_status_history_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  CONSTRAINT `fk_order_status_history_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_status_history`
--

LOCK TABLES `order_status_history` WRITE;
/*!40000 ALTER TABLE `order_status_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_status_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_id` bigint NOT NULL AUTO_INCREMENT,
  `order_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_id` bigint NOT NULL,
  `restaurant_id` bigint NOT NULL,
  `address_id` bigint DEFAULT NULL,
  `delivery_address_snapshot` text COLLATE utf8mb4_unicode_ci,
  `delivery_latitude` decimal(10,7) DEFAULT NULL,
  `delivery_longitude` decimal(10,7) DEFAULT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `item_discount` decimal(10,2) DEFAULT '0.00',
  `tax_amount` decimal(10,2) DEFAULT '0.00',
  `delivery_fee` decimal(10,2) DEFAULT '0.00',
  `platform_fee` decimal(10,2) DEFAULT '0.00',
  `packaging_fee` decimal(10,2) DEFAULT '0.00',
  `total_amount` decimal(10,2) NOT NULL,
  `payment_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT 'PENDING',
  `order_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT 'PLACED',
  `special_instructions` text COLLATE utf8mb4_unicode_ci,
  `placed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `accepted_at` timestamp NULL DEFAULT NULL,
  `delivered_at` timestamp NULL DEFAULT NULL,
  `cancelled_at` timestamp NULL DEFAULT NULL,
  `cancellation_reason` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`order_id`),
  UNIQUE KEY `uq_orders_order_number` (`order_number`),
  KEY `fk_orders_customer_id` (`customer_id`),
  KEY `fk_orders_restaurant_id` (`restaurant_id`),
  KEY `fk_orders_address_id` (`address_id`),
  KEY `fk_orders_created_by` (`created_by`),
  KEY `fk_orders_updated_by` (`updated_by`),
  CONSTRAINT `fk_orders_address_id` FOREIGN KEY (`address_id`) REFERENCES `addresses` (`address_id`),
  CONSTRAINT `fk_orders_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_orders_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `fk_orders_restaurant_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`),
  CONSTRAINT `fk_orders_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_methods`
--

DROP TABLE IF EXISTS `payment_methods`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_methods` (
  `payment_method_id` bigint NOT NULL AUTO_INCREMENT,
  `method_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`payment_method_id`),
  UNIQUE KEY `uq_payment_methods_name` (`method_name`),
  KEY `fk_payment_methods_created_by` (`created_by`),
  KEY `fk_payment_methods_updated_by` (`updated_by`),
  CONSTRAINT `fk_payment_methods_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_payment_methods_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_methods`
--

LOCK TABLES `payment_methods` WRITE;
/*!40000 ALTER TABLE `payment_methods` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment_methods` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `payment_id` bigint NOT NULL AUTO_INCREMENT,
  `order_id` bigint NOT NULL,
  `payment_method_id` bigint NOT NULL,
  `payment_reference` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT 'PENDING',
  `gateway_transaction_id` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `paid_at` timestamp NULL DEFAULT NULL,
  `refund_amount` decimal(10,2) DEFAULT '0.00',
  `refund_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `refund_reason` text COLLATE utf8mb4_unicode_ci,
  `refunded_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`payment_id`),
  UNIQUE KEY `uq_payments_reference` (`payment_reference`),
  KEY `fk_payments_order_id` (`order_id`),
  KEY `fk_payments_payment_method_id` (`payment_method_id`),
  KEY `fk_payments_created_by` (`created_by`),
  KEY `fk_payments_updated_by` (`updated_by`),
  CONSTRAINT `fk_payments_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_payments_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  CONSTRAINT `fk_payments_payment_method_id` FOREIGN KEY (`payment_method_id`) REFERENCES `payment_methods` (`payment_method_id`),
  CONSTRAINT `fk_payments_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_categories`
--

DROP TABLE IF EXISTS `restaurant_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_categories` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `restaurant_id` bigint NOT NULL,
  `category_id` bigint NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_restaurant_categories` (`restaurant_id`,`category_id`),
  KEY `fk_restaurant_categories_category_id` (`category_id`),
  KEY `fk_restaurant_categories_created_by` (`created_by`),
  KEY `fk_restaurant_categories_updated_by` (`updated_by`),
  CONSTRAINT `fk_restaurant_categories_category_id` FOREIGN KEY (`category_id`) REFERENCES `food_categories` (`category_id`),
  CONSTRAINT `fk_restaurant_categories_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_restaurant_categories_restaurant_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`),
  CONSTRAINT `fk_restaurant_categories_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_categories`
--

LOCK TABLES `restaurant_categories` WRITE;
/*!40000 ALTER TABLE `restaurant_categories` DISABLE KEYS */;
INSERT INTO `restaurant_categories` VALUES (1,1,1,'2026-11-19 08:40:30',NULL,NULL,NULL,1),(2,1,2,'2026-11-19 08:40:30',NULL,NULL,NULL,1);
/*!40000 ALTER TABLE `restaurant_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_cuisines`
--

DROP TABLE IF EXISTS `restaurant_cuisines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_cuisines` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `restaurant_id` bigint NOT NULL,
  `cuisine_id` bigint NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_restaurant_cuisines` (`restaurant_id`,`cuisine_id`),
  KEY `fk_restaurant_cuisines_cuisine_id` (`cuisine_id`),
  KEY `fk_restaurant_cuisines_created_by` (`created_by`),
  KEY `fk_restaurant_cuisines_updated_by` (`updated_by`),
  CONSTRAINT `fk_restaurant_cuisines_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_restaurant_cuisines_cuisine_id` FOREIGN KEY (`cuisine_id`) REFERENCES `cuisines` (`cuisine_id`),
  CONSTRAINT `fk_restaurant_cuisines_restaurant_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`),
  CONSTRAINT `fk_restaurant_cuisines_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_cuisines`
--

LOCK TABLES `restaurant_cuisines` WRITE;
/*!40000 ALTER TABLE `restaurant_cuisines` DISABLE KEYS */;
/*!40000 ALTER TABLE `restaurant_cuisines` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_hours`
--

DROP TABLE IF EXISTS `restaurant_hours`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_hours` (
  `hours_id` bigint NOT NULL AUTO_INCREMENT,
  `restaurant_id` bigint NOT NULL,
  `day_of_week` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `opening_time` time DEFAULT NULL,
  `closing_time` time DEFAULT NULL,
  `is_closed` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`hours_id`),
  UNIQUE KEY `uq_restaurant_hours_day` (`restaurant_id`,`day_of_week`),
  KEY `fk_restaurant_hours_created_by` (`created_by`),
  KEY `fk_restaurant_hours_updated_by` (`updated_by`),
  CONSTRAINT `fk_restaurant_hours_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_restaurant_hours_restaurant_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`),
  CONSTRAINT `fk_restaurant_hours_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_hours`
--

LOCK TABLES `restaurant_hours` WRITE;
/*!40000 ALTER TABLE `restaurant_hours` DISABLE KEYS */;
/*!40000 ALTER TABLE `restaurant_hours` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_owners`
--

DROP TABLE IF EXISTS `restaurant_owners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_owners` (
  `owner_id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `verification_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT 'PENDING',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`owner_id`),
  UNIQUE KEY `uq_restaurant_owners_user_id` (`user_id`),
  KEY `fk_restaurant_owners_created_by` (`created_by`),
  KEY `fk_restaurant_owners_updated_by` (`updated_by`),
  CONSTRAINT `fk_restaurant_owners_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_restaurant_owners_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_restaurant_owners_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_owners`
--

LOCK TABLES `restaurant_owners` WRITE;
/*!40000 ALTER TABLE `restaurant_owners` DISABLE KEYS */;
INSERT INTO `restaurant_owners` VALUES (1,1,'PENDING','2026-11-19 08:31:21',NULL,NULL,NULL,1);
/*!40000 ALTER TABLE `restaurant_owners` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurant_reviews`
--

DROP TABLE IF EXISTS `restaurant_reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurant_reviews` (
  `review_id` bigint NOT NULL AUTO_INCREMENT,
  `order_id` bigint NOT NULL,
  `customer_id` bigint NOT NULL,
  `restaurant_id` bigint NOT NULL,
  `rating` int NOT NULL,
  `review_text` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`review_id`),
  UNIQUE KEY `uq_restaurant_reviews` (`order_id`,`customer_id`),
  KEY `fk_restaurant_reviews_customer_id` (`customer_id`),
  KEY `fk_restaurant_reviews_restaurant_id` (`restaurant_id`),
  KEY `fk_restaurant_reviews_created_by` (`created_by`),
  KEY `fk_restaurant_reviews_updated_by` (`updated_by`),
  CONSTRAINT `fk_restaurant_reviews_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_restaurant_reviews_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `fk_restaurant_reviews_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  CONSTRAINT `fk_restaurant_reviews_restaurant_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`),
  CONSTRAINT `fk_restaurant_reviews_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurant_reviews`
--

LOCK TABLES `restaurant_reviews` WRITE;
/*!40000 ALTER TABLE `restaurant_reviews` DISABLE KEYS */;
/*!40000 ALTER TABLE `restaurant_reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `restaurants`
--

DROP TABLE IF EXISTS `restaurants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurants` (
  `restaurant_id` bigint NOT NULL AUTO_INCREMENT,
  `owner_id` bigint NOT NULL,
  `restaurant_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text COLLATE utf8mb4_unicode_ci,
  `city` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pincode` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `latitude` decimal(10,7) DEFAULT NULL,
  `longitude` decimal(10,7) DEFAULT NULL,
  `logo_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cover_image` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `average_rating` decimal(3,2) DEFAULT '0.00',
  `minimum_order_amount` decimal(10,2) DEFAULT '0.00',
  `estimated_delivery_time` int DEFAULT NULL,
  `is_open` tinyint(1) DEFAULT '1',
  `restaurant_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT 'PENDING',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`restaurant_id`),
  KEY `fk_restaurants_owner_id` (`owner_id`),
  KEY `fk_restaurants_created_by` (`created_by`),
  KEY `fk_restaurants_updated_by` (`updated_by`),
  CONSTRAINT `fk_restaurants_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_restaurants_owner_id` FOREIGN KEY (`owner_id`) REFERENCES `restaurant_owners` (`owner_id`),
  CONSTRAINT `fk_restaurants_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `restaurants`
--

LOCK TABLES `restaurants` WRITE;
/*!40000 ALTER TABLE `restaurants` DISABLE KEYS */;
INSERT INTO `restaurants` VALUES (1,1,'Demo Kitchen 20261119083121909910','Sample restaurant for browsing API testing.','demo.restaurant.20261119083121909910@example.test','556083121909910','10 Example Street','Bengaluru','Karnataka','560001',NULL,NULL,NULL,NULL,0.00,0.00,30,1,'PENDING','2026-11-19 08:31:21',NULL,NULL,NULL,1);
/*!40000 ALTER TABLE `restaurants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `role_id` bigint NOT NULL AUTO_INCREMENT,
  `role_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `uq_roles_role_name` (`role_name`),
  KEY `fk_roles_created_by` (`created_by`),
  KEY `fk_roles_updated_by` (`updated_by`),
  CONSTRAINT `fk_roles_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_roles_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Customer','Customer account role','2026-11-19 09:01:29',NULL,NULL,NULL,1);
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_roles`
--

DROP TABLE IF EXISTS `user_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_roles` (
  `user_role_id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `role_id` bigint NOT NULL,
  `assigned_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`user_role_id`),
  UNIQUE KEY `uq_user_roles_user_role` (`user_id`,`role_id`),
  KEY `fk_user_roles_role_id` (`role_id`),
  KEY `fk_user_roles_created_by` (`created_by`),
  KEY `fk_user_roles_updated_by` (`updated_by`),
  CONSTRAINT `fk_user_roles_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_user_roles_role_id` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`),
  CONSTRAINT `fk_user_roles_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_user_roles_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_roles`
--

LOCK TABLES `user_roles` WRITE;
/*!40000 ALTER TABLE `user_roles` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` bigint NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `profile_image` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email_verified` tinyint(1) DEFAULT '0',
  `phone_verified` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by` bigint DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` bigint DEFAULT NULL,
  `status` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uq_users_email` (`email`),
  UNIQUE KEY `uq_users_phone` (`phone`),
  KEY `fk_users_created_by` (`created_by`),
  KEY `fk_users_updated_by` (`updated_by`),
  CONSTRAINT `fk_users_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_users_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Sample Restaurant Owner','demo.owner.20261119083121909910@example.test','555083121909910','REPLACE_WITH_ARGON2_HASH',NULL,0,0,'2026-11-19 08:31:21',NULL,NULL,NULL,1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-24  9:34:35
