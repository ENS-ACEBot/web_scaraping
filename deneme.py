import time
import sys

def custom_sleep(duration):
    """
    Custom sleep function that shows a progress bar indicating how much time is left to wait.
    
    Parameters:
    duration (int): The total time to wait in seconds.
    """
    interval = duration / 10
    for i in range(10):
        sys.stdout.write('_')
        sys.stdout.flush()    
    sys.stdout.write('\n')
    for i in range(10):
        time.sleep(interval)
        sys.stdout.write('█')
        sys.stdout.flush()
    sys.stdout.write('\n')

# Example usage
print("Waiting for 10 seconds:")
custom_sleep(10)
print("Done!")