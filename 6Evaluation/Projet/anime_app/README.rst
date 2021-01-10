=========
anime_app
=========

==================
Structure générale
==================

L'application web se compose deux onglets: Advance search et Recommendation.

Le premier onglet permet de réaliser des recherches avancés d'animés en les filtrant par:
    * leurs genres
    * leur première date de diffusion
    * leur statut
    * leur type
    * leur durée par épisode
    * l'âge de leur public
    * leurs studios de production
    * leur score
    * leur nombre d'épisodes

Le second onglet recommande à l'utilisateur un certain nombre d'animés 
en se basant sur des titres que ce dernier à apprécier.

Dans ces deux onglets, les animés proposés sont classés selon leur score et leur popularité sur le site https://myanimelist.net/.

=====================
Onglet Advance search
=====================

Cette onglet comporte un certain nombre de slider, dropdowns et checklist que l'utilisateur
peut utiliser afin de personaliser sa recherche d'animés.
Ce dernier lance la recherche en appuyant sur le bouton submit situé en dessous du filtre de genres.

Les résultats de la recherche réalisée s'afichent dans les cases situées en dessous de ce bouton.
Afin de faire défiler les animés sélectionnés par l'ordinateur, l'utilisateur peut utiliser les boutons
next et back situés à gauche du bouton submit.

=====================
Onglet Recommendation
=====================

Dans cette onglet, l'utilisateur doit saisir dans la barre situé en haut de son écran les titres d'animés 
qu'il a déjà vus et appréciés. Il doit ensuite appuyer sur le bouton submit situé à gauche de cette barre 
afin de lancer l'algorithme de recommendation.

En dessous de cette barre de saisi, l'utilisateur peut régler le nombre maximale de d'animés que l'ordinateur
peut lui proposer (plus ce dernier est plus faible plus l'algorithme de recommandations sera sélectif).
L'utilisateur peut également choisir de voir la totalité des animés que l'ordinateurs peut lui proposé
en cochant la case "See all results". L'ordinateur va alors lui sélectionner parmi l'ensemble des animés
qu'il connait tous ceux qui partage au moins un leurs genres avec ceux saisies plus haut.

Tout comme l'onglet Advance search, les recommandations apparaitront dans les cases situées en bas de page.
Les boutons next et back seront eux aussi présents afin de faire défiler les animés recommandés.

====================
Contenu de anime_app
====================

Ce répertoire contient :
    * assets est le dossier comportant les éléments CSS et les images utilisés dans la mise en page de l'application
    * app.py définit les strutures de chaque onglets et les modlaités de mise à jour de ces derniers
    * controls.py contient les fonctions contenant les valeurs et labels utilisés pour construire les dropdowns, sliders et checklist de l'UI. Il contient aussi les fonctions requêtant la BDD d'animés et celles créant le contenu des cases de résultats.
    * requirements.txt contient la liste des packages nécessaires pour faire tourner l'application dans son containers
    * Dockerfile définissant l'image utilisée pour construire le container anime_app

======================
Fonctions de requêtage
======================
Les fonctions suivantes sont dans controls.py:
    * make_request() construit à partir des valeurs des sliders, des dropdowns et  des checklists de l'UI une requête MongoDB. Les champs concernés par les requêtes générées par cette fonction sont: le titre principal, les titres alternatifs, les genres, le type, le statut, les studios de productions, l'année de la première diffusion, le nombre d'épisodes, la durée par épisode et le score.
    * select_anime() exécute la requête qu'on lui donne en argument en triant les éventuellement les résultats selon leur score et leur popularité.
    * clean_selection() supprime dans une sélection d'animés les animés liés entre eux. Dans un ensemble d'animés reliés entre eux, seul l'un d'entre eux est conservé dans la liste.
    * find_references() extrait et met en forme les informations des animés appréciés par l'utilisateur pour l'algorithme de Recommendation
    * anime_Recommendation() renvoie une liste d'animés recommandés à l'utilisateur suivant les titres qu'il a saisie au prélable dans l'UI. On passe à cette fonction un nombre maximal de recommandations afin qu'elle ajuste la complexité de la requête (tant que le nombre de recommandatiobs n'est pas inférieur à ce nombre, on ajoute des champs à la requête). Les champs concernés sont: les genres, la durée par épisode, le nombre d'épisodes et l'année de la première diffusion. Le filtre de genres qui est présent par défaut à également plusieurs niveaux de complexité suivant le nombre de genres (1,2,....n) partagés entre les animés recommandés et les animés appréciés (couvrant n genres distincts).
    * partieliste() détermine les différents sous-ensembles issus de la liste passée en argument. Cette fonction est utilisée afin de construire les requêtes fitrant les genres dans anime_Recommendation().
    * to_time() convertit des durées en secondes en datetime.time ou datetime.datetime. Cette fonction est appelée par anime_recommendation() lors que la crétion du filtre sur le champs duration.

=====================
Fonctions d'affichage
=====================
Les fonctions suivantes sont dans controls.py:
    * init_component() crée les labels et les valeurs des dropdowns, sliders et checklists de l'UI de l'onglet Advance search. Elle se base sur les valeurs maximales et minimales que peuvent prendre les champs de la base mongo suivant: type, âge du public, statut, durée d'un épisode, nombre d'épisodes, première année de diffusion, genres, studios de production.
    * print_infos() met en forme la chaine de caractère contenant les informations relatives à un animé sélectionné dans la BDD.

Les fonctions suivantes sont dans app.py:
    * build_banner() crée la bannière commune aux deux onglets de l'application
    * build_tabs() crée les deux onglets Advance search et Recommendation
    * build_advance_search() définit la structure de l'onglet Advance search
    * build_recommendation() définit la structure de l'onglet Recommendation

========================
Fonctions de mise à jour
========================
Les fonctions suivantes sont dans app.py:
    * update_drop() met à jour le format des dropdowns selon les valeurs sélectionnés. Quand une valeur "All \*" est sélectioné, elle désactive la possibilité de saisir plusieurs valeurs dans le dropdown correspondant. Cette fonctionnalité est rétablit dès que "All \*" n'est plus sélectionné.
    * render_tab() affiche uniquement à l'écran l'onglet sélectionné par l'utilisateur
    * print_advance_search_result() met à jour les résultats de la recherche avancé d'animés quand submit est appuyé. Elle permet de faire défiler les résultats de la recherche précendente par un appui sur back ou next.
    * print_Recommendation_result() met à jouor la liste de recommandations quand submit est appuyé et de faire défiler les résultats par u appuie sur next ou back.

NB: Pour avoir davantage d'informations sur les fonctions précedemment citées consulter leurs doctypes 
et leurs commentaires dans leur scripts respectifs. 



