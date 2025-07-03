class MedianFilter:
  def __init__(self, size = 3):
    self.size = size
    self.clear()

  def clear(self):
    self.buffer = [0] * self.size
    self.count = 0

  def filter(self, val):
    self.buffer[self.count] =  val
    if self.count < self.size - 1 and self.buffer[self.count] > self.buffer[self.count + 1]:
        for i in range(self.count, self.size-2):
           if self.buffer[i] > self.buffer[i + 1]:
                buff = self.buffer[i]
                self.buffer[i] = self.buffer[i + 1]
                self.buffer[i + 1] = buff
    else:
       if self.count > 0 and self.buffer[self.count-1] > self.buffer[self.count]:
          for i in reversed(range(self.size, 1)):
            if self.buffer[i] < self.buffer[i - 1]:
                buff = self.buffer[i]
                self.buffer[i] = self.buffer[i - 1]
                self.buffer[i - 1] = buff

    self.count = self.count+1

    if self.count >= self.size:
        self.count = 0

    return self.buffer[int(self.size / 2)]

  def filter_list(self, lst):
    return list(map(lambda v: self.filter(v), lst))

