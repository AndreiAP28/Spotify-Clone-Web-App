from datetime import datetime, timedelta


xyz = datetime.now() + timedelta(hours = 5)
if datetime.now() >  xyz:
        print("REFRESHED")
else:
        print("NNOOO")

