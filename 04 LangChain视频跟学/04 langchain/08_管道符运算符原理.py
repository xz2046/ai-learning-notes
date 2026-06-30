
class Test(object):
    def __init__(self,name):
        self.name = name

    def __or__(self, other):
        return MyList(self, other)
    
    def __str__(self):
        return self.name
    
class MyList(object):
    def __init__(self, *args):
        self.mylist = []
        for arg in args:
            self.mylist.append(arg)

    def __or__(self, other):
        self.mylist.append(other)
        return self
    
    def run(self):
        for i in self.mylist:
            print(i)

if __name__ == "__main__":
    a =Test("a")
    b = Test("b")
    c = Test("c")

    d = a| b| c
    d.run()