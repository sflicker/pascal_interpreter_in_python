
#####################
## AST
#####################
class AST(object):
    def __init__(self):
        pass

#####################
## AST visitor
#####################

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        pass
#        raise Exception('No visit_{} method'.format(type(node).__name__))
