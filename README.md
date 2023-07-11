# pyflaker `2.1.0`
`pyflaker` is a pure Python snowflake ID generator. It offers a `SnowflakeGenerator` class that can be used to create unique snowflake IDs, as well as utility functions to create and convert snowflake IDs.

# Support
Discord - `@drixxobot`

# Features
- `EKO_EPOCH` - A default datetime value for `2019-04-15 04:12:00+0`
- `snowflake_to_datetime` - A function to convert a snowflake ID and an epoch to a `datetime` object
- `generate_snowflake` - A coroutine function to generate a snowflake ID based on provided `epoch`, `worker_id`, `process_id`, `last_timestamp`, and `sequence` values.
- `SnowflakeGenerator` - An asynchronous snowflake generator class to handle the creation and management of a single `SnowflakeGenerator` instance

# Requirements
- Python 3.11

## Core modules imported
- `asyncio` - Used to generate Lock and Event, and Semaphore instances, and handle `sleep()` calls
- `datetime` - Used to generate date and time values
- `typing` - For type-hinting purposes
