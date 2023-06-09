# Case-BE-Tapio

Dans ce rapport je vais détailler les différents choix fait pour la réalisation de ce case, la solution élaborée ainsi que les améliorations principales effectuée par rapport à ma précédente solution.

## Commandes

Voici la liste des différentes commandes :
- **Ajouter une migration en DB :** python3 manage.py makemigrations 
- **Exécuter les migrations :** python3 manage.py migrate
- **Run le projet :** python3 manage.py runserver
- **Peupler la DB :** python3 manage.py loaddata dummy db.json
- **Lancer les test unitaires :** python3 manage.py test api

## Hypothèses et choix d'implémentation

1. **Le calcul des émissions totales**

Les émissions totales d’un rapport sont la somme des  émissions totales des sources appartenant à celui-ci.

Pour calculer la somme totale des émissions d’une source, j’ai fait le choix d’additionner les différents amortissements de la sources ainsi que de ses modifications. Je calcule les amortissements en prenant l’attribut *total_emission* que je divise pas le *lifetime*. Si une année a été spécifiée en paramètre, j’additionne également les émissions d’utilisation de la source. Ces émissions correspondent à la *value* multipliée par l’*emission_factor*. 

Lorsqu'une source contient des modifications, on ajoute l'amortissement de la modification en question. De plus, contrairement à ma première solution, on ne modifie pas la valeurs des champs *value* et *emission_factor* de la source, lorsqu’une modification est ajoutée. Grace à cela on peut garder trace des valeurs originale de la source. Mais cela implique une modification du calcul des émission d'usage de la source. Lorsqu'une modification est appliquée, on prend en compte les valeurs fournies par celle-ci.

2. **Le calcul des deltas**

Le calcul des deltas est la partie qui a été la plus modifiée par rapport à ma première solution. Ici j'ai décidé de ne pas recalculer les émissions totales pour les différentes années, mais plutôt de récupérer les dernières modification directement et de calculer le delta grace à celles-ci. Cela augmente l'efficacité du programme, mais cela nécessite que la liste des modifications soit triée en fonction de l'*acquisition_year*.

3. **Les endpoints**


Lorsqu’un id est spécifié pour un report ou une source, le paramètre *year* peut être ajoute afin de récolter les informations pour une année spécifique. On peut également ajouter le paramètre *to* qui permet de preciser une période.

- Report :
  - /api/reports
  - /api/reports/report id 
- Source :
  - /api/sources
  - /api/sources/source id

Exemple : http://127.0.0.1:8000/api/source/100/?year=2022&to=2025

## Améliorations effectuées 

Tout d’abord j'ai ajouté une suite de tests qui permet de vérifier plus facilement les modèles ainsi que leurs fonctions *get_total_emissions* et *get_delta*.

Ensuite comme mentionné ci-dessus j'ai modifié l'utilisation du modèle *Modification* qui permet de garder trace des valeurs initiales de la source, mais aussi qui facilite et optimise le calcul du delta.

J'ai également suivi votre conseil, et désormais je charge la liste complètes des modifications concernées par un rapport, et ensuite je le filtre en fonction de la source. Cela permet de ne faire qu'un seul appel en base de données pour récupérer les modifications.

Concernant les serializers, j'ai laissé l'entièreté des champs du dictionaire, ce n'est pas indispensable, mais cela me permet de vérifier facilement la valeur des différents champs lors du dévelopement et de mes tests.