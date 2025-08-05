#!/usr/bin/env python3
"""
Multi-Agent AI-Researcher Enhanced System with Dynamic Topic Support
"""

import sys
import os
import logging
import yaml
import argparse
from pathlib import Path
import tempfile
import shutil
import datetime
import io
from contextlib import redirect_stdout
import multiprocessing

# 处理导入冲突
project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
sys.path.insert(0, project_root)

# 临时重命名agentverse.py来避免冲突
agentverse_py_path = os.path.join(project_root, 'agentverse', 'agentverse.py')
if os.path.exists(agentverse_py_path):
    temp_name = agentverse_py_path + '.tmp'
    os.rename(agentverse_py_path, temp_name)
    renamed = True
else:
    renamed = False

try:
    from agentverse.simulation import Simulation

    def load_and_process_config(config_path: Path, topic: str) -> str:
        """
        Load configuration file and replace topic placeholders
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # Replace placeholders
        topic_lower = topic.lower()
        config_content = config_content.replace('{topic}', topic)
        config_content = config_content.replace('{topic_lower}', topic_lower)
        
        # Create temporary directory and configuration file
        temp_dir = tempfile.mkdtemp()
        temp_config_path = Path(temp_dir) / "config.yaml"
        
        with open(temp_config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        return temp_dir

    def run_multi_agent_simulation(topic: str, run_id: int = 0, num_runs: int = 1):
        """Run multi-agent academic discussion"""
        # Configure unique logging for this run
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_lower = topic.lower().replace(" ", "_")
        log_filename = f"logs/multi_{topic_lower}_run{run_id}_{timestamp}.log"
        os.makedirs(os.path.dirname(log_filename), exist_ok=True)
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info(f"Starting run {run_id+1}/{num_runs} for topic: {topic}")

        print("Multi-Agent AI-Researcher Enhanced System")
        print("=" * 60)
        print(f"Research Topic: {topic}")
        print("=" * 60)
        print()
        
        
        try:
            # Configuration file path
            config_path = Path(__file__).parent / "config.yaml"
            
            # Process configuration file
            temp_dir = load_and_process_config(config_path, topic)
            
            # Use the original from_task method to create a task in AgentVerse format
            # Create a directory structure matching AgentVerse format
            task_dir = Path(temp_dir) / "multi_topic"
            task_dir.mkdir(exist_ok=True)
            
            # Copy the configuration file to the correct location
            shutil.copy(Path(temp_dir) / "config.yaml", task_dir / "config.yaml")
            
            # Load simulation
            task = "multi_topic"
            tasks_dir = str(temp_dir)
            
            print("Initializing AI-Researcher tools...")
            agentverse = Simulation.from_task(task, tasks_dir)
            print("System initialization complete!")
            print()
            
            print("Starting multi-agent discussion...")
            print(f"Topic: {topic}")
            print("-" * 60)
            
            # Configure unique output file
            output_filename = f"outputs/multi_{topic_lower}_run{run_id}_{timestamp}.txt"
            os.makedirs(os.path.dirname(output_filename), exist_ok=True)
            
            # Capture output
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                agentverse.run()
            
            # Write captured output to file
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(output_buffer.getvalue())
            logging.info(f"Output saved to {output_filename}")
            
            print(f"\nGenerated content saved to: {output_filename}")
            
            print("-" * 60)
            print("Discussion complete!")
            print()

            print(f"Your multi-agent AI-Researcher enhanced system ran successfully! Topic: {topic}")
            
            # Clean up temporary files
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            print(f"Error during execution: {e}")
            import traceback
            traceback.print_exc()
            # Ensure temporary files are cleaned up
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

    def run_multi_agent_simulation_wrapper(args):
        topic, run_id, num_runs = args
        run_multi_agent_simulation(topic, run_id, num_runs)

    def main():
        """Main function"""
        parser = argparse.ArgumentParser(description='Multi-Agent AI-Researcher Enhanced System with Dynamic Topic Support')
        parser.add_argument('--topic', type=str, 
                           default="Consciousness Interpretability",
                           help='Research Topic')
        parser.add_argument('--num_runs', type=int, 
                           default=1,
                           help='Number of content generations (default: 1)')
        parser.add_argument('--parallel', action='store_true',
                        help='Enable parallel execution (default: off)')
        
        args = parser.parse_args()
        
        if args.parallel:
            with multiprocessing.Pool() as pool:
                pool.map(run_multi_agent_simulation_wrapper, [(args.topic, i, args.num_runs) for i in range(args.num_runs)])
        else:
            for i in range(args.num_runs):
                run_multi_agent_simulation(args.topic, run_id=i, num_runs=args.num_runs)

    if __name__ == "__main__":
        main()

finally:
    # Restore original file name
    if renamed:
        os.rename(temp_name, agentverse_py_path) 