from login import shoonya

otp=input()
client=shoonya(twofa=otp)
api=client.login()
