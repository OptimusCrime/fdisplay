# fdisplay

A simple script that rearranges the order of displays for macOS, because I got tired of rearranging the displays 
manually every time I connected to external monitors.

- Supports one or two external monitors.
- Supports arranging displays with the MacBook on either the left or right side of the external monitors.

If you have two external monitors, you can call the script multiple times to swap their positions.

```bash
$ ./fdisplay.py left # Macbook on the left side (also the default)
$ ./fdisplay.py right # Macbook on the right side
```

## Requirements

- [jakehilborn/displayplacer](https://github.com/jakehilborn/displayplacer)