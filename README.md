# pyflake
`pyflake` is a pure Python snowflake ID generator. It offers a standalone `pyflake_generator` function that can be used to create unique snowflake IDs, as well as an optional `PyflakeClient` class to easily manage a generator and generate IDs on the fly.

# Features
- `to_timestamp` - A translator function to convert snowflake IDs into UNIX timestamps (ms). A known epoch time is required to translate any snowflake ID
- `generate_seed` - A function that returns a random `int` value that is no greater in length than a provided `bits` size
- `pyflake_generator` - Standalone function that outputs a `generator` producing 64-bit snowflake IDs. Accepts an epoch timestamp and two additional 5-bit IDs
- `PyflakeClient` - A simple client class to handle the creation and management of a single `pyflake_generator` instance, and convenient ID generation and translation

# Requirements
- Python 3.10

## Core modules imported
- `time` - Used to generate timestamp values
- `math` - Used to ensure `time` timestamp values are `int` and not `float`
- `random` - Used to generate seed values within `generate_seed`

# Usage
## generate_seed(`bits: int`)
This package includes a handy function for quick seed generation, which outputs a random number no longer than the provided bit value.

To generate a seed with a bit value of no more than 5, as is the case with both the `pid` and `seed` variables, call the `generate_seed(bits)` function and store the response for later use.

Both the `PyflakeClient` class and `pyflake_generator` function require `epoch` time, `pid` or process ID, and `seed` values on initialization. While the `pid` and `seed` variables are limited to a maximum integer value of `31`, or a bit length of `5` or `(2^5-1)`, the actual provided values of each are arbitrary. The `generate_seed` function makes generating these values a simple process.

Timestamp values are expected to be received as millisecond values no greater than `42` bits in length that may be converted to a human-readable date. While a valid <42-bit integer may be generated using the `generate_seed` function, timestamp values should NOT be generated using the `generate_seed` function if a human-readable date is expected to be referenced from the ID in the future.
```python
  from pyflake import generate_seed
  
  seed = generate_seed(5)
  print(seed)
```

## pyflake_generator(`epoch: int`, `pid: int`, `seed: int`, `sleep: int` = x / 1000)
A standalone snowflake ID generator may be created without an overhead `PyflakeClient` by importing and calling the `pyflake_generator(epoch, pid, seed)` function.

While made available, the `sleep` parameter is optional, and will define how long the generator should wait if it encounters a situation where its ID sequence becomes overrun, or other time-related issues where the generator may need to pause before returning a value to the requesting client. Passing a value of `1` will instruct the function to delay for `1 millisecond` before proceeding, which is sufficient for this generator's purposes.

A total of `4095` IDs may be generated over a `12` bit sequence, which has a shelf life of no longer than `1 millisecond`, mitigating a very small, although still realistic chance, that two IDs will be generated at once, while providing enough range in the sequence to produce nearly `4.1k` IDs in that lifespan before resetting the sequence. Delaying the client by a minimum of `1 millisecond` ensures overrun sequences do not occur, and IDs remain unique for not only the life of the generator, but the client that manages it.
```python
  from pyflake import pyflake_generator, generate_seed

  # Sun, 15 Apr 2019 04:12:00.000-GMT+0:00
  epoch = 1555301520000
  
  pid = generate_seed(5) # 5 bits, random.randint(1, 31) or random.randint(1, (2^5-1))
  seed = generate_seed(5) # 5 bits, random.randint(1, 31) or random.randint(1, (2^5-1))
  sleep = 1 # 1 / 1000 = 1 ms (one millisecond)
    
  generator = pyflake_generator(epoch, pid, seed, sleep)
```

To generate an ID from `pyflake_generator`, the `next(<pyflake_generator>)` method should be called, and the resulting value stored for later reference:
```python
  id = next(generator)
  print(id)
```
Expected output is a `dictionary` object:
```python
  {
    'timestamp': 1668081259486,
    'seed': 6,
    'pid': 6,
    'sequence': 0,
    'snowflake': 473032512445898752,
    'idx': 1
  }
```

## PyflakeClient(`epoch: int`)
This package offers the `PyflakeClient` class to easily create, renew, and destroy a `pyflake_generator`, as well as generate IDs with a cleaner API versus calling `next(<pyflake_generator>)`.
```python
  from pyflake import PyflakeClient

  epoch = 1555301520000

  client = PyflakeClient(epoch)    
```
Once a client instance has been created, a generator can be created for it by calling the `PyflakeClient.create_generator(pid, seed)` method.

### PyflakeClient.create_generator(`pid: int`, `seed: int`)
In order to create a generator, `pid` and `seed` values are required. The `int` values passed here should be no more than `5` bits, `(2^5-1)`, or `31` each. To conveniently generate a random `int` value within these constraints, import the `generate_seed` function.
```python
  from pyflake import PyflakeClient, generate_seed

  epoch = 1555301520000
  client = PyflakeClient(epoch)

  pid = generate_seed(5)
  seed = generate_seed(5)  

  client.create_generator(pid, seed)
```

### PyflakeClient.destroy_generator()
The `PyflakeClient`'s `_generator` attribute, storing the result of the `pyflake_generator` produced on initial generator creation, may be manually destroyed at any time by calling the `PyflakeClient.destroy_generator()` method. This method checks if a `pyflake_generator` is available to the `PyflakeClient` before attempting to destroy it. This method is automatically called during the `PyflakeClient.renew_generator()` process.
```python
  client.destroy_generator()
```
### PyflakeClient.renew_generator(`pid: int`, `seed: int`)
The `PyflakeClient` also offers the ability to renew the available `pyflake_generator` by calling the `PyflakeClient.renew_generator(pid, seed)` method. By using the imported `generate_seed` function to create new `pid` and `seed` values, we can quickly renew the client's generator values and produce all new IDs without creating an entirely new `PyflakeClient` instance:
```python
  pid = generate_seed(5)
  seed = generate_seed(5)
  client.renew_generator(pid, seed)
```
Once the available `pyflake_generator` has been destroyed, the `renew_generator` process continues on to create a new `pyflake_generator` for the `PyflakeClient` to utilize under the same attribute name: `_generator`, by calling the same `PyflakeClient.create_generator(pid, seed)` method used to create the generator when the client was first initialized. Once the `PyflakeClient.renew_generator()` process has completed, new IDs may be perpetually generated from the new `pyflake_generator` until the script is terminated, or the client's `_generator` attribute is renewed again or destroyed.

### PyflakeClient.generate()
Once the generator has been created, the client can begin generating, caching, and outputting snowflake IDs to requesting clients. To generate an ID from the `PyflakeClient` module, the `PyflakeClient.generate()` method should be called, and the resulting value stored for later reference:
```python
  id = client.generate()
  print(id)
```
Expected output when requesting a snowflake ID from the `PyflakeClient` is a `str` value:
```python
473032512445898752
```
### PyflakeClient.\_cache
When using the `PyflakeClient` module, every snowflake ID generated using the client (and its current and future attached generators) is stored in the `PyflakeClient`'s local `_cache` property. Entries here are stored within a `dict` and keyed by the `PyflakeClient`'s `_generated` property value `+ 1` at the time of caching.

Since all generated snowflakes are cached, they may be later retrieved for review, reference, or other analysis. All cached snowflakes are representative of the deconstructed snowflake object generated by the `pyflake_generator` function that created it.
```python
  {
    'timestamp': 1668081259486,
    'seed': 6,
    'pid': 6,
    'sequence': 0,
    'snowflake': 473032512445898752,
    'idx': 1
  }
```
### PyflakeClient.get_info()
The `PyflakeClient` class offers a convenient `get_info()` method to retrieve information requesting clients may need to commonly reference. Calling the `PyflakeClient.get_info()` method will return a dictionary object of valuable metadata:
```python
  {
    'pid': 6, # int value, represents the 'process id' specified by the managing client
    'seed': 6, # int value, represents the 'seed' value specified by the managing client
    'epoch': 1555301520000, # int value, represents the epoch time (in milliseconds) which all client snowflake IDs are based
    'generated': 2, # int value, represents the number of snowflakes generated since client initialization
    'generator': True # boolean value, indicates the presence of an available client generator
  }
```

## Conversion
A standalone translator function `to_timestamp` can be used to convert all snowflake IDs generated into timestamps (milliseconds), provided the epoch time used to create the snowflake is both known and provided.

### to_timestamp(`epoch: int`, `id: int`, `fmt: str`)
The `fmt` variable is optional and defaults to `ms` for `milliseconds`. Passing a value of `s` for `seconds` will return a value of seconds passed since UNIX epoch time.

```python
  from pyflake import pyflake_generator, generate_seed, to_timestamp
  
  epoch = 1555301520000
  pid = generate_seed(5)
  seed = generate_seed(5)
    
  generator = pyflake_generator(epoch, pid, seed)
  
  id = next(generator)
  fmt = 'ms'

  id = to_timestamp(epoch, id, fmt)
  print(id)
```

### PyflakeClient.to_timestamp(`id: int`, `fmt: str`)
This function is built into the `PyflakeClient` class and does not need to be additionally imported.

When calling the `to_timestamp` method, the client's epoch is used to determine the snowflake's resulting timestamp. As such, snowflakes generated using a different client or generator may return invalid timestamps if the epoch time used to generate the snowflake ID is different than the epoch time of the client used for conversion.

The `fmt` variable is optional here as well, and defaults to `ms` for `milliseconds`. Passing a value of `s` for `seconds` will return a value of seconds passed since UNIX epoch time. 

NOTE: Due to the bit placement of the `timestamp` value utilized during snowflake generation, the translator method will continue to accurately translate snowflakes even if the `pid` or `seed` values are renewed after `PyflakeClient` initialization. However, if the `PyflakeClient`'s epoch time is modified, previous snowflake IDs may no longer be translatable. Requesting clients may have more flexibility in changing the client's `_epoch` attribute value when utilizing the built-in `PyflakeClient` cache, or another data cache, as historical epoch times may be stored alongside generated snowflakes and referenced until the record is permanently destroyed.

```python
  from pyflake import PyflakeClient, generate_seed

  epoch = 1555301520000
    
  client = PyflakeClient(epoch)
  pid = generate_seed(5)
  seed = generate_seed(5)
  
  client.create_generator(pid, seed)
  
  id = client.generate()
  fmt = 'ms'
  
  id = client.to_timestamp(id, fmt)
  print(id)
```
