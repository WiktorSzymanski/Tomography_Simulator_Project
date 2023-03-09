

class ImageExec:
  def __init__(self, image):
    self.image = image
    self.height, self.width, _ = image.shape

  def set_pixel(self, x, y, color):
    if (x >= self.width or y >= self.height or x < 0 or y < 0):
      raise Exception(f'Point ({x}, {y}) out of image!!!')
    self.image[y][x] = color

  def draw_bresenham_line(self, point1, point2, color):
    x1, y1 = point1
    x2, y2 = point2
    
    rise = y2 - y1
    run = x2 - x1

    if run == 0:
      if y2 < y1:
        y1, y2 = (y2, y1)
      for y in range(y1, y2 + 1):
        self.set_pixel(x1, y, color)
    else:
      m = float(rise) / run
      adjust = 1 if m >= 0 else -1
      offset = 0
      threshold = 0.5

      if m <= 1 and m >= -1:
        delta = abs(m)
        y = y1
        if x2 < x1:
          x1, x2 = (x2, x1)
          y = y2
        for x in range(x1, x2 + 1):
          self.set_pixel(x, y, color)
          offset += delta
          if offset >= threshold:
            y+= adjust
            threshold += 1
      else:
        delta = abs(float(run) / rise)
        x = x1
        if y2 < y1:
          y1, y2 = (y2, y1)
          x = x2
        for y in range(y1, y2 + 1):
          self.set_pixel(x, y, color)
          offset += delta
          if offset >= threshold:
            x += adjust
            threshold += 1

  def calc_bresenham_line(self, point1, point2):
    sum = 0
    px = 0

    x1, y1 = point1
    x2, y2 = point2
    
    rise = y2 - y1
    run = x2 - x1

    if run == 0:
      if y2 < y1:
        y1, y2 = (y2, y1)
      for y in range(y1, y2 + 1):
        sum += self.image[y][x1][0]
        px += 1
        self.set_pixel(x1, y, (255, 0, 0))
    else:
      m = float(rise) / run
      adjust = 1 if m >= 0 else -1
      offset = 0
      threshold = 0.5

      if m <= 1 and m >= -1:
        delta = abs(m)
        y = y1
        if x2 < x1:
          x1, x2 = (x2, x1)
          y = y2
        for x in range(x1, x2 + 1):
          sum += self.image[y][x][0]
          px += 1
          self.set_pixel(x, y, (0, 0, 255))
          offset += delta
          if offset >= threshold:
            y+= adjust
            threshold += 1
      else:
        delta = abs(float(run) / rise)
        x = x1
        if y2 < y1:
          y1, y2 = (y2, y1)
          x = x2
        for y in range(y1, y2 + 1):
          sum += self.image[y][x][0]
          px += 1
          offset += delta
          self.set_pixel(x, y, (0, 255, 0))
          if offset >= threshold:
            x += adjust
            threshold += 1

    return sum, px