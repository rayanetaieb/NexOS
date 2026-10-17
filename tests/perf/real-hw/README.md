# Comparaison sur PC réel

Les comparaisons faites en machine virtuelle (docs/COMPARISON.md) ne mesurent ni la vitesse réelle,
ni l'autonomie. Pour comparer NexOS à Windows ou à une autre distribution sur **le même PC** :

1. Démarrer le système, ouvrir la session, ne rien lancer.
2. Linux : `sh collect-linux.sh > rapport.txt` — Windows (PowerShell administrateur) :
   `powershell -ExecutionPolicy Bypass -File collect-windows.ps1 > rapport.txt`
3. Le script attend 2 minutes de repos puis note : mémoire utilisée (même définition sur les deux :
   totale − disponible), nombre de processus, espace disque du système, durée du dernier démarrage.
4. Répéter 3 fois par système et garder la médiane.

**Pas encore testé** : `collect-windows.ps1` n'a pas pu être exécuté (pas de Windows dans l'environnement
de développement) ; `collect-linux.sh` est vérifié en machine virtuelle.
