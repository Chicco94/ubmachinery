from ublib.models.CommesseMacchinario import CommesseMacchinario, dataclass, datetime


@dataclass(init=True)
class CommesseMacchinarioExt(CommesseMacchinario):
    idext: int = None

a = CommesseMacchinario(1,2,"descr",datetime.now(),datetime.now(),0,1)
b = CommesseMacchinarioExt(2,2,"descr",datetime.now(),datetime.now(),0,1,idext=3)
c = CommesseMacchinarioExt(1,2,"descr",datetime.now(),datetime.now(),0,1,idext=3)

def test(x:CommesseMacchinario):
    x.co_qtaProdotta += 1
    print(x)


print(a)
print(b)

test(a)
test(b)
