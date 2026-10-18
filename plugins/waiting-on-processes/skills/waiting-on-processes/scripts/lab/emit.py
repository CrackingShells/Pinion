import time
for i in range(4):
    print("EVENT", i, "emitted at", time.strftime("%T")); time.sleep(2)
