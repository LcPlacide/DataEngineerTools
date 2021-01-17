===================
Lancement du projet
===================

Se placer dans le répertoire DataEngineerTools/6Evaluation/Projet et lancer les containers

.. code-block:: bash

    docker-compose up -d
    
Pour vérifier qu'ils tournent correctement, on utilise la commande:

.. code-block:: bash

    docker-compose ps

Pour consulter l'application web, on se rend à l'url http://localhost:8050/home

On stoppent les containers avec la commande:

.. code-block:: bash

    docker-compose down
    
NB: L'application est fourni avec un BDD d'animés complète l'exécution d'animescrawler n'est pas obligatoire.
Cependant, si vous souhaitez mettre à jour cela prendra environ un demi-heure selon votre connexion internet.

==============================
Mise à jour de la BDD d'animés
==============================

Se placer dans le répertoire DataEngineerTools/6Evaluation/Projet et lancer les containers

Ouvrir le jupyter notebook dans un navigateur en se rendant à l'url http://localhost:8888/

Ouvrir le notebook animescrawler.ipynb situé dans le répertoire animescrawler et exécuter sa première cellule.

Relancer les containers afin de les mettre à jour

NB: En cas de problèmes, la seconde cellule de ce notebook permet de charger la BDD original
à partir d'un json fourni avec l'application. Pour plus d'information consulter le readme du répertoire animescrawler.
