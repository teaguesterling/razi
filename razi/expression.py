from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles

from razi.functions import functions, _get_function

class ChemElement(object):
    """Represents a molecular structure value."""

    def __str__(self):
        return self.desc

    def __repr__(self):
        return "<%s at 0x%x; %r>" % (self.__class__.__name__, 
                                     id(self), self.desc)
    
    def __getattr__(self, name):
        return getattr(functions, name)(self)

class TxtChemElement(ChemElement, expression.Function):
    """Represents a chemical value expressed within application code (e.g a 
    SMILES string).
    
    Extends expression.Function so that in a SQL expression context the value 
    is interpreted as 'txt_to_mol(value)' or as the equivalent function in 
    the currently used database as appropriate for the given type.
    """
    
    def __init__(self, desc):
        assert isinstance(desc, basestring)
        self.desc = desc
        expression.Function.__init__(self, "")


@compiles(TxtChemElement)
def __compile_txtchemelement(element, compiler, **kw):
    function = _get_function(element, compiler, [element.desc], 
                             kw.get('within_columns_clause', False))
    return compiler.process(function)

    
class MoleculeElement(object):
    pass

class TxtMoleculeElement(MoleculeElement, TxtChemElement):
    """Represents a Molecule value expressed within application code (a SMILES).
    """
    
    def __init__(self, desc):
        TxtChemElement.__init__(self, desc)
        
        
class PersistentMoleculeElement(MoleculeElement):
    """Represents a Molecule value loaded from the database."""
    
    def __init__(self, desc):
        self.desc = desc


class PatternElement(object):
    pass


class TxtPatternElement(PatternElement, TxtChemElement):
    """Represents a chemical fragment pattern expressed within application code
    (i.e. a SMARTS string)
    """
    
    def __init__(self, desc):
        TxtChemElement.__init__(self, desc)


def _to_mol(value):
    """Interpret a value as a Molecule-compatible construct."""

    if hasattr(value, '__clause_element__'):
        return value.__clause_element__()
    elif isinstance(value, (expression.ClauseElement, MoleculeElement)):
        return value
    elif isinstance(value, basestring):
        return TxtMoleculeElement(value)
    elif value is None:
        return None
    else:
        raise TypeError


    