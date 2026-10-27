# Evaluation

Roll out trained policies in Gazebo and measure task success.

## Metrics

- **Success rate** — fraction of episodes where the task is completed.
- **Episode length** — time/steps to completion.
- **Action smoothness** — jerk / position error vs. demonstrations.

## Planned scripts

- `eval_sim.py` — load a fine-tuned policy, run N episodes in Gazebo via the ROS bridge, log results.
- `record_demo.py` — capture Gazebo rollouts to video for the README/demo gallery.

## Demo videos

Drop MP4s here (or link them in the README) to showcase the arm completing
language-instructed tasks in simulation.
