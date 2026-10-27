# Résultats d'évaluation — SmolVLA fine-tuné sur Meta-World

## Modèle
- **Base** : `lerobot/smolvla_base` (SmolVLA 450 M, encodeur vision SmolVLM2-500M gelé, ~100 M de params action expert entraînées)
- **Fine-tune** : `lerobot/metaworld_mt50` (50 tâches, 2500 épisodes de démonstrations)
- **10 000 étapes** · batch 32 · AdamW (lr 1e-4) · scheduler cosine
- Reprise propre depuis le checkpoint 8000 après un timeout Kaggle (12 h), via `--resume=true --config_path=<checkpoint>/pretrained_model`

## Évaluation (Meta-World, `pick-place-v3`)
- 20 épisodes · simulateur Meta-World intégré à LeRobot (MuJoCo 3.3.0 + metaworld 3.1.1)
- **Taux de réussite : 10 % (2/20)**
- Intervalle de confiance 95 % (Wilson) : **2.8 % – 30.1 %**
- Récompense moyenne : somme 99.3 · max 0.91
- Durée d'éval : ~35 min (≈105 s/épisode)

## Épisodes réussis
| Épisode | sum_reward | max_reward |
|---------|-----------|------------|
| n°7     | 149.9     | 6.30       |
| n°9     | 1647.5    | 6.40       |

## Vidéos de démonstration
- `eval_episode_7.mp4` — succès
- `eval_episode_9.mp4` — succès
- (épisodes 0–6 et 8 = échecs typiques, le bras n'attrape pas la cible)

## Interprétation
Résultat **positif** : le modèle a réellement appris le pick-and-place (2 succès propres),
contre 0 % sur `assembly-v3` (tâche plus dure) avec seulement 2000 étapes lors d'un test antérieur.
Pistes d'amélioration : plus d'étapes, fine-tune mono-tâche ciblé, données réelles (SO-100).

Données brutes : `eval_info.json`, vidéos dans `videos/pick-place-v3_0/`.
