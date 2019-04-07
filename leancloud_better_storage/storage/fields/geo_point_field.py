from leancloud import GeoPoint

from .defaults import undefined
from .field import Field
from ..query import Condition, ConditionOperator


class GeoPointField(Field):
    _fit_fn = {
        tuple: lambda pair: GeoPoint(pair[0], pair[1]),
        GeoPoint: lambda gp: gp,
    }

    def __init__(self, name=None, nullable=True, default=undefined):
        super().__init__(name, nullable, default)

    def near(self, geo_point):
        """
        查询离靠近指定点的对象，按距离升序。

        :param geo_point: 指定地理点
        """
        try:
            return Condition(self, ConditionOperator.Near, self._fit_fn[type(geo_point)](geo_point))
        except (KeyError, IndexError):
            raise ValueError('param geo_point must be instance of GeoPoint or '
                             'tuple with two or more elements (only use first two).')

    def within_kilometers(self, geo_point, kilometers):
        """
        查询离指定点 kilometers 距离内的对象

        :param geo_point: 地理点
        :param kilometers: 距离，单位千米
        """
        try:
            return Condition(self, ConditionOperator.WithinKilometers, (self._fit_fn[type(geo_point)](geo_point),
                                                                        kilometers))
        except (KeyError, IndexError):
            raise ValueError('param geo_point must be instance of GeoPoint or '
                             'tuple with two or more elements (only use first two).')

    def __set__(self, instance, value):
        try:
            super().__set__(instance, self._fit_fn[type(value)](value))
        except (KeyError, IndexError):
            raise ValueError('param geo_point must be instance of GeoPoint or '
                             'tuple with two or more elements (only use first two).')
