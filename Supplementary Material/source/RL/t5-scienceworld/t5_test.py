import os

for i in range(15):
    for task_id in [2]:#[0, 5, 12, 18, 20, 23, 25, 28]:
        os.system(f"CUDA_VISIBLE_DEVICES=0,1,2,3,4 python main.py --task_num {task_id} --env_step_limit 100 --lm_path sciworld_11b_rerun_dt --simplification_str easy --beams 16 --max_episode_per_file 1000 --mode dt --set test --output_path logs --model_parallelism_size 5")