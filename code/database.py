import datetime


class DataBase:
    def __init__(self, filename):
        self.filename = filename
        self.users = None
        self.file = None
        self.load()

    def load(self):
        self.file = open(self.filename, "r",encoding='utf-8')
        self.users = {}

        for line in self.file:
            name,password,created,hrecord = line.strip().split(";")
            self.users[name] = (password,created,hrecord)
        self.file.close()

    def get_user(self, name):
        if name in self.users:
            return self.users[name]
        else:
            return -1

    def add_user(self,password,name):
        if name.strip() not in self.users:
            self.users[name.strip()] = (password.strip(), DataBase.get_date(),"none")
            self.save()
            return 1
        else:
            print("user name exists already")
            return -1
    
    def add_tr(self,name,hr,spo2):
        if self.users[name][2]=="none":
            tr= DataBase.get_date()+","+str(hr)+","+str(spo2)
            self.users[name] = (self.users[name][0],self.users[name][1],tr)
            self.save()
            return 1
        else:
            tr=self.users[name][2]+"/"+DataBase.get_date()+","+str(hr)+","+str(spo2)
            self.users[name] = (self.users[name][0],self.users[name][1],tr)
            self.save()
            return 1

    def add_hr(self,name,textt):
        if self.users[name][2]=="none":
            tt= textt
            self.users[name] = (self.users[name][0],self.users[name][1],tt)
            self.save()
            return 1
        else:
            tt= textt
            tt=self.users[name][2]+"/"+tt
            self.users[name] = (self.users[name][0],self.users[name][1],tt)
            self.save()
            return 1

    def del_hr(self,name,indextrd):
        x=self.users[name][2].split("/")
        k=[]
        for ii in range(len(x)):
            k=k+[ii]
        kk=list(set(k).difference(set(indextrd)))
        xx=[]
        for i in range(len(kk)):
            xx=xx+[x[kk[i]]]
        hrr=""
        for j in range(len(kk)):
            if j!=len(kk)-1:
                hrr=hrr+xx[j]+"/"
            else:
                hrr=hrr+xx[j]
        self.users[name] = (self.users[name][0],self.users[name][1],hrr)
        self.save()
        return 1

    def del_tr(self,name):
        x=self.users[name][2].split("/")
        xx=""
        for ii in range(len(x)-1):
            if ii!=len(x)-2:
                xx=xx+x[ii]+"/"
            else:
                xx=xx+x[ii]
        self.users[name] = (self.users[name][0],self.users[name][1],xx)
        self.save()
        return 1
        
    def validate(self, name, password):
        if self.get_user(name) != -1:
            return self.users[name][0] == password
        else:
            return False

    def save(self):
        with open(self.filename, "w",encoding='utf-8') as f:
            for user in self.users:
                f.write(user + ";" + self.users[user][0] + ";" + self.users[user][1] + ";" + self.users[user][2]  +"\n")

    @staticmethod
    def get_date():
        return str(datetime.datetime.now()).split(" ")[0]


