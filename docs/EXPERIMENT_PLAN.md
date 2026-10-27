# Plan d'expérience — SmolVLA : multi-tâche vs spécialisé (Meta-World)

## 1. Question de recherche

> **Le fine-tuning multi-tâche d'un petit VLA ouvert (SmolVLA 450M) vaut-il le coup, et que gagne/perd-on en se spécialisant sur quelques tâches ?**

Objectif concret : mesurer le taux de réussite de 3 modèles + 1 référence, tous évalués sur la **même sélection de tâches**, pour produire un tableau et un graphe comparables.

## 2. Les 4 modèles

| ID | Point de départ | Données d'entraînement | Étapes | Statut |
|----|----------------|------------------------|--------|--------|
| **M0** | `lerobot/smolvla_base` | — (0-shot) | 0 | évalué en S1 |
| **M1** | `lerobot/smolvla_base` | MT50 (50 tâches) | 10 000 | ✅ entraîné, évalué en S1 |
| **M2** | `lerobot/smolvla_base` | 4 tâches (choix data-driven) | 10 000 | à entraîner (après S1) |
| **Expert** | — (politiques scriptées metaworld) | — | — | référence ≈ 100 % |

> M1 et M2 partent **du même point** (`smolvla_base`) avec **le même budget d'étapes (10k)**. La seule différence = le choix des données. C'est ce qui rend la comparaison propre.

## 3. Sélection de tâches (12 au total, fixe pour tous les modèles)

| Difficulté | Tâches |
|------------|--------|
| **easy** (3) | `door-close-v3`, `reach-v3`, `button-press-topdown-v3` |
| **medium** (4) | `basketball-v3`, `bin-picking-v3`, `coffee-push-v3`, `sweep-v3` |
| **hard** (3) | `pick-place-v3`, `push-v3`, `assembly-v3` |
| **very_hard** (2) | `shelf-place-v3`, `disassemble-v3` |

**Règle clé** : les 4 modèles sont évalués sur **exactement ces 12 tâches**.

## 4. Choix des 4 tâches de spécialisation M2 (data-driven)

**Principe** : spécialiser M2 sur des tâches où M1 est « à moitié bon » (~20-70 % de réussite), car c'est là qu'on peut mesurer un écart net.

- Trop facile → M1 réussit déjà, pas de marge (plafonné).
- Trop dur → M2 risque d'échouer aussi, les deux à ~0 % (aucun signal).
- **~20-70 %** → M2 a de la marge pour progresser nettement.

**Procédure** :
1. Lancer **S1** (éval M0 + M1 sur les 12 tâches).
2. Lire les taux de réussite de M1.
3. Choisir les **4 tâches où M1 ∈ [20 %, 70 %]** (probablement dans le groupe medium).
4. Lancer **S2** (entraîner M2 sur ces 4 tâches).

## 5. Plan d'entraînement — M2

### 5.1 Créer le dataset filtré
Extraire de `lerobot/metaworld_mt50` les épisodes des 4 tâches choisies (champ `task`) → ~4 × 50 = ~200 épisodes → dataset local.

### 5.2 Entraînement (commande)
```bash
lerobot-train \
  --policy.type=smolvla \
  --policy.load_vlm_weights=true \
  --policy.push_to_hub=false \
  --dataset.root=./data/metaworld_4tasks \
  --batch_size=32 \
  --steps=10000 \
  --save_freq=2000 \
  --log_freq=100 \
  --output_dir=./outputs/metaworld_4tasks \
  --wandb.enable=false
```
- Durée estimée : ~3-4 h (T4).

## 6. Plan d'évaluation

### 6.1 Protocole
- **10 épisodes / tâche** pour M0, M1, M2 (toujours reporter le CI95 Wilson).
- **5 épisodes / tâche** pour Expert (quasi-déterministe).
- `seed` fixe, `--eval.batch_size=1`.
- Métrique : taux de réussite (succès = critère interne Meta-World), par tâche + par groupe.

### 6.2 Commande
```bash
lerobot-eval \
  --policy.path=<chemin_du_modèle> \
  --env.type=metaworld \
  --env.task=<task> \
  --eval.batch_size=1 \
  --eval.n_episodes=10
```

### 6.3 Sessions Kaggle

| Session | Contenu | Durée |
|---------|---------|-------|
| **S1** | Éval M0 + M1 (12 tâches × 10 ep) | ~6-7 h |
| **S2** | Entraîner M2 (4 tâches) | ~3-4 h |
| **S3** | Éval M2 + Expert (12 tâches) | ~5 h |

## 7. Tableau de résultats (template)

| Tâche | Diff. | M0 | M1 | M2 | Expert |
|-------|-------|----|----|----|--------|
| door-close-v3 | easy | | | | ~100 % |
| reach-v3 | easy | | | | |
| button-press-topdown-v3 | easy | | | | |
| basketball-v3 | medium | | | | |
| bin-picking-v3 | medium | | | | |
| coffee-push-v3 | medium | | | | |
| sweep-v3 | medium | | | | |
| pick-place-v3 | hard | | 10 % (20ep) | | |
| push-v3 | hard | | | | |
| assembly-v3 | hard | | | | |
| shelf-place-v3 | very_hard | | | | |
| disassemble-v3 | very_hard | | | | |
| **Moyenne** | — | | | | |

+ graphe : taux de réussite par difficulté (3 courbes M0/M1/M2 + ligne Expert).

## 8. Interprétation attendue
- **M0 < M1** partout → le fine-tuning aide (attendue).
- **M2 > M1 sur les 4 tâches de spécialisation** → la spécialisation aide les tâches ciblées.
- **M2 vs M1 sur les 8 autres** → mesure de l'oubli catastrophique (résultat le plus intéressant).

## 9. Points d'attention
- Le résultat pick-place à 20 épisodes (10 %) reste documenté à part ; le benchmark utilise 10 ep/tâche.
- Toujours reporter le CI95 — avec 10 épisodes il est large.
- Le dataset filtré M2 doit garder le même schéma que `metaworld_mt50`.
