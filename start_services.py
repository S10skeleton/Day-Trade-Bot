import subprocess

def start_tensorboard():
    print("Starting TensorBoard...")
    return subprocess.Popen(
        [
            "tensorboard",
            "--logdir=web/backend/ppo_tensorboard/",
            "--host=127.0.0.1",
            "--port=6006"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

def start_backend():
    print("Starting backend...")
    return subprocess.Popen(
        ["flask", "run", "--host=127.0.0.1", "--port=5000"],
        cwd="web/backend",  # Path to backend directory
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

def start_frontend():
    print("Starting frontend...")
    return subprocess.Popen(
        ["npm", "start"],
        cwd="web/frontend",  # Path to frontend directory
        shell=True,          # Required on Windows for commands like npm
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

if __name__ == "__main__":
    try:
        tensorboard_proc = start_tensorboard()
        backend_proc = start_backend()
        frontend_proc = start_frontend()

        print("All services started successfully.")
        print("TensorBoard is running on http://127.0.0.1:6006")
        print("Backend is running on http://127.0.0.1:5000")
        print("Frontend is running on http://localhost:3000")

        # Wait for all processes to finish
        tensorboard_proc.wait()
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("Stopping all services...")
        tensorboard_proc.terminate()
        backend_proc.terminate()
        frontend_proc.terminate()
