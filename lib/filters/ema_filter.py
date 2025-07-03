
class EMAFilter:
  def __init__(self, k_factor = 0.1):
    self.init = False;
    self.k_factor = k_factor
    if self.k_factor > 1:
      raise "k should be between 0 and 1"
    self.clear()

  def clear(self):
    self.buffer = 0

  def filter(self, val):
    if not self.init:
      self.init = True
      self.buffer = val
      return val

    self.buffer = self.buffer + (val - self.buffer) * self.k_factor
    return self.buffer

  def filter_list(self, lst):
    return list(map(lambda v: self.filter(v), lst))
