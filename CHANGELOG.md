# Version 0.3.0

- Fix mistakes in PT net implementation
- Improved documentation
- Wrapped `asyncio.run` in a clean interface
  - It also supports attaching asyncio tasks additional to the PT loops
- Improved graphviz generator
  - Custom indentation and label names
  - Custom coloring for `SpecialPlace`
- Can subscribe to transition firing notifications from any task
- Custom formatted debug printing
- Added new tests and examples


## Version 0.2.0

- Improved documentation
- Removed all global state, all related PTs belong to a particular SoyutNet instance
- Arcs can have multiple labels
- Token count records can be merged and sorted by time at the end of simulation
- Added Graphviz dot file generator
- New tests and examples

## Version 0.1.0

First version
