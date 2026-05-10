# 🗞️ Daily AI & Robotics Newsletter — Setup

## 1. Créer un nouveau repo GitHub

Crée un repo (public ou privé) sur GitHub, par exemple `ai-newsletter`, et push le contenu du dossier `newsletter/` dedans :

```bash
cd newsletter
git init
git add .
git commit -m "feat: daily AI & robotics newsletter"
git remote add origin https://github.com/sayfcha/ai-newsletter.git
git push -u origin main
```

## 2. Créer un App Password Gmail

Ton compte Gmail a besoin d'un "App Password" pour autoriser l'envoi d'emails depuis GitHub Actions :

1. Va sur https://myaccount.google.com/apppasswords
2. (Active la vérification en 2 étapes si ce n'est pas déjà fait)
3. Crée un nouveau mot de passe d'application → choisis "Mail" et "Autre" → nomme-le "Newsletter Bot"
4. Copie le mot de passe généré (16 caractères, ex: `abcd efgh ijkl mnop`)

## 3. Configurer les secrets GitHub

Dans ton repo GitHub :

1. Va dans **Settings** → **Secrets and variables** → **Actions**
2. Ajoute ces 2 secrets :

| Secret Name      | Value                          |
|------------------|--------------------------------|
| `SENDER_EMAIL`   | `sayfcha2@gmail.com`           |
| `SENDER_PASSWORD`| Le App Password de l'étape 2   |

## 4. Tester

Tu peux déclencher le workflow manuellement :

1. Va dans l'onglet **Actions** de ton repo
2. Clique sur **"Daily AI & Robotics Newsletter"**
3. Clique sur **"Run workflow"**
4. Vérifie ta boîte mail !

## 5. C'est tout !

Le workflow se déclenchera automatiquement chaque jour à **7h du matin (heure de Paris)**.

---

## Structure des sources

Le script agrège les flux RSS de :
- **IA** : TechCrunch AI, The Verge AI, MIT Tech Review, VentureBeat, Ars Technica
- **Robotique** : IEEE Spectrum, The Robot Report, TechCrunch Robotics
- **Tech** : Hacker News (top), TechCrunch, The Verge, Ars Technica

Tu peux ajouter/retirer des sources en éditant le dictionnaire `FEEDS` dans `newsletter.py`.
