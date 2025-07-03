class RAFilter:
  def __init__(self, size = 3):
    self.size = size
    self.init = False
    self.clear();

  def clear(self):
    self.buffer = [0] * self.size
    self.count = 0
    self.average = 0

  def filter(self, val):
    self.count = self.count+1
    if self.count >= self.size:
        self.count = 0

    self.average = self.average - self.buffer[self.count]
    self.average = self.average + val;
    self.buffer[self.count] = val;

    if not self.init:
      if self.count+1 >= self.size:
        self.init = True
      return int(self.average / self.count)

    return int(self.average / self.size)

  def filter_list(self, lst):
    return list(map(lambda v: self.filter(v), lst))
