import math


class Variable():

    Atomic = object()
    Scalar = object()
    NoOperation = "X"


    def __init__(self, value, operation=NoOperation,type=Atomic, children=[]):
        self.value = float(value)
        self.d = 0
        self.operation = operation
        self.children = children
        self.type = type

    def __repr__(self):
        if self.type == self.Scalar:
            return f'Scalar({self.value})'
        if self.operation == self.NoOperation:
            return f'Var({self.value})'
        return f"{self.operation} [ {', '.join([i.__repr__() for i in self.children])} ]"

    def __add__(self, other):
        if not isinstance(other, Variable):
            other = Variable(value=other, type=self.Scalar)
        return Variable(self.value + other.value, '+', self.Atomic,[self, other])

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if not isinstance(other, Variable):
            other = Variable(other,type=self.Scalar)
        return  Variable(self.value - other.value, '-',self.Atomic, [self, other])

    def __rsub__(self, other):
        if not isinstance(other, Variable):
            other = Variable(other,type=self.Scalar)
        return Variable(other.value - self.value, '-', self.Atomic,[other, self])

    def __mul__(self, other):
        if not isinstance(other, Variable):
            other = Variable(other,type=self.Scalar)
        return Variable(self.value * other.value, '*', self.Atomic,[self, other])

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if not isinstance(other, Variable):
            other = Variable(other,type=self.Scalar)
        return Variable(self.value / other.value, '/', self.Atomic,[self, other])

    def __rtruediv__(self, other):
        if not isinstance(other, Variable):
            other = Variable(other,type=self.Scalar)
        return Variable(other.value / self.value, '/', self.Atomic,[other,self])

    def exp(self):
        return Variable(math.exp(self.value),operation='exp',type=self.Atomic,children=[self])

    def log(self):
        return Variable(math.log(self.value),operation='log',type=self.Atomic,children=[self])

    def tanh(self):
        return Variable(math.tanh(self.value), operation='tanh', type=self.Atomic, children=[self])

    def _getVariables(self):
        vars = set()
        for v in self.children:
            if isinstance(v, Variable):
                if v.type == self.Atomic:
                    vars.add(v)
                vars |= v._getVariables()
        return vars

    def _derivate(self, target, var):
        # one variable
        if var == target:
            return 1
        elif var.type == self.Scalar:
            return 0
        elif var.operation == '+':  # (a+b)/da = a
            return sum([self._derivate(target, v) for v in var.children])
        elif var.operation == '-':  # (a-b)/da = a
            return self._derivate(target,var.children[0]) - self._derivate(target,var.children[1])
        elif var.operation == '*':
            return self._derivate(target,var.children[0]) * var.children[1].value \
                    + self._derivate(target,var.children[1]) * var.children[0].value
        elif var.operation == '/':
            return (self._derivate(target, var.children[0]) * var.children[1].value -\
                    self._derivate(target, var.children[1]) * var.children[0].value)\
                   /(var.children[1].value ** 2)
        elif var.operation == 'exp':
            return var.value * self._derivate(target, var.children[0])
        elif var.operation == 'log':
            return (1 / var.children[0].value) * self._derivate(target,var.children[0])
        elif var.operation == 'tanh':
            return 1-(math.tanh(var.children[0].value)**2)
        else:
            return 0




    def backward(self):
        vars = self._getVariables()

        for v in vars:
            v.d = Variable(self._derivate(v, self))








if __name__ == "__main__":
    a = Variable(0.0)
    p = 1.0 / (1 + (-3 * a).exp())

    print(f'val:{p.value}\n{p}')
    loss = p.log()
    print(f'val:{loss.value}\n{loss}')
    print(math.log(0.5))
    loss.backward()
    print(a.d.value)
