import time
import math
import random

# all generated IDs may be converted back into a timestamp by stripping
# the lower 22 bits and adding the epoch time into the remaining value.
# A timestamp cannot be returned without knowing the epoch used to
# generate it.
def to_timestamp(epoch, id, fmt = 'ms'):
    id = id >> 22   # strip the lower 22 bits holding the pid, seed, and sequence
    id += epoch # adjust for defined epoch time (ms)

    # clients can optionally request timestamp in seconds format
    # by specifying fmt as 's' instead of 'ms'
    if fmt == 's':
        id = id / 1000

    return id

# returns a random integer that is no less than one, and no greater
# than the maximum integer value of the bits provided
def generate_seed(bits):
    return random.randint(1, (2^bits-1))

# returns a generator that allows a client to generate IDs by calling
# `next([generator])` on the generator
def pyflake_generator(epoch, pid, seed, sleep=lambda x: time.sleep(x/1000.0)):
    # A snowflake is comprised of 64 total bits
    # 42 of the 64 bits exist in the timestamp value (in milliseconds)
    # 22 of the 64 total bits exist in:
    pid_bits = 5
    seed_bits = 5
    sequence_bits = 12

    # define the maximum allowed seed values based on defined bits
    max_pid = -1 ^ (-1 << pid_bits)
    max_seed = -1 ^ (-1 << seed_bits)
    sequence_mask = -1 ^ (-1 << sequence_bits)

    # bit position where the process ID can be found in the snowflake
    pid_shift = sequence_bits

    # bit position where the seed value can be found in the snowflake
    seed_shift = sequence_bits + pid_bits

    # left-hand bit position where the timestamp can be found
    timestamp_shift = sequence_bits + pid_bits + seed_bits

    # enforce maximum integers allowed on provided seed values
    assert pid >= 0 and pid <= max_pid
    assert seed >= 0 and seed <= max_seed

    # if all is well, generator creation begins

    # local generator variables
    last_timestamp = -1
    sequence = 0

    # this process will loop 'while true' until a yield statement is
    # reached, at which time the loop will be paused pending a call to
    # `next(<generator>)`, which will return a string value and increment
    # the sequence. Multiple unique IDs may be crafted from a single
    # generator instance, and near-infinite unique IDs may be generated
    # by utilizing multiple generator instances within a single package
    while True:
        timestamp = math.floor(time.time() * 1000)

        # If the previous timestamp is greater than the current timestamp,
        # as if time is moving backwards, wait until time catches up to
        # ensure only sequential IDs are issued in ascending order
        if last_timestamp > timestamp:
            sleep(last_timestamp-timestamp)
            continue

        # if an ID was already generated under the current sequence value
        # as such may be the case in race conditions, where multiple IDs
        # are requested at the same time, we want to increase the sequence
        # before proceeding.
        if last_timestamp == timestamp:
            sequence = (sequence + 1) & sequence_mask
            # in the event the sequence becomes overrun, the sequence is updated
            # and the process continues after a one-second delay, ensuring a new
            # timestamp is used, preventing conflicts in IDs where sequences are
            # full, or cannot provide further unique values
            if sequence == 0:
                sequence = -1 & sequence_mask
                sleep(1)
                continue
        # Otherwise, if the current timestamp is greater than the
        # previous timestamp, the sequence is reset, as there will be no
        # conflicts with previous IDs under a new timestamp
        else:
            sequence = 0

        # update the 'last_timestamp' value with the most-recently obtained
        # timestamp, used to generate the currently-requested snowflake
        last_timestamp = timestamp

        # yield the loop and return the value to the requesting client
        # pending future client requests
        yield (
            # subtract the current timestamp from the defined epoch, which
            # returns the miliseconds passed since the epoch time, and place
            # the timestamp value in the sequence relative to the defined
            # 'timestamp_shift' bit value defined above
            ((timestamp-epoch) << timestamp_shift) |
            # the same is done to the seed and pid values for sequence placement
            (seed << seed_shift) |
            (pid << pid_shift) |
            # finally, the current sequence value is returned, preventing race
            # conditions and ensuring uniqueness across IDs generated within
            # the same millisecond
            sequence)

# a snowflake generator client class
# use of this class is not required - a generator may be created by
# calling the global `generator` function above the below class just makes
# managing the generator that much easier
class PyflakeClient():
    def __init__(self, epoch, pid, seed):
        self.epoch = epoch

        # process ID and a random generated integer are used as seed values
        # for the client generator
        # since the maximum bits for both is 5, the value cannot be greater
        # than (2^5-1), or 31
        self.generator = generator(self.epoch, pid, seed)

    # destroys the current generator, if one exists
    def destroy(self):
        if getattr(self, 'generator'):
            delattr(self, 'generator')

    # creates a new generator, if one does not exist
    def create(self, pid, seed):
        if not getattr(self, 'generator'):
            setattr(self, 'generator', generator(self.epoch, pid, seed))

    # replaces the current generator with a new one, and allows
    # the requesting client to define a process ID and seed value
    def renew(self, pid, seed):
        self.destroy()
        self.create(pid, seed)

    # shortcut function, quickly returns a snowflake ID from the attached
    # generator, based on timestamp value at the time the request was made
    def generate(self):
        return next(self.generator)

    def to_timestamp(self, id, fmt):
        return to_timestamp(self.epoch, id, fmt)
