=============
animescrawler
=============

Site web scrapé: https://myanimelist.net/

===============================
Quels données sont récupérées ?
===============================

Pour chaque animé disponible, on récupère:
    * son titre principale
    * ses titres alternatifs
    * son type
    * ses genres
    * son statut (diffusion terminé, diffusion en cours, à venir)
    * l'âge du public
    * la durée d'un épisode
    * leur nombre d'épisodes
    * son synopsis
    * les animés avec qui il est lié
    * les studios de productions
    * les dates de sa première diffusion
    * l'url de sa page sur myanimelist.net
    * son image de présentation
    * son rang
    * son score
    * sa popularité

====================
Stockage des données
====================
MongoDB

=====================
Mise à jour de la BDD 
=====================

Se placer dans le répertoire DataEngineerTools/6Evaluation/Projet et lancer les containers

Ouvrir le jupyter notebook dans un navigateur en se rendant à l'url http://localhost:8888/

Ouvrir le notebook animescrawler.ipynb situé dans le répertoire animescrawler et exécuter sa première cellule.

Relancer les containers afin de les mettre à jour

NB: En cas de problèmes, la seconde cellule de ce notebook permet de charger la BDD original
à partir d'un json fourni avec l'application.

===================================
Contenu du répertoire animescrawler
===================================

Le répertoire animescrawler contient:
    * items.py définit le format des scrapyItem qui contiendront les infos des animés
    * middlewares.py définit comment l’intergiciel extrait les pages de réponse et comment l’araignée fait le grattage. Dans notre cas, il est laissé tel quel.
    * pipelines.py définit comment chaque élément est inséré dans la base de données Mongo après le nettoyage de ses champs
    * setting.py gère le comportement de la spider en réglant le temps de téléchargement entre chaque requête sur le même domaine, désactivant les cookies et ordonant les pipelines
    * utils.py contient les différents user_agents utilisés pour faire un rotation à chaque requête envoyé au server

Le répertoire spiders contient:
    * anime_complet.json contenant les données initialements scrapées lors de la création de l'application
    * anime.json contenant les données récupérées lors de la dernière tentative de scraping
    * myanimelist.py définissant l'unique spider du crawler. Ce script contient: 
        * l'url de départ comportant les liens renvoyant aux différents index utilisés pour classer les animés (Upcomming,Just Added,#,A,...,Z)
        * les fonctions de parsing récupérant les informatiosn utiles pour construire les scrapyItems qui seront envoyés au pipeline
        * les fonctions traitant les erreurs 403 générées par l'apparition d'un captcha sur le site. Celle-ci relancent résolvent le captcha puis planifie une nouvelle tentative de scraping.

====================
Fonctions de parsing
====================
Les fonctions suivantes sont définies dans myanimelist.py:
    * parse() récupère sur l'url de départ http://myanimelist.net/anime.php les url pointant sur les premières pages des indexs classant les animés (Upcomming,Just Added,#,A,...,Z)
    * parse_index_links() récupère la liste d'url de parse() et y récupère les url pointant vers des pages complémentaires de chaque index
    * parse_page_links() récupère la liste d'url de parse_index_links() et y récupère les url pointant vers les page spécifiques à chaque animés
    * parse_anime_links() récupère la liste d'url de parse_page_links() et y récupère les informations utiles pour construire les scrapy Item qui seront poussé dans le pipeline

========================================
Fonctions de gestion d'erreur 403 et 404
========================================
Les fonctions suivantes sont définies dans myanimelist.py:
    * handle_error() est appelée à chaque erreur 403 ou 404 par les fonctions de parsing. Elle appelle la fonction résolvant les captcha et planifit les nouvelles tentatives de parsing des pages erronées
    * captcha_solving() est appelée par handle_error() en cas d'erreur 403. Celle-ci ouvre la page erronée dans un navigateur distant commandé par selenium et y résoud le captcha en cliquant sur le bouton "submit".

======================
Fonctions de nettoyage
======================
Les fonctions suivantes sont définies dans pipelines.py:
    * process_item() est la principale fonction de nettoyage de scrapy Item. Elle appelle un certain nombre de fonction afin de:
        * suprimer les espaces en fin et en début des chaines de caractères
        * convertir les champs score, ranked et popularity en entier ou réel
        * convertir les champs duration et aired en datetime ou en dict de datetime
        * remplir les champs manquant par des None, [] ou {}
        * joindre les lignes du champ synopsis en une seul chaine de caractères
        * supprimer dans les champs comportant des listes des doublons  
    * clean_string() supprime les espaces inutiles dans les chaines de caractères et formate des données manquantes
    * clean_number() convertit les chaines de caractères en entier ou réel
    * clean_duration() convertit les chaines de caractères en datetime
    * find_month() convertit un nom de mois en numéro de mois
    * to_date() construit datetime à partir d'un n° de jour, d'un n° de mois et d'une d'année
    * clean_aired() convertit une chaine de caractères en une date de début et une date de fin

=====================
Fonctions de stockage
=====================
Les fonctions suivantes sont définies dans pipelines.py:
    * open_spider() ouvre la connexion avec le server Mongo
    * close_spider() ferme la connexion avec le server Mongo
    * process_item() enregistre dans la collection myanimelist les scrapy Items néttoyés

NB: Pour obtenir des informations complémentaires sur les fonctions énoncées ci-dessus, consulter leurs 
doctypes dans leurs scripts respectifs.
