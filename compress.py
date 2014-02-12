#!/usr/bin/env python
import blosc
import json
import pandas
import sys

f = sys.argv[1]
d = pandas.read_csv(f)

for cname in d.columns:
  print cname
  c = d[cname]
  assert c.dtype.name.startswith("int")
  if c.min() >= -128 and c.max() <= 127:
    t = "b"
  elif c.min() >= -32768 and c.max() <= 32767:
    t = "h"
  elif c.min() >= -2147483648 and c.max() <= 2147483647:
    t = "l"
  else:
    assert "don't know type to pack" is False
  t = "<" + t
  meta = json.dumps({"dtype": t})
  print meta
