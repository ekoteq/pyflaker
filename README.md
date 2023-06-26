# pyflaker `2.0.0`
`pyflaker` is a pure Python snowflake ID generator. It offers a standalone `SnowflakeGenerator` class that can be used to create unique snowflake IDs, as well as an optional `SnowflakeGeneratorMeta` class to easily create new SnowflakeGenerator classes on the fly.

# Support
Discord - `@drixxobot`

# Features
- `SnowflakeGenerator` - A simple class to handle the creation and management of a single `SnowflakeGenerator` instance
- `SnowflakeGeneratorMeta` - A meta type class for defining new SnowflakeGenerator classes

# Requirements
- Python 3.11

## Core modules imported
- `datetime` - Used to generate timestamp values
- `typing` - For type-hinting purposes
- `time` - For synchronous `sleep` calls
