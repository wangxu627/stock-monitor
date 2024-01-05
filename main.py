import threading
import subprocess
from job import run, clear_trigger_condition, add_compare_data, get_diff_info

def main():
    t1 = threading.Thread(target=run)
    t1.start()
    run_gunicorn()
    t1.join()

def run_gunicorn():
    command = ['gunicorn', '-w', '1', 'app:app', '-b', '0.0.0.0:5001']
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print(output)


if __name__ == '__main__':
    main()
