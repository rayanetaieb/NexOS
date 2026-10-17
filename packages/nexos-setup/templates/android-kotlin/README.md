# Modèle Android Kotlin NexOS

Projet minimal (une activité, un test unitaire, aucune dépendance hors SDK) copié par
`nexos-setup android --new-project` dans `~/AndroidStudioProjects/BonjourNexOS`.

- Ouvrir le dossier dans Android Studio ; Gradle 8.11.1, Android Gradle Plugin 8.7.3,
  Kotlin 2.1.0, compileSdk 35 (Android Studio propose la mise à niveau si plus récent).
- Le wrapper Gradle (`gradlew`, `gradle-wrapper.jar`) est généré par Android Studio au premier
  import ; il n'est pas inclus (binaire téléchargé depuis services.gradle.org).

**État de vérification** : la construction Gradle (APK) n'a
**pas** pu être exécutée dans l'environnement de construction de NexOS (services.gradle.org,
maven.google.com et dl.google.com y sont bloqués). À valider sur une machine connectée.
