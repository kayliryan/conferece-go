from json import JSONEncoder
from django.db.models import QuerySet
from datetime import datetime

class DateEncoder(JSONEncoder):
    def default(self, o):
        # if o is an instance of datetime
        #    return o.isoformat()
        if isinstance(o, datetime):
            return o.isoformat()
        else:
            return super().default(o)
            # otherwise
        #    return super().default(o)

class QuerySetEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, QuerySet):
            return list(o)
        else:
            return super().default(o)

class ModelEncoder(QuerySetEncoder, DateEncoder, JSONEncoder):
    encoders = {}

    def default(self, o):
        #   if the object to decode is the same class as what's in the
        #   model property, then
        if isinstance(o, self.model):
            #     * create an empty dictionary that will hold the property names
        #       as keys and the property values as values
            d = {}
            # if o has the attribute get_api_url
            if hasattr(o, 'get_api_url'):
            #    then add its return value to the dictionary
            #    with the key "href"
                d['href'] = o.get_api_url()
            #     for each name in the properties list
            for property in self.properties:
            #         * get the value of that property from the model instance
        #           given just the property name
                value = getattr(o, property)
        #         * put it into the dictionary with that property name as
        #           the key
                if property in self.encoders:
                    encoder = self.encoders[property]
                    value = encoder.default(value)
                d[property]=value
            d.update(self.get_extra_data(o))
        #     * return the dictionary
            return d
        #   otherwise,
        #       return super().default(o)  # From the documentation
        else:
            return super().default(o)
        
    def get_extra_data(self, o):
        return {}


