# pyflake
`pyflake` is a pure Python snowflake ID generator. It offers a standalone generator that can be used to create near-endlessly unique snowflake IDs, as well as an optional PyflakeClient class to easily manage a generator and generate IDs on the fly.

# Requirements
- Python 3.10

## Core modules imported
- `time` - Used to generate timestamp values
- `math` - Used to ensure timestamp values are `int` and not `float`
- `random` - Used to generate seed values within `generate_seed`

# Usage

## Seeds
This package includes a handy function for quick seed generation, which outputs a random number no longer than the provided bit value.

To generate a seed with a bit value of no more than 5, as is the case with both the `pid` and `seed` variables, call the `generate_seed(bits)` function and store the response for later use.

Both the `PyflakeClient` class and `pyflake_generator` function require `epoch` time, `pid` or process ID, and `seed` values on initialization. While the `pid` and `seed` variables are limited to a maximum integer value of `31`, or a bit length of `5` or `(2^5-1)`, the actual provided values of each are arbitrary. The `generate_seed` function makes generating these values a simple process.

Timestamp values are expected to be received as millisecond values no greater than `42` bits in length that may be converted to a human-readable date. While a valid <42-bit integer may be generated using the `generate_seed` function, timestamp values should NOT be generated using the `generate_seed` function if a human-readable date is expected to be referenced from the ID in the future.
```python
  from pyflake import generate_seed
  
  seed = generate_seed(5)
  print(seed)
```

## pyflake_generator
A standalone snowflake ID generator may be created without an overhead `PyflakeClient` by importing and calling the `pyflake_generator(epoch, pid, seed)` function.
```python
  from pyflake import pyflake_generator, generate_seed

  # Sun, 15 Apr 2019 04:12:00.000-GMT+0:00
  epoch = 1555301520000
  
  pid = generate_seed(5)
  seed = generate_seed(5)
    
  generator = pyflake_generator(epoch, pid, seed)
```

To generate an ID from `pyflake_generator`, the `next(<pyflake_generator>)` method should be called, and the resulting value stored for later reference:
```python
  id = next(generator)
  print(id)
```

## PyflakeClient
This package offers the `PyflakeClient` class to easily create, renew, and destroy a `pyflake_generator`, as well as generate IDs with a cleaner API versus calling `next(<pyflake_generator>)`.
```python
  from pyflake import PyflakeClient, generate_seed

  epoch = 1555301520000
  pid = generate_seed(5)
  seed = generate_seed(5)
    
  client = PyflakeClient(epoch, pid, seed)
```

To generate an ID from the `PyflakeClient` module, the `PyflakeClient.generate()` method should be called, and the resulting value stored for later reference:
```python
  id = client.generate()
  print(id)
```

The `PyflakeClient` also offers the ability to renew the available `pyflake_generator` by calling the `PyflakeClient.renew(pid, seed)` method:
```python
  pid = generate_seed(5)
  seed = generate_seed(5)
  client.renew(pid, seed)
```

On renewal, the old `pyflake_generator` is destroyed via the `PyflakeClient.destroy()` method, which first checks if a `pyflake_generator` is available to the `PyflakeClient` before attempting to destroy it. While this method may be called via `PyflakeClient.destroy()`, it is automatically called during the `PyflakeClient.renew()` process.
```python
  client.destroy()
```

Once the available `pyflake_generator` has been destroyed, the `renew` method creates a new `pyflake_generator` for the PyflakeClient to utilize. This method also checks if a `pyflake_generator` is available prior to creating a new one to prevent unintentional overwrites. Like `PyflakeClient.destroy()`, This method is also automatically called during the `PyflakeClient.renew()` process, and passes along the `pid` and `seed` variable values.
```python
  client.create(pid, seed)
```

Once the `PyflakeClient.renew()` process has completed, new IDs may be perpetually generated until the script is terminated, or the `pyflake_generator` is renewed again or destroyed.

## Conversion
A standalone translator function `to_timestamp` can be used to convert all snowflake IDs generated into timestamps (milliseconds).

### pyflake_generator
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

### PyflakeClient
This function is built into the `PyflakeClient` class and does not need to be additionally imported.

When calling the `to_timestamp` method, the client's epoch is used to determine the snowflake's resulting timestamp. As such, snowflakes generated using a different client or generator may return invalid timestamps if the epoch time used to generate the snowflake ID is different than the epoch time of the client used for conversion.

The `fmt` variable is optional here as well, and defaults to `ms` for `milliseconds`. Passing a value of `s` for `seconds` will return a value of seconds passed since UNIX epoch time. 

NOTE: Due to the bit placement of the `timestamp` value utilized during snowflake generation, the translator method will continue to accurately translate snowflakes even if the `pid` or `seed` values are renewed after `PyflakeClient` initialization. However, if the `PyflakeClient`'s epoch time is modified, previous snowflake IDs may no longer be translatable.

```python
  from pyflake import PyflakeClient, generate_seed

  epoch = 1555301520000
  pid = generate_seed(5)
  seed = generate_seed(5)
    
  client = PyflakeClient(epoch, pid, seed)
  
  id = client.generate()
  fmt = 'ms'
  
  id = client.to_timestamp(id, fmt)
  print(id)
```
