import sys

from zeep.xsd.types.base import Type
from zeep.xsd.types.collection import UnionType  # FIXME
from zeep.xsd.types.simple import AnySimpleType  # FIXME


class UnresolvedType(Type):
    def __init__(self, qname, schema):
        self.qname = qname
        assert self.qname.text != "None"
        self.schema = schema

    def __repr__(self):
        return "<%s(qname=%r)>" % (self.__class__.__name__, self.qname.text)

    def render(self, parent, value, xsd_type=None, render_path=None):
        raise RuntimeError(
            "Unable to render unresolved type %s. This is probably a bug."
            % (self.qname)
        )

    def resolve(self):
        retval = self.schema.get_type(self.qname)
        return retval.resolve()


class UnresolvedCustomType(Type):
    def __init__(self, qname, base_type, schema):
        assert qname is not None
        self.qname = qname
        self.name = self._name()
        self.schema = schema
        self.base_type = base_type

    def __repr__(self):
        return "<%s(qname=%r, base_type=%r)>" % (
            self.__class__.__name__,
            self.qname.text,
            self.base_type,
        )

    def _name(self):
        if sys.version_info >= (3, 0):
            return self.qname.localname

        return str(self.qname.localname)

    def resolve(self):
        base = self.base_type
        base = base.resolve()

        cls_attributes = {"__module__": "zeep.xsd.dynamic_types"}

        if issubclass(base.__class__, UnionType):
            xsd_type = type(self.name, (base.__class__,), cls_attributes)
            return xsd_type(base.item_types)

        elif issubclass(base.__class__, AnySimpleType):
            xsd_type = type(self.name, (base.__class__,), cls_attributes)
            return xsd_type(self.qname)

        else:
            xsd_type = type(self.name, (base.base_class,), cls_attributes)
            return xsd_type(self.qname)
