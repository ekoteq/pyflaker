# pyflake
`pyflake` is a pure Python snowflake ID generator. It offers a standalone generator that can be used to create near-endlessly unique snowflake IDs, as well as an optional client class to easily manage a generator and generate IDs on the fly.

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

Both the `Client` class and `generator` function require `epoch` time, `pid` or process ID, and `seed` values on initialization. While the `pid` and `seed` variables are limited to a maximum integer value of `31`, or a bit length of `5` or `(2^5-1)`, the actual provided values of each are arbitrary. The `generate_seed` function makes generating these values a simple process.

Timestamp values are expected to be received as millisecond values no greater than `12` bits in length that may be converted to a human-readable UNIX date string. Timestamp values should NOT be generated using the `generate_seed` function if a human-readable date is expected to be referenced from the snowflake ID in the future.
```python
  from pyflake import generate_seed
  
  _seed = generate_seed(5)
  print(_seed)
```

## Standalone Generator
A standalone snowflake ID generator may be created without an overhead client by importing and calling the `generator(epoch, pid, seed)` function.
```python
  from pyflake import generator, generate_seed

  # Sun, 15 Apr 2019 04:12:00.000-GMT+0:00
  _epoch = 1555301520000
  
  _pid = generate_seed(5)
  _seed = generate_seed(5)
    
  _generator = generator(_epoch, _pid, _seed)
```

To generate an ID from a standalone generator, the `next(<generator>)` method should be called, and the resulting value stored for later reference:
```python
  _id = next(_generator)
  print(_id)
```

## Client
This package offers a client class to easily create, renew, and destroy a generator, as well as generate IDs with a cleaner API (as opposed to calling `next(<generator>)`.
```python
  from pyflake import Client, generate_seed

  _epoch = 1555301520000
  _pid = generate_seed(5)
  _seed = generate_seed(5)
    
  _client = Client(_epoch, _pid, _seed)
```

To generate an ID from the client module, the `generate()` method should be called, and the resulting value stored for later reference:
```python
  _id = _client.generate()
  print(_id)
```

The client also offers the ability to renew the available generator by calling the client's `renew(pid, seed)` method:
```python
  _pid = generate_seed(5)
  _seed = generate_seed(5)
  _client.renew(_pid, _seed)
```

On renewal, the old generator is destroyed via the client's `destroy()` method, which first checks if a generator is available to the client before attempting to destroy it. While this method may be called via `client.destroy(),` it is automatically called during the `renew` process.
```python
  _client.destroy()
```

Once the available generator has been destroyed, the `renew` method creates a new generator for the client to utilize. This method also checks if a generator is available prior to creating a new one to prevent unintentional overwrites. Like `client.destroy()`, This method is also automatically called during the `renew` process, and passes along the `pid` and `seed` values.
```python
  _client.create(_pid, _seed)
```

Once the `renew` process has completed, new IDs may be perpetually generated until the script is terminated, or the generator is renewed again or destroyed.

## Conversion
A standalone translator function `to_timestamp` can be used to convert all snowflake IDs generated into timestamps (milliseconds).

### Standalone Generator
The `fmt` variable is optional and defaults to `ms` for `milliseconds.` Passing a value of `s` for `seconds` will return a value of seconds passed since UNIX epoch time.

```python
  from pyflake import generator, generate_seed, to_timestamp
  
  _epoch = 1555301520000
  _pid = generate_seed(5)
  _seed = generate_seed(5)
    
  _generator = generator(_epoch, _pid, _seed)
  
  _id = next(_generator)
  _fmt = 'ms'

  _id = to_timestamp(_epoch, _id, _fmt)
  print(_id)
```

### Client
This function is built into the client class and does not need to be additionally imported.

When calling the `to_timestamp` method, the client's epoch is used to determine the snowflake's resulting timestamp. As such, snowflakes generated using a different Client or generator may return invalid timestamps if the epoch time used to generate the snowflake ID is different than the epoch time of the client used for conversion.

The `fmt` variable is optional here as well, and defaults to `ms` for `milliseconds.` Passing a value of `s` for `seconds` will return a value of seconds passed since UNIX epoch time. 

NOTE: Due to the bit placement of the `timestamp` value utilized during snowflake generation, the translator method will continue to accurately translate snowflakes even if the `pid` or `seed` generator values are renewed after client initialization. However, if the client's epoch time is modified, previous snowflake IDs may no longer be translatable.

```python
  from pyflake import Client, generate_seed

  _epoch = 1555301520000
  _pid = generate_seed(5)
  _seed = generate_seed(5)
    
  _client = Client(_epoch, _pid, _seed)
  
  _id = _client.generate()
  _fmt = 'ms'
  
  _id = _client.to_timestamp(_id, _fmt)
  print(_id)
```
