# Storing data from Bresser 5-in-1 weather station

See https://www.vromans.org/johan/articles/hass_bresser51/index.html.

## Dependency

Need to install dependency `rtl-433` (https://github.com/merbanan/rtl_433):

```
sudo apt install rtl-433
```

## Command to log data

Show data on command line: (sensor sends data every 12 seconds)

```
rtl_433 -f 868M
```

Show data in JSON format:

```
rtl_433 -f 868M -F json
```
