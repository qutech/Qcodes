"""This modules contains classes that define a unified interface for "asynchronous" instrument/parameter control.
Asynchronous means that the python/QCoDeS delegates the timing control to the physical instruments.

Example applications are fast voltage sweeps but also parameter sweeps of qupulse pulses.

The Sync class represents synchronisation points with a certain length. It can be created by hand or by an async_set
command.

Open question:
 - How to handle subsets of syncs?

"""


import numpy

from abc import abstractmethod
from typing import Mapping, NamedTuple, Optional


class Sync:
    """Consists of several sync points which are relative to a trigger event.

    1. Nest syncs
    2. delay ´maybe indirect as delay between triggers
    3. Sync point length? Other meta data?

    Errors are raised on execution
    """
    Periodic = NamedTuple('Periodic', [('period', float),
                                       ('begin', float),
                                       ('length', float),
                                       ('count', int)])

    Explicit = NamedTuple('Explicit', [('begin', numpy.ndarray),
                                       ('length', numpy.ndarray)])

    def __init__(self):
        self._commands = {}

    @abstractmethod
    def _compile_commands(self) -> Mapping['AsyncInstrument', 'AsyncCommand']:
        """compile the commands of this and"""

    def execute(self):
        for instrument, commands in self._compile_commands().items():
            instrument.prepare(self, commands)

    def delayed(self, delay) -> 'Sync':
        """Utility function to create a delayed copy if a device is triggered later"""
        raise NotImplementedError()

    def repeated(self, count) -> 'Sync':
        return RepeatedSync(self, count)

    def as_periodic(self) -> Optional[Periodic]:
        """Return periodic sync point description or None"""
        raise NotImplementedError()

    def as_explicit(self) -> Explicit:
        """Return explicit sync point description with shape == (N, 2)"""
        raise NotImplementedError()

    def duration(self):
        raise NotImplementedError()

    def num_sync_points(self) -> int:
        raise NotImplementedError()

    def add_command(self, instrument: 'AsyncInstrument', command):
        self._commands.setdefault(instrument, []).append(command)


class ExplicitSync(Sync):
    """Explicit sync points"""
    def __init__(self, sync_times: numpy.ndarray, points_lengths: numpy.ndarray, duration=None):
        assert numpy.all(numpy.diff(sync_times) >= 0)
        assert numpy.all(points_lengths >= 0)
        assert sync_times.size == points_lengths.size

        if duration is None:
            duration = sync_times[-1] + points_lengths[-1]
        super().__init__()

        self._explicit = self.Explicit(sync_times, points_lengths)
        self._duration = duration

    def duration(self):
        return self._duration

    def as_periodic(self) -> Optional[Sync.Periodic]:
        if self._explicit.begin.size == 1:
            return self.Periodic(self.duration(), self._explicit.begin[0], self._explicit.length[0], 1)
        else:
            return None

    def as_explicit(self) -> Sync.Explicit:
        return self._explicit


class RepeatedSync(Sync):
    def __init__(self, sync: Sync, count: int):
        super().__init__()
        self.count = count
        self.sync = sync

    def _compile_commands(self) -> Mapping['AsyncInstrument', 'AsyncCommand']:
        resulting_commands = self._commands.copy()

        for instrument, command in self.sync._compile_commands().items():
            repeated_command = command.repeated(self.count)
            if instrument in resulting_commands:
                resulting_commands[instrument] = resulting_commands[instrument].parallel(repeated_command)
            else:
                resulting_commands[instrument] = command
        return resulting_commands

    def duration(self):
        return self.sync.duration() * self.sync

    def as_periodic(self):
        """Return periodic sync point description or None"""
        inner = self.sync.as_periodic()
        if inner is not None:
            return self.Periodic(inner.period, inner.begin, inner.length, self.count*inner.count)

    def as_explicit(self) -> Sync.Explicit:
        """Return explicit sync point description"""
        inner = self.sync.as_explicit()
        offsets = numpy.arange(self.count) * self.duration()

        begin = inner.begin[None, :] + offsets[:, None]
        length = numpy.repeat(inner.length, self.count)
        return self.Explicit(begin, length)

    def num_sync_points(self) -> int:
        return self.count * self.sync.num_sync_points()


class AsyncCommand:
    """Carries the instrument specific configuration for an (a)synchronous command. The exact timing information is
    not stored here but in the Sync object.

    This needs to be subclassed and implemented by each async instrument. Examples are sweeps and
    buffered acquisitions."""

    def repeated(self, count: int) -> 'AsyncCommand':
        raise NotImplementedError()

    def concatenate(*async_commands):
        """Concatenate multiple commands raises if concatenation not possible"""
        raise NotImplementedError()

    def parallel(self, *async_commands):
        """see _parallel"""
        if async_commands:
            return self._parallel(*async_commands)
        else:
            return self

    @abstractmethod
    def _parallel(*async_commands):
        """

        Same length?
        """
        raise NotImplementedError()


class AsyncInstrument:
    """TODO: interface to cancel preparation
    """

    @abstractmethod
    def prepare(self, sync, async_command: AsyncCommand):
        """prepare the instrument to execute the asynchronous command.

        :param sync:
        :param async_command:
        :return:
        """


class AsyncParameter:
    def async_set(self, values, sync: Sync = None) -> Sync:
        """If the sync is None a new sync is created. Here an async command is created and placed in the sync.
        The AsyncCommand does not need to

        :param values:
        :param sync:
        :return:
        """

    def async_get(self, sync: Sync) -> callable:
        """
        :param sync:
        :return:
        """


class AsyncDacCommand(AsyncCommand):
    def __init__(self, ramp_rate, commands: str):
        raise NotImplementedError('This should result in a script for DecaDac')

    def _parallel(*async_commands):
        raise NotImplementedError('parallel deca dac ramps not implemented yet')


class AsyncDacVoltage(AsyncParameter):
    def __init__(self, channel):
        self.channel = channel

    def async_set(self, values, sync: Sync = None) -> Sync:
        if sync is None:
            # calc sync from ramp rate and values
            raise NotImplementedError()
        else:
            period = sync.as_periodic()
            if period is None:
                raise ValueError('dac only periodic')
            else:
                raise NotImplementedError('sync.add_command(self.channel.instrument, AsyncDacCommand())')


class AsyncDac(AsyncInstrument):
    def prepare(self, sync, async_command: AsyncCommand):
        raise NotImplementedError('create the "script" and upload it to the decadac')


