# Commandes Vocales pour NVDA

Exécutez des commandes NVDA en parlant plutôt qu'en appuyant sur des touches.

NVDA possède déjà une description pour chaque commande dans sa boîte de dialogue Gestes de commandes. Commandes Vocales écoute via votre microphone, convertit votre parole en texte grâce au moteur hors ligne ([Vosk](https://alphacephei.com/vosk/) par défaut, ou un modèle [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) que vous choisissez, voir Le modèle vocal), compare ce texte aux descriptions (ainsi qu'aux phrases que vous définissez vous-même), puis exécute la commande la plus appropriée. Votre voix est traitée sur votre ordinateur et n'en sort jamais.

## Comment ça fonctionne

1.  Lorsque vous commencez l'écoute, l'extension collecte les commandes qui sont disponibles pour le moment. Cela inclut les commandes de l'application dans laquelle vous travaillez, une commande propre à une autre application ne sera donc proposée que si celle-ci a le focus.
2.  Vous parlez, puis vous arrêtez l'écoute. Le moteur vocal convertit votre parole en texte.
3.  Le texte est comparé aux descriptions de commandes et à vos propres phrases. Le système de reconnaissance est également informé des phrases attendues, ce qui le rend beaucoup plus précis que la dictée libre. Les modèles sherpa ne peuvent pas être limités de cette manière: ils écrivent du texte ordinaire, donc l'extension le compare de manière plus stricte (voir Choisir quoi dire).
4.  Si une commande correspond clairement, elle s'exécute. Si plusieurs commandes correspondent de manière équivalente, une liste s'ouvre pour vous laisser choisir.

## Configuration requise

- NVDA 2026.1 o ultérieur, version 64 bits, sous Windows.
- Un microphone configuré comme périphérique d'enregistrement par défaut sous Windows.
- Une connexion Internet pour une seule fois pour télécharger le modèle vocal (un petit modèle Vosk pèse environ 40 à 100 Mo ; les modèles Sherpa pèsent de 24 à 124 Mo, plus une mémoire d'exécution de 21 Mo qu'ils partagent tous).

## Installation et première exécution

1.  Ouvrez le fichier `.nvda-addon` et confirmez l'installation. Redémarrez NVDA lorsque cela vous est demandé.
2.  Quelques secondes après le démarrage de NVDA, l'extension détecte qu'aucun modèle vocal n'est installé et vous demande l'autorisation d'en télécharger un pour votre langue NVDA. Avec un NVDA turc, il s'agit du modèle turc-stt ; pour les autres langues, il s'agit du modèle Vosk. Choisissez **Oui**. Le téléchargement s'effectue en arrière-plan; NVDA annonce la progression et vous informe lorsque les commandes vocales sont prêtes.

Si vous choisissez **Non**, l'extension ne vous posera plus la question au démarrage. On vous posera à nouveau la question lorsque vous commencerez à écouter ou lorsque vous choisissez un modèle qui n'est pas installé dans la boîte de dialogue du modèle vocal (voir Le modèle vocal).

## Démarrage rapide

Aucune touche n'est assignée par défaut, choisissez les vôtres:

1.  Ouvrez le menu NVDA, puis Préférences, puis Gestes de commandes.
2.  Développez la catégorie **Commandes Vocales** et assignez une touche à **Démarre l'écoute d'une commande vocale**. Assignez également des touches aux autres commandes si vous le souhaitez.

Sans touches, vous pouvez également utiliser le menu Outils (voir Le menu Outils).

Ensuite, pour donner une commande vocale:

1.  Appuyez sur votre touche. Un bip aigu indique que l'écoute a commencé.
2.  Prononcez la commande.
3.  Appuyez à nouveau sur la touche, ou restez simplement silencieux un instant (environ une seconde) après avoir parlé. Un bip grave indique que l'écoute est terminée, et la commande s'exécute.

L'arrêt après silence peut être désactivé avec la commande des Gestes de commande « Active ou désactive l'arrêt automatique de l'écoute lorsque vous restez silencieux après avoir parlé » (ou dans le menu Outils). Pour modifier la durée de silence requise, définissez `silence_seconds` (de 0.5 à 5, 1.2 par défaut) dans `settings.json`.

Si rien n'est reconnu, NVDA dit "Pas compris". Si ce qu'il a entendu ne correspond à aucune commande suffisamment bien, NVDA dit "Aucune commande correspondante" et nomme la plus proche, ou ouvre une liste de candidats (voir En cas d'incertitude).

## Le menu Outils

Ouvrez le menu NVDA, puis Outils, puis **Commandes Vocales** pour utiliser l'extension sans assigner de touches:

- **Démarrer ou arrêter l'écoute** fonctionne comme la touche: choisissez-le une fois pour démarrer et une seconde fois pour arrêter. Utiliser une touche est plus rapide, car il faut ouvrir le menu à chaque fois.
- **Éditeur de phrases de commande...** ouvre l'éditeur de phrases.
- **Enseigner la dernière phrase prononcée...** ouvre la boîte de dialogue pour les noms que le système de reconnaissance ne connaît pas.
- **Mes commandes...** ouvre la boîte de dialogue pour vos propres commandes.
- **Activer ou désactiver l'atténuation du volume** active ou désactive l'atténuation du volume des autres applications.
- **Activer ou désactiver l'arrêt après silence** active ou désactive l'arrêt de l'écoute après un silence.
- **Modèle vocal...** ouvre la boîte de dialogue permettant de choisir, télécharger et gérer le modèle vocal (voir Le modèle vocal).
- **Saisissez une commande...** ouvre une boîte de dialogue dans laquelle vous pouvez saisir une phrase de commande.

Ces commandes font la même chose que les commandes de la boîte de dialogue Gestes de commandes (voir Référence des commandes).

## Choisir quoi dire

Les descriptions de NVDA sont souvent des phrases complètes, par exemple "Annoncer la ligne courante sous le curseur d'application. Deux appuis: épeler la ligne." Vous n'avez pas besoin de tout dire.

| Ce que vous dites                                                                                           | Ce à quoi vous attendre                                                                     |
|--------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| La première phrase de la description, comme "Annoncer la ligne courante sous le curseur d'application" | Fonctionne généralement bien. Pour beaucoup de commandes, la première phrase constitue toute la description. |
| Une courte phrase que vous avez définie dans [l'éditeur de phrases](#your-own-phrases), comme "lire ligne"              | Exacte et très fiable. **Recommandée pour les commandes que vous utilisez quotidiennement.**   |
| Une courte paraphrase personnalisée non définie nulle part, comme "lire la ligne actuelle"           | Moins fiable. Cela peut ouvrir la liste ou correspondre à une commande similaire.           |

Deux choses aident dans la pratique. Prononcez la phrase à un rythme régulier, dans un moment de calme, et n'omettez pas les mots distinctifs. Et définissez également des phrases courtes pour les commandes que vous utilisez le plus souvent: cela ne prend qu'une minute et rend tout plus rapide.

**Avec un modèle sherpa** (voir Le modèle vocal) vous pouvez prononcer une commande plus naturellement, car le texte est comparé à la commande dans les deux sens: les mots que vous avez dits doivent se trouver dans la commande, et les mots de la commande doivent se trouver dans ce que vous avez dit. Les mots supplémentaires tels que "s'il vous plaît" sont tolérés. Un fragment qui correspond exactement à une commande l'exécute également, par exemple "musique" pour votre propre commande "Ouvrir le dossier musique" lorsqu'aucune autre commande ne contient ce mot; un fragment qui correspond à plusieurs commandes ouvre une liste, et les fragments de moins de quatre lettres sont ignorés. Une orthographe ou un espacement différent, tel que "masa üstünü göster" pour "Masaüstünü göster", fonctionne également lorsqu'une commande est clairement la plus proche par le son. Les textes qui ne ressemblent à aucune commande ne sont pas interprétés; NVDA indique à la place ce qu'il a entendu, par exemple "Entendu: merci. Aucune commande correspondante".

## Vos propres phrases

Utilisez l'éditeur de phrases pour prononcer les commandes à votre façon. Assignez une touche à **Ouvre la boîte de dialogue permettant de modifier les phrases (alias) utilisées pour les commandes** et ouvrez-le depuis l'application dont vous souhaitez modifier les commandes.

1.  Dans **Rechercher des commandes**, saisissez quelques mots pour filtrer la liste, puis sélectionnez la commande dans **Commandes**.
2.  Saisissez votre phrase dans **Nouvelle phrase** et choisissez **Ajouter une phrase**. Vous pouvez ajouter plusieurs phrases à une même commande. Pour en modifier ou en supprimer une, sélectionnez-la dans **Phrases que vous dites pour cette commande** et choisissez **Modifier la phrase sélectionnée** ou **Supprimer la phrase sélectionnée**.
3.  Décochez **Utiliser également la description d'origine** si la commande ne doit répondre qu'à vos phrases.
4.  Choisissez **Enregistrer**.

Les bonnes phrases sont courtes, deux à quatre mots, et sonnent différemment les unes des autres. Vos phrases sont prioritaires sur les descriptions d'origine, et fonctionnent avec la fonction de répétition ainsi que la liste de candidats, comme n'importe quelle autre commande. L'éditeur affiche les commandes disponibles dans l'application où vous l'avez ouvert, ouvrez-le donc dans une application pour modifier les commandes de cette application.

## Noms inconnus du système de reconnaissance

Le modèle vocal dispose d'un vocabulaire fixe et ne peut pas apprendre de nouveaux mots. Une commande contenant un nom rare ou étranger, comme le nom d'un artiste ou le titre d'une chanson, on l'entendra souvent sous la forme d'autres mots à la sonorité similaire. Par exemple, "Zülfü Livaneli" peut s'écrire comme "gül suyu divane izi". L'extension tente effectivement de faire correspondre ce texte par le son, ce qui fonctionne lorsque le modèle écrit quelque chose proche du nom ("inti ilimani" pour "Inti Illimani"), mais pas lorsqu'il écrit des mots complètement différents. Les modèles sherpas n'ont pas de liste de mots fixe, mais ils peuvent eux aussi écrire un nom inconnu différemment de ce à quoi vous vous attendez.

Si une commande n'est pas reconnue, enseignez à l'extension ce que le système de reconnaissance a entendu:

1.  Prononcez la commande qui a échoué.
2.  Ouvrez le menu Outils, puis Commandes Vocales, puis **Enseigner la dernière phrase prononcée**. Vous pouvez aussi assigner une touche à **Ouvre une boîte de dialogue qui ajoute la dernière phrase entendue par le système de reconnaissance vocale d'une commande de votre choix** dans la boîte de dialogue Gestes de commandes.
3.  La liste en haut affiche les textes produits par le système de reconnaissance, tous cochés. Décochez ceux qui semblent incorrects.
4.  Dans **Rechercher des commandes**, trouvez la commande, sélectionnez-la dans la liste ci-dessous et choisissez **Enregistrer les phrases**.

Les textes cochés sont enregistrés comme phrases de cette commande, exactement comme si vous les aviez saisis dans l'éditeur de phrases, vous pouvez les modifier ou les supprimer ultérieurement. Comme il s'agit de mots que le modèle connaît déjà, la même prononciation est automatiquement retrouvée la prochaine fois. La liste affiche toujours ce que le système de reconnaissance a entendu la dernière fois que vous avez prononcé une commande, qu'elle ait été reconnue ou non, ouvrez donc cette boîte de dialogue immédiatement après un échec. C'est aussi un moyen rapide de voir ce que le système de reconnaissance a fait avec votre voix, sans avoir besoin de consulter le journal NVDA. Les commandes que vous saisissez dans la boîte de dialogue de commandes ne sont pas incluses.

## Partager et sauvegarder vos phrases

L'éditeur de phrases peut enregistrer vos phrases dans un fichier et les charger à nouveau, ce qui vous permet de les sauvegarder, de les transférer sur un autre ordinateur ou de les partager avec d'autres personnes.

- **Exporter des phrases...** (Ctrl+E) enregistre les phrases présentes dans l'éditeur, ainsi que les commandes dont vous avez désactivé la description d'origine, dans un fichier `.json`. Les commandes sans phrase sont exclues.
- **Importer des phrases...** (Ctrl+I) lit le fichier et ajoute vos phrases à l'éditeur. Rien de ce que vous possédez déjà n'est supprimé ni modifié: les phrases que vous avez déjà sont ignorées, pour une commande pour laquelle vous avez déjà des paramètres, votre choix **Utiliser également la description d'origine** est conservé. NVDA vous indique le nombre de modifications importées. Rien n'est enregistré tant que vous ne choisissez pas **Enregistrer** (Ctrl+S), vous pouvez donc d'abord consulter le résultat, puis choisir Annuler pour le supprimer.

Dans l'éditeur de phrases, ces raccourcis fonctionnent peu importe où se trouve le focus.

Le fichier a le même format que `aliases.json` dans le dossier des paramètres des Commandes Vocales (voir Paramètres et données), une copie de ce fichier peut donc aussi être importée. Les phrases sont associées aux commandes par un identifiant indépendant de la langue de l'interface, un fichier créé par l'éditeur fonctionne donc avec n'importe quelle langue NVDA. Un fichier peut également nommer une commande par son texte plutôt que par son identifiant, tel qu'il apparaît dans la liste de l'éditeur: `description - category`, par exemple `Show desktop - Windows commands`. Une telle entrée ne correspond que si NVDA utilise la langue de ce texte. Une phrase pour une commande inexistante sur votre ordinateur, par exemple, une commande d'une application que vous n'avez pas installée est conservée mais ne fait rien tant que cette commande n'existe pas. L'éditeur n'affiche que les commandes disponibles à l'endroit où vous l'avez ouvert, ouvrez-le donc dans une application pour voir les phrases importées des commandes de cette application. Vos propres commandes (voir Vos propres commandes) reçoivent un identifiant différent sur chaque ordinateur, leurs phrases ne sont donc pas conservées; ajoutez plutôt les mêmes phrases aux commandes sur l'autre ordinateur.

**Un ensemble turc tout prêt.** L'extension est fournie avec le `tr-phrases.json` dans son dossier `locale\tr\LC_MESSAGES`: il s'agit de phrases courtes en turc (deux ou trois mots) pour les commandes propres à NVDA et de nombreuses extensions populaires. Importez-le comme n'importe quel autre fichier. Il nomme les commandes d'après leur texte (voir ci-dessus), de sorte qu'il fonctionne avec une version turque de NVDA. Pour une commande pour laquelle vous n'avez aucun paramètre, il désactive également la description longue d'origine, afin que cette commande ne réponde qu'à la phrase courte; réactivez **Utiliser également la description d'origine** dans l'éditeur si vous souhaitez les deux.

## Exclure des commandes du contrôle vocal

Certaines commandes ne doivent jamais être exécutées par la voix, par exemple parce qu'elles sont risquées ("fermer la fenêtre", "verrouiller l'ordinateur") ou parce qu'elles ressemblent trop à d'autres et sont souvent choisies par erreur. Pour en exclure une:

1.  Ouvrez l'éditeur de phrases et sélectionnez la commande, comme décrit dans Vos propres phrases.
2.  Décochez **Utiliser également la description d'origine**, et n'ajoutez aucune phrase personnalisée.
3.  Choisissez **Enregistrer**.

La commande ne fait alors plus partie de ce que l'extension écoute, elle ne sera jamais exécutée, jamais proposée dans la liste des candidats, et sans correspondance par un son. Cela fonctionne toujours avec sa propre touche dans la boîte de dialogue Gestes de commandes. Cela fonctionne pour les commandes NVDA, les commandes Windows intégrées et vos propres commandes. Pour réactiver une commande, sélectionnez-la à nouveau et cochez **Utiliser également la description d'origine**, ou ajoutez une phrase. Vous pouvez également supprimer une commande personnalisée directement dans sa boîte de dialogue.

Exclure une commande améliore la fiabilité de la reconnaissance: moins il y a de commandes parmi lesquelles choisir, moins on risque de confondre une commande similaire avec celle que vous avez prononcée.

## Répéter une commande

Terminez la phrase par un nombre et le mot "fois": "lire la ligne deux fois", "ligne suivante trois fois". Le nombre peut être compris entre deux et cinq, et les chiffres sont également acceptés ("3 fois"). La commande s'exécute autant de fois de suite.

Pour les commandes qui réagissent à des pressions répétées, NVDA comptabilise cela comme des appuis de touches répétés. Par exemple, la commande qui annonce la ligne courante la lit une fois, l'épelle deux fois et donne le code international trois fois. Pour d'autres commandes, comme le déplacement à la ligne suivante, l'effet est simplement que cela se produit plusieurs fois.

## Appuyer sur des touches par la voix

Les commandes de la catégorie Gestes de commandes **Touches émulées du clavier du système** appuient sur une touche du clavier du système pour vous, comme une touche fléchée, Tab ou Échap. Elles fonctionnent comme n'importe quelle autre commande, et la répétition est particulièrement pratique ici: "flèche bas trois fois" appuie sur la touche trois fois. Prononcez le nom de la touche tel qu'il apparaît dans la boîte de dialogue Gestes de commandes. NVDA traite cet appui de la même manière que ses propres touches émulées: il laisse d'abord ses propres commandes gérer la touche, puis la transmet au système.

## Commandes Windows intégrées

La boîte de dialogue Gestes de commandes de NVDA ne liste que les commandes propres à NVDA, l'extension apporte donc son propre ensemble de commandes Windows à l'échelle du système. Vous les prononcez comme n'importe quelle autre commande, par exemple "afficher le bureau", "afficher la barre des tâches", "afficher la zone de notification", "copier" ou "coller". Chacune d'elles appuie simplement sur le raccourci que Windows utilise déjà, donc cela fonctionne dans n'importe quelle application. Les raccourcis se terminant par une lettre (comme Windows+I) sont pressées par le code de touche virtuelle plutôt que par le caractère, Ils sont donc compatibles avec toutes les dispositions de clavier, y compris le turque.

- **Bureau et interface:** afficher le bureau, afficher la barre des tâches, afficher la zone de notification, ouvrir le menu Démarrer, ouvrir l'Explorateur de fichiers, ouvrir la boîte de dialogue Exécuter, ouvrir les paramètres Windows, ouvrir la recherche Windows, ouvrir les paramètres rapides, ouvrir le centre de notifications, ouvrir l'historique du presse-papiers, ouvrir le panneau des émojis, démarrer la dictée vocale de Windows, ouvrir le menu de projection de l'affichage, faire une capture d'écran, ouvrir le Gestionnaire des tâches, verrouiller l'ordinateur.
- **Fenêtres et bureaux virtuels:** réduire toutes les fenêtres, restaurer les fenêtres réduites, afficher la vue des tâches, passer à la fenêtre précédente, fermer la fenêtre, agrandir la fenêtre, réduire la fenêtre, ancrer la fenêtre à gauche ou à droite, bureau virtuel suivant, précédent, nouveau et fermer le bureau virtuel.
- **Son et média:** augmenter le volume, baisser le volume, couper ou rétablir le son, lire ou mettre en pause le média, piste suivante, piste précédente.
- **Édition:** copier, couper, coller, tout sélectionner, annuler, rétablir, enregistrer, rechercher, imprimer, créer un nouveau document, ouvrir un fichier, renommer, propriétés, actualiser.
- **Navigation et onglets:** page précédente, page suivante, nouvel onglet, fermer l'onglet, rouvrir l'onglet fermé, onglet suivant, onglet précédent.

Les commandes pour lesquelles la répétition est pertinente acceptent "deux fois" etc., par exemple "augmenter le volume trois fois" ou "onglet suivant deux fois". Ces commandes apparaissent dans l'éditeur de phrases de commande sous la catégorie **Commandes Windows**, Vous pouvez donc ajouter vos propres phrases ou désactiver leur phrase d'origine. Une commande NVDA ayant la même description est prioritaire. Les descriptions sont traduisibles; ainsi, les phrases que vous prononcez seront dans votre langue.

## Vos propres commandes

Vous pouvez ajouter vos propres commandes. Assignez une touche à **Ouvre la boîte de dialogue permettant d'ajouter vos propres commandes** dans la catégorie Commandes Vocales de la boîte de dialogue Gestes de commandes, appuyez dessus, puis choisissez **Ajouter**. Saisissez ce que vous allez dire, puis choisissez ce que fait la commande:

- **Ouvrir un programme, un fichier, un dossier ou une adresse web:** saisissez-la ou utilisez les boutons pour parcourir. Il s'ouvre comme si vous aviez double-cliqué dessus, une adresse web s'ouvre donc dans votre navigateur. Les variables d'environnement telles que `%USERPROFILE%` fonctionnent, tout comme les noms de dossiers `music`, `documents`, `downloads`, `desktop`, `pictures` et `videos`, ainsi que les adresses `shell:` de Windows. Un programme présent dans le chemin système, comme `notepad`, n'a pas besoin de dossier.
- **Appuyez sur une combinaison de touches:** saisissez les touches en utilisant les noms de touches NVDA, par exemple `control+shift+n`. Les abréviations courantes comme `ctrl`, `win`, `esc` et `left` sont comprises. Ces commandes peuvent être répétées ("deux fois").

Vos commandes sont listées dans l'éditeur de phrases sous la catégorie **Mes commandes**, où vous pouvez ajouter des phrases supplémentaires. Si une de vos commandes porte le même nom qu'une commande NVDA, c'est la vôtre qui est utilisée. Rien ici n'exécute de scripts ou de commandes shell: une commande transmet sa cible à Windows ou appuie sur des touches. Vos commandes sont stockées dans `userCommands.json` dans le dossier des paramètres des Commandes Vocales (voir Paramètres et données).

## En cas d'incertitude

Lorsque plusieurs commandes semblent convenir, ou qu'aucune ne convient suffisamment pour être exécutée seule, la liste des meilleurs candidats s'ouvre. (Avec un modèle Sherpa, la liste ne s'ouvre que lorsque quelque chose ressemble à une commande ; sinon, NVDA dit simplement ce qu'il a entendu.) Utilisez les flèches directionnelles et appuyez sur Entrée pour exécuter la commande souhaitée, ou sur Échap pour annuler. Si vous avez choisi une répétition, elle s'appliquera à la commande choisie.

## Saisir au clavier plutôt que parler

Assignez une touche à **Ouvre une boîte de dialogue dans laquelle vous pouvez saisir une phrase de commande**. Le texte saisi est analysé de la même manière que la commande vocale, ce qui est pratique pour tester des phrases et dans les situations où vous ne pouvez pas parler.

## Référence des commandes

Toutes ces commandes se trouvent dans la boîte de dialogue de Gestes de commandes, dans la catégorie Commandes Vocales.

| Commande                                                                                                                | Ce que cela fait                                                                     |
|------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| Démarre l'écoute d'une commande vocale ; appuyez à nouveau, ou restez silencieux un instant après avoir parlé, pour arrêter l'écoute et exécuter la commande | La commande principale. Appuyez une fois pour démarrer et une seconde fois pour arrêter.                         |
| Ouvre une boîte de dialogue dans laquelle vous pouvez saisir une phrase de commande                                                                        | Exécute la phrase saisie via la même correspondance.                                   |
| Ouvre la boîte de dialogue permettant de modifier les phrases (alias) utilisées pour les commandes                                                   | Ouvre l'éditeur de phrases.                                                         |
| Active ou désactive l'atténuation du volume des autres applications lors de l'écoute d'une commande vocale                                  | Active ou désactive l'atténuation du volume.                                                 |
| Active ou désactive l'arrêt automatique de l'écoute lorsque vous restez silencieux après avoir parlé                                        | Active ou désactive l'arrêt après silence.                                                   |
| Ouvre la boîte de dialogue du modèle vocal: choisissez, téléchargez et gérez le modèle                                                   | Choisissez le modèle vocal, téléchargez-le après confirmation, puis ouvrez le dossier du modèle. |
| Ouvre une boîte de dialogue qui ajoute la dernière phrase entendue par le système de reconnaissance vocale d'une commande de votre choix                     | Enseigne à l'extension un nom qu'elle ne reconnaît pas.                                 |
| Ouvre la boîte de dialogue permettant d'ajouter vos propres commandes: ouvrir un programme, un fichier, un dossier ou une adresse Web, ou appuyer sur une combinaison de touches | Ouvre la boîte de dialogue pour vos propres commandes.                                          |

## Atténuation du volume des autres applications

La musique et les vidéos seraient captées par le microphone et perturberaient le système de reconnaissance. Pendant l'écoute, le volume de toutes les sessions audio, à l'exception de celle de NVDA, est atténué à 20% de son volume, et il est rétabli lorsque vous l'arrêtez. Une session dont vous modifiez vous-même le volume entre-temps reste inchangée.

Windows mémorise les volumes de chaque application, l'extension enregistre donc également un petit fichier de récupération. Si NVDA se ferme pendant que le volume est atténué, les volumes d'origine sont rétablis au prochain démarrage de NVDA.

Cette fonctionnalité utilise une bibliothèque fournie avec NVDA. Si cette bibliothèque est absente, l'écoute fonctionne toujours, mais sans atténuer le volume de quoi que ce soit. Vous pouvez le désactiver avec la commande à bascule.

## Le modèle vocal

Ouvrez **Modèle vocal...** dans le menu Outils, ou assignez une touche à **Ouvre la boîte de dialogue du modèle vocal: choisissez, téléchargez et gérez le modèle**. La boîte de dialogue répertorie les modèles disponibles pour la langue de votre NVDA et indique pour chacun d'eux s'il est en cours d'utilisation, installé ou non installé.

- **Utiliser** bascule vers le modèle sélectionné (un double-clic sur un modèle fait de même). Un modèle qui n'est pas installé est d'abord téléchargé: l'extension vous indique sa taille, sa provenance et sa licence, et ne le télécharge qu'après votre accord. Le modèle ne peut pas être modifié pendant l'écoute ou lorsqu'un téléchargement est en cours.
- **Ouvrir le dossier du modèle** ouvre le dossier où sont conservés les modèles, pour installer un modèle manuellement.

| Modèle                                     | Langues                                        | Téléchargement              | Licence                                                         |
|-------------------------------------------|--------------------------------------------------|-----------------------|-----------------------------------------------------------------|
| Vosk (petit modèle)                        | Chaque langue qui en possède un sur la liste officielle | Généralement 40 à 100 Mo  | Voir la liste des modèles                                              |
| turkish-stt (mihu AI)                     | Turc                                          | 68 Mo                 | Licence communautaire mihu (gratuit pour un usage personnel)                  |
| Kroko English, Français, Deutsch, Español | Anglais, français, allemand, espagnol                 | 57, 57, 58 et 124 Mo | Modèle communautaire Kroko ; conditions sur huggingface.co/Banafo/Kroko-ASR |
| Zipformer ru (Alpha Cephei)               | Russe                                          | 24 Mo                 | Voir huggingface.co/alphacep/vosk-model-small-streaming-ru       |

**Vosk ou un modèle sherpa.** Vosk est limité à la liste de commandes, ce qui convient aux commandes courtes. Les modèles sherpa écrivent du texte libre, ce qui s'adapte généralement mieux à la parole ordinaire et aux mots inconnus, mais correspond plus strictement aux commandes (voir Choisir quoi dire). Essayez les deux et conservez celui qui fonctionne le mieux avec votre voix et votre microphone. La valeur par défaut est turkish-stt pour un NVDA en turc qui n'a pas encore de modèle Vosk installé ; un modèle Vosk installé n'est jamais remplacé à votre insu, et toutes les autres langues restent sur Vosk jusqu'à ce que vous choisissiez un modèle sherpa. Votre choix est mémorisé. Si NVDA bascule vers une langue que le modèle sherpa choisi ne prend pas en charge, l'extension se rabat sur Vosk.

**Installer un modèle sherpa.** Le premier modèle sherpa nécessite également le runtime sherpa-onnx (trois fichiers DLL, 21 Mo). Il est téléchargé depuis github.com, toujours dans la même version, et vérifié par rapport à une somme de contrôle fixe ; les fichiers du modèle proviennent de huggingface.co ou github.com et sont également vérifiés. Le runtime est conservé dans `voiceCommands\sherpa-runtime` et chaque modèle dans son propre dossier `sherpa-...` à l'intérieur de `voiceCommands\model`. Le runtime nécessite NVDA en version 64 bits. Si votre nom d'utilisateur Windows contient des lettres telles que ş, ğ ou ı, l'extension utilise le nom court (8.3) du dossier, que certains disques ont désactivé (voir Dépannage).

**Modèles Vosk.**

- L'extension recherche le modèle dans le dossier `voiceCommands\model` situé dans le dossier de configuration de NVDA, par exemple `%AppData%\nvda\voiceCommands\model`. **Ouvrir le dossier du modèle** dans la boîte de dialogue vous y amène directement.
- Le téléchargement automatique utilise la liste officielle des modèles disponible sur <https://alphacephei.com/vosk/models>. Il sélectionne un petit modèle pour votre langue NVDA, vérifie sa somme de contrôle et l'extrait dans ce dossier.
- Pour installer un modèle vous-même, téléchargez-en un modèle sur cette page et extrayez-le dans le dossier model. Les deux dispositions du modèle Vosk sont reconnues, et les fichiers peuvent être dans un sous-dossier.
- Les grands modèles sont plus précis mais ils nécessitent beaucoup plus de mémoire et leur chargement est plus long.
- S'il n'existe pas de modèle prêt pour votre langue,, l'extension vous propose d'ouvrir la page des modèles.

## Paramètres et données

Stockés dans `%AppData%\nvda\voiceCommands`, ou dans le dossier de configuration d'un NVDA portable:

| Élément                    | Contenu                                                                                                                |
|-------------------------|-------------------------------------------------------------------------------------------------------------------------|
| `aliases.json`          | Vos phrases issues de l'éditeur de phrases et la boîte de dialogue enseigner.                                                               |
| `userCommands.json`     | Vos propres commandes.                                                                                                      |
| `settings.json`         | Si l'atténuation du volume est activée, s'il faut demander confirmation du téléchargement au démarrage, si l'écoute s'arrête après un silence et au bout de combien de temps, et le moteur vocal et le modèle que vous avez choisis. |
| `ducking-recovery.json` | Temporaire: existe uniquement pendant que le volume des autres applications est atténué, pour le restaurer après un plantage.                        |
| `model\`                | Les modèles vocaux: les modèles Vosk et les dossiers `sherpa-...`.                                                            |
| `sherpa-runtime\`       | Le runtime sherpa-onnx, téléchargé en même temps que le premier modèle sherpa.                                               |

Les valeurs en haut de `globalPlugins/voiceCommands/__init__.py`, tels que les seuils de correspondance et la taille de la liste des candidats, vous pouvez les modifier si vous souhaitez en ajuster le comportement.

## Dépannage

| Problème                                        | Que vérifier                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "Modèle Vosk introuvable"                         | Installez un modèle comme décrit ci-dessus. Le message indique le nom exact du dossier.                                                                                                                                                                                                                                                                                                                                                                                                    |
| "Le moteur vocal sélectionné n'est pas installé"  | Ouvrez **Modèle vocal...** et choisissez **Utiliser**: l'extension propose de le télécharger à nouveau. Si cela continue d'échouer, supprimez le dossier du modèle sous `model\` et le dossier `sherpa-runtime`, puis téléchargez à nouveau.                                                                                                                                                                                                                                                                 |
| "Impossible de charger le modèle" avec un modèle sherpa | Assurez-vous que NVDA est en version 64 bits. Si votre nom d'utilisateur Windows contient des lettres telles que ş, ğ ou ı, le modèle peut ne pas se charger lorsque les noms de dossiers courts sont désactivés sur le lecteur ; vérifiez le journal (voir ci-dessous) et utilisez Vosk si le problème persiste.                                                                                                                                                                                                                                               |
| "Entendu: ... Aucune commande correspondante"               | Un modèle sherpa a généré un texte dont les mots ne correspondent à aucune commande. Si le texte correspond à ce que vous avez dit, la commande s'appelle autrement : ajoutez votre propre phrase courte (voir Vos propres phrases). Sinon, répétez-la ou essayez un autre modèle.                                                                                                                                                                                                                                          |
| Rien n'est reconnu                          | Assurez-vous que le microphone approprié est bien le microphone par défaut de Windows et qu'il n'est pas coupé.                                                                                                                                                                                                                                                                                                                                                                                                       |
| Un nom n'est jamais reconnu                     | Le modèle peut l'écrire comme d'autres mots. Ouvrez **Enseigner la dernière phrase prononcée** juste après l'avoir dit pour voir ce qui avait été entendu, et enregistrez-le comme une phrase (voir Noms inconnus du système de reconnaissance).                                                                                                                                                                                                                                                                                |
| La mauvaise commande s'exécute                         | Définissez une courte phrase personnalisée pour cette commande dans l'éditeur de phrases.                                                                                                                                                                                                                                                                                                                                                                                                   |
| "Cette commande n'est pas disponible pour le moment"      | La commande appartient à une autre application. Dites-le pendant que cette application a le focus.                                                                                                                                                                                                                                                                                                                                                                                       |
| La musique ou la vidéo continue d'interférer           | Certaines applications n'exposent pas de session audio qui puisse être atténué. Mettez-les en pause avant d'écouter.                                                                                                                                                                                                                                                                                                                                                                         |
| Vous voulez voir ce qui a été entendu                 | Ouvrez **Enseigner la dernière phrase prononcée** juste après avoir parlé: sa liste affiche les textes produits par le système de reconnaissance. Pour plus de détails, définissez le niveau de journalisation de NVDA sur Débogage(Menu NVDA, Préférences, Paramètres, Confidentialité et sécurité, Niveau de journalisation), parlez et ouvrez le journal (NVDA+F1): les lignes "Voice command recognition" montrent ce que chaque système de reconnaissance a entendu, et les lignes "Voice command candidate" montrent à quel point les meilleures coïncidences étaient proches. Ces lignes ne sont écrites qu'au niveau Débogage. |

## Confidentialité

Le son du microphone est traité sur votre ordinateur par le moteur vocal (Vosk ou sherpa-onnx) et n'est jamais envoyé nulle part. Le réseau est utilisé uniquement lorsque vous autorisez le téléchargement du modèle, et uniquement pour se connecter à alphacephei.com (modèles Vosk), huggingface.co (le modèle turkish-stt) et github.com (le runtime sherpa-onnx et les autres modèles sherpa).

## Traduction

L'extension est écrite en anglais et est fournie avec une traduction turque. Pour la traduire, copiez `voiceCommands.pot` dans `locale/<langue>/LC_MESSAGES/nvda.po` et traduisez les messages; chacun contient un commentaire à l'intention des traducteurs. Les mots utilisés pour répéter une commande ("two times") sont également traduisibles, pour une prononciation naturelle dans votre langue.

## Licence

Commandes Vocales est distribué sous la Licence Publique Générale GNU, version 2.

Le runtime sherpa-onnx que l'extension télécharge est distribué sous la licence Apache 2.0, et la bibliothèque ONNX Runtime qu'il contient est sous la licence MIT. Chaque modèle vocal a sa propre licence (voir Le modèle vocal).