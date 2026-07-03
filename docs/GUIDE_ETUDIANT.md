# Guide étudiant : Comprendre et réaliser le projet AI Study Guide Generator

Ce document explique, avec des mots simples, ce que demande chaque tâche du
projet, pourquoi elle existe, et ce qu'il faut concrètement produire. Il
s'appuie sur l'implémentation réelle présente dans ce dépôt (dossier
`agents/`, `tools/`, `main.py`, etc.) pour donner des exemples concrets.

Ne copie pas ce projet tel quel : utilise-le comme référence pour comprendre
la logique, puis écris ton propre code.

---

## Idée générale du projet

On construit un petit système d'agents IA qui reçoit un sujet de
programmation (ex : "Python decorators") et qui génère un guide d'étude
complet au format Markdown, avec :

- une explication simple,
- les concepts clés,
- un exemple de code,
- un exercice pratique,
- des erreurs courantes,
- des commentaires de relecture,
- un résumé final.

Le système n'est pas "un seul gros prompt". C'est plusieurs agents, chacun
avec un rôle précis, qui se passent le travail les uns aux autres, plus des
petites fonctions Python "normales" (pas d'IA dedans) qui font les tâches
mécaniques comme écrire un fichier ou vérifier qu'une section existe.

---

## Tâche 0 : Créer la structure du projet

**Ce qu'on te demande :** créer les dossiers et fichiers vides qui vont
accueillir le code, avant même d'écrire la logique.

**Pourquoi :** si tout le code est dans un seul fichier, le projet devient
vite illisible. En séparant `agents/`, `tools/`, `data/`, `output/` dès le
départ, chaque partie du système a un endroit clair où vivre.

**Ce que tu dois faire concrètement :**

- Créer les dossiers `agents/`, `tools/`, `output/`, `data/`.
- Créer les fichiers `README.md`, `requirements.txt`, `.env.example`,
  `.gitignore`, `main.py` à la racine.
- Ajouter `.env` dans `.gitignore` (jamais commiter de vraies clés ou
  configurations locales).
- Optionnel : ajouter des `__init__.py` vides dans `agents/` et `tools/`
  pour pouvoir les importer comme des packages Python (`from agents.x import
  y`).

Tu n'as pas besoin d'écrire la logique tout de suite. Juste la structure.

---

## Tâche 1 : Installer et configurer le modèle local

**Ce qu'on te demande :** faire fonctionner un modèle de langage **en
local** sur ta machine, sans dépendre d'une API payante.

**Pourquoi cette architecture en 3 couches :**

```
Google ADK  →  LiteLLM  →  Ollama  →  Modèle local
```

- **Ollama** fait tourner réellement le modèle sur ta machine (comme un
  petit serveur local).
- **LiteLLM** est une couche de traduction : elle permet à ton code Python
  de parler à Ollama (ou à OpenAI, Gemini, etc.) avec la même syntaxe,
  peu importe le fournisseur.
- **Google ADK** est le framework qui gère les agents (rôle, instructions,
  exécution, sessions).

Si une seule de ces couches est mal configurée, rien ne fonctionne, d'où
l'importance de tester chaque couche séparément avant d'assembler.

**Ce que tu dois faire concrètement :**

1. Créer un environnement virtuel Python et l'activer :

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Installer les dépendances (`google-adk`, `litellm`, `python-dotenv` dans
   `requirements.txt`) :

   ```bash
   pip install -r requirements.txt
   ```

3. Installer Ollama (ex. via Homebrew sur macOS) :

   ```bash
   brew install ollama
   brew services start ollama
   ```

4. Télécharger un petit modèle local :

   ```bash
   ollama pull llama3.2:1b
   ```

5. **Tester le modèle directement avec Ollama, avant de toucher au code
   Python** :

   ```bash
   ollama run llama3.2:1b "Say hello in one short sentence."
   ```

   Si ça ne répond pas ici, ça ne répondra pas non plus dans ton agent :
   inutile de déboguer le code Python avant d'avoir validé cette étape.
6. Documenter dans `.env.example` les variables attendues (sans valeurs
   secrètes, juste des exemples) :

   ```
   OLLAMA_API_BASE=http://localhost:11434
   MODEL_NAME=ollama_chat/<nom-de-ton-modele>
   ```

7. Copier `.env.example` vers `.env` (fichier réel, non commité) et
   l'ajuster si besoin.

**Résultat attendu :** tu peux lancer `ollama run <modèle> "..."` et
recevoir une vraie réponse texte.

---

## Tâche 2 : Créer ton premier agent (Explainer Agent)

**Ce qu'on te demande :** construire un agent capable de recevoir un sujet
et de répondre avec une explication structurée.

**Pourquoi un agent et pas juste un `print(llm.generate(...))` :** un agent
associe un modèle à un **rôle** et à des **instructions**. Ce sont ces
instructions qui transforment un modèle générique en un outil réutilisable
et prévisible. Des instructions vagues donnent des réponses vagues ; des
instructions précises (structure attendue, format, longueur) donnent des
réponses exploitables par le reste du programme.

**Ce que tu dois faire concrètement :**

- Créer `agents/explainer_agent.py` avec un `Agent` ADK dont le modèle est
  `LiteLlm(model="ollama_chat/<ton-modele>")`.
- Écrire une instruction claire qui dit exactement quoi produire : ici,
  trois sections précises : `## Simple Explanation`, `## Key Concepts`,
  `## Example`, rien d'autre.
- Exécuter cet agent avec un prompt simple (le sujet) et récupérer le texte
  de réponse.

Concrètement, dans ce dépôt, l'agent utilise un utilitaire partagé
(`agents/runner_utils.py`) qui encapsule la mécanique ADK (créer une
session, envoyer un message, lire les événements, extraire le texte final).
Tu peux t'en inspirer, mais comprends bien ce que fait chaque étape plutôt
que de la copier sans la lire :

- `InMemoryRunner` : fait tourner l'agent en mémoire (pas de base de données
  externe).
- Une **session** représente une conversation ; on en crée une par
  exécution.
- On envoie un message utilisateur (`types.Content`) et on lit les
  événements renvoyés jusqu'à trouver la réponse finale
  (`event.is_final_response()`).

**Teste avec au moins deux sujets différents** (ex. "Python decorators",
"HTTP status codes") pour voir si la structure demandée est respectée de
façon cohérente.

**Résultat attendu :** lancer ton script avec un sujet affiche une
explication structurée en Markdown dans le terminal.

---

## Tâche 3 : Outil pour sauvegarder le Markdown

**Ce qu'on te demande :** écrire une fonction Python "normale" (pas un
agent, pas d'IA) qui sauvegarde du texte dans un fichier.

**Pourquoi un outil déterministe :** un modèle de langage peut varier d'une
exécution à l'autre. Mais écrire un fichier ne devrait jamais être
"créatif" : on veut un comportement 100% prévisible : même entrée, même
résultat. C'est le principe général : laisser le modèle gérer la partie
flexible (le texte), et laisser du code classique gérer la partie mécanique
(le fichier).

**Ce que tu dois faire concrètement :**

- Créer `tools/file_writer.py` avec une fonction
  `save_markdown_file(file_path: str, content: str) -> str`.
- Elle doit :
  - créer le dossier parent s'il n'existe pas (`Path.mkdir(parents=True,
    exist_ok=True)`),
  - écrire le contenu dans le fichier,
  - renvoyer un message utile (chemin sauvegardé, ou message d'erreur clair
    si l'écriture échoue).
- **Teste cette fonction seule**, sans agent, avant de la connecter au reste
  (ex. `python tools/file_writer.py` avec un petit test en bas du fichier).

**Résultat attendu :** un fichier Markdown apparaît réellement dans
`output/` après exécution.

---

## Tâche 4 : Outil de validation des sections

**Ce qu'on te demande :** écrire une fonction qui vérifie que le Markdown
généré contient bien toutes les sections attendues, sans juger la qualité
du contenu, juste la structure.

**Pourquoi :** un modèle peut oublier une section, ou mal la nommer. Une
vérification automatique et déterministe permet de détecter ce problème
sans relire le texte à la main à chaque fois.

**Ce que tu dois faire concrètement :**

- Créer `tools/validation.py` avec une liste `REQUIRED_SECTIONS` (Topic,
  Simple Explanation, Key Concepts, Example, Practice Exercise, Common
  Mistakes, Review Comments, Final Summary).
- Écrire `validate_required_sections(markdown: str) -> dict` qui renvoie
  quelque chose comme `{"is_valid": bool, "missing_sections": [...]}`.
- Le point délicat : les petits modèles locaux ne reproduisent pas toujours
  le texte des titres exactement. Dans ce projet, deux ajustements ont été
  nécessaires après des tests réels :
  1. Comparer les titres en **ignorant la casse** et en acceptant qu'un
     titre **commence par** le nom attendu (ex. `## Practice Exercise:
     Something` doit quand même valider `Practice Exercise`).
  2. **Ignorer les lignes à l'intérieur des blocs de code** (entre
     ```` ``` ````), car un commentaire Python `# quelque chose` dans un
     exemple de code ne doit pas être compté comme un titre Markdown.

**Important :** aligne le nom des sections dans tes prompts d'agents et
dans ton validateur. Si l'agent écrit "Explanation" mais que le validateur
attend "Simple Explanation", la validation échouera même si le contenu est
bon.

**Résultat attendu :** ta fonction peut dire correctement quelles sections
manquent sur un texte de test incomplet, et confirmer qu'un texte complet
est valide.

---

## Tâche 5 : Practice Designer Agent

**Ce qu'on te demande :** un deuxième agent, séparé du premier, qui
construit un exercice pratique **à partir de** l'explication déjà générée,
sans la répéter.

**Pourquoi séparer cet agent de l'Explainer :** si un seul agent devait tout
faire (expliquer + créer l'exercice + relire), les instructions
deviendraient longues et confuses, et le modèle aurait tendance à mélanger
les rôles (répéter l'explication dans l'exercice, par exemple). En donnant
à chaque agent une responsabilité unique, les prompts restent courts et les
résultats plus cohérents.

**Ce que tu dois faire concrètement :**

- Créer `agents/practice_designer_agent.py`.
- L'agent reçoit en entrée : le sujet **et** l'explication déjà produite
  (tu les passes dans le prompt, ex. `f"Topic: {topic}\n\nExplanation
  already written:\n{explanation}"`).
- L'instruction doit clairement dire : "ne réécris pas l'explication,
  produis uniquement une section `## Practice Exercise`".
- L'exercice doit être petit : faisable en 10 à 20 minutes, avec si
  pertinent une entrée/sortie attendue et 1-2 indices.

**Point d'attention observé dans ce projet :** un petit modèle a tendance à
enrichir le titre demandé (ex. `## Practice Exercise: Enumerate and Match
HTTP Status Codes` au lieu de `## Practice Exercise`) ou à ajouter des
sous-titres `###` non demandés. Rendre l'instruction très explicite
("exactement ce titre, sans mots supplémentaires sur la ligne du titre")
réduit ce problème, mais ne l'élimine pas toujours, c'est pour ça que
l'outil de validation (tâche 4) doit rester tolérant sur la forme exacte.

**Résultat attendu :** en donnant le sujet + l'explication à cet agent, tu
obtiens un exercice cohérent avec ce qui a été expliqué avant.

---

## Tâche 6 : Reviewer Agent

**Ce qu'on te demande :** un troisième agent qui **relit** un brouillon déjà
assemblé et donne un avis critique, sans réécrire le guide en entier.

**Pourquoi :** ajouter une étape de relecture améliore la qualité globale
sans complexifier les agents précédents. C'est un pattern courant dans les
systèmes multi-agents : un agent "producteur" et un agent "contrôleur
qualité" séparés.

**Ce que tu dois faire concrètement :**

- Créer `agents/reviewer_agent.py`.
- L'agent reçoit le brouillon complet (topic + explication + exercice) en
  entrée.
- Il doit produire : ce qui manque, ce qui est ambigu, des suggestions
  concrètes, et une recommandation courte (approuvé / à revoir).
- Une consigne utile à donner au modèle : être **spécifique**. "Improve the
  explanation" est trop vague ; "L'exemple ne montre pas l'appel de la
  fonction" est utile.

**Résultat attendu :** donner un brouillon à cet agent produit des
commentaires de relecture qui pointent des points précis, pas des généralités.

---

## Tâche 7 : Construire le workflow séquentiel complet

**Ce qu'on te demande :** relier tous les agents et outils dans `main.py`
dans le bon ordre, pour que chaque étape utilise le résultat de la
précédente.

**L'ordre attendu :**

```
Sujet saisi par l'utilisateur
↓
Explainer Agent           → explication + concepts + exemple
↓
Practice Designer Agent   → exercice (basé sur l'explication)
↓
Assemblage du brouillon
↓
Reviewer Agent            → relecture du brouillon
↓
Assemblage du Markdown final
↓
Outil de validation       → vérifie les sections requises
↓
Outil de sauvegarde       → écrit output/study_guide.md
```

**Ce que tu dois faire concrètement :**

- Écrire une fonction qui assemble le Markdown final avec les bons titres
  `#`/`##` dans le bon ordre (Topic, Simple Explanation, Key Concepts,
  Example, Practice Exercise, Common Mistakes, Review Comments, Final
  Summary).
- Afficher des messages de progression clairs pendant l'exécution
  (`[1/5] Running Explainer Agent...`, etc.), utile pour comprendre où le
  programme en est, surtout si un modèle local met du temps à répondre.
- Si la validation échoue, afficher clairement quelles sections manquent
  (mais tu n'es pas obligé de tout corriger automatiquement).
- Garder cette logique lisible dans `main.py` : ne cache pas tout dans une
  seule fonction géante. Une fonction par étape logique (récupérer le
  sujet, lancer chaque agent, assembler, valider, sauvegarder) rend le fichier
  plus facile à suivre.

**Résultat attendu :** `python main.py "un sujet"` produit un fichier
Markdown complet dans `output/study_guide.md`, avec toutes les sections
demandées.

---

## Tâche 8 : Gestion des erreurs et de la configuration

**Ce qu'on te demande :** anticiper les problèmes les plus courants et
donner des messages d'erreur compréhensibles, plutôt que de laisser le
programme planter avec une trace d'erreur obscure.

**Cas à couvrir concrètement :**

- **Sujet vide** : vérifier avant de lancer les agents.

  ```python
  if not topic.strip():
      raise ValueError("Topic cannot be empty.")
  ```

- **Variables d'environnement manquantes** (`MODEL_NAME`,
  `OLLAMA_API_BASE`) : vérifier leur présence au tout début du programme,
  avant même de tenter d'appeler un agent, avec un message qui dit quoi
  faire (ex. "copie `.env.example` vers `.env`").
- **Ollama non lancé / modèle non disponible** : entourer l'appel à
  l'agent d'un `try/except` et donner un message qui oriente vers la bonne
  vérification (Ollama tourne-t-il ? le modèle a-t-il été téléchargé ?).
- **Erreur d'écriture de fichier** : capturer les erreurs `OSError` dans
  l'outil de sauvegarde et renvoyer un message clair plutôt que de laisser
  planter le programme.
- **Échec de validation** : ce n'est pas une erreur bloquante, mais elle
  doit être visible (message d'avertissement listant les sections
  manquantes).

**Pourquoi ce n'est pas juste "ajouter des try/except partout" :** l'idée
n'est pas d'attraper toutes les exceptions génériquement (ça cache les vrais
bugs pendant le développement). L'idée est d'anticiper les erreurs
*prévisibles* liées à la configuration et à l'environnement, et de laisser
les erreurs inattendues remonter normalement pendant que tu développes.

**Résultat attendu :** si tu retires ton fichier `.env`, ou si tu coupes
Ollama, ou si tu passes un sujet vide, le programme doit te dire clairement
ce qui ne va pas, pas juste planter avec une trace Python illisible.

---

## Tâche 9 : Compléter le README et la réflexion

**Ce qu'on te demande :** documenter le projet pour que quelqu'un d'autre
(un camarade, un mentor) puisse le comprendre et le lancer sans toi.

**Sections attendues dans le README :**
Description, Requirements, Setup, Configuration, How to Run, Example Input,
Example Output, Project Structure, Agents, Tools, Self-Validation
Checklist, Reflection, Known Limitations.

**Ce que tu dois faire concrètement pour chaque section :**

- **Setup / Configuration / How to Run** : donne des commandes que tu as
  **réellement testées**, pas des commandes copiées sans vérifier qu'elles
  fonctionnent chez toi.
- **Example Output** : garde-le court (quelques lignes de sortie console
  suffisent, pas besoin de coller tout le guide généré dans le README,
  tu peux renvoyer vers `output/study_guide.md`).
- **Agents / Tools** : explique le rôle de chacun en une ou deux phrases,
  pas juste leur nom de fichier.
- **Self-Validation Checklist** : reprends les exigences du sujet
  (au moins 3 agents, au moins 2 outils, sortie Markdown, `.env` ignoré,
  etc.) et coche ce qui est réellement vérifié.

**Pour la section Reflection, réponds honnêtement à partir de ton
expérience réelle, pas de généralités théoriques :**

1. **Différence entre un appel direct à un LLM et un agent IA ?** Un appel
   direct = un prompt, une réponse, sans rôle fixe ni organisation autour.
   Un agent = un modèle + un rôle défini + une place dans un workflow (et
   potentiellement des outils qu'il peut appeler).
2. **Rôle de chaque agent dans ton système ?** Sois précis sur ce que fait
   *chacun* et pourquoi il ne fait pas le travail des autres.
3. **Rôle de chaque outil ?** Explique pourquoi ces tâches précises sont
   déterministes plutôt que confiées au modèle.
4. **Partie la plus difficile ?** Cherche un vrai problème que tu as
   rencontré (par exemple : le modèle ne respecte pas exactement le nom des
   titres demandés) et explique comment tu l'as résolu concrètement.
5. **Limite observée avec ton modèle ?** Base-toi sur ce que tu as
   réellement constaté en testant (formulations imprévues, titres
   modifiés, contenu plus long ou plus court que demandé, lenteur, etc.),
   pas sur une supposition générale.

**Résultat attendu :** un README que tu pourrais donner à quelqu'un qui n'a
jamais vu ton code, et qui lui permettrait de l'installer et de le lancer
seul.

---

## Erreurs fréquentes à éviter

- **Donner trop de responsabilités à un seul agent.** Si un agent doit
  expliquer, créer l'exercice, et faire la relecture, ses instructions
  deviennent longues et le résultat incohérent. Un agent = un rôle.
- **Instructions vagues.** "Explique le sujet" donne un résultat
  imprévisible. "Réponds avec exactement ces trois titres, dans cet ordre,
  avec ce contenu attendu sous chacun" donne un résultat exploitable.
- **Ne pas tester chaque couche séparément.** Si l'agent ne répond pas,
  teste d'abord Ollama seul (`ollama run ...`), puis l'outil seul
  (`python tools/file_writer.py`), avant de blâmer tout le pipeline.
- **Désaligner les noms de sections entre le prompt et le validateur.** Le
  validateur doit chercher exactement (ou au moins de façon tolérante) les
  titres que les agents sont instruits à produire.
- **Attraper toutes les exceptions génériquement.** Ça cache les vrais bugs
  pendant que tu développes. Gère spécifiquement les erreurs prévisibles
  (config manquante, sujet vide, échec d'écriture), laisse le reste
  remonter normalement.
- **Committer `.env` ou toute clé/secret.** Vérifie toujours `git status`
  avant de committer, et assure-toi que `.env` est bien dans
  `.gitignore`.
