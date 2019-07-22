-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema belt
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `belt` ;

-- -----------------------------------------------------
-- Schema belt
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `belt` DEFAULT CHARACTER SET utf8 ;
USE `belt` ;

-- -----------------------------------------------------
-- Table `belt`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `belt`.`users` ;

CREATE TABLE IF NOT EXISTS `belt`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NULL DEFAULT NULL,
  `last_name` VARCHAR(255) NULL DEFAULT NULL,
  `username` VARCHAR(255) NULL DEFAULT NULL,
  `email` VARCHAR(255) NULL DEFAULT NULL,
  `pw_hash` VARCHAR(255) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 8
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `belt`.`quotes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `belt`.`quotes` ;

CREATE TABLE IF NOT EXISTS `belt`.`quotes` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `quote_content` VARCHAR(255) NULL DEFAULT NULL,
  `quote_author` VARCHAR(255) NULL DEFAULT NULL,
  `author` INT(11) NOT NULL,
  `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `fk_messages_users_idx` (`author` ASC) VISIBLE,
  CONSTRAINT `fk_messages_users`
    FOREIGN KEY (`author`)
    REFERENCES `belt`.`users` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `belt`.`users_likes_quotes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `belt`.`users_likes_quotes` ;

CREATE TABLE IF NOT EXISTS `belt`.`users_likes_quotes` (
  `quotes_id` INT(11) NOT NULL AUTO_INCREMENT,
  `users_id` INT(11) NOT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`quotes_id`, `users_id`),
  INDEX `fk_users_has_messages_messages1_idx` (`quotes_id` ASC) VISIBLE,
  INDEX `fk_users_has_messages_users_idx` (`users_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_messages_messages1`
    FOREIGN KEY (`quotes_id`)
    REFERENCES `belt`.`quotes` (`id`),
  CONSTRAINT `fk_users_has_messages_users`
    FOREIGN KEY (`users_id`)
    REFERENCES `belt`.`users` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
