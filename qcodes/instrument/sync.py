"""This modules contains classes that define a unified interface for "synchronous" instrument/parameter control.
Asynchronous means that the python/QCoDeS delegates the timing control to the physical instruments.

Example applications are fast voltage sweeps but also parameter sweeps of qupulse pulses.

The Sync class represents synchronisation points with a certain length. It can be created by hand or by an sync_set
command.

Open question:
 - How to handle subsets of syncs?

"""


import numpy

from abc import abstractmethod
from typing import NamedTuple, Optional, Dict, List, Callable, Set


class Sync:
    """Synchronization proxy between `SyncParameter.sync_get` and `SyncParameter.sync_set` calls. Consists of several
    sync points which are relative to a trigger event. Stores synchronous commands together with their instruments.

    The time points can either be explicit i.e. a list of begin, length pairs or implicit i.e. a periodic description.
    Obviously not all syncs gan be described as period but some(most) instruments will require periodic sync points
    because they sample with a fixed rate.

    Call execute to prepare all involved instruments for the synchronous operation.
    """
    Periodic = NamedTuple('Periodic', [('period', float),
                                       ('begin', float),
                                       ('length', float),
                                       ('count', int)])

    Explicit = NamedTuple('Explicit', [('begin', numpy.ndarray),
                                       ('length', numpy.ndarray)])

    def __init__(self):
        self._commands = {}  # type: Dict[SyncInstrument, List[SyncCommand]]

    def get_instruments(self) -> Set['SyncInstrument']:
        """
        Returns:
            Set of all instruments involved in this sync operation.
        """
        return set(self._commands.keys())

    def _compile_commands(self) -> Dict['SyncInstrument', 'SyncCommand']:
        """Compile the commands of this Sync object and it's eventual children.

        This means merging the list of commands in _commands into a single command."""
        return {instrument: first_command.parallel(*commands)
                for (instrument, (first_command, *commands)) in self._commands.items()}

    def execute(self):
        """Prepare all instruments for synchronous operation. The function returns when all instruments are prepared.
        Triggering is not specified. It probably needs to be done externally."""
        for instrument, commands in self._compile_commands().items():
            instrument.prepare(self, commands)

    def cancel(self) -> Set['SyncInstrument']:
        """Cancel all synchronous preparations / operations.
        Returns:
            Set of instruments where canceling might have failed
        """
        failed = set()
        for instrument in self.get_instruments():
            successful_cancel = instrument.cancel_sync_operations()
            if not successful_cancel:
                failed.add(instrument)
        return failed

    def repeated(self, count) -> 'Sync':
        """Creates a new sync operation that is a repetition of the current.

        Args:
            count: repetition count

        Returns:
            new sync operation
        """
        return RepeatedSync(self, count)

    @abstractmethod
    def as_periodic(self) -> Optional[Periodic]:
        """Return periodic sync point description or None"""

    @abstractmethod
    def as_explicit(self) -> Explicit:
        """Return explicit sync point description with shape == (N, 2)"""

    @abstractmethod
    @property
    def duration(self) -> float:
        """Duration of the sync object."""

    @abstractmethod
    @property
    def num_sync_points(self) -> int:
        """Number of synchronization points"""

    def add_command(self, instrument: 'SyncInstrument', command):
        """Add a new command to this sync object."""
        self._commands.setdefault(instrument, []).append(command)


class ExplicitSync(Sync):
    """Explicit sync points"""
    def __init__(self, sync_times: numpy.ndarray, sync_lengths: numpy.ndarray, duration=None):
        """

        Args:
            sync_times: Time points of sync i.e. where something should happen
            sync_lengths: Lengths of sync i.e. how long should a measurement be / a set value be constant
            duration: Total duration of the sync object. Needs to be >= sync_times[-1] + sync_lengths[-1]
        """
        assert numpy.all(numpy.diff(sync_times) >= 0)
        assert numpy.all(sync_lengths >= 0)
        assert sync_times.ndim == 1
        assert sync_lengths.ndim == 1
        assert sync_times.size == sync_lengths.size

        if duration is None:
            duration = sync_times[-1] + sync_lengths[-1]
        super().__init__()

        self._explicit = self.Explicit(sync_times, sync_lengths)
        self._duration = duration

    @property
    def duration(self):
        return self._duration

    def as_periodic(self) -> Optional[Sync.Periodic]:
        if self._explicit.begin.size == 1:
            return self.Periodic(self.duration(), self._explicit.begin[0], self._explicit.length[0], 1)
        else:
            return None

    def as_explicit(self) -> Sync.Explicit:
        return self._explicit

    @property
    def num_sync_points(self) -> int:
        return self._explicit.begin.size


class RepeatedSync(Sync):
    def __init__(self, sync: Sync, count: int):
        super().__init__()
        self.count = count
        self.sync = sync

    def get_instruments(self) -> Set['SyncInstrument']:
        return super().get_instruments().union(self.sync.get_instruments())

    def _compile_commands(self) -> Dict['SyncInstrument', 'SyncCommand']:
        resulting_commands = super()._compile_commands()
        to_repeat = self.sync._compile_commands()

        for instrument, command in to_repeat.items():
            repeated_command = command.repeated(self.count)

            if instrument in resulting_commands:
                # merge the command from this sync with the repeated command from sub sync
                resulting_commands[instrument] = resulting_commands[instrument].parallel(repeated_command)
            else:
                resulting_commands[instrument] = repeated_command
        return resulting_commands

    @property
    def duration(self):
        return self.sync.duration * self.count

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

    @property
    def num_sync_points(self) -> int:
        return self.count * self.sync.num_sync_points()


class SyncCommand:
    """Carries the instrument specific configuration for an synchronous command. The exact timing information is
    not stored here but in the Sync object.

    This needs to be subclassed and implemented by each sync instrument. Examples are sweeps and
    buffered acquisitions."""

    @abstractmethod
    def repeated(self, count: int) -> 'SyncCommand':
        """Create a command that is a repetition of the current if possible.

        Args:
            count: repetition_count
        Raises:
            TypeError if this command cannot be repeated
        """

    def concatenate(*sync_commands):
        """Concatenate multiple commands

        Args:
            *sync_commands: commands to concatenate

        Raises:
            TypeError if concatenation not possible

        Returns:
            A single command representing the concatenation
        """
        raise NotImplementedError()

    def parallel(self, *sync_commands: 'SyncCommand') -> 'SyncCommand':
        """see _parallel"""
        if sync_commands:
            return self._parallel(*sync_commands)
        else:
            return self

    @abstractmethod
    def _parallel(*sync_commands: 'SyncCommand') -> 'SyncCommand':
        """ Build a new command that merges all provided commands

        Args:
            *sync_commands: Commands to merge into one

        Returns:
            Merged command
        """
        raise NotImplementedError()


class SyncInstrument:
    @abstractmethod
    def prepare(self, sync: Sync, sync_command: SyncCommand):
        """Prepare the instrument to execute the synchronous command. The trigger

        Requirement for implementation: Logs every change of the instrument state for easy debugging.
        Logs should go to instrument.sync

        Args:
            sync:
            sync_command:
        """

    @abstractmethod
    def cancel_sync_operations(self) -> bool:
        """
        - Cancel all running threads and coroutines
        - Cancel sweep of instrument
        - Set instrument to a usable state i.e. simple get and set on parameters work

        Returns:
              True if instrument is usable afterwards, False if one if the above is impossible/failed
        """


class SyncParameter:
    def sync_set(self, values, sync: Sync = None) -> Sync:
        """If the sync is None a new sync is created. Here an sync command is created and placed in the sync.
        The SyncCommand does not need to.

        Args:
            values:
            sync:

        Returns:
            sync or new Sync object
        """

    def sync_get(self, sync: Sync) -> Callable[[], numpy.ndarray]:
        """Create the commands that are necessary to do a synchronous measurement and add them to the provided sync
        object. Use the returned callable to obtain the measured values.

        Args:
            sync: Specifies the times points when to measure

        Returns:
            Callable that blocks until it returns the measured values. It raises an exception if the instrument was not
            configured via sync.execute.
        """

    def is_running(self) -> bool:
        """

        Returns:
            True if set or get is in progress
        """


class SyncDacCommand(SyncCommand):
    def __init__(self, ramp_rate, commands: str):
        raise NotImplementedError('This should result in a script for DecaDac')

    def _parallel(*sync_commands):
        raise NotImplementedError('parallel deca dac ramps not implemented yet')


class SyncDacVoltage(SyncParameter):
    def __init__(self, channel):
        self.channel = channel

    def sync_set(self, values, sync: Sync = None) -> Sync:
        if sync is None:
            # calc sync from ramp rate and values
            raise NotImplementedError()
        else:
            period = sync.as_periodic()
            if period is None:
                raise ValueError('dac only periodic')
            else:
                raise NotImplementedError('sync.add_command(self.channel.instrument, SyncDacCommand())')


class SyncDac(SyncInstrument):
    def prepare(self, sync, sync_command: SyncCommand):
        raise NotImplementedError('create the "script" and upload it to the decadac')
