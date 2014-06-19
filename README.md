# BronyCUB IRC Bot #

## Qu'est-ce que c'est ? ##
	Berry-punch est un 'bot' irc, c'est-à-dire un client
[irc](http://fr.wikipedia.org/wiki/Internet_Relay_Chat) autonome : concrètement,
c'est un programme qui permet d'administrer un canal (gestion des droits
utilisateurs, modération…) et aussi de divertir (phrases amusantes, réaction
aux messages des utilisateurs…)

## Installation/démarrage ##
### Dépendances logicielles ###
Pour pouvoir fonctionner, ce bot a besoin :  
- De GNU Bash (version 4.3 minimum)
- De GNU Netcat ( /!\ pas la version BSD)
- Des outils UNIX standard: grep, sed, cat… (version GNU recommandée, les paquets se nomment coreutils et util-linux généralement sous GNU/Linux)

### Procédure ###
Il suffit de récupérer le contenu du projet, de le poser quelque part et de lancer
le script principal (SHBot.sh).

Au démarrage, le bot demande un utilisateur/mot de passe.
Il s'agit du nick du bot (le pseudo sur IRC, Berry-Punch dans notre cas) et du mot
de passe associé à ce pseudo.

Ensuite, le bot se connecte au canal et est opérationnel.

## Commandes à connaitre ##
Les commandes sont préfixées par défaut de '!' (modifiable).
Pour connaître la liste des commandes disponibles : !list
Pour obtenir une aide sur chaque commande : !help <commande>
