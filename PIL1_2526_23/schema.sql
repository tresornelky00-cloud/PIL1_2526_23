-- ============================================================
-- IFRI MentorLink — Schéma MySQL complet
-- Usage : mysql -u root -p ifri_mentorlink < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS ifri_mentorlink CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ifri_mentorlink;

-- ── Users ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    nom              VARCHAR(100) NOT NULL,
    prenom           VARCHAR(100) NOT NULL,
    email            VARCHAR(255) NOT NULL UNIQUE,
    telephone        VARCHAR(20)  NOT NULL UNIQUE,
    mot_de_passe     VARCHAR(255) NOT NULL,
    photo_profil     VARCHAR(500) DEFAULT NULL,
    filiere          ENUM('GL','IA','IM','SE_IoT','SI') NOT NULL,
    niveau           ENUM('L1','L2','L3','M1','M2') NOT NULL,
    bio              TEXT DEFAULT NULL,
    date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP,
    actif            BOOLEAN DEFAULT TRUE
);

-- ── Compétences ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS competences (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    nom       VARCHAR(100) NOT NULL UNIQUE,
    categorie VARCHAR(50)  DEFAULT 'Général'
);

-- ── Pivot users ↔ compétences ─────────────────────────────────
CREATE TABLE IF NOT EXISTS user_competences (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    competence_id INT NOT NULL,
    type          ENUM('maitrise','lacune') NOT NULL,
    UNIQUE KEY uq_user_comp_type (user_id, competence_id, type),
    FOREIGN KEY (user_id)       REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (competence_id) REFERENCES competences(id) ON DELETE CASCADE
);

-- ── Disponibilités ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS disponibilites (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    jour        ENUM('Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche') NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin   TIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── Offres de mentorat ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS offres_mentorat (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    type_offre    ENUM('offre','demande') NOT NULL,
    competence_id INT NOT NULL,
    format        ENUM('presentiel','en_ligne','les_deux') DEFAULT 'les_deux',
    description   TEXT DEFAULT NULL,
    active        BOOLEAN DEFAULT TRUE,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)       REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (competence_id) REFERENCES competences(id)
);

-- ── Matchs ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS matchs (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    mentor_id  INT NOT NULL,
    mentore_id INT NOT NULL,
    score      DECIMAL(5,2) NOT NULL,
    statut     ENUM('propose','accepte','refuse','termine') DEFAULT 'propose',
    date_match DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_match (mentor_id, mentore_id),
    FOREIGN KEY (mentor_id)  REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (mentore_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── Conversations ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversations (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user1_id      INT NOT NULL,
    user2_id      INT NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_conv (user1_id, user2_id),
    FOREIGN KEY (user1_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (user2_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── Messages ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS messages (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    expediteur_id   INT NOT NULL,
    contenu         TEXT NOT NULL,
    lu              BOOLEAN DEFAULT FALSE,
    date_envoi      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (expediteur_id)   REFERENCES users(id) ON DELETE CASCADE
);

-- ── Données initiales : compétences ──────────────────────────
INSERT IGNORE INTO competences (nom, categorie) VALUES
  ('Python',                    'Programmation'),
  ('Java',                      'Programmation'),
  ('C/C++',                     'Programmation'),
  ('JavaScript',                'Programmation'),
  ('PHP',                       'Programmation'),
  ('HTML/CSS',                  'Web'),
  ('React',                     'Web'),
  ('Flask/Django',              'Web'),
  ('Node.js',                   'Web'),
  ('SQL/MySQL',                 'Bases de données'),
  ('PostgreSQL',                'Bases de données'),
  ('MongoDB',                   'Bases de données'),
  ('Algèbre linéaire',          'Mathématiques'),
  ('Probabilités',              'Mathématiques'),
  ('Équations différentielles', 'Mathématiques'),
  ('Linux/Unix',                'Systèmes'),
  ('Réseaux',                   'Systèmes'),
  ('Arduino/IoT',               'Systèmes'),
  ('Machine Learning',          'Intelligence Artificielle'),
  ('Deep Learning',             'Intelligence Artificielle'),
  ('Traitement d''images',      'Intelligence Artificielle');
