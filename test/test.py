import requests
import datetime
import time
from flask import jsonify
import sys

class Test:
    def __init__(self, date:str, eppes:str):
        self.date = datetime.datetime.strptime(date, "%Y%m%d")
        self.eppes = eppes

#date = "20201201"
#test = Test(date, "zigeuner")
#tests = [test]
#res = json.dumps([e.__dict__ for e in tests])
#print(res)
#print(test.__dict__)
#exit()

a_add = "http://localhost:5004/apartments/add?name={name}&address={ad}&noiselevel={nl}&floor={floor}"
a_rem = "http://localhost:5004/apartments/remove?id={id}"
a_list = "http://localhost:5004/apartments/list"

b_add = "http://localhost:5004/booking/add?apartment={ap}&from={st}&to={end}&who={who}"
b_rem = "http://localhost:5004/booking/cancel?id={id}"
b_change = "http://localhost:5004/booking/change?id={id}&from={st}&to={end}"
b_list = "http://localhost:5004/booking/list"
b_list_a = "http://localhost:5004/booking/list_apartments"

s = "http://localhost:5004/search/search?from={st}&to={end}"
s_list_b = "http://localhost:5004/search/list_bookings"
s_list_a = "http://localhost:5004/search/list_apartments"

def apartments():
    print("""What do you want to do?
              1. Add
              2. Remove""")
    x = int(input())
    if x == 1:
        print("Name: ")
        name = input()
        print("Address: ")
        address = input()
        print("Noise level: ")
        nl = input()
        print("Floor: ")
        floor = input()
        print(requests.get(a_add.format(name=name, ad=address, nl=nl, floor=floor)).text)
    else:
        print("Id: ")
        id = input()
        print(requests.get(a_rem.format(id=id)).text)

def booking():
    print("""What do you want to do?
              1. Add
              2. Remove
              3. Change""")
    x = int(input())
    if x == 1:
        print("Apartment: ")
        ap = input()
        print("From: ")
        start = input()
        print("To: ")
        end = input()
        print("Who: ")
        who = input()
        print(requests.get(b_add.format(ap=f"{ap}", st=start, end=end, who=who)).text)
    elif x == 2:
        print("Id: ")
        id = input()
        print(requests.get(a_rem.format(id=id)).text)
    else:
        print("Id: ")
        id = input()
        print("From: ")
        start = input()
        print("To: ")
        end = input()
        print(b_change.format(id=id, st=start, end=end).text)

def search():
    print("From: ")
    start = input()
    print("To: ")
    end = input()

try:
    while True:
        print("""Which service do you want to access?
              1. Apartments
              2. Booking
              3. Search""")
        x = int(input())
        if x == 1:
            apartments()
        elif x == 2:
            booking()
        else:
            search()

except KeyboardInterrupt:
    sys.exit(0)

#res1 = requests.get(a_add.format(name="Appartamento2", ad="ViaAlessandria", nl="3",floor="1"))
#time.sleep(3)
#res2 = requests.get(a_rem.format(id="126df28d99e54fca9401cad9e0e4b907"))
#res3 = requests.get(a_list)
#apartment = res3.json()[0]["id"]
#print(f"The apartment created is {apartment}")
#time.sleep(3)
# res4 = requests.get(b_add.format(ap=f"{apartment}", st="20201201", end="20201210", who="Matteo"))
# res4 = requests.get(b_add.format(ap="bcb4b0a67f6e4ba1ab86ebbab0395630", st="20201101", end="20201110", who="Matteo"))
#res4 = requests.get(b_change.format(id="a2af98dd55a34a76b796599056405dfe", st="20201201", end="20201210"))
#time.sleep(3)
#res2 = requests.get(a_rem.format(id=f"{apartment}"))
#time.sleep(3)
#res5 = requests.get(b_rem.format(id="084d97b3288c4b9ea07ecf7c9c6b0717"))
#res6 = requests.get(b_change.format(id="", st="", end=""))
#res3 = requests.get(a_list)
#res7 = requests.get(b_list)
#res8 = requests.get(b_list_a)
#res9 = requests.get(s.format(st="20201201", end="20201213"))
#res10 = requests.get(s_list_a)
#res11 = requests.get(s_list_b)

#print(res3.text)
#print(res4.text)
#print(res7.text)
#print(res8.text)
#print(res10.text)
#print(res11.text)

#requests.get(a_add.format(name="A", ad="Bolzano", nl="4",floor="0"))
#requests.get(a_add.format(name="B", ad="Merano", nl="0",floor="2"))
#requests.get(a_add.format(name="C", ad="Trento", nl="1",floor="1"))
res = requests.get(a_list)
#print(res.text)
for i in range(3):
    if res.json()[i]["name"] == "A":
        a_a = res.json()[i]["id"]
    elif res.json()[i]["name"] == "B":
        a_b = res.json()[i]["id"]
    elif res.json()[i]["name"] == "C":
        a_c = res.json()[i]["id"]

#requests.get(b_add.format(ap=f"{a_a}", st="20240101", end="20240201", who="Matteo"))
#time.sleep(1)
requests.get(b_add.format(ap=f"{a_b}", st="20240301", end="20240307", who="Paola"))
time.sleep(1)
res = requests.get(b_list)
print(res.text)
for i in res.json():
    if i["apartment"] == f"{a_b}" and i["who"] == "Paola":
        b_p = i["id"]

res = requests.get(b_change.format(id=f"{b_p}", st="20240301", end="20240308"))
print(res.text)
time.sleep(1)
res = requests.get(b_list)
print(res.text)

requests.get(b_rem.format(id=f"{b_p}"))