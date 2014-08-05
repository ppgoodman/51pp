/*
Navicat PGSQL Data Transfer

Source Server         : myubuntu
Source Server Version : 90304
Source Host           : 127.0.0.1:5432
Source Database       : p2pworld
Source Schema         : public

Target Server Type    : PGSQL
Target Server Version : 90304
File Encoding         : 65001

Date: 2014-08-05 13:17:11
*/


-- ----------------------------
-- Table structure for bttorrent
-- ----------------------------
DROP TABLE IF EXISTS "public"."bttorrent";
CREATE TABLE "public"."bttorrent" (
"idx" int4 DEFAULT nextval('bttorrent_idx_seq'::regclass) NOT NULL,
"infohash" char(60) COLLATE "default" NOT NULL,
"name" varchar(256) COLLATE "default" NOT NULL,
"length" int8 NOT NULL,
"buildtime" timestamp(6) NOT NULL,
"files" text COLLATE "default" NOT NULL,
"hits" int4 NOT NULL,
"downloads" int4 NOT NULL
)
WITH (OIDS=FALSE)

;

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Indexes structure for table bttorrent
-- ----------------------------
CREATE UNIQUE INDEX "bttorrent_idx_index" ON "public"."bttorrent" USING btree (idx);

-- ----------------------------
-- Primary Key structure for table bttorrent
-- ----------------------------
ALTER TABLE "public"."bttorrent" ADD PRIMARY KEY ("infohash");


-- ----------------------------
-- Table structure for keywordstatistics
-- ----------------------------
DROP TABLE IF EXISTS "public"."keywordstatistics";
CREATE TABLE "public"."keywordstatistics" (
"idx" int4 DEFAULT nextval('keywordstatistics_idx_seq'::regclass) NOT NULL,
"keywords" varchar(100) COLLATE "default" NOT NULL,
"times" int4 DEFAULT 0 NOT NULL
)
WITH (OIDS=FALSE)

;

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Primary Key structure for table keywordstatistics
-- ----------------------------
ALTER TABLE "public"."keywordstatistics" ADD PRIMARY KEY ("idx");
