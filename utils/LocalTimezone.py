from datetime import tzinfo, timedelta, datetime
import time as time
from typing import Optional

STDOFFSET = timedelta(seconds=-time.timezone)
if time.daylight:
    DSTOFFSET = timedelta(seconds=-time.altzone)
else:
    DSTOFFSET = STDOFFSET

class LocalTimezone(tzinfo):
    """A concrete subclass of tzinfo used to obtain the offset from UTC based on system time. See
    https://docs.python.org/3/library/datetime.html#datetime.tzinfo.
    """
    def utcoffset(self, dt: datetime) -> timedelta:
        """See https://docs.python.org/3/library/datetime.html#datetime.tzinfo.utcoffset."""
        return DSTOFFSET if self._isdst(dt) else STDOFFSET

    def _isdst(self, dt: datetime) -> bool:
        """See https://docs.python.org/3/library/datetime.html#datetime.tzinfo.dst."""
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = time.mktime(tt)
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0
