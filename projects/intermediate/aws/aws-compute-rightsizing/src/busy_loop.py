"""
Optional: run this ON one demo instance to generate real CPU load so it shows up
as "right-sized" instead of "idle". SSH/SSM into the instance and run it for a few
minutes, then stop it. The OTHER instance, left alone, stays idle for contrast.

    python3 busy_loop.py 300   # burn CPU for 300 seconds
"""

import sys
import time

seconds = int(sys.argv[1]) if len(sys.argv) > 1 else 180
end = time.time() + seconds
x = 0
while time.time() < end:
    x = (x * x + 1) % 2147483647
print(f"done burning CPU for {seconds}s")
