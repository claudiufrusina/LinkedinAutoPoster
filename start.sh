#!/bin/bash
# Start both the scheduler and the web GUI in parallel.
# The web GUI runs in the background; the scheduler runs in the foreground
# so Docker can track its process lifecycle.

echo "Starting LinkedIn Auto Poster..."
echo "  → Web GUI:   http://0.0.0.0:${WEB_PORT:-5000}"
echo "  → Scheduler: posting at configured times"
echo ""

# Launch the web GUI in the background
python web.py &
WEB_PID=$!

# Launch the scheduler in the foreground
python main.py &
SCHEDULER_PID=$!

# Trap SIGTERM/SIGINT to gracefully stop both processes
trap "echo 'Shutting down...'; kill $WEB_PID $SCHEDULER_PID 2>/dev/null; exit 0" SIGTERM SIGINT

# Wait for either process to exit
wait -n $WEB_PID $SCHEDULER_PID
EXIT_CODE=$?

# If one exits, stop the other
kill $WEB_PID $SCHEDULER_PID 2>/dev/null
exit $EXIT_CODE
