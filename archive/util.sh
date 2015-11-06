clear;
echo "Roll one PID:"
ps -A | grep py
echo ""
echo "Current contents of ./logs/"
ls logs
echo ""
echo "Log tail without heartbeats:"
grep -v "Heartbeat" rofm.log | tail -n20
echo ""
echo "Last of log:"
tail -n3 rofm.log
echo ""
echo ""
echo "It is currently:"
date