

class ISerializable(object):
    """
    Interface for serialization and deserialization.
    """
    def __init__(self):
        super(ISerializable, self).__init__()

    def serialize(self, *args, **Kwargs):
        '''
        Implements how item should be serialized.

        Raises:
            NotImplementedError.
        '''
        raise NotImplementedError('serialize method of ISerializable is not implemented')

    def deserialize(self, *args, **Kwargs):
        '''
        Implements how item should be deserialized.

        Raises:
            NotImplementedError.
        '''
        raise NotImplementedError('deserialize method of ISerializable is not implemented')


class IItemBase(ISerializable):
    '''
    Item interface.

    Base for pins and nodes.
    '''

    def __init__(self):
        super(IItemBase, self).__init__()

    @property
    def uid(self):
        '''
        uid getter.

        used by graph and by nodes for fast members access
        pins inside node and nodes inside graph.

        Returns:
            universally unique identifier UUID class.
        '''
        pass

    @uid.setter
    def uid(self, value):
        '''
        uid setter.

        Args:
            value:  uuid4 universally unique identifier
        '''
        pass

    @uid.deleter
    def uid(self):
        '''
        uid deleter.

        uid is a fundamental element. Do not allow to accidentally delete it.

        Raises:
            NotImplementedError.
        '''
        raise NotImplementedError('uid property of IItemBase can not be deleted')

    def getName(self):
        '''
        returns item's name as string.

        Returns:
            string name of item.
        '''
        raise NotImplementedError('getName method of IItemBase is not implemented')

    def setName(self, name):
        '''
        sets item's name.

        Args:
            name: string to be used as name.
        '''
        raise NotImplementedError('setName method of IItemBase is not implemented')

    def kill(self):
        raise NotImplementedError('kill method of IItemBase is not implemented')


class IPin(IItemBase):
    """
    Pin interface.
    """

    def __init__(self):
        super(IPin, self).__init__()

    @staticmethod
    def color():
        '''
        Defines what color pin will be drawn.

        Returns:
            QColor class.
        '''
        raise NotImplementedError('color method of IPin is not implemented')

    @staticmethod
    def pinDataTypeHint():
        """
        Static hint of what data type is this pin, as well as default value for this data type.

        Used to easily find pin classes by type id.


        Returns:
            A tuple containing data type id as first element + default value for this data type as second.

        Examples:
            # printing hints
            >>> somePin.pinDataTypeHint()
            (0, 0.0)
            >>> somePin.pinDataTypeHint()
            (3, False)

            # this is how it used in pins initialization
            >>> def _REGISTER_PIN_TYPE(pinSubclass):
            >>>     dType = pinSubclass.pinDataTypeHint()[0]
            >>>     if dType not in _PINS:
            >>>         _PINS[pinSubclass.pinDataTypeHint()[0]] = pinSubclass
            >>>     else:
            >>>         raise Exception("Error registering pin type {0}\n pin with ID [{1}] already registered".format(pinSubclass.__name__))

        @sa [DataTypes](@ref AGraphCommon.DataTypes)
        """
        raise NotImplementedError('pinDataTypeHint method of IPin is not implemented')

    def supportedDataTypes(self):
        '''
        An array of supported data types.

        Array of data types that can be casted to this type. For example - int can support float, or vector3 can support vector4 etc.
        '''
        raise NotImplementedError('supportedDataTypes method of IPin is not implemented')

    def defaultValue(self):
        '''
        Default value for this particular pin.

        This can be set whenever you need.

        @sa PyFlow.Pins
        '''
        raise NotImplementedError('defaultValue method of IPin is not implemented')

    def getData(self):
        raise NotImplementedError('getData method of IPin is not implemented')

    def setData(self, value):
        raise NotImplementedError('setData method of IPin is not implemented')

    def call(self):
        raise NotImplementedError('call method of IPin is not implemented')

    @property
    def dataType(self):
        raise NotImplementedError('dataType getter method of IPin is not implemented')

    @dataType.setter
    def dataType(self, value):
        raise NotImplementedError('dataType setter method of IPin is not implemented')

    def isUserStruct(self):
        raise NotImplementedError('isUserStruct method of IPin is not implemented')

    def getUserStruct(self):
        raise NotImplementedError('getUserStruct method of IPin is not implemented')

    def setUserStruct(self, inStruct):
        raise NotImplementedError('setUserStruct method of IPin is not implemented')


class INode(IItemBase):

    def __init__(self):
        super(INode, self).__init__()

    def compute(self):
        raise NotImplementedError('compute method of INode is not implemented')

    def isCallable(self):
        raise NotImplementedError('isCallable method of INode is not implemented')

    def addInputPin(self, pinName, dataType, foo=None):
        raise NotImplementedError('addInputPin method of INode is not implemented')

    def addOutputPin(self, pinName, dataType, foo=None):
        raise NotImplementedError('addOutputPin method of INode is not implemented')

    def getUniqPinName(self, name):
        raise NotImplementedError('getUniqPinName method of INode is not implemented')

    def postCreate(self, jsonTemplate=None):
        raise NotImplementedError('postCreate method of INode is not implemented')

    def setData(self, pinName, data, pinSelectionGroup):
        raise NotImplementedError('setData method of INode is not implemented')

    def getData(self, pinName, pinSelectionGroup):
        raise NotImplementedError('getData method of INode is not implemented')


class IPackage(object):
    def __init__(self):
        super(IPackage, self).__init__()

    @staticmethod
    def GetFunctionLibraries():
        pass

    @staticmethod
    def GetNodeClasses():
        pass

    @staticmethod
    def GetPinClasses():
        pass
