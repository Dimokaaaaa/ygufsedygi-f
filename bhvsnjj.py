class Student:
    def __init__(self,name,ustalost,hungry,power,day):
        self.name = name
        self.ustalost = 0
        self.hungry = 0
        self.power = 3
        self.day = 1
        print("hi I'm student",name)
    def cooking(self):
        print(self.name,"love cook")
    def studying(self):
        print(self.name,"love studying")
    def sheck_stats(self):
        print("my stats:"+"hungry:"+self.hungry,"ustalost:"+self.ustalost,"power:"+self.power)

player = Student("Dimoka")
print("Rules: if ur live's stats(for exemple: hungry or ustalost) will be more 100"+'%'+" u will lose")
print("1= go to gym,2= go to cook, 3= go to sleep(skip day)")
while 
wuwtd = int(input("what u want to do?"))
